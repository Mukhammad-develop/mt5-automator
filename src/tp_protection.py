"""
TP2 Protection System
Manages TP2 protection logic to prevent new entries after TP2 is hit
"""
import asyncio
from typing import Dict, Any, Set
from datetime import datetime
from src.utils import create_class_logger, update_signal_status


class TP2Protection:
    """
    TP2 Protection System
    
    When TP2 is hit:
    - Cancel all pending orders for that signal
    - Block new orders from being placed
    - Allow existing positions to continue
    """
    
    def __init__(self, config: Dict[str, Any], mt5_engine, position_tracker):
        """
        Initialize TP2 protection
        
        Args:
            config: Configuration dictionary
            mt5_engine: MT5Engine instance
            position_tracker: PositionTracker instance
        """
        self.logger = create_class_logger('TP2Protection')
        self.config = config
        self.mt5_engine = mt5_engine
        self.position_tracker = position_tracker
        
        # TP2 settings
        self.trading_config = config.get('trading', {})
        self.tp2_move_to_breakeven = self.trading_config.get('tp2_move_to_breakeven', True)
        
        # Track signals with TP2 protection active
        self.protected_signals: Set[str] = set()
        
        # Track when protection was activated
        self.protection_timestamps: Dict[str, str] = {}
        
        if self.tp2_move_to_breakeven:
            self.logger.info("TP2Protection initialized: Will move positions to BE when TP2 hit")
        else:
            self.logger.info("TP2Protection initialized: Will NOT move positions to BE")
    
    def is_protected(self, signal_id: str) -> bool:
        """
        Check if signal has TP2 protection active
        
        Args:
            signal_id: Signal ID
            
        Returns:
            True if protected
        """
        return signal_id in self.protected_signals
    
    def activate_protection(self, signal_id: str, move_to_breakeven: bool = True) -> bool:
        """
        Activate TP2 protection for a signal
        
        Args:
            signal_id: Signal ID
            move_to_breakeven: Whether to move remaining positions' SL to breakeven
            
        Returns:
            True if protection activated successfully
        """
        try:
            self.logger.warning(f"Activating TP2 protection for signal {signal_id}")
            
            # Cancel all pending orders for this signal (CRITICAL: Must cancel LIMIT orders when TP2 reached)
            pending_orders = self.mt5_engine.get_pending_orders_by_signal(signal_id)
            
            if pending_orders:
                self.logger.warning(f"🛡️ TP2 Protection: Found {len(pending_orders)} pending order(s) to cancel for signal {signal_id}")
            
            cancelled_count = 0
            for order in pending_orders:
                order_price = order.get('price_open', 'N/A')
                if self.mt5_engine.cancel_pending_order(order['ticket']):
                    cancelled_count += 1
                    self.logger.warning(f"✅ Cancelled pending LIMIT order #{order['ticket']} at {order_price} (TP2 reached)")
                else:
                    self.logger.error(f"❌ Failed to cancel pending order #{order['ticket']} at {order_price}")
            
            if cancelled_count > 0:
                self.logger.warning(f"🛡️ Successfully cancelled {cancelled_count} pending LIMIT order(s) for signal {signal_id}")
            elif pending_orders:
                self.logger.error(f"❌ Failed to cancel any pending orders for signal {signal_id} (check MT5 connection)")
            
            # Move remaining positions to breakeven (protect profits)
            if move_to_breakeven:
                self._move_positions_to_breakeven(signal_id)
            
            # Add to protected set
            self.protected_signals.add(signal_id)
            self.protection_timestamps[signal_id] = datetime.now().isoformat()
            
            # Mark signal as TP2 hit in database (prevents re-entry even after restart)
            if update_signal_status(signal_id, 'tp2_hit'):
                self.logger.info(f"✅ Signal {signal_id} marked as 'tp2_hit' in database")
            
            self.logger.warning(f"🛡️ TP2 PROTECTION ACTIVE for signal {signal_id} (will NOT re-enter if posted again)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error activating TP2 protection: {e}", exc_info=True)
            return False
    
    def _move_positions_to_breakeven(self, signal_id: str):
        """
        Move remaining positions to breakeven (EXCEPT Position 3 runner)
        
        Position 3 (runner) should NOT be moved to breakeven - it uses trailing stop instead
        
        Args:
            signal_id: Signal ID
        """
        try:
            # Get signal info
            signal_info = self.position_tracker.get_signal_info(signal_id)
            if not signal_info:
                return
            
            signal = signal_info.get('signal', {})
            direction = signal.get('direction', '')
            
            # Check if Position 3 Runner is enabled
            position_3_runner_enabled = self.trading_config.get('position_3_runner_enabled', True)
            
            # Get open positions
            positions = self.mt5_engine.get_positions_by_signal(signal_id)
            
            if not positions:
                self.logger.info(f"No open positions to move to BE for signal {signal_id}")
                return
            
            moved_count = 0
            skipped_position_3 = 0
            
            for position in positions:
                # Check if this is Position 3 (runner) - skip it!
                comment = position.get('comment', '')
                if '_pos3' in comment and position_3_runner_enabled:
                    self.logger.info(f"⏭️ Skipping Position 3 #{position['ticket']} - uses trailing stop, not breakeven")
                    skipped_position_3 += 1
                    continue
                
                entry_price = position['open_price']
                current_sl = position.get('sl', 0)
                
                # Calculate breakeven SL (entry + small buffer for spread/commission)
                if direction == 'BUY':
                    new_sl = entry_price + 0.1
                    # Only move if new SL is better than current
                    if not current_sl or current_sl == 0 or new_sl > current_sl:
                        if self.mt5_engine.modify_position(position['ticket'], sl=new_sl):
                            self.logger.info(f"✅ Moved position #{position['ticket']} to BE: SL={new_sl} (TP2 protection)")
                            moved_count += 1
                        else:
                            self.logger.warning(f"Failed to move position #{position['ticket']} to BE")
                else:  # SELL
                    new_sl = entry_price - 0.1
                    # Only move if new SL is better than current
                    if not current_sl or current_sl == 0 or new_sl < current_sl:
                        if self.mt5_engine.modify_position(position['ticket'], sl=new_sl):
                            self.logger.info(f"✅ Moved position #{position['ticket']} to BE: SL={new_sl} (TP2 protection)")
                            moved_count += 1
                        else:
                            self.logger.warning(f"Failed to move position #{position['ticket']} to BE")
            
            if moved_count > 0:
                self.logger.warning(f"🛡️ Moved {moved_count} position(s) to BREAKEVEN (TP2 protection)")
            if skipped_position_3 > 0:
                self.logger.info(f"🏃 Position 3 runner(s) skipped - using trailing stop instead of breakeven")
            
        except Exception as e:
            self.logger.error(f"Error moving positions to breakeven: {e}", exc_info=True)
    
    def deactivate_protection(self, signal_id: str):
        """
        Deactivate TP2 protection (when all positions closed)
        
        Args:
            signal_id: Signal ID
        """
        if signal_id in self.protected_signals:
            self.protected_signals.discard(signal_id)
            
            if signal_id in self.protection_timestamps:
                activated_at = self.protection_timestamps[signal_id]
                self.logger.info(f"TP2 protection deactivated for signal {signal_id} (was active since {activated_at})")
                del self.protection_timestamps[signal_id]
    
    async def monitor_tp2(self, check_interval: int = 5):
        """
        Monitor for TP2 hits (runs continuously)
        
        Args:
            check_interval: Check interval in seconds
        """
        self.logger.info("Starting TP2 monitoring...")
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Get all active signals
                active_signals = self.position_tracker.get_all_active_signals()
                
                if not active_signals:
                    continue
                
                # Check each signal for TP2 hit
                for signal_id in active_signals:
                    # Skip if already protected
                    if self.is_protected(signal_id):
                        # Check if all positions are closed
                        positions = self.mt5_engine.get_positions_by_signal(signal_id)
                        if not positions:
                            self.deactivate_protection(signal_id)
                        continue
                    
                    # Check if TP2 has been hit (even if no positions exist yet)
                    # This handles case where market reaches TP2 before any positions open
                    # In that case, we should cancel all pending LIMIT orders
                    if self.position_tracker.check_tp_hit(signal_id, tp_level=2):
                        # Check if there are pending orders to cancel
                        pending_orders = self.mt5_engine.get_pending_orders_by_signal(signal_id)
                        positions = self.mt5_engine.get_positions_by_signal(signal_id)
                        
                        # CRITICAL: Always cancel pending orders when TP2 is reached, even if no positions
                        # This ensures LIMIT orders (Positions 2 & 3) are canceled when TP2 is hit
                        if pending_orders:
                            self.logger.warning(f"TP2 reached - Canceling {len(pending_orders)} pending LIMIT order(s) for signal {signal_id}")
                            # Cancel pending orders first
                            cancelled_count = 0
                            for order in pending_orders:
                                if self.mt5_engine.cancel_pending_order(order['ticket']):
                                    cancelled_count += 1
                                    self.logger.info(f"✅ Cancelled pending order #{order['ticket']} at {order.get('price_open', 'N/A')}")
                                else:
                                    self.logger.error(f"❌ Failed to cancel pending order #{order['ticket']}")
                            
                            if cancelled_count > 0:
                                self.logger.warning(f"🛡️ Cancelled {cancelled_count} pending order(s) - TP2 reached")
                        
                        # Activate protection if there are pending orders OR open positions
                        # This prevents false triggers when signal is already completed
                        if pending_orders or positions:
                            self.activate_protection(signal_id, move_to_breakeven=self.tp2_move_to_breakeven)
                
            except Exception as e:
                self.logger.error(f"Error in TP2 monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(check_interval)
    
    def can_place_order(self, signal_id: str) -> bool:
        """
        Check if new orders can be placed for signal
        
        Args:
            signal_id: Signal ID
            
        Returns:
            True if orders can be placed, False if blocked by TP2 protection
        """
        if self.is_protected(signal_id):
            self.logger.warning(f"Order blocked: TP2 protection active for signal {signal_id}")
            return False
        return True
    
    def get_protected_signals(self) -> list:
        """
        Get list of protected signal IDs
        
        Returns:
            List of signal IDs with active TP2 protection
        """
        return list(self.protected_signals)
    
    def get_protection_info(self, signal_id: str) -> Dict[str, Any]:
        """
        Get protection information for a signal
        
        Args:
            signal_id: Signal ID
            
        Returns:
            Protection info dictionary
        """
        if signal_id not in self.protected_signals:
            return {'protected': False}
        
        return {
            'protected': True,
            'activated_at': self.protection_timestamps.get(signal_id, 'unknown')
        }
    
    def force_activate_protection(self, signal_id: str, reason: str = "Manual"):
        """
        Manually activate protection (for emergency stop, etc.)
        
        Args:
            signal_id: Signal ID
            reason: Reason for activation
        """
        self.logger.warning(f"Force activating TP2 protection for {signal_id}: {reason}")
        self.activate_protection(signal_id)
    
    def clear_all_protection(self):
        """
        Clear all TP2 protection (use with caution)
        """
        self.logger.warning("Clearing ALL TP2 protection")
        self.protected_signals.clear()
        self.protection_timestamps.clear()


def main():
    """
    Test TP2 protection
    """
    import asyncio
    from src.utils import load_config, setup_logging
    from src.mt5_engine import MT5Engine
    from src.position_tracker import PositionTracker
    
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
        
        # Create TP2 protection
        tp2_protection = TP2Protection(config, engine, tracker)
        
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
        
        # Test protection
        logger.info(f"Can place order: {tp2_protection.can_place_order(signal_id)}")
        
        # Activate protection
        tp2_protection.activate_protection(signal_id)
        
        logger.info(f"Can place order after protection: {tp2_protection.can_place_order(signal_id)}")
        logger.info(f"Protected signals: {tp2_protection.get_protected_signals()}")
        
        # Monitor for a short time
        logger.info("Monitoring TP2 for 30 seconds...")
        
        try:
            await asyncio.wait_for(tp2_protection.monitor_tp2(check_interval=5), timeout=30)
        except asyncio.TimeoutError:
            logger.info("Monitoring test completed")
        
        engine.disconnect()
    
    asyncio.run(test())


if __name__ == '__main__':
    main()

