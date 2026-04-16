"""QC-SCM Detection Service entry point."""

import logging
import os
from pathlib import Path

import yaml
import uvicorn


def _apply_library_logging(api_cfg: dict) -> None:
    """Set third-party library log levels from config (YOLO/OpenCV env vars)."""
    lib = api_cfg.get("library_logging") or {}
    if lib.get("yolo_verbose") is not None:
        os.environ["YOLO_VERBOSE"] = str(lib["yolo_verbose"]).lower()
    if lib.get("opencv") is not None:
        os.environ["OPENCV_LOG_LEVEL"] = str(lib["opencv"])


def _suppress_noisy_loggers() -> None:
    for name in (
        "aioice",
        "aiortc",
        "ultralytics",
        "uvicorn.access",
        "uvicorn.error",
        "httpcore",
        "httpx",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)


def main():
    """Launch FastAPI server. Configuration from config/api.yaml only."""
    base = Path(__file__).resolve().parent
    api_cfg_path = base / "config" / "api.yaml"
    if api_cfg_path.exists():
        with open(api_cfg_path) as f:
            api_cfg = yaml.safe_load(f) or {}
    else:
        api_cfg = {}

    api_cfg.setdefault("host", "0.0.0.0")
    api_cfg.setdefault("port", 8000)
    api_cfg.setdefault("log_level", "warning")

    _apply_library_logging(api_cfg)

    _suppress_noisy_loggers()

    uvicorn.run(
        "api.api_server:app",
        host=api_cfg["host"],
        port=api_cfg["port"],
        log_level=api_cfg["log_level"],
        access_log=False,
        reload=False,
    )


if __name__ == "__main__":
    main()
