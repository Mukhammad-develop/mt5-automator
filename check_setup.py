"""
Simple setup checker for Windows
Run: python check_setup.py
"""
import sys
import os

print("=" * 70)
print("MT5 AUTOMATOR - QUICK SETUP CHECK")
print("=" * 70)
print()

# Check Python
print("1. Python Version:")
print(f"   Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
if sys.version_info >= (3, 9):
    print("   [OK] Python version is good")
else:
    print("   [FAIL] Need Python 3.9 or higher")
print()

# Check config file
print("2. Configuration File:")
if os.path.exists('config.env'):
    print("   [OK] config.env exists")
else:
    print("   [FAIL] config.env not found")
    print("   -> Copy config.env.example to config.env")
print()

# Check required packages
print("3. Python Packages:")
packages = {
    'telethon': 'telethon',
    'MetaTrader5': 'MetaTrader5',
    'pytesseract': 'pytesseract',
    'Pillow': 'PIL',
    'opencv': 'cv2',
    'yaml': 'yaml',
    'dotenv': 'dotenv'
}

missing = []
for name, import_name in packages.items():
    try:
        __import__(import_name)
        print(f"   [OK] {name}")
    except ImportError:
        print(f"   [FAIL] {name} - not installed")
        missing.append(name)

if missing:
    print()
    print("   To install missing packages, run:")
    if sys.platform == 'win32':
        print("   pip install -r requirements-windows.txt")
    else:
        print("   pip install -r requirements.txt")
print()

# Check Tesseract
print("4. Tesseract OCR:")
try:
    import subprocess
    result = subprocess.run(['tesseract', '--version'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version = result.stdout.split('\n')[0]
        print(f"   [OK] {version}")
    else:
        print("   [FAIL] Tesseract not working")
        print("   -> Set TESSERACT_CMD in config.env")
except FileNotFoundError:
    print("   [FAIL] Tesseract not found in PATH")
    print("   -> Set TESSERACT_CMD in config.env")
    print("   -> See docs/FIX_TESSERACT_WINDOWS.md")
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    print("   -> Set TESSERACT_CMD in config.env")
print()

# Summary
print("=" * 70)
if not missing and os.path.exists('config.env'):
    print("[OK] Basic setup looks good!")
    print()
    print("Next steps:")
    print("1. Edit config.env with your credentials:")
    print("   - MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
    print("   - TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
    print("   - TELEGRAM_CHANNELS")
    print("2. Run: python test_system.py (to test everything)")
    print("3. Run: python main.py (to start the bot)")
else:
    print("[!] Some issues found - see above")
    if missing:
        print()
        print("Install missing packages:")
        if sys.platform == 'win32':
            print("  pip install -r requirements-windows.txt")
        else:
            print("  pip install -r requirements.txt")
print("=" * 70)


