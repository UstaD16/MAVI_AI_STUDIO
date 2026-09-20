from __future__ import annotations

from pathlib import Path

from core.active_source import ACTIVE_SOURCE_MANAGER
from core.real_renewal import REAL_RENEWAL_ENGINE


def main() -> None:

    print()
    print("=" * 72)
    print("MAVI AI STUDIO • REAL RENEWAL TEST")
    print("=" * 72)

    # ---------------------------------------------------------------
    # 1. KAYNAKLARI TARA
    # ---------------------------------------------------------------

    sources = (
        ACTIVE_SOURCE_MANAGER.list_sources()
    )

    if not sources:

        print()
        print("[HATA] MAVI'NİN MÜZİKLERİ/Kaynak içinde")
        print("       müzik bulunamadı.")
        print()

        return

    print()
    print("KAYNAKLAR")
    print()

    for index, track in enumerate(
        sources
    ):

        print(
            f"  [{index}] "
            f"{track.name} | "
            f"{track.path.name}"
        )

    # ---------------------------------------------------------------
    # 2. İLK KAYNAĞI ACTIVE SOURCE YAP
    # ---------------------------------------------------------------

    active = (
        ACTIVE_SOURCE_MANAGER.select_index(
            0
        )
    )

    print()
    print("ACTIVE SOURCE")
    print(
        f"  {active.name}"
    )
    print(
        f"  {active.path}"
    )

    # ---------------------------------------------------------------
    # 3. SEÇİLEN ENSTRÜMANLAR
    # ---------------------------------------------------------------

    instruments = [
        "zurna",
        "davul",
        "bass guitar",
        "sol klarnet",
    ]

    print()
    print("SEÇİLEN ENSTRÜMANLAR")

    for instrument in instruments:
        print(
            f"  • {instrument}"
        )

    # ---------------------------------------------------------------
    # 4. PROVIDER DURUMU
    # ---------------------------------------------------------------

    print()
    print("REAL PROVIDER")

    status = (
        REAL_RENEWAL_ENGINE.status()
    )

    print(
        f"  Provider : "
        f"{status['provider']}"
    )

    print(
        f"  Model    : "
        f"{status['model']}"
    )

    print(
        f"  Ready    : "
        f"{status['ready']}"
    )

    # ---------------------------------------------------------------
    # 5. GERÇEK RENEWAL
    # ---------------------------------------------------------------

    print()
    print("=" * 72)
    print("GERÇEK RENEWAL BAŞLATILIYOR")
    print("=" * 72)

    result = (
        REAL_RENEWAL_ENGINE.generate(
            instruments=instruments
        )
    )

    # ---------------------------------------------------------------
    # 6. SONUÇ
    # ---------------------------------------------------------------

    print()
    print("=" * 72)
    print("SONUÇ")
    print("=" * 72)

    print(
        f"Success : "
        f"{result.success}"
    )

    print(
        f"Source  : "
        f"{result.source_path}"
    )

    print(
        f"Output  : "
        f"{result.output_path}"
    )

    if result.error:

        print()
        print(
            "HATA:"
        )
        print(
            result.error
        )

    # ---------------------------------------------------------------
    # 7. DOSYA KONTROLÜ
    # ---------------------------------------------------------------

    if result.success:

        output = Path(
            result.output_path
        )

        print()

        if (
            output.exists()
            and output.stat().st_size > 0
        ):

            print(
                "[OK] Gerçek üretim dosyası oluştu."
            )

            print(
                f"[OK] Boyut: "
                f"{output.stat().st_size:,} bytes"
            )

        else:

            print(
                "[HATA] Provider başarılı döndü "
                "ancak çıktı dosyası bulunamadı."
            )

    print()
    print("=" * 72)
    print("REAL RENEWAL TEST TAMAMLANDI")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()