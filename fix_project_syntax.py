from pathlib import Path

ROOT = Path(__file__).resolve().parent


def clean_python_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig")

    original = text

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = text.splitlines()

    # Baştaki Markdown code fence
    while lines and not lines[0].strip():
        lines.pop(0)

    if lines and lines[0].strip().lower() in {
        "```python",
        "```py",
        "```",
    }:
        lines.pop(0)

    # Sondaki Markdown code fence
    while lines and not lines[-1].strip():
        lines.pop()

    if lines and lines[-1].strip() == "```":
        lines.pop()

    cleaned = "\n".join(lines).rstrip() + "\n"

    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        return True

    return False


def main() -> None:
    changed = []
    failed = []

    for path in ROOT.rglob("*.py"):
        if path.name == Path(__file__).name:
            continue

        try:
            if clean_python_file(path):
                changed.append(path.relative_to(ROOT))
        except Exception as exc:
            failed.append((path.relative_to(ROOT), str(exc)))

    print("=" * 60)
    print("MAVI AI STUDIO - PYTHON SYNTAX CLEANUP")
    print("=" * 60)

    if changed:
        print("\nTemizlenen dosyalar:")
        for path in changed:
            print(f"  OK  {path}")
    else:
        print("\nTemizlenecek Markdown code fence bulunmadı.")

    if failed:
        print("\nTemizlenemeyen dosyalar:")
        for path, error in failed:
            print(f"  ERR {path} -> {error}")

    print("\nİşlem tamamlandı.")


if __name__ == "__main__":
    main()