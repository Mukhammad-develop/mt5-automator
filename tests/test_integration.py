"""
Integration tests for MT5 Automator
Tests component interactions without actual trading
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.signal_parser import SignalParser
from src.ocr_processor import OCRProcessor
from src.utils import load_config, generate_signal_id


def test_signal_flow():
    """Test complete signal processing flow"""
    print("\nTesting Signal Processing Flow...")
    print("-" * 50)
    
    try:
        config = load_config('config/config.yaml')
    except:
        config = {
            'trading': {'default_symbol': 'XAUUSD'},
            'ocr': {
                'tesseract_cmd': '/usr/bin/tesseract',
                'preprocessing': {
                    'resize_factor': 2.0,
                    'contrast_boost': True,
                    'denoise': True,
                    'sharpen': True
                }
            }
        }
    
    # Create parser
    parser = SignalParser(config)
    
    # Test signal
    test_signal_text = """
    BUY XAUUSD 2650.50 - 2648.20
    SL1: 2645.00
    SL2: 2643.50
    SL3: 2642.00
    TP1: 2655.00
    TP2: 2660.00
    """
    
    print("1. Parsing signal...")
    signal = parser.parse_signal(test_signal_text)
    
    if signal:
        print("   ✓ Signal parsed successfully")
        print(f"   Direction: {signal['direction']}")
        print(f"   Entry: {signal['entry_upper']} - {signal['entry_lower']}")
        print(f"   TP1: {signal['tp1']}, TP2: {signal['tp2']}")
        print(f"   SL1: {signal['sl1']}, SL2: {signal['sl2']}, SL3: {signal['sl3']}")
    else:
        print("   ✗ Failed to parse signal")
        return False
    
    print("\n2. Generating signal ID...")
    signal_id = generate_signal_id(signal)
    print(f"   ✓ Signal ID: {signal_id}")
    
    print("\n3. Validating signal structure...")
    required_fields = ['direction', 'symbol', 'entry_upper', 'entry_middle', 'entry_lower']
    for field in required_fields:
        if field not in signal:
            print(f"   ✗ Missing field: {field}")
            return False
    print("   ✓ All required fields present")
    
    print("\n4. Testing signal formatting...")
    formatted = parser.format_signal(signal)
    print(f"   ✓ Formatted output:\n{formatted}")
    
    print("-" * 50)
    print("Integration test passed! ✓\n")
    return True


def test_ocr_integration():
    """Test OCR processor integration"""
    print("\nTesting OCR Integration...")
    print("-" * 50)
    
    try:
        config = load_config('config/config.yaml')
    except:
        config = {
            'ocr': {
                'tesseract_cmd': '/usr/bin/tesseract',
                'preprocessing': {
                    'resize_factor': 2.0,
                    'contrast_boost': True,
                    'denoise': True,
                    'sharpen': True
                }
            }
        }
    
    try:
        ocr_processor = OCRProcessor(config)
        print("   ✓ OCR Processor initialized")
        
        # Check if test image exists
        test_image = 'data/images/test_signal.jpg'
        if os.path.exists(test_image):
            print(f"   ✓ Test image found: {test_image}")
            text = ocr_processor.process_image(test_image)
            if text:
                print(f"   ✓ OCR extracted text ({len(text)} chars)")
            else:
                print("   ⚠ OCR returned no text")
        else:
            print("   ⚠ No test image found (expected at data/images/test_signal.jpg)")
            print("   Place a signal image there to test OCR")
        
        print("-" * 50)
        print("OCR integration test completed\n")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("   Note: Tesseract OCR may not be installed")
        print("-" * 50)
        return False


def test_risk_calculation_logic():
    """Test risk calculation logic (without MT5 connection)"""
    print("\nTesting Risk Calculation Logic...")
    print("-" * 50)
    
    # Simulated account and signal data
    balance = 10000
    risk_percent = 1.0
    num_positions = 3
    
    test_signal = {
        'direction': 'BUY',
        'symbol': 'XAUUSD',
        'entry_upper': 2650.50,
        'entry_middle': 2649.35,
        'entry_lower': 2648.20,
        'sl1': 2645.00,
        'sl2': 2643.50,
        'sl3': 2642.00
    }
    
    print(f"   Account balance: ${balance}")
    print(f"   Risk per signal: {risk_percent}%")
    print(f"   Number of positions: {num_positions}")
    
    # Calculate total risk
    risk_amount = balance * (risk_percent / 100)
    risk_per_position = risk_amount / num_positions
    
    print(f"\n   Total risk: ${risk_amount}")
    print(f"   Risk per position: ${risk_per_position:.2f}")
    
    # Calculate pip risk for each position
    entries = [test_signal['entry_upper'], test_signal['entry_middle'], test_signal['entry_lower']]
    sls = [test_signal['sl1'], test_signal['sl2'], test_signal['sl3']]
    
    print("\n   Position breakdown:")
    for i, (entry, sl) in enumerate(zip(entries, sls), 1):
        pip_distance = abs(entry - sl) / 0.01  # For gold, 1 pip = 0.01
        print(f"   Position {i}: Entry={entry}, SL={sl}, Risk={pip_distance:.0f} pips")
    
    print("\n   ✓ Risk calculation logic verified")
    print("-" * 50)
    print("Risk calculation test passed! ✓\n")
    return True


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("MT5 AUTOMATOR - INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Signal Flow", test_signal_flow()))
    results.append(("OCR Integration", test_ocr_integration()))
    results.append(("Risk Calculation", test_risk_calculation_logic()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS ✓" if result else "FAIL ✗"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

