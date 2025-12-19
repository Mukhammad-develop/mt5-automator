# Running System Tests

This guide explains how to run the system test suite to verify that all components of the MT5 Automator are working correctly.

## Quick Start

Run the test suite with a single command:

```bash
python test_system.py
```

## What Gets Tested

The test suite checks the following components:

1. **Configuration Loading** - Verifies that all required configuration sections are present
2. **Signal Parser (Regex)** - Tests the regex-based signal parsing with various formats
3. **AI Signal Parser** - Tests the AI-powered signal parser (if API key is configured)
4. **MT5 Connection** - Tests connection to MetaTrader 5 terminal
5. **Symbol Resolver** - Tests automatic symbol resolution to broker-specific names
6. **Risk Manager** - Tests lot size calculation and trade validation
7. **Telegram Connection** - Tests connection to Telegram API

## Prerequisites

Before running tests, make sure:

1. **Configuration is set up** - `config.env` file exists with all required settings
2. **MT5 Terminal is running** (for MT5 tests) - The MetaTrader 5 terminal should be open and logged in
3. **Python dependencies installed** - Run `pip install -r requirements.txt`

## Test Results

The test suite will show:

- ✅ **Passed** - Component is working correctly
- ❌ **Failed** - Component has an issue that needs to be fixed
- ⚠️ **Skipped** - Component test was skipped (usually because a dependency is missing)

### Example Output

```
============================================================
MT5 AUTOMATOR SYSTEM TEST
============================================================

============================================================
Testing: Configuration Loading
============================================================
  ✅ Found config section: telegram
  ✅ Found config section: mt5
  ✅ Found config section: trading
  ✅ Telegram API ID configured
  ✅ MT5 login configured
  ✅ Risk percent: 1.0%
  ✅ Number of positions: 3
  ✅ Default symbol: BTCUSD
✅ PASSED: Configuration Loading

============================================================
Testing: Signal Parser (Regex)
============================================================
  ✅ Parsed signal 1: BUY BTCUSD
     Entry: 90000.0 - 90100.0
  ✅ Parsed signal 2: SELL XAUUSD
  ✅ Parsed signal 3: BUY BTCUSD
✅ PASSED: Signal Parser (Regex)

...

============================================================
TEST SUMMARY
============================================================

Total tests: 7
✅ Passed: 6
❌ Failed: 0
⚠️  Skipped: 1

✅ Passed tests:
   - Configuration Loading
   - Signal Parser (Regex)
   - AI Signal Parser
   - MT5 Connection
   - Symbol Resolver
   - Risk Manager

⚠️  Skipped tests:
   - Telegram Connection

============================================================
🎉 All critical tests passed! System is ready to use.
⚠️  Some optional tests were skipped (check configuration).
============================================================
```

## Troubleshooting

### MT5 Connection Fails

**Error:** `Failed to connect to MT5`

**Solutions:**
1. Make sure MT5 terminal is running
2. Check that you're logged into your MT5 account
3. Verify `MT5_LOGIN`, `MT5_PASSWORD`, and `MT5_SERVER` in `config.env` are correct
4. On Windows, check that the MT5 path in config is correct (default: `C:/Program Files/MetaTrader 5/terminal64.exe`)

### Telegram Connection Fails

**Error:** `Failed to connect to Telegram`

**Solutions:**
1. Verify `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` in `config.env` are correct
2. Check your internet connection
3. Make sure you've completed the initial Telegram authentication (first run will ask for phone number and code)
4. If using a new session, you may need to authorize the device

### Symbol Not Found

**Error:** `Symbol BTCUSD not found`

**Solutions:**
1. Open MT5 terminal
2. Go to Market Watch
3. Right-click and select "Show All"
4. Find and enable the symbol (right-click → "Show Symbol")
5. The symbol resolver will cache it for future use

### AI Parser Skipped

**Warning:** `AI parsing disabled`

**Solutions:**
1. This is optional - the system will fall back to regex parsing
2. To enable AI parsing, add `DEEPSEEK_API_KEY` to `config.env`
3. Get an API key from https://platform.deepseek.com/

### Risk Manager Fails

**Error:** `Could not calculate lot sizes`

**Solutions:**
1. Make sure MT5 is connected
2. Verify the symbol exists in MT5
3. Check that account has sufficient balance
4. Verify risk percentage in config is reasonable (e.g., 1.0%)

## Running Specific Tests

If you want to test only specific components, you can modify `test_system.py` or run individual test methods:

```python
from test_system import SystemTester

tester = SystemTester()
tester.test("MT5 Connection", tester.test_mt5_connection)
```

## Continuous Testing

For development, you can run tests automatically:

```bash
# Watch for changes and run tests
python test_system.py

# Or use pytest (if installed)
pytest test_system.py -v
```

## What to Do After Tests

1. **All tests passed** - You're ready to run the main bot! Start with:
   ```bash
   python main.py
   ```

2. **Some tests failed** - Fix the issues before running the bot:
   - Check error messages in the test output
   - Verify configuration in `config.env`
   - Ensure all dependencies are installed
   - Make sure MT5 terminal is running (for MT5 tests)

3. **Tests skipped** - These are usually optional components:
   - AI parser can be skipped if API key is not set
   - Telegram can be skipped if credentials are missing
   - MT5 can be skipped if terminal is not running

## Next Steps

After tests pass:

1. **Start the bot:**
   ```bash
   python main.py
   ```

2. **Monitor logs:**
   - Check `logs/mt5_automator.log` for detailed logs
   - Watch console output for warnings and errors

3. **Test with a real signal:**
   - Send a test signal to your Telegram channel
   - Verify it's parsed correctly
   - Check that orders are placed (or logged in dry-run mode)

## Additional Resources

- **Configuration Guide:** See `config.env.example` for all available settings
- **Troubleshooting:** Check logs in `logs/mt5_automator.log`
- **Support:** Review other documentation in the `docs/` folder

