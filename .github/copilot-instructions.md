# Archangelix – AI Agent Guide

- Scope: single Python CLI (`archangelix.py`) that loads exams from `exams/*.json` files, runs an interactive Q&A, calculates a score, and saves the result to `results/{exam_name_underscored}_{YYYYMMDD_HHMMSS}.json`.
- Runtime: Python 3 standard library only. Entry point: `python3 archangelix.py <command>`.
- Do not introduce external deps or frameworks unless explicitly requested; keep the CLI minimal and stdout-based.

## Commands
- `show_exams`: list exams, run interactive session, save results.
- `show_results`: list saved results, print summary table.

## Exam JSON Schema
- File: `exams/*.json` example in `exams/python.json`.
- Keys: `name`, `description`, `questions`.
- Each question: `question`, `type`, `explanation`, optional `options` (for choice types), optional `correct_answer` (for free_text).

## Question Types & Grading
- `yes_no`: input "yes"/"y" -> correct; otherwise incorrect.
- `single_choice`: user selects 1-based option number; convert to 0-based index and read `options[idx].correct`.
- `multiple_choice`: user enters comma-separated 1-based numbers; convert to 0-based and compare sorted indices to those where `options[].correct` is true.
- `free_text`: lowercase input must contain `correct_answer` substring if provided; if absent, treated as correct.

## Scoring & Persistence
- Score: `(correct_gradable / total_gradable) * 10`.
- Result file: `results/{exam_name_underscored}_{YYYYMMDD_HHMMSS}.json` (UTF-8, `ensure_ascii=False`).
- Stored fields: exam metadata, timestamp, score, counts, and per-question results including `user_answer` (1-based for choices), `correct`, and `explanation`.

## UX Conventions
- Options are displayed as 1-based indices in prompts.
- Multiple choice expects comma-separated 1-based integers.
- Input is minimally validated; out-of-range values mark as incorrect.

## Developer Notes
- No external deps; keep output to stdout.
- Add exams by following the schema; ensure `type` and fields match handled cases.
- For debugging, run commands directly; interactive input drives flow.
