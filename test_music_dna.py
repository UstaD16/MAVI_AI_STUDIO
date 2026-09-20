from core.source_analyzer import SOURCE_ANALYZER
from core.music_dna import MUSIC_DNA_BUILDER


def main() -> None:
    print()
    print("=" * 72)
    print("MAVI AI STUDIO • MUSIC DNA")
    print("=" * 72)
    print()

    analysis = SOURCE_ANALYZER.analyze_first_source()

    if analysis is None:
        print("Kaynak müzik bulunamadı.")
        return

    dna = MUSIC_DNA_BUILDER.build(
        analysis
    )

    print(f"Kaynak      : {dna.source_name}")
    print(f"Süre        : {dna.duration:.2f} sn")
    print(f"BPM         : {dna.bpm:.2f}")
    print(f"Key         : {dna.key or 'henüz tespit edilmedi'}")
    print(f"Genre       : {dna.genre or 'henüz tespit edilmedi'}")
    print(f"Energy      : {dna.energy:.3f}")

    print()
    print("RHYTHM DNA")
    print(f"  {dna.rhythm_identity}")

    print()
    print("MELODIC DNA")
    print(f"  {dna.melodic_identity}")

    print()
    print("HARMONIC DNA")
    print(f"  {dna.harmonic_identity}")

    print()
    print("ARRANGEMENT DNA")
    print(f"  {dna.arrangement_identity}")

    print()
    print("KORUMA")
    print(f"  Melody : {dna.preserve_melody}")
    print(f"  Rhythm : {dna.preserve_rhythm}")
    print(f"  Form   : {dna.preserve_form}")

    print()
    print("TAGS")
    for tag in dna.tags:
        print(f"  • {tag}")

    print()
    print("=" * 72)
    print("MUSIC DNA TAMAMLANDI")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()