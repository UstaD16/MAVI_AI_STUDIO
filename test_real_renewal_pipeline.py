# -*- coding: utf-8 -*-

from pathlib import Path

from production_service import get_production_service


PROJECT_ROOT = Path(__file__).resolve().parent

SOURCE = PROJECT_ROOT / "test_source.wav"

OUTPUT = (
    Path.home()
    / "Desktop"
    / "MAVI'NİN MÜZİKLERİ"
    / "Üretilen"
    / "mavi_real_renewal_test.wav"
)


PROMPT = (
    "Faithful renewal of the original Turkish folk dance music. "
    "Preserve the original melody, rhythm, phrasing, tempo and structure. "
    "Realistic acoustic performance with davul, zurna, bass guitar and "
    "Sol klarnet. Natural human musicianship, organic dynamics, "
    "traditional Turkish folk character. "
    "The original musical identity must remain dominant."
)


NEGATIVE_PROMPT = (
    "EDM, chiptune, 8-bit, arcade music, random melody, "
    "unrelated melody, unrelated rhythm, plastic MIDI, toy sound, "
    "synthetic game sound, cheap synth, robotic performance, "
    "genre replacement, melody replacement"
)


def main():

    print("=" * 72)
    print("MAVI AI STUDIO • REAL RENEWAL PIPELINE TEST")
    print("=" * 72)

    print()
    print("SOURCE")
    print(f"  {SOURCE}")

    if not SOURCE.exists():
        print()
        print("[FAIL] test_source.wav bulunamadı.")
        print("Önceki 30 saniyelik test WAV'ı gerekli.")
        return 1

    service = get_production_service(
        force_new=True
    )

    print()
    print("PRODUCTION SERVICE")

    status = service.status()

    print(
        f"  Ready      : {status.get('ready')}"
    )
    print(
        f"  Generation : "
        f"{status.get('generation_available')}"
    )

    if not service.is_ready():
        print()
        print(
            "[FAIL] Production Service hazır değil."
        )
        return 1

    print()
    print("REAL GENERATION")
    print("  Provider   : Local Stable Audio 3")
    print("  Model      : sm-music")
    print("  Decoder    : same-s")
    print("  Duration   : 30 sec")
    print(
        "  Instruments: Davul + Zurna + "
        "Bas Gitar + Sol Klarnet"
    )

    try:

        result = service.renew(
            source_file=str(SOURCE),
            analysis={
                "duration": 30.0,
                "bpm": None,
                "key": "",
                "genre": "Turkish Folk Dance",
                "energy": None,
            },
            user_command=(
                "Eski müziği koru, "
                "davul zurna bas gitar ve "
                "sol klarnet ile yenile."
            ),
            instruments=[
                "Davul",
                "Zurna",
                "Bas Gitar",
                "Sol Klarnet",
            ],
            style="Turkish Folk Dance",
            region="Turkish Folk",
            renewal_strength=0.35,
            output_file=str(OUTPUT),
        )

    except Exception as exc:

        print()
        print("[FAIL] REAL GENERATION EXCEPTION")
        print(exc)
        return 1

    print()
    print("RESULT")
    print(
        f"  Success      : "
        f"{getattr(result, 'success', False)}"
    )
    print(
        f"  Provider     : "
        f"{getattr(result, 'provider', '')}"
    )
    print(
        f"  Model        : "
        f"{getattr(result, 'model', '')}"
    )
    print(
        f"  Status       : "
        f"{getattr(result, 'status', '')}"
    )
    print(
        f"  Duration     : "
        f"{getattr(result, 'duration', 0)}"
    )
    print(
        f"  Generation   : "
        f"{getattr(result, 'generation_time', 0):.2f} sec"
    )
    print(
        f"  Output       : "
        f"{getattr(result, 'output_path', '')}"
    )

    error = getattr(
        result,
        "error",
        "",
    )

    if error:
        print(
            f"  Error        : {error}"
        )

    output_path = Path(
        getattr(
            result,
            "output_path",
            "",
        )
        or ""
    )

    if (
        getattr(result, "success", False)
        and output_path.exists()
        and output_path.stat().st_size > 0
    ):

        print()
        print("=" * 72)
        print("REAL RENEWAL PIPELINE PASSED")
        print("=" * 72)
        print()
        print(
            "Gerçek WAV başarıyla üretildi."
        )
        print(
            f"Dosya: {output_path}"
        )

        return 0

    print()
    print("=" * 72)
    print("REAL RENEWAL PIPELINE FAILED")
    print("=" * 72)

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )