# QC-SCM Detection Service (VM / Docker deployment)

Production-ready multi-session quality control detection service with:
- FastAPI backend (`/api/reports/*`, `/api/config`, `/webrtc/offer`)
- OpenCV capture + single-thread inference pipeline
- WebRTC streaming (direct / STUN / TURN relay) driven by config
- Firebase Realtime Database event publishing

## Run locally (VM / bare metal)

### Prerequisites
- Python 3.10
- A public camera URL (RTSP or HTTP)
- Model files in `models/`:
  - `models/detect_box.onnx`
  - `models/defect_box.onnx`
  - Optional GPU TensorRT siblings (only used when GPU is available):
    - `models/detect_box.engine`
    - `models/defect_box.engine`
- Required runtime configs in `config/`:
  - `config/box_detector.yaml`
  - `config/defect_detector.yaml`
  - `config/stream.yaml`
  - `config/firebase.yaml`
  - `config/webrtc.yaml` (**required**)
  - `config/app.yaml` (optional, CORS)

### Install

```bash
python -m pip install -r requirements.txt
```

### Provide secrets (do not commit)
- **Firebase service account**: place your key as `config/firebase-service-account.json`
- **WebRTC TURN secret / ICE servers**: create `config/webrtc.yaml`

### Start

```bash
python main.py
```

The API binds to `0.0.0.0:8000` by default (see `config/api.yaml`).

## Run with Docker (CPU default, GPU-compatible)

This image is CPU-compatible by default. It will only attempt TensorRT `.engine` models when CUDA is available at runtime **and** the `.engine` files exist.

### Build

```bash
docker build -t qc-scm-flow:latest .
```

### Run

Mount your runtime configs + secrets + model files:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/config:/app/config:ro" \
  -v "$PWD/models:/app/models:ro" \
  qc-scm-flow:latest
```

Notes:
- `config/webrtc.yaml` is required at startup.
- `config/firebase-service-account.json` must exist and match `config/firebase.yaml`.

## API usage (existing frontend-compatible)

### Open a report (start a session)
`POST /api/reports/open`

Body:
```json
{
  "report_id": "R-123",
  "camera_source": "rtsp://public-host:554/stream",
  "production_line_id": "LINE-1"
}
```

### Close a report
`POST /api/reports/close`

### List active reports
`GET /api/reports`

### Health
`GET /api/health`

## Deployment notes

### Camera source (URL-only)
- `camera_source` must be a **public** URL string (RTSP or HTTP).
- The server consumes the URL directly via OpenCV (`cv2.VideoCapture(camera_source)`).

### GPU vs CPU model selection (no behavior change)
- Device selection remains config-driven (`device: auto` in detector configs).
- If CUDA is available and the resolved device is `cuda`:
  - the service prefers `*.engine` next to the configured `*.onnx` (when present)
- If CUDA is not available:
  - the service uses `*.onnx` (CPU-only ONNX Runtime)

### WebRTC modes (config-driven, unchanged)
Configured in `config/webrtc.yaml`:
- `auto`: best effort (STUN + TURN)
- `direct`: no ICE servers (host candidates only)
- `stun`: STUN only
- `relay`: TURN only (client uses `iceTransportPolicy: "relay"`)

