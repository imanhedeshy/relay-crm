import { gql, useMutation, useQuery, useReactiveVar } from '@apollo/client';
import { FormEvent, useEffect, useState } from 'react';
import { persistSelectedUserId, reloadPage, selectedUserIdVar } from './appState';

const USERS_QUERY = gql`
  query SeedUsers {
    users {
      id
      fullName
      email
      memberships {
        companyId
        role
      }
    }
  }
`;

const VIEWER_QUERY = gql`
  query ViewerAndCompanies {
    viewer {
      id
      fullName
      email
      memberships {
        companyId
        role
      }
    }
    companies {
      id
      name
      companyType
      parentId
    }
  }
`;

const DASHBOARD_QUERY = gql`
  query Dashboard($companyId: ID!) {
    leads(companyId: $companyId) {
      id
      title
      contactName
      contactEmail
      status
      scoringStatus
      score
      createdAt
      company {
        id
        name
      }
      createdBy {
        id
        fullName
      }
      activities {
        id
        kind
        note
        createdAt
      }
    }
    deals(companyId: $companyId) {
      id
      name
      stage
      valueCents
    }
    activities(companyId: $companyId) {
      id
      kind
      note
      createdAt
      lead {
        id
        title
      }
    }
  }
`;

const CREATE_LEAD_MUTATION = gql`
  mutation CreateLead($input: CreateLeadInput!) {
    createLead(input: $input) {
      id
      title
      scoringStatus
      score
    }
  }
`;

const WRITE_ROLES = new Set(['PARENT_ADMIN', 'CHILD_MANAGER', 'SALES_REP']);

type Membership = {
  companyId: string;
  role: string;
};

type User = {
  id: string;
  fullName: string;
  email: string;
  memberships: Membership[];
};

type Company = {
  id: string;
  name: string;
  companyType: 'PARENT' | 'CHILD';
  parentId: string | null;
};

type LeadActivity = {
  id: string;
  kind: string;
  note: string;
  createdAt: string;
};

type Lead = {
  id: string;
  title: string;
  contactName: string;
  contactEmail: string;
  status: string;
  scoringStatus: string;
  score: number | null;
  createdAt: string;
  company: {
    id: string;
    name: string;
  };
  createdBy: {
    id: string;
    fullName: string;
  };
  activities: LeadActivity[];
};

type Deal = {
  id: string;
  name: string;
  stage: string;
  valueCents: number;
};

type Activity = {
  id: string;
  kind: string;
  note: string;
  createdAt: string;
  lead: {
    id: string;
    title: string;
  };
};

type ViewerAndCompaniesData = {
  viewer: User;
  companies: Company[];
};

type DashboardData = {
  leads: Lead[];
  deals: Deal[];
  activities: Activity[];
};

function currency(cents: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(cents / 100);
}

function formatRole(role: string) {
  return role
    .toLowerCase()
    .split('_')
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(' ');
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(value));
}

