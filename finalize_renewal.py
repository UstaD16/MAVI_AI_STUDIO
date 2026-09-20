# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
FINALIZE RENEWAL
v0.1
============================================================

Prod. By Ufuk Akdoğan

Gerçek renewal pipeline'ının son güvenli adımı.

Akış:

    source
       ↓
    generated WAV
       ↓
    generation validation
       ↓
    renewal validation
       ↓
    final WAV
       ↓
    output/final
       ↓
    manifest + report

BU DOSYA:
- generation yapmaz
- fake audio üretmez
- procedural audio üretmez
- placeholder üretmez
- başarısız kalite çıktısını final olarak kabul etmez
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# ROOT
# ============================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
)


# ============================================================
# LOCAL IMPORT
# ============================================================

try:

    from validate_generation import (
        GenerationValidator,
    )

except Exception as exc:

    GenerationValidator = None
    GENERATION_VALIDATOR_IMPORT_ERROR = exc

else:

    GENERATION_VALIDATOR_IMPORT_ERROR = None


try:

    from validate_renewal import (
        RenewalValidator,
    )

except Exception as exc:

    RenewalValidator = None
    RENEWAL_VALIDATOR_IMPORT_ERROR = exc

else:

    RENEWAL_VALIDATOR_IMPORT_ERROR = None


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1"

DEFAULT_TOLERANCE = 2.0

DEFAULT_SAMPLE_RATE = 48000

FINAL_DIR = (
    ROOT
    / "output"
    / "final"
)

MANIFEST_DIR = (
    ROOT
    / "output"
)


# ============================================================
# ERRORS
# ============================================================

class FinalizeRenewalError(Exception):
    """Final renewal temel hatası."""


class FinalizeRenewalValidationError(
    FinalizeRenewalError
):
    """Final renewal validation hatası."""


class FinalizeRenewalOutputError(
    FinalizeRenewalError
):
    """Final output hatası."""


# ============================================================
# DATA
# ============================================================

@dataclass
class FinalizeResult:

    success: bool

    source: str = ""

    generated: str = ""

    final_output: str = ""

    manifest: str = ""

    generation_score: float = 0.0

    renewal_score: float = 0.0

    error: str = ""

    warnings: List[str] = None  # type: ignore[assignment]

    metadata: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:

        if self.warnings is None:
            self.warnings = []

        if self.metadata is None:
            self.metadata = {}

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ============================================================
# PATH HELPERS
# ============================================================

def build_final_name(
    source: Path,
) -> str:

    stem = source.stem

    return (
        f"{stem}_MAVI_RENEWED.wav"
    )


def build_manifest_name(
    source: Path,
) -> str:

    return (
        f"{source.stem}_MAVI_RENEWED_manifest.json"
    )


# ============================================================
# FINALIZER
# ============================================================

