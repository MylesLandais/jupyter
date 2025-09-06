# Nebula Jupyter System

> !Important: Organization is no longer accepting pull requests to be made with any emojis, please keep this in mind before submitting to code review channels
> Please read `CONTRIBUTING.md` for more information on getting involved with the project

## Latest Development Session (January 6, 2025)

**ASR Model Evaluation System Implementation**
- Built comprehensive ASR (Automatic Speech Recognition) evaluation framework
- Implemented model adapters for FasterWhisper and OLMoASR (HuggingFace Whisper models)
- Created leaderboard generation system with PostgreSQL integration
- Developed Docker-based testing environment with CUDA support
- Added secret scanning and repository security measures
- Successfully tested multiple Whisper model variants on Vaporeon copypasta dataset

**Key Achievements:**
- Complete spec-driven development workflow (Requirements → Design → Tasks → Implementation)
- Working model comparison with WER/CER metrics and processing time analysis
- Database storage for evaluation results and historical tracking
- Containerized development environment for reproducible testing

## ASR Hearing Benchmark Roadmap

### Phase 1: Foundation (Completed)
- [x] Core ASR evaluation framework
- [x] Model adapter architecture (FasterWhisper, OLMoASR)
- [x] Basic metrics calculation (WER, CER, processing time)
- [x] PostgreSQL storage and leaderboard system
- [x] Docker development environment

### Phase 2: Production Readiness Testing (Next 2-4 weeks)
- [ ] **Robustness Testing**
  - Audio quality degradation tests (noise, compression, distortion)
  - Multiple speaker scenarios and accent variations
  - Real-world audio conditions (background noise, reverb, etc.)
  
- [ ] **Performance Benchmarking**
  - Latency requirements for real-time applications
  - Memory usage and resource consumption analysis
  - Concurrent processing capabilities
  - Batch processing optimization

- [ ] **Model Coverage Expansion**
  - OpenAI Whisper API integration via OpenRouter
  - Additional open-source models (Wav2Vec2, SpeechT5)
  - Specialized domain models (medical, legal, technical)

### Phase 3: Advanced Evaluation Metrics (4-6 weeks)
- [ ] **Semantic Understanding**
  - Key phrase detection accuracy
  - Intent recognition in transcribed text
  - Domain-specific terminology handling
  
- [ ] **Production Scenarios**
  - Meeting transcription accuracy
  - Phone call quality audio processing
  - Streaming vs batch processing comparison
  - Multi-language support evaluation

### Phase 4: Automated Testing Pipeline (6-8 weeks)
- [ ] **Continuous Integration**
  - Automated model regression testing
  - Performance monitoring and alerting
  - A/B testing framework for model updates
  
- [ ] **Dataset Management**
  - Synthetic audio generation for edge cases
  - Privacy-compliant test dataset creation
  - Benchmark dataset standardization

### Phase 5: Production Deployment Support (8-10 weeks)
- [ ] **Model Selection Framework**
  - Cost vs accuracy optimization
  - Deployment environment recommendations
  - Model switching and fallback strategies
  
- [ ] **Monitoring and Observability**
  - Real-time performance tracking
  - Error pattern analysis
  - User feedback integration

## Current System Components

### ASR Evaluation Framework
- **Model Adapters**: Unified interface for different ASR models
- **Metrics Engine**: WER, CER, BLEU score calculation
- **Leaderboard System**: PostgreSQL-backed ranking and comparison
- **Test Suite**: Comprehensive model availability and functionality testing

### Development Tools
- **Docker Environment**: CUDA-enabled containers for GPU acceleration
- **Secret Scanning**: Talisman pre-commit hooks for security
- **Spec-Driven Development**: Kiro AI assistant integration for structured development

## Legacy Components

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

This repository serves as a comprehensive development and testing environment for AI/ML workflows, with a primary focus on **ASR (Automatic Speech Recognition) model evaluation and benchmarking**. The system provides tools for evaluating, comparing, and selecting ASR models for production deployment.

### Core Focus: ASR Model Evaluation
The primary objective is building a robust evaluation framework for "hearing" systems - testing ASR models for production readiness across various real-world scenarios, audio conditions, and performance requirements.

### Key Services and Libraries:
- **ASR Models**: FasterWhisper, OLMoASR, OpenAI Whisper (via OpenRouter)
- **Evaluation Metrics**: WER, CER, BLEU scores, processing time analysis
- **Storage**: PostgreSQL with pgvector for results and leaderboards
- **Infrastructure**: Docker containers with CUDA support
- **Cloud Services**: RunPod GPU instances, OpenRouter API access
- **Development**: JupyterLab environment with VS Code integration

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
├── .devcontainer/            # VS Code dev container configuration
├── .kiro/                    # Kiro AI assistant specs and configurations
│   └── specs/asr-model-evaluation-system/  # ASR evaluation spec
├── asr_evaluation/           # Core ASR evaluation framework
│   ├── adapters/            # Model adapters (FasterWhisper, OLMoASR)
│   ├── core/                # Interfaces and configuration
│   ├── metrics/             # Evaluation metrics calculation
│   ├── storage/             # PostgreSQL integration
│   └── utils/               # Utility functions
├── tests/                   # Comprehensive test suite
├── transcriptions/          # Evaluation datasets (Vaporeon copypasta)
├── notebooks/               # Jupyter notebooks (git tracked)
├── docker-compose.yml       # Multi-service container setup
├── start.sh                # Development environment setup
├── asr_leaderboard.py      # Main leaderboard generation script
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

## ASR Evaluation Quick Start

### Running the Leaderboard System

1. **Start the development environment**:
   ```bash
   ./start.sh
   ```

2. **Run ASR model evaluation** (inside Docker container):
   ```bash
   docker exec -it jupyter-jupyterlab-1 python /home/jovyan/workspaces/asr_leaderboard.py
   ```

3. **View results**:
   - Console output shows real-time evaluation progress
   - Results saved to `results/transcriptions/` directory
   - Database leaderboard accessible via PostgreSQL

### Testing Individual Models

```bash
# Test OLMoASR adapter
docker exec -it jupyter-jupyterlab-1 python /home/jovyan/workspaces/test_olmoasr.py

# Run comprehensive test suite
docker exec -it jupyter-jupyterlab-1 python /home/jovyan/workspaces/run_tests.py
```

### Current Evaluation Dataset

The system includes the **Vaporeon Copypasta Dataset** for initial testing:
- 164 seconds of clear English speech
- Known reference transcription for WER/CER calculation
- Challenging content with internet meme terminology
- Located in `transcriptions/` directory

### Model Performance (Latest Results)

| Model | WER | Processing Time | Status |
|-------|-----|----------------|---------|
| faster-whisper-base | ~15-25% | ~2-3s | Working |
| faster-whisper-small | ~20-30% | ~1-2s | Working |
| hf-whisper-base | ~15-25% | ~3-4s | Working |
| hf-whisper-tiny | ~40-50% | ~0.7s | Working (limited accuracy) |

*Results may vary based on hardware and model availability*