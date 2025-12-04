# Configuration Files

## Setup Instructions

### 1. Create Your Configuration Files

Copy the example files and customize them:

```bash
# Copy config.yaml
cp config/config.yaml.example config/config.yaml

# Copy .env
cp config.env.example config.env
# OR
cp config.env.example .env  # Place in root directory
```

### 2. Edit config.yaml

Update with your settings:

```yaml
telegram:
  channels:
    - "your_channel_username"  # Your actual channel

mode:
  dry_run: true  # false for production on Windows

trading:
  risk_percent: 1.0  # Your risk tolerance
```

### 3. Edit config.env (or .env)

Add your API credentials:

```bash
TELEGRAM_API_ID=your_actual_api_id
TELEGRAM_API_HASH=your_actual_api_hash
TELEGRAM_PHONE=+1234567890
DEEPSEEK_API_KEY=sk-your-actual-key
```

## Security Notes

⚠️ **IMPORTANT:**
- `config.yaml` and `config.env` contain **sensitive credentials**
- These files are in `.gitignore` and **will not be committed to git**
- **Never** share these files publicly
- **Never** commit them to GitHub

✅ **Safe to commit:**
- `config.yaml.example`
- `config.env.example`

❌ **Never commit:**
- `config.yaml` (your actual config)
- `config.env` (your actual credentials)
- `.env` (your actual credentials)

## File Locations

```
mt5_automator/
├── config/
│   ├── config.yaml.example  ✅ Template (in git)
│   └── config.yaml          ❌ Your config (NOT in git)
├── config.env.example       ✅ Template (in git)
├── config.env               ❌ Your credentials (NOT in git)
└── .env                     ❌ Your credentials (NOT in git)
```

## Getting API Keys

### Telegram API
1. Visit: https://my.telegram.org/auth
2. Login with your phone
3. Go to "API development tools"
4. Create app → Copy `api_id` and `api_hash`

### DeepSeek API
1. Visit: https://platform.deepseek.com
2. Create account
3. Get API key from dashboard

## Quick Start

```bash
# 1. Setup
cp config/config.yaml.example config/config.yaml
cp config.env.example .env

# 2. Edit files with your credentials
nano config/config.yaml
nano .env

# 3. Run
python3 main.py
```

## Troubleshooting

**"Config file not found"**
- Make sure you copied `config.yaml.example` to `config.yaml`

**"Environment variable not set"**
- Make sure you created `.env` or `config.env`
- Check file is in the correct location

**"Invalid credentials"**
- Verify API keys are correct
- Check for extra spaces or quotes

For more help, see: [../docs/QUICKSTART.md](../docs/QUICKSTART.md)

