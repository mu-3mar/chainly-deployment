### Chainly AI Detection Service

Production-ready **FastAPI** service for **real-time quality-control detection** using **Ultralytics YOLO** (PyTorch, CPU), **OpenCV** frame processing, **multi-session** threaded inference, optional **WebRTC** video streaming (via `aiortc`), and **Firebase Realtime Database** event logging.

---

### Project Overview

This repository runs a server (`python main.py`) that starts a FastAPI app (Uvicorn) on **port 8000**. Clients can open/close detection sessions (reports), stream annotated video via WebRTC (if configured), and read health/config endpoints.

---

### Features

- **AI detection (YOLO)**: loads two YOLO models (box + defect) and runs inference in real time (CPU by default).
- **Real-time processing**: threaded camera capture + continuous pipeline loop per active session.
- **API endpoints**: session lifecycle, health, config.
- **WebRTC streaming (optional)**: provides ICE config and WebRTC offer/answer endpoint when `config/webrtc.yaml` is present.

---

### Project Structure

- **`main.py`**: entry point; launches Uvicorn on port **8000**.
- **`api/`**: FastAPI app and routes (sessions, health, WebRTC).
- **`config/`**: YAML/JSON configuration (safe defaults + templates; secrets are excluded).
- **`core/`**: pipeline/session management, model loader, Firebase client, streaming tracks.
- **`detectors/`**: YOLO detector wrapper.
- **`models/`**: model artifacts (assumed present locally).

---

### Setup Instructions

#### Option 1: Run with Docker (recommended)

Build:

```bash
docker build -t chainly-ai .
```

Run (mount config at runtime):

```bash
docker run -p 8000:8000 -v $(pwd)/config:/app/config chainly-ai
```

#### Option 2: Run locally

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

---

### Configuration Setup (VERY IMPORTANT)

This project **DOES NOT include secrets**. You must provide the following files **manually** before running:

1. **`config/firebase.yaml`**
2. **`config/webrtc.yaml`**
3. **A Firebase service account JSON** (placed inside `config/`, filename referenced by `config/firebase.yaml`)

Use the committed templates as starting points:

- **`config/firebase.example.yaml`** → copy to **`config/firebase.yaml`**
- **`config/webrtc.example.yaml`** → copy to **`config/webrtc.yaml`**

Example workflow:

```bash
cp config/firebase.example.yaml config/firebase.yaml
cp config/webrtc.example.yaml config/webrtc.yaml
```

Then edit the new files and place your Firebase service account JSON inside `config/`.

---

### How to run after adding configs

1. **Place config files inside `config/`**
   - `config/firebase.yaml`
   - `config/webrtc.yaml`
   - `config/<your-firebase-service-account>.json`
2. **Build the Docker image**

```bash
docker build -t chainly-ai .
```

3. **Run the container (configs are used at runtime)**

```bash
docker run -p 8000:8000 -v $(pwd)/config:/app/config chainly-ai
```

---

### Access the app

- **API base**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`

---

### 🔐 Security Notes

The following files are **NOT included** in the repository because they contain secrets:

- **Firebase service account JSON** (contains a private key)
- **`config/firebase.yaml`** (points to credentials and environment-specific database URL)
- **`config/webrtc.yaml`** (contains TURN secret used to generate temporary credentials)

Do **not** push these to GitHub.

---

### 📦 What to share privately

These files must be shared **out-of-band** (private transfer) and placed in the **`config/`** folder:

- Firebase service account JSON
- `config/firebase.yaml`
- `config/webrtc.yaml`

---

### Execution Flow (runtime config, not build-time)

1. Clone the repo
2. Add the private config files into `config/` (from a private source)
3. Build:

```bash
docker build -t chainly-ai .
```

4. Run (mount config directory at runtime):

```bash
docker run -p 8000:8000 -v $(pwd)/config:/app/config chainly-ai
```

**Important**: the configuration files are read **at runtime** from `/app/config` (the mounted volume). They are **not** required during the Docker build.

---

### Final Summary

- **What goes to GitHub**: application code + safe defaults + example config templates (`config/*.example.*`)
- **What is shared privately**: Firebase service account JSON, `config/firebase.yaml`, `config/webrtc.yaml`
- **When configs are used**: **runtime**, via the mounted `config/` directory

