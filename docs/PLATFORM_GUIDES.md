# Platform-Specific Guides

Detailed setup and usage for macOS and Windows.

---

## 🍎 macOS Development Guide

### Purpose
Develop and test the system on macOS without MT5, then deploy to Windows for production.

### What Works on macOS
- ✅ Telegram integration
- ✅ AI signal parsing (text + images)
- ✅ OCR processing
- ✅ Signal validation
- ✅ Risk calculations
- ✅ Dry-run mode (shows commands)
- ✅ All tests

### What Doesn't Work
- ❌ MT5 connection (Windows only)
- ❌ Real trading

### Development Workflow

1. **Develop on macOS**
   ```bash
   pip3 install -r requirements-dev.txt
   python3 main.py  # Dry-run mode
   ```

2. **Test Components**
   ```bash
   python3 src/telegram_monitor.py
   python3 src/signal_parser.py
   python3 tests/run_tests.py
   ```

3. **Deploy to Windows**
   ```bash
   git push origin main
   # On Windows: git pull, configure, run
   ```

### Dry-Run Mode

See exactly what would execute on Windows:

```bash
# macOS shows:
🧪 DRY RUN - PLACE_ORDER
  ticket: 1000
  type: BUY LIMIT
  symbol: XAUUSD
  volume: 0.33
  entry_price: 2650.5
  stop_loss: 2645.0
  take_profit: 2655.0

# Same commands execute for real on Windows!
```

### Testing Strategy

**On macOS:**
- Test signal parsing (✅)
- Test AI with real channels (✅)
- Verify risk calculations (✅)
- Review dry-run commands (✅)

**On Windows:**
- Demo account testing (✅)
- Verify orders execute correctly (✅)
- 24-hour stability test (✅)
- Go live (✅)

### IDE Setup

**VS Code:**
```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python3",
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.envFile": "${workspaceFolder}/.env"
}
```

**PyCharm:**
- Mark `src/` as Sources Root
- Add `.env` file to Environment Variables
- Set Python 3.9+ interpreter

### Useful Commands

```bash
# Run with debug logging
python3 main.py --log-level DEBUG

# Test specific component
PYTHONPATH=. python3 src/signal_parser.py

# Run tests
python3 tests/run_tests.py

# Check setup
python3 setup.py
```

---

## 🪟 Windows Production Guide

### Purpose
Run actual MT5 trading in production.

### Prerequisites

1. **MetaTrader 5**
   - Downloaded from broker
   - Logged in and running
   - Automated trading enabled

2. **Python 3.9+**
   - Download from python.org
   - Add to PATH during installation

3. **Tesseract OCR**
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location

### Installation

```cmd
cd C:\mt5_automator
pip install -r requirements-windows.txt
```

### Configuration

**1. MT5 Path**

Find your MT5 installation:
```
C:\Program Files\MetaTrader 5\terminal64.exe
```

Or leave empty to use active MT5 instance.

**2. Environment Variables**

Create `.env`:
```
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo  # or Real
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
DEEPSEEK_API_KEY=sk-your-key
```

**3. Production Mode**

Edit `config/config.yaml`:
```yaml
mode:
  dry_run: false  # PRODUCTION
```

### Testing Checklist

**Before Going Live:**

- [ ] Tested on demo account
- [ ] Verified order placement
- [ ] Checked TP/SL levels
- [ ] Tested breakeven logic
- [ ] Verified TP2 protection
- [ ] Monitored for 24+ hours
- [ ] Reviewed all logs
- [ ] Set risk conservatively (0.5-1%)

### Running as Service

**Option 1: Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program
   - Program: `C:\Python\python.exe`
   - Arguments: `C:\mt5_automator\main.py`
   - Start in: `C:\mt5_automator`

**Option 2: NSSM (Service Manager)**

```cmd
nssm install MT5Automator
# Set path to python.exe and main.py
nssm start MT5Automator
```

### Monitoring

**Real-time Logs:**
```cmd
tail -f logs/mt5_automator.log
```

Or use:
- PowerShell: `Get-Content logs/mt5_automator.log -Wait`
- Notepad++: File → Reload (F5)

**Key Metrics:**
- Signals received
- Orders placed
- TP/SL hits
- Errors/warnings

### Remote Access

**TeamViewer/AnyDesk:**
- Monitor from anywhere
- Check MT5 terminal
- Review logs

**RDP (Windows VPS):**
```
mstsc /v:your-vps-ip
```

### Backup Strategy

**Daily:**
- Logs to cloud storage
- Config files backup

**Weekly:**
- Full system backup
- Trade history export

### Performance Optimization

**1. Resource Usage**
- CPU: <10% idle, <30% active
- RAM: ~200-500 MB
- Disk: Minimal

**2. Network**
- Stable internet required
- Low latency to broker
- Telegram API access

**3. MT5 Settings**
- Enable automated trading
- Disable chart updates (faster)
- Minimize indicator load

### Troubleshooting Windows

**Issue: MT5 not connecting**
```cmd
# Test manually
python src\mt5_engine.py
```

**Issue: Orders not placing**
- Check broker allows automated trading
- Verify account not restricted
- Check margin requirements
- Review MT5 journal

**Issue: High CPU usage**
- Reduce logging level to WARNING
- Disable AI if not needed
- Check for infinite loops

---

## 🔄 Cross-Platform Workflow

### Development Cycle

```
┌─────────────┐
│   macOS     │  Develop & Test
│  (Dry-run)  │  with dry-run mode
└──────┬──────┘
       │ git push
       ↓
┌─────────────┐
│   Windows   │  Production
│  (Real MT5) │  with live trading
└─────────────┘
```

### Best Practices

1. **Always develop on macOS first**
   - Test signal parsing
   - Verify AI works
   - Check all logic

2. **Deploy to Windows for production**
   - Demo account first
   - Monitor carefully
   - Go live gradually

3. **Keep code in sync**
   ```bash
   # macOS
   git push origin main
   
   # Windows
   git pull origin main
   ```

### Configuration Management

**Shared (Both Platforms):**
- Telegram channels
- Risk settings
- Trading parameters
- AI settings

**Platform-Specific:**
```yaml
# macOS config.yaml
mode:
  dry_run: true
mt5:
  path: ""  # Not needed

# Windows config.yaml
mode:
  dry_run: false
mt5:
  path: "C:/Program Files/MetaTrader 5/terminal64.exe"
```

---

## 📊 Platform Comparison

| Feature | macOS | Windows |
|---------|-------|---------|
| **Development** | ✅ Excellent | ⚠️ Possible |
| **Testing** | ✅ Full (dry-run) | ✅ Full (demo) |
| **Production** | ❌ Not possible | ✅ Full support |
| **AI Parsing** | ✅ Yes | ✅ Yes |
| **OCR** | ✅ Yes | ✅ Yes |
| **Dry-run** | ✅ Default | ✅ Optional |
| **MT5 Trading** | ❌ No | ✅ Yes |
| **Setup Time** | 15 min | 15 min |
| **Cost** | MacBook | VPS ($10-30/mo) |

---

## 🎯 Recommendations

### For Developers
- **Primary:** macOS for development
- **Secondary:** Windows VPS for production
- **Workflow:** Develop → Test → Deploy

### For Traders
- **Option 1:** Windows PC/Laptop
- **Option 2:** Windows VPS (reliable, 24/7)
- **Not Recommended:** macOS only (no trading)

### For Both
- Use Git for version control
- Keep configs separate per platform
- Test thoroughly before live trading
- Monitor logs regularly

---

## 🆘 Platform-Specific Support

### macOS
- **Issue:** Can't trade
- **Answer:** Expected! Deploy to Windows

### Windows
- **Issue:** Deployment complexity
- **Answer:** Use Task Scheduler or NSSM

### Both
- **Issue:** AI costs too high
- **Answer:** Disable AI, use regex parser

---

## 📚 Additional Resources

- **macOS Setup:** See QUICKSTART.md
- **Windows Setup:** See QUICKSTART.md
- **AI Features:** See AI_INTEGRATION.md
- **Full Docs:** See README.md

**Choose your platform and get started!** 🚀

