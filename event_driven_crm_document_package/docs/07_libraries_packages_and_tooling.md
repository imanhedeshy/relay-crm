# Recommended Libraries and Packages

## Root / workspace
- `nx`
- `@nx/js`
- `@nx/react`
- `@nx/vite`
- `typescript`

## Frontend (`apps/web`)
- `react`
- `react-dom`
- `react-router-dom`
- `@apollo/client`
- `graphql`
- `vite`
- `@vitejs/plugin-react`
- optional:
  - `zod`
  - `clsx`

## Gateway (`apps/gateway`)
- `@apollo/server`
- `@apollo/gateway`
- `graphql`
- `express`
- `cors`
- `tsx`
- `typescript`

## Python services
- `Django`
- `ariadne`
- `psycopg[binary]`
- `python-dotenv`
- `gunicorn`

## Async worker
- `confluent-kafka`
- `tenacity`
- `structlog`

## Why Ariadne
Ariadne is practical because it is schema-first, easy to keep clean and understandable, and a good fit for small challenge services.

## Why not Celery
Kafka is a challenge requirement. Using Celery as the primary async mechanism would dilute the point.
