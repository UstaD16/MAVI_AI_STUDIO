from core.active_source import ACTIVE_SOURCE_MANAGER
from core.source_analyzer import SOURCE_ANALYZER


def main():
    print()
    print("=" * 72)
    print("MAVI AI STUDIO • ACTIVE SOURCE ANALYSIS")
    print("=" * 72)
    print()

    tracks = ACTIVE_SOURCE_MANAGER.list_sources()

    if not tracks:
        print("Kaynak klasöründe müzik bulunamadı.")
        return

    print("KAYNAKLAR")
    print()

    for index, track in enumerate(tracks):
        print(f"  [{index}] {track.name}")

    print()
    print("İlk kaynak ACTIVE SOURCE olarak seçiliyor...")
    print()

    active = ACTIVE_SOURCE_MANAGER.select_index(0)

    print(f"ACTIVE SOURCE : {active.name}")
    print(f"PATH          : {active.path}")

    print()
    print("ANALİZ BAŞLIYOR...")
    print()

    result = SOURCE_ANALYZER.analyze_active_source()

    if result is None:
        print("Analiz sonucu alınamadı.")
        return

    print(f"Success     : {result.success}")
    print(f"Duration    : {result.duration:.2f} sn")
    print(f"Sample Rate : {result.sample_rate}")
    print(f"Channels    : {result.channels}")
    print(f"BPM         : {result.bpm:.2f}")
    print(f"Key         : {result.key or 'henüz tespit edilmedi'}")
    print(f"Genre       : {result.genre or 'henüz tespit edilmedi'}")
    print(f"Energy      : {result.energy:.3f}")
    print(f"Confidence  : {result.confidence:.3f}")

    print()
    print("INSTRUMENTS")

    if result.instruments:
        for instrument in result.instruments:
            print(f"  • {instrument}")
    else:
        print("  • Henüz tespit edilmedi")

    print()
    print("=" * 72)
    print("ACTIVE SOURCE ANALYSIS TAMAMLANDI")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()