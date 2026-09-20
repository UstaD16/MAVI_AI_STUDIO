from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.audio_io import require_valid_audio
from core.analyzer import ANALYZER
from core.music_dna import MUSIC_DNA_BUILDER
from core.renewal import RENEWAL_ENGINE
from core.generation_request import build_generation_request
from core.provider_payload import build_provider_payload
from core.real_provider_router import REAL_PROVIDER_ROUTER


OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "test_real_generation.wav"


def ask_source_audio() -> Path:
    print()
    print("=" * 72)
    print("MAVI AI STUDIO - REAL GENERATION TEST")
    print("=" * 72)
    print()
    print("Kaynak müzik dosyasının tam yolunu gir.")
    print("Örnek:")
    print(r"C:\Users\ORGOC\Desktop\muzik.wav")
    print()

    raw = input("SOURCE AUDIO > ").strip().strip('"')

    if not raw:
        raise RuntimeError("Kaynak ses dosyası girilmedi.")

    source = Path(raw)

    if not source.is_absolute():
        source = (ROOT / source).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Kaynak dosya bulunamadı: {source}")

    require_valid_audio(source)

    return source


def ask_instruments() -> list[str]:
    print()
    print("İstediğin yeni enstrümanları virgülle yaz.")
    print()
    print("Örnek:")
    print("bass guitar, davul, trumpet")
    print()
    print("Alternatif:")
    print("bağlama, zurna, si bemol klarnet")
    print()

    raw = input("INSTRUMENTS > ").strip()

    if not raw:
        return [
            "bass guitar",
            "davul",
            "trumpet",
        ]

    instruments = [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]

    if not instruments:
        raise RuntimeError("Enstrüman listesi oluşturulamadı.")

    return instruments


def print_provider_status() -> dict:
    status = REAL_PROVIDER_ROUTER.status()

    print()
    print("-" * 72)
    print("REAL PROVIDER STATUS")
    print("-" * 72)

    for key, value in status.items():
        print(f"{key:16}: {value}")

    print("-" * 72)

    return status


def main() -> int:
    try:
        print_provider_status()

        source_path = ask_source_audio()
        instruments = ask_instruments()

        print()
        print("=" * 72)
        print("1/6 ANALYZER")
        print("=" * 72)

        analysis = ANALYZER.analyze(str(source_path))

        print()
        print("ANALYSIS:")
        print(f"  BPM       : {getattr(analysis, 'bpm', 0)}")
        print(f"  KEY       : {getattr(analysis, 'key', '')}")
        print(f"  GENRE     : {getattr(analysis, 'genre', '')}")
        print(f"  ENERGY    : {getattr(analysis, 'energy', 0)}")
        print(f"  DURATION  : {getattr(analysis, 'duration', 0)}")

        print()
        print("=" * 72)
        print("2/6 MUSIC DNA")
        print("=" * 72)

        dna = MUSIC_DNA_BUILDER.build(analysis)

        print("Music DNA oluşturuldu.")
        print(f"  BPM       : {getattr(dna, 'bpm', 0)}")
        print(f"  KEY       : {getattr(dna, 'key', '')}")
        print(f"  GENRE     : {getattr(dna, 'genre', '')}")
        print(f"  ENERGY    : {getattr(dna, 'energy', 0)}")

        print()
        print("=" * 72)
        print("3/6 RENEWAL PLAN")
        print("=" * 72)

        renewal_plan = RENEWAL_ENGINE.create_plan(
            analysis=analysis,
            music_dna=dna,
            command="Eski müziğin karakterini ve melodisini koru; "
                    "modern ve temiz bir düzenleme yap.",
            instruments=instruments,
        )

        print("Renewal Plan oluşturuldu.")

        plan_instruments = getattr(
            renewal_plan,
            "instruments",
            [],
        )

        print()
        print("REQUESTED INSTRUMENTS:")

        if plan_instruments:
            for instrument in plan_instruments:
                name = getattr(
                    instrument,
                    "name",
                    str(instrument),
                )
                print(f"  - {name}")
        else:
            for instrument in instruments:
                print(f"  - {instrument}")

        print()
        print("=" * 72)
        print("4/6 GENERATION REQUEST")
        print("=" * 72)

        try:
            request = build_generation_request(
                source_path=str(source_path),
                analysis=analysis,
                music_dna=dna,
                renewal_plan=renewal_plan,
            )
        except TypeError:
            request = build_generation_request(
                source_path=str(source_path),
                analysis=analysis,
                music_dna=dna,
                renewal_plan=renewal_plan,
                command="Eski müziğin karakterini ve melodisini koru; "
                        "modern ve temiz bir düzenleme yap.",
                instruments=instruments,
            )

        print("GenerationRequest hazır.")

        print()
        print("=" * 72)
        print("5/6 PROVIDER PAYLOAD")
        print("=" * 72)

        try:
            payload = build_provider_payload(request)
        except TypeError:
            payload = build_provider_payload(
                request=request,
                analysis=analysis,
                music_dna=dna,
                renewal_plan=renewal_plan,
            )

        print("ProviderPayload hazır.")

        print()
        print("=" * 72)
        print("6/6 REAL AI GENERATION")
        print("=" * 72)
        print()
        print("Gerçek Stable Audio üretimi başlatılıyor.")
        print("Bu aşamada sahte/prosedürel ses kullanılmaz.")
        print()
        print(f"SOURCE : {source_path}")
        print(f"OUTPUT : {OUTPUT_PATH}")
        print()

        status = REAL_PROVIDER_ROUTER.status()

        if not status.get("configured"):
            print("HATA: Stability API anahtarı yapılandırılmamış.")
            print()
            print("STABILITY_API_KEY ortam değişkenini ayarla.")
            print()
            return 2

        if not status.get("ready"):
            print("HATA: Real provider hazır değil.")
            print()
            print(status)
            print()
            return 3

        result = REAL_PROVIDER_ROUTER.generate(
            payload,
            OUTPUT_PATH,
        )

        if not isinstance(result, dict):
            raise RuntimeError(
                "Real provider beklenmeyen bir sonuç döndürdü."
            )

        print()
        print("-" * 72)
        print("GENERATION RESULT")
        print("-" * 72)

        for key, value in result.items():
            print(f"{key:18}: {value}")

        print("-" * 72)

        if not result.get("success"):
            raise RuntimeError(
                result.get(
                    "error",
                    "Real generation başarısız.",
                )
            )

        output_path = result.get("output_path")

        if not output_path:
            output_path = OUTPUT_PATH

        output_path = Path(output_path)

        if not output_path.exists():
            raise RuntimeError(
                f"Provider başarılı görünüyor ancak WAV bulunamadı: "
                f"{output_path}"
            )

        require_valid_audio(output_path)

        print()
        print("=" * 72)
        print("REAL GENERATION SUCCESS")
        print("=" * 72)
        print()
        print(f"Gerçek üretilen WAV:")
        print(output_path)
        print()

        return 0

    except KeyboardInterrupt:
        print()
        print("Test kullanıcı tarafından durduruldu.")
        return 130

    except Exception as exc:
        print()
        print("=" * 72)
        print("REAL GENERATION FAILED")
        print("=" * 72)
        print()
        print(type(exc).__name__)
        print(str(exc))
        print()

        return 1


if __name__ == "__main__":
    raise SystemExit(main())