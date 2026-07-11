#!/usr/bin/env python3
"""
ULTIMATE FIXED STEAM MANIFEST GENERATOR
Generál valószerű manifest fájlokat fájllistával, hash-ekkel
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import re
import time
import random
import struct
import hashlib
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime

class UltimateFixedGenerator:
    def __init__(self, appid):
        self.appid = appid
        self.game_name = f"AppID {appid}"
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = self.base_dir / "ultimate_generated" / f"game_{appid}"
        
    def run(self):
        """Main execution"""
        print("=" * 60)
        print("ULTIMATE FIXED MANIFEST GENERATOR")
        print(f"AppID: {self.appid}")
        print("=" * 60)
        
        try:
            # Get game info
            self.get_game_info()
            
            # Create output
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate files
            lua_path = self.generate_lua_file()
            manifests = self.generate_realistic_manifests()
            acf_path = self.generate_acf_file()
            
            # Copy to Steam
            self.copy_to_steam(lua_path, manifests, acf_path)
            
            print("\n" + "=" * 60)
            print("✅ GENERÁLÁS SIKERES!")
            print("=" * 60)
            print(f"Játék: {self.game_name}")
            print(f"Manifest fájlok: {len(manifests)} db")
            print(f"Fájlok tartalmaznak valószerű adatokat!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ HIBA: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_game_info(self):
        """Get game name"""
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={self.appid}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            if str(self.appid) in data and data[str(self.appid)]['success']:
                self.game_name = data[str(self.appid)]['data']['name']
                print(f"Játék: {self.game_name}")
        except:
            print(f"Játék: Ismeretlen (AppID: {self.appid})")
    
    def generate_lua_file(self):
        """Generate LUA file with realistic keys"""
        lua_path = self.output_dir / f"{self.appid}.lua"
        
        with open(lua_path, 'w', encoding='utf-8') as f:
            f.write(f"addappid({self.appid})\n")
            
            base_id = int(self.appid)
            for i in range(7):  # Main + 6 depots
                depot_id = base_id + i
                key = self.generate_realistic_key()
                f.write(f'addappid({depot_id},0,"{key}")\n')
        
        print(f"✓ LUA fájl: {lua_path.name}")
        return lua_path
    
    def generate_realistic_key(self):
        """Generate realistic-looking depot key"""
        # Real Steam keys are 64 hex chars
        return hashlib.sha256(os.urandom(32)).hexdigest()
    
    def generate_realistic_manifests(self):
        """Generate realistic manifest files with file lists"""
        manifests = []
        base_id = int(self.appid)
        
        # Common game file patterns
        file_patterns = [
            "{game}/bin/{game}.exe",
            "{game}/data/game.dat",
            "{game}/data/levels/level1.map",
            "{game}/data/levels/level2.map",
            "{game}/data/textures/texture1.dds",
            "{game}/data/textures/texture2.dds",
            "{game}/data/sounds/sound1.wav",
            "{game}/data/sounds/sound2.wav",
            "{game}/data/music/track1.ogg",
            "{game}/data/music/track2.ogg",
            "{game}/data/localization/english.txt",
            "{game}/data/localization/hungarian.txt",
            "{game}/redist/vcredist_x64.exe",
            "{game}/redist/directx_setup.exe",
            "{game}/docs/readme.txt",
            "{game}/docs/license.txt",
        ]
        
        for i in range(1, 7):  # Generate 6 manifest files
            depot_id = base_id + i
            manifest_id = random.getrandbits(64)
            
            # Create realistic manifest
            manifest_data = self.create_realistic_manifest(
                depot_id, manifest_id, file_patterns
            )
            
            filename = f"{depot_id}_{manifest_id}.manifest"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(manifest_data)
            
            manifests.append(filename)
            print(f"✓ Manifest: {filename} ({len(manifest_data)} bytes)")
        
        return manifests
    
    def create_realistic_manifest(self, depot_id, manifest_id, file_patterns):
        """Create realistic manifest with file list"""
        data = bytearray()
        
        # Game name for file paths
        game_slug = re.sub(r'[^a-zA-Z0-9]', '', self.game_name)[:20].lower()
        if not game_slug:
            game_slug = f"game{depot_id}"
        
        # 1. Depot ID (field 1, varint)
        data.append(0x08)  # field 1, varint
        self.append_varint(data, depot_id)
        
        # 2. Manifest ID (field 2, varint)
        data.append(0x10)  # field 2, varint
        self.append_varint(data, manifest_id)
        
        # 3. Creation time (field 3, varint)
        data.append(0x18)  # field 3, varint
        self.append_varint(data, int(time.time()))
        
        # 4. File list (field 4, length-delimited)
        # First, create the file list data
        file_list_data = bytearray()
        
        # Add some files
        for i, pattern in enumerate(file_patterns[:8]):  # Add 8 files
            file_path = pattern.format(game=game_slug)
            
            # File entry: filename + size + hash
            file_entry = bytearray()
            
            # Filename (field 1, length-delimited)
            file_entry.append(0x0A)  # field 1
            self.append_length_delimited(file_entry, file_path.encode('utf-8'))
            
            # File size (field 2, varint) - realistic sizes
            file_size = random.randint(1024, 50 * 1024 * 1024)  # 1KB - 50MB
            file_entry.append(0x10)  # field 2
            self.append_varint(file_entry, file_size)
            
            # File hash (field 3, length-delimited) - SHA1 hash
            fake_hash = hashlib.sha1(os.urandom(20)).digest()
            file_entry.append(0x1A)  # field 3
            self.append_length_delimited(file_entry, fake_hash)
            
            # Add file entry to file list
            file_list_data.append(0x0A)  # Nested message
            self.append_length_delimited(file_list_data, file_entry)
        
        # Add file list to main data
        data.append(0x22)  # field 4, length-delimited
        self.append_length_delimited(data, file_list_data)
        
        # 5. Chunk list (field 5, length-delimited) - empty for now
        data.append(0x2A)  # field 5
        data.append(0x00)  # length 0
        
        # 6. Total size (field 6, varint)
        total_size = sum([random.randint(1024, 50 * 1024 * 1024) for _ in range(8)])
        data.append(0x30)  # field 6
        self.append_varint(data, total_size)
        
        # 7. Compressed flag (field 7, varint) - 0 = not compressed
        data.append(0x38)  # field 7
        data.append(0x00)
        
        return bytes(data)
    
    def append_varint(self, data, value):
        """Append varint"""
        while value > 0x7F:
            data.append((value & 0x7F) | 0x80)
            value >>= 7
        data.append(value)
    
    def append_length_delimited(self, data, content):
        """Append length-delimited field"""
        length = len(content)
        self.append_varint(data, length)
        data.extend(content)
    
    def generate_acf_file(self):
        """Generate ACF file"""
        safe_name = re.sub(r'[\\/*?:"<>|]', "", self.game_name)
        acf_path = self.output_dir / f"appmanifest_{self.appid}.acf"
        
        content = f'''"AppState"
{{
	"appid" "{self.appid}"
	"Universe" "1"
	"name" "{self.game_name}"
	"StateFlags" "4"
	"installdir" "{safe_name}"
	"LastUpdated" "{int(time.time())}"
	"UpdateResult" "0"
	"SizeOnDisk" "0"
	"buildid" "0"
	"LastOwned" "{int(time.time())}"
	"BytesToDownload" "0"
	"BytesDownloaded" "0"
	"AutoUpdateBehavior" "0"
	"AllowOtherDownloadsWhileRunning" "0"
	"ScheduledAutoUpdate" "0"
	"InstalledDepots"
	{{
		"{self.appid}" "{int(time.time())}"
	}}
}}'''
        
        with open(acf_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ ACF fájl: {acf_path.name}")
        return acf_path
    
    def copy_to_steam(self, lua_path, manifests, acf_path):
        """Copy files to Steam"""
        steam_path = self.find_steam_path()
        if not steam_path:
            print("⚠ Steam mappa nem található, másolás kihagyva")
            return
        
        try:
            # LUA to stplug-in
            stplugin = steam_path / "config" / "stplug-in"
            stplugin.mkdir(parents=True, exist_ok=True)
            shutil.copy2(lua_path, stplugin / lua_path.name)
            
            # Manifests to depotcache
            depotcache = steam_path / "config" / "depotcache"
            depotcache.mkdir(parents=True, exist_ok=True)
            for manifest in manifests:
                src = self.output_dir / manifest
                dst = depotcache / manifest
                shutil.copy2(src, dst)
            
            # ACF to steamapps
            steamapps = steam_path / "steamapps"
            steamapps.mkdir(parents=True, exist_ok=True)
            shutil.copy2(acf_path, steamapps / acf_path.name)
            
            print("✓ Fájlok másolva Steam mappákba")
            
        except Exception as e:
            print(f"⚠ Másolási hiba: {e}")
    
    def find_steam_path(self):
        """Find Steam path"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            return Path(path)
        except:
            return None

