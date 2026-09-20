from __future__ import annotations

from core.active_source import ACTIVE_SOURCE_MANAGER
from core.renewal_workflow import RENEWAL_WORKFLOW


def main():
    print("=" * 72)
    print("MAVI AI STUDIO • RENEWAL WORKFLOW TEST")
    print("=" * 72)

    sources = ACTIVE_SOURCE_MANAGER.list_sources()

    if not sources:
        print("KAYNAK YOK.")
        return

    print("\nKAYNAKLAR")
    for index, track in enumerate(sources):
        print(
            f"  [{index}] "
            f"{track.name} | {track.path.name}"
        )

    active = ACTIVE_SOURCE_MANAGER.select_index(0)

    print("\nACTIVE SOURCE")
    print(f"  {active.name}")
    print(f"  {active.path}")

    instruments = [
        "zurna",
        "davul",
        "bass guitar",
        "sol klarnet",
    ]

    print("\nENSTRÜMANLAR")
    for instrument in instruments:
        print(f"  • {instrument}")

    print("\nRENEWAL HAZIRLIĞI")

    try:
        payload = RENEWAL_WORKFLOW.prepare(
            instruments=instruments
        )

        print("  Payload : OK")
        print(
            f"  Model   : "
            f"{getattr(payload, 'model', 'stable-audio-3')}"
        )
        print(
            f"  Strength: "
            f"{getattr(payload, 'strength', 0.35)}"
        )

        print("\nPROMPT")
        print(
            getattr(payload, "prompt", "")
        )

        print("\nNEGATIVE PROMPT")
        print(
            getattr(payload, "negative_prompt", "")
        )

    except Exception as exc:
        print("\nHATA:")
        print(exc)
        return

    print("\nPROVIDER DURUMU")

    status = RENEWAL_WORKFLOW.status()
    provider = status.get("provider", {})

    print(
        f"  Active Provider : "
        f"{provider.get('active_provider')}"
    )
    print(
        f"  Ready           : "
        f"{provider.get('ready')}"
    )

    print("\n" + "=" * 72)
    print("RENEWAL WORKFLOW HAZIR.")
    print("=" * 72)


if __name__ == "__main__":
    main()