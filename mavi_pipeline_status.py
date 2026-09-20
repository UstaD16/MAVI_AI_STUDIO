# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
PIPELINE STATUS
v0.1
============================================================

Prod. By Ufuk Akdoğan

MAVI'nin merkezi production pipeline durumunu tek noktadan
okur ve özetler.

BU DOSYA:
- generation başlatmaz
- audio üretmez
- mix/master çalıştırmaz
- fake/procedural/placeholder audio üretmez
"""

from __future__ import annotations

import json
import os
import sys

from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# ROOT
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

LOG_DIR = (
    ROOT / "logs"
)

OUTPUT_DIR = (
    ROOT / "output"
)

STATUS_FILE = (
    LOG_DIR
    / "mavi_pipeline_status.json"
)


# ============================================================
# PIPELINE
# ============================================================

PIPELINE_STAGES = (
    "SOURCE",
    "ANALYZE",
    "MUSIC DNA",
    "RENEWAL PLAN",
    "REAL GENERATION",
    "STEMS",
    "QUALITY GATE",
    "MIX",
    "MASTER",
    "WAV",
)


# ============================================================
# HELPERS
# ============================================================

def load_json(
    path: Path,
) -> Dict[str, Any]:

    if not path.exists():
        return {}

    if not path.is_file():
        return {}

    try:

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
    ):

        return {}

    return (
        payload
        if isinstance(payload, dict)
        else {}
    )


def file_exists(
    path: Path,
) -> bool:

    return (
        path.exists()
        and path.is_file()
    )


def latest_audio(
    directory: Path,
) -> str:

    if not directory.exists():
        return ""

    extensions = {
        ".wav",
        ".mp3",
        ".flac",
        ".ogg",
        ".m4a",
        ".aac",
        ".wma",
    }

    files = [
        path
        for path in directory.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in extensions
        )
    ]

    if not files:
        return ""

    files.sort(
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    return str(
        files[0]
    )


# ============================================================
# REPORT SOURCES
# ============================================================

def read_reports() -> Dict[str, Dict[str, Any]]:

    sources = {
        "integration": (
            LOG_DIR
            / "integration_test.json"
        ),
        "inspection": (
            LOG_DIR
            / "pipeline_inspection.json"
        ),
        "worker": (
            LOG_DIR
            / "worker_status.json"
        ),
        "system": (
            LOG_DIR
            / "full_system_check.json"
        ),
        "pipeline": (
            OUTPUT_DIR
            / "pipeline_result.json"
        ),
        "generation": (
            OUTPUT_DIR
            / "generation_result.json"
        ),
        "generation_validation": (
            OUTPUT_DIR
            / "generation_validation.json"
        ),
        "renewal_validation": (
            OUTPUT_DIR
            / "shote_mori_validation.json"
        ),
        "finalize": (
            OUTPUT_DIR
            / "finalize_renewal_result.json"
        ),
        "production": (
            OUTPUT_DIR
            / "MAVI_production_report.json"
        ),
    }

    result: Dict[
        str,
        Dict[str, Any]
    ] = {}

    for name, path in sources.items():

        payload = load_json(
            path
        )

        result[name] = {
            "path": str(path),
            "exists": bool(payload),
            "payload": payload,
        }

    return result


# ============================================================
# STAGE STATUS
# ============================================================

def determine_stage_status(
    reports: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:

    status = {
        stage: "PENDING"
        for stage in PIPELINE_STAGES
    }

    integration = reports[
        "integration"
    ][
        "payload"
    ]

    inspection = reports[
        "inspection"
    ][
        "payload"
    ]

    worker = reports[
        "worker"
    ][
        "payload"
    ]

    pipeline = reports[
        "pipeline"
    ][
        "payload"
    ]

    generation = reports[
        "generation"
    ][
        "payload"
    ]

    generation_validation = reports[
        "generation_validation"
    ][
        "payload"
    ]

    finalize = reports[
        "finalize"
    ][
        "payload"
    ]

    if integration.get(
        "success"
    ):

        for stage in (
            "SOURCE",
            "ANALYZE",
            "MUSIC DNA",
            "RENEWAL PLAN",
        ):

            status[stage] = "READY"

    if inspection.get(
        "success"
    ):

        status[
            "ANALYZE"
        ] = "READY"

        status[
            "MUSIC DNA"
        ] = "READY"

        status[
            "RENEWAL PLAN"
        ] = "READY"

    if worker.get(
        "real_worker_ready"
    ):

        status[
            "REAL GENERATION"
        ] = "READY"

    if generation.get(
        "success"
    ):

        status[
            "REAL GENERATION"
        ] = "COMPLETE"

    if generation_validation.get(
        "success"
    ):

        status[
            "QUALITY GATE"
        ] = "PASS"

    if pipeline.get(
        "success"
    ):

        for stage in (
            "SOURCE",
            "ANALYZE",
            "MUSIC DNA",
            "RENEWAL PLAN",
            "REAL GENERATION",
            "QUALITY GATE",
            "MIX",
            "MASTER",
            "WAV",
        ):

            status[stage] = "COMPLETE"

    if finalize.get(
        "success"
    ):

        status[
            "REAL GENERATION"
        ] = "COMPLETE"

        status[
            "QUALITY GATE"
        ] = "PASS"

        status[
            "MIX"
        ] = "COMPLETE"

        status[
            "MASTER"
        ] = "COMPLETE"

        status[
            "WAV"
        ] = "COMPLETE"

    return status


# ============================================================
# FINAL STATE
# ============================================================

def determine_final_state(
    stages: Dict[str, str],
    reports: Dict[str, Dict[str, Any]],
) -> str:

    finalize = reports[
        "finalize"
    ][
        "payload"
    ]

    pipeline = reports[
        "pipeline"
    ][
        "payload"
    ]

    worker = reports[
        "worker"
    ][
        "payload"
    ]

    if finalize.get(
        "success"
    ):

        return "PRODUCTION COMPLETE"

    if pipeline.get(
        "success"
    ):

        return "PIPELINE COMPLETE"

    if worker.get(
        "real_worker_ready"
    ):

        return "REAL WORKER READY"

    if any(
        value in {
            "COMPLETE",
            "PASS",
            "READY",
        }
        for value in stages.values()
    ):

        return "PIPELINE IN PROGRESS"

    return "NOT READY"


# ============================================================
# CURRENT OUTPUT
# ============================================================

def current_output(
    reports: Dict[str, Dict[str, Any]],
) -> str:

    finalize = reports[
        "finalize"
    ][
        "payload"
    ]

    pipeline = reports[
        "pipeline"
    ][
        "payload"
    ]

    generation = reports[
        "generation"
    ][
        "payload"
    ]

    candidates = [
        finalize.get(
            "final_output",
            "",
        ),
        pipeline.get(
            "final_output",
            "",
        ),
        generation.get(
            "output",
            "",
        ),
    ]

    for value in candidates:

        if value:

            path = (
                Path(
                    str(value)
                )
                .expanduser()
            )

            if file_exists(
                path
            ):

                return str(
                    path.resolve()
                )

            return str(
                path.resolve()
            )

    return latest_audio(
        OUTPUT_DIR
        / "final"
    )


# ============================================================
# BUILD STATUS
# ============================================================

def build_status() -> Dict[str, Any]:

    reports = read_reports()

    stages = determine_stage_status(
        reports
    )

    final_state = determine_final_state(
        stages,
        reports,
    )

    output = current_output(
        reports
    )

    return {
        "status_version": "0.1",

        "application": {
            "name": "MAVI AI STUDIO",
            "author": "Ufuk Akdoğan",
        },

        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },

        "pipeline": {
            "stages": list(
                PIPELINE_STAGES
            ),
            "status": stages,
            "final_state": final_state,
        },

        "worker": {
            "real_worker_ready": (
                reports[
                    "worker"
                ][
                    "payload"
                ].get(
                    "real_worker_ready",
                    False,
                )
            ),
        },

        "audio": {
            "current_output": output,
            "output_exists": (
                bool(
                    output
                    and file_exists(
                        Path(
                            output
                        )
                    )
                )
            ),
        },

        "policy": {
            "real_generation": True,
            "fake_audio": False,
            "procedural_audio": False,
            "placeholder_audio": False,
        },

        "reports": {
            name: {
                "exists": data["exists"],
                "path": data["path"],
            }
            for name, data
            in reports.items()
        },

        "environment": {
            "MAVI_STABLE_AUDIO_3_DIR": os.getenv(
                "MAVI_STABLE_AUDIO_3_DIR",
                "",
            ),
            "MAVI_STABLE_AUDIO_CLI": os.getenv(
                "MAVI_STABLE_AUDIO_CLI",
                "",
            ),
            "MAVI_WORKER_PYTHON": os.getenv(
                "MAVI_WORKER_PYTHON",
                "",
            ),
            "MAVI_WORKER_SCRIPT": os.getenv(
                "MAVI_WORKER_SCRIPT",
                "",
            ),
        },
    }


# ============================================================
# SAVE
# ============================================================

def save_status(
    status: Dict[str, Any],
) -> Path:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    STATUS_FILE.write_text(
        json.dumps(
            status,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return STATUS_FILE


# ============================================================
# PRINT
# ============================================================

def print_status(
    status: Dict[str, Any],
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "PIPELINE STATUS"
    )
    print(
        "============================================================"
    )
    print()

    print(
        f"FINAL STATE : "
        f"{status['pipeline']['final_state']}"
    )

    print()

    for stage in status[
        "pipeline"
    ][
        "stages"
    ]:

        value = (
            status[
                "pipeline"
            ][
                "status"
            ].get(
                stage,
                "PENDING",
            )
        )

        print(
            f"{stage:<20} : {value}"
        )

    print()
    print(
        "------------------------------------------------------------"
    )

    worker_ready = (
        status[
            "worker"
        ][
            "real_worker_ready"
        ]
    )

    print(
        f"REAL WORKER : "
        f"{'READY' if worker_ready else 'NOT READY'}"
    )

    output = (
        status[
            "audio"
        ][
            "current_output"
        ]
    )

    print(
        f"OUTPUT      : "
        f"{output or 'NONE'}"
    )

    print(
        "------------------------------------------------------------"
    )

    print(
        "POLICY"
    )

    print(
        "  Real generation : True"
    )

    print(
        "  Fake audio      : False"
    )

    print(
        "  Procedural      : False"
    )

    print(
        "  Placeholder     : False"
    )

    print()
    print(
        f"STATUS FILE : {STATUS_FILE}"
    )

    print(
        "============================================================"
    )
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    status = build_status()

    try:

        path = save_status(
            status
        )

    except OSError:

        path = STATUS_FILE

    print_status(
        status
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )