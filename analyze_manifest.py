import struct

def analyze_manifest(filepath):
    with open(filepath, 'rb') as f:
        data = f.read(200)  # Olvassunk többet
    
    print(f"Fájl elemzése: {filepath}")
    print(f"Teljes fájlméret: {len(data)} bytes (első 200)")
    
    # Hex dump
    print("\nHex dump (első 64 byte):")
    for i in range(0, min(64, len(data)), 16):
        hex_part = ' '.join(f'{b:02X}' for b in data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"{i:04X}: {hex_part:<48}  {ascii_part}")
    
    # Próbáljuk meg értelmezni a Steam manifest formátumot
    print("\nFormátum elemzés:")
    
    if len(data) >= 4:
        magic = data[:4]
        print(f"Magic bytes: {magic.hex()} = {magic}")
        
        # Steam manifest formátumok:
        # - "VSIF" (Valve Steam Index File)
        # - Egyéb Valve formátumok
        
        if magic == b'VSIF':
            print("Formátum: Valve Steam Index File (VSIF)")
        elif magic == b'\x17\x0D\x55\x0A':
            print("Formátum: Valve manifest (régi formátum)")
        else:
            print(f"Ismeretlen magic: {magic.hex()}")
    
    # Nézzük meg a fájl végét is
    if len(data) > 100:
        print(f"\nUtolsó 32 byte:")
        end_data = data[-32:]
        hex_part = ' '.join(f'{b:02X}' for b in end_data)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in end_data)
        print(f"Hex: {hex_part}")
        print(f"ASCII: {ascii_part}")

# Elemzés
analyze_manifest(r'C:\Users\iga\Downloads\Plague_Inc__Evolved_T9\246621_1419867256180428038.manifest')

# Összehasonlítás a mi generált fájlunkkal
print("\n" + "="*60)
print("Összehasonlítás a mi generált fájlunkkal:")
analyze_manifest(r'C:\Users\iga\Desktop\j\Plague_Inc_Evolved_MAIN_FORMAT\246621_1419867256180428038.manifest')