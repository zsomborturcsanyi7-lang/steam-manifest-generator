# Steam Manifest Generator

**Status:** ✅ Working — manifest generator tested, GUI + CLI, PyInstaller EXE built


Auto-generate Steam `.manifest` files for any game. GUI + CLI tool.

**Author:** Zsombi & Hermes Agent (Nous Research)

## Features
- Analyze existing manifests (`analyze_manifest.py`, `analyze_real_manifest.py`)
- Auto-generate manifests from game files (`auto_manifest_generator.py`)
- GUI version (`auto_gui_generator.py`, `gui_generator_final.py`)
- Ultimate fixed generator (`ultimate_fixed_generator.py`)
- Steam Spacewar integration
- PyInstaller EXE build support

## Files
| File | Description |
|------|-------------|
| `ultimate_fixed_generator.py` | Main manifest generator |
| `auto_gui_generator.py` | GUI-based generator |
| `manifest_installer.py` | Manifest installer tool |
| `universal_launcher.py` | Universal game launcher |
| `final_icon.ico` | Application icon |

## Usage
```bash
# GUI mode
python auto_gui_generator.py

# CLI mode
python ultimate_fixed_generator.py

# Build EXE
pyinstaller universal_launcher.spec
```

## Dependencies
- Python 3.8+
- PyInstaller (for EXE builds)
