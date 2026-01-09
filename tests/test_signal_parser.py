"""
Unit tests for Signal Parser
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.signal_parser import SignalParser
from src.utils import load_config, evaluate_entry_distance


def test_basic_buy_signal():
    """Test parsing basic BUY signal"""
    config = {'trading': {'default_symbol': 'XAUUSD'}}
    parser = SignalParser(config)
    
    text = """
    BUY 2650.50 - 2648.20
    SL1: 2645.00
    TP1: 2655.00
    TP2: 2660.00
    """
    
    signal = parser.parse_signal(text)
    
    assert signal is not None
    assert signal['direction'] == 'BUY'
    assert signal['entry_upper'] == 2650.50
    assert signal['entry_lower'] == 2648.20
    assert signal['entry_middle'] == (2650.50 + 2648.20) / 2
    assert signal['sl1'] == 2645.00
    assert signal['tp1'] == 2655.00
    assert signal['tp2'] == 2660.00
    
    print("✓ Basic BUY signal test passed")


def test_basic_sell_signal():
    """Test parsing basic SELL signal"""
    config = {'trading': {'default_symbol': 'XAUUSD'}}
    parser = SignalParser(config)
    
    text = """
    SELL 2655.00 - 2657.50
    SL: 2662.00
    TP1: 2648.00
    TP2: 2640.00
    """
    
    signal = parser.parse_signal(text)
    
    assert signal is not None
    assert signal['direction'] == 'SELL'
    assert signal['entry_upper'] == 2657.50
    assert signal['entry_lower'] == 2655.00
    assert signal['sl1'] == 2662.00
    assert signal['tp1'] == 2648.00
    assert signal['tp2'] == 2640.00
    
    print("✓ Basic SELL signal test passed")


def test_compact_format():
    """Test parsing compact signal format"""
    config = {'trading': {'default_symbol': 'XAUUSD'}}
    parser = SignalParser(config)
    
    text = """
    BUY GOLD 2645-2643
    TP1 2650
    TP2 2655
    SL 2640
    """
    
    signal = parser.parse_signal(text)
    
    assert signal is not None
    assert signal['direction'] == 'BUY'
    assert signal['symbol'] == 'XAUUSD'  # GOLD normalized to XAUUSD
    assert signal['entry_upper'] == 2645
    assert signal['entry_lower'] == 2643
    
    print("✓ Compact format test passed")


def test_detailed_format():
    """Test parsing detailed signal format"""
    config = {'trading': {'default_symbol': 'XAUUSD'}}
    parser = SignalParser(config)
    
    text = """
    SELL XAUUSD
    Entry: 2655 - 2657
    Stop Loss 1: 2662
    Stop Loss 2: 2664
    Take Profit 1: 2648
    Take Profit 2: 2640
    """
    
    signal = parser.parse_signal(text)
    
    assert signal is not None
    assert signal['direction'] == 'SELL'
    assert signal['sl1'] == 2662
    assert signal['sl2'] == 2664
    
    print("✓ Detailed format test passed")


def test_invalid_signal():
    """Test that invalid signals are rejected"""
    config = {'trading': {'default_symbol': 'XAUUSD'}}
    parser = SignalParser(config)
    
    # Missing direction
    text1 = "2650.50 - 2648.20"
    signal1 = parser.parse_signal(text1)
    assert signal1 is None
    
    # Invalid TP (below entry for BUY)
    text2 = """
    BUY 2650 - 2648
    TP1: 2640
    SL: 2645
    """
    signal2 = parser.parse_signal(text2)
    assert signal2 is None
    
    print("✓ Invalid signal rejection test passed")


def test_missing_tp_sl_rejected():
    """Ensure signals without TP and SL are rejected"""
    config = {'trading': {'default_symbol': 'XAUUSD'}}
    parser = SignalParser(config)
    
    text = "BUY 2650 - 2648"  # No TP/SL
    signal = parser.parse_signal(text)
    assert signal is None
    print("✓ Missing TP/SL rejection test passed")


def test_entry_distance_guard():
    """Ensure entry distance guard flags far-away entries"""
    current_price = 100.0
    entry_upper = 200.0
    entry_lower = 199.0
    percent_threshold = 10.0
    
    result = evaluate_entry_distance(entry_upper, entry_lower, current_price, percent_threshold)
    assert result['exceeded'] is True
    assert result['reason'] == 'percent'
    
    # Within threshold should pass
    close_result = evaluate_entry_distance(105.0, 95.0, current_price, percent_threshold)
    assert close_result['exceeded'] is False
    
    print("✓ Entry distance guard test passed")


def test_all():
    """Run all tests"""
    print("\nRunning Signal Parser Tests...")
    print("-" * 50)
    
    test_basic_buy_signal()
    test_basic_sell_signal()
    test_compact_format()
    test_detailed_format()
    test_invalid_signal()
    test_missing_tp_sl_rejected()
    test_entry_distance_guard()
    
    print("-" * 50)
    print("All tests passed! ✓\n")


if __name__ == '__main__':
    test_all()
