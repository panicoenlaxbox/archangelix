# Archangelix – AI Agent Guide

- Scope: single Python CLI (`archangelix.py`) that loads exams from `exams/*.json` files, runs an interactive Q&A, calculates a score, and saves the result to `results/{exam_name_underscored}_{YYYYMMDD_HHMMSS}.json`.
- Runtime: Python 3 standard library only. Entry point: `python3 archangelix.py <command>`.
- Do not introduce external deps or frameworks unless explicitly requested; keep the CLI minimal and stdout-based.
