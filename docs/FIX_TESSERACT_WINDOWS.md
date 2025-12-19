# Fix Tesseract OCR on Windows

If you get the error `tesseract: Имя "tesseract" не распознано` (tesseract not recognized), Tesseract is installed but not in your system PATH. Here are two ways to fix it:

## Method 1: Add Tesseract to System PATH (Recommended)

This allows you to use `tesseract` from anywhere in PowerShell.

### Step 1: Find Tesseract Installation Path

Tesseract is usually installed in one of these locations:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

**To find it:**
1. Open File Explorer
2. Go to `C:\Program Files\` or `C:\Program Files (x86)\`
3. Look for `Tesseract-OCR` folder
4. Inside, you should see `tesseract.exe`

**Or use PowerShell to search:**
```powershell
Get-ChildItem -Path "C:\Program Files" -Filter "tesseract.exe" -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\Program Files (x86)" -Filter "tesseract.exe" -Recurse -ErrorAction SilentlyContinue
```

### Step 2: Add to PATH

1. **Open System Properties:**
   - Press `Win + R`
   - Type `sysdm.cpl` and press Enter
   - Or: Right-click "This PC" → Properties → Advanced system settings

2. **Edit PATH:**
   - Click "Environment Variables" button
   - Under "System variables", find `Path` and click "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR` (or your actual path)
   - Click "OK" on all windows

3. **Restart PowerShell:**
   - Close all PowerShell windows
   - Open a new PowerShell window
   - Test: `tesseract --version`

## Method 2: Update Config File (Easier, No Restart Needed)

If you don't want to modify system PATH, just tell the bot where Tesseract is installed.

### Step 1: Find Tesseract Path

Same as Method 1 - find where `tesseract.exe` is located.

### Step 2: Update config.env

1. Open `config.env` in a text editor
2. Find the line with `TESSERACT_CMD` (or add it if missing)
3. Set it to the full path to tesseract.exe:

```env
# For example, if Tesseract is in default location:
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

**Important:** Use forward slashes `/` or double backslashes `\\` in the path:
- ✅ `C:/Program Files/Tesseract-OCR/tesseract.exe`
- ✅ `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`
- ❌ `C:\Program Files\Tesseract-OCR\tesseract.exe` (single backslash won't work)

### Step 3: Verify

The bot will automatically use this path. No restart needed!

## Quick Test

After fixing, test Tesseract:

**If you used Method 1 (PATH):**
```powershell
tesseract --version
```

**If you used Method 2 (Config):**
The bot will use the path from config automatically. You can test by running:
```powershell
python test_system.py
```

## Troubleshooting

### "File not found" error

- Make sure the path is correct (check File Explorer)
- Use forward slashes `/` in config file
- Make sure `tesseract.exe` exists at that location

### Still not working?

1. **Check if Tesseract is actually installed:**
   - Look in Start Menu → Tesseract-OCR folder
   - If you see shortcuts, it's installed

2. **Reinstall Tesseract:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - During installation, check "Add to PATH" option
   - This automatically adds it to PATH

3. **Use full path in config:**
   - Even if PATH doesn't work, the config method will work
   - Just make sure the path is correct

## Example config.env Entry

```env
# OCR Settings (if using config method)
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

## Verify It Works

Run the test suite:
```powershell
python test_system.py
```

If Tesseract is configured correctly, the OCR tests should pass (or at least not fail with "not found" errors).

