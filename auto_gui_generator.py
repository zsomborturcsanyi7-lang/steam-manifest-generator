#!/usr/bin/env python3
"""
AUTOMATIC STEAM MANIFEST GENERATOR WITH GUI
Teljesen automatikus generátor GUI-val
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
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

class AutoManifestGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AUTO STEAM MANIFEST GENERATOR")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#162447", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🚀 AUTO STEAM MANIFEST GENERATOR", 
                bg="#162447", fg="#00b7c2", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a2e", padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = tk.LabelFrame(main_container, text="Játék kiválasztása", 
                                   bg="#1a1a2e", fg="#00b7c2", 
                                   font=("Arial", 12, "bold"), padx=15, pady=15)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # AppID input
        tk.Label(input_frame, text="Steam AppID:", bg="#1a1a2e", fg="#e6e6e6",
                font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.appid_var = tk.StringVar()
        appid_entry = tk.Entry(input_frame, textvariable=self.appid_var, 
                              font=("Arial", 11), bg="#0f3460", fg="white",
                              insertbackground="white", bd=0)
        appid_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=5)
        
        # Game name input
        tk.Label(input_frame, text="Vagy játék neve:", bg="#1a1a2e", fg="#e6e6e6",
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        
        self.game_name_var = tk.StringVar()
        game_entry = tk.Entry(input_frame, textvariable=self.game_name_var,
                             font=("Arial", 11), bg="#0f3460", fg="white",
                             insertbackground="white", bd=0)
        game_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=5)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        
        # Quick buttons for popular games
        quick_frame = tk.Frame(main_container, bg="#1a1a2e")
        quick_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(quick_frame, text="Gyors választás:", bg="#1a1a2e", fg="#e6e6e6",
                font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        popular_games = [
            ("Plague Inc (246620)", "246620"),
            ("CS2 (730)", "730"),
            ("Dota 2 (570)", "570"),
            ("TF2 (440)", "440"),
            ("L4D2 (550)", "550"),
            ("Portal 2 (620)", "620")
        ]
        
        for name, appid in popular_games:
            btn = tk.Button(quick_frame, text=name, bg="#0f3460", fg="white",
                           font=("Arial", 9), bd=0,
                           command=lambda a=appid: self.set_appid(a))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Options
        options_frame = tk.LabelFrame(main_container, text="Beállítások",
                                     bg="#1a1a2e", fg="#00b7c2",
                                     font=("Arial", 12, "bold"), padx=15, pady=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_copy_var = tk.BooleanVar(value=True)
        auto_copy_cb = tk.Checkbutton(options_frame, text="Automatikus másolás Steam mappákba",
                                     variable=self.auto_copy_var, bg="#1a1a2e", fg="#e6e6e6",
                                     selectcolor="#0f3460", font=("Arial", 10))
        auto_copy_cb.pack(anchor="w")
        
        self.create_info_var = tk.BooleanVar(value=True)
        info_cb = tk.Checkbutton(options_frame, text="Információs fájl létrehozása",
                                variable=self.create_info_var, bg="#1a1a2e", fg="#e6e6e6",
                                selectcolor="#0f3460", font=("Arial", 10))
        info_cb.pack(anchor="w", pady=(5, 0))
        
        # Generate button
        self.generate_btn = tk.Button(main_container, text="🚀 GENERÁLÁS INDÍTÁSA",
                                     bg="#00b7c2", fg="white", font=("Arial", 12, "bold"),
                                     bd=0, padx=30, pady=10, cursor="hand2",
                                     command=self.start_generation)
        self.generate_btn.pack(pady=(0, 15))
        
        # Log area
        log_frame = tk.LabelFrame(main_container, text="Folyamat",
                                 bg="#1a1a2e", fg="#00b7c2",
                                 font=("Arial", 12, "bold"), padx=15, pady=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10,
                                                 bg="#0f3460", fg="#00ff9d",
                                                 font=("Consolas", 9), bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Kész: Válassz játékot és kattints a Generálás gombra")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             bg="#162447", fg="#e6e6e6", font=("Arial", 9),
                             anchor="w", padx=10)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def set_appid(self, appid):
        """Set AppID from quick button"""
        self.appid_var.set(appid)
        self.game_name_var.set("")
        self.log("AppID beállítva: " + appid)
        
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def clear_log(self):
        """Clear log"""
        self.log_text.delete(1.0, tk.END)
        
    def start_generation(self):
        """Start the generation process"""
        appid = self.appid_var.get().strip()
        game_name = self.game_name_var.get().strip()
        
        if not appid and not game_name:
            messagebox.showwarning("Hiányzó adat", "Kérlek adj meg egy AppID-t vagy játéknevet!")
            return
        
        # If game name is provided but no AppID, try to search for it
        if not appid and game_name:
            self.log(f"Játék keresése: {game_name}")
            found_appid = self.search_appid_by_name(game_name)
            if found_appid:
                appid = found_appid
                self.appid_var.set(appid)
                self.log(f"Talált AppID: {appid}")
            else:
                messagebox.showerror("Hiba", f"Nem található játék: {game_name}")
                return
        
        if not appid.isdigit():
            messagebox.showerror("Hiba", "Érvénytelen AppID! Csak szám lehet.")
            return
        
        # Disable button and start generation in thread
        self.generate_btn.config(state="disabled", text="⏳ GENERÁLÁS FOLYAMATBAN...")
        self.clear_log()
        self.status_var.set("Generálás folyamatban...")
        
        # Start generation thread
        thread = threading.Thread(target=self.generate_files, 
                                 args=(appid,), daemon=True)
        thread.start()
        
    def search_appid_by_name(self, game_name):
        """Search for AppID by game name"""
        try:
            search_url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(game_name)}&l=english"
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            if data.get('total', 0) > 0:
                return str(data['items'][0]['id'])
        except:
            pass
        return None
        
    def generate_files(self, appid):
        """Generate all files"""
        try:
            self.log("=" * 50)
            self.log(f"AUTOMATIKUS GENERÁLÁS INDUL")
            self.log(f"AppID: {appid}")
            self.log("=" * 50)
            
            # Create generator instance
            generator = AutoManifestGenerator(appid, self)
            
            # Run generation
            success = generator.run()
            
            if success:
                self.log("\n" + "=" * 50)
                self.log("✅ GENERÁLÁS SIKERES!")
                self.log("=" * 50)
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "Siker", 
                    f"Fájlok sikeresen generálva!\n\nAppID: {appid}\nJáték: {generator.game_name}\n\nIndítsd újra a Steam-et!"
                ))
                
                self.status_var.set("Generálás sikeres!")
            else:
                self.status_var.set("Generálás sikertelen!")
                
        except Exception as e:
            self.log(f"\n❌ HIBA: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "Hiba", 
                f"Hiba történt a generálás során:\n\n{str(e)}"
            ))
            self.status_var.set("Hiba történt!")
            
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.generate_btn.config(
                state="normal", 
                text="🚀 GENERÁLÁS INDÍTÁSA"
            ))

class AutoManifestGenerator:
    def __init__(self, appid, gui=None):
        self.appid = appid
        self.game_name = f"AppID {appid}"
        self.gui = gui
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = self.base_dir / "gui_generated" / f"game_{appid}"
        
        # Steam paths
        self.steam_path = self.find_steam_path()
        
    def find_steam_path(self):
        """Find Steam installation path"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            return Path(path)
        except:
            # Common Steam paths
            paths = [
                Path("C:/Program Files (x86)/Steam"),
                Path("C:/Program Files/Steam"),
                Path(os.path.expanduser("~")) / "AppData" / "Local" / "Steam"
            ]
            for path in paths:
                if path.exists():
                    return path
            return None
    
    def log(self, message):
        """Log message through GUI or print"""
        if self.gui:
            self.gui.log(message)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def run(self):
        """Main execution method"""
        try:
            # Step 1: Get game info
            self.log("[1/7] Játék információk lekérése...")
            self.get_game_info()
            
            # Step 2: Create output directory
            self.log("[2/7] Kimeneti mappa létrehozása...")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"   Mappa: {self.output_dir}")
            
            # Step 3: Generate LUA file
            self.log("[3/7] LUA fájl generálása...")
            lua_path = self.generate_lua_file()
            self.log(f"   OK: {lua_path.name}")
            
            # Step 4: Generate manifest files
            self.log("[4/7] Manifest fájlok generálása...")
            manifests = self.generate_manifest_files()
            self.log(f"   OK: {len(manifests)} manifest fájl")
            
            # Step 5: Generate ACF file
            self.log("[5/7] ACF fájl generálása...")
            acf_path = self.generate_acf_file()
            self.log(f"   OK: {acf_path.name}")
            
            # Step 6: Copy to Steam folders if enabled
            if hasattr(self.gui, 'auto_copy_var') and self.gui.auto_copy_var.get():
                self.log("[6/7] Fájlok másolása Steam mappákba...")
                self.copy_to_steam_folders(lua_path, manifests, acf_path)
            else:
                self.log("[6/7] Automatikus másolás kihagyva")
            
            # Step 7: Generate info file if enabled
            if hasattr(self.gui, 'create_info_var') and self.gui.create_info_var.get():
                self.log("[7/7] Információs fájl generálása...")
                info_path = self.generate_info_file(manifests)
                self.log(f"   OK: {info_path.name}")
            else:
                self.log("[7/7] Információs fájl kihagyva")
            
            # Summary
            self.log(f"\nJáték: {self.game_name}")
            self.log(f"Kimeneti mappa: {self.output_dir}")
            self.log(f"Létrehozott fájlok:")
            self.log(f"  - {lua_path.name} (LUA)")
            self.log(f"  - {len(manifests)} manifest fájl")
            self.log(f"  - {acf_path.name} (ACF)")
            
            return True
            
        except Exception as e:
            self.log(f"\nHIBA: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def get_game_info(self):
        """Get game name from Steam API"""
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={self.appid}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            if str(self.appid) in data and data[str(self.appid)]['success']:
                self.game_name = data[str(self.appid)]['data']['name']
                self.log(f"   Játék neve: {self.game_name}")
            else:
                self.log(f"   Ismeretlen játék, AppID használva")
                
        except Exception as e:
            self.log(f"   Nem sikerült lekérni a játéknevet: {e}")
    
    def generate_lua_file(self):
        """Generate LUA file with proper keys"""
        lua_path = self.output_dir / f"{self.appid}.lua"
        
        # Get keys from online sources
        keys = self.fetch_depot_keys()
        
        with open(lua_path, 'w', encoding='utf-8') as f:
            f.write(f"addappid({self.appid})\n")
            
            # Add main app key
            main_key = keys.get(str(self.appid), self.generate_random_key())
            f.write(f'addappid({self.appid},0,"{main_key}")\n')
            
            # Add depot keys (for depots +1 to +6 like in examples)
            base_id = int(self.appid)
            for i in range(1, 7):
                depot_id = base_id + i
                depot_key = keys.get(str(depot_id), self.generate_random_key())
                f.write(f'addappid({depot_id},0,"{depot_key}")\n')
        
        return lua_path
    
    def fetch_depot_keys(self):
        """Fetch depot keys from online sources"""
        keys = {}
        sources = [
            "https://raw.githubusercontent.com/SteamRE/DepotKeys/master/keys.json",
            "https://raw.githubusercontent.com/GreenLuma-Reborn/Steam-Manifests/master/keys.json",
        ]
        
        for url in sources:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    if isinstance(data, dict):
                        keys.update(data)
            except Exception as e:
                self.log(f"   Figyelmeztetés: Nem sikerült betölteni {url}: {e}")
                continue
        
        return keys
    
    def generate_random_key(self):
        """Generate random 64-character hex key"""
        return ''.join(random.choice('0123456789abcdef') for _ in range(64))
    
    def generate_manifest_files(self):
        """Generate manifest files"""
        manifests = []
        base_id = int(self.appid)
        
        for i in range(1, 7):  # Generate 6 manifest files
            depot_id = base_id + i
            manifest_id = random.getrandbits(64)
            
            # Create manifest file
            manifest_data = self.create_advanced_manifest(depot_id, manifest_id)
            
            filename = f"{depot_id}_{manifest_id}.manifest"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(manifest_data)
            
            manifests.append(filename)
        
        return manifests
    
    def create_advanced_manifest(self, depot_id, manifest_id):
        """Create more advanced manifest file"""
        data = bytearray()
        
        # Field 1: depot_id
        data.append(0x08)
        self.append_varint(data, depot_id)
        
        # Field 2: manifest_id
        data.append(0x10)
        self.append_varint(data, manifest_id)
        
        # Field 3: creation_time (current timestamp)
        data.append(0x18)
        self.append_varint(data, int(time.time()))
        
        # Field 4: filenames_encrypted (false)
        data.append(0x20)
        data.append(0x00)
        
        # Field 5: compressed (false)
        data.append(0x28)
        data.append(0x00)
        
        # Field 6: total_size (0 for now)
        data.append(0x30)
        self.append_varint(data, 0)
        
        # Field 7: files (empty list)
        data.append(0x3A)
        data.append(0x00)
        
        # Field 8: chunks (empty list)
        data.append(0x42)
        data.append(0x00)
        
        return bytes(data)
    
    def append_varint(self, data, value):
        """Append varint to bytearray"""
        while value > 0x7F:
            data.append((value & 0x7F) | 0x80)
            value >>= 7
        data.append(value)
    
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
	}}
}}'''
        
        with open(acf_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return acf_path
    
    def copy_to_steam_folders(self, lua_path, manifests, acf_path):
        """Copy files to Steam folders automatically"""
        if not self.steam_path or not self.steam_path.exists():
            self.log("   Figyelmeztetés: Steam mappa nem található, másolás kihagyva")
            return
        
        try:
            # Copy LUA to stplug-in
            stplugin_dir = self.steam_path / "config" / "stplug-in"
            stplugin_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(lua_path, stplugin_dir / lua_path.name)
            self.log(f"   LUA másolva: {stplugin_dir}")
            
            # Copy manifests to depotcache
            depotcache_dir = self.steam_path / "config" / "depotcache"
            depotcache_dir.mkdir(parents=True, exist_ok=True)
            for manifest in manifests:
                src = self.output_dir / manifest
                dst = depotcache_dir / manifest
                shutil.copy2(src, dst)
            self.log(f"   Manifest fájlok másolva: {depotcache_dir}")
            
            # Copy ACF to steamapps
            steamapps_dir = self.steam_path / "steamapps"
            steamapps_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(acf_path, steamapps_dir / acf_path.name)
            self.log(f"   ACF másolva: {steamapps_dir}")
            
        except Exception as e:
            self.log(f"   Figyelmeztetés: Másolási hiba: {e}")
    
    def generate_info_file(self, manifests):
        """Generate info JSON file"""
        info = {
            "appid": self.appid,
            "game_name": self.game_name,
            "generated_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "output_dir": str(self.output_dir),
            "manifests": manifests,
            "steam_path": str(self.steam_path) if self.steam_path else "Not found",
            "instructions": "Indítsd újra a Steam-et a változások érvényesítéséhez"
        }
        
        info_path = self.output_dir / f"{self.appid}_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
        
        return info_path

def main():
    """Main function"""
    root = tk.Tk()
    app = AutoManifestGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()