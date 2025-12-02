"""
MT5 Automator Setup Script
Helps verify installation and setup
"""
import sys
import os
import subprocess

def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70 + "\n")

def print_status(item, status, details=""):
    """Print status item"""
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {item}")
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
        'Pillow', 'cv2', 'yaml', 'dotenv'
    ]
    
    all_installed = True
    for package in packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            elif package == 'yaml':
                __import__('yaml')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print_status(f"Package: {package}", True)
        except ImportError:
            print_status(f"Package: {package}", False, "Run: pip install -r requirements.txt")
            all_installed = False
    
    return all_installed

def check_tesseract():
    """Check if Tesseract is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        status = result.returncode == 0
        version = result.stdout.split('\n')[0] if status else ""
        print_status("Tesseract OCR", status, version if status else "Not installed")
        return status
    except FileNotFoundError:
        print_status("Tesseract OCR", False, "Not found in PATH")
        return False

def check_config_files():
    """Check if configuration files exist"""
    files = [
        ('config/config.yaml', 'Configuration file'),
        ('.env', 'Environment variables (copy from .env.example)')
    ]
    
    all_exist = True
    for file, desc in files:
        exists = os.path.exists(file)
        print_status(f"{desc}", exists, f"File: {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_directories():
    """Check if required directories exist"""
    dirs = ['src', 'config', 'logs', 'data', 'tests']
    
    all_exist = True
    for dir_name in dirs:
        exists = os.path.isdir(dir_name)
        print_status(f"Directory: {dir_name}", exists)
        if not exists:
            all_exist = False
    
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
        print("\033[92m✓ All checks passed! System is ready.\033[0m\n")
        print("Next steps:")
        print("1. Edit .env with your credentials")
        print("2. Update config/config.yaml with your channels")
        print("3. Run: python main.py")
        print("\nQuick start guide: See QUICKSTART.md")
    else:
        print("\033[91m✗ Some checks failed. Please fix the issues above.\033[0m\n")
        print("Installation guide: See README.md")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

