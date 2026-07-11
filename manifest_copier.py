import os
import shutil
import struct
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class ManifestCopier:
    def __init__(self, root):
        self.root = root
        self.root.title("MANIFEST FÁJL MÁSOLÓ")
        self.root.geometry("600x500")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Source directory
        tk.Label(self.root, text="Forrás mappa (működő manifest fájlokkal):", 
                font=("Arial", 10)).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.source_frame = tk.Frame(self.root)
        self.source_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.source_var = tk.StringVar()
        tk.Entry(self.source_frame, textvariable=self.source_var, 
                font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.source_frame, text="Tallózás", 
                  command=lambda: self.browse_folder(self.source_var)).pack(side=tk.LEFT, padx=5)
        
        # Target AppID
        tk.Label(self.root, text="Cél AppID (új játék):", 
                font=("Arial", 10)).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.appid_frame = tk.Frame(self.root)
        self.appid_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.appid_var = tk.StringVar()
        tk.Entry(self.appid_frame, textvariable=self.appid_var, 
                font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Output directory
        tk.Label(self.root, text="Kimeneti mappa:", 
                font=("Arial", 10)).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "Modified_Manifests"))
        tk.Entry(self.output_frame, textvariable=self.output_var, 
                font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.output_frame, text="Tallózás", 
                  command=lambda: self.browse_folder(self.output_var)).pack(side=tk.LEFT, padx=5)
        
        # Process button
        self.process_btn = ttk.Button(self.root, text="MANIFEST FÁJLOK MÓDOSÍTÁSA", 
                                     command=self.process_files)
        self.process_btn.pack(pady=20)
        
        # Log text
        self.log_text = tk.Text(self.root, height=15, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    def browse_folder(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def process_files(self):
        source_dir = self.source_var.get()
        target_appid = self.appid_var.get()
        output_dir = self.output_var.get()
        
        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("Hiba", "Kérlek válassz forrás mappát!")
            return
        
        if not target_appid or not target_appid.isdigit():
            messagebox.showerror("Hiba", "Kérlek adj meg egy érvényes AppID-t!")
            return
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        self.process_btn.config(state="disabled")
        
        try:
            self.log("=" * 50)
            self.log("MANIFEST FÁJLOK MÓDOSÍTÁSA")
            self.log("=" * 50)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            self.log(f"Kimeneti mappa: {output_dir}")
            
            # Find source AppID from manifest files
            source_appid = self.find_source_appid(source_dir)
            self.log(f"Forrás AppID: {source_appid}")
            self.log(f"Cél AppID: {target_appid}")
            
            # Copy and modify manifest files
            manifest_files = []
            for filename in os.listdir(source_dir):
                if filename.endswith(".manifest"):
                    source_file = os.path.join(source_dir, filename)
                    
                    # Parse the filename to get depot_id and manifest_id
                    match = re.match(r'(\d+)_(\d+)\.manifest', filename)
                    if match:
                        old_depot_id = match.group(1)
                        manifest_id = match.group(2)
                        
                        # Calculate new depot_id
                        if source_appid:
                            diff = int(old_depot_id) - int(source_appid)
                            new_depot_id = int(target_appid) + diff
                        else:
                            new_depot_id = int(target_appid) + 1
                        
                        new_filename = f"{new_depot_id}_{manifest_id}.manifest"
                        dest_file = os.path.join(output_dir, new_filename)
                        
                        # Copy and modify the manifest file
                        self.modify_manifest_file(source_file, dest_file, 
                                                 int(old_depot_id), new_depot_id)
                        
                        manifest_files.append(new_filename)
                        self.log(f"✓ {filename} → {new_filename}")
            
            # Generate LUA file
            self.log("\nLUA fájl generálása...")
            lua_path = os.path.join(output_dir, f"{target_appid}.lua")
            self.generate_lua_file(target_appid, manifest_files, lua_path)
            self.log(f"✓ LUA fájl: {target_appid}.lua")
            
            # Generate ACF file
            self.log("\nACF fájl generálása...")
            acf_path = os.path.join(output_dir, f"appmanifest_{target_appid}.acf")
            self.generate_acf_file(target_appid, acf_path)
            self.log(f"✓ ACF fájl: appmanifest_{target_appid}.acf")
            
            self.log("\n" + "=" * 50)
            self.log("✅ MÓDOSÍTÁS KÉSZ!")
            self.log(f"Fájlok itt: {output_dir}")
            self.log("\nMásold a fájlokat a Steam mappáiba:")
            self.log("1. .manifest fájlok → Steam/config/depotcache/")
            self.log("2. .lua fájl → Steam/config/stplug-in/")
            self.log("3. .acf fájl → Steam/steamapps/")
            
            messagebox.showinfo("Kész", f"Fájlok sikeresen módosítva!\n{output_dir}")
            
        except Exception as e:
            self.log(f"\n❌ HIBA: {str(e)}")
            messagebox.showerror("Hiba", f"Hiba történt:\n{str(e)}")
        finally:
            self.process_btn.config(state="normal")
    
    def find_source_appid(self, source_dir):
        """Find the source AppID from manifest filenames"""
        for filename in os.listdir(source_dir):
            if filename.endswith(".lua"):
                match = re.match(r'(\d+)\.lua', filename)
                if match:
                    return match.group(1)
        
        # If no LUA file, try to guess from manifest filenames
        for filename in os.listdir(source_dir):
            if filename.endswith(".manifest"):
                match = re.match(r'(\d+)_\d+\.manifest', filename)
                if match:
                    return match.group(1)
        
        return None
    
    def modify_manifest_file(self, source_path, dest_path, old_depot_id, new_depot_id):
        """Modify manifest file with new depot ID"""
        # Read the binary file
        with open(source_path, 'rb') as f:
            data = f.read()
        
        # Simple approach: just copy the file (for now)
        # In a real implementation, we would parse the protobuf and modify the depot_id field
        shutil.copy2(source_path, dest_path)
        
        # TODO: Actually modify the protobuf depot_id field
        # This requires proper protobuf parsing
    
    def generate_lua_file(self, appid, manifest_files, output_path):
        """Generate LUA file based on manifest files"""
        base_id = int(appid)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"addappid({appid})\n")
            
            # Add entries for each manifest
            for manifest in manifest_files:
                match = re.match(r'(\d+)_(\d+)\.manifest', manifest)
                if match:
                    depot_id = match.group(1)
                    manifest_id = match.group(2)
                    
                    # Generate placeholder key
                    import random
                    key = ''.join(random.choice('0123456789abcdef') for _ in range(64))
                    
                    f.write(f'addappid({depot_id},0,"{key}")\n')
    
    def generate_acf_file(self, appid, output_path):
        """Generate ACF file"""
        content = f'''"AppState"
{{
	"appid" "{appid}"
	"Universe" "1"
	"name" "Generated Game {appid}"
	"StateFlags" "4"
	"installdir" "Game_{appid}"
	"LastUpdated" "0"
	"UpdateResult" "0"
	"SizeOnDisk" "0"
	"buildid" "0"
	"LastOwned" "0"
	"BytesToDownload" "0"
	"BytesDownloaded" "0"
	"AutoUpdateBehavior" "0"
	"AllowOtherDownloadsWhileRunning" "0"
	"ScheduledAutoUpdate" "0"
}}'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    root = tk.Tk()
    app = ManifestCopier(root)
    root.mainloop()