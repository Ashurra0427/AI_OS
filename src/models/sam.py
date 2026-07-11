"""Segment Anything Model (SAM) — UI element selection from screenshots."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class SAM:
    def __init__(self) -> None:
        self._model_loaded = False

    def _load_model(self) -> None:
        if self._model_loaded:
            return
        try:
            import torch
            from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
            self._mask_generator = SamAutomaticMaskGenerator(
                model=sam_model_registry["vit_h"](checkpoint="sam_vit_h.pth"),
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
            self._model_loaded = True
        except Exception as exc:
            logger.warning("sam_load_failed error=%s", str(exc))
            self._model_loaded = False

    def segment(self, image_path: str) -> list[dict[str, Any]]:
        self._load_model()
        if not self._model_loaded:
            return self._fallback_segment(image_path)
        try:
            img = Image.open(image_path).convert("RGB")
            arr = np.array(img)
            masks = self._mask_generator.generate(arr)
            return [
                {
                    "bbox": m["bbox"],
                    "area": int(m["area"]),
                    "predicted_iou": float(m["predicted_iou"]),
                    "stability_score": float(m["stability_score"]),
                }
                for m in masks
            ]
        except Exception as exc:
            logger.error("sam_segment_failed", error=str(exc))
            return self._fallback_segment(image_path)

    def _fallback_segment(self, image_path: str) -> list[dict[str, Any]]:
        p = Path(image_path)
        if not p.exists():
            return []
        img = Image.open(image_path)
        w, h = img.size
        return [
            {"bbox": [0, 0, w, h], "area": w * h, "predicted_iou": 1.0, "stability_score": 1.0, "fallback": True}
        ]
