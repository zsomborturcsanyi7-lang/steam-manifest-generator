import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import winreg
import threading
import urllib.request
import json
import re
import subprocess
import time

class SteamGodModeInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("STEAM TOOLKIT PRO - GOD MODE")
        self.root.geometry("900x700")
        self.root.configure(bg="#0f111a")

        self.steam_path = self.find_steam_path()
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#1c1f2b", foreground="white", fieldbackground="#1c1f2b", borderwidth=0, font=("Segoe UI", 9))
        style.map("Treeview", background=[('selected', '#3498db')])
        style.configure("TNotebook", background="#1c1f2b", borderwidth=0)
        style.configure("TNotebook.Tab", background="#2d3436", foreground="white", padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", "#00a8ff")])
        style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#00a8ff", foreground="white")
        style.map("TButton", background=[('active', '#0097e6')])

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: INSTALLER
        self.install_tab = tk.Frame(self.notebook, bg="#0f111a")
        self.notebook.add(self.install_tab, text="📥 TELEPÍTŐ")
        self.setup_install_tab()

        # Tab 2: LIBRARY MANAGER
        self.library_tab = tk.Frame(self.notebook, bg="#0f111a")
        self.notebook.add(self.library_tab, text="📚 KÖNYVTÁR KEZELŐ")
        self.setup_library_tab()

    def setup_install_tab(self):
        main = tk.Frame(self.install_tab, bg="#0f111a", padx=30, pady=30)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="MANIFEST HUB TELEPÍTŐ", bg="#0f111a", fg="#00a8ff", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        tk.Label(main, text="Forrás mappa kiválasztása:", bg="#0f111a", fg="#bdc3c7").pack(anchor="w")
        src_frame = tk.Frame(main, bg="#0f111a")
        src_frame.pack(fill=tk.X, pady=10)
        self.source_dir = tk.StringVar()
        tk.Entry(src_frame, textvariable=self.source_dir, bg="#1c1f2b", fg="white", bd=0, font=("Segoe UI", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        ttk.Button(src_frame, text="Tallózás", width=12, command=self.browse_source).pack(side=tk.LEFT, padx=5)

        ttk.Button(main, text="ADATOK INJEKTÁLÁSA A STEAM-BE", command=self.install_process).pack(fill=tk.X, pady=20, ipady=15)

        self.log_area = tk.Text(main, height=12, bg="#12141d", fg="#2ecc71", font=("Consolas", 10), bd=0, padx=15, pady=15)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def setup_library_tab(self):
        main = tk.Frame(self.library_tab, bg="#0f111a", padx=30, pady=30)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="FIXEK ÉS JÁTÉKOK ÁLLAPOTA", bg="#0f111a", fg="#00a8ff", font=("Segoe UI", 20, "bold")).pack(pady=(0, 10))
        tk.Label(main, text="Itt kezelheted a láthatóságot és frissítheted a hiányzó kulcsokat.", bg="#0f111a", fg="#7f8c8d").pack(pady=(0, 20))

        # Game List with columns
        cols = ('ID', 'Név', 'Állapot', 'Kulcs Szükséges')
        self.game_tree = ttk.Treeview(main, columns=cols, show='headings', height=12)
        for col in cols: self.game_tree.heading(col, text=col)
        self.game_tree.column('ID', width=100, anchor="center")
        self.game_tree.column('Név', width=350)
        self.game_tree.column('Állapot', width=150, anchor="center")
        self.game_tree.column('Kulcs Szükséges', width=150, anchor="center")
        self.game_tree.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        btn_frame = tk.Frame(main, bg="#0f111a", pady=20)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="🔄 LISTA FRISSÍTÉSE", command=self.refresh_library).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="👁️ ELREJT / MEGJELENÍT", command=self.toggle_game_visibility).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔑 KULCS KERESÉS (10+ FORRÁS)", command=self.repair_keys).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧹 STEAM CACHE TISZTÍTÁS", command=self.clear_steam_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🚀 STEAM ÚJRAINDÍTÁSA", command=self.restart_steam).pack(side=tk.LEFT, padx=5)

        self.refresh_library()

    def restart_steam(self):
        if not self.steam_path: return
        steam_exe = os.path.join(self.steam_path, "steam.exe")
        if not os.path.exists(steam_exe):
            messagebox.showerror("Hiba", "Nem található a steam.exe!")
            return

        self.log("Steam leállítása...")
        try:
            # Kill steam.exe
            subprocess.run(["taskkill", "/F", "/IM", "steam.exe"], capture_output=True)
            time.sleep(2)
            
            self.log("Steam újraindítása...")
            subprocess.Popen([steam_exe])
            self.log("Steam elindítva.")
        except Exception as e:
            messagebox.showerror("Hiba", f"Nem sikerült az újraindítás: {str(e)}")

    def find_steam_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            return os.path.abspath(path)
        except: return None

    def log(self, msg):
        self.log_area.insert(tk.END, f"[#] {msg}\n")
        self.log_area.see(tk.END)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path: self.source_dir.set(path)

    def is_f2p(self, appid):
        # Ingyenes vagy publikus AppID-k listája (példák)
        f2p_ids = ["730", "570", "440", "480", "1046930"] # CS2, Dota2, TF2, Spacewar, Dota Underlords...
        return str(appid) in f2p_ids

    def refresh_library(self):
        for i in self.game_tree.get_children(): self.game_tree.delete(i)
        if not self.steam_path: return

        steamapps = os.path.join(self.steam_path, "steamapps")
        if not os.path.exists(steamapps): return

        vdf_path = os.path.join(self.steam_path, "config", "key.vdf")
        vdf_content = ""
        if os.path.exists(vdf_path):
            with open(vdf_path, "r") as f: vdf_content = f.read()

        for file in sorted(os.listdir(steamapps)):
            if file.startswith("appmanifest_") and (file.endswith(".acf") or file.endswith(".acf.disabled")):
                appid = file.split("_")[1].split(".")[0]
                status = "🟢 LÁTHATÓ" if file.endswith(".acf") else "🔴 REJTETT"
                
                # Kulcs szükségesség ellenőrzése
                if self.is_f2p(appid):
                    key_status = "NEM KELL (F2P)"
                elif appid in vdf_content:
                    key_status = "VAN KULCS"
                else:
                    key_status = "HIÁNYZIK / PUB"

                # Get name from ACF
                name = "Ismeretlen"
                try:
                    with open(os.path.join(steamapps, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        match = re.search(r'"name"\s+"(.*?)"', content)
                        if match: name = match.group(1)
                except: pass

                self.game_tree.insert('', tk.END, values=(appid, name, status, key_status))

    def toggle_game_visibility(self):
        selected = self.game_tree.selection()
        if not selected: return
        
        appid, name, status, _ = self.game_tree.item(selected[0])['values']
        steamapps = os.path.join(self.steam_path, "steamapps")
        
        # A statuszban benne vannak az emoji-k, le kell vágnunk
        clean_status = "LÁTHATÓ" if "LÁTHATÓ" in status else "REJTETT"
        
        old_name = f"appmanifest_{appid}.acf" if clean_status == "LÁTHATÓ" else f"appmanifest_{appid}.acf.disabled"
        new_name = f"appmanifest_{appid}.acf.disabled" if clean_status == "LÁTHATÓ" else f"appmanifest_{appid}.acf"
        
        try:
            os.rename(os.path.join(steamapps, old_name), os.path.join(steamapps, new_name))
            self.refresh_library()
            messagebox.showinfo("Siker", f"A(z) {name} állapota mostantól: {('REJTETT' if clean_status == 'LÁTHATÓ' else 'LÁTHATÓ')}")
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def clear_steam_cache(self):
        if not self.steam_path: return
        depotcache = os.path.join(self.steam_path, "config", "depotcache")
        if os.path.exists(depotcache):
            try:
                for f in os.listdir(depotcache):
                    os.remove(os.path.join(depotcache, f))
                messagebox.showinfo("Siker", "Steam Manifest Cache sikeresen ürítve! Indítsd újra a Steamet.")
            except Exception as e:
                messagebox.showerror("Hiba", f"Nem sikerült minden fájlt törölni: {str(e)}")

    def repair_keys(self):
        selected = self.game_tree.selection()
        if not selected: return
        appid = str(self.game_tree.item(selected[0])['values'][0])
        self.log(f"Mélyreható keresés indítása: {appid}")
        threading.Thread(target=self.key_search_worker, args=(appid,), daemon=True).start()

    def fetch_json(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except: return None

    def key_search_worker(self, appid):
        self.log(f"Mélyreható keresés indítása (AppID: {appid})...")
        
        # 1. Adatgyűjtés a Steam-ről (DLC-k lekérése, mint a generátorban)
        self.log("Játék adatainak lekérése a Steam Store-ból...")
        store_data = self.fetch_json(f"https://store.steampowered.com/api/appdetails?appids={appid}")
        
        target_ids = {appid, str(int(appid)+1), str(int(appid)+2)}
        if store_data and str(appid) in store_data and store_data[str(appid)]['success']:
            dlcs = store_data[str(appid)]['data'].get('dlc', [])
            for d in dlcs:
                target_ids.add(str(d))
                target_ids.add(str(int(d)+1))
            self.log(f"Talált DLC-k: {len(dlcs)} db.")

        # 2. Helyi manifestek beolvasása
        steamapps = os.path.join(self.steam_path, "steamapps")
        if os.path.exists(steamapps):
            for f in os.listdir(steamapps):
                if f.startswith(f"{appid}_") and f.endswith(".manifest"):
                    target_ids.add(f.split("_")[0])

        self.log(f"Keresés összesen {len(target_ids)} azonosítóra...")

        # 10+ Forrás
        sources = [
            "https://raw.githubusercontent.com/SteamRE/Steam86/master/depot_keys.json",
            "https://raw.githubusercontent.com/SteamRE/DepotKeys/master/depot_keys.json",
            "https://raw.githubusercontent.com/K3rnelPan1c5750/Steam-Depot-Keys/main/keys.json",
            "https://raw.githubusercontent.com/GreenLuma-Reborn/Steam-Manifests/master/keys.json",
            "https://raw.githubusercontent.com/Jack-Myth/AnySteamKeys/master/keys.json",
            "https://raw.githubusercontent.com/Pointer9x/DepotKeys/master/keys.json",
            "https://raw.githubusercontent.com/SteamData/DepotKeys/master/keys.json",
            "https://raw.githubusercontent.com/C4S3-1/Steam-Depot-Keys/master/keys.json",
            "https://api.manifesthub.dev/api/v1/keys",
            "https://raw.githubusercontent.com/Pleasuredome/DepotKeys/master/depot_keys.json"
        ]
        
        found_keys = {}
        for i, url in enumerate(sources, 1):
            try:
                self.log(f"Forrás #{i} ellenőrzése...")
                data = self.fetch_json(url)
                if data:
                    for tid in target_ids:
                        if tid in data and tid not in found_keys:
                            found_keys[tid] = data[tid]
                            self.log(f"KULCS MEGVAN: {tid}")
            except: pass

        if found_keys:
            for tid, key in found_keys.items():
                self.update_key_vdf(tid, key)
            self.root.after(0, self.refresh_library)
            messagebox.showinfo("Siker", f"Sikeresen találtunk {len(found_keys)} kulcsot és injektáltuk őket!")
        else:
            self.log("HIBA: Egyik forrásban sem találtunk kulcsot. Próbáld meg később.")

    def update_key_vdf(self, appid, key):
        vdf_path = os.path.join(self.steam_path, "config", "key.vdf")
        content = ""
        if os.path.exists(vdf_path):
            with open(vdf_path, "r") as f: content = f.read()
        
        if appid in content: return
        
        if '"depots"' in content:
            new_entry = f'\n    "{appid}"\n    {{\n        "DecryptionKey" "{key}"\n    }}'
            content = content.replace('"depots"\n{', '"depots"\n{' + new_entry)
        else:
            content = f'"depots"\n{{\n    "{appid}"\n    {{\n        "DecryptionKey" "{key}"\n    }}\n}}'
        
        with open(vdf_path, "w") as f: f.write(content)

    def install_process(self):
        src = self.source_dir.get()
        if not src or not self.steam_path: return
        
        config_path = os.path.join(self.steam_path, "config")
        depotcache = os.path.join(config_path, "depotcache")
        stplugin = os.path.join(config_path, "stplug-in")
        steamapps = os.path.join(self.steam_path, "steamapps")
        
        # Célmappák létrehozása ha nem léteznek
        for path in [depotcache, stplugin, steamapps]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

        self.log("Telepítés folyamatban...")
        try:
            for item in os.listdir(src):
                src_file = os.path.join(src, item)
                if os.path.isdir(src_file):
                    # Ha mappát választottunk ki ami alkönyvtárakat tartalmaz (pl. a játék neve)
                    for sub_item in os.listdir(src_file):
                        sub_src = os.path.join(src_file, sub_item)
                        if sub_item.endswith(".manifest"):
                            shutil.copy2(sub_src, os.path.join(depotcache, sub_item))
                        elif sub_item.endswith(".lua"):
                            shutil.copy2(sub_src, os.path.join(stplugin, sub_item))
                        elif sub_item.startswith("appmanifest_") and sub_item.endswith(".acf"):
                            shutil.copy2(sub_src, os.path.join(steamapps, sub_item))
                
                # Gyökérben lévő fájlok kezelése
                if item.endswith(".manifest"):
                    shutil.copy2(src_file, os.path.join(depotcache, item))
                elif item.endswith(".lua"):
                    shutil.copy2(src_file, os.path.join(stplugin, item))
                elif item.startswith("appmanifest_") and item.endswith(".acf"):
                    shutil.copy2(src_file, os.path.join(steamapps, item))
                elif item == "key.vdf":
                    dst_key = os.path.join(config_path, "key.vdf")
                    if not os.path.exists(dst_key):
                        shutil.copy2(src_file, dst_key)
            
            self.log("SIKERTÖRTÉNET: Adatok injektálva a Steam rendszermisszióba!")
            self.refresh_library()
            messagebox.showinfo("Siker", "A telepítés befejeződött. Kérlek indítsd újra a Steamet!")
        except Exception as e:
            self.log(f"HIBA: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteamGodModeInstaller(root)
    root.mainloop()
