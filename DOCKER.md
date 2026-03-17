# Run MiroFish in Docker

Everything runs in Docker—nothing on your host except Docker itself.

## Quick start

```bash
# 1. Start services
docker compose up -d

# 2. Pull the LLM model (one-time, ~230MB for SmolLM-360M)
docker exec mirofish-ollama ollama pull smollm:360m

# 3. Ready
# Frontend: http://localhost:7599
# Backend:  http://localhost:5001
```

## Usage

- **Frontend**: http://localhost:7599
- **Backend API**: http://localhost:5001

## Services

| Service | Port | Purpose |
|---------|------|---------|
| mirofish | 7599, 5001 | Web app + API |
| ollama | 11434 | Local LLM |

## Commands

```bash
# View logs
docker compose logs -f

# Stop
docker compose down

# Stop and remove Ollama model data
docker compose down -v
```

## First run

On first `docker compose up`, MiroFish builds from the local Dockerfile. After pulling the model, upload a document and run a simulation.
