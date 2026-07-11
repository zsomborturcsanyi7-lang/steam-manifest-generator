@echo off
cd /d "C:\Users\iga\Desktop\j"
echo Teszt futtatása a gui_generator.py-val...
python -c "
import subprocess
import sys
import os

# Futtatjuk a gui_generator.py-t egy alprocessben
result = subprocess.run([sys.executable, 'gui_generator.py'], 
                       capture_output=True, text=True, timeout=10)
print('Kilépési kód:', result.returncode)
if result.stdout:
    print('STDOUT:', result.stdout[:500])
if result.stderr:
    print('STDERR:', result.stderr[:500])
"
pause