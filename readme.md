# Nebula Jupyter System

> !Important: Organization is no longer accepting pull requests to be made with any emojis, please keep this in mind before submitting to code review channels
> Please read `CONTRIBUTING.md` for more information on getting involved with the project

## Roadmap

- **High priority** Using comfy via api-websockets
- pgvector
- Fixing VLLM demo
- Image Datasets
- FineTuning diffusion models

## Current Notebooks & Scripts

- cleanup runpod instances
- init runpod ollama
- openrouter_tool_use
- dataset_pipeline
    - Workflows for creating/updating and tracking datasets across versioning
- Finetune_Wan22
- Finetune_QwenImg
- bench_eval_vlm_responses
    - used for shooting out different language models across open router or local/ollama+hf data

## Environment Configuration

Create a `.env` file from `.env.example` and configure the following:

```bash
RUNPOD_API_KEY=rpa_....
OPENROUTER_API_KEY=sk-or-v1-..........
FINNHUB_API_KEY=....
# TODO: Add HF token configurations
```

**Additional Services**: HuggingFace, Github, and Runpod all leverage shared SSH keys for system access.

**TODO Items**:
- Update repo with HF token configurations
- RunPod Instance/Backup -- try-again/Restore loops for runpod (occasionally our spot instances break and we're too poor & budget to restart)

## About

This repository serves as a development and testing environment for various AI projects. 

The project relies on several key services and libraries:
- **Runpod**: Cloud GPU instances
- **VLLM**: High-performance LLM inference
- **Ollama**: Local LLM deployment
- **OpenRouter**: LLM API gateway
- **Langchain**: LLM application framework
- **pgvector**: Vector database for embeddings

## Development Environment Setup

This project uses a containerized development environment with JupyterLab and PostgreSQL with pgvector extension.

### Prerequisites

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Install [Visual Studio Code](https://code.visualstudio.com/)
- Install the [VS Code Remote Development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

### Quick Start

1. **Clone and setup environment**:
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

2. **Create notebooks directory**:
   ```bash
   mkdir -p notebooks
   ```

3. **Start the development environment**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   The script will:
   - Build and start all Docker services
   - Display the JupyterLab URL with access token
   - Show helpful commands for management

4. **Open in VS Code** (optional):
   - Open the project folder in VS Code
   - Use Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
   - Select **"Dev Containers: Reopen in Container"**

### Project Structure

```
jupyter/
├── .devcontainer/
│   └── devcontainer.json     # VS Code dev container config
├── notebooks/                # Your Jupyter notebooks (git tracked)
├── docker-compose.yml        # Multi-service container setup
├── Dockerfile               # JupyterLab container definition
├── start.sh                # Quick start script
├── .env                    # Environment variables (create from .env.example)
└── README.md
```

### Services

- **JupyterLab**: Available at `http://localhost:8888` (token provided by start.sh)
- **PostgreSQL + pgvector**: Available at `localhost:5432`
  - Database: `jupyter-dev`
  - User: `postgres`
  - Password: `password` (change in production)

### Management Commands

```bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Shell into JupyterLab container
docker compose exec jupyterlab bash

# Restart services
docker compose restart
```

### Git Integration

Notebooks created in the `notebooks/` directory are automatically available on your host machine and can be committed to git normally. This allows for proper version control of your work.