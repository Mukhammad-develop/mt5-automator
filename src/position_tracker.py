"""
Position Tracker
Monitors open positions and manages breakeven and TP/SL logic
"""
import asyncio
from typing import Dict, Any, Set, List
from datetime import datetime
from src.utils import create_class_logger


class PositionTracker:
    """
    Track and manage open positions
    """
    
    def __init__(self, config: Dict[str, Any], mt5_engine):
        """
        Initialize position tracker
        
        Args:
            config: Configuration dictionary
            mt5_engine: MT5Engine instance
        """
        self.logger = create_class_logger('PositionTracker')
        self.config = config
        self.trading_config = config.get('trading', {})
        self.mt5_engine = mt5_engine
        
        # Breakeven settings
        self.breakeven_enabled = self.trading_config.get('breakeven_enabled', False)
        self.breakeven_trigger = self.trading_config.get('breakeven_trigger', 'middle_entry')
        self.breakeven_offset = self.trading_config.get('breakeven_offset', 5.0)
        
        # Track positions that have been moved to breakeven
        self.breakeven_positions: Set[int] = set()
        
        # Track active signals
        self.active_signals: Dict[str, Dict[str, Any]] = {}
        
        if self.breakeven_enabled:
            self.logger.info(f"PositionTracker initialized: BE enabled, trigger={self.breakeven_trigger}, offset={self.breakeven_offset}")
        else:
            self.logger.info("PositionTracker initialized: Breakeven DISABLED")
    
    def register_signal(self, signal_id: str, signal: Dict[str, Any]):
        """
        Register a new signal for tracking
        
        Args:
            signal_id: Unique signal ID
            signal: Signal dictionary
        """
        self.active_signals[signal_id] = {
            'signal': signal,
            'positions': [],
            'registered_at': datetime.now().isoformat()
        }
        self.logger.info(f"Registered signal {signal_id} for tracking")
    
    def add_position(self, signal_id: str, ticket: int, position_num: int):
        """
        Add position to tracking
        
        Args:
            signal_id: Signal ID
            ticket: Position ticket
            position_num: Position number (1, 2, 3)
        """
        if signal_id in self.active_signals:
            self.active_signals[signal_id]['positions'].append({
                'ticket': ticket,
                'position_num': position_num,
                'opened_at': datetime.now().isoformat()
            })
            self.logger.info(f"Added position #{ticket} to signal {signal_id}")
    
    def remove_signal(self, signal_id: str):
        """
        Remove signal from tracking
        
        Args:
            signal_id: Signal ID
        """
        if signal_id in self.active_signals:
            del self.active_signals[signal_id]
            self.logger.info(f"Removed signal {signal_id} from tracking")
    
    async def monitor_positions(self, check_interval: int = 5):
        """
        Monitor all tracked positions (runs continuously)
        
        Args:
            check_interval: Check interval in seconds
        """
        self.logger.info("Starting position monitoring...")
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                if not self.active_signals:
                    continue
                
                # Check each active signal
                for signal_id, signal_data in list(self.active_signals.items()):
                    await self._check_signal_positions(signal_id, signal_data)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(check_interval)
    
    async def _check_signal_positions(self, signal_id: str, signal_data: Dict[str, Any]):
        """
        Check positions for a specific signal
        
        Args:
            signal_id: Signal ID
            signal_data: Signal data dictionary
        """
        try:
            signal = signal_data['signal']
            direction = signal['direction']
            
            # Get current positions from MT5
            positions = self.mt5_engine.get_positions_by_signal(signal_id)
            
            if not positions:
                # All positions closed, remove signal
                self.logger.info(f"All positions closed for signal {signal_id}")
                self.remove_signal(signal_id)
                return
            
            # Get current price
            current_price = self.mt5_engine.get_current_price(signal['symbol'])
            if current_price is None:
                return
            
            # Check breakeven for each position
            for position in positions:
                await self._check_breakeven(position, signal, current_price, direction)
            
        except Exception as e:
            self.logger.error(f"Error checking signal positions: {e}")
    
    async def _check_breakeven(self, position: Dict[str, Any], signal: Dict[str, Any],
                               current_price: float, direction: str):
        """
        Check and apply breakeven logic
        
        Args:
            position: Position dictionary
            signal: Signal dictionary
            current_price: Current market price
            direction: Trade direction (BUY/SELL)
        """
        try:
            # Skip if breakeven is disabled
            if not self.breakeven_enabled:
                return
            
            ticket = position['ticket']
            
            # Skip if already at breakeven
            if ticket in self.breakeven_positions:
                return
            
            # Determine breakeven trigger price
            if self.breakeven_trigger == 'middle_entry':
                trigger_price = signal['entry_middle']
            elif self.breakeven_trigger == 'lower_entry':
                trigger_price = signal['entry_lower'] if direction == 'BUY' else signal['entry_upper']
            else:
                return
            
            # Check if price has reached trigger
            price_reached_trigger = False
            
            if direction == 'BUY':
                # For BUY, price should go above middle entry + offset
                if current_price >= trigger_price + self.breakeven_offset:
                    price_reached_trigger = True
                    self.logger.info(f"BE trigger reached for #{ticket}: current={current_price}, trigger={trigger_price}, offset={self.breakeven_offset}")
            else:  # SELL
                # For SELL, price should go below middle entry - offset
                if current_price <= trigger_price - self.breakeven_offset:
                    price_reached_trigger = True
                    self.logger.info(f"BE trigger reached for #{ticket}: current={current_price}, trigger={trigger_price}, offset={self.breakeven_offset}")
            
            # Additional check: Only move if position is actually in profit
            if price_reached_trigger:
                entry_price = position['open_price']
                is_in_profit = False
                
                if direction == 'BUY':
                    # For BUY, current price should be above entry
                    if current_price > entry_price + self.breakeven_offset:
                        is_in_profit = True
                else:  # SELL
                    # For SELL, current price should be below entry
                    if current_price < entry_price - self.breakeven_offset:
                        is_in_profit = True
                
                if not is_in_profit:
                    self.logger.debug(f"Position #{ticket} not in enough profit yet for BE: entry={entry_price}, current={current_price}")
                    return
            
            if price_reached_trigger:
                # Move SL to breakeven (entry price + small offset for commission)
                entry_price = position['open_price']
                
                # Add small buffer for spread/commission
                if direction == 'BUY':
                    new_sl = entry_price + 0.1
                else:
                    new_sl = entry_price - 0.1
                
                # Only move if new SL is better than current
                current_sl = position['sl']
                should_move = False
                
                if direction == 'BUY':
                    if not current_sl or current_sl == 0 or new_sl > current_sl:
                        should_move = True
                else:  # SELL
                    if not current_sl or current_sl == 0 or new_sl < current_sl:
                        should_move = True
                
                if should_move:
                    success = self.mt5_engine.modify_position(ticket, sl=new_sl)
                    
                    if success:
                        self.breakeven_positions.add(ticket)
                        self.logger.info(f"Moved position #{ticket} to breakeven: SL={new_sl}")
                    else:
                        self.logger.warning(f"Failed to move position #{ticket} to breakeven")
        
        except Exception as e:
            self.logger.error(f"Error checking breakeven: {e}")
    
    def get_active_signal_count(self) -> int:
        """
        Get number of active signals
        
        Returns:
            Number of active signals
        """
        return len(self.active_signals)
    
    def get_signal_info(self, signal_id: str) -> Dict[str, Any]:
        """
        Get information about a specific signal
        
        Args:
            signal_id: Signal ID
            
        Returns:
            Signal info dictionary or empty dict
        """
        return self.active_signals.get(signal_id, {})
    
    def get_all_active_signals(self) -> List[str]:
        """
        Get list of all active signal IDs
        
        Returns:
            List of signal IDs
        """
        return list(self.active_signals.keys())
    
    def check_tp_hit(self, signal_id: str, tp_level: int) -> bool:
        """
        Check if TP level has been hit for any position in signal
        
        Args:
            signal_id: Signal ID
            tp_level: TP level (1 or 2)
            
        Returns:
            True if TP has been hit
        """
        try:
            if signal_id not in self.active_signals:
                return False
            
            signal = self.active_signals[signal_id]['signal']
            tp_price = signal.get(f'tp{tp_level}')
            
            if tp_price is None:
                return False
            
            # Get current positions
            positions = self.mt5_engine.get_positions_by_signal(signal_id)
            
            # Get current price
            current_price = self.mt5_engine.get_current_price(signal['symbol'])
            if current_price is None:
                return False
            
            direction = signal['direction']
            
            # Check if TP reached
            if direction == 'BUY':
                # For BUY, TP is above entry, check if price reached it
                if current_price >= tp_price:
                    self.logger.info(f"TP{tp_level} reached for signal {signal_id}: price={current_price}, tp={tp_price}")
                    return True
            else:  # SELL
                # For SELL, TP is below entry, check if price reached it
                if current_price <= tp_price:
                    self.logger.info(f"TP{tp_level} reached for signal {signal_id}: price={current_price}, tp={tp_price}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking TP hit: {e}")
            return False


