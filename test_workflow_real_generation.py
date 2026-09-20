# -*- coding: utf-8 -*-

from pathlib import Path

from core.active_source import ACTIVE_SOURCE_MANAGER
from core.renewal_workflow import RENEWAL_WORKFLOW


SOURCE_INDEX = 0

OUTPUT = (
    Path.home()
    / "Desktop"
    / "MAVI'NİN MÜZİKLERİ"
    / "Üretilen"
    / "workflow_real_30s.wav"
)


def main():

    print("=" * 72)
    print("MAVI AI STUDIO • WORKFLOW REAL GENERATION TEST")
    print("=" * 72)

    # --------------------------------------------------------------
    # ACTIVE SOURCE
    # --------------------------------------------------------------

    print()
    print("ACTIVE SOURCE")

    try:

        if not ACTIVE_SOURCE_MANAGER.has_active_source():
            ACTIVE_SOURCE_MANAGER.select_index(
                SOURCE_INDEX
            )

        active = ACTIVE_SOURCE_MANAGER.get()

    except Exception as exc:

        print(
            f"[FAIL] Active source seçilemedi: {exc}"
        )
        return 1

    if active is None:

        print("[FAIL] ACTIVE SOURCE bulunamadı.")
        return 1

    source_path = getattr(
        active,
        "path",
        None,
    )

    if not source_path:
        source_path = getattr(
            active,
            "source_path",
            None,
        )

    print(f"  {source_path}")

    if not source_path:
        print("[FAIL] Active source path boş.")
        return 1

    source_path = Path(source_path)

    if not source_path.exists():

        print(
            f"[FAIL] Kaynak bulunamadı: {source_path}"
        )
        return 1

    # --------------------------------------------------------------
    # INFORMATIONAL STATUS
    # --------------------------------------------------------------

    print()
    print("WORKFLOW STATUS")

    try:

        status = RENEWAL_WORKFLOW.status()

        print(
            f"  Production Ready : "
            f"{status.get('production_ready')}"
        )

        print(
            f"  Generation       : "
            f"{status.get('generation_available')}"
        )

        print(
            f"  Backend          : "
            f"{status.get('backend')}"
        )

        print(
            "  Status kontrolü üretimi engellemiyor."
        )

    except Exception as exc:

        print(
            f"  Status okunamadı: {exc}"
        )

    # --------------------------------------------------------------
    # REAL WORKFLOW
    # --------------------------------------------------------------

    print()
    print("REAL WORKFLOW")

    print(
        "  Davul + Zurna + Bas Gitar + Sol Klarnet"
    )

    print(
        "  Duration : 30 sec"
    )

    print(
        "  Provider : Local Stable Audio 3"
    )

    print()
    print(
        "Gerçek üretim başlatılıyor..."
    )

    try:

        result = RENEWAL_WORKFLOW.execute(
            instruments=[
                "Davul",
                "Zurna",
                "Bas Gitar",
                "Sol Klarnet",
            ],

            user_command=(
                "Orijinal melodiyi ve ritmi koru. "
                "Davul, zurna, bas gitar ve sol "
                "klarnet ile doğal folk düzenleme "
                "oluştur."
            ),

            output_file=OUTPUT,

            duration=30.0,
        )

    except Exception as exc:

        print()
        print(
            "[FAIL] Workflow exception:"
        )
        print(exc)

        return 1

    # --------------------------------------------------------------
    # RESULT
    # --------------------------------------------------------------

    print()
    print("RESULT")

    print(
        f"  Success        : "
        f"{result.success}"
    )

    print(
        f"  Provider       : "
        f"{result.provider}"
    )

    print(
        f"  Model          : "
        f"{result.model}"
    )

    print(
        f"  Duration       : "
        f"{result.duration}"
    )

    print(
        f"  Generation     : "
        f"{result.generation_time:.2f} sec"
    )

    print(
        f"  Output         : "
        f"{result.output_path}"
    )

    if result.error:

        print(
            f"  Error          : "
            f"{result.error}"
        )

    # --------------------------------------------------------------
    # FILE CHECK
    # --------------------------------------------------------------

    output_path = (
        Path(result.output_path)
        if result.output_path
        else OUTPUT
    )

    if (
        result.success
        and output_path.exists()
        and output_path.stat().st_size > 0
    ):

        print()
        print("=" * 72)
        print(
            "WORKFLOW REAL GENERATION PASSED"
        )
        print("=" * 72)

        print()
        print(
            "ACTIVE SOURCE → RENEWAL → "
            "PRODUCTION → LOCAL STABLE AUDIO 3 → WAV"
        )

        print()
        print(
            f"Gerçek çıktı: {output_path}"
        )

        return 0

    print()
    print("=" * 72)
    print(
        "WORKFLOW REAL GENERATION FAILED"
    )
    print("=" * 72)

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )