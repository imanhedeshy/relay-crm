import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import {
  ApolloGateway,
  IntrospectAndCompose,
  RemoteGraphQLDataSource,
  type GraphQLDataSourceProcessOptions
} from '@apollo/gateway';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';

dotenv.config({ path: '../../.env' });
dotenv.config();

const port = Number(process.env.PORT ?? 4000);

type GatewayContext = {
  userId?: string;
};

class RelayRemoteDataSource extends RemoteGraphQLDataSource<GatewayContext> {
  override willSendRequest({ request, context }: GraphQLDataSourceProcessOptions<GatewayContext>) {
    if (context.userId && request.http) {
      request.http.headers.set('x-user-id', context.userId);
    }
  }
}

function createGateway() {
  return new ApolloGateway({
    supergraphSdl: new IntrospectAndCompose({
      subgraphs: [
        { name: 'auth', url: process.env.AUTH_SERVICE_URL ?? 'http://localhost:8001/graphql/' },
        { name: 'company', url: process.env.COMPANY_SERVICE_URL ?? 'http://localhost:8002/graphql/' },
        { name: 'crm', url: process.env.CRM_SERVICE_URL ?? 'http://localhost:8003/graphql/' },
        { name: 'workflow', url: process.env.WORKFLOW_SERVICE_URL ?? 'http://localhost:8004/graphql/' }
      ]
    }),
    buildService({ url }) {
      return new RelayRemoteDataSource({ url });
    }
  });
}

function isAbortedRequestError(error: unknown) {
  if (!(error instanceof Error)) {
    return false;
  }

  const requestError = error as Error & {
    code?: string;
    type?: string;
  };

  return requestError.message === 'request aborted' || requestError.type === 'request.aborted' || requestError.code === 'ECONNABORTED';
}

async function bootstrap() {
  const server = new ApolloServer<GatewayContext>({
    gateway: createGateway(),
    includeStacktraceInErrorResponses: false,
    introspection: true
  });
  await server.start();

  const app = express();
  app.use(cors());
  app.get('/health', (_req, res) => {
    res.json({ ok: true });
  });
  app.use(
    '/graphql',
    express.json(),
    expressMiddleware(server, {
      context: async ({ req }) => ({
        userId: req.header('x-user-id') ?? undefined
      })
    })
  );
  app.use((error: unknown, _req: express.Request, res: express.Response, next: express.NextFunction) => {
    if (isAbortedRequestError(error)) {
      if (!res.headersSent && !res.destroyed) {
        res.status(499).end();
      }
      return;
    }

    next(error);
  });

  await new Promise<void>((resolve) => {
    app.listen(port, () => {
      console.log(`gateway listening on ${port}`);
      resolve();
    });
  });
}

async function startWithRetry() {
  for (;;) {
    try {
      await bootstrap();
      return;
    } catch (error) {
      console.error('failed to start gateway, retrying in 3s', error);
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }
}

startWithRetry();
