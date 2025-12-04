# Quick Start Guide

Get MT5 Trading Automator running in under 15 minutes on **macOS** or **Windows**.

---

## 🖥️ macOS Setup (Testing/Development)

### What You'll Get
- ✅ Full signal processing (Telegram + AI)
- ✅ Dry-run mode (shows what would execute)
- ❌ No actual MT5 trading (Windows only)

### Step 1: Install Python Dependencies (2 min)

```bash
cd mt5_automator
pip3 install -r requirements-dev.txt
```

### Step 2: Install Tesseract OCR (1 min)

```bash
brew install tesseract
```

### Step 3: Get API Keys (5 min)

**Telegram API:**
1. Visit: https://my.telegram.org/auth
2. Login → "API development tools"
3. Create app → Copy `api_id` and `api_hash`

**DeepSeek AI (Optional but Recommended):**
1. Visit: https://platform.deepseek.com
2. Create account → Get API key

### Step 4: Configure Environment (2 min)

Create `.env` file:

```bash
cat > .env << EOF
# Telegram (Required)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# DeepSeek AI (Optional - for better parsing)
DEEPSEEK_API_KEY=sk-your-key-here

# MT5 (Not needed for macOS testing)
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=
EOF
```

### Step 5: Configure Channels (1 min)

Edit `config/config.yaml`:

```yaml
telegram:
  channels:
    - "your_signal_channel_username"

mode:
  dry_run: true  # Keep true for macOS
```

### Step 6: Run! (1 min)

```bash
python3 main.py
```

**What You'll See:**
```
🧪 DRY RUN MODE - Commands will be logged, not executed
Connected to Telegram
Monitoring channels...

[New signal received]
AI Vision parsed: BUY XAUUSD 2650-2648
Risk calculation: 1.0% = $100

🧪 DRY RUN - PLACE_ORDER
  ticket: 1000
  type: BUY LIMIT
  symbol: XAUUSD
  volume: 0.33
  entry_price: 2650.5
  stop_loss: 2645.0
  take_profit: 2655.0
```

✅ **Testing complete!** You see exactly what would execute on Windows.

---

## 🪟 Windows Setup (Production Trading)

### What You'll Get
- ✅ Full signal processing
- ✅ Real MT5 trading
- ✅ Actual order execution

### Prerequisites

- ✅ MetaTrader 5 installed and logged in
- ✅ Broker account with trading enabled
- ✅ Python 3.9+ installed

### Step 1: Install Python Dependencies (2 min)

```cmd
cd mt5_automator
pip install -r requirements-windows.txt
```

### Step 2: Install Tesseract OCR (2 min)

Download and install from:
https://github.com/UB-Mannheim/tesseract/wiki

Default installation path: `C:\Program Files\Tesseract-OCR`

### Step 3: Get API Keys (5 min)

Same as macOS:
- **Telegram API**: https://my.telegram.org/auth
- **DeepSeek AI**: https://platform.deepseek.com (optional)

### Step 4: Configure Environment (2 min)

Create `.env` file:

```cmd
notepad .env
```

Add:
```
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# DeepSeek AI (Optional)
DEEPSEEK_API_KEY=sk-your-key-here

# MT5 (Required for Windows)
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Server
```

### Step 5: Configure for Production (2 min)

Edit `config/config.yaml`:

```yaml
telegram:
  channels:
    - "your_signal_channel_username"

mt5:
  path: "C:/Program Files/MetaTrader 5/terminal64.exe"

mode:
  dry_run: false  # PRODUCTION MODE - Real trading!

trading:
  risk_percent: 1.0  # Start conservative
  num_positions: 3
```

### Step 6: Test Connection First (1 min)

```cmd
python src\mt5_engine.py
```

Should show:
```
MT5 connection test passed!
Account: {'balance': 10000, ...}
```

### Step 7: Run Production! (1 min)

```cmd
python main.py
```

**What You'll See:**
```
Production mode - Real trading enabled
Connected to MT5
Connected to Telegram
MT5 Automator is RUNNING

[New signal received]
AI Vision parsed: BUY XAUUSD 2650-2648
Calculated lot sizes: [0.33, 0.33, 0.33]
Order #123456 placed: BUY LIMIT XAUUSD 0.33 lot @ 2650.5
Order #123457 placed: BUY MARKET XAUUSD 0.33 lot @ 2649.35
Order #123458 placed: BUY LIMIT XAUUSD 0.33 lot @ 2648.2

TRADE EXECUTED: BUY XAUUSD
Orders: 3
Total volume: 0.99 lots
```

🚀 **Live trading active!**

---

## 📊 Comparison

| Feature | macOS | Windows |
|---------|-------|---------|
| **Setup Time** | 15 min | 15 min |
| **Signal Processing** | ✅ Full | ✅ Full |
| **AI Parsing** | ✅ Yes | ✅ Yes |
| **OCR** | ✅ Yes | ✅ Yes |
| **MT5 Connection** | ❌ No | ✅ Yes |
| **Trading** | 🧪 Dry-run | ✅ Real |
| **Use Case** | Testing | Production |

---

## 🎯 First Signal Test

### macOS Test

Send yourself a test message:

```
BUY XAUUSD 2650 - 2648
SL: 2645
TP1: 2655
TP2: 2660
```

Watch the dry-run output!

### Windows Test

**⚠️ IMPORTANT:** Test on DEMO account first!

1. Open MT5 demo account
2. Update `.env` with demo credentials
3. Run the system
4. Send test signal
5. Verify orders in MT5 terminal

---

## 🔧 Configuration Options

### Minimal (Get Started Fast)

```yaml
telegram:
  channels: ["your_channel"]

mode:
  dry_run: true  # false for Windows production

trading:
  risk_percent: 1.0
  num_positions: 3
```

### Full Configuration

```yaml
telegram:
  channels:
    - "channel1"
    - "channel2"
    - "channel3"

ai:
  enabled: true  # Use DeepSeek AI
  use_vision: true  # AI reads images directly
  fallback_to_ocr: true  # Backup to Tesseract
  fallback_to_regex: true  # Backup to regex

mode:
  dry_run: false  # Production mode

mt5:
  path: "C:/Program Files/MetaTrader 5/terminal64.exe"

trading:
  risk_percent: 1.0  # Risk per signal
  num_positions: 3  # Positions per signal (3, 6, or 9)
  default_symbol: "XAUUSD"
  breakeven_trigger: "middle_entry"
  breakeven_offset: 0.1

ocr:
  tesseract_cmd: "/usr/bin/tesseract"  # macOS/Linux
  # tesseract_cmd: "C:/Program Files/Tesseract-OCR/tesseract.exe"  # Windows

logging:
  level: "INFO"  # DEBUG for troubleshooting
  file: "logs/mt5_automator.log"
```

---

## 🆘 Troubleshooting

### macOS Issues

**"MetaTrader5 not found"**
- ✅ **Expected!** Use `requirements-dev.txt`

**"Tesseract not found"**
```bash
brew install tesseract
```

**"Module 'src' not found"**
```bash
export PYTHONPATH=/path/to/mt5_automator
python3 main.py
```

### Windows Issues

**"MT5 initialize failed"**
- Check MT5 is running
- Verify path in config.yaml
- Try without path (uses active MT5)

**"Login failed"**
- Check credentials in .env
- Verify server name
- Ensure account not locked

**"Tesseract not found"**
- Install from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH or update config.yaml

### Common Issues (Both)

**"Invalid API ID/Hash"**
- Get from: https://my.telegram.org
- Check for spaces in .env

**"No signals received"**
- Verify channel usernames (no @ symbol)
- Check you have access to channels
- Look for errors in logs

**"AI parsing failed"**
- Check DEEPSEEK_API_KEY in .env
- System falls back to regex automatically

---

## 📈 Next Steps

### After Setup (macOS)

1. ✅ Test with real channels
2. ✅ Verify AI parsing works
3. ✅ Check dry-run commands look correct
4. ✅ Deploy to Windows when ready

### After Setup (Windows)

1. ⚠️ Test on DEMO account first!
2. ✅ Monitor for 24 hours
3. ✅ Check logs regularly
4. ✅ Adjust risk if needed
5. ✅ Go live when confident

### Recommended Testing

**Day 1:** Demo account, 0.01 lots
**Day 2:** Demo account, normal lots
**Day 3:** Check all signals processed correctly
**Day 4+:** Go live with low risk (0.5-1%)

---

## 📚 More Documentation

- **[AI_INTEGRATION.md](AI_INTEGRATION.md)** - DeepSeek AI features
- **[PLATFORM_GUIDES.md](PLATFORM_GUIDES.md)** - Platform-specific details
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical specs
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[../README.md](../README.md)** - Complete documentation

---

## 🎉 Summary

### macOS Users
```bash
pip3 install -r requirements-dev.txt
# Configure .env
python3 main.py
# See dry-run commands ✅
```

### Windows Users
```cmd
pip install -r requirements-windows.txt
# Configure .env and config.yaml
# Set dry_run: false
python main.py
# Real trading active! 🚀
```

**Both platforms use the exact same code!**

---

## 🛡️ Safety Tips

- ✅ Always test on demo first
- ✅ Start with low risk (0.5-1%)
- ✅ Monitor logs regularly
- ✅ Keep credentials secure
- ✅ Set broker trading limits
- ⚠️ Never run unmonitored initially

**Happy Trading!** 📈
