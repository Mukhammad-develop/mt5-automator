"""
MT5 Automator Setup Script
Helps verify installation and setup
"""
import sys
import os
import subprocess

# Windows-friendly symbols and colors
def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70 + "\n")

def print_status(item, status, details=""):
    """Print status item (Windows-compatible)"""
    # Use simple symbols for Windows compatibility
    symbol = "[OK]" if status else "[FAIL]"
    # Windows PowerShell/CMD may not support ANSI colors properly
    # Use simple text for better compatibility
    print(f"{symbol} {item}")
    
    if details:
        print(f"  {details}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 9)
    status = version >= required
    print_status(
        f"Python {version.major}.{version.minor}.{version.micro}",
        status,
        "Minimum required: Python 3.9" if not status else ""
    )
    return status

def check_dependencies():
    """Check if required packages are installed"""
    packages = [
        'telethon', 'MetaTrader5', 'pytesseract', 
        'PIL', 'cv2', 'yaml', 'dotenv'
    ]
    
    # Map package names to import names
    import_map = {
        'PIL': 'PIL',
        'cv2': 'cv2',
        'yaml': 'yaml',
        'dotenv': 'dotenv'
    }
    
    all_installed = True
    requirements_file = 'requirements-windows.txt' if sys.platform == 'win32' else 'requirements.txt'
    
    for package in packages:
        try:
            if package in import_map:
                __import__(import_map[package])
            else:
                __import__(package)
            print_status(f"Package: {package}", True)
        except ImportError:
            print_status(f"Package: {package}", False, f"Run: pip install -r {requirements_file}")
            all_installed = False
    
    return all_installed

def check_tesseract():
    """Check if Tesseract is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        status = result.returncode == 0
        version = result.stdout.split('\n')[0] if status else ""
        print_status("Tesseract OCR", status, version if status else "Not installed")
        if not status:
            print_status("", False, "  -> Set TESSERACT_CMD in config.env (see docs/FIX_TESSERACT_WINDOWS.md)")
        return status
    except FileNotFoundError:
        print_status("Tesseract OCR", False, "Not found in PATH")
        print_status("", False, "  -> Set TESSERACT_CMD in config.env (see docs/FIX_TESSERACT_WINDOWS.md)")
        return False
    except subprocess.TimeoutExpired:
        print_status("Tesseract OCR", False, "Command timed out")
        return False
    except Exception as e:
        print_status("Tesseract OCR", False, f"Error: {e}")
        print_status("", False, "  -> Set TESSERACT_CMD in config.env (see docs/FIX_TESSERACT_WINDOWS.md)")
        return False

def check_config_files():
    """Check if configuration files exist"""
    files = [
        ('config.env', 'Configuration file (config.env)'),
        ('config.env.example', 'Example config (config.env.example)')
    ]
    
    all_exist = True
    for file, desc in files:
        exists = os.path.exists(file)
        print_status(f"{desc}", exists, f"File: {file}")
        if not exists and file == 'config.env':
            # Try to create from example
            if os.path.exists('config.env.example'):
                try:
                    import shutil
                    shutil.copy('config.env.example', 'config.env')
                    print_status("", True, "  -> Created config.env from config.env.example")
                    print_status("", False, "  -> IMPORTANT: Edit config.env with your credentials!")
                    all_exist = True  # File now exists
                except Exception as e:
                    print_status("", False, f"  -> Failed to create: {e}")
                    print_status("", False, "  -> Manually copy config.env.example to config.env")
                    all_exist = False
            else:
                print_status("", False, "  -> Copy config.env.example to config.env and edit it")
                all_exist = False
    
    return all_exist

def check_directories():
    """Check if required directories exist, create if missing"""
    dirs = ['src', 'config', 'logs', 'data', 'data/images', 'tests']
    
    all_exist = True
    for dir_name in dirs:
        exists = os.path.isdir(dir_name)
        if not exists:
            try:
                os.makedirs(dir_name, exist_ok=True)
                print_status(f"Directory: {dir_name}", True, "Created automatically")
            except Exception as e:
                print_status(f"Directory: {dir_name}", False, f"Failed to create: {e}")
                all_exist = False
        else:
            print_status(f"Directory: {dir_name}", True)
    
    return all_exist

def main():
    """Main setup check"""
    print_header("MT5 TRADING AUTOMATOR - SETUP VERIFICATION")
    
    checks = []
    
    print_header("1. Python Environment")
    checks.append(check_python_version())
    
    print_header("2. Python Dependencies")
    checks.append(check_dependencies())
    
    print_header("3. External Tools")
    checks.append(check_tesseract())
    
    print_header("4. Project Structure")
    checks.append(check_directories())
    
    print_header("5. Configuration Files")
    checks.append(check_config_files())
    
    # Summary
    print_header("SETUP SUMMARY")
    
    if all(checks):
        print("[OK] All checks passed! System is ready.\n")
        print("Next steps:")
        print("1. Edit config.env with your credentials")
        print("   - MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
        print("   - TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        print("   - TELEGRAM_CHANNELS (comma-separated)")
        print("2. Run: python main.py")
        print("\nQuick start guide: See docs/WINDOWS_QUICKSTART.md")
    else:
        print("[FAIL] Some checks failed. Please fix the issues above.\n")
        print("Installation guide: See README.md")
        print("Windows guide: See docs/WINDOWS_QUICKSTART.md")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

