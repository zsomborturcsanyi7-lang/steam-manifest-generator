# Steam Toolkit & Online Fix Generator

Ez a projekt egy Python-alapú eszközkészlet Steam játékok manifest fájljainak generálásához és online multiplayer "fixek" (Spacewar álcázás) automatizált kezeléséhez.

## Projekt Áttekintés

A projekt két fő komponensből áll:
1.  **Manifest Generátor**: Lekéri a Steam API-ból a játékok adatait és legenerálja a szükséges `.manifest` és `.lua` konfigurációs fájlokat.
2.  **Universal Launcher**: Lehetővé teszi a játékok "patchelését" és indítását a Spacewar (AppID 480) hálózatán keresztül, egyedi játékosnevek és SteamID-k biztosításával a zökkenőmentes multiplayer élményért.

## Technológiai Stack

- **Nyelv**: Python 3.x
- **GUI**: Tkinter
- **Hálózat**: Requests (Steam API eléréshez)
- **Csomagolás**: PyInstaller (önálló .exe fájlok létrehozásához)
- **Emuláció**: Goldberg Steam Emulator kompatibilitás (a `spacewar` mappán keresztül)

## Fő Fájlok és Könyvtárak

- `gui_generator.py`: A manifest generátor forráskódja.
- `universal_launcher.py`: Az online fixet kezelő és játékot indító alkalmazás.
- `spacewar/`: Sablon könyvtár, amely a módosított `steam_api.dll` és `steam_api64.dll` fájlokat tartalmazza.
- `SteamManifestGenerator.spec`: PyInstaller konfiguráció a buildeléshez.
- `dist/` & `build/`: A lefordított futtatható állományok és átmeneti fájlok helye.

## Használati Útmutató

### Manifest Generálás
1. Futtasd a `gui_generator.py`-t.
2. Add meg a cél AppID-t.
3. A program létrehoz egy mappát a játék adataival és a manifest fájlokkal.

### Online Fix & Játék Indítás
1. Futtasd a `universal_launcher.py`-t.
2. Add meg a kívánt játékbeli nevedet.
3. Válaszd ki a játék indítófájlját (.exe).
4. Kattints a "PATCH & INDÍTÁS" gombra.
5. A program automatikusan kezeli a fájlokat, beállítja az AppID-t és elindítja a játékot.
6. A játék bezárása után lehetőség van az eredeti fájlok visszaállítására.

## Fejlesztési Irányelvek

- **Surgical Updates**: Csak a szükséges fájlmódosításokat végezzük el, mindig tartsuk meg az eredeti fájlok biztonsági mentését (`.original`).
- **Threading**: A hálózati műveleteket és a játék indítását külön szálon vagy aszinkron módon kell kezelni, hogy a GUI reszponzív maradjon.
- **Portabilitás**: A `spacewar` mappának mindig a launcher mellett kell lennie a megfelelő működéshez.

## Buildelés

Az alkalmazás fordítása a következő paranccsal végezhető el:
```bash
pyinstaller SteamManifestGenerator.spec
```
Vagy a launcherhez:
```bash
pyinstaller --noconsole --onefile --icon=final_icon.ico universal_launcher.py
```
