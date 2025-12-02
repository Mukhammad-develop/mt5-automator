# Quick Start Guide

Get MT5 Trading Automator running in 10 minutes!

## Prerequisites

- Python 3.9+
- MetaTrader 5 installed
- Telegram account
- Tesseract OCR installed

## 5-Step Setup

### Step 1: Install Dependencies (2 min)

**On Windows (with MT5):**
```bash
pip install -r requirements-windows.txt
```

**On macOS/Linux (development only):**
```bash
pip install -r requirements-dev.txt
```

**Note**: MetaTrader5 only works on Windows. For macOS development, see `MACOS_DEVELOPMENT.md`

### Step 2: Get Telegram API Credentials (3 min)

1. Visit: https://my.telegram.org/auth
2. Login with your phone
3. Click "API development tools"
4. Create app, copy `api_id` and `api_hash`

### Step 3: Configure Environment (2 min)

Create `.env` file:

```bash
# Copy example
cp config/.env.example .env

# Edit with your details
nano .env
```

Add your credentials:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890
TELEGRAM_PHONE=+1234567890
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_broker_server
```

### Step 4: Update Channel List (1 min)

Edit `config/config.yaml`:

```yaml
telegram:
  channels:
    - "your_signal_channel_username"
```

### Step 5: Run! (2 min)

```bash
python main.py
```

On first run:
- Enter Telegram verification code when prompted
- System will create session file
- Check connection to MT5

## First Signal Test

Send a test signal to yourself:

```
BUY XAUUSD 2650 - 2648
SL: 2645
TP1: 2655
TP2: 2660
```

Check logs:
```bash
tail -f logs/mt5_automator.log
```

## Safety Tips

✅ **DO:**
- Test with demo account first
- Start with 0.1% risk
- Monitor for 24 hours before going live
- Keep logs backed up

❌ **DON'T:**
- Use real account without testing
- Set risk > 2% per signal
- Leave running without monitoring
- Ignore error messages

## Next Steps

1. **Review Settings**: Check `config/config.yaml`
2. **Test Components**: Run `python tests/run_tests.py`
3. **Monitor Logs**: Watch for errors
4. **Adjust Risk**: Start conservative
5. **Read Full Docs**: See README.md

## Common Issues

**Can't connect to Telegram?**
- Check API credentials
- Verify phone number format (+country code)

**MT5 not connecting?**
- Ensure MT5 is running
- Check login credentials
- Verify server name

**No signals received?**
- Check channel usernames
- Verify you have access to channels
- Look for errors in logs

## Need Help?

1. Check logs: `logs/mt5_automator.log`
2. Run tests: `python tests/run_tests.py`
3. Review README.md troubleshooting section
4. Check MT5 terminal for errors

---

**Remember**: Always test with demo account first! 🛡️

