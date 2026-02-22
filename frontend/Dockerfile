FROM node:20-slim

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Use a specific store path to avoid conflicts
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# Copy the rest of the app, ensuring node_modules is ignored by .dockerignore
COPY . .

EXPOSE 3000

# Run in dev mode with host binder for vite
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]
