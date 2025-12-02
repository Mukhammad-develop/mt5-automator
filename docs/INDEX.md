# MT5 Trading Automator Documentation

## Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 10 minutes
- **[../README.md](../README.md)** - Full system documentation

## Platform Guides

- **[MACOS_DEVELOPMENT.md](MACOS_DEVELOPMENT.md)** - Development on macOS/Linux
- **[MACOS_SETUP_COMPLETE.md](MACOS_SETUP_COMPLETE.md)** - macOS setup summary
- **[ISSUE_RESOLVED.md](ISSUE_RESOLVED.md)** - MetaTrader5 installation issue fix

## Reference

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical specifications
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and roadmap
- **[INSTALLATION_COMPLETE.txt](INSTALLATION_COMPLETE.txt)** - Installation checklist

## Quick Links

### Configuration
- `../config/config.yaml` - Main configuration file
- `../.env` - Environment variables (create from `.env.example`)

### Source Code
- `../src/` - All source modules
- `../main.py` - Entry point

### Testing
- `../tests/` - Test suite
- Run: `python3 tests/run_tests.py`

## Installation Commands

**macOS/Linux (Development):**
```bash
pip install -r requirements-dev.txt
```

**Windows (Production):**
```bash
pip install -r requirements-windows.txt
```

## Support

1. Check logs: `logs/mt5_automator.log`
2. Run tests: `python3 tests/run_tests.py`
3. Review troubleshooting in README.md

