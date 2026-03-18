import logging
import os
import subprocess
import time
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class FFmpegStream:
    """
    FFmpeg subprocess pipe for RTSP/HTTP URLs.
    Eliminates OpenCV's built-in RTSP decoder which can produce green/black
    frames inside Docker due to missing codec libraries.
    """

    def __init__(self, url: str, width: int = 1280, height: int = 720):
        self.url = url
        self.width = int(width)
        self.height = int(height)
        self._pipe: Optional[subprocess.Popen] = None
        self._frame_bytes = self.width * self.height * 3

        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", "error",
            "-rtsp_transport", "tcp",
            "-i", self.url,
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-vf", f"scale={self.width}:{self.height}",
            "-",
        ]

        try:
            self._pipe = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=open(os.devnull, "wb"),
                bufsize=10 ** 8,
            )
            logger.debug(
                "FFmpegStream opened: url=%s, res=%dx%d",
                self.url, self.width, self.height,
            )
        except Exception as e:
            logger.error("Failed to start FFmpeg for %s: %s", self.url, e)
            raise RuntimeError(f"Could not open FFmpeg stream: {e}")

    def read(self) -> Optional[np.ndarray]:
        """
        Reads one frame from the FFmpeg pipe.
        Returns:
            np.ndarray if a full frame was read, or None if the stream dropped
            or partial data was received.
        """
        if self._pipe is None or self._pipe.stdout is None:
            return None

        raw = self._pipe.stdout.read(self._frame_bytes)
        
        # If we didn't get a full frame, the stream likely dropped.
        if len(raw) < self._frame_bytes:
            return None

        frame = np.frombuffer(raw, np.uint8).reshape(
            (self.height, self.width, 3)
        )
        
        # Temporary debug validation requested by user
        print(frame.shape)

        return frame

    def release(self) -> None:
        """Terminates the FFmpeg subprocess and cleans up."""
        if self._pipe is not None:
            self._pipe.terminate()
            try:
                self._pipe.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                self._pipe.kill()
            self._pipe = None
            logger.debug("FFmpegStream released")
