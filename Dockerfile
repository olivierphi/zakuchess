# from https://github.com/vercel/next.js/blob/canary/examples/with-docker/Dockerfile

FROM node:18-bookworm-slim AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Assets downloading
FROM base AS assets_download

# By having a separate build stage for downloading assets, we can cache them
# as long as the `assets-download-and-copy.ts` script doesn't change.

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY scripts/assets-download-and-copy.ts scripts/assets-download-and-copy.ts

RUN node_modules/.bin/tsx scripts/assets-download-and-copy.ts

# Rebuild the source code only when needed
FROM base AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    make \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=deps /app/node_modules ./node_modules
COPY --from=assets_download /app/static ./static
COPY . .

RUN make build

# Production image, copy all the files and run the server
FROM base AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 zakuchess

COPY --from=deps --chown=nextjs:nodejs /app/package.json ./package.json
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/src ./src
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/Makefile ./Makefile
COPY --from=builder --chown=nextjs:nodejs /app/tsconfig.json ./tsconfig.json

USER zakuchess

EXPOSE 3000

ENV NODE_ENV=production
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=3000

CMD ["./node_modules/.bin/tsx", "src/server-nodejs.ts"]
