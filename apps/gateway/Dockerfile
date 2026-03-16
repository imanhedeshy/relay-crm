FROM node:20-alpine

WORKDIR /workspace

COPY package.json package.json
COPY package-lock.json package-lock.json
COPY apps/gateway/package.json apps/gateway/package.json
COPY apps/web/package.json apps/web/package.json

RUN npm ci

COPY . .

WORKDIR /workspace/apps/gateway

EXPOSE 4000

CMD ["npm", "run", "start"]
