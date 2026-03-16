import assert from 'node:assert/strict';
import test from 'node:test';
import { type AddressInfo } from 'node:net';
import { ApolloServer } from '@apollo/server';
import { RelayRemoteDataSource, createApp, createContext, isAbortedRequestError, type GatewayContext } from './index';

test('RelayRemoteDataSource forwards x-user-id to subgraphs', () => {
  const dataSource = new RelayRemoteDataSource({ url: 'http://example.test/graphql' });
  const headers = new Headers();

  dataSource.willSendRequest({
    request: {
      http: {
        headers
      }
    } as never,
    context: {
      userId: 'viewer-123'
    }
  } as never);

  assert.equal(headers.get('x-user-id'), 'viewer-123');
});

test('createContext reads the incoming x-user-id header', () => {
  const context = createContext({
    header(name: string) {
      return name === 'x-user-id' ? 'viewer-456' : undefined;
    }
  } as never);

  assert.deepEqual(context, { userId: 'viewer-456' });
});

test('gateway app exposes health and graphql routes with request context', async (t) => {
  const server = new ApolloServer<GatewayContext>({
    typeDefs: `#graphql
      type Query {
        viewerId: String!
      }
    `,
    resolvers: {
      Query: {
        viewerId: (_source: unknown, _args: unknown, context: GatewayContext) => context.userId ?? 'anonymous'
      }
    }
  });
  await server.start();
  t.after(async () => {
    await server.stop();
  });

  const app = createApp(server);
  const listener = app.listen(0);
  t.after(async () => {
    await new Promise<void>((resolve, reject) => {
      listener.close((error) => {
        if (error) {
          reject(error);
          return;
        }

        resolve();
      });
    });
  });

  const { port } = listener.address() as AddressInfo;

  const healthResponse = await fetch(`http://127.0.0.1:${port}/health`);
  assert.equal(healthResponse.status, 200);
  assert.deepEqual(await healthResponse.json(), { ok: true });

  const graphqlResponse = await fetch(`http://127.0.0.1:${port}/graphql`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-user-id': 'viewer-789'
    },
    body: JSON.stringify({
      query: 'query ViewerId { viewerId }'
    })
  });
  const graphqlBody = (await graphqlResponse.json()) as {
    data: {
      viewerId: string;
    };
  };

  assert.equal(graphqlResponse.status, 200);
  assert.equal(graphqlBody.data.viewerId, 'viewer-789');
});

test('isAbortedRequestError recognizes aborted request errors', () => {
  assert.equal(isAbortedRequestError(new Error('request aborted')), true);
  assert.equal(isAbortedRequestError(new TypeError('different')), false);
});
