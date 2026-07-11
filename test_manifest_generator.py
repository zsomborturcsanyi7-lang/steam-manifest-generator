import os
import json
import re
import time

# Teszteljük a javított manifest generálást
def test_manifest_generation():
    appid = "730"
    game_name = "Counter-Strike 2"
    safe_name = re.sub(r'[\\/*?:"<>|]', "", game_name)
    base_dir = r"C:\Users\iga\Desktop\j"
    output_dir = os.path.join(base_dir, f"{safe_name} ({appid})")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Teszt adatok
    json_output = {
        "depot": {
            "730": {
                "manifests": {"public": {"gid": "1234567890123456789"}},
                "decryptionkey": "testkey123"
            }
        }
    }
    
    # Manifest generálás (a javított kóddal)
    for d_id, data in json_output["depot"].items():
        gid = data["manifests"]["public"]["gid"]
        manifest_data = {
            "depot_id": int(d_id),
            "gid": gid,
            "creation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "size": 0,
            "chunks": []
        }
        manifest_path = os.path.join(output_dir, f"{d_id}_{gid}.manifest")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
        
        print(f"Manifest fájl létrehozva: {manifest_path}")
        print("Tartalom:")
        with open(manifest_path, "r") as f:
            print(f.read())
    
    # Ellenőrizzük a gui_generator.py-t is
    print("\n--- gui_generator.py ellenőrzése ---")
    with open(os.path.join(base_dir, "gui_generator.py"), "r", encoding="utf-8") as f:
        content = f.read()
        if "GENERATED MANIFEST CONTENT" in content:
            print("HIBA: Még mindig van 'GENERATED MANIFEST CONTENT' a kódban!")
        else:
            print("OK: A 'GENERATED MANIFEST CONTENT' szöveg nincs a kódban")
        
        if "json.dump(manifest_data" in content:
            print("OK: A javított manifest generálás kódja benne van")
        else:
            print("HIBA: A javított kód nincs benne")

if __name__ == "__main__":
    test_manifest_generation()