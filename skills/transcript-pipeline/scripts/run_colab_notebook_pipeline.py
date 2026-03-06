#!/usr/bin/env python3
"""Dedicated Colab notebook explainer pipeline entrypoint.

This is a thin wrapper around update_ai_notes_with_resources_and_colab.py to provide
an explicit pipeline command focused on AI/ML Colab augmentation.
"""

from __future__ import annotations

from update_ai_notes_with_resources_and_colab import main


if __name__ == '__main__':
    raise SystemExit(main())
