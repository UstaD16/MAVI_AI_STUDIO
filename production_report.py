# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
PRODUCTION REPORT
v0.1
============================================================

Prod. By Ufuk Akdoğan

MAVI production sürecindeki JSON raporlarını tek bir okunabilir
production report altında toplar.

Bu dosya:
- audio üretmez
- generation başlatmaz
- mix/master çalıştırmaz
- fake/procedural audio oluşturmaz

Okur:
- integration_test.json
- pipeline_inspection.json
- worker_status.json
- generation_result.json
- generation_validation.json
- shote_mori_validation.json
- finalize_renewal_result.json
- renewal manifest

ve tek bir rapor üretir.
"""

from __future__ import annotations

import argparse
import json
import sys

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# ROOT / PATHS
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)

OUTPUT_DIR = (
    ROOT
    / "output"
)

LOG_DIR = (
    ROOT
    / "logs"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "MAVI_production_report.json"
)

REPORT_TEXT_FILE = (
    OUTPUT_DIR
    / "MAVI_production_report.txt"
)


# ============================================================
# ERRORS
# ============================================================

class ProductionReportError(Exception):
    """Production report temel hatası."""


# ============================================================
# JSON LOADER
# ============================================================

class JsonLoader:

    def load(
        self,
        path: Path,
    ) -> Optional[Dict[str, Any]]:

        if not path.exists():
            return None

        if not path.is_file():
            return None

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

            return None

        if not isinstance(
            payload,
            dict,
        ):

            return None

        return payload


# ============================================================
# REPORT BUILDER
# ============================================================

class ProductionReportBuilder:

    FILES = {
        "integration": (
            LOG_DIR
            / "integration_test.json"
        ),
        "inspection": (
            LOG_DIR
            / "pipeline_inspection.json"
        ),
        "worker_status": (
            LOG_DIR
            / "worker_status.json"
        ),
        "generation_result": (
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
    }

    def __init__(
        self,
    ) -> None:

        self.loader = JsonLoader()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    def load_all(
        self,
    ) -> Dict[str, Any]:

        data: Dict[str, Any] = {}

        for name, path in self.FILES.items():

            payload = self.loader.load(
                path
            )

            if payload is not None:

                data[name] = {
                    "path": str(path),
                    "payload": payload,
                }

        # Renewal manifest varsa ayrıca ekle.
        manifests = sorted(
            OUTPUT_DIR.glob(
                "*_MAVI_RENEWED_manifest.json"
            ),
            key=lambda item: item.name.lower(),
        )

        if manifests:

            manifest_path = manifests[-1]

            payload = self.loader.load(
                manifest_path
            )

            if payload is not None:

                data["renewal_manifest"] = {
                    "path": str(
                        manifest_path
                    ),
                    "payload": payload,
                }

        return data

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def _status(
        self,
        payload: Optional[Dict[str, Any]],
    ) -> str:

        if not payload:
            return "NOT AVAILABLE"

        if "success" in payload:

            return (
                "SUCCESS"
                if bool(
                    payload["success"]
                )
                else "FAILED"
            )

        if "status" in payload:

            return str(
                payload["status"]
            )

        if "real_worker_ready" in payload:

            return (
                "READY"
                if payload["real_worker_ready"]
                else "NOT READY"
            )

        return "AVAILABLE"

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    def _score(
        self,
        payload: Optional[Dict[str, Any]],
        key: str = "score",
    ) -> Optional[float]:

        if not payload:
            return None

        value = payload.get(
            key
        )

        if value is None:
            return None

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    def _output_from_payload(
        self,
        payload: Optional[Dict[str, Any]],
    ) -> str:

        if not payload:
            return ""

        candidates = [
            payload.get("final_output"),
            payload.get("output"),
            payload.get("generated"),
        ]

        for value in candidates:

            if value:

                return str(
                    value
                )

        metadata = payload.get(
            "metadata",
            {},
        )

        if isinstance(
            metadata,
            dict,
        ):

            value = metadata.get(
                "output"
            )

            if value:
                return str(
                    value
                )

        return ""

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    def build(
        self,
    ) -> Dict[str, Any]:

        loaded = self.load_all()

        integration = (
            loaded.get(
                "integration",
                {},
            ).get(
                "payload",
                {},
            )
        )

        inspection = (
            loaded.get(
                "inspection",
                {},
            ).get(
                "payload",
                {},
            )
        )

        worker = (
            loaded.get(
                "worker_status",
                {},
            ).get(
                "payload",
                {},
            )
        )

        generation = (
            loaded.get(
                "generation_result",
                {},
            ).get(
                "payload",
                {},
            )
        )

        generation_validation = (
            loaded.get(
                "generation_validation",
                {},
            ).get(
                "payload",
                {},
            )
        )

        renewal_validation = (
            loaded.get(
                "renewal_validation",
                {},
            ).get(
                "payload",
                {},
            )
        )

        finalize = (
            loaded.get(
                "finalize",
                {},
            ).get(
                "payload",
                {},
            )
        )

        manifest = (
            loaded.get(
                "renewal_manifest",
                {},
            ).get(
                "payload",
                {},
            )
        )

        final_output = (
            self._output_from_payload(
                finalize
            )
            or self._output_from_payload(
                generation
            )
        )

        report = {
            "report_version": "0.1",

            "created_at": (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            ),

            "application": {
                "name": "MAVI AI STUDIO",
                "author": "Ufuk Akdoğan",
            },

            "pipeline_status": {
                "integration": (
                    self._status(
                        integration
                    )
                ),
                "inspection": (
                    self._status(
                        inspection
                    )
                ),
                "worker": (
                    "READY"
                    if worker.get(
                        "real_worker_ready",
                        False,
                    )
                    else "NOT READY"
                ),
                "generation": (
                    self._status(
                        generation
                    )
                ),
                "generation_validation": (
                    self._status(
                        generation_validation
                    )
                ),
                "renewal_validation": (
                    self._status(
                        renewal_validation
                    )
                ),
                "finalize": (
                    self._status(
                        finalize
                    )
                ),
            },

            "scores": {
                "generation": (
                    self._score(
                        generation_validation
                    )
                ),
                "renewal": (
                    self._score(
                        renewal_validation
                    )
                ),
                "finalize_generation": (
                    self._score(
                        finalize,
                        "generation_score",
                    )
                ),
                "finalize_renewal": (
                    self._score(
                        finalize,
                        "renewal_score",
                    )
                ),
            },

            "audio": {
                "generated_output": (
                    self._output_from_payload(
                        generation
                    )
                ),
                "validated_output": (
                    generation_validation.get(
                        "output",
                        {}
                    ).get(
                        "path",
                        "",
                    )
                    if isinstance(
                        generation_validation.get(
                            "output"
                        ),
                        dict,
                    )
                    else ""
                ),
                "final_output": (
                    final_output
                ),
            },

            "source": {
                "path": (
                    renewal_validation.get(
                        "source",
                        {}
                    ).get(
                        "path",
                        "",
                    )
                    if isinstance(
                        renewal_validation.get(
                            "source"
                        ),
                        dict,
                    )
                    else manifest.get(
                        "source",
                        "",
                    )
                )
            },

            "renewal": {
                "mode": (
                    generation.get(
                        "metadata",
                        {}
                    ).get(
                        "request_mode",
                        "",
                    )
                    if isinstance(
                        generation.get(
                            "metadata"
                        ),
                        dict,
                    )
                    else ""
                ),
                "preservation": (
                    generation.get(
                        "metadata",
                        {}
                    ).get(
                        "source_preservation",
                        None,
                    )
                    if isinstance(
                        generation.get(
                            "metadata"
                        ),
                        dict,
                    )
                    else None
                ),
                "instruments": (
                    generation.get(
                        "metadata",
                        {}
                    ).get(
                        "instruments",
                        [],
                    )
                    if isinstance(
                        generation.get(
                            "metadata"
                        ),
                        dict,
                    )
                    else []
                ),
            },

            "quality": {
                "generation": (
                    generation_validation
                ),
                "renewal": (
                    renewal_validation
                ),
            },

            "worker": {
                "real_worker_ready": worker.get(
                    "real_worker_ready",
                    False,
                ),
                "stable_audio_cli": (
                    worker.get(
                        "environment",
                        {}
                    ).get(
                        "stable_audio_cli",
                        {},
                    )
                    if isinstance(
                        worker.get(
                            "environment"
                        ),
                        dict,
                    )
                    else {}
                ),
            },

            "policy": {
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },

            "files_loaded": sorted(
                loaded.keys()
            ),

            "raw_sources": loaded,
        }

        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        report[
            "final_status"
        ] = self._calculate_final_status(
            report
        )

        return report

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    def _calculate_final_status(
        self,
        report: Dict[str, Any],
    ) -> str:

        statuses = (
            report[
                "pipeline_status"
            ]
        )

        if statuses.get(
            "finalize"
        ) == "SUCCESS":

            return "PRODUCTION COMPLETE"

        if statuses.get(
            "generation"
        ) == "SUCCESS":

            if statuses.get(
                "generation_validation"
            ) == "SUCCESS":

                return "GENERATION COMPLETE"

        if statuses.get(
            "worker"
        ) == "READY":

            return "WORKER READY"

        return "PIPELINE INCOMPLETE"


# ============================================================
# TEXT REPORT
# ============================================================

class ProductionTextReport:

    def build(
        self,
        report: Dict[str, Any],
    ) -> str:

        statuses = report[
            "pipeline_status"
        ]

        scores = report[
            "scores"
        ]

        renewal = report[
            "renewal"
        ]

        audio = report[
            "audio"
        ]

        lines: List[str] = []

        lines.extend(
            [
                "============================================================",
                "MAVI AI STUDIO",
                "PRODUCTION REPORT",
                "============================================================",
                "",
                f"FINAL STATUS : {report['final_status']}",
                "",
                "PIPELINE",
                "------------------------------------------------------------",
                f"Integration           : {statuses.get('integration', '')}",
                f"Inspection            : {statuses.get('inspection', '')}",
                f"Real Worker           : {statuses.get('worker', '')}",
                f"Generation            : {statuses.get('generation', '')}",
                f"Generation Validation : {statuses.get('generation_validation', '')}",
                f"Renewal Validation    : {statuses.get('renewal_validation', '')}",
                f"Finalize              : {statuses.get('finalize', '')}",
                "",
                "SCORES",
                "------------------------------------------------------------",
                f"Generation : {scores.get('generation')}",
                f"Renewal    : {scores.get('renewal')}",
                f"Final Gen  : {scores.get('finalize_generation')}",
                f"Final Ren  : {scores.get('finalize_renewal')}",
                "",
                "RENEWAL",
                "------------------------------------------------------------",
                f"Mode           : {renewal.get('mode', '')}",
                f"Preservation   : {renewal.get('preservation')}",
                f"Instruments    : {renewal.get('instruments', [])}",
                "",
                "AUDIO",
                "------------------------------------------------------------",
                f"Generated : {audio.get('generated_output', '')}",
                f"Validated : {audio.get('validated_output', '')}",
                f"Final     : {audio.get('final_output', '')}",
                "",
                "POLICY",
                "------------------------------------------------------------",
                "Real generation : True",
                "Fake audio      : False",
                "Procedural      : False",
                "Placeholder     : False",
                "",
                "============================================================",
                "",
            ]
        )

        return "\n".join(
            lines
        )


# ============================================================
# SAVE
# ============================================================

def save_json_report(
    report: Dict[str, Any],
) -> Path:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return REPORT_FILE


def save_text_report(
    text: str,
) -> Path:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_TEXT_FILE.write_text(
        text,
        encoding="utf-8",
    )

    return REPORT_TEXT_FILE


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Build MAVI production report"
        )
    )

    parser.add_argument(
        "--json",
        default=str(
            REPORT_FILE
        ),
        help="JSON report output.",
    )

    parser.add_argument(
        "--text",
        default=str(
            REPORT_TEXT_FILE
        ),
        help="Text report output.",
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    try:

        builder = (
            ProductionReportBuilder()
        )

        report = (
            builder.build()
        )

        text = (
            ProductionTextReport().build(
                report
            )
        )

        json_path = save_json_report(
            report
        )

        text_path = save_text_report(
            text
        )

        print()
        print(
            text
        )

        print(
            f"JSON REPORT : {json_path}"
        )

        print(
            f"TEXT REPORT : {text_path}"
        )

        return 0

    except Exception as exc:

        print()
        print(
            "PRODUCTION REPORT ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )