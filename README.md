# MT5 Trading Automator

A fully automated MetaTrader 5 trading system that reads trading signals from Telegram channels (text + images via OCR), interprets them, and executes trades with complete TP/SL management and risk control.

## Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](docs/QUICKSTART.md) | Get started in 10 minutes |
| [MACOS_DEVELOPMENT.md](docs/MACOS_DEVELOPMENT.md) | Development on macOS/Linux |
| [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | Technical specifications |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history |

## Features

### 1. Telegram Signal Reader
- Monitors multiple Telegram channels simultaneously
- Processes both text and image messages
- Advanced OCR with image preprocessing for accurate signal extraction
- Automatic reconnection and error handling

### 2. Smart Signal Interpretation
- Parses BUY/SELL signals with entry ranges
- Extracts multiple TP and SL levels
- Auto-calculates middle entry level
- Validates signals before execution
- Handles various signal formats

### 3. Automated MT5 Trading
- Secure credential handling
- Places multiple positions (configurable: 3, 6, 9, etc.)
- Smart order type selection (LIMIT vs MARKET)
- Risk-based lot calculation
- Automatic TP/SL assignment

### 4. Full TP/SL Automation
- Position-specific TP/SL management
- Breakeven logic (moves SL when price reaches target)
- Automatic position tracking
- Real-time monitoring

### 5. TP2 Protection System
- Cancels pending orders when TP2 is hit
- Prevents new entries after target reached
- Allows running positions to continue

### 6. Stability & Logging
- Comprehensive logging system
- Automatic reconnection
- Error recovery
- Detailed trade history

## System Requirements

- **Python**: 3.9 or higher
- **Operating System**: 
  - Windows 10/11 (recommended for MT5)
  - Linux (requires Wine or remote MT5 connection)
- **MetaTrader 5**: Installed and configured
- **Tesseract OCR**: For image processing

## Installation

### 1. Clone or Download

```bash
cd /path/to/installation
```

### 2. Install Python Dependencies

**On Windows (with MT5):**
```bash
pip install -r requirements-windows.txt
```

**On macOS/Linux (for development/testing without MT5):**
```bash
pip install -r requirements-dev.txt
```

**Note**: The `MetaTrader5` Python package only works on Windows. For development on macOS/Linux, use the mock engine (see Development section below).

### 3. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location or update `config/config.yaml` with custom path

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 4. Install MetaTrader 5

- Download from: https://www.metatrader5.com/
- Install and login to your broker account
- Note the installation path for configuration

## Configuration

### 1. Telegram API Setup

1. Visit https://my.telegram.org/auth
2. Login with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 2. Create Environment File

Copy the example environment file:

```bash
cp config/.env.example .env
```

Edit `.env` with your credentials:

```bash
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# MT5
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

### 3. Configure Settings

Edit `config/config.yaml`:

```yaml
telegram:
  channels:
    - "channel_username_1"
    - "channel_username_2"

trading:
  risk_percent: 1.0          # Risk per signal (1%)
  num_positions: 3           # Number of positions per signal
  default_symbol: "XAUUSD"   # Default trading symbol
  
mt5:
  path: "C:/Program Files/MetaTrader 5/terminal64.exe"  # Windows
  # path: "/path/to/mt5/terminal"  # Linux
```

## Usage

### Running the System

**Standard Mode:**
```bash
python main.py
```

**With Docker:**
```bash
cd docker
docker-compose up -d
```

**View Logs:**
```bash
tail -f logs/mt5_automator.log
```

### First Run

On first run, you'll need to:

1. Authenticate with Telegram (enter code sent to your phone)
2. Verify MT5 connection
3. Check that channels are accessible

The system will create a session file for Telegram authentication.

## Signal Format

The system supports various signal formats. Here are examples:

### Format 1: Standard
```
BUY XAUUSD 2650.50 - 2648.20
SL1: 2645.00
SL2: 2643.50
SL3: 2642.00
TP1: 2655.00
TP2: 2660.00
```

### Format 2: Compact
```
SELL 2655-2657
SL: 2662
TP1: 2648
TP2: 2640
```

### Format 3: Detailed
```
BUY GOLD
Entry: 2645 - 2643
Stop Loss 1: 2640
Stop Loss 2: 2638
Take Profit 1: 2650
Take Profit 2: 2655
```

The parser is flexible and handles variations in formatting.

## Trading Logic

### Position Distribution

For 3 positions (default):
- **Position 1**: Entry at upper level, TP1, SL1
- **Position 2**: Entry at middle level, TP2, SL2
- **Position 3**: Entry at lower level, TP2, SL3

### Order Types

- **BUY Signal**:
  - If current price < entry → BUY LIMIT
  - If current price ≥ entry → BUY MARKET

- **SELL Signal**:
  - If current price > entry → SELL LIMIT
  - If current price ≤ entry → SELL MARKET

### Risk Management

- Risk is calculated per signal (e.g., 1% of account)
- Risk is distributed equally across all positions
- Lot size is calculated based on SL distance
- Automatic validation of margin requirements

### Breakeven Logic

When price reaches the trigger point (middle entry + offset):
- Stop loss moves to entry price (breakeven)
- Protects against losses after market moves in favor

### TP2 Protection

When TP2 is hit:
1. All pending orders are cancelled
2. New orders from the same signal are blocked
3. Existing positions continue until closed

## Architecture

```
┌─────────────────┐
│  Telegram API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Telegram Monitor│──────▶│ OCR Processor│
└────────┬────────┘      └──────┬───────┘
         │                      │
         └──────────┬───────────┘
                    ▼
            ┌───────────────┐
            │ Signal Parser │
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │ Risk Manager  │
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │  MT5 Engine   │
            └───────┬───────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐   ┌──────────────┐
│Position Tracker │   │TP2 Protection│
└─────────────────┘   └──────────────┘
```

## Logging

Logs are stored in `logs/mt5_automator.log` with rotation.

**Log Levels:**
- **INFO**: Normal operations, signals received, trades placed
- **WARNING**: Invalid signals, TP2 protection activated
- **ERROR**: Connection failures, trade rejections
- **DEBUG**: Detailed processing steps (enable in config)

## Testing

### Test Individual Components

**Test Telegram Connection:**
```bash
python src/telegram_monitor.py
```

**Test MT5 Connection:**
```bash
python src/mt5_engine.py
```

**Test Signal Parser:**
```bash
python src/signal_parser.py
```

**Test OCR Processor:**
```bash
python src/ocr_processor.py
```

### Demo Account Testing

**Strongly recommended**: Test with MT5 demo account first!

1. Open demo account with your broker
2. Configure credentials in `.env`
3. Run system with small risk (0.1%)
4. Monitor for 24-48 hours

## Troubleshooting

### Telegram Connection Issues

**Error: "Invalid API ID/Hash"**
- Verify credentials at https://my.telegram.org
- Check for extra spaces in `.env` file

**Error: "Phone number required"**
- Make sure phone number includes country code
- Format: +1234567890

### MT5 Connection Issues

**Error: "MT5 initialize failed"**
- Verify MT5 is installed and running
- Check path in config.yaml
- Try running without path (uses active MT5 instance)

**Error: "Login failed"**
- Verify credentials are correct
- Check server name matches broker
- Ensure account is not locked

### OCR Issues

**Poor OCR Accuracy:**
- Ensure images are clear and high resolution
- Adjust preprocessing settings in config
- Check tesseract is installed correctly

### Trading Issues

**Orders Not Placing:**
- Check account margin
- Verify symbol is available
- Check broker allows automated trading
- Review MT5 terminal for error messages

## Security Considerations

1. **Never commit `.env` file** - contains sensitive credentials
2. **Use strong passwords** for MT5 account
3. **Enable 2FA** on Telegram if possible
4. **Monitor logs** regularly for unusual activity
5. **Set appropriate risk limits** in configuration
6. **Use demo account** for initial testing

## Advanced Configuration

### Multiple Position Configurations

To use 6 positions instead of 3, update `config.yaml`:

```yaml
trading:
  num_positions: 6
```

Position distribution:
- 1-2: Upper entry
- 3-4: Middle entry
- 5-6: Lower entry

### Custom OCR Settings

```yaml
ocr:
  preprocessing:
    resize_factor: 3.0      # Increase for small images
    contrast_boost: true
    denoise: true
    sharpen: true
```

### Monitoring Multiple Accounts

Run multiple instances with different config files:

```bash
python main.py --config config/account1.yaml
python main.py --config config/account2.yaml
```

## Deployment Options

### Option 1: Windows VPS (Recommended)

- Most compatible with MT5
- Run directly with Python
- Use Task Scheduler for auto-start

### Option 2: Linux VPS with Wine

- More cost-effective
- Requires MT5 running under Wine
- May have compatibility issues

### Option 3: Hybrid (Linux Container + Windows MT5)

- Run Python application in Docker on Linux
- Connect to MT5 on Windows via network
- Requires custom bridge implementation

### PaaS Deployment

For Railway, Render, Heroku:
1. Use Dockerfile provided
2. Set environment variables in platform
3. Note: Requires remote MT5 connection

## Maintenance

### Regular Tasks

- **Daily**: Check logs for errors
- **Weekly**: Review trade performance
- **Monthly**: Update dependencies
- **As needed**: Adjust risk parameters

### Updates

```bash
# Backup configuration
cp config/config.yaml config/config.yaml.backup

# Update code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Support & Contribution

### Getting Help

1. Check logs in `logs/mt5_automator.log`
2. Review this README
3. Test individual components
4. Check MT5 terminal for errors

### Contributing

Contributions are welcome! Areas for improvement:
- Additional signal format parsers
- Enhanced OCR preprocessing
- Web dashboard for monitoring
- Additional risk management strategies
- Support for more brokers/platforms

## Disclaimer

**IMPORTANT**: 
- This software is for educational purposes
- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Always test thoroughly with demo account first
- The authors are not responsible for any trading losses
- Use at your own risk

## License

This project is provided as-is for educational and personal use.

---

**Version**: 1.0.0  
**Last Updated**: December 2025

For questions or issues, please review the logs and troubleshooting section above.

