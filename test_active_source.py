from core.active_source import ACTIVE_SOURCE_MANAGER


def main():
    print()
    print("=" * 72)
    print("MAVI AI STUDIO • ACTIVE SOURCE")
    print("=" * 72)
    print()

    tracks = ACTIVE_SOURCE_MANAGER.list_sources()

    if not tracks:
        print("Kaynak klasöründe müzik bulunamadı.")
        return

    print("KAYNAKLAR")
    print()

    for index, track in enumerate(tracks):
        print(
            f"  [{index}] {track.name}"
            f"  | {track.path.name}"
        )

    print()
    print("TEST: İlk kaynak ACTIVE SOURCE yapılıyor...")
    print()

    active = ACTIVE_SOURCE_MANAGER.select_index(0)

    print(f"ACTIVE SOURCE : {active.name}")
    print(f"PATH          : {active.path}")
    print(f"DURATION      : {active.duration:.2f} sn")

    print()
    print("STATUS")
    print(ACTIVE_SOURCE_MANAGER.status())

    print()
    print("=" * 72)
    print("ACTIVE SOURCE TAMAMLANDI")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()