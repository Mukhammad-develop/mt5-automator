# MT5 Trading Automator - Documentation Index

Complete documentation for the MT5 Trading Automator system.

---

## 🚀 Getting Started

### [QUICKSTART.md](QUICKSTART.md)
**Start here!** 15-minute setup guide for both macOS and Windows.
- macOS: Testing & development (dry-run mode)
- Windows: Production trading (real MT5)

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

- `../config/config.yaml` - Main configuration
- `../.env` - API keys and credentials (create from .env.example)

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

### I want to deploy to Windows
→ [QUICKSTART.md](QUICKSTART.md) → Windows section

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
├── QUICKSTART.md                 # 15-min setup (both platforms)
├── AI_INTEGRATION.md             # AI features & vision
├── PLATFORM_GUIDES.md            # Platform-specific details
├── PROJECT_SUMMARY.md            # Technical specifications
└── CHANGELOG.md                  # Version history
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
