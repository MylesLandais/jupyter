# ComfyUI on RunPod Serverless

Serverless image generation using ComfyUI workflows on RunPod infrastructure.

## Architecture

```
jupyter workspace                RunPod Serverless
  notebooks/comfy/                 Endpoint: ufz90md8f6n5kx
    runpod_runner.py  ----API---->   handler.py (MylesLandais/ComfyUI)
    runpod_quickstart.ipynb          ComfyUI + custom nodes
                                     /runpod-volume (network volume 4wdzn7kf5p)
  data/comfy-workflows/                models/diffusion_models/
    manifest.json                      models/clip/
    z_image.json (API format)          models/vae/
    templates/ (frontend format)

  scripts/
    hydrate_runpod_s3.py           RunPod S3 API (eur-no-1)
    hydrate_volume.py              On-pod hydration script
```

## Quick Start

```python
from runpod_runner import RunPodWorkflowRunner, run_workflow

# One-liner
results = run_workflow('data/comfy-workflows/z_image.json', seed=42)

# With prompt override
runner = RunPodWorkflowRunner()
workflow = runner.load_workflow('data/comfy-workflows/z_image.json')
# ... modify nodes ...
workflow = runner.update_seed(workflow, seed=12345)
payload = runner.wrap_workflow(workflow)
job_id = runner.submit_job(payload)
status = runner.poll_status(job_id)
files = runner.save_outputs(status, 'outputs/my_run')
```

See `notebooks/comfy/runpod_quickstart.ipynb` for a full walkthrough.

## Workflow Dataset

Workflows live in `data/comfy-workflows/`. Two formats:

- **API format** (root level): flat dict of node_id -> {class_type, inputs}. This is what the runner sends to RunPod. Node connections use `["node_id", output_index]` arrays.
- **Frontend format** (`templates/`): LiteGraph/UI format with nodes array, links, positions. Useful for importing into the ComfyUI web interface. Not directly submittable to the API.

The `manifest.json` maps models to HuggingFace sources, S3 paths, and workflow associations.

### Current Workflows

| Workflow | File | Models | Notes |
|----------|------|--------|-------|
| Z-Image base | `z_image.json` | z_image_bf16, qwen_3_4b, ae | 30-50 steps, CFG 3-5 |
| Z-Image turbo | TBD | z_image_turbo_bf16, qwen_3_4b, ae | Uses custom bundled node in template |

### Adding a Workflow

1. Export the API format from ComfyUI (Save API button in the web UI) or convert from frontend format manually.
2. Place in `data/comfy-workflows/` with a descriptive name.
3. Add model entries to `manifest.json` if new models are required.
4. Hydrate the volume/bucket with any new models.

## Model Management

### Network Volume

| Property | Value |
|----------|-------|
| Volume ID | `4wdzn7kf5p` |
| Name | `comfy_data` |
| Size | 64 GB |
| Region | EUR-NO-1 |
| Mount | `/runpod-volume` (serverless), `/workspace` (pods) |

### Current Models (~31 GB)

| Model | Size | Path on Volume |
|-------|------|----------------|
| z_image_bf16.safetensors | 11.46 GB | models/diffusion_models/ |
| z_image_turbo_bf16.safetensors | 11.46 GB | models/diffusion_models/ |
| qwen_3_4b.safetensors | 7.49 GB | models/clip/ |
| ae.safetensors | 0.31 GB | models/vae/ |

### Hydration

When the volume is empty or needs new models:

**On-pod (fast, same datacenter):**

```bash
# Spin up a pod in EUR-NO-1 with the network volume
# SSH in, then:
pip install huggingface_hub
python3 /runpod-volume/scripts/hydrate.py
```

The hydration script is kept on the volume at `scripts/hydrate.py`. Source is at `scripts/hydrate_volume.py` in this repo.

**Remote (slow, any machine):**

```bash
python scripts/hydrate_runpod_s3.py --dry-run   # preview
python scripts/hydrate_runpod_s3.py              # upload all
python scripts/hydrate_runpod_s3.py --list       # check bucket
```

S3 uploads to EUR-NO-1 are slow (~1 GB/13 min). Use the on-pod method for initial setup.

## Worker Repository

The ComfyUI worker is a fork at `MylesLandais/ComfyUI` branch `feature/runpod-worker`.

Key files in the worker:
- `Dockerfile.runpod` -- container build with custom nodes
- `handler.py` -- RunPod serverless handler (websocket-based, handles images + audio)
- `src/extra_model_paths.yaml` -- maps `/runpod-volume/models/` subdirectories
- `src/start.sh` -- container entrypoint

Pushing to `feature/runpod-worker` with changes in `src/`, `handler.py`, or `Dockerfile.runpod` triggers a GitHub Actions workflow that creates a release and kicks off a RunPod image rebuild.

Rebuilds take 15-60 minutes. Deploying a new endpoint can be faster than waiting for an in-place rebuild.

## Credentials

All credentials are in `.env`:

```
RUNPOD_API_KEY          # API access
RUNPOD_ENDPOINT_ID      # serverless endpoint
RUNPOD_S3_ENDPOINT      # https://s3api-eur-no-1.runpod.io
RUNPOD_S3_ACCESS_KEY    # S3 auth
RUNPOD_S3_SECRET_KEY    # S3 auth
RUNPOD_S3_BUCKET        # 4wdzn7kf5p
```

## Troubleshooting

See `RUNPOD_TROUBLESHOOTING.md` in the worker repo for build/deployment issues.

Common issues in this workspace:
- **ModuleNotFoundError**: Use `.venv/bin/python3` or ensure the venv is active.
- **Models not found**: Check that `extra_model_paths.yaml` in the worker maps all required directories. See the worker repo's troubleshooting doc.
- **Slow S3 uploads**: Expected for EUR-NO-1. Use on-pod hydration instead.
- **HF cache permission denied**: The hydration script falls back to `cache/huggingface/` in the project root if `~/.cache/huggingface` is not writable.
