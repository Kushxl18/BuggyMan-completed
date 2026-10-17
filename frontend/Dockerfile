# ============================================================================
# BuggyMan Frontend Multi-Stage Production Dockerfile
# Stage 1: Build production React bundle with Vite
# Stage 2: Serve optimized assets with Nginx & SPA reverse proxy
# ============================================================================

# --- Stage 1: Builder ---
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package*.json ./
RUN npm install

# Copy application source
COPY . .

# Build production distribution
RUN npm run build

# --- Stage 2: Production Nginx Server ---
FROM nginx:alpine

# Remove default nginx static site
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled SPA bundle from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with SPA routing & /api proxying
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
