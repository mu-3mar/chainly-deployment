# Chainly AI

Production-oriented **CPU-only** computer vision service: **FastAPI** exposes a multi-session API, **Ultralytics YOLO** runs box and defect detection, and **WebRTC** streams annotated video. Configuration and secrets stay outside the image and are mounted or copied at runtime.

## Features

- **FastAPI** with OpenAPI docs at `/docs`
- **Ultralytics YOLO** inference on **PyTorch CPU** (no ONNX export path in this service)
- **Threaded camera pipeline**, per-session workers, and **WebRTC** video tracks
- **Firebase** integration for reporting (credentials via config)
- **Docker** image tuned for **layer caching**: dependency install is separate from application code

## Project structure

| Path | Role |
|------|------|
| `main.py` | Process entry: reads `config/api.yaml`, starts Uvicorn |
| `api/` | FastAPI app, routes, WebRTC offer/answer |
| `core/` | Model loader, sessions, stream, pipeline, device helpers |
| `detectors/` | YOLO wrapper (confidence, IoU, device) |
| `models/` | Weight files (`.pt` / checkpoints) — not committed |
| `config/` | YAML + secrets — not committed; use `*.example.*` templates |
| `utils/` | Geometry, visualization helpers |

## Setup

### Docker

Build and run (mount your local `config` so the container sees YAML and Firebase credentials):

```bash
docker build -t chainly-ai .
docker run -p 8000:8000 -v $(pwd)/config:/app/config chainly-ai
```

The API process is started with `python main.py` (same as local runs).

### Configuration

**Config files are not shipped in the repository for security and environment differences.** You must add them manually under `config/`, using the checked-in examples as templates (e.g. `webrtc.example.yaml` → `webrtc.yaml`, Firebase JSON paths as documented in those files).

Minimum expectations:

- `config/api.yaml` — host, port, logging (optional)
- `config/webrtc.yaml` — STUN/TURN for WebRTC
- `config/box_detector.yaml`, `config/defect_detector.yaml`, `config/stream.yaml` — models and thresholds
- `config/firebase.yaml` (and service account JSON as referenced) — if you use Firebase

Place YOLO weight files under `models/` (or use absolute `model_path` values in YAML).

### Access

- **Interactive API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## Performance notes

- **CPU-only**: PyTorch is installed from the official CPU wheel index inside the image; inference uses `device="cpu"`.
- **Image size**: Slim base + CPU wheels targets roughly **~2 GB** depending on Ultralytics and transitive deps.
- **Rebuild speed**: Changing only application code should **not** invalidate the dependency layers in the Dockerfile.

## License

See your repository’s license file if applicable.
