# Testing on macOS with Dry-Run Mode

## Overview

You can now **fully test the system on macOS** without MT5. The system will:
1. ✅ Read Telegram signals
2. ✅ Use DeepSeek AI to parse complex signals (emojis, stickers, markdown)
3. ✅ Calculate lot sizes
4. ✅ **SHOW what MT5 commands WOULD be executed** (without actually trading)

Your client will run the same code on Windows with `dry_run: false` for real trading.

## Setup

### 1. Install Dependencies

```bash
pip3 install -r requirements-dev.txt
```

### 2. Get DeepSeek API Key

1. Visit: https://platform.deepseek.com
2. Create account
3. Get API key
4. Add to `.env`:

```bash
DEEPSEEK_API_KEY=sk-your-key-here
```

### 3. Configure for Testing

Edit `config/config.yaml`:

```yaml
# Enable AI parsing (handles complex Telegram formats)
ai:
  enabled: true
  api_key: "${DEEPSEEK_API_KEY}"
  fallback_to_regex: true

# Enable dry-run mode (for macOS testing)
mode:
  dry_run: true  # Shows commands without executing
```

### 4. Add Telegram Credentials

```bash
# .env file
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
DEEPSEEK_API_KEY=sk-your-key-here
```

## How It Works

### Dry-Run Mode Output

When a signal arrives, you'll see:

```
╔══════════════════════════════════════════════════════════════════════
║ 🧪 DRY RUN - PLACE_ORDER
╠──────────────────────────────────────────────────────────────────────
║ Target: Position 1
║ Time: 2025-12-02 14:30:45
    ticket: 1000
    type: BUY LIMIT
    symbol: XAUUSD
    volume: 0.33
    entry_price: 2650.5
    stop_loss: 2645.0
    take_profit: 2655.0
    position_num: 1
    signal_id: 59f25ae87e7d
    comment: 59f25ae87e7d_pos1
╚══════════════════════════════════════════════════════════════════════
```

You'll see ALL actions that would be executed:
- ✅ Account queries
- ✅ Price checks
- ✅ Order placements
- ✅ Position modifications
- ✅ Stop loss adjustments
- ✅ Order cancellations

### AI Signal Parsing

The AI parser handles **ANY format**, including:

```
🔥 𝐆𝐎𝐋𝐃 𝐒𝐈𝐆𝐍𝐀𝐋 🔥

➡️ LONG XAUUSD
📍 Zone: 2648.50 - 2650.20
🎯 Targets:
   TP1: 2655.00
   TP2: 2660.50
🛑 Stop: 2645.00
```

The AI will:
1. Ignore emojis and formatting
2. Understand "LONG" = BUY, "Zone" = Entry
3. Extract all numbers correctly
4. Return structured data

## Running Tests

### Test AI Parser

```bash
python3 src/ai_signal_parser.py
```

### Test Dry-Run Mode

```bash
python3 src/dry_run_mode.py
```

### Run Full System

```bash
python3 main.py
```

You'll see:
- Telegram connection
- Signal received
- AI parsing
- Risk calculation
- **Detailed dry-run commands** (what would be executed on Windows)

## For Your Client (Windows Production)

### Step 1: Same Code

Your client uses the **exact same code**.

### Step 2: Configuration Change

On Windows, change `config/config.yaml`:

```yaml
mode:
  dry_run: false  # PRODUCTION MODE - Real trading
```

### Step 3: MT5 Credentials

Add to `.env`:

```bash
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=broker_server_name
```

### Step 4: Run

```bash
# On Windows with MT5 installed
pip install -r requirements-windows.txt
python main.py
```

Now the **same commands** you saw in dry-run mode will execute for real!

## Advantages

### ✅ For You (macOS Testing)
- Test complete signal flow
- Verify AI parsing works with real Telegram channels
- See exact MT5 commands that will execute
- No need for Windows VM
- Safe testing with no trading risk

### ✅ For Your Client (Windows Production)
- Same proven code
- Just flip `dry_run: false`
- Real trading with verified logic

## Example Workflow

### 1. Test on macOS

```bash
# Terminal 1: Run the system
python3 main.py

# You'll see:
# ✅ Connected to Telegram
# ✅ Monitoring channels...
# ✅ New signal received
# ✅ AI parsing...
# ✅ Signal parsed: BUY XAUUSD 2650-2648
# 🧪 DRY RUN - PLACE_ORDER (Position 1)
# 🧪 DRY RUN - PLACE_ORDER (Position 2)
# 🧪 DRY RUN - PLACE_ORDER (Position 3)
```

### 2. Verify Commands Look Correct

Check the dry-run output:
- Entry prices correct?
- Stop losses correct?
- Take profits correct?
- Lot sizes reasonable?

### 3. Deploy to Windows

```bash
# On Windows
git clone <your-repo>
cd mt5_automator

# Change config
# mode:
#   dry_run: false

# Run
python main.py
```

Now it trades for real!

## Configuration Reference

```yaml
# AI Parsing (handles complex formats)
ai:
  enabled: true              # Use DeepSeek AI
  api_key: "${DEEPSEEK_API_KEY}"
  fallback_to_regex: true    # Use regex if AI fails

# System Mode
mode:
  dry_run: true   # macOS: true (testing)
                  # Windows: false (production)

# Trading (used in both modes)
trading:
  risk_percent: 1.0
  num_positions: 3
```

## Troubleshooting

### Issue: No dry-run output

**Check**: Is `mode.dry_run: true` in config?

### Issue: AI parsing fails

**Check**: Is `DEEPSEEK_API_KEY` set in `.env`?  
**Fallback**: System uses regex parser automatically

### Issue: Want to test regex parser

**Solution**: Set `ai.enabled: false` in config

## Summary

| Feature | macOS (Testing) | Windows (Production) |
|---------|----------------|---------------------|
| Telegram | ✅ Works | ✅ Works |
| AI Parsing | ✅ Works | ✅ Works |
| Signal Validation | ✅ Works | ✅ Works |
| Risk Calculation | ✅ Works | ✅ Works |
| **MT5 Commands** | **🧪 Logged** | **✅ Executed** |

Perfect setup for safe testing! 🚀

