# ============================================
# Base stage - Bun runtime
# ============================================
FROM oven/bun:1 AS base

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# ============================================
# Development stage
# ============================================
FROM base AS development

# Install all dependencies
RUN bun install

# Copy source code
COPY . .

EXPOSE 5173

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

# ============================================
# Build stage for production
# ============================================
FROM base AS build

RUN bun install --frozen-lockfile

COPY . .

RUN bun run build

# ============================================
# Production stage
# ============================================
FROM oven/bun:1-slim AS production

WORKDIR /app

COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules

EXPOSE 4173

CMD ["bun", "run", "preview", "--host", "0.0.0.0"]
