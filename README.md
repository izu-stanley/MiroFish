<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="MiroFish Logo" width="75%"/>

<a href="https://trendshift.io/repositories/16144" target="_blank"><img src="https://trendshift.io/api/badge/repositories/16144" alt="666ghj%2FMiroFish | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

A Simple and Universal Swarm Intelligence Engine, Predicting Anything
</br>
<em>A Simple and Universal Swarm Intelligence Engine, Predicting Anything</em>

<a href="https://www.shanda.com/" target="_blank"><img src="./static/image/shanda_logo.png" alt="666ghj%2MiroFish | Shanda" height="40"/></a>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/MiroFish?style=flat-square&color=DAA520)](https://github.com/666ghj/MiroFish/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/666ghj/MiroFish)

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com/channels/1469200078932545606/1469201282077163739)
[![X](https://img.shields.io/badge/X-Follow-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/mirofish_ai)
[![Instagram](https://img.shields.io/badge/Instagram-Follow-E4405F?style=flat-square&logo=instagram&logoColor=white)](https://www.instagram.com/mirofish_ai/)

[English](./README.md) | [中文](./README-ZH.md)

</div>

## Overview

**MiroFish** is a next-generation AI prediction engine powered by multi-agent technology. By extracting seed information from the real world (breaking news, policy drafts, financial signals), it builds a high-fidelity parallel digital world. Thousands of agents with independent personalities, long-term memory, and behavioral logic interact and evolve. You can inject variables from a "God's-eye view" to predict outcomes—**rehearse the future in a digital sandbox**.

> Upload seed materials (reports or stories) and describe your prediction in natural language.  
> MiroFish returns a detailed prediction report and an interactive digital world.

### Vision

MiroFish creates a swarm intelligence mirror of reality. By capturing collective emergence from individual interactions, we go beyond traditional prediction:

- **Macro**: A rehearsal lab for decision-makers—test policies and PR at zero risk
- **Micro**: A creative sandbox for users—simulate novel endings or explore scenarios

## Live Demo

Try the online demo: [mirofish-live-demo](https://666ghj.github.io/mirofish-demo/)

## Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/运行截图1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

## Demo Videos

### 1. Wuhan University Public Opinion Simulation

<div align="center">
<a href="https://www.bilibili.com/video/BV1VYBsBHEMY/" target="_blank"><img src="./static/image/武大模拟演示封面.png" alt="MiroFish Demo Video" width="75%"/></a>

Click to watch the full demo
</div>

### 2. Dream of the Red Chamber Lost Ending Simulation

<div align="center">
<a href="https://www.bilibili.com/video/BV1cPk3BBExq" target="_blank"><img src="./static/image/红楼梦模拟推演封面.jpg" alt="MiroFish Demo Video" width="75%"/></a>

Click to watch MiroFish predict the lost ending from the first 80 chapters
</div>

## Workflow

1. **Graph Building**: Seed extraction & memory injection & GraphRAG
2. **Environment Setup**: Entity extraction & persona generation & config
3. **Simulation**: Dual-platform parallel simulation & temporal memory
4. **Report**: ReportAgent with tools for deep interaction
5. **Interaction**: Chat with agents & ReportAgent

## Quick Start

### Source deployment (recommended)

#### Prerequisites

| Tool | Version | Description | Check |
|------|---------|-------------|-------|
| **Node.js** | 18+ | Frontend runtime (includes npm) | `node -v` |
| **Python** | ≥3.11, ≤3.12 | Backend runtime | `python --version` |
| **uv** | latest | Python package manager | `uv --version` |

#### 1. Configure environment variables

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
```

**Environment variables (CLI mode):**

```env
# Cursor Agent CLI - main brain (replaces Ollama)
# Install: curl https://cursor.com/install -fsS | bash
CURSOR_AGENT_PATH=cursor-agent
USE_LOCAL_MODE=true
```

#### 2. Install dependencies

```bash
# Install all (root + frontend + backend)
npm run setup:all
```

Or step by step:

```bash
# Node deps (root + frontend)
npm run setup

# Python deps (backend, creates venv)
npm run setup:backend
```

#### 3. Start services

```bash
# Start frontend and backend (from project root)
npm run dev
```

**URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Start separately:**

```bash
npm run backend   # backend only
npm run frontend  # frontend only
```

#### 4. CLI mode (no UI)

Use Cursor Agent as the brain—no Ollama or cloud services:

```bash
# Install Cursor Agent CLI
curl https://cursor.com/install -fsS | bash

# Run full pipeline (seed files to report)
npm run run -- <project-dir> -r "simulation requirement description"

# Examples
npm run run -- ./my-docs -r "Predict campus event outcomes"
npm run run -- . --seed-file doc.md -r "Simulate social media response" -o report.md
```

### Docker deployment

**Prerequisites:** Docker and Docker Compose only—no Python, Node, or uv required.

```bash
# 1. Configure env (same as source deployment)
cp .env.example .env

# 2. Build and start the web app
docker compose up -d
```

Reads `.env` from project root; maps ports 3000 (frontend) and 5001 (backend).

**Trigger the pipeline from the host (no local installs):**

Use `run.sh` to run the full pipeline inside Docker. Place seed files (.md, .txt, .pdf) in your project directory.

```bash
# Run pipeline (project dir must contain seed files)
./run.sh ./my-project -r "Simulate campus event outcomes"

# Write report to file in project dir
./run.sh ./my-project -r "Predict campus event outcomes" -o report.md
```

The script mounts your project directory into the container and shares outputs with the web app via the `backend/uploads` volume.

## Join the Conversation

<div align="center">
<img src="./static/image/QQ群.png" alt="QQ Group" width="60%"/>
</div>

The MiroFish team is recruiting. If you're interested in multi-agent applications, send your resume to **mirofish@shanda.com**

## Acknowledgments

**MiroFish is supported and incubated by Shanda Group.**

The simulation engine is powered by **[OASIS](https://github.com/camel-ai/oasis)**. Thanks to the CAMEL-AI team for their open-source contributions.

## Project Statistics

<a href="https://www.star-history.com/#666ghj/MiroFish&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
 </picture>
</a>
