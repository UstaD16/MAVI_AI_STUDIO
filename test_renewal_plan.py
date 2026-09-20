from core.source_analyzer import SOURCE_ANALYZER
from core.music_dna import MUSIC_DNA_BUILDER
from core.renewal import RENEWAL_ENGINE


def main():
    print()
    print("=" * 72)
    print("MAVI AI STUDIO • RENEWAL PLAN")
    print("=" * 72)
    print()

    # 1. Kaynağı analiz et
    analysis = SOURCE_ANALYZER.analyze_first_source()

    if analysis is None:
        print("Kaynak müzik bulunamadı.")
        return

    # 2. Music DNA oluştur
    dna = MUSIC_DNA_BUILDER.build(analysis)

    # 3. Gerçek yenileme planını oluştur
    plan = RENEWAL_ENGINE.create_plan(dna)

    print(f"Kaynak      : {dna.source_name}")
    print(f"Süre        : {dna.duration:.2f} sn")
    print(f"BPM         : {dna.bpm:.2f}")
    print(f"Key         : {dna.key or 'henüz tespit edilmedi'}")
    print(f"Genre       : {dna.genre or 'henüz tespit edilmedi'}")

    print()
    print("YENİLEME HEDEFİ")
    print(f"  {plan.objective}")

    print()
    print("KORUNACAKLAR")

    for item in plan.preserve:
        print(f"  ✓ {item}")

    print()
    print("YENİLEME STRATEJİSİ")

    for item in plan.strategy:
        print(f"  • {item}")

    print()
    print("ENSTRÜMAN PLANI")

    if plan.instruments:
        for instrument in plan.instruments:
            print(f"  • {instrument}")
    else:
        print("  • Henüz enstrüman seçilmedi.")

    print()
    print("YASAKLAR / KISITLAR")

    for item in plan.constraints:
        print(f"  ✕ {item}")

    print()
    print("=" * 72)
    print("RENEWAL PLAN TAMAMLANDI")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()