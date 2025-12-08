# MT5 Trading Automator - Documentation Index

Complete documentation for the MT5 Trading Automator system.

---

## 🚀 Getting Started

### [WINDOWS_QUICKSTART.md](WINDOWS_QUICKSTART.md) ⭐ **NEW!**
**Windows users start here!** Complete 20-minute production setup.
- ✅ Full MT5 + DeepSeek AI integration
- ✅ Step-by-step with screenshots
- ✅ Dry-run testing → Live trading
- ✅ Safety checklists and troubleshooting

### [QUICKSTART.md](QUICKSTART.md)
General setup guide for both platforms.
- macOS: Testing & development (dry-run mode)
- Windows: Alternative shorter guide

---

## 📖 Core Documentation

### [AI_INTEGRATION.md](AI_INTEGRATION.md)
DeepSeek AI features for intelligent signal processing.
- AI text parsing (handles any format)
- AI vision (reads images directly)
- Better than OCR for complex signals

### [PLATFORM_GUIDES.md](PLATFORM_GUIDES.md)
Detailed platform-specific guides.
- macOS development workflow
- Windows production setup
- Cross-platform best practices

### [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
Technical specifications and architecture.
- System overview
- Component details
- Performance characteristics

### [CHANGELOG.md](CHANGELOG.md)
Version history and roadmap.
- Current version features
- Planned enhancements
- Future development

---

## 🛠️ Setup Guides (Text Files)

### [START_HERE.txt](START_HERE.txt) ⚡ **Ultra-Simple**
3-step quickstart for non-technical users.
- Minimal instructions
- Copy-paste commands
- Windows-focused

### [SIMPLE_SETUP.txt](SIMPLE_SETUP.txt)
Super simple guide with Q&A.
- One-file config (config.env)
- Common questions answered
- Beginner-friendly

### [WINDOWS_SETUP.txt](WINDOWS_SETUP.txt)
Detailed Windows installation.
- Step-by-step setup
- All prerequisites
- Troubleshooting section

---

## 🐛 Fix & Troubleshooting Guides

### [AUTO_SYMBOL_DETECTION.txt](AUTO_SYMBOL_DETECTION.txt)
How automatic symbol resolution works.
- Detects broker-specific symbols
- Works for all pairs automatically
- XAUUSD → XAUUSD+, etc.

### [FIX_XAUUSD_PLUS.txt](FIX_XAUUSD_PLUS.txt)
Manual symbol mapping guide.
- For custom broker symbols
- How to configure SYMBOL_MAPPING
- Examples for different brokers

### [BREAKEVEN_FIX.txt](BREAKEVEN_FIX.txt)
Breakeven logic explained.
- Why it was moving SL immediately
- How the fix works
- Configuration options

---

## 📋 Quick Reference

### Installation Commands

**macOS (Testing):**
```bash
pip3 install -r requirements-dev.txt
python3 main.py  # Dry-run mode
```

**Windows (Production):**
```cmd
pip install -r requirements-windows.txt
python main.py  # Real trading
```

### Configuration Files

- `../config.env` - ONE config file for everything (recommended)
- `../config/config.yaml` - Advanced YAML config (optional)

### Key Settings

```yaml
# Enable/disable features
ai:
  enabled: true  # AI parsing
  use_vision: true  # AI for images

mode:
  dry_run: true  # macOS: true, Windows: false

trading:
  risk_percent: 1.0  # Risk per signal
  num_positions: 3  # Positions per signal
```

---

## 🎯 By Use Case

### I want to test on macOS
→ [QUICKSTART.md](QUICKSTART.md) → macOS section

### I want to deploy to Windows for production
→ [WINDOWS_QUICKSTART.md](WINDOWS_QUICKSTART.md) ⭐ **RECOMMENDED**

### I want to understand AI features
→ [AI_INTEGRATION.md](AI_INTEGRATION.md)

### I need platform-specific help
→ [PLATFORM_GUIDES.md](PLATFORM_GUIDES.md)

### I want technical details
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🔧 Component Documentation

