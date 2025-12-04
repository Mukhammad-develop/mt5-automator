"""
Utility functions for MT5 Trading Automator
"""
import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv


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
    
    # Create logger
    logger = logging.getLogger('MT5Automator')
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(log_level)
    
    # Console handler (can be different level than file)
    console_handler = logging.StreamHandler()
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
    Load configuration from YAML file with environment variable substitution
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    # Load environment variables
    load_dotenv()
    
    # Read YAML file
    with open(config_path, 'r') as f:
        config_str = f.read()
    
    # Replace environment variables
    config_str = os.path.expandvars(config_str)
    
    # Parse YAML
    config = yaml.safe_load(config_str)
    
    return config


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
    
    # Add timestamp
    signal['saved_at'] = datetime.now().isoformat()
    
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
    Get signal by ID from database
    
    Args:
        signal_id: Signal ID
        db_path: Path to database file
        
    Returns:
        Signal dictionary or None
    """
    signals = load_signals_from_db(db_path)
    for signal in signals:
        if signal.get('signal_id') == signal_id:
            return signal
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

