from core.workspace import MAVI_WORKSPACE


def main() -> None:
    print()
    print("=" * 72)
    print("MAVI AI STUDIO • MUSIC WORKSPACE")
    print("=" * 72)
    print()

    paths = MAVI_WORKSPACE.paths()

    print(f"ROOT     : {paths['root']}")
    print(f"KAYNAK   : {paths['source']}")
    print(f"ÜRETİLEN : {paths['generated']}")
    print(f"STEMS    : {paths['stems']}")
    print(f"MIX      : {paths['mix']}")
    print(f"MASTER   : {paths['master']}")

    print()
    print("-" * 72)

    for name, path in paths.items():
        status = "OK" if path.exists() and path.is_dir() else "FAIL"
        print(f"[ {status} ] {name:<10} {path}")

    print("-" * 72)
    print()
    print("MAVI'NİN MÜZİKLERİ çalışma alanı hazır.")
    print()


if __name__ == "__main__":
    main()