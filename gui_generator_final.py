import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.parse
import threading
import re
import time
import shutil

class SteamManifestGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("STEAM MANIFEST GENERATOR - FINAL")
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
        
        tk.Label(header_frame, text="STEAM MANIFEST GENERATOR", bg="#1c1f2b", fg="#00a8ff", font=self.header_font).pack()
        tk.Label(header_frame, text="LUA + Manifest fájlok generálása", bg="#1c1f2b", fg="#7f8c8d", font=("Segoe UI", 9)).pack()

        container = tk.Frame(self.root, bg="#0f111a", padx=40, pady=30)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Steam AppID:", bg="#0f111a", fg="#ecf0f1", font=self.main_font).pack(anchor="w")
        
        self.appid_entry = tk.Entry(container, font=("Segoe UI", 14), bg="#1c1f2b", fg="white", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#34495e")
        self.appid_entry.pack(fill=tk.X, pady=(10, 25), ipady=10)
        self.appid_entry.insert(0, "246620")

        tk.Label(container, text="Forrás mappa (manifest fájlok):", bg="#0f111a", fg="#ecf0f1", font=self.main_font).pack(anchor="w", pady=(20, 5))
        
        self.source_frame = tk.Frame(container, bg="#0f111a")
        self.source_frame.pack(fill=tk.X, pady=5)
        
        self.source_dir = tk.StringVar()
        tk.Entry(self.source_frame, textvariable=self.source_dir, bg="#1c1f2b", fg="white", bd=0, font=("Segoe UI", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        ttk.Button(self.source_frame, text="Tallózás", width=12, command=self.browse_source).pack(side=tk.LEFT, padx=5)
        
        # Alapértelmezett forrás a főmappa
        default_source = r"C:\Users\iga\Downloads\Plague_Inc__Evolved_T9"
        if os.path.exists(default_source):
            self.source_dir.set(default_source)

        btn_frame = tk.Frame(container, bg="#0f111a")
        btn_frame.pack(fill=tk.X, pady=20)

        self.gen_btn = ttk.Button(btn_frame, text="FÁJLOK GENERÁLÁSA", command=self.start_process)
        self.gen_btn.pack(fill=tk.X, ipady=15)

        tk.Label(container, text="Folyamat állapota:", bg="#0f111a", fg="#bdc3c7", font=self.main_font).pack(anchor="w", pady=(30, 5))
        
        self.log_area = tk.Text(container, bg="#12141d", fg="#27ae60", font=self.log_font, bd=0, padx=15, pady=15, state="disabled", highlightthickness=1, highlightbackground="#2c3e50")
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[#] {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def browse_source(self):
        path = filedialog.askdirectory()
        if path: self.source_dir.set(path)

    def start_process(self):
        appid = self.appid_entry.get().strip()
        source_dir = self.source_dir.get().strip()
        
        if not appid:
            messagebox.showwarning("Figyelem", "Kérlek adj meg egy AppID-t!")
            return
        
        if not source_dir or not os.path.exists(source_dir):
            messagebox.showwarning("Figyelem", "Kérlek válassz forrás mappát!")
            return
        
        self.gen_btn.config(state="disabled")
        self.log_area.config(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state="disabled")
        
        threading.Thread(target=self.generate_files, args=(appid, source_dir), daemon=True).start()

    def generate_files(self, appid, source_dir):
        self.log(f"Generálás indítása AppID: {appid}")
        self.log(f"Forrás mappa: {source_dir}")
        
        # Célmappa
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, f"Generated_{appid}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 1. LUA fájl generálása (főmappa formátum)
        self.log("LUA fájl generálása...")
        lua_content = self.generate_lua_file(appid)
        lua_path = os.path.join(output_dir, f"{appid}.lua")
        
        with open(lua_path, "w", encoding="utf-8") as f:
            f.write(lua_content)
        
        self.log(f"LUA fájl létrehozva: {lua_path}")
        
        # 2. Manifest fájlok másolása a forrásmappából
        self.log("Manifest fájlok keresése...")
        manifest_files = []
        
        for file in os.listdir(source_dir):
            if file.endswith(".manifest"):
                src_file = os.path.join(source_dir, file)
                dst_file = os.path.join(output_dir, file)
                
                try:
                    shutil.copy2(src_file, dst_file)
                    manifest_files.append(file)
                    self.log(f"  - Másolva: {file}")
                except Exception as e:
                    self.log(f"  - HIBA {file}: {str(e)}")
        
        if manifest_files:
            self.log(f"Összesen {len(manifest_files)} manifest fájl másolva.")
        else:
            self.log("FIGYELEM: Nem található manifest fájl a forrásmappában!")
            self.log("Üres manifest fájlok létrehozása...")
            self.create_empty_manifests(appid, output_dir)
        
        # 3. JSON info fájl
        info = {
            "appid": appid,
            "generated_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_dir": source_dir,
            "output_dir": output_dir,
            "lua_file": f"{appid}.lua",
            "manifest_files": manifest_files
        }
        
        info_path = os.path.join(output_dir, f"{appid}_info.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4)
        
        self.log(f"\n✓ GENERÁLÁS KÉSZ!")
        self.log(f"   Célmappa: {output_dir}")
        self.log(f"   LUA fájl: {appid}.lua")
        self.log(f"   Manifest fájlok: {len(manifest_files)} db")
        
        self.root.after(0, lambda: self.gen_btn.config(state="normal"))
        self.root.after(0, lambda: messagebox.showinfo("Kész", f"Fájlok generálva: {output_dir}"))

    def generate_lua_file(self, appid):
        """LUA fájl generálása a főmappa formátumának megfelelően"""
        # Alap LUA tartalom - ezt testreszabhatod
        lua_content = f"""addappid({appid})
addappid({appid},0,"{"0"*64}")  # Placeholder kulcs
"""
        
        # További AppID-k hozzáadása a példa alapján
        base_id = int(appid)
        for i in range(1, 7):
            dep_id = base_id + i
            placeholder_key = "".join(["0" for _ in range(64)])  # 64 hex karakter
            lua_content += f'addappid({dep_id},0,"{placeholder_key}")\n'
        
        return lua_content

    def create_empty_manifests(self, appid, output_dir):
        """Üres manifest fájlok létrehozása"""
        base_id = int(appid)
        
        for i in range(1, 7):
            dep_id = base_id + i
            manifest_id = hash(f"{dep_id}_{time.time()}") % (10**19)
            manifest_filename = f"{dep_id}_{manifest_id}.manifest"
            manifest_path = os.path.join(output_dir, manifest_filename)
            
            # Üres bináris fájl (protobuf placeholder)
            with open(manifest_path, "wb") as f:
                # Egyszerű protobuf-like fejléc
                f.write(b'\x0A\x00')  # Protobuf field 1, length 0
                
            self.log(f"  - Üres manifest: {manifest_filename}")

if __name__ == "__main__":
    from tkinter import filedialog
    root = tk.Tk()
    app = SteamManifestGenerator(root)
    root.mainloop()