class RenewalFinalizer:

    def __init__(
        self,
    ) -> None:

        FINAL_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------------
    # COPY
    # --------------------------------------------------------

    def copy_to_final(
        self,
        generated: Path,
        source: Path,
    ) -> Path:

        if not generated.exists():

            raise FinalizeRenewalOutputError(
                (
                    "Generated WAV bulunamadı: "
                    f"{generated}"
                )
            )

        if not generated.is_file():

            raise FinalizeRenewalOutputError(
                (
                    "Generated output dosya değil: "
                    f"{generated}"
                )
            )

        final_path = (
            FINAL_DIR
            / build_final_name(
                source
            )
        )

        try:

            shutil.copy2(
                generated,
                final_path,
            )

        except OSError as exc:

            raise FinalizeRenewalOutputError(
                (
                    "Final WAV kopyalanamadı: "
                    f"{exc}"
                )
            ) from exc

        if (
            not final_path.exists()
            or final_path.stat().st_size <= 0
        ):

            raise FinalizeRenewalOutputError(
                (
                    "Final WAV oluşturuldu "
                    "ancak geçerli değil."
                )
            )

        return final_path

    # --------------------------------------------------------
    # GENERATION VALIDATION
    # --------------------------------------------------------

    def validate_generation(
        self,
        generated: Path,
        target_seconds: float,
    ) -> Any:

        if GenerationValidator is None:

            raise FinalizeRenewalValidationError(
                (
                    "GenerationValidator import "
                    "edilemedi: "
                    f"{GENERATION_VALIDATOR_IMPORT_ERROR}"
                )
            )

        validator = (
            GenerationValidator()
        )

        return validator.validate(
            output=generated,
            target_seconds=target_seconds,
            target_sample_rate=(
                DEFAULT_SAMPLE_RATE
            ),
            duration_tolerance=(
                DEFAULT_TOLERANCE
            ),
        )

    # --------------------------------------------------------
    # RENEWAL VALIDATION
    # --------------------------------------------------------

    def validate_renewal(
        self,
        source: Path,
        generated: Path,
    ) -> Any:

        if RenewalValidator is None:

            raise FinalizeRenewalValidationError(
                (
                    "RenewalValidator import "
                    "edilemedi: "
                    f"{RENEWAL_VALIDATOR_IMPORT_ERROR}"
                )
            )

        validator = (
            RenewalValidator()
        )

        return validator.validate(
            source=source,
            renewed=generated,
        )

    # --------------------------------------------------------
    # MANIFEST
    # --------------------------------------------------------

    def write_manifest(
        self,
        source: Path,
        generated: Path,
        final_output: Path,
        generation_validation: Any,
        renewal_validation: Any,
    ) -> Path:

        manifest_path = (
            MANIFEST_DIR
            / build_manifest_name(
                source
            )
        )

        payload = {
            "version": VERSION,
            "created_at": (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            ),
            "source": str(
                source
            ),
            "generated": str(
                generated
            ),
            "final_output": str(
                final_output
            ),
            "generation_validation": (
                generation_validation.as_dict()
            ),
            "renewal_validation": (
                renewal_validation.as_dict()
            ),
            "pipeline": [
                "SOURCE",
                "ANALYZE",
                "MUSIC DNA",
                "RENEWAL PLAN",
                "REAL GENERATION",
                "QUALITY GATE",
                "FINAL RENEWAL",
            ],
            "policy": {
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },
        }

        manifest_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return manifest_path

    # --------------------------------------------------------
    # FINALIZE
    # --------------------------------------------------------

    def finalize(
        self,
        source: str | Path,
        generated: str | Path,
        target_seconds: float,
    ) -> FinalizeResult:

        source_path = (
            Path(
                source
            )
            .expanduser()
            .resolve()
        )

        generated_path = (
            Path(
                generated
            )
            .expanduser()
            .resolve()
        )

        if not source_path.exists():

            raise FinalizeRenewalOutputError(
                (
                    "Source bulunamadı: "
                    f"{source_path}"
                )
            )

        if not generated_path.exists():

            raise FinalizeRenewalOutputError(
                (
                    "Generated WAV bulunamadı: "
                    f"{generated_path}"
                )
            )

        generation_validation = (
            self.validate_generation(
                generated=generated_path,
                target_seconds=(
                    target_seconds
                ),
            )
        )

        if not generation_validation.success:

            raise FinalizeRenewalValidationError(
                (
                    "Generation quality gate "
                    "başarısız."
                )
            )

        renewal_validation = (
            self.validate_renewal(
                source=source_path,
                generated=generated_path,
            )
        )

        if not renewal_validation.success:

            raise FinalizeRenewalValidationError(
                (
                    "Renewal quality gate "
                    "başarısız."
                )
            )

        final_output = (
            self.copy_to_final(
                generated=generated_path,
                source=source_path,
            )
        )

        manifest_path = (
            self.write_manifest(
                source=source_path,
                generated=generated_path,
                final_output=final_output,
                generation_validation=(
                    generation_validation
                ),
                renewal_validation=(
                    renewal_validation
                ),
            )
        )

        warnings = []

        warnings.extend(
            getattr(
                generation_validation,
                "warnings",
                [],
            )
            or []
        )

        warnings.extend(
            getattr(
                renewal_validation,
                "warnings",
                [],
            )
            or []
        )

        return FinalizeResult(
            success=True,
            source=str(
                source_path
            ),
            generated=str(
                generated_path
            ),
            final_output=str(
                final_output
            ),
            manifest=str(
                manifest_path
            ),
            generation_score=float(
                getattr(
                    generation_validation,
                    "score",
                    0.0,
                )
            ),
            renewal_score=float(
                getattr(
                    renewal_validation,
                    "score",
                    0.0,
                )
            ),
            warnings=warnings,
            metadata={
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
                "final_directory": str(
                    FINAL_DIR
                ),
            },
        )


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
    result: FinalizeResult,
    path: Path,
) -> Path:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            result.as_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


# ============================================================
# PRINT
# ============================================================

def print_result(
    result: FinalizeResult,
) -> None:

    print()
    print(
        "============================================================"
    )
    print(
        "MAVI AI STUDIO"
    )
    print(
        "FINALIZE RENEWAL"
    )
    print(
        "============================================================"
    )

    print(
        "STATUS : "
        + (
            "SUCCESS"
            if result.success
            else "FAILED"
        )
    )

    print(
        f"GENERATION SCORE : "
        f"{result.generation_score:.4f}"
    )

    print(
        f"RENEWAL SCORE    : "
        f"{result.renewal_score:.4f}"
    )

    print()

    print(
        f"SOURCE  : {result.source}"
    )

    print(
        f"GENERATED: {result.generated}"
    )

    print(
        f"FINAL   : {result.final_output}"
    )

    print(
        f"MANIFEST: {result.manifest}"
    )

    if result.warnings:

        print()
        print(
            "WARNINGS"
        )

        for warning in result.warnings:

            print(
                f"  - {warning}"
            )

    print(
        "============================================================"
    )
    print()


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Finalize validated MAVI renewal"
        )
    )

    parser.add_argument(
        "--source",
        required=True,
    )

    parser.add_argument(
        "--generated",
        required=True,
    )

    parser.add_argument(
        "--target-seconds",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--result",
        default="",
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    finalizer = (
        RenewalFinalizer()
    )

    try:

        result = finalizer.finalize(
            source=args.source,
            generated=args.generated,
            target_seconds=(
                args.target_seconds
            ),
        )

        print_result(
            result
        )

        if args.result:

            save_result(
                result,
                Path(
                    args.result
                )
                .expanduser()
                .resolve(),
            )

        return 0

    except Exception as exc:

        result = FinalizeResult(
            success=False,
            source=str(
                args.source
            ),
            generated=str(
                args.generated
            ),
            error=(
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
            metadata={
                "real_generation": True,
                "fake_audio": False,
                "procedural_audio": False,
                "placeholder_audio": False,
            },
        )

        if args.result:

            try:

                save_result(
                    result,
                    Path(
                        args.result
                    )
                    .expanduser()
                    .resolve(),
                )

            except Exception:

                pass

        print_result(
            result
        )

        print(
            f"ERROR: {result.error}"
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )