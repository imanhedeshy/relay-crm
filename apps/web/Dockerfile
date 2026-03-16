FROM node:20-alpine

WORKDIR /workspace

ARG VITE_GRAPHQL_URL=http://localhost:4000/graphql

COPY package.json package.json
COPY package-lock.json package-lock.json
COPY apps/web/package.json apps/web/package.json
COPY apps/gateway/package.json apps/gateway/package.json

RUN npm ci

COPY . .

WORKDIR /workspace/apps/web

ENV VITE_GRAPHQL_URL=${VITE_GRAPHQL_URL}

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "preview"]
