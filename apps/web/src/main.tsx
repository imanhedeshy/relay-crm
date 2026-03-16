import { ApolloClient, ApolloProvider, HttpLink, InMemoryCache, from, makeVar } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

export const selectedUserIdVar = makeVar<string | null>(localStorage.getItem('relaycrm-user-id'));

const authLink = setContext((_, { headers }) => {
  const userId = selectedUserIdVar();

  return {
    headers: {
      ...headers,
      ...(userId ? { 'x-user-id': userId } : {})
    }
  };
});

const httpLink = new HttpLink({
  uri: import.meta.env.VITE_GRAPHQL_URL ?? 'http://localhost:4000/graphql'
});

const client = new ApolloClient({
  link: from([authLink, httpLink]),
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

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
  </React.StrictMode>
);
