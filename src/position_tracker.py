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
        
        # Breakeven settings (DEPRECATED - use trailing stop instead)
        self.breakeven_enabled = self.trading_config.get('breakeven_enabled', False)
        self.breakeven_trigger = self.trading_config.get('breakeven_trigger', 'middle_entry')
        self.breakeven_offset = self.trading_config.get('breakeven_offset', 5.0)
        
        # Trailing Stop settings (NEW)
        self.trailing_stop_enabled = self.trading_config.get('trailing_stop_enabled', True)
        self.trailing_stop_pips = self.trading_config.get('trailing_stop_pips', 20)
        self.trailing_stop_activation_pips = self.trading_config.get('trailing_stop_activation_pips', 10)
        
        # Position 3 Runner Strategy
        self.position_3_runner_enabled = self.trading_config.get('position_3_runner_enabled', True)
        self.position_3_trailing_after_tp2 = self.trading_config.get('position_3_trailing_after_tp2', True)
        
        # Convert pips to points (for different symbols)
        # For GOLD (XAUUSD): 1 pip = 0.01, so 20 pips = 0.20
        # For Forex: 1 pip = 0.0001, so 20 pips = 0.0020
        # We'll calculate dynamically based on symbol
        
        # Track positions that have been moved to breakeven
        self.breakeven_positions: Set[int] = set()
        
        # Track best prices for trailing stop (highest for BUY, lowest for SELL)
        self.position_best_prices: Dict[int, float] = {}
        
        # Track which Position 3 runners have had TP2 reached (allowed to trail)
        self.position_3_trailing_activated: Set[int] = set()
        
        # Track when TP2 is reached for each signal
        self.tp2_reached_signals: Set[str] = set()
        
        # Track active signals
        self.active_signals: Dict[str, Dict[str, Any]] = {}
        
        if self.trailing_stop_enabled:
            if self.position_3_runner_enabled and self.position_3_trailing_after_tp2:
                self.logger.info(f"PositionTracker initialized: TRAILING STOP enabled, distance={self.trailing_stop_pips} pips")
                self.logger.info(f"🏃 Position 3 RUNNER strategy enabled: Trailing activates AFTER TP2 reached")
            else:
                self.logger.info(f"PositionTracker initialized: TRAILING STOP enabled, distance={self.trailing_stop_pips} pips, activation={self.trailing_stop_activation_pips} pips")
        elif self.breakeven_enabled:
            self.logger.warning(f"PositionTracker initialized: BE enabled (DEPRECATED), trigger={self.breakeven_trigger}, offset={self.breakeven_offset}")
        else:
            self.logger.warning("PositionTracker initialized: No SL management (not recommended)")
    
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

    def get_position_num(self, signal_id: str, ticket: int, comment: str = '') -> Optional[int]:
        """
        Resolve position number using tracked tickets (preferred) or comment fallback.
        """
        tracked = self.active_signals.get(signal_id, {}).get('positions', [])
        for pos in tracked:
            if pos.get('ticket') == ticket:
                return pos.get('position_num')
        if comment and '_pos' in comment:
            try:
                return int(comment.split('_pos')[-1])
            except (ValueError, TypeError):
                return None
        return None
    
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
                # If no open positions, only remove signal if there are no pending orders
                pending_orders = self.mt5_engine.get_pending_orders_by_signal(signal_id)
                if pending_orders:
                    self.logger.info(
                        f"No open positions for signal {signal_id}, but {len(pending_orders)} pending order(s) remain"
                    )
                    return
                
                # All positions closed and no pending orders, remove signal
                self.logger.info(f"All positions closed for signal {signal_id}")
                self.remove_signal(signal_id)
                return
            
            # Get current price
            current_price = self.mt5_engine.get_current_price(signal['symbol'])
            if current_price is None:
                return
            
            # Check if TP2 has been reached (for Position 3 runner strategy)
            if self.position_3_runner_enabled and self.position_3_trailing_after_tp2:
                if signal_id not in self.tp2_reached_signals:
                    await self._check_tp2_reached(signal_id, signal, current_price, direction, positions)
            
            # Check trailing stop (preferred) or breakeven for each position
            if self.trailing_stop_enabled:
                for position in positions:
                    await self._check_trailing_stop(position, signal, current_price, direction, signal_id)
            elif self.breakeven_enabled:
                for position in positions:
                    await self._check_breakeven(position, signal, current_price, direction)
            
        except Exception as e:
            self.logger.error(f"Error checking signal positions: {e}")
    
    async def _check_tp2_reached(self, signal_id: str, signal: Dict[str, Any], 
                                 current_price: float, direction: str, positions: List[Dict[str, Any]]):
        """
        Check if TP2 price has been reached and activate trailing for Position 3
        
        Args:
            signal_id: Signal ID
            signal: Signal dictionary
            current_price: Current market price
            direction: Trade direction
            positions: List of open positions
        """
        try:
            tp2_price = signal.get('tp2')
            if not tp2_price:
                return
            
            # Check if TP2 price has been reached
            tp2_reached = False
            
            if direction == 'BUY':
                # For BUY, check if price reached TP2 (above TP2)
                if current_price >= tp2_price:
                    tp2_reached = True
            else:  # SELL
                # For SELL, check if price reached TP2 (below TP2)
                if current_price <= tp2_price:
                    tp2_reached = True
            
            # Fallback: check history if TP2 was hit and price has already retraced
            if not tp2_reached and hasattr(self.mt5_engine, 'was_tp_hit'):
                tp2_reached = self.mt5_engine.was_tp_hit(
                    signal_id=signal_id,
                    symbol=signal.get('symbol'),
                    tp_price=tp2_price,
                    direction=direction,
                    position_num=2
                )
            
            if tp2_reached:
                self.activate_position_3_trailing(signal_id, current_price=current_price, signal=signal)
        
        except Exception as e:
            self.logger.error(f"Error checking TP2 reached: {e}", exc_info=True)

    def activate_position_3_trailing(self, signal_id: str, current_price: float = None,
                                     signal: Dict[str, Any] = None) -> bool:
        """
        Activate trailing stop for Position 3 after TP2 is reached.
        """
        try:
            signal_info = {'signal': signal} if signal else self.get_signal_info(signal_id)
            if not signal_info:
                return False
            
            signal = signal_info.get('signal', {})
            tp2_price = signal.get('tp2')
            direction = signal.get('direction', '')
            if not tp2_price or not direction:
                return False
            
            positions = self.mt5_engine.get_positions_by_signal(signal_id)
            if not positions:
                return False
            
            # Mark TP2 reached for the signal
            self.tp2_reached_signals.add(signal_id)
            
            for position in positions:
                comment = position.get('comment', '')
                pos_num = self.get_position_num(signal_id, position['ticket'], comment)
                if pos_num != 3:
                    continue
                
                ticket = position['ticket']
                if ticket in self.position_3_trailing_activated:
                    return True
                
                # Calculate pip value for trailing distance
                symbol = signal.get('symbol', '')
                if 'XAU' in symbol or 'GOLD' in symbol or 'BTC' in symbol:
                    pip_value = 0.01
                elif 'JPY' in symbol:
                    pip_value = 0.01
                else:
                    pip_value = 0.0001
                
                trailing_distance = self.trailing_stop_pips * pip_value
                
                if direction == 'BUY':
                    new_sl = tp2_price - trailing_distance
                else:
                    new_sl = tp2_price + trailing_distance
                
                tp2_or_current = current_price if current_price is not None else tp2_price
                self.position_best_prices[ticket] = tp2_or_current
                
                if self.mt5_engine.modify_position(ticket, sl=new_sl):
                    self.position_3_trailing_activated.add(ticket)
                    self.logger.warning(
                        f"🏃 Position 3 #{ticket} RUNNER activated - SL set to {new_sl} "
                        f"(TP2 {tp2_price} - {self.trailing_stop_pips} pips)"
                    )
                    return True
                
                self.logger.error(f"❌ Failed to set trailing stop for Position 3 #{ticket}")
                return False
            
            return False
        except Exception as e:
            self.logger.error(f"Error activating Position 3 trailing: {e}", exc_info=True)
            return False
    
    async def _check_trailing_stop(self, position: Dict[str, Any], signal: Dict[str, Any],
                                   current_price: float, direction: str, signal_id: str = None):
        """
        Check and apply trailing stop logic
        
        Args:
            position: Position dictionary
            signal: Signal dictionary
            current_price: Current market price
            direction: Trade direction (BUY/SELL)
            signal_id: Signal ID (optional, for Position 3 runner check)
        """
        try:
            ticket = position['ticket']
            entry_price = position['open_price']
            current_sl = position.get('sl', 0)
            symbol = signal['symbol']
            comment = position.get('comment', '')
            
            # Check if this is Position 3 with runner strategy
            pos_num = self.get_position_num(signal_id, ticket, comment)
            is_position_3 = pos_num == 3
            if self.position_3_runner_enabled and self.position_3_trailing_after_tp2 and not is_position_3:
                # Only Position 3 should ever trail in runner mode
                return
            tp2_reached_for_position_3 = False
            if is_position_3 and self.position_3_runner_enabled and self.position_3_trailing_after_tp2:
                # Position 3: Only trail if TP2 has been reached
                if ticket not in self.position_3_trailing_activated:
                    # TP2 not reached yet, don't trail
                    return
                tp2_reached_for_position_3 = True  # Skip activation_distance check for Position 3 after TP2
            
            # Calculate pip value based on symbol
            # For GOLD (XAUUSD): 1 pip = 0.01
            # For BTC: 1 pip = 0.01 (similar to gold)
            # For Forex pairs: 1 pip = 0.0001 (except JPY pairs: 0.01)
            if 'XAU' in symbol or 'GOLD' in symbol or 'BTC' in symbol:
                pip_value = 0.01
            elif 'JPY' in symbol:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            # Convert pips to price points
            trailing_distance = self.trailing_stop_pips * pip_value
            activation_distance = self.trailing_stop_activation_pips * pip_value
            
            # Calculate current profit in pips
            if direction == 'BUY':
                profit_distance = current_price - entry_price
            else:  # SELL
                profit_distance = entry_price - current_price
            
            # Check if position is profitable enough to activate trailing stop
            # SKIP this check for Position 3 after TP2 is reached (already activated)
            if not tp2_reached_for_position_3 and profit_distance < activation_distance:
                # Not enough profit yet, don't trail
                return
            
            # Initialize or update best price for this position
            if ticket not in self.position_best_prices:
                # First time tracking this position
                self.position_best_prices[ticket] = current_price
                self.logger.info(f"📊 Trailing stop activated for #{ticket} (profit: {profit_distance/pip_value:.1f} pips)")
            
            # Update best price
            if direction == 'BUY':
                # For BUY: Track highest price
                if current_price > self.position_best_prices[ticket]:
                    self.position_best_prices[ticket] = current_price
                    self.logger.debug(f"New high for BUY #{ticket}: {current_price}")
            else:  # SELL
                # For SELL: Track lowest price
                if current_price < self.position_best_prices[ticket]:
                    self.position_best_prices[ticket] = current_price
                    self.logger.debug(f"New low for SELL #{ticket}: {current_price}")
            
            # Calculate new SL based on best price
            best_price = self.position_best_prices[ticket]
            
            if direction == 'BUY':
                # For BUY: SL should be trailing_distance BELOW best price
                new_sl = best_price - trailing_distance
                # Only move SL UP (never down)
                should_move = not current_sl or current_sl == 0 or new_sl > current_sl
            else:  # SELL
                # For SELL: SL should be trailing_distance ABOVE best price
                new_sl = best_price + trailing_distance
                # Only move SL DOWN (never up)
                should_move = not current_sl or current_sl == 0 or new_sl < current_sl
            
            if should_move:
                # Validate SL distance against broker's minimum stop level
                symbol_info = self.mt5_engine.get_symbol_info(symbol)
                if symbol_info:
                    # Get broker's minimum stop level
                    import MetaTrader5 as mt5
                    mt5_symbol_info = mt5.symbol_info(symbol)
                    if mt5_symbol_info:
                        stop_level = mt5_symbol_info.trade_stops_level * mt5_symbol_info.point
                        if stop_level > 0:
                            # Check if new_sl meets minimum distance requirement
                            if direction == 'BUY':
                                # For BUY: SL must be at least stop_level below current price
                                min_sl = current_price - stop_level
                                if new_sl > min_sl:
                                    # SL too close to current price, skip update
                                    self.logger.debug(f"Trailing stop SL {new_sl} too close to current {current_price} (min distance: {stop_level:.2f}) - skipping")
                                    return
                            else:  # SELL
                                # For SELL: SL must be at least stop_level above current price
                                max_sl = current_price + stop_level
                                if new_sl < max_sl:
                                    # SL too close to current price, skip update
                                    self.logger.debug(f"Trailing stop SL {new_sl} too close to current {current_price} (min distance: {stop_level:.2f}) - skipping")
                                    return
                
                # Move SL
                success = self.mt5_engine.modify_position(ticket, sl=new_sl)
                
                if success:
                    profit_locked = (new_sl - entry_price) if direction == 'BUY' else (entry_price - new_sl)
                    profit_pips = profit_locked / pip_value
                    self.logger.warning(f"🔒 Trailing Stop moved for #{ticket}: SL={new_sl:.2f} (locking {profit_pips:.1f} pips profit)")
                else:
                    self.logger.warning(f"Failed to update trailing stop for #{ticket}")
        
        except Exception as e:
            self.logger.error(f"Error checking trailing stop: {e}", exc_info=True)
    
    async def _check_breakeven(self, position: Dict[str, Any], signal: Dict[str, Any],
                               current_price: float, direction: str):
        """
        Check and apply breakeven logic (DEPRECATED - use trailing stop instead)
        
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
            
            direction = signal['direction']
            
            # Get current price - use ASK for BUY, BID for SELL
            # For BUY: we buy at ASK, so check ASK price
            # For SELL: we sell at BID, so check BID price
            if direction == 'BUY':
                current_price = self.mt5_engine.get_current_price(signal['symbol'], 'ask')
            else:  # SELL
                current_price = self.mt5_engine.get_current_price(signal['symbol'], 'bid')
            
            if current_price is None:
                return False
            
            # Check if TP reached
            if direction == 'BUY':
                # For BUY, TP is above entry, check if ASK price reached it
                if current_price >= tp_price:
                    self.logger.info(f"TP{tp_level} reached for signal {signal_id}: price={current_price}, tp={tp_price}")
                    return True
            else:  # SELL
                # For SELL, TP is below entry, check if BID price reached it
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
