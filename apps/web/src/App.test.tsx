import { ApolloLink, ApolloProvider, Observable, type FetchResult } from '@apollo/client';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import { createApolloClient } from './apolloClient';
import * as appState from './appState';

type OperationHandler = (variables: Record<string, unknown>) => FetchResult | Promise<FetchResult>;

const users = [
  {
    id: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
    fullName: 'Maya Manager',
    email: 'manager.a@relaycrm.local',
    memberships: [{ companyId: '22222222-2222-4222-8222-222222222222', role: 'CHILD_MANAGER' }]
  },
  {
    id: 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',
    fullName: 'Vic Viewer',
    email: 'viewer@relaycrm.local',
    memberships: [{ companyId: '22222222-2222-4222-8222-222222222222', role: 'VIEWER' }]
  }
];

const companies = [
  {
    id: '22222222-2222-4222-8222-222222222222',
    name: 'ChildCoA',
    companyType: 'CHILD',
    parentId: '11111111-1111-4111-8111-111111111111'
  }
];

function createMockLink(handlers: Record<string, OperationHandler>) {
  return new ApolloLink((operation) => {
    const handler = handlers[operation.operationName];

    return new Observable<FetchResult>((observer) => {
      if (!handler) {
        observer.error(new Error(`Unhandled operation: ${operation.operationName}`));
        return;
      }

      Promise.resolve(handler(operation.variables as Record<string, unknown>))
        .then((result) => {
          observer.next(result);
          observer.complete();
        })
        .catch((error) => observer.error(error));
    });
  });
}

function renderApp(handlers: Record<string, OperationHandler>) {
  const client = createApolloClient(createMockLink(handlers));

  return render(
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
  );
}

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
    appState.selectedUserIdVar(null);
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    appState.selectedUserIdVar(null);
  });

  it('persists the selected demo user and reloads the page', async () => {
    const reloadSpy = vi.spyOn(appState, 'reloadPage').mockImplementation(() => {});

    renderApp({
      SeedUsers: () => ({
        data: {
          users
        }
      })
    });

    await screen.findByText('Pick a seeded user to begin');

    await userEvent.selectOptions(screen.getByLabelText('Demo user'), users[0].id);

    await waitFor(() => {
      expect(localStorage.getItem(appState.USER_STORAGE_KEY)).toBe(users[0].id);
      expect(reloadSpy).toHaveBeenCalledTimes(1);
    });
  });

  it('shows the read-only viewer state when a viewer is selected', async () => {
    localStorage.setItem(appState.USER_STORAGE_KEY, users[1].id);
    appState.selectedUserIdVar(users[1].id);

    renderApp({
      SeedUsers: () => ({
        data: {
          users
        }
      }),
      ViewerAndCompanies: () => ({
        data: {
          viewer: users[1],
          companies
        }
      }),
      Dashboard: () => ({
        data: {
          leads: [],
          deals: [],
          activities: []
        }
      })
    });

    expect(await screen.findByText('Lead creation is unavailable for this role')).toBeInTheDocument();
    expect(screen.getByText('Read-only role')).toBeInTheDocument();
    expect(screen.getByText(/this role cannot create new leads/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Create lead' })).not.toBeInTheDocument();
  });
});
