import os
import re
import time
import random
import struct

def generate_binary_manifest(depot_id, manifest_id):
    """Bináris manifest fájl generálása (egyszerű placeholder)"""
    data = bytearray()
    
    # Egyszerű fejléc
    data.extend(b'MANF')  # Magic number
    data.extend(struct.pack('<I', depot_id))  # Depot ID
    data.extend(struct.pack('<Q', int(manifest_id)))  # Manifest ID
    data.extend(struct.pack('<I', 0))  # Size
    data.extend(struct.pack('<I', 0))  # Chunk count
    
    # Véletlen adatok (placeholder)
    for _ in range(100):
        data.append(random.randint(0, 255))
        
    return bytes(data)

# Főmappa formátum generálása
appid = "246620"
game_name = "Plague Inc: Evolved"
safe_name = re.sub(r'[\\/*?:"<>|]', "", game_name)
base_dir = r"C:\Users\iga\Desktop\j"
output_dir = os.path.join(base_dir, f"{safe_name}_MAIN_FORMAT")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. LUA fájl - pontosan úgy, mint a főmappában
print("1. LUA fájl generálása...")
lua_content = """addappid(246620)
addappid(246581,0,"976876bb00da7560e27d8ee567af59026d035d782916bb06a5d77186aa7d59f2")
addappid(246620,0,"540f338bcb2eb1e9d469f9302ea6b60481008cef56be0e01e378a92f72041732")
addappid(246621,0,"19ad23e511f566d12808b52a4cfabb6457d8acc91815acbaddc6fdfe76dacfbe")
addappid(246622,0,"dd2e9f4b104c4ce27c22dadf3dd13210e54a51c0fa09f14addd72d8c05121f89")
addappid(246623,0,"516e04bc485cebe525f9d28a727a2fbc29aad932656bcb36238448797d52a337")
addappid(246624,0,"b7170469891310d1335cb12516164cff304a536657ad2c35fad0950719133123")
addappid(246625,0,"3c1666a26d525bf81d9b9c90bbd47b0fd637db2d2056950f5a9c8c72f76109bb")
addappid(246626,0,"8d0fb3394cd06ae93b744373a1024f9a4c4b5c4a1e30ed95fadbb05718d02ff2")
"""

with open(os.path.join(output_dir, "246620.lua"), "w", encoding="utf-8") as f:
    f.write(lua_content)

# 2. Bináris manifest fájlok - pontosan úgy, mint a főmappában
print("2. Bináris manifest fájlok generálása...")
manifest_files = {
    "246621_1419867256180428038.manifest": (246621, 1419867256180428038),
    "246622_3385820183857561230.manifest": (246622, 3385820183857561230),
    "246623_8964011060351618132.manifest": (246623, 8964011060351618132),
    "246624_712597846969897429.manifest": (246624, 712597846969897429),
    "246625_8060770308095908779.manifest": (246625, 8060770308095908779),
    "246626_1898025581291238622.manifest": (246626, 1898025581291238622),
}

for filename, (depot_id, manifest_id) in manifest_files.items():
    binary_data = generate_binary_manifest(depot_id, manifest_id)
    with open(os.path.join(output_dir, filename), "wb") as f:
        f.write(binary_data)
    print(f"  - {filename} létrehozva ({len(binary_data)} bytes)")

# 3. Összehasonlítás a főmappával
print("\n3. Összehasonlítás a főmappával:")
main_folder = r"C:\Users\iga\Downloads\Plague_Inc__Evolved_T9"

if os.path.exists(main_folder):
    main_files = os.listdir(main_folder)
    generated_files = os.listdir(output_dir)
    
    print(f"Főmappa fájljai ({len(main_files)} db):")
    for f in sorted(main_files):
        print(f"  - {f}")
    
    print(f"\nGenerált fájljaink ({len(generated_files)} db):")
    for f in sorted(generated_files):
        print(f"  - {f}")
    
    # Ellenőrizzük a LUA fájlokat
    print("\n4. LUA fájlok összehasonlítása:")
    with open(os.path.join(main_folder, "246620.lua"), "r") as f:
        main_lua = f.read()
    
    with open(os.path.join(output_dir, "246620.lua"), "r") as f:
        our_lua = f.read()
    
    if main_lua == our_lua:
        print("  ✓ A LUA fájlok IDENTIKUSAK!")
    else:
        print("  ✗ A LUA fájlok KÜLÖNBÖZŐEK!")
        print(f"  Főmappa LUA hossz: {len(main_lua)} karakter")
        print(f"  Mi LUA hossz: {len(our_lua)} karakter")
        
        # Soronkénti összehasonlítás
        main_lines = main_lua.strip().split('\n')
        our_lines = our_lua.strip().split('\n')
        
        print(f"\n  Sorok száma: Főmappa={len(main_lines)}, Mi={len(our_lines)}")
        
        for i in range(min(len(main_lines), len(our_lines))):
            if main_lines[i] != our_lines[i]:
                print(f"  Első különböző sor ({i+1}):")
                print(f"    Főmappa: {main_lines[i]}")
                print(f"    Mi: {our_lines[i]}")
                break
else:
    print(f"A főmappa nem található: {main_folder}")

print(f"\n✓ Generálás kész! Fájlok itt: {output_dir}")