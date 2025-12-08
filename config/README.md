# Configuration (Simple - ONE File Only!)

## For Windows Production Users

You only need to edit **ONE file**: `config.env`

All settings (Telegram, MT5, DeepSeek, channels) are in this single file.

### Quick Setup (3 Steps)

**Step 1:** Open `config.env` with Notepad

**Step 2:** Fill in your details:

```bash
# ===== TELEGRAM SETTINGS =====
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+421907975101
TELEGRAM_CHANNELS=google_target_qaaw,another_channel,third_channel

# ===== MT5 SETTINGS =====
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_broker_server

# ===== DEEPSEEK AI SETTINGS =====
DEEPSEEK_API_KEY=sk-your-actual-key-here
```

**Step 3:** Save and run `python main.py`

That's it! No YAML files, no multiple config files.

## Getting Your API Keys

### 1. Telegram API (Required)

1. Go to: https://my.telegram.org/auth
2. Login with your phone number
3. Click "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`
6. Paste them in `config.env`

### 2. DeepSeek API (Required)

1. Go to: https://platform.deepseek.com/
2. Sign up (free account)
3. Click "API Keys" in dashboard
4. Click "Create New Key"
5. Copy the key (starts with `sk-...`)
6. Paste it in `config.env`

### 3. Add Telegram Channels

In `config.env`, find this line:

```bash
TELEGRAM_CHANNELS=google_target_qaaw
```

To add multiple channels, separate them with commas:

```bash
TELEGRAM_CHANNELS=channel1,channel2,channel3
```

You can use:
- Channel usernames: `google_target_qaaw`
- Channel IDs: `-1003397933414`

## Security Notes

⚠️ **IMPORTANT:**
- `config.env` contains your passwords and API keys
- This file is **NOT** committed to git (it's in `.gitignore`)
- **Never** share this file publicly
- Keep it safe on your computer only

## Settings You Can Change

All in `config.env`:

| Setting | Description | Example |
|---------|-------------|---------|
| `RISK_PERCENT` | Risk per trade (%) | `1.0` = 1% |
| `NUM_POSITIONS` | How many positions per signal | `3` |
| `DEFAULT_SYMBOL` | Trading symbol | `XAUUSD` |
| `DRY_RUN` | Test mode (true/false) | `false` for real trading |

## Troubleshooting

**"Invalid literal for int()"**
→ You forgot to add values in `config.env`

**"Telegram error"**
→ Check your `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`

**"MT5 connection failed"**
→ Check your `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`
→ Make sure MT5 is open and logged in

**"DeepSeek API error"**
→ Check your `DEEPSEEK_API_KEY` is correct

## For Advanced Users (Optional)

If you prefer YAML configuration, you can still create `config/config.yaml` manually.
The system will use it if it exists, otherwise it uses `config.env` directly.

For 99% of users: **Just use config.env!**