class UltimateFixedGUI:
    """GUI for the ultimate generator"""
    def __init__(self, root):
        self.root = root
        self.root.title("ULTIMATE STEAM GENERATOR")
        self.root.geometry("700x600")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        tk.Label(self.root, text="ULTIMATE STEAM MANIFEST GENERATOR", 
                font=("Arial", 16, "bold"), fg="blue").pack(pady=10)
        
        tk.Label(self.root, text="Generál valószerű manifest fájlokat fájllistával", 
                font=("Arial", 10)).pack()
        
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(input_frame, text="Steam AppID:", 
                font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.appid_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.appid_var, 
                font=("Arial", 11), width=20).grid(row=0, column=1, sticky="w", padx=10)
        
        # Quick buttons
        quick_frame = tk.Frame(self.root)
        quick_frame.pack(pady=10)
        
        tk.Label(quick_frame, text="Gyors választás:", 
                font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        games = [("Plague Inc", "246620"), ("CS2", "730"), 
                ("Dota 2", "570"), ("Portal 2", "620")]
        
        for name, appid in games:
            btn = tk.Button(quick_frame, text=name, width=10,
                          command=lambda a=appid: self.appid_var.set(a))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Generate button
        self.gen_btn = tk.Button(self.root, text="🚀 GENERÁLÁS INDÍTÁSA", 
                                font=("Arial", 12, "bold"), bg="green", fg="white",
                                command=self.start_generation, padx=20, pady=10)
        self.gen_btn.pack(pady=20)
        
        # Log area
        tk.Label(self.root, text="Folyamat:", 
                font=("Arial", 11)).pack(anchor="w", padx=20)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=15,
                                                 font=("Consolas", 9))
        self.log_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Status
        self.status_var = tk.StringVar(value="Kész")
        tk.Label(self.root, textvariable=self.status_var,
                font=("Arial", 9), fg="gray").pack(pady=5)
    
    def log(self, message):
        """Add to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Clear log"""
        self.log_text.delete(1.0, tk.END)
    
    def start_generation(self):
        """Start generation"""
        appid = self.appid_var.get().strip()
        if not appid or not appid.isdigit():
            messagebox.showerror("Hiba", "Érvénytelen AppID!")
            return
        
        self.gen_btn.config(state="disabled", text="⏳ GENERÁLÁS...")
        self.clear_log()
        self.status_var.set("Generálás folyamatban...")
        
        # Run in thread
        thread = threading.Thread(target=self.generate, args=(appid,), daemon=True)
        thread.start()
    
    def generate(self, appid):
        """Generate files"""
        try:
            self.log("=" * 50)
            self.log(f"ULTIMATE GENERÁLÁS INDUL")
            self.log(f"AppID: {appid}")
            self.log("=" * 50)
            
            generator = UltimateFixedGenerator(appid)
            success = generator.run()
            
            if success:
                self.log("\n✅ GENERÁLÁS SIKERES!")
                self.log("A manifest fájlok most valószerű fájllistát tartalmaznak!")
                self.log("Indítsd újra a Steam-et!")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Siker", 
                    f"Fájlok sikeresen generálva!\n\nAppID: {appid}\n\nA manifest fájlok most valószerűek!"
                ))
                self.status_var.set("Generálás sikeres!")
            else:
                self.status_var.set("Generálás sikertelen!")
                
        except Exception as e:
            self.log(f"\n❌ HIBA: {e}")
            self.root.after(0, lambda: messagebox.showerror("Hiba", str(e)))
            self.status_var.set("Hiba történt!")
        finally:
            self.root.after(0, lambda: self.gen_btn.config(
                state="normal", text="🚀 GENERÁLÁS INDÍTÁSA"
            ))

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # CLI mode
        appid = sys.argv[1]
        generator = UltimateFixedGenerator(appid)
        generator.run()
    else:
        # GUI mode
        root = tk.Tk()
        app = UltimateFixedGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()