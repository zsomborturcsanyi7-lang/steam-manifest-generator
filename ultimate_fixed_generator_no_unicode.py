#!/usr/bin/env python3
"""
ULTIMATE FIXED STEAM MANIFEST GENERATOR - NO UNICODE
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
            print("GENERALAS SIKERES!")
            print("=" * 60)
            print(f"Jatek: {self.game_name}")
            print(f"Manifest fajlok: {len(manifests)} db")
            print(f"Fajlok tartalmaznak valoszeru adatokat!")
            print("\nInditsd ujra a Steam-et!")
            
            return True
            
        except Exception as e:
            print(f"\nHIBA: {e}")
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
                print(f"Jatek: {self.game_name}")
        except:
            print(f"Jatek: Ismeretlen (AppID: {self.appid})")
    
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
        
        print(f"OK: LUA fajl: {lua_path.name}")
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
            print(f"OK: Manifest: {filename} ({len(manifest_data)} bytes)")
        
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
        
        print(f"OK: ACF fajl: {acf_path.name}")
        return acf_path
    
    def copy_to_steam(self, lua_path, manifests, acf_path):
        """Copy files to Steam"""
        steam_path = self.find_steam_path()
        if not steam_path:
            print("FIGYELMEZTETES: Steam mappa nem talalhato, masolas kihagyva")
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
            
            print("OK: Fajlok masolva Steam mappakba")
            
        except Exception as e:
            print(f"FIGYELMEZTETES: Masolasi hiba: {e}")
    
    def find_steam_path(self):
        """Find Steam path"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            return Path(path)
        except:
            return None

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # CLI mode
        appid = sys.argv[1]
        generator = UltimateFixedGenerator(appid)
        success = generator.run()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("Hasznalat: python ultimate_fixed_generator_no_unicode.py <AppID>")
        print("Pelda: python ultimate_fixed_generator_no_unicode.py 246620")

if __name__ == "__main__":
    main()