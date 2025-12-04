# Windows Quick Start - MT5 Trading Bot with AI

**Complete setup in 20 minutes** → Fully automated trading with Telegram signals + DeepSeek AI + MT5

---

## 🎯 What You're Building

A fully automated trading system that:
- 📱 Reads signals from Telegram channels (text + images)
- 🤖 Uses DeepSeek AI to understand complex signals
- 💰 Auto-calculates risk-based lot sizes
- 📊 Executes trades on MetaTrader 5
- 🛡️ Manages TP/SL and breakeven automatically
- 🔄 Runs 24/7 on Windows

---

## ✅ Prerequisites (5 minutes)

Before starting, you need:

### 1. MetaTrader 5
- ✅ Installed and running
- ✅ Logged into broker account (DEMO for testing!)
- ✅ Can place manual trades
- 📍 Default path: `C:\Program Files\MetaTrader 5\terminal64.exe`

### 2. Python 3.9+
Download from: https://www.python.org/downloads/

**⚠️ IMPORTANT:** Check "Add Python to PATH" during installation!

Verify:
```cmd
python --version
```
Should show: `Python 3.9.x` or higher

### 3. Git (Optional)
For cloning the repository:
```cmd
git clone https://github.com/Mukhammad-develop/mt5-automator.git
cd mt5-automator
```

Or download ZIP and extract.

---

## 📦 Installation (10 minutes)

### Step 1: Install Python Dependencies (3 min)

Open Command Prompt in project folder:

```cmd
cd C:\path\to\mt5-automator
pip install -r requirements-windows.txt
```

**Packages installed:**
- ✅ MetaTrader5 (MT5 Python API)
- ✅ Telethon (Telegram client)
- ✅ OpenAI (DeepSeek API)
- ✅ Pillow, OpenCV (Image processing)
- ✅ PyTesseract (OCR backup)
- ✅ PyYAML, python-dotenv (Config)

### Step 2: Install Tesseract OCR (2 min)

Download installer:
👉 https://github.com/UB-Mannheim/tesseract/wiki

**Choose:** `tesseract-ocr-w64-setup-5.3.x.exe`

**Install to:** `C:\Program Files\Tesseract-OCR` (default)

✅ Add to PATH during installation (check the box)

Verify:
```cmd
tesseract --version
```

### Step 3: Get API Keys (5 min)

#### A. Telegram API (Required)

1. Visit: **https://my.telegram.org/auth**
2. Login with your phone number
3. Click **"API development tools"**
4. Create new application:
   - App title: `MT5 Automator`
   - Short name: `mt5bot`
   - Platform: `Desktop`
5. **Copy** `api_id` and `api_hash`

#### B. DeepSeek AI API (Required for AI parsing)

1. Visit: **https://platform.deepseek.com**
2. Sign up / Login
3. Go to **API Keys** section
4. Click **"Create API Key"**
5. **Copy** the key (starts with `sk-`)

💡 **Cost:** ~$0.27 per 1M tokens (very cheap, ~100 signals = $0.01)

---

## ⚙️ Configuration (5 minutes)

### Step 1: Create Environment File

In project root, create `.env` file:

```cmd
notepad .env
```

Paste and **replace with your real values**:

```env
# ==========================================
# TELEGRAM API (Get from my.telegram.org)
# ==========================================
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+1234567890

# ==========================================
# DEEPSEEK AI API (Get from platform.deepseek.com)
# ==========================================
DEEPSEEK_API_KEY=sk-your-actual-key-here

# ==========================================
# MT5 CREDENTIALS (Your broker login)
# ==========================================
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=YourBroker-Demo

# Example servers:
# - Exness-MT5Trial
# - ICMarkets-Demo02
# - FTMO-Demo
```

**Save and close**

### Step 2: Configure Trading Settings

Edit `config\config.yaml`:

```cmd
notepad config\config.yaml
```

**Minimal Production Config:**

```yaml
# ==========================================
# TELEGRAM CHANNELS
# ==========================================
telegram:
  channels:
    - "your_signal_channel_username"  # Replace with actual channel
    - "another_channel"                # Add more as needed
  # NO @ symbol, just the username

# ==========================================
# DEEPSEEK AI CONFIGURATION
# ==========================================
ai:
  enabled: true                # Use AI parsing
  provider: "deepseek"         # DeepSeek AI
  model: "deepseek-chat"       # Best for text signals
  vision_model: "deepseek-reasoner"  # Best for image signals
  use_vision: true             # Parse images with AI
  fallback_to_ocr: true        # Backup: Use Tesseract if AI fails
  fallback_to_regex: true      # Backup: Use regex if OCR fails
  max_retries: 2
  timeout: 30

# ==========================================
# MT5 SETTINGS
# ==========================================
mt5:
  path: "C:/Program Files/MetaTrader 5/terminal64.exe"
  # Leave empty to use currently running MT5

# ==========================================
# TRADING PARAMETERS
# ==========================================
trading:
  risk_percent: 1.0            # 1% risk per signal
  num_positions: 3             # 3 positions per signal (standard)
  default_symbol: "XAUUSD"     # Default if not specified in signal
  breakeven_trigger: "middle_entry"  # Move SL to BE when middle hit
  breakeven_offset: 0.1        # Small profit buffer

# ==========================================
# MODE (IMPORTANT!)
# ==========================================
mode:
  dry_run: true  # ⚠️ START WITH TRUE FOR TESTING!
  # Set to false ONLY after successful demo testing

# ==========================================
# OCR SETTINGS (Backup)
# ==========================================
ocr:
  tesseract_cmd: "C:/Program Files/Tesseract-OCR/tesseract.exe"
  preprocessing:
    resize_factor: 2.0
    contrast_boost: true
    denoise: true
    sharpen: true

# ==========================================
# LOGGING
# ==========================================
logging:
  level: "INFO"              # INFO = clean, DEBUG = detailed
  console_level: "WARNING"   # Only important messages in console
  file: "logs/mt5_automator.log"
  max_bytes: 10485760
  backup_count: 5
```

**Save and close**

---

## 🚀 First Run - Dry Run Mode (Safe Testing)

### Step 1: Test MT5 Connection

```cmd
python src\mt5_engine.py
```

✅ **Expected Output:**
```
MT5Engine initialized
Attempting to connect to MT5...
Connected to MT5 successfully
MT5 connection test passed!
Account: {'balance': 10000, 'equity': 10000, ...}
XAUUSD: Bid=2645.50, Ask=2645.80
```

❌ **If it fails:**
- Check MT5 is open and logged in
- Verify credentials in `.env`
- Check server name is correct

### Step 2: Test Telegram Connection

```cmd
python main.py
```

**First time:** You'll be asked for verification code
1. Enter code from Telegram
2. May ask for 2FA password if enabled

✅ **Expected Output:**
```
🧪 DRY RUN MODE - Commands will be logged, not executed
MT5Engine initialized
Connected to Telegram as +1234567890
Monitoring channels: ['your_channel']
MT5 Automator is RUNNING - Press Ctrl+C to stop
Waiting for signals...
```

**Leave it running!**

### Step 3: Send Test Signal

In Telegram, send to yourself or test channel:

```
BUY XAUUSD 2650.50 - 2648.20
SL1: 2645.00
SL2: 2643.50
SL3: 2642.00
TP1: 2655.00
TP2: 2660.00
```

✅ **Expected Output:**
```
======================================================================
Processing new signal from your_channel
======================================================================
📊 Parsed: BUY XAUUSD | Entry: 2650.5-2648.2 | TP: 2655.0/2660.0 | SL: 2645.0

🧪 DRY RUN: BUY LIMIT XAUUSD 0.07 lot @ 2650.5 | SL: 2645.0 | TP: 2655.0 | Ticket: #1000
🧪 DRY RUN: BUY LIMIT XAUUSD 0.06 lot @ 2649.35 | SL: 2643.5 | TP: 2660.0 | Ticket: #1001
🧪 DRY RUN: BUY LIMIT XAUUSD 0.05 lot @ 2648.2 | SL: 2642.0 | TP: 2660.0 | Ticket: #1002

======================================================================
✅ TRADE EXECUTED
======================================================================
Signal: BUY XAUUSD (2650.5-2648.2)
Orders: 3 positions
Volume: 0.18 lots
Signal ID: abc123def456
======================================================================
```

🎉 **Perfect!** The system:
- ✅ Received signal from Telegram
- ✅ Parsed with DeepSeek AI
- ✅ Calculated risk-based lot sizes
- ✅ Determined order types (LIMIT/MARKET)
- ✅ Showed what WOULD execute

**No real trades placed!** Just simulation.

---

## 🔥 Go Live - Production Mode

### ⚠️ CRITICAL SAFETY STEPS

1. **Test on DEMO account for 24-48 hours minimum**
2. **Monitor all signals manually first**
3. **Verify lot calculations are correct**
4. **Start with LOW risk (0.5-1%)**
5. **Set broker account limits**

### Enable Production Trading

Edit `config\config.yaml`:

```yaml
mode:
  dry_run: false  # 🔴 LIVE TRADING ENABLED!
```

**Optional but RECOMMENDED safety limits:**

```yaml
trading:
  risk_percent: 0.5  # Start very conservative
  max_daily_trades: 10  # Prevent runaway trading
  max_total_risk: 5.0   # Max 5% total exposure
```

### Run Production

```cmd
python main.py
```

✅ **Expected Output:**
```
Production mode - Real trading enabled
Connected to MT5: Balance=$10,000, Equity=$10,000
Connected to Telegram as +1234567890
MT5 Automator is RUNNING
```

**When signal arrives:**
```
======================================================================
Processing new signal from signal_channel
======================================================================
📊 Parsed: BUY XAUUSD | Entry: 2650.5-2648.2 | TP: 2655.0/2660.0 | SL: 2645.0
Calculated lot sizes: [0.07, 0.06, 0.05]

Order #12345678 placed: BUY LIMIT XAUUSD 0.07 lot @ 2650.5, SL=2645.0, TP=2655.0
Order #12345679 placed: BUY LIMIT XAUUSD 0.06 lot @ 2649.35, SL=2643.5, TP=2660.0
Order #12345680 placed: BUY LIMIT XAUUSD 0.05 lot @ 2648.2, SL=2642.0, TP=2660.0

======================================================================
✅ TRADE EXECUTED
======================================================================
Signal: BUY XAUUSD (2650.5-2648.2)
Orders: 3 positions
Volume: 0.18 lots
Signal ID: abc123def456
======================================================================
```

**Check MT5 Terminal** → You'll see the orders! 🎯

---

## 📊 How It Works

### Signal Flow

```
Telegram Signal (Text/Image)
         ↓
DeepSeek AI Parsing (Smart interpretation)
         ↓
Signal Validation (Check format, prices)
         ↓
Risk Calculation (1% account = X lots)
         ↓
MT5 Order Placement (3 positions)
         ↓
Position Monitoring (Breakeven, TP protection)
         ↓
Automatic Management (Close at TP, move SL)
```

### Position Logic (3 Orders)

**Example: BUY XAUUSD 2650.50 - 2648.20**

| Position | Entry | SL | TP | Logic |
|----------|-------|----|----|-------|
| **#1** | 2650.50 (Upper) | 2645.00 | 2655.00 | Closes first at TP1 |
| **#2** | 2649.35 (Middle) | 2643.50 | 2660.00 | Closes at TP2 |
| **#3** | 2648.20 (Lower) | 2642.00 | 2660.00 | Closes at TP2 |

**Breakeven Logic:**
- When price hits middle entry → All SLs move to breakeven
- Protects profit automatically

**TP2 Protection:**
- When TP2 hit → Cancel all pending orders
- Prevents new entries after target reached

---

## 🛡️ Advanced Features

### 1. AI Vision for Images

If signal channel sends images, DeepSeek AI reads them directly:

```python
# Automatically handled!
- Image received → DeepSeek Vision analyzes
- Extracts: BUY/SELL, prices, TP, SL
- Falls back to Tesseract OCR if AI fails
```

### 2. Multi-Channel Support

Monitor multiple channels:

```yaml
telegram:
  channels:
    - "premium_signals_fx"
    - "gold_signals_pro"
    - "free_forex_signals"
```

### 3. Symbol Detection

AI automatically detects symbols:
- XAUUSD (Gold)
- EURUSD, GBPUSD (Forex)
- BTCUSD (Crypto)
- US30, NAS100 (Indices)

### 4. Flexible Signal Formats

AI understands messy signals:

✅ Works with:
```
Buy gold 2650-2648 sl 2645 tp 2655/2660
BUY XAUUSD
Entry: 2650.50 - 2648.20
🎯 TP1: 2655 | TP2: 2660
❌ SL: 2645
GOLD 🔥
👉 BUY 2650-2648
SL: 2645 TP: 2655
```

All parsed correctly by AI!

---

## 🔧 Troubleshooting

### Problem: "MT5 initialize failed"

**Solution:**
```cmd
# 1. Check MT5 is open
# 2. Verify it's logged in
# 3. Try connecting manually in MT5 first
# 4. Check path in config.yaml
# 5. Try removing path (uses active MT5)
```

### Problem: "Login failed"

**Solution:**
```
# Check .env file:
MT5_LOGIN=12345678         # Your account number
MT5_PASSWORD=YourPassword  # Exact password
MT5_SERVER=Broker-Demo     # Exact server name from MT5
```

### Problem: "Order failed: 10015 - Invalid filling type"

**Solution:**
✅ **Already handled!** The system auto-detects broker's filling mode.

If still fails:
- Check symbol is available for trading
- Verify market is open
- Check lot size is within limits

### Problem: "DeepSeek API error"

**Solution:**
```
# 1. Check API key in .env is correct
# 2. Verify you have credits at platform.deepseek.com
# 3. Check internet connection
# 4. System will fallback to OCR automatically
```

