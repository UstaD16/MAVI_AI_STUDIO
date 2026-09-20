from core.source_manager import SOURCE_MANAGER


def main() -> None:
    print()
    print("=" * 72)
    print("MAVI AI STUDIO • SOURCE MUSIC MANAGER")
    print("=" * 72)
    print()

    info = SOURCE_MANAGER.describe()

    print(f"Kaynak klasörü : {info['directory']}")
    print(f"Müzik sayısı   : {info['count']}")
    print()

    if not info["files"]:
        print("Kaynak klasöründe henüz müzik yok.")
        print()
        print("Müziklerini buraya koy:")
        print(info["directory"])
    else:
        print("Bulunan müzikler:")
        print("-" * 72)

        for index, item in enumerate(info["files"], start=1):
            print(f"{index:02d}. {item['filename']}")

        print()
        print(f"İlk kaynak: {SOURCE_MANAGER.first_track()}")

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()