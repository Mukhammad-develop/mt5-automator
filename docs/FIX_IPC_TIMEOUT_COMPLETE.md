# Complete Guide: Fixing MT5 IPC Timeout Error

If you're getting `(-10005, 'IPC timeout')` errors, follow these steps **in order**:

## ✅ Step 1: Enable Automated Trading in MT5

**This is REQUIRED for API access!**

1. **Open MT5 terminal**
2. **Go to:** Tools → Options (or press `Ctrl+O`)
3. **Click:** "Expert Advisors" tab
4. **Check these boxes:**
   - ✅ "Allow automated trading"
   - ✅ "Allow DLL imports" (if available)
5. **Click:** "OK"
6. **Restart MT5**

## ✅ Step 2: Restart MT5 as Administrator

1. **Close MT5 completely:**
   - File → Exit
   - Check Task Manager → End any `terminal64.exe` processes

2. **Restart as Administrator:**
   - Right-click MT5 shortcut → "Run as administrator"
   - Log in to your account
   - Wait until fully loaded (prices updating)

3. **Verify automated trading is enabled:**
   - Look at the toolbar - there should be a green "AutoTrading" button
   - If it's red/gray, click it to enable

## ✅ Step 3: Test Python Connection

Run this test to verify Python can connect:

```powershell
py -3.12 -c "import MetaTrader5 as mt5; import time; time.sleep(5); result = mt5.initialize(); print('Success:', result); print('Error:', mt5.last_error() if not result else 'None'); mt5.shutdown() if result else None"
```

**If this returns `Success: True`**, the connection works! Run the bot.

**If this returns `Success: False`**, continue to Step 4.

## ✅ Step 4: Check Windows Firewall

1. **Open:** Windows Security → Firewall & network protection
2. **Click:** "Allow an app through firewall"
3. **Find:** "MetaTrader 5" or add manually:
   - Click "Change settings" → "Allow another app"
   - Browse to: `C:\Program Files\MetaTrader 5\terminal64.exe`
   - Check both "Private" and "Public"
4. **Click:** "OK"

## ✅ Step 5: Verify MT5 is Ready

Before running the bot, check:

- ✅ MT5 window is open and visible (not minimized)
- ✅ You are logged in (check Journal tab for "Login successful")
- ✅ Prices are updating in Market Watch
- ✅ "AutoTrading" button is green/enabled
- ✅ Account balance is visible

## ✅ Step 6: Try Different MT5 Installation

If still failing, try:

1. **Download fresh MT5 installer** from: https://www.metatrader5.com/
2. **Uninstall current MT5** (keep data if asked)
3. **Install fresh MT5**
4. **Log in and enable automated trading**
5. **Test connection again**

## ✅ Step 7: Check MetaTrader5 Package Version

Update the Python package:

```powershell
py -3.12 -m pip install --upgrade MetaTrader5
```

## ✅ Step 8: Alternative - Use MT5 Path

If auto-detect fails, try specifying the path in `config.env`:

```env
MT5_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
```

## Common Issues

### "IPC timeout" but MT5 is running
- **Cause:** MT5 is running but API interface isn't ready
- **Fix:** Restart MT5 as Administrator, wait 10 seconds after login

### "IPC timeout" after restart
- **Cause:** Windows blocking the connection
- **Fix:** Check firewall settings (Step 4)

### Connection works in test but bot fails
- **Cause:** Bot connecting too quickly
- **Fix:** The retry mechanism should handle this (already added)

## Still Not Working?

If all steps fail:

1. **Check MT5 version:** Should be build 3800+ (newer is better)
2. **Check Python version:** Should be 3.9-3.13 (not 3.14+)
3. **Try different broker:** Some brokers have better API support (XM, IC Markets, etc.)
4. **Contact broker support:** Ask if they support MT5 Python API

## Success Indicators

When everything works, you'll see:

```
MT5 initialized successfully
Logged in to MT5 account: [your_account]
Account balance: [amount] [currency]
MT5 connected successfully
```

If you see this, the bot is ready to trade! 🎉

