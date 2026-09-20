# -*- coding: utf-8 -*-

"""
============================================================
MAVI AI STUDIO
REAL AI PROVIDER BRIDGE
v0.1
============================================================

Gerçek müzik AI provider bağlantısının merkezidir.

KURALLAR:

1. API anahtarı yoksa READY görünmez.
2. API anahtarı yoksa üretim yapılmaz.
3. Fake audio yok.
4. Procedural audio yok.
5. Placeholder audio yok.
6. Provider başarısızsa başarı raporlanmaz.
7. Provider'dan gerçek audio dönmeden generation başarılı
   kabul edilmez.

Bu dosya provider seçimi ve gerçek HTTP iletişim katmanıdır.

Provider'a özel endpoint / authentication bilgileri config
üzerinden sağlanabilir.

============================================================
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
import urllib.error
import urllib.request
import uuid

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from core.provider_payload import (
    ProviderPayload,
)


# ============================================================
# ERRORS
# ============================================================

class ProviderError(Exception):
    """Provider temel hatası."""


class ProviderNotConfiguredError(
    ProviderError
):
    """Provider yapılandırılmamış."""


class ProviderAuthenticationError(
    ProviderError
):
    """API authentication hatası."""


class ProviderRequestError(
    ProviderError
):
    """Provider request hatası."""


class ProviderResponseError(
    ProviderError
):
    """Provider response hatası."""


class ProviderAudioError(
    ProviderError
):
    """Provider gerçek audio döndürmedi."""


# ============================================================
# STATUS
# ============================================================

@dataclass
class ProviderStatus:
    """
    Provider canlı durumu.
    """

    configured: bool = False

    authenticated: bool = False

    ready: bool = False

    provider_name: str = ""

    message: str = ""

    error: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESULT
# ============================================================

@dataclass
class ProviderGenerationResult:
    """
    Gerçek provider generation sonucu.
    """

    success: bool = False

    request_id: str = ""

    provider_name: str = ""

    audio_path: str = ""

    audio_format: str = ""

    duration: float = 0.0

    message: str = ""

    raw_response: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# REAL PROVIDER
# ============================================================

class RealMusicProvider:
    """
    Gerçek müzik AI provider bridge.

    Provider bilgileri environment variable üzerinden
    alınabilir:

        MAVI_PROVIDER_NAME
        MAVI_PROVIDER_URL
        MAVI_API_KEY
        MAVI_API_KEY_HEADER

    Varsayılan authentication header:

        Authorization: Bearer <API_KEY>

    Bu sınıf kendi başına audio üretmez.

    Provider'dan gerçek audio gelmesi gerekir.
    """

    def __init__(
        self,
        provider_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: Optional[str] = None,
        timeout: int = 300,
    ) -> None:

        self.provider_name = (
            provider_name
            or os.environ.get(
                "MAVI_PROVIDER_NAME",
                "",
            )
        ).strip()

        self.endpoint = (
            endpoint
            or os.environ.get(
                "MAVI_PROVIDER_URL",
                "",
            )
        ).strip()

        self.api_key = (
            api_key
            or os.environ.get(
                "MAVI_API_KEY",
                "",
            )
        ).strip()

        self.api_key_header = (
            api_key_header
            or os.environ.get(
                "MAVI_API_KEY_HEADER",
                "Authorization",
            )
        ).strip()

        self.timeout = max(
            10,
            int(timeout),
        )

        self.history: list[
            ProviderGenerationResult
        ] = []

    # ========================================================
    # STATUS
    # ========================================================

    def status(
        self,
    ) -> ProviderStatus:

        if not self.provider_name:

            return ProviderStatus(
                configured=False,
                authenticated=False,
                ready=False,
                message=(
                    "AI provider yapılandırılmamış."
                ),
            )

        if not self.endpoint:

            return ProviderStatus(
                configured=False,
                authenticated=False,
                ready=False,
                provider_name=(
                    self.provider_name
                ),
                message=(
                    "AI provider endpoint eksik."
                ),
            )

        if not self.api_key:

            return ProviderStatus(
                configured=True,
                authenticated=False,
                ready=False,
                provider_name=(
                    self.provider_name
                ),
                message=(
                    "API anahtarı bulunamadı."
                ),
            )

        return ProviderStatus(
            configured=True,
            authenticated=True,
            ready=True,
            provider_name=(
                self.provider_name
            ),
            message=(
                "AI provider hazır."
            ),
            metadata={
                "real_provider": True,
                "fake_audio": False,
                "procedural_audio": False,
            },
        )

    # ========================================================
    # REQUIRE READY
    # ========================================================

    def _require_ready(
        self,
    ) -> None:

        current = self.status()

        if not current.configured:

            raise ProviderNotConfiguredError(
                current.message
            )

        if not current.authenticated:

            raise ProviderAuthenticationError(
                current.message
            )

        if not current.ready:

            raise ProviderError(
                current.message
            )

    # ========================================================
    # HEADERS
    # ========================================================

    def _headers(
        self,
    ) -> dict[str, str]:

        self._require_ready()

        headers = {
            "Content-Type":
                "application/json",

            "Accept":
                "application/json",
        }

        if self.api_key_header.lower() == (
            "authorization"
        ):

            headers[
                self.api_key_header
            ] = (
                f"Bearer {self.api_key}"
            )

        else:

            headers[
                self.api_key_header
            ] = self.api_key

        return headers

    # ========================================================
    # REQUEST BODY
    # ========================================================

    @staticmethod
    def _build_body(
        payload: ProviderPayload,
    ) -> dict[str, Any]:

        data = payload.to_dict()

        # ----------------------------------------------------
        # HARD SAFETY FLAGS
        # ----------------------------------------------------

        data[
            "real_audio_required"
        ] = True

        data[
            "fake_audio_allowed"
        ] = False

        data[
            "procedural_audio_allowed"
        ] = False

        data[
            "source_based"
        ] = True

        # ----------------------------------------------------
        # EXPLICIT OUTPUT REQUIREMENT
        # ----------------------------------------------------

        data[
            "response_format"
        ] = "real_audio_file"

        data[
            "audio_format"
        ] = "wav"

        data[
            "output_requirements"
        ] = {
            "must_return_real_audio":
                True,

            "must_follow_source":
                True,

            "must_preserve_melody":
                True,

            "must_preserve_rhythm":
                True,

            "must_preserve_form":
                True,

            "must_not_generate_unrelated_song":
                True,

            "must_not_generate_arcade_music":
                True,

            "must_not_generate_chiptune":
                True,

            "must_not_generate_8bit":
                True,

            "must_not_return_midi_only":
                True,
        }

        return data

    # ========================================================
    # HTTP POST
    # ========================================================

    def _post(
        self,
        body: dict[str, Any],
    ) -> dict[str, Any]:

        self._require_ready()

        encoded = json.dumps(
            body,
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        request = urllib.request.Request(
            self.endpoint,
            data=encoded,
            headers=self._headers(),
            method="POST",
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                response_data = (
                    response.read()
                )

        except urllib.error.HTTPError as exc:

            try:

                error_body = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                )

            except Exception:

                error_body = ""

            if exc.code in (
                401,
                403,
            ):

                raise ProviderAuthenticationError(
                    (
                        f"Provider authentication "
                        f"hatası ({exc.code}). "
                        f"{error_body[-1000:]}"
                    )
                ) from exc

            raise ProviderRequestError(
                (
                    f"Provider HTTP "
                    f"hatası ({exc.code}). "
                    f"{error_body[-1000:]}"
                )
            ) from exc

        except urllib.error.URLError as exc:

            raise ProviderRequestError(
                f"Provider bağlantı hatası: {exc}"
            ) from exc

        except TimeoutError as exc:

            raise ProviderRequestError(
                "Provider bağlantısı zaman aşımına uğradı."
            ) from exc

        if not response_data:

            raise ProviderResponseError(
                "Provider boş response döndürdü."
            )

        try:

            decoded = json.loads(
                response_data.decode(
                    "utf-8"
                )
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:

            raise ProviderResponseError(
                "Provider JSON response döndürmedi."
            ) from exc

        if not isinstance(
            decoded,
            dict,
        ):

            raise ProviderResponseError(
                "Provider response formatı geçersiz."
            )

        return decoded

    # ========================================================
    # AUDIO EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_audio(
        response: dict[str, Any],
    ) -> tuple[
        Optional[bytes],
        Optional[str],
    ]:

        # ----------------------------------------------------
        # DIRECT BASE64 FIELDS
        # ----------------------------------------------------

        possible_fields = [
            "audio_base64",
            "audio",
            "wav_base64",
            "audio_data",
        ]

        for field_name in possible_fields:

            value = response.get(
                field_name
            )

            if not isinstance(
                value,
                str,
            ):

                continue

            value = value.strip()

            if not value:

                continue

            # data URI
            if "," in value and (
                value.startswith(
                    "data:audio/"
                )
            ):

                value = value.split(
                    ",",
                    1,
                )[1]

            try:

                return (
                    base64.b64decode(
                        value,
                        validate=True,
                    ),
                    "wav",
                )

            except Exception:

                continue

        # ----------------------------------------------------
        # NESTED AUDIO
        # ----------------------------------------------------

        audio_object = response.get(
            "audio"
        )

        if isinstance(
            audio_object,
            dict,
        ):

            for field_name in (
                "base64",
                "data",
                "audio_base64",
            ):

                value = (
                    audio_object.get(
                        field_name
                    )
                )

                if not isinstance(
                    value,
                    str,
                ):

                    continue

                try:

                    return (
                        base64.b64decode(
                            value,
                            validate=True,
                        ),
                        "wav",
                    )

                except Exception:

                    pass

        return (
            None,
            None,
        )

    # ========================================================
    # SAVE AUDIO
    # ========================================================

    @staticmethod
    def _save_audio(
        audio_data: bytes,
        output_directory: Optional[
            str | Path
        ] = None,
        request_id: str = "",
        extension: str = "wav",
    ) -> Path:

        if not audio_data:

            raise ProviderAudioError(
                "Provider gerçek audio verisi döndürmedi."
            )

        directory = (
            Path(
                output_directory
            ).expanduser()
            if output_directory
            else Path(
                "output"
            )
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_request_id = (
            request_id
            or uuid.uuid4().hex
        )

        output = (
            directory
            / f"{safe_request_id}_generated.{extension}"
        )

        # ----------------------------------------------------
        # WAV SIGNATURE CHECK
        # ----------------------------------------------------

        if extension.lower() == "wav":

            if not audio_data.startswith(
                b"RIFF"
            ):

                raise ProviderAudioError(
                    "Provider audio WAV olarak belirtilmiş "
                    "ancak geçerli RIFF başlığı yok."
                )

            if (
                len(audio_data) < 12
                or audio_data[8:12]
                != b"WAVE"
            ):

                raise ProviderAudioError(
                    "Provider WAV response geçersiz."
                )

        try:

            with open(
                output,
                "wb",
            ) as handle:

                handle.write(
                    audio_data
                )

        except OSError as exc:

            raise ProviderAudioError(
                f"Provider audio diske yazılamadı: {exc}"
            ) from exc

        if not output.exists():

            raise ProviderAudioError(
                "Provider audio çıktısı oluşmadı."
            )

        if output.stat().st_size <= 44:

            raise ProviderAudioError(
                "Provider audio dosyası boş veya geçersiz."
            )

        return output.resolve()

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        payload: ProviderPayload,
        output_directory: Optional[
            str | Path
        ] = None,
    ) -> ProviderGenerationResult:

        self._require_ready()

        if not isinstance(
            payload,
            ProviderPayload,
        ):

            raise ProviderRequestError(
                "Geçersiz ProviderPayload."
            )

        request_id = (
            payload.request_id
            or uuid.uuid4().hex
        )

        body = self._build_body(
            payload
        )

        response = self._post(
            body
        )

        audio_data, extension = (
            self._extract_audio(
                response
            )
        )

        if not audio_data:

            raise ProviderAudioError(
                "Provider başarılı response verdi "
                "ancak gerçek audio döndürmedi."
            )

        audio_path = self._save_audio(
            audio_data=audio_data,
            output_directory=output_directory,
            request_id=request_id,
            extension=(
                extension
                or "wav"
            ),
        )

        result = ProviderGenerationResult(
            success=True,

            request_id=request_id,

            provider_name=(
                self.provider_name
            ),

            audio_path=str(
                audio_path
            ),

            audio_format=(
                extension
                or "wav"
            ),

            message=(
                "Provider gerçek audio üretti."
            ),

            raw_response=response,

            metadata={
                "real_audio":
                    True,

                "fake_audio":
                    False,

                "procedural_audio":
                    False,

                "source_based":
                    True,

                "provider_authenticated":
                    True,
            },
        )

        self.history.append(
            result
        )

        if len(
            self.history
        ) > 100:

            self.history = (
                self.history[-100:]
            )

        return result

    # ========================================================
    # LAST RESULT
    # ========================================================

    def last_result(
        self,
    ) -> Optional[
        ProviderGenerationResult
    ]:

        if not self.history:

            return None

        return self.history[-1]

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_history(
        self,
    ) -> None:

        self.history.clear()


# ============================================================
# DEFAULT PROVIDER
# ============================================================

MAVI_PROVIDER = RealMusicProvider()


# ============================================================
# PUBLIC HELPERS
# ============================================================

def provider_status() -> ProviderStatus:

    return MAVI_PROVIDER.status()


def provider_ready() -> bool:

    return MAVI_PROVIDER.status().ready


def generate_with_provider(
    payload: ProviderPayload,
    output_directory: Optional[
        str | Path
    ] = None,
) -> ProviderGenerationResult:

    return MAVI_PROVIDER.generate(
        payload=payload,
        output_directory=output_directory,
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "ProviderError",
    "ProviderNotConfiguredError",
    "ProviderAuthenticationError",
    "ProviderRequestError",
    "ProviderResponseError",
    "ProviderAudioError",
    "ProviderStatus",
    "ProviderGenerationResult",
    "RealMusicProvider",
    "MAVI_PROVIDER",
    "provider_status",
    "provider_ready",
    "generate_with_provider",
]
