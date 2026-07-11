import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_generator import ManifestHubGeneratorGUI
import tkinter as tk
import json
import time

# Create a hidden root window
root = tk.Tk()
root.withdraw()

# Create the app instance
app = ManifestHubGeneratorGUI(root)

# Test data for AppID 246620 (amit a célmappában láttunk)
appid = "246620"
game_name = "Test Game"

# Create sample JSON output structure
json_output = {
    "appid": int(appid),
    "name": game_name,
    "type": "Game",
    "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "depot": {
        "246620": {
            "config": {"oslist": "windows", "language": ""},
            "manifests": {"public": {"gid": "1568636336937792842", "size": "0", "download": "0"}},
            "decryptionkey": "testkey123"
        },
        "246621": {
            "config": {"oslist": "windows", "language": ""},
            "manifests": {"public": {"gid": "243223469513067432", "size": "0", "download": "0"}},
            "decryptionkey": ""
        }
    }
}

print("Generálás indítása...")
app.write_files(appid, game_name, json_output)

# Check the generated files
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"Test Game ({appid})")
print(f"\nGenerált fájlok a következő mappában: {output_dir}")

if os.path.exists(output_dir):
    files = os.listdir(output_dir)
    print(f"\nGenerált fájlok ({len(files)} db):")
    for file in files:
        filepath = os.path.join(output_dir, file)
        size = os.path.getsize(filepath)
        print(f"  - {file} ({size} bytes)")
        
        # Check manifest files
        if file.endswith(".manifest"):
            print(f"    Manifest tartalom:")
            with open(filepath, "r") as f:
                content = f.read()
                print(f"    {content[:200]}...")
else:
    print("HIBA: A kimeneti mappa nem jött létre!")

print("\nTeszt kész!")