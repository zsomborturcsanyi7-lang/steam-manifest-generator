import struct

def analyze_real_manifest():
    try:
        with open(r'C:\Users\iga\Downloads\Plague_Inc__Evolved_T9\246621_1419867256180428038.manifest', 'rb') as f:
            data = f.read(1000)  # Read more data
            
        print(f"Valódi manifest fájl elemzése")
        print(f"Teljes méret: {len(data)} bytes")
        
        print("\n1. Első 100 byte hex:")
        for i in range(0, 100, 16):
            hex_part = ' '.join(f'{b:02X}' for b in data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f"{i:04X}: {hex_part:<48}  {ascii_part}")
        
        print("\n2. Szöveges tartalom keresése:")
        # Look for text strings
        text_start = None
        strings_found = []
        for i in range(len(data)):
            if 32 <= data[i] < 127:  # Printable ASCII
                if text_start is None:
                    text_start = i
            else:
                if text_start is not None and i - text_start > 4:
                    try:
                        text = data[text_start:i].decode('ascii', errors='ignore')
                        if len(text) > 4 and not text.isspace():
                            strings_found.append((text_start, text))
                    except:
                        pass
                text_start = None
        
        for pos, text in strings_found[:10]:  # Show first 10 strings
            print(f"  Pos {pos}: '{text}'")
        
        print("\n3. Fájl vége (utolsó 100 byte):")
        if len(data) > 100:
            end_data = data[-100:]
            for i in range(0, 100, 16):
                hex_part = ' '.join(f'{b:02X}' for b in end_data[i:i+16])
                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in end_data[i:i+16])
                print(f"{len(data)-100+i:04X}: {hex_part:<48}  {ascii_part}")
        
        print("\n4. Fontos megfigyelések:")
        print("   - A fájl tartalmaz szöveges útvonalakat (pl. MonoBleedingEdge)")
        print("   - Ez egy valódi, teljes manifest fájl fájllistával")
        print("   - A mi generált fájljaink üresek, nincs bennük fájllista")
        
    except Exception as e:
        print(f"Hiba: {e}")

if __name__ == "__main__":
    analyze_real_manifest()