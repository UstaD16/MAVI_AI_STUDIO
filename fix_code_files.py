from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent


def clean_python_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")

        original = text

        # Baştaki markdown kod çitini temizle
        stripped = text.lstrip()

        if stripped.startswith("```python"):
            stripped = stripped[len("```python"):].lstrip("\r\n")
        elif stripped.startswith("```py"):
            stripped = stripped[len("```py"):].lstrip("\r\n")
        elif stripped.startswith("```"):
            stripped = stripped[3:].lstrip("\r\n")

        # Sondaki markdown kod çitini temizle
        stripped = stripped.rstrip()

        if stripped.endswith("```"):
            stripped = stripped[:-3].rstrip()

        if stripped != original:
            path.write_text(
                stripped + "\n",
                encoding="utf-8",
            )
            return True

        return False

    except Exception as exc:
        print(f"[ERROR] {path}: {exc}")
        return False


def main() -> None:
    changed = 0
    checked = 0

    excluded = {
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
    }

    for path in ROOT.rglob("*.py"):
        if any(part in excluded for part in path.parts):
            continue

        checked += 1

        if clean_python_file(path):
            changed += 1
            print(f"[FIXED] {path.relative_to(ROOT)}")

    print()
    print("=" * 60)
    print(f"Python files checked : {checked}")
    print(f"Python files cleaned : {changed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