### Source Code
- `../src/telegram_monitor.py` - Telegram integration
- `../src/ai_signal_parser.py` - AI parsing (text + vision)
- `../src/ocr_processor.py` - Tesseract OCR fallback
- `../src/signal_parser.py` - Regex parser fallback
- `../src/mt5_engine.py` - MT5 trading (Windows)
- `../src/dry_run_mode.py` - Testing mode (macOS)
- `../src/risk_manager.py` - Lot size calculation
- `../src/position_tracker.py` - Position monitoring
- `../src/tp_protection.py` - TP2 protection system

### Testing
- `../tests/test_signal_parser.py` - Unit tests
- `../tests/test_integration.py` - Integration tests
- `../tests/run_tests.py` - Test runner

---

## 🆘 Troubleshooting

### Common Issues

**macOS: "MetaTrader5 not found"**
- Expected! Use `requirements-dev.txt`
- MT5 only works on Windows

**Windows: "MT5 connection failed"**
- Check MT5 is running
- Verify credentials in `.env`
- Test with: `python src\mt5_engine.py`

**Both: "AI parsing failed"**
- Check `DEEPSEEK_API_KEY` in `.env`
- System falls back to regex automatically

**Both: "No signals received"**
- Verify channel usernames (no @ symbol)
- Check logs: `logs/mt5_automator.log`
- Ensure you have access to channels

---

## 📚 External Resources

### Get API Keys
- **Telegram:** https://my.telegram.org/auth
- **DeepSeek:** https://platform.deepseek.com

### Download Software
- **Python:** https://www.python.org/downloads/
- **MT5:** From your broker
- **Tesseract (Windows):** https://github.com/UB-Mannheim/tesseract/wiki

### Helpful Links
- **Full README:** [../README.md](../README.md)
- **GitHub Repo:** https://github.com/Mukhammad-develop/mt5-automator

---

## 📊 Documentation Structure

```
docs/
├── INDEX.md (this file)          # Documentation index
│
├── 🚀 Getting Started (Markdown)
│   ├── WINDOWS_QUICKSTART.md ⭐  # Windows production (RECOMMENDED)
│   └── QUICKSTART.md             # General setup (both platforms)
│
├── 📖 Core Documentation (Markdown)
│   ├── AI_INTEGRATION.md         # AI features & vision
│   ├── PLATFORM_GUIDES.md        # Platform-specific details
│   ├── PROJECT_SUMMARY.md        # Technical specifications
│   └── CHANGELOG.md              # Version history
│
├── 🛠️ Setup Guides (Text)
│   ├── START_HERE.txt ⚡         # Ultra-simple 3-step guide
│   ├── SIMPLE_SETUP.txt          # Simple with Q&A
│   └── WINDOWS_SETUP.txt         # Detailed Windows setup
│
└── 🐛 Fix Guides (Text)
    ├── AUTO_SYMBOL_DETECTION.txt # Automatic symbol resolver
    ├── FIX_XAUUSD_PLUS.txt       # Manual symbol mapping
    └── BREAKEVEN_FIX.txt         # Breakeven logic fix
```

---

## 🎓 Learning Path

### Beginner
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Follow macOS or Windows setup
3. Test with demo signals

### Intermediate
1. Explore [AI_INTEGRATION.md](AI_INTEGRATION.md)
2. Understand [PLATFORM_GUIDES.md](PLATFORM_GUIDES.md)
3. Customize configuration

### Advanced
1. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Study source code
3. Extend functionality

---

## 🔄 Updates

This documentation is for **Version 1.0.0** (December 2025).

See [CHANGELOG.md](CHANGELOG.md) for version history and planned features.

---

## ✅ Checklist

Before you start:
- [ ] Read QUICKSTART.md
- [ ] Choose platform (macOS or Windows)
- [ ] Get API keys
- [ ] Install dependencies
- [ ] Configure .env
- [ ] Test with demo
- [ ] Monitor logs

---

**Ready to start?** → [QUICKSTART.md](QUICKSTART.md) 🚀
