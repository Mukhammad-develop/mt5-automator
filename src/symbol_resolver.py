"""
Symbol Resolver - Automatically detect broker-specific symbol names
"""
import json
import os
from typing import Optional, Dict, Any, List
from src.utils import create_class_logger


class SymbolResolver:
    """
    Automatically resolves signal symbols to broker-specific symbol names
    """
    
    def __init__(self, mt5_engine, config: Dict[str, Any]):
        """
        Initialize symbol resolver
        
        Args:
            mt5_engine: MT5 engine instance
            config: Configuration dictionary
        """
        self.logger = create_class_logger('SymbolResolver')
        self.mt5_engine = mt5_engine
        self.config = config
        
        # Cache file for resolved symbols
        self.cache_file = 'data/symbol_mapping_cache.json'
        self.cache = self._load_cache()
        
        # Common symbol variations to try
        self.common_variations = {
            'XAUUSD': ['XAUUSD', 'XAUUSD+', 'XAUUSD.', 'XAUUSDm', '#XAUUSD', 'GOLD', 'GOLDm', 'GOLD.'],
            'EURUSD': ['EURUSD', 'EURUSD+', 'EURUSD.', 'EURUSDm', '#EURUSD', 'EURUSD.a', 'EURUSDc'],
            'GBPUSD': ['GBPUSD', 'GBPUSD+', 'GBPUSD.', 'GBPUSDm', '#GBPUSD', 'GBPUSD.a', 'GBPUSDc'],
            'USDJPY': ['USDJPY', 'USDJPY+', 'USDJPY.', 'USDJPYm', '#USDJPY', 'USDJPY.a', 'USDJPYc'],
            'AUDUSD': ['AUDUSD', 'AUDUSD+', 'AUDUSD.', 'AUDUSDm', '#AUDUSD', 'AUDUSD.a', 'AUDUSDc'],
            'USDCAD': ['USDCAD', 'USDCAD+', 'USDCAD.', 'USDCADm', '#USDCAD', 'USDCAD.a', 'USDCADc'],
            'NZDUSD': ['NZDUSD', 'NZDUSD+', 'NZDUSD.', 'NZDUSDm', '#NZDUSD', 'NZDUSD.a', 'NZDUSDc'],
            'USDCHF': ['USDCHF', 'USDCHF+', 'USDCHF.', 'USDCHFm', '#USDCHF', 'USDCHF.a', 'USDCHFc'],
            'EURJPY': ['EURJPY', 'EURJPY+', 'EURJPY.', 'EURJPYm', '#EURJPY', 'EURJPY.a', 'EURJPYc'],
            'GBPJPY': ['GBPJPY', 'GBPJPY+', 'GBPJPY.', 'GBPJPYm', '#GBPJPY', 'GBPJPY.a', 'GBPJPYc'],
            'EURGBP': ['EURGBP', 'EURGBP+', 'EURGBP.', 'EURGBPm', '#EURGBP', 'EURGBP.a', 'EURGBPc'],
            'XAGUSD': ['XAGUSD', 'XAGUSD+', 'XAGUSD.', 'XAGUSDm', '#XAGUSD', 'SILVER', 'SILVERm', 'SILVER.'],
            'BTCUSD': ['BTCUSD', 'BTCUSD+', 'BTCUSD.', 'BTCUSDm', '#BTCUSD', 'BITCOIN'],
            'ETHUSD': ['ETHUSD', 'ETHUSD+', 'ETHUSD.', 'ETHUSDm', '#ETHUSD', 'ETHEREUM'],
        }
        
        self.logger.info("SymbolResolver initialized")
    
    def _load_cache(self) -> Dict[str, str]:
        """Load symbol mapping cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    self.logger.info(f"Loaded {len(cache)} cached symbol mappings")
                    return cache
            except Exception as e:
                self.logger.warning(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save symbol mapping cache to file"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            self.logger.debug("Symbol mapping cache saved")
        except Exception as e:
            self.logger.warning(f"Error saving cache: {e}")
    
    def resolve(self, signal_symbol: str) -> str:
        """
        Resolve signal symbol to broker-specific symbol
        
        Args:
            signal_symbol: Symbol from signal (e.g., XAUUSD)
            
        Returns:
            Broker-specific symbol (e.g., XAUUSD+)
        """
        # Normalize symbol
        signal_symbol = signal_symbol.upper().strip()
        
        # Check cache first
        if signal_symbol in self.cache:
            self.logger.debug(f"Symbol from cache: {signal_symbol} → {self.cache[signal_symbol]}")
            return self.cache[signal_symbol]
        
        # Try to resolve
        broker_symbol = self._resolve_symbol(signal_symbol)
        
        if broker_symbol:
            # Cache the result
            self.cache[signal_symbol] = broker_symbol
            self._save_cache()
            self.logger.info(f"✅ Symbol resolved: {signal_symbol} → {broker_symbol}")
            return broker_symbol
        else:
            # Fallback to original
            self.logger.warning(f"⚠️ Could not resolve symbol: {signal_symbol}, using as-is")
            return signal_symbol
    
    def _resolve_symbol(self, signal_symbol: str) -> Optional[str]:
        """
        Try to resolve symbol using various methods
        
        Args:
            signal_symbol: Symbol from signal
            
        Returns:
            Broker symbol or None
        """
        # Method 1: Try exact match
        if self._check_symbol_exists(signal_symbol):
            return signal_symbol
        
        # Method 2: Try common variations
        variations = self.common_variations.get(signal_symbol, [])
        for variation in variations:
            if self._check_symbol_exists(variation):
                self.logger.info(f"Found variation: {signal_symbol} → {variation}")
                return variation
        
        # Method 3: Try with common suffixes
        common_suffixes = ['+', '.', 'm', '#', '.a', '.b', '.c', '_raw', '_ecn']
        for suffix in common_suffixes:
            test_symbol = signal_symbol + suffix
            if self._check_symbol_exists(test_symbol):
                self.logger.info(f"Found with suffix: {signal_symbol} → {test_symbol}")
                return test_symbol
        
        # Method 4: Search in all available symbols
        broker_symbol = self._search_all_symbols(signal_symbol)
        if broker_symbol:
            return broker_symbol
        
        return None
    
    def _check_symbol_exists(self, symbol: str) -> bool:
        """
        Check if symbol exists in MT5
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if symbol exists
        """
        try:
            symbol_info = self.mt5_engine.get_symbol_info(symbol)
            return symbol_info is not None
        except Exception as e:
            self.logger.debug(f"Symbol check failed for {symbol}: {e}")
            return False
    
    def _search_all_symbols(self, signal_symbol: str) -> Optional[str]:
        """
        Search through all available symbols for a match
        
        Args:
            signal_symbol: Symbol from signal
            
        Returns:
            Best matching broker symbol or None
        """
        try:
            import MetaTrader5 as mt5
            
            # Get all symbols
            symbols = mt5.symbols_get()
            if not symbols:
                return None
            
            signal_base = signal_symbol.replace('/', '').replace('-', '').upper()
            
            # Look for symbols containing the base
            matches = []
            for sym in symbols:
                sym_name = sym.name.upper()
                if signal_base in sym_name or sym_name in signal_base:
                    matches.append(sym.name)
            
            if matches:
                # Prefer shorter names (usually more standard)
                matches.sort(key=len)
                best_match = matches[0]
                self.logger.info(f"Found in symbol search: {signal_symbol} → {best_match}")
                return best_match
            
        except Exception as e:
            self.logger.error(f"Error searching symbols: {e}")
        
        return None
    
    def clear_cache(self):
        """Clear the symbol mapping cache"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.logger.info("Symbol mapping cache cleared")
    
    def get_cache(self) -> Dict[str, str]:
        """Get current cache contents"""
        return self.cache.copy()

