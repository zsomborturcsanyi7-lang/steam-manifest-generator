# steam-manifest-generator

Steam manifest file generator featuring graphical and command-line interfaces.

## Overview & Purpose
steam-manifest-generator simplifies the creation and inspection of Steam `.manifest` configuration files for game deployment and library management.

## Key Features
- Dual Graphical User Interface (Tkinter) and CLI mode.
- Automated file checksum calculation and manifest formatting.
- Standalone executable build support via PyInstaller.

## Tech Stack & Dependencies
- **Language**: Python 3.9+
- **GUI Framework**: Tkinter
- **Packaging**: PyInstaller

## Project Structure
```text
steam-manifest-generator/
├── gui_generator_final.py
├── manifest_core.py
├── requirements.txt
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.9+

### Steps
```bash
git clone https://github.com/zsomborturcsanyi7-lang/steam-manifest-generator.git
cd steam-manifest-generator
python gui_generator_final.py
```

## Usage Examples
```bash
python gui_generator_final.py --cli --path "C:\Games\TargetGame"
```

## Status & License
Status: Functional Application.
License: MIT
