import { ApolloClient, HttpLink, InMemoryCache, from, type ApolloLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { selectedUserIdVar } from './appState';

export function createApolloClient(linkOverride?: ApolloLink) {
  const authLink = setContext((_, { headers }) => {
    const userId = selectedUserIdVar();

    return {
      headers: {
        ...headers,
        ...(userId ? { 'x-user-id': userId } : {})
      }
    };
  });

  const transportLink =
    linkOverride ??
    new HttpLink({
      uri: import.meta.env.VITE_GRAPHQL_URL ?? 'http://localhost:4000/graphql'
    });

  return new ApolloClient({
    link: from([authLink, transportLink]),
    cache: new InMemoryCache({
      typePolicies: {
        Query: {
          fields: {
            companies: {
              merge: false
            }
          }
        }
      }
    })
  });
}
