This repository is a collection of small, single-file Python utilities and simple front-end assets (HTML/CSS/JS).

Key ideas for an AI coding agent working in this repo:

- Project scope
  - Small, largely independent scripts under folders such as `excel-merger/`, `duplicate-finder/`, `color-picker/`, `screenshot-to-text/`, `pomodoro-timer/`.
  - Each utility is intended to be runnable directly (many have `if __name__ == "__main__"` entry points).

- Common patterns and conventions
  - Plain Python scripts (no package layout). Edit and run files directly.
  - CLI-style scripts use `argparse` (example: `bulk_rename.py`). Keep changes backwards-compatible with the existing CLI flags.
  - GUI scripts use `tkinter` and expect a local desktop environment (examples: `color-picker/picker.py`, `pomodoro-timer/timer.py`). Avoid converting these to web apps unless requested.
  - Excel tooling uses `pandas` and sometimes `pyxlsb` for `.xlsb` files (example: `excel-merger/merger.py`). Add `pyxlsb` only if working with `.xlsb` files.

- Environment & OS assumptions
  - Most scripts assume a Windows environment and often contain hard-coded absolute paths (e.g., Tesseract executable in `import pytesseract.py` and `screenshot-to-text/extract_text.py`). When editing, prefer making paths configurable via environment variables or CLI flags rather than changing the source user-specific paths.

- Integration points & external dependencies
  - Tesseract OCR: scripts set `pytesseract.pytesseract.tesseract_cmd` to a Windows path. If modifying OCR scripts, respect existing behavior and provide a CLI/ENV override.
  - Excel handling: `pandas` is used; reading `.xlsb` uses `engine='pyxlsb'`. Ensure `pyxlsb` is included when adding requirements.

- Testing, debugging, and running
  - No test harness present. For quick validation, run scripts directly with Python (e.g., `python bulk_rename.py <folder> --dry`).
  - For GUI scripts, run on a machine with a desktop session.
  - When adding dependencies, provide a `requirements.txt` at repo root with pinned versions.

- Safety and small-priority improvements to prefer
  - Replace hard-coded absolute paths with CLI args or environment variables and document defaults in the file header.
  - Keep changes minimal and backwards-compatible: maintain existing CLI flags, file outputs (`output.txt`, `ocr_results/`), and naming conventions.
  - When merging files or refactoring, preserve the `if __name__ == "__main__"` behavior so scripts remain runnable.

- Files to inspect for references/examples
  - `bulk_rename.py` — example CLI + slugify/rename logic and dry-run flow.
  - `import pytesseract.py` and `screenshot-to-text/extract_text.py` — shows how Tesseract path and input/output flow are handled.
  - `excel-merger/merger.py` — shows `pandas` usage and `.xlsb` handling.
  - `duplicate-finder/duplicate_finder.py` — shows file-hash duplicate detection with `sha256`.

- When creating new features
  - Add a short usage example at the top of the modified file.
  - Add or update `requirements.txt` if external packages are introduced.
  - Prefer small, self-contained PRs because each script is largely independent.

If anything here is unclear or you'd like me to expand specific sections (examples for refactors, a template `requirements.txt`, or automated test snippets), tell me which area and I'll iterate.
