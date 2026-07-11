import struct
import os

def create_simple_steam_manifest(depot_id, manifest_id, output_path):
    """
    Egyszerű Steam manifest fájl létrehozása
    Based on analysis of real Steam manifest files
    """
    # A valódi manifest fájlok elején van egy protobuf fejléc
    # A hex dump alapján: D0 17 F6 71 ... majd szöveges adatok
    
    data = bytearray()
    
    # Protobuf field 1: depot id (varint)
    # Field number: 1 (0000 1000), value: depot_id
    data.append(0x08)  # Field 1, varint
    # Varint encoding of depot_id
    value = depot_id
    while value > 0x7F:
        data.append((value & 0x7F) | 0x80)
        value >>= 7
    data.append(value)
    
    # Protobuf field 2: manifest id (varint)  
    data.append(0x10)  # Field 2, varint
    # Varint encoding of manifest_id
    value = manifest_id
    while value > 0x7F:
        data.append((value & 0x7F) | 0x80)
        value >>= 7
    data.append(value)
    
    # Protobuf field 3: file entries (length-delimited)
    # Üres fájllista
    data.append(0x1A)  # Field 3, length-delimited
    data.append(0x00)  # Length: 0
    
    # Protobuf field 4: chunks (length-delimited)
    # Üres chunk lista
    data.append(0x22)  # Field 4, length-delimited  
    data.append(0x00)  # Length: 0
    
    # További protobuf mezők...
    # Creation time
    data.append(0x28)  # Field 5, varint
    data.append(0x00)  # Value: 0
    
    # Fájlok száma
    data.append(0x30)  # Field 6, varint
    data.append(0x00)  # Value: 0
    
    # Teljes méret
    data.append(0x38)  # Field 7, varint  
    data.append(0x00)  # Value: 0
    
    # Írjuk fájlba
    with open(output_path, 'wb') as f:
        f.write(bytes(data))
    
    return len(data)

# Teszt
print("Egyszerű Steam manifest fájl generálása...")
depot_id = 246621
manifest_id = 1419867256180428038

output_dir = r"C:\Users\iga\Desktop\j\test_manifests"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"{depot_id}_{manifest_id}.manifest")
size = create_simple_steam_manifest(depot_id, manifest_id, output_file)

print(f"Manifest fájl létrehozva: {output_file}")
print(f"Méret: {size} bytes")

# Összehasonlítás a valódi fájllal
real_file = r"C:\Users\iga\Downloads\Plague_Inc__Evolved_T9\246621_1419867256180428038.manifest"
if os.path.exists(real_file):
    real_size = os.path.getsize(real_file)
    print(f"\nValódi manifest fájl mérete: {real_size} bytes")
    print(f"Különbség: {real_size - size} bytes")
    
    # Nézzük meg az első néhány byte-ot
    with open(real_file, 'rb') as f:
        real_data = f.read(20)
    
    with open(output_file, 'rb') as f:
        our_data = f.read(20)
    
    print(f"\nValódi fájl első 20 byte: {real_data.hex()}")
    print(f"Mi fájl első 20 byte: {our_data.hex()}")
else:
    print(f"\nValódi fájl nem található: {real_file}")

print("\nA manifest fájl tartalmazza a depot_id-t és manifest_id-t protobuf formátumban.")
print("Ez egy egyszerű, de működő manifest fájl lehet a Steam számára.")