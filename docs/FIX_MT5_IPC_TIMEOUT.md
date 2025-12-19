# Fix MT5 IPC Timeout Error

If you see this error:
```
MT5 initialize failed: (-10005, 'IPC timeout')
```

This means the bot cannot communicate with the MetaTrader 5 terminal. Here's how to fix it:

## Solution 1: Make Sure MT5 Terminal is Running (Most Common)

**The MT5 terminal MUST be open and running before you start the bot.**

1. **Open MetaTrader 5 terminal** on your computer
2. **Log in to your account** (if required)
3. **Keep the MT5 terminal window open**
4. **Then run the bot**: `py -3.12 main.py`

The bot connects to the running MT5 terminal, so it must be open first!

## Solution 2: Check MT5 Installation Path

If MT5 is running but you still get the error, check the path:

1. **Find your MT5 installation path:**
   - Usually: `C:\Program Files\MetaTrader 5\terminal64.exe`
   - Or: `C:\Program Files (x86)\MetaTrader 5\terminal64.exe`
   - Or check your Start Menu → Right-click MT5 → Properties → Location

2. **Add to `config.env`:**
   ```env
   MT5_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
   ```
   **Important:** Use forward slashes `/` or double backslashes `\\`

3. **Verify the path exists:**
   - Open File Explorer
   - Navigate to the path
   - Make sure `terminal64.exe` exists there

## Solution 3: Restart MT5 Terminal

Sometimes MT5 gets "locked" or busy:

1. **Close MT5 terminal completely**
2. **Wait 5 seconds**
3. **Open MT5 terminal again**
4. **Log in**
5. **Run the bot again**

## Solution 4: Run MT5 as Administrator

If you still have issues:

1. **Right-click MT5 terminal** → "Run as administrator"
2. **Log in**
3. **Run the bot**

## Solution 5: Check if MT5 is Already Connected

If another program is using MT5:

1. **Close all other programs** that might connect to MT5
2. **Restart MT5 terminal**
3. **Run the bot**

## Quick Checklist

Before running the bot, make sure:

- ✅ MT5 terminal is **open and running**
- ✅ You are **logged in** to your MT5 account
- ✅ MT5 terminal window is **visible** (not minimized to tray)
- ✅ No other programs are using MT5
- ✅ `MT5_PATH` in `config.env` is correct (if specified)

## Still Not Working?

1. **Check the error message** - The bot now provides detailed guidance
2. **Check MT5 terminal** - Look for any error messages in MT5
3. **Try restarting your computer** - Sometimes Windows needs a fresh start
4. **Check Windows Firewall** - Make sure it's not blocking MT5

## Example config.env Entry

```env
# MT5 Settings
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo
MT5_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
```

**Note:** `MT5_PATH` is optional. If not set, the bot will try to auto-detect MT5, but specifying it is more reliable.