def main():
    """
    Test position tracker
    """
    import asyncio
    from src.utils import load_config, setup_logging
    from src.mt5_engine import MT5Engine
    
    async def test():
        # Load config
        config = load_config()
        logger = setup_logging(config)
        
        # Create MT5 engine
        engine = MT5Engine(config)
        
        if not engine.connect():
            logger.error("Failed to connect to MT5")
            return
        
        # Create position tracker
        tracker = PositionTracker(config, engine)
        
        # Test signal
        test_signal = {
            'direction': 'BUY',
            'symbol': 'XAUUSD',
            'entry_upper': 2650.50,
            'entry_middle': 2649.35,
            'entry_lower': 2648.20,
            'sl1': 2645.00,
            'tp1': 2655.00,
            'tp2': 2660.00
        }
        
        signal_id = 'test_signal_001'
        
        # Register signal
        tracker.register_signal(signal_id, test_signal)
        
        # Monitor for a short time
        logger.info("Monitoring positions for 30 seconds...")
        
        try:
            await asyncio.wait_for(tracker.monitor_positions(check_interval=5), timeout=30)
        except asyncio.TimeoutError:
            logger.info("Monitoring test completed")
        
        engine.disconnect()
    
    asyncio.run(test())


if __name__ == '__main__':
    main()

