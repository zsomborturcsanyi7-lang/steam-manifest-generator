import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.parse
import threading
import re
import time

class ManifestHubGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MANIFEST HUB - ADVANCED GENERATOR")
        self.root.geometry("750x650")
        self.root.configure(bg="#0f111a")

        self.main_font = ("Segoe UI", 10)
        self.header_font = ("Segoe UI", 20, "bold")
        self.log_font = ("Consolas", 9)

        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TButton", font=("Segoe UI", 11, "bold"), background="#00a8ff", foreground="white", borderwidth=0)
        style.map("TButton", background=[('active', '#0097e6')])
        
        style.configure("TEntry", fieldbackground="#1c1f2b", foreground="white", borderwidth=0)
        
        self.setup_ui()

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg="#1c1f2b", pady=20)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="MANIFEST HUB", bg="#1c1f2b", fg="#00a8ff", font=self.header_font).pack()
        tk.Label(header_frame, text="Universal Steam Tool - Generator & Downloader", bg="#1c1f2b", fg="#7f8c8d", font=("Segoe UI", 9)).pack()

        container = tk.Frame(self.root, bg="#0f111a", padx=40, pady=30)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Játék neve vagy Steam AppID:", bg="#0f111a", fg="#ecf0f1", font=self.main_font).pack(anchor="w")
        
        self.query_entry = tk.Entry(container, font=("Segoe UI", 14), bg="#1c1f2b", fg="white", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#34495e")
        self.query_entry.pack(fill=tk.X, pady=(10, 25), ipady=10)
        self.query_entry.insert(0, "Age of Empires IV")
        self.query_entry.bind("<FocusIn>", lambda e: self.query_entry.delete(0, tk.END) if self.query_entry.get() == "Age of Empires IV" else None)

        btn_frame = tk.Frame(container, bg="#0f111a")
        btn_frame.pack(fill=tk.X)

        self.gen_btn = ttk.Button(btn_frame, text="ADATOK KERESÉSE ÉS GENERÁLÁS", command=self.start_process)
        self.gen_btn.pack(fill=tk.X, ipady=15)

        tk.Label(container, text="Folyamat állapota:", bg="#0f111a", fg="#bdc3c7", font=self.main_font).pack(anchor="w", pady=(30, 5))
        
        self.log_area = tk.Text(container, bg="#12141d", fg="#27ae60", font=self.log_font, bd=0, padx=15, pady=15, state="disabled", highlightthickness=1, highlightbackground="#2c3e50")
        self.log_area.pack(fill=tk.BOTH, expand=True)

        footer = tk.Label(self.root, text="v3.5 - ManifestHub Format Compatible", bg="#0f111a", fg="#7f8c8d", font=("Segoe UI", 8), pady=10)
        footer.pack(side=tk.BOTTOM)

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[#] {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def fetch_json(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except:
            return None

    def start_process(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Figyelem", "Kérlek adj meg egy nevet vagy AppID-t!")
            return
        
        self.gen_btn.config(state="disabled")
        self.log_area.config(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state="disabled")
        
        threading.Thread(target=self.worker, args=(query,), daemon=True).start()

    def search_appid_by_name(self, name):
        try:
            search_url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(name)}&l=hungarian&cc=HU"
            data = self.fetch_json(search_url)
            if data and data.get('total') > 0:
                best_match = data['items'][0]
                return str(best_match['id']), best_match['name']
        except:
            pass
        return None, None

    def worker(self, query):
        appid = query
        game_name = "Unknown Game"

        if not query.isdigit():
            self.log(f"Keresés név alapján: '{query}'...")
            found_id, found_name = self.search_appid_by_name(query)
            if found_id:
                appid = found_id
                game_name = found_name
                self.log(f"Találat: {game_name} (AppID: {appid})")
            else:
                self.log("HIBA: Nem található ilyen nevű játék!")
                self.root.after(0, lambda: self.gen_btn.config(state="normal"))
                return

        self.log(f"Adatok lekérése a Steam-ről (ID: {appid})...")
        store_data = self.fetch_json(f"https://store.steampowered.com/api/appdetails?appids={appid}")
        dlc_list = []
        if store_data and str(appid) in store_data and store_data[str(appid)]['success']:
            game_data = store_data[str(appid)]['data']
            game_name = game_data['name']
            dlc_list = game_data.get('dlc', [])
            self.log(f"Megerősítve: {game_name}")
            self.log(f"DLC-k száma: {len(dlc_list)}")

        self.log("Online adatbázisok átvizsgálása (Depot Keys)...")
        sources = [
            "https://raw.githubusercontent.com/SteamRE/Steam86/master/depot_keys.json",
            "https://raw.githubusercontent.com/SteamRE/DepotKeys/master/depot_keys.json",
            "https://raw.githubusercontent.com/K3rnelPan1c5750/Steam-Depot-Keys/main/keys.json",
            "https://api.manifesthub.dev/api/v1/keys",
            "https://raw.githubusercontent.com/GreenLuma-Reborn/Steam-Manifests/master/keys.json"
        ]
        
        all_found_keys = {}
        for i, url in enumerate(sources, 1):
            data = self.fetch_json(url)
            if data:
                for k, v in data.items():
                    if k not in all_found_keys: all_found_keys[k] = v
                self.log(f"Forrás #{i} betöltve.")

        json_output = {
            "appid": int(appid),
            "name": game_name,
            "type": "Game",
            "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "depot": {}
        }

        depot_ids = set([int(appid), int(appid)+1, int(appid)+2] + [int(d) for d in dlc_list])
        for dep_id in depot_ids:
            dep_str = str(dep_id)
            key = all_found_keys.get(dep_str, "")
            if key: self.log(f"KULCS MEGVAN: Depot {dep_str}")
            
            gid = str(abs(hash(str(dep_id) + "manifest_v3")) % 10**19)
            json_output["depot"][dep_str] = {
                "config": {"oslist": "windows", "language": ""},
                "manifests": {"public": {"gid": gid, "size": "0", "download": "0"}},
                "decryptionkey": key
            }
            if dep_id in dlc_list: json_output["depot"][dep_str]["dlcappid"] = dep_str

        self.write_files(appid, game_name, json_output)

    def write_files(self, appid, game_name, json_output):
        safe_name = re.sub(r'[\\/*?:"<>|]', "", game_name)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, f"{safe_name} ({appid})")
        
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        # JSON
        with open(os.path.join(output_dir, f"{appid}.json"), "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=4)
        
        # LUA
        with open(os.path.join(output_dir, f"{appid}.lua"), "w", encoding="utf-8") as f:
            f.write(f"addappid({appid})\n")
            for d_id, data in json_output["depot"].items():
                key = data.get("decryptionkey", "")
                gid = data["manifests"]["public"]["gid"]
                line = f'addappid({d_id},0,"{key}")\n' if key else f'addappid({d_id})\n'
                f.write(line)
                f.write(f'setManifestid({d_id},"{gid}")\n')

        # VDF
        with open(os.path.join(output_dir, "key.vdf"), "w", encoding="utf-8") as f:
            f.write('"depots"\n{\n')
            for d_id, data in json_output["depot"].items():
                if data.get("decryptionkey"):
                    f.write(f'    "{d_id}"\n    {{\n        "DecryptionKey" "{data["decryptionkey"]}"\n    }}\n')
            f.write('}\n')

        # .manifests - JAVÍTOTT RÉSZ
        for d_id, data in json_output["depot"].items():
            gid = data["manifests"]["public"]["gid"]
            manifest_data = {
                "depot_id": int(d_id),
                "gid": gid,
                "creation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "size": 0,
                "chunks": []
            }
            with open(os.path.join(output_dir, f"{d_id}_{gid}.manifest"), "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)

        # .acf
        with open(os.path.join(output_dir, f"appmanifest_{appid}.acf"), "w", encoding="utf-8") as f:
            f.write('"AppState"\n{\n')
            f.write(f'    "appid" "{appid}"\n')
            f.write(f'    "name" "{game_name}"\n')
            f.write('    "StateFlags" "4"\n')
            f.write(f'    "installdir" "{safe_name}"\n')
            f.write('}\n')

        self.log(f"KÉSZ! Fájlok elmentve: {output_dir}")
        self.root.after(0, lambda: self.gen_btn.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ManifestHubGeneratorGUI(root)
    root.mainloop()