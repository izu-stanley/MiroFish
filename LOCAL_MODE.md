# MiroFish Local Mode

Run MiroFish on your laptop or offline—**no Zep Cloud** or other external graph services required.

## Features

- **Zero external dependencies**: Graph data stored in local JSON files
- **Lower resource usage**: Single LLM call for entity extraction (instead of Zep batch processing)
- **Same workflow**: Upload → Ontology → Graph → Simulation → Report

## Quick Start

### 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
# Local LLM (Ollama recommended)
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=smollm:360m

# Enable local mode
USE_LOCAL_MODE=true
```

### 2. Install Ollama (required)

```bash
# macOS
brew install ollama
ollama serve
ollama pull smollm:360m
```

### 3. Install dependencies and start

```bash
npm run setup:all
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:5001

## Architecture

| Item | This setup |
|------|------------|
| LLM | Ollama (local only) |
| Graph storage | Local `backend/uploads/local_graphs/` |
| Entity extraction | Single LLM call (~30k chars max) |
| Report search | Local keyword search |

## Resource recommendations

- **Document length**: Keep under ~30k characters; longer docs are truncated
- **Entity count**: Max ~50 entities per extraction
- **Simulation rounds**: Keep under 40 rounds to limit LLM usage

## Troubleshooting

**Q: Startup error "ZEP_API_KEY not configured"**  
A: Ensure `USE_LOCAL_MODE=true` is set in `.env`.

**Q: Very few entities extracted**  
A: Check that the LLM is running (e.g. Ollama), or try a shorter document.

**Q: No results when generating reports**  
A: Local mode uses keyword search; try more specific keywords.
