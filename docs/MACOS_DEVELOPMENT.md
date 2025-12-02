# Development on macOS/Linux

Since MetaTrader5 only runs on Windows, you can't install the `MetaTrader5` Python package on macOS or Linux. However, you can still develop and test most of the system using the mock engine.

## Quick Setup for macOS

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

This skips the MetaTrader5 package which is Windows-only.

### 2. Install Tesseract OCR

```bash
brew install tesseract
```

### 3. Configure Environment

```bash
cp config/.env.example .env
# Edit .env with your Telegram credentials
# You can leave MT5 credentials empty for now
```

### 4. Test Components

You can test all components except MT5 integration:

**Test Telegram Monitor:**
```bash
python src/telegram_monitor.py
```

**Test Signal Parser:**
```bash
python src/signal_parser.py
```

**Test OCR Processor:**
```bash
python src/ocr_processor.py
```

**Run Tests:**
```bash
python tests/run_tests.py
```

## Using Mock MT5 Engine

For development, you can use the mock MT5 engine which simulates trading without actual MT5 connection.

### Option 1: Modify main.py temporarily

Replace the import in `main.py`:

```python
# Original
from src.mt5_engine import MT5Engine

# For macOS development
from src.mt5_engine_mock import MT5EngineMock as MT5Engine
```

### Option 2: Create a dev version

```bash
cp main.py main_dev.py
# Edit main_dev.py to use MT5EngineMock
python main_dev.py
```

## Development Workflow

1. **Develop on macOS**: Test Telegram, OCR, signal parsing
2. **Deploy to Windows VPS**: Run with real MT5 connection
3. **Monitor remotely**: View logs via SSH/RDP

## Deployment Options for macOS Users

### Option 1: Windows VPS (Recommended)
- Rent a Windows VPS (e.g., Contabo, Vultr)
- Install MT5 and Python
- Deploy code there
- Use `requirements-windows.txt`

### Option 2: Wine on Linux
- Use a Linux VPS
- Install Wine and MT5 under Wine
- More complex setup
- May have compatibility issues

### Option 3: Hybrid Setup
- Develop on macOS
- Run MT5 on Windows PC/VPS
- Connect via custom bridge (requires additional implementation)

## Testing Strategy

### On macOS (Development)
✓ Telegram integration
✓ OCR processing
✓ Signal parsing
✓ Risk calculations (logic only)
✓ Code quality
✓ Unit tests

### On Windows (Production Testing)
✓ Full MT5 integration
✓ Order placement
✓ Position tracking
✓ TP/SL management
✓ End-to-end testing

## Common Issues on macOS

### Issue: MetaTrader5 package won't install
**Solution**: Use `requirements-dev.txt` instead of `requirements.txt`

### Issue: Can't test trading
**Solution**: Use mock engine or deploy to Windows VPS for real testing

### Issue: Need to test full system
**Solution**: 
1. Use Windows VM (Parallels, VMWare)
2. Or deploy to Windows VPS
3. Or use GitHub Actions with Windows runner

## Production Deployment

When ready for production:

1. Set up Windows VPS
2. Install MT5 and Python
3. Clone repository
4. Use `requirements-windows.txt`
5. Configure credentials
6. Run `python main.py`

## Remote Development

### SSH to Windows VPS
```bash
ssh user@your-windows-vps
cd mt5_automator
python main.py
```

### View Logs Remotely
```bash
ssh user@your-vps "tail -f /path/to/mt5_automator/logs/mt5_automator.log"
```

### Deploy Changes
```bash
# On macOS
git push origin main

# On Windows VPS
git pull origin main
# Restart the application
```

## Summary

- **Development on macOS**: ✓ Possible with mock engine
- **Testing signal processing**: ✓ Fully supported
- **Real trading on macOS**: ✗ Not possible (MT5 is Windows-only)
- **Solution**: Deploy to Windows VPS for production

---

**Bottom Line**: Develop and test everything except MT5 integration on macOS, then deploy to Windows for production trading.

