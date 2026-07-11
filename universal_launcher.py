import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess

class UniversalLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Online Fix Launcher")
        self.root.geometry("600x550")
        self.root.configure(bg="#1a1a1a")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Arial", 10, "bold"), background="#3498db", foreground="white")
        style.map("TButton", background=[('active', '#2980b9')])

        main_frame = tk.Frame(root, bg="#1a1a1a", padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="GAME CONNECTOR & FIXER", bg="#1a1a1a", fg="#e74c3c", font=("Arial", 22, "bold")).pack(pady=(0, 20))

        # Játékos név
        tk.Label(main_frame, text="Játékos név (Steam Name):", bg="#1a1a1a", fg="white").pack(anchor="w")
        self.name_entry = tk.Entry(main_frame, font=("Arial", 12), bg="#2d3436", fg="white", insertbackground="white")
        self.name_entry.pack(fill=tk.X, pady=5)
        self.name_entry.insert(0, "Player")

        # AppID (Spacewar alapértelmezett)
        tk.Label(main_frame, text="Fix AppID (Spacewar = 480):", bg="#1a1a1a", fg="white").pack(anchor="w", pady=(10, 0))
        self.appid_entry = tk.Entry(main_frame, font=("Arial", 12), bg="#2d3436", fg="white", insertbackground="white")
        self.appid_entry.pack(fill=tk.X, pady=5)
        self.appid_entry.insert(0, "480")

        # EXE választó
        self.exe_path = tk.StringVar()
        tk.Label(main_frame, text="Játék indítófájl (.exe):", bg="#1a1a1a", fg="white").pack(anchor="w", pady=(10, 0))
        exe_frame = tk.Frame(main_frame, bg="#1a1a1a")
        exe_frame.pack(fill=tk.X, pady=5)
        tk.Entry(exe_frame, textvariable=self.exe_path, font=("Arial", 10), bg="#2d3436", fg="#b2bec3", state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(exe_frame, text="Tallózás", width=10, command=self.browse_exe).pack(side=tk.LEFT, padx=(5, 0))

        # Funkció gombok
        btn_frame = tk.Frame(main_frame, bg="#1a1a1a")
        btn_frame.pack(fill=tk.X, pady=30)

        self.patch_btn = ttk.Button(btn_frame, text="PATCH & INDÍTÁS", command=self.start_process)
        self.patch_btn.pack(fill=tk.X, ipady=10)

        # Log
        self.log_area = tk.Text(main_frame, height=8, bg="#000000", fg="#00ff00", font=("Consolas", 9), padx=10, pady=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=10)

    def log(self, msg):
        self.log_area.insert(tk.END, f"> {msg}\n")
        self.log_area.see(tk.END)

    def browse_exe(self):
        path = filedialog.askopenfilename(filetypes=[("Játék EXE", "*.exe")])
        if path: self.exe_path.set(path)

    def start_process(self):
        if not self.exe_path.get():
            messagebox.showerror("Hiba", "Válassz ki egy játék .exe fájlt!")
            return
        
        self.patch_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        game_exe = self.exe_path.get()
        game_dir = os.path.dirname(game_exe)
        player_name = self.name_entry.get().strip()
        appid = self.appid_entry.get().strip()
        spacewar_src = os.path.abspath("spacewar")

        self.log("Folyamat indítása...")
        
        try:
            # 1. Spacewar fájlok másolása
            if os.path.exists(spacewar_src):
                self.log("DLL-ek másolása...")
                for item in os.listdir(spacewar_src):
                    s = os.path.join(spacewar_src, item)
                    d = os.path.join(game_dir, item)
                    if os.path.isfile(s):
                        if os.path.exists(d): 
                            os.rename(d, d + ".original") # Biztonsági mentés
                        shutil.copy2(s, d)
            
            # 2. steam_appid.txt létrehozása
            with open(os.path.join(game_dir, "steam_appid.txt"), "w") as f:
                f.write(appid)
            self.log(f"AppID beállítva: {appid}")

            # 3. Név beállítása (Goldberg emulátor stílus)
            settings_dir = os.path.join(game_dir, "settings")
            if not os.path.exists(settings_dir): os.makedirs(settings_dir)
            with open(os.path.join(settings_dir, "account_name.txt"), "w", encoding="utf-8") as f:
                f.write(player_name)
            self.log(f"Név beállítva: {player_name}")

            # 4. Indítás
            self.log("Játék indítása...")
            subprocess.Popen([game_exe], cwd=game_dir)
            self.log("Sikeres indítás! Jó játékot!")

        except Exception as e:
            self.log(f"HIBA: {str(e)}")
        
        self.root.after(0, lambda: self.patch_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalLauncherGUI(root)
    root.mainloop()
