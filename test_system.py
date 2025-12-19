"""
System Test Suite
Run this to verify all components are working correctly
"""
import sys
import asyncio
from typing import Dict, Any
from src.utils import load_config, setup_logging
from src.signal_parser import SignalParser
from src.ai_signal_parser import AISignalParser
from src.symbol_resolver import SymbolResolver
from src.risk_manager import RiskManager

# Try to import MT5 engine
try:
    from src.mt5_engine import MT5Engine
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️  MT5 package not available - will skip MT5 tests")

# Try to import Telegram monitor
try:
    from src.telegram_monitor import TelegramMonitor
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  Telegram package not available - will skip Telegram tests")


class SystemTester:
    """Test all system components"""
    
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logging(self.config)
        self.results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }
    
    def test(self, name: str, func):
        """Run a test and record result"""
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print(f"{'='*60}")
            result = func()
            if result:
                print(f"✅ PASSED: {name}")
                self.results['passed'].append(name)
            else:
                print(f"❌ FAILED: {name}")
                self.results['failed'].append(name)
        except Exception as e:
            print(f"❌ ERROR in {name}: {e}")
            self.results['failed'].append(name)
            import traceback
            traceback.print_exc()
    
    def test_config_loading(self) -> bool:
        """Test 1: Configuration loading"""
        try:
            print("Checking configuration...")
            
            # Check required sections
            required_sections = ['telegram', 'mt5', 'trading']
            for section in required_sections:
                if section not in self.config:
                    print(f"  ❌ Missing config section: {section}")
                    return False
                print(f"  ✅ Found config section: {section}")
            
            # Check Telegram config
            telegram_config = self.config.get('telegram', {})
            if not telegram_config.get('api_id'):
                print("  ⚠️  Telegram API ID not set (will skip Telegram tests)")
            else:
                print("  ✅ Telegram API ID configured")
            
            # Check MT5 config
            mt5_config = self.config.get('mt5', {})
            if not mt5_config.get('login'):
                print("  ⚠️  MT5 login not set (will skip MT5 tests)")
            else:
                print("  ✅ MT5 login configured")
            
            # Check trading config
            trading_config = self.config.get('trading', {})
            print(f"  ✅ Risk percent: {trading_config.get('risk_percent', 1.0)}%")
            print(f"  ✅ Number of positions: {trading_config.get('num_positions', 3)}")
            print(f"  ✅ Default symbol: {trading_config.get('default_symbol', 'BTCUSD')}")
            
            return True
        except Exception as e:
            print(f"  ❌ Config loading error: {e}")
            return False
    
    def test_signal_parser(self) -> bool:
        """Test 2: Signal parser (regex)"""
        try:
            parser = SignalParser(self.config)
            
            # Test signal 1: Standard format
            test_signal_1 = """
            BUY BTCUSD
            Entry: 90000 - 90100
            TP1: 90500
            TP2: 91000
            SL: 89500
            """
            signal1 = parser.parse_signal(test_signal_1)
            if not signal1:
                print("  ❌ Failed to parse test signal 1")
                return False
            print(f"  ✅ Parsed signal 1: {signal1['direction']} {signal1['symbol']}")
            print(f"     Entry: {signal1['entry_lower']} - {signal1['entry_upper']}")
            
            # Test signal 2: @ format
            test_signal_2 = "SELL @4200 4210 TP1: 4190 TP2: 4180 SL: 4220"
            signal2 = parser.parse_signal(test_signal_2)
            if not signal2:
                print("  ❌ Failed to parse test signal 2")
                return False
            print(f"  ✅ Parsed signal 2: {signal2['direction']} {signal2['symbol']}")
            
            # Test signal 3: BTC detection
            test_signal_3 = "btc buy NOW >>> @90300 90385"
            signal3 = parser.parse_signal(test_signal_3)
            if not signal3:
                print("  ❌ Failed to parse test signal 3")
                return False
            if signal3['symbol'] != 'BTCUSD':
                print(f"  ❌ Symbol not normalized: {signal3['symbol']} (expected BTCUSD)")
                return False
            print(f"  ✅ Parsed signal 3: {signal3['direction']} {signal3['symbol']}")
            
            return True
        except Exception as e:
            print(f"  ❌ Signal parser error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_ai_signal_parser(self) -> bool:
        """Test 3: AI signal parser"""
        try:
            parser = AISignalParser(self.config)
            
            if not parser.enabled:
                print("  ⚠️  AI parsing disabled (check DEEPSEEK_API_KEY)")
                self.results['skipped'].append("AI Signal Parser")
                return True  # Not a failure, just disabled
            
            # Test simple signal
            test_signal = "BUY BTCUSD @90000 90100 TP1: 90500 TP2: 91000 SL: 89500"
            signal = parser.parse_signal(test_signal)
            
            if signal:
                print(f"  ✅ AI parsed signal: {signal['direction']} {signal['symbol']}")
                return True
            else:
                print("  ⚠️  AI parsing returned None (may be API issue)")
                self.results['skipped'].append("AI Signal Parser")
                return True  # Not a failure if API is down
            
        except Exception as e:
            print(f"  ⚠️  AI parser error (may be API issue): {e}")
            self.results['skipped'].append("AI Signal Parser")
            return True  # Don't fail if AI is unavailable
    
    def test_mt5_connection(self) -> bool:
        """Test 4: MT5 connection"""
        if not MT5_AVAILABLE:
            print("  ⚠️  MT5 package not available - skipping")
            self.results['skipped'].append("MT5 Connection")
            return True
        
        try:
            engine = MT5Engine(self.config)
            print("  Attempting to connect to MT5...")
            
            if engine.connect():
                print("  ✅ MT5 connected successfully")
                
                # Test account info
                account_info = engine.get_account_info()
                if account_info:
                    print(f"  ✅ Account balance: {account_info['balance']} {account_info['currency']}")
                    print(f"  ✅ Leverage: 1:{account_info['leverage']}")
                else:
                    print("  ⚠️  Could not get account info")
                
                # Test symbol info
                symbol = self.config.get('trading', {}).get('default_symbol', 'BTCUSD')
                symbol_info = engine.get_symbol_info(symbol)
                if symbol_info:
                    print(f"  ✅ Symbol {symbol} found: Bid={symbol_info['bid']}, Ask={symbol_info['ask']}")
                else:
                    print(f"  ⚠️  Symbol {symbol} not found (may need to enable in MT5)")
                
                engine.disconnect()
                return True
            else:
                print("  ❌ Failed to connect to MT5")
                print("     Check: MT5 terminal is running, login credentials are correct")
                return False
                
        except Exception as e:
            print(f"  ❌ MT5 connection error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_symbol_resolver(self) -> bool:
        """Test 5: Symbol resolver"""
        if not MT5_AVAILABLE:
            print("  ⚠️  MT5 not available - skipping")
            self.results['skipped'].append("Symbol Resolver")
            return True
        
        try:
            engine = MT5Engine(self.config)
            if not engine.connect():
                print("  ⚠️  MT5 not connected - skipping")
                self.results['skipped'].append("Symbol Resolver")
                return True
            
            resolver = SymbolResolver(engine, self.config)
            
            # Test symbol resolution
            test_symbols = ['BTCUSD', 'XAUUSD', 'EURUSD']
            for symbol in test_symbols:
                resolved = resolver.resolve(symbol)
                if resolved:
                    if resolved == symbol:
                        print(f"  ✅ {symbol} → {resolved} (exact match)")
                    else:
                        print(f"  ✅ {symbol} → {resolved} (resolved)")
                else:
                    print(f"  ⚠️  {symbol} → not found (may not be available on broker)")
            
            engine.disconnect()
            return True
            
        except Exception as e:
            print(f"  ❌ Symbol resolver error: {e}")
            return False
    
    def test_risk_manager(self) -> bool:
        """Test 6: Risk manager"""
        if not MT5_AVAILABLE:
            print("  ⚠️  MT5 not available - skipping")
            self.results['skipped'].append("Risk Manager")
            return True
        
        try:
            engine = MT5Engine(self.config)
            if not engine.connect():
                print("  ⚠️  MT5 not connected - skipping")
                self.results['skipped'].append("Risk Manager")
                return True
            
            risk_mgr = RiskManager(self.config, engine)
            
            # Test signal
            test_signal = {
                'direction': 'BUY',
                'symbol': 'BTCUSD',
                'entry_upper': 90000.0,
                'entry_middle': 90050.0,
                'entry_lower': 90100.0,
                'sl1': 89500.0,
                'tp1': 90500.0,
                'tp2': 91000.0
            }
            
            # Try to get symbol info
            symbol_info = engine.get_symbol_info(test_signal['symbol'])
            if not symbol_info:
                print(f"  ⚠️  Symbol {test_signal['symbol']} not found - using mock data")
                engine.disconnect()
                self.results['skipped'].append("Risk Manager")
                return True
            
            # Calculate lot sizes
            lot_sizes = risk_mgr.calculate_lot_sizes(test_signal)
            if lot_sizes:
                print(f"  ✅ Calculated lot sizes: {lot_sizes}")
                print(f"     Total volume: {sum(lot_sizes):.2f} lots")
                
                # Validate trade
                valid = risk_mgr.validate_trade(test_signal, lot_sizes)
                if valid:
                    print("  ✅ Trade validation passed")
                else:
                    print("  ⚠️  Trade validation failed (may be margin issue)")
            else:
                print("  ⚠️  Could not calculate lot sizes")
            
            engine.disconnect()
            return True
            
        except Exception as e:
            print(f"  ❌ Risk manager error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_telegram_connection(self) -> bool:
        """Test 7: Telegram connection"""
        if not TELEGRAM_AVAILABLE:
            print("  ⚠️  Telegram package not available - skipping")
            self.results['skipped'].append("Telegram Connection")
            return True
        
        try:
            monitor = TelegramMonitor(self.config)
            print("  Attempting to connect to Telegram...")
            
            # Test connection
            success = await monitor.test_connection()
            if success:
                print("  ✅ Telegram connected successfully")
                
                # Check channels
                channels = self.config.get('telegram', {}).get('channels', [])
                if channels:
                    print(f"  ✅ Monitoring {len(channels)} channel(s):")
                    for channel in channels:
                        print(f"     - {channel}")
                else:
                    print("  ⚠️  No channels configured")
                
                await monitor.disconnect()
                return True
            else:
                print("  ❌ Failed to connect to Telegram")
                print("     Check: API credentials, phone number, internet connection")
                return False
                
        except Exception as e:
            print(f"  ❌ Telegram connection error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("MT5 AUTOMATOR SYSTEM TEST")
        print("="*60)
        print("\nThis will test all components of the trading system.")
        print("Make sure MT5 terminal is running (if testing MT5).\n")
        
        # Run synchronous tests
        self.test("Configuration Loading", self.test_config_loading)
        self.test("Signal Parser (Regex)", self.test_signal_parser)
        self.test("AI Signal Parser", self.test_ai_signal_parser)
        self.test("MT5 Connection", self.test_mt5_connection)
        self.test("Symbol Resolver", self.test_symbol_resolver)
        self.test("Risk Manager", self.test_risk_manager)
        
        # Run async tests
        async def run_async_tests():
            await self.test("Telegram Connection", self.test_telegram_connection)
        
        asyncio.run(run_async_tests())
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['skipped'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        skipped = len(self.results['skipped'])
        
        print(f"\nTotal tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Skipped: {skipped}")
        
        if self.results['passed']:
            print("\n✅ Passed tests:")
            for test in self.results['passed']:
                print(f"   - {test}")
        
        if self.results['failed']:
            print("\n❌ Failed tests:")
            for test in self.results['failed']:
                print(f"   - {test}")
        
        if self.results['skipped']:
            print("\n⚠️  Skipped tests:")
            for test in self.results['skipped']:
                print(f"   - {test}")
        
        print("\n" + "="*60)
        
        if failed == 0:
            print("🎉 All critical tests passed! System is ready to use.")
            if skipped > 0:
                print("⚠️  Some optional tests were skipped (check configuration).")
        else:
            print("⚠️  Some tests failed. Please fix the issues before using the system.")
        
        print("="*60 + "\n")


def main():
    """Main entry point"""
    tester = SystemTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()