### Problem: "No signals received"

**Solution:**
```yaml
# In config.yaml, check:
channels:
  - "channel_username"  # NO @ symbol
  - "username_only"     # Correct
  - "@username"         # ❌ WRONG
```

Also:
- Verify you can see channel messages in Telegram
- Check spelling of username
- Look in `logs/mt5_automator.log` for errors

### Problem: "Lot size too large/small"

**Solution:**
```yaml
# Adjust risk in config.yaml:
trading:
  risk_percent: 0.5  # Lower for smaller lots
  # or
  risk_percent: 2.0  # Higher for larger lots
```

---

## 📈 Optimization Tips

### 1. Risk Management

**Conservative (Recommended):**
```yaml
risk_percent: 0.5  # 0.5% per signal
```

**Moderate:**
```yaml
risk_percent: 1.0  # 1% per signal
```

**Aggressive (Not recommended):**
```yaml
risk_percent: 2.0  # 2% per signal
```

### 2. Position Count

**Standard:**
```yaml
num_positions: 3  # 3 orders per signal
```

**Granular:**
```yaml
num_positions: 6  # 6 orders (more entries)
```

### 3. Breakeven Settings

**Tight (Move SL quickly):**
```yaml
breakeven_trigger: "lower_entry"  # After lower entry hit
breakeven_offset: 0.05
```

**Loose (Let it breathe):**
```yaml
breakeven_trigger: "middle_entry"  # After middle entry hit
breakeven_offset: 0.2
```

---

## 🔄 Running 24/7

### Option 1: Windows VPS (Recommended)

1. Rent Windows VPS (Vultr, DigitalOcean, AWS)
2. Install MT5 + Python
3. Copy project to VPS
4. Run with:
   ```cmd
   python main.py
   ```

### Option 2: Local PC

Keep PC running 24/7:

1. Disable sleep mode:
   ```
   Settings → System → Power & Sleep → Never
   ```

2. Run in background:
   ```cmd
   pythonw main.py
   ```

3. Or use Task Scheduler to auto-start

### Option 3: Screen/tmux on VPS

```cmd
# Create session
python main.py

# Detach: Ctrl+B, then D
# Reattach: screen -r
```

---

## 📊 Monitoring

### Check Logs

```cmd
# View recent logs
type logs\mt5_automator.log | more

# Watch live
Get-Content logs\mt5_automator.log -Wait -Tail 20
```

### Check Database

Processed signals stored in:
```
data\signals_db.json
```

### MT5 Terminal

Monitor in MT5:
- **Toolbox** → **Trade** → See active orders
- **History** → See closed trades
- **Experts** → See system logs

---

## 🎓 Example Workflows

### Workflow 1: Conservative Trading

```yaml
# config.yaml
trading:
  risk_percent: 0.5
  num_positions: 3
  
mode:
  dry_run: false
```

**Result:** Small, safe positions

### Workflow 2: High Volume

```yaml
# config.yaml
telegram:
  channels:
    - "channel1"
    - "channel2"
    - "channel3"
    
trading:
  risk_percent: 0.3  # Lower risk per signal
  num_positions: 3
```

**Result:** More signals, diversified risk

### Workflow 3: Testing New Channel

```yaml
# config.yaml
mode:
  dry_run: true  # Safe mode
  
telegram:
  channels:
    - "new_untested_channel"
```

**Result:** See signals without trading

---

## ✅ Final Checklist

Before going live:

- [ ] Tested on DEMO account for 24+ hours
- [ ] Verified all signals parsed correctly
- [ ] Checked lot sizes are appropriate
- [ ] Confirmed orders placed correctly in MT5
- [ ] Reviewed logs for errors
- [ ] Set risk conservatively (0.5-1%)
- [ ] Configured broker trading limits
- [ ] Backed up configuration files
- [ ] Monitoring system is in place
- [ ] Know how to stop system (Ctrl+C)

---

## 📞 Support & Updates

- **GitHub:** https://github.com/Mukhammad-develop/mt5-automator
- **Issues:** Report bugs on GitHub Issues
- **Updates:** `git pull` to get latest version

---

## 🚀 You're Ready!

```cmd
# Start trading bot
python main.py
```

**The system will:**
- ✅ Monitor Telegram 24/7
- ✅ Parse signals with AI
- ✅ Calculate risk automatically
- ✅ Execute trades on MT5
- ✅ Manage positions
- ✅ Protect profits

**Happy Trading!** 📈💰

---

**⚠️ Disclaimer:** Trading involves risk. This software is provided as-is. Always test on demo accounts first. Never risk more than you can afford to lose.

