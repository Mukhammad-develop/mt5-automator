"""
Signal Parser
Interprets trading signals from text and validates them
"""
import re
from typing import Dict, Any, Optional, List
from src.utils import create_class_logger


class SignalParser:
    """
    Parse and validate trading signals
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize signal parser
        
        Args:
            config: Configuration dictionary
        """
        self.logger = create_class_logger('SignalParser')
        self.config = config
        self.trading_config = config.get('trading', {})
        self.default_symbol = self.trading_config.get('default_symbol', 'XAUUSD')
        
        self.logger.info("SignalParser initialized")
    
    def parse_signal(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse trading signal from text
        
        Args:
            text: Signal text (from message or OCR)
            
        Returns:
            Parsed signal dictionary or None if invalid
        """
        try:
            self.logger.info("Parsing signal...")
            self.logger.debug(f"Input text: {text}")
            
            # Extract direction (BUY/SELL)
            direction = self._extract_direction(text)
            if not direction:
                self.logger.warning("Could not determine signal direction")
                return None
            
            # Extract entry levels
            entry_upper, entry_lower = self._extract_entry_range(text)
            if entry_upper is None or entry_lower is None:
                self.logger.warning("Could not extract entry range")
                return None
            
            # If entry range is the same (single entry price), create a spread for staged entry
            # This ensures 3 positions are placed at different levels (upper, middle, lower)
            if entry_upper == entry_lower:
                # Create a spread: for gold, use ~2 pips (0.2) spread
                # For other pairs, adjust based on typical pip size
                spread = 0.2  # Default 2 pips for gold
                entry_upper = entry_upper + spread / 2  # Upper entry
                entry_lower = entry_lower - spread / 2  # Lower entry
                self.logger.info(f"Single entry price detected - created spread: {entry_lower:.2f} - {entry_upper:.2f}")
            
            # Calculate middle entry
            entry_middle = (entry_upper + entry_lower) / 2
            
            # Extract stop losses
            sl1 = self._extract_price(text, ['SL1', 'SL 1', 'STOP LOSS 1', 'STOPLOSS1'])
            sl2 = self._extract_price(text, ['SL2', 'SL 2', 'STOP LOSS 2', 'STOPLOSS2'])
            sl3 = self._extract_price(text, ['SL3', 'SL 3', 'STOP LOSS 3', 'STOPLOSS3'])
            
            # If no labeled SL, try to find SL as single value
            if sl1 is None:
                sl1 = self._extract_price(text, ['SL', 'STOP LOSS', 'STOPLOSS'])
            
            # Extract take profits
            tp1 = self._extract_price(text, ['TP1', 'TP 1', 'TAKE PROFIT 1', 'TAKEPROFIT1', 'TARGET 1'])
            tp2 = self._extract_price(text, ['TP2', 'TP 2', 'TAKE PROFIT 2', 'TAKEPROFIT2', 'TARGET 2'])
            tp3 = self._extract_price(text, ['TP3', 'TP 3', 'TAKE PROFIT 3', 'TAKEPROFIT3', 'TARGET 3'])
            
            # If no labeled TP, try to find TP as single value
            if tp1 is None:
                tp1 = self._extract_price(text, ['TP', 'TAKE PROFIT', 'TAKEPROFIT', 'TARGET'])
            
            # Extract symbol (if present)
            symbol = self._extract_symbol(text) or self.default_symbol
            
            # Build signal dictionary
            signal = {
                'direction': direction,
                'symbol': symbol,
                'entry_upper': entry_upper,
                'entry_middle': entry_middle,
                'entry_lower': entry_lower,
                'sl1': sl1,
                'sl2': sl2,
                'sl3': sl3,
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3,
                'raw_text': text
            }
            
            # Validate signal
            if self._validate_signal(signal):
                self.logger.info(f"Parsed: {direction} {entry_upper}-{entry_lower}, TP1={tp1}, TP2={tp2}, SL={sl1}")
                return signal
            else:
                self.logger.warning("Signal validation failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parsing signal: {e}", exc_info=True)
            return None
    
    def _extract_direction(self, text: str) -> Optional[str]:
        """
        Extract trading direction (BUY/SELL)
        
        Args:
            text: Signal text
            
        Returns:
            'BUY' or 'SELL' or None
        """
        text_upper = text.upper()
        
        # Look for BUY/SELL keywords
        if re.search(r'\bBUY\b', text_upper):
            return 'BUY'
        elif re.search(r'\bSELL\b', text_upper):
            return 'SELL'
        
        return None
    
    def _extract_entry_range(self, text: str) -> tuple:
        """
        Extract entry range (upper and lower levels)
        
        Args:
            text: Signal text
            
        Returns:
            Tuple of (upper, lower) prices or (None, None)
        """
        # Pattern 1: "BUY/SELL 2650.50 - 2648.20"
        pattern1 = r'(?:BUY|SELL)\s+(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)'
        match = re.search(pattern1, text, re.IGNORECASE)
        if match:
            price1 = float(match.group(1))
            price2 = float(match.group(2))
            return (max(price1, price2), min(price1, price2))
        
        # Pattern 2: "Entry: 2650.50 - 2648.20"
        pattern2 = r'ENTRY\s*:?\s*(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)'
        match = re.search(pattern2, text, re.IGNORECASE)
        if match:
            price1 = float(match.group(1))
            price2 = float(match.group(2))
            return (max(price1, price2), min(price1, price2))
        
        # Pattern 3: Two prices on same line after BUY/SELL
        pattern3 = r'(?:BUY|SELL).*?(\d+\.?\d+).*?(\d+\.?\d+)'
        match = re.search(pattern3, text, re.IGNORECASE)
        if match:
            price1 = float(match.group(1))
            price2 = float(match.group(2))
            # Only accept if prices are reasonably close (within 10%)
            if abs(price1 - price2) / max(price1, price2) < 0.1:
                return (max(price1, price2), min(price1, price2))
        
        return (None, None)
    
    def _extract_price(self, text: str, keywords: List[str]) -> Optional[float]:
        """
        Extract price value for specific keywords
        
        Args:
            text: Signal text
            keywords: List of possible keywords (e.g., ['TP1', 'TP 1'])
            
        Returns:
            Price value or None
        """
        for keyword in keywords:
            # Pattern: "KEYWORD: 2650.50" or "KEYWORD 2650.50" or "KEYWORD: 2,650.50"
            pattern = rf'{re.escape(keyword)}\s*:?\s*(\d+[,.]?\d*\.?\d*)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_symbol(self, text: str) -> Optional[str]:
        """
        Extract trading symbol from text
        
        Args:
            text: Signal text
            
        Returns:
            Symbol or None
        """
        # Common forex and commodity symbols
        symbols = [
            'XAUUSD', 'GOLD', 'GBPUSD', 'EURUSD', 'USDJPY', 'AUDUSD',
            'USDCAD', 'NZDUSD', 'USDCHF', 'EURJPY', 'GBPJPY', 'EURGBP',
            'BTCUSD', 'ETHUSD', 'XAGUSD', 'SILVER'
        ]
        
        text_upper = text.upper()
        for symbol in symbols:
            if symbol in text_upper:
                # Normalize gold/silver symbols
                if symbol == 'GOLD':
                    return 'XAUUSD'
                elif symbol == 'SILVER':
                    return 'XAGUSD'
                return symbol
        
        return None
    
    def _validate_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Validate signal data
        
        Args:
            signal: Signal dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            direction = signal['direction']
            entry_upper = signal['entry_upper']
            entry_lower = signal['entry_lower']
            entry_middle = signal['entry_middle']
            tp1 = signal.get('tp1')
            tp2 = signal.get('tp2')
            sl1 = signal.get('sl1')
            
            # Check required fields
            if not all([direction, entry_upper, entry_lower]):
                self.logger.warning("Missing required fields")
                return False
            
            # Check entry range makes sense
            if entry_upper <= entry_lower:
                self.logger.warning(f"Invalid entry range: {entry_upper} <= {entry_lower}")
                return False
            
            # At least TP1 or SL1 should be present
            if tp1 is None and sl1 is None:
                self.logger.warning("Missing both TP and SL")
                return False
            
            # Validate BUY signal
            if direction == 'BUY':
                # TP should be above entry
                if tp1 is not None and tp1 <= entry_upper:
                    self.logger.warning(f"BUY: TP1 ({tp1}) should be above entry ({entry_upper})")
                    return False
                
                # SL should be below entry
                if sl1 is not None and sl1 >= entry_lower:
                    self.logger.warning(f"BUY: SL1 ({sl1}) should be below entry ({entry_lower})")
                    return False
            
            # Validate SELL signal
            elif direction == 'SELL':
                # TP should be below entry
                if tp1 is not None and tp1 >= entry_lower:
                    self.logger.warning(f"SELL: TP1 ({tp1}) should be below entry ({entry_lower})")
                    return False
                
                # SL should be above entry
                if sl1 is not None and sl1 <= entry_upper:
                    self.logger.warning(f"SELL: SL1 ({sl1}) should be above entry ({entry_upper})")
                    return False
            
            # Validate TP order (TP1 < TP2 < TP3 for BUY, reverse for SELL)
            if tp1 is not None and tp2 is not None:
                if direction == 'BUY' and tp2 <= tp1:
                    self.logger.warning(f"BUY: TP2 ({tp2}) should be > TP1 ({tp1})")
                    return False
                elif direction == 'SELL' and tp2 >= tp1:
                    self.logger.warning(f"SELL: TP2 ({tp2}) should be < TP1 ({tp1})")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating signal: {e}")
            return False
    
    def format_signal(self, signal: Dict[str, Any]) -> str:
        """
        Format signal for display
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Formatted string
        """
        lines = [
            f"Direction: {signal['direction']}",
            f"Symbol: {signal['symbol']}",
            f"Entry: {signal['entry_upper']} - {signal['entry_lower']} (mid: {signal['entry_middle']})",
        ]
        
        if signal.get('tp1'):
            lines.append(f"TP1: {signal['tp1']}")
        if signal.get('tp2'):
            lines.append(f"TP2: {signal['tp2']}")
        if signal.get('tp3'):
            lines.append(f"TP3: {signal['tp3']}")
        
        if signal.get('sl1'):
            lines.append(f"SL1: {signal['sl1']}")
        if signal.get('sl2'):
            lines.append(f"SL2: {signal['sl2']}")
        if signal.get('sl3'):
            lines.append(f"SL3: {signal['sl3']}")
        
        return '\n'.join(lines)


def main():
    """
    Test signal parser
    """
    from src.utils import load_config, setup_logging
    
    # Load config
    config = load_config()
    logger = setup_logging(config)
    
    # Create parser
    parser = SignalParser(config)
    
    # Test signals
    test_signals = [
        """
        BUY 2650.50 - 2648.20
        SL1: 2645.00
        SL2: 2643.50
        SL3: 2642.00
        TP1: 2655.00
        TP2: 2660.00
        """,
        """
        SELL XAUUSD
        Entry: 2655 - 2657
        Stop Loss: 2662
        Take Profit 1: 2648
        Take Profit 2: 2640
        """,
        """
        BUY GOLD 2645-2643
        TP1 2650
        TP2 2655
        SL 2640
        """
    ]
    
    for i, test_text in enumerate(test_signals, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"Test Signal {i}")
        logger.info(f"{'='*50}")
        
        signal = parser.parse_signal(test_text)
        
        if signal:
            logger.info("Successfully parsed:")
            logger.info(f"\n{parser.format_signal(signal)}")
        else:
            logger.error("Failed to parse signal")


if __name__ == '__main__':
    main()