function AuthenticatedDashboard() {
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [title, setTitle] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactEmail, setContactEmail] = useState('');

  const viewerQuery = useQuery<ViewerAndCompaniesData>(VIEWER_QUERY, {
    fetchPolicy: 'network-only',
    nextFetchPolicy: 'network-only',
    notifyOnNetworkStatusChange: true
  });

  const dashboardQuery = useQuery<DashboardData>(DASHBOARD_QUERY, {
    variables: { companyId: selectedCompanyId },
    skip: !selectedCompanyId,
    pollInterval: selectedCompanyId ? 3000 : 0,
    fetchPolicy: 'network-only',
    nextFetchPolicy: 'network-only',
    notifyOnNetworkStatusChange: true
  });

  const [createLead, createLeadState] = useMutation(CREATE_LEAD_MUTATION, {
    onCompleted: () => {
      setTitle('');
      setContactName('');
      setContactEmail('');
      void dashboardQuery.refetch();
    }
  });

  const viewer = viewerQuery.data?.viewer;
  const visibleCompanies = (viewerQuery.data?.companies ?? []).filter((company) => company.companyType === 'CHILD');
  const activeCompany = visibleCompanies.find((company) => company.id === selectedCompanyId);
  const leadCount = dashboardQuery.data?.leads.length ?? 0;
  const dealCount = dashboardQuery.data?.deals.length ?? 0;
  const activityCount = dashboardQuery.data?.activities.length ?? 0;
  const roleLabels = viewer ? Array.from(new Set(viewer.memberships.map((membership) => formatRole(membership.role)))) : [];
  const canCreateLead = viewer?.memberships.some((membership) => WRITE_ROLES.has(membership.role)) ?? false;

  useEffect(() => {
    if (!visibleCompanies.length) {
      setSelectedCompanyId('');
      return;
    }

    if (!visibleCompanies.some((company) => company.id === selectedCompanyId)) {
      setSelectedCompanyId(visibleCompanies[0].id);
    }
  }, [selectedCompanyId, visibleCompanies]);

  async function handleCreateLead(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId || !canCreateLead) {
      return;
    }

    await createLead({
      variables: {
        input: {
          companyId: selectedCompanyId,
          title,
          contactName,
          contactEmail
        }
      }
    });
  }

  if (viewerQuery.error) {
    return (
      <section aria-live="assertive" className="card empty-state error" role="alert">
        <h2>Viewer query failed</h2>
        <p>{viewerQuery.error.message}</p>
      </section>
    );
  }

  if (viewerQuery.loading || !viewer) {
    return (
      <section aria-live="polite" className="card empty-state" role="status">
        <h2>Loading viewer context</h2>
        <p>Fetching roles and visible companies from the federated API.</p>
      </section>
    );
  }

  if (!visibleCompanies.length) {
    return (
      <section aria-live="polite" className="card empty-state" role="status">
        <h2>No child companies are available for this viewer</h2>
        <p>This seeded user does not currently have access to a child-company scope.</p>
      </section>
    );
  }

  if (!selectedCompanyId) {
    return (
      <section aria-live="polite" className="card empty-state" role="status">
        <h2>Preparing company scope</h2>
        <p>Applying the first visible child company before loading CRM data.</p>
      </section>
    );
  }

  return (
    <>
      <section className="grid context-grid">
        <article className="card">
          <p className="eyebrow">Viewer</p>
          <h2>{viewer.fullName}</h2>
          <p className="muted">{viewer.email}</p>
          <p className="supporting-copy">
            Signed in with {viewer.memberships.length} membership{viewer.memberships.length === 1 ? '' : 's'} and{' '}
            {visibleCompanies.length} visible child compan{visibleCompanies.length === 1 ? 'y' : 'ies'}.
          </p>
          <p className="status-line compact">
            <span aria-hidden="true" className={`status-dot ${canCreateLead ? 'allowed' : 'readonly'}`} />
            {canCreateLead ? 'This role can create leads in the current scope.' : 'This role is read-only in CRM.'}
          </p>
          <div aria-label="Viewer roles" className="pill-row">
            {roleLabels.map((role) => (
              <span className="pill" key={role}>
                {role}
              </span>
            ))}
          </div>
        </article>

        <article className="card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Company scope</p>
              <h2>{activeCompany?.name ?? 'Select a child company'}</h2>
            </div>
            <span className="status-chip neutral">{visibleCompanies.length} visible</span>
          </div>
          <label htmlFor="company-scope">Child company</label>
          <select
            aria-describedby="company-scope-help"
            disabled={!visibleCompanies.length}
            id="company-scope"
            value={selectedCompanyId}
            onChange={(event) => setSelectedCompanyId(event.target.value)}
          >
            {visibleCompanies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
          <p className="form-hint" id="company-scope-help">
            Parent admins can move across child companies. Other roles stay limited to their assigned child company.
          </p>
          {activeCompany ? (
            <dl className="summary-list">
              <div>
                <dt>Selected scope</dt>
                <dd>{activeCompany.name}</dd>
              </div>
              <div>
                <dt>Access mode</dt>
                <dd>{visibleCompanies.length > 1 ? 'Cross-child access' : 'Single-child access'}</dd>
              </div>
            </dl>
          ) : null}
        </article>

        <article className="card">
          <p className="eyebrow">Live view</p>
          <h2>What updates here</h2>
          <div className="metric-grid">
            <div className="metric-card">
              <span className="metric-label">Leads</span>
              <strong className="metric-value">{leadCount}</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Deals</span>
              <strong className="metric-value">{dealCount}</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Activities</span>
              <strong className="metric-value">{activityCount}</strong>
            </div>
          </div>
          <p aria-live="polite" className="status-line">
            <span aria-hidden="true" className="status-dot" />
            Polling CRM every 3 seconds for scoring and follow-up updates.
          </p>
        </article>
      </section>

      <section className="grid">
        <article className="card form-card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Create lead</p>
              <h2>{canCreateLead ? 'Start the async workflow' : 'Lead creation is unavailable for this role'}</h2>
            </div>
            <span className={`status-chip ${canCreateLead ? 'pending' : 'neutral'}`}>
              {canCreateLead ? 'LeadCreated to Kafka' : 'Read-only access'}
            </span>
          </div>
          <p className="form-hint" id="lead-form-help">
            {canCreateLead
              ? 'Save a lead in the selected company. The worker scores it asynchronously and writes a follow-up activity. Exact duplicate leads in the same company are rejected.'
              : 'You can review the live CRM state in this scope, but this role cannot create new leads.'}
          </p>
          {canCreateLead ? (
            <form aria-describedby="lead-form-help" onSubmit={handleCreateLead}>
              <label htmlFor="lead-title">Lead title</label>
              <input
                autoComplete="off"
                id="lead-title"
                placeholder="Quarterly renewal opportunity"
                required
                value={title}
                onChange={(event) => setTitle(event.target.value)}
              />

              <label htmlFor="lead-contact-name">Contact name</label>
              <input
                autoComplete="name"
                id="lead-contact-name"
                placeholder="Jordan Rivera"
                required
                value={contactName}
                onChange={(event) => setContactName(event.target.value)}
              />

              <label htmlFor="lead-contact-email">Contact email</label>
              <input
                autoComplete="email"
                id="lead-contact-email"
                placeholder="jordan@example.com"
                required
                type="email"
                value={contactEmail}
                onChange={(event) => setContactEmail(event.target.value)}
              />

              <button disabled={createLeadState.loading || !selectedCompanyId} type="submit">
                {createLeadState.loading ? 'Creating lead...' : 'Create lead'}
              </button>
            </form>
          ) : (
            <div aria-live="polite" className="permission-callout" role="status">
              <p className="permission-title">Read-only role</p>
              <p>
                Switch to <strong>Ben Branch</strong>, <strong>Maya Manager</strong>, <strong>Priya Parent</strong>, or{' '}
                <strong>Sara Sales</strong> to create leads and trigger the Kafka scoring workflow.
              </p>
            </div>
          )}
          {createLeadState.error ? (
            <p className="inline-error" role="alert">
              {createLeadState.error.message}
            </p>
          ) : null}
        </article>

        <article className="card">
          <p className="eyebrow">Workflow checklist</p>
          <h2>What should happen next</h2>
          <ol className="workflow-steps">
            <li>The lead appears immediately in CRM with a pending score.</li>
            <li>The `crm.lead.created` event is published to Kafka.</li>
            <li>The workflow worker scores the lead and creates a follow-up activity.</li>
          </ol>
        </article>
      </section>

      {dashboardQuery.loading && !dashboardQuery.data ? (
        <section aria-live="polite" className="card empty-state" role="status">
          <h2>Loading CRM data</h2>
          <p>Fetching leads, activities, and deals for the selected child company.</p>
        </section>
      ) : dashboardQuery.error ? (
        <section aria-live="assertive" className="card empty-state error" role="alert">
          <h2>CRM query failed</h2>
          <p>{dashboardQuery.error.message}</p>
        </section>
      ) : (
        <>
          <section aria-busy={dashboardQuery.loading} className="card">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Leads</p>
                <h2>{activeCompany ? `${activeCompany.name} pipeline` : 'Current pipeline'}</h2>
                <p className="section-subtitle">
                  {leadCount} lead{leadCount === 1 ? '' : 's'} in scope. Scores refresh automatically.
                </p>
              </div>
              <span className="muted">{dashboardQuery.loading ? 'Refreshing...' : 'Live data'}</span>
            </div>
            {(dashboardQuery.data?.leads ?? []).length ? (
              <div className="lead-grid">
                {(dashboardQuery.data?.leads ?? []).map((lead) => (
                  <article className="lead-card" key={lead.id}>
                    <div className="lead-topline">
                      <div>
                        <h3>{lead.title}</h3>
                        <p>
                          {lead.contactName} · {lead.contactEmail}
                        </p>
                      </div>
                      <span className={`status-chip ${lead.scoringStatus.toLowerCase()}`}>{lead.scoringStatus}</span>
                    </div>
                    <p className="lead-caption">Created {formatDateTime(lead.createdAt)}</p>
                    <dl className="meta-grid">
                      <div>
                        <dt>Owner</dt>
                        <dd>{lead.createdBy.fullName}</dd>
                      </div>
                      <div>
                        <dt>Score</dt>
                        <dd>{lead.score ?? 'Pending'}</dd>
                      </div>
                      <div>
                        <dt>Status</dt>
                        <dd>{lead.status}</dd>
                      </div>
                      <div>
                        <dt>Company</dt>
                        <dd>{lead.company.name}</dd>
                      </div>
                    </dl>
                    <div aria-label={`Workflow activities for ${lead.title}`} className="activity-list">
                      <p className="list-heading">Workflow activities</p>
                      {lead.activities.length ? (
                        lead.activities.map((activity) => (
                          <div className="activity-row" key={activity.id}>
                            <div>
                              <span>{activity.kind}</span>
                              <p>{activity.note}</p>
                            </div>
                            <time dateTime={activity.createdAt}>{formatDateTime(activity.createdAt)}</time>
                          </div>
                        ))
                      ) : (
                        <p className="muted">No workflow activities yet.</p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-list">
                No leads in this company yet. Create one above to watch the scoring workflow update the dashboard.
              </div>
            )}
          </section>

          <section className="grid">
            <article className="card">
              <p className="eyebrow">Deals</p>
              <h2>Existing revenue work</h2>
              <p className="section-subtitle">Current open deal records for the selected child company.</p>
              {(dashboardQuery.data?.deals ?? []).length ? (
                <div className="list-block">
                  {(dashboardQuery.data?.deals ?? []).map((deal) => (
                    <div className="list-row" key={deal.id}>
                      <div>
                        <strong>{deal.name}</strong>
                        <p>{deal.stage}</p>
                      </div>
                      <span>{currency(deal.valueCents)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-list">No deals are currently seeded for this company.</div>
              )}
            </article>

            <article className="card">
              <p className="eyebrow">Activities</p>
              <h2>Recent follow-up work</h2>
              <p className="section-subtitle">Cross-lead activity generated by CRM users and workflow automation.</p>
              {(dashboardQuery.data?.activities ?? []).length ? (
                <div className="list-block">
                  {(dashboardQuery.data?.activities ?? []).map((activity) => (
                    <div className="list-row" key={activity.id}>
                      <div>
                        <strong>{activity.kind}</strong>
                        <p>{activity.note}</p>
                      </div>
                      <span>{activity.lead.title}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-list">No activities have been recorded for this company yet.</div>
              )}
            </article>
          </section>
        </>
      )}
    </>
  );
}

export default function App() {
  const selectedUserId = useReactiveVar(selectedUserIdVar);
  const usersQuery = useQuery<{ users: User[] }>(USERS_QUERY);
  const [isSwitchingUser, setIsSwitchingUser] = useState(false);
  const selectedUser = (usersQuery.data?.users ?? []).find((user) => user.id === selectedUserId);

  function switchUser(nextUserId: string | null) {
    setIsSwitchingUser(true);
    persistSelectedUserId(nextUserId);
    reloadPage();
  }

  return (
    <div className="shell">
      <div className="ambient ambient-left" />
      <div className="ambient ambient-right" />
      <main className="layout">
        <header className="hero card">
          <div className="hero-copy">
            <p className="eyebrow">Event-driven CRM challenge</p>
            <h1>RelayCRM</h1>
            <p className="lede">
              A small federated CRM that shows hierarchy-aware visibility, server-side authorization, and Kafka-driven
              eventual consistency.
            </p>
            <ol className="hero-steps">
              <li>Choose a seeded demo user.</li>
              <li>Review the allowed child-company scope.</li>
              <li>Create a lead and watch the async score and activity update.</li>
            </ol>
          </div>

          <section aria-labelledby="demo-user-heading" className="selector-panel">
            <div>
              <p className="eyebrow">Session</p>
              <h2 id="demo-user-heading">Switch demo user</h2>
              <p className="form-hint" id="demo-user-help">
                Changing the user reloads the dashboard with that person&apos;s roles, company scope, and live CRM data.
              </p>
            </div>

            <label htmlFor="demo-user">Demo user</label>
            <select
              aria-describedby="demo-user-help demo-user-status"
              disabled={usersQuery.loading || isSwitchingUser}
              id="demo-user"
              value={selectedUserId ?? ''}
              onChange={(event) => {
                const nextUserId = event.target.value;
                if (!nextUserId) {
                  void switchUser(null);
                  return;
                }

                void switchUser(nextUserId);
              }}
            >
              <option value="">Select a seeded user</option>
              {(usersQuery.data?.users ?? []).map((user) => (
                <option key={user.id} value={user.id}>
                  {user.fullName}
                </option>
              ))}
            </select>

            <div className="selector-footer">
              {selectedUserId ? (
                <button className="ghost-button" disabled={isSwitchingUser} onClick={() => void switchUser(null)} type="button">
                  Clear viewer
                </button>
              ) : null}

              <p aria-live="polite" className="assistive-note" id="demo-user-status" role="status">
                {isSwitchingUser
                  ? 'Switching viewer and refreshing data...'
                  : usersQuery.loading
                    ? 'Loading seeded users...'
                    : selectedUser
                      ? `Current viewer: ${selectedUser.fullName}`
                      : 'No viewer selected yet.'}
              </p>
            </div>

            {usersQuery.error ? (
              <p className="inline-error" role="alert">
                {usersQuery.error.message}
              </p>
            ) : null}
          </section>
        </header>

        {!selectedUserId ? (
          <section aria-live="polite" className="card empty-state" role="status">
            <h2>Pick a seeded user to begin</h2>
            <p>Choose one of the seeded roles to load viewer context, access scope, and live CRM data.</p>
            <ol className="empty-steps">
              <li>Admins can move between child companies they are allowed to see.</li>
              <li>Managers and reps stay locked to their assigned child company.</li>
              <li>Lead scoring updates arrive asynchronously after the record is created.</li>
            </ol>
          </section>
        ) : (
          <AuthenticatedDashboard key={selectedUserId} />
        )}
      </main>
    </div>
  );
}
