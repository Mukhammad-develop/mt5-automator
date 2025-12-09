"""
Utility functions for MT5 Trading Automator
"""
import os
import sys
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv
import re


class SafeConsoleHandler(logging.StreamHandler):
    """
    Console handler that safely handles Unicode characters on Windows.
    Strips emojis from console output but keeps them in file logs.
    """
    
    # Common emoji patterns
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+",
        flags=re.UNICODE
    )
    
    def emit(self, record):
        """
        Emit a record, stripping emojis for console output
        """
        try:
            # Get the formatted message
            msg = self.format(record)
            
            # Strip emojis for console (Windows compatibility)
            if sys.platform == 'win32':
                msg = self.EMOJI_PATTERN.sub('', msg).strip()
            
            # Try to write with UTF-8 encoding
            stream = self.stream
            if hasattr(stream, 'buffer'):
                # For sys.stdout/sys.stderr, use the underlying buffer
                stream.buffer.write((msg + self.terminator).encode('utf-8', errors='replace'))
                stream.buffer.flush()
            else:
                # Fallback to regular write with error handling
                try:
                    stream.write(msg + self.terminator)
                    self.flush()
                except UnicodeEncodeError:
                    # If encoding fails, replace problematic characters
                    safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
                    stream.write(safe_msg + self.terminator)
                    self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Setup logging with file and console handlers
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger instance
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'logs/mt5_automator.log')
    max_bytes = log_config.get('max_bytes', 10485760)
    backup_count = log_config.get('backup_count', 5)
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            # Try to set console output to UTF-8
            import codecs
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass  # If it fails, the SafeConsoleHandler will handle it
    
    # Create logger
    logger = logging.getLogger('MT5Automator')
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with rotation (UTF-8 encoding)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # Console handler with safe Unicode handling
    console_handler = SafeConsoleHandler(sys.stdout)
    console_level = getattr(logging, log_config.get('console_level', 'WARNING'))
    console_handler.setLevel(console_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def load_config(config_path: str = 'config/config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file or directly from config.env
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    # Load environment variables from config.env
    load_dotenv('config.env')
    
    # If config.yaml doesn't exist, use simple config from environment variables
    if not os.path.exists(config_path):
        return _load_config_from_env()
    
    # Read YAML file
    with open(config_path, 'r') as f:
        config_str = f.read()
    
    # Replace environment variables
    config_str = os.path.expandvars(config_str)
    
    # Parse YAML
    config = yaml.safe_load(config_str)
    
    return config


def _load_config_from_env() -> Dict[str, Any]:
    """
    Create config directly from environment variables (config.env).
    This is the simplified approach for non-technical users.
    
    Returns:
        Configuration dictionary
    """
    # Parse channels from comma-separated string
    channels_str = os.getenv('TELEGRAM_CHANNELS', 'google_target_qaaw')
    channels = [ch.strip() for ch in channels_str.split(',') if ch.strip()]
    
    # Parse symbol mapping from comma-separated string
    # Format: XAUUSD=XAUUSD+,EURUSD=EURUSD.a
    symbol_mapping = {}
    mapping_str = os.getenv('SYMBOL_MAPPING', '')
    if mapping_str:
        for mapping in mapping_str.split(','):
            if '=' in mapping:
                signal_sym, broker_sym = mapping.split('=', 1)
                symbol_mapping[signal_sym.strip()] = broker_sym.strip()
    
    return {
        'telegram': {
            'api_id': int(os.getenv('TELEGRAM_API_ID', '0')),
            'api_hash': os.getenv('TELEGRAM_API_HASH', ''),
            'phone': os.getenv('TELEGRAM_PHONE', ''),
            'session_name': os.getenv('TELEGRAM_SESSION', 'mt5_automator_session'),
            'channels': channels
        },
        'mt5': {
            'login': int(os.getenv('MT5_LOGIN', '0')),
            'password': os.getenv('MT5_PASSWORD', ''),
            'server': os.getenv('MT5_SERVER', ''),
            'path': 'C:/Program Files/MetaTrader 5/terminal64.exe'
        },
        'ai': {
            'enabled': True,
            'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'api_base': 'https://api.deepseek.com/v1',
            'model': 'deepseek-chat',
            'vision_model': 'deepseek-reasoner',
            'use_vision': True,
            'fallback_to_ocr': True,
            'fallback_to_regex': True,
            'max_retries': 2,
            'timeout': 30
        },
        'mode': {
            'dry_run': os.getenv('DRY_RUN', 'false').lower() == 'true'
        },
        'trading': {
            'risk_percent': float(os.getenv('RISK_PERCENT', '1.0')),
            'num_positions': int(os.getenv('NUM_POSITIONS', '3')),
            'default_symbol': os.getenv('DEFAULT_SYMBOL', 'XAUUSD'),
            'symbol_mapping': symbol_mapping,
            'breakeven_enabled': os.getenv('BREAKEVEN_ENABLED', 'false').lower() == 'true',
            'breakeven_trigger': os.getenv('BREAKEVEN_TRIGGER', 'middle_entry'),
            'breakeven_offset': float(os.getenv('BREAKEVEN_OFFSET', '5.0')),
            'tp2_move_to_breakeven': os.getenv('TP2_MOVE_TO_BREAKEVEN', 'true').lower() == 'true',
            'position_1_tp': os.getenv('POSITION_1_TP', 'TP1').upper(),  # TP1 or TP2
            'staged_entry_enabled': os.getenv('STAGED_ENTRY_ENABLED', 'true').lower() == 'true',
            'trailing_stop_enabled': os.getenv('TRAILING_STOP_ENABLED', 'true').lower() == 'true',
            'trailing_stop_pips': float(os.getenv('TRAILING_STOP_PIPS', '20')),
            'trailing_stop_activation_pips': float(os.getenv('TRAILING_STOP_ACTIVATION_PIPS', '10')),
            'position_3_runner_enabled': os.getenv('POSITION_3_RUNNER_ENABLED', 'true').lower() == 'true',
            'position_3_trailing_after_tp2': os.getenv('POSITION_3_TRAILING_AFTER_TP2', 'true').lower() == 'true'
        },
        'ocr': {
            'tesseract_cmd': 'C:/Program Files/Tesseract-OCR/tesseract.exe',
            'preprocessing': {
                'resize_factor': 2.0,
                'contrast_boost': True,
                'denoise': True,
                'sharpen': True
            }
        },
        'logging': {
            'level': 'INFO',
            'console_level': 'WARNING',
            'file': 'logs/mt5_automator.log',
            'max_bytes': 10485760,
            'backup_count': 5
        }
    }


def generate_signal_id(signal_data: Dict[str, Any]) -> str:
    """
    Generate unique signal ID based on signal content
    
    Args:
        signal_data: Signal dictionary
        
    Returns:
        Unique signal ID
    """
    # Create string from key signal parameters
    key_str = f"{signal_data.get('direction')}_{signal_data.get('entry_upper')}_{signal_data.get('entry_lower')}_{signal_data.get('tp1')}_{signal_data.get('tp2')}"
    
    # Generate hash
    signal_id = hashlib.md5(key_str.encode()).hexdigest()[:12]
    
    return signal_id


def save_signal_to_db(signal: Dict[str, Any], db_path: str = 'data/signals_db.json'):
    """
    Save signal to database
    
    Args:
        signal: Signal dictionary
        db_path: Path to database file
    """
    # Load existing signals
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            signals = json.load(f)
    else:
        signals = []
    
    # Add timestamp and status
    signal['saved_at'] = datetime.now().isoformat()
    signal['status'] = signal.get('status', 'active')  # Default: active
    
    # Append new signal
    signals.append(signal)
    
    # Save back
    with open(db_path, 'w') as f:
        json.dump(signals, f, indent=2)


def load_signals_from_db(db_path: str = 'data/signals_db.json') -> list:
    """
    Load all signals from database
    
    Args:
        db_path: Path to database file
        
    Returns:
        List of signals
    """
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            return json.load(f)
    return []


def get_signal_by_id(signal_id: str, db_path: str = 'data/signals_db.json') -> Optional[Dict[str, Any]]:
    """
    Get signal by ID from database (returns most recent)
    
    Args:
        signal_id: Signal ID
        db_path: Path to database file
        
    Returns:
        Signal dictionary or None
    """
    signals = load_signals_from_db(db_path)
    # Return most recent signal with this ID (in case of duplicates)
    for signal in reversed(signals):  # Start from end (most recent)
        if signal.get('signal_id') == signal_id:
            return signal
    return None


def update_signal_status(signal_id: str, status: str, db_path: str = 'data/signals_db.json') -> bool:
    """
    Update signal status in database
    
    Args:
        signal_id: Signal ID
        status: New status ('active', 'tp2_hit', 'completed', 'cancelled')
        db_path: Path to database file
        
    Returns:
        True if updated successfully
    """
    try:
        if not os.path.exists(db_path):
            return False
        
        with open(db_path, 'r') as f:
            signals = json.load(f)
        
        # Update all signals with this ID (in case of duplicates)
        updated = False
        for signal in signals:
            if signal.get('signal_id') == signal_id:
                signal['status'] = status
                signal['status_updated_at'] = datetime.now().isoformat()
                updated = True
        
        if updated:
            with open(db_path, 'w') as f:
                json.dump(signals, f, indent=2)
        
        return updated
        
    except Exception as e:
        print(f"Error updating signal status: {e}")
        return False


def check_signal_status(signal_id: str, db_path: str = 'data/signals_db.json') -> Optional[str]:
    """
    Check status of a signal in database
    
    Args:
        signal_id: Signal ID
        db_path: Path to database file
        
    Returns:
        Signal status or None if not found
    """
    signal = get_signal_by_id(signal_id, db_path)
    if signal:
        return signal.get('status', 'unknown')
    return None


def format_price(price: float, decimals: int = 2) -> str:
    """
    Format price for display
    
    Args:
        price: Price value
        decimals: Number of decimal places
        
    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"


def calculate_pip_value(symbol: str, lot_size: float, account_currency: str = 'USD') -> float:
    """
    Calculate pip value for a symbol
    
    Args:
        symbol: Trading symbol
        lot_size: Lot size
        account_currency: Account currency
        
    Returns:
        Pip value in account currency
    """
    # Simplified pip value calculation
    # For XAUUSD (gold), 1 pip = 0.01, so pip value = lot_size * 0.01
    # For forex pairs, typically 1 pip = 0.0001, pip value = lot_size * 100000 * 0.0001 = lot_size * 10
    
    if 'XAU' in symbol or 'GOLD' in symbol:
        # Gold: 1 lot = 100 oz, 1 pip = 0.01
        return lot_size * 100 * 0.01
    elif 'JPY' in symbol:
        # JPY pairs: 1 pip = 0.01
        return lot_size * 100000 * 0.01
    else:
        # Standard forex: 1 pip = 0.0001
        return lot_size * 100000 * 0.0001


def calculate_pip_distance(price1: float, price2: float, symbol: str) -> float:
    """
    Calculate distance in pips between two prices
    
    Args:
        price1: First price
        price2: Second price
        symbol: Trading symbol
        
    Returns:
        Distance in pips
    """
    if 'XAU' in symbol or 'GOLD' in symbol:
        # Gold: 1 pip = 0.01
        return abs(price1 - price2) / 0.01
    elif 'JPY' in symbol:
        # JPY pairs: 1 pip = 0.01
        return abs(price1 - price2) / 0.01
    else:
        # Standard forex: 1 pip = 0.0001
        return abs(price1 - price2) / 0.0001


def validate_lot_size(lot_size: float, min_lot: float = 0.01, max_lot: float = 100.0) -> float:
    """
    Validate and clamp lot size within allowed range
    
    Args:
        lot_size: Requested lot size
        min_lot: Minimum allowed lot
        max_lot: Maximum allowed lot
        
    Returns:
        Valid lot size
    """
    lot_size = round(lot_size, 2)
    lot_size = max(min_lot, min(lot_size, max_lot))
    return lot_size


def create_class_logger(class_name: str) -> logging.Logger:
    """
    Create a logger for a specific class
    
    Args:
        class_name: Name of the class
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'MT5Automator.{class_name}')

