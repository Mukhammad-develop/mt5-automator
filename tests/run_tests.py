"""
Test runner for MT5 Automator
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\n" + "="*70)
print(" MT5 TRADING AUTOMATOR - TEST SUITE")
print("="*70 + "\n")

# Run unit tests
print("UNIT TESTS")
print("-"*70)
try:
    from test_signal_parser import test_all as test_parser
    test_parser()
except Exception as e:
    print(f"✗ Signal parser tests failed: {e}\n")

# Run integration tests
print("\nINTEGRATION TESTS")
print("-"*70)
try:
    from test_integration import run_all_tests
    success = run_all_tests()
except Exception as e:
    print(f"✗ Integration tests failed: {e}\n")
    success = False

print("\n" + "="*70)
if success:
    print(" TEST SUITE COMPLETED SUCCESSFULLY ✓")
else:
    print(" SOME TESTS FAILED - REVIEW OUTPUT ABOVE ✗")
print("="*70 + "\n")

sys.exit(0 if success else 1)

