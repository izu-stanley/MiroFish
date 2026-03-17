# MiroFish - Full stack (frontend + backend)

FROM python:3.11-slim-bookworm

# Install Node.js 18+, curl, build deps (gcc/python3-dev for psutil)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gcc python3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Cursor Agent CLI (for ontology, entity extraction, reports)
# Requires CURSOR_API_KEY env var at runtime for API access
RUN curl -fsS https://cursor.com/install | bash
ENV PATH="/root/.local/bin:${PATH}"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json* ./
COPY frontend/package.json frontend/package-lock.json* ./frontend/
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Install Node dependencies (npm install if lock is stale)
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi \
    && if [ -f frontend/package-lock.json ]; then npm ci --prefix frontend; else npm install --prefix frontend; fi

# Install Python dependencies (Python 3.11 has tiktoken wheels)
RUN cd backend && uv sync --frozen

# Copy source
COPY . .

# Create uploads dir for volume mount
RUN mkdir -p backend/uploads

EXPOSE 3000 5001

# Start both frontend and backend
CMD ["npm", "run", "dev"]
