"""
Dry Run Mode - Shows what would be executed without actual trading
Perfect for testing on macOS without MT5
"""
from typing import Dict, Any, List
from datetime import datetime
from src.utils import create_class_logger


class DryRunMT5Engine:
    """
    Dry-run MT5 engine that logs what would be executed
    Use this for testing on macOS or when you want to see actions without trading
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize dry-run engine"""
        self.logger = create_class_logger('DryRunMT5')
        self.config = config
        self.connected = False
        
        # Trading settings
        self.trading_config = config.get('trading', {})
        self.symbol_mapping = self.trading_config.get('symbol_mapping', {})
        
        # Simulated state
        self.mock_balance = 10000.0
        self.mock_price = 2650.0
        self.order_counter = 1000
        self.mock_positions = []
        self.mock_orders = []
        
        self.logger.warning("="*70)
        self.logger.warning("🧪 DRY RUN MODE ENABLED - NO REAL TRADING")
        self.logger.warning("All MT5 commands will be SIMULATED and LOGGED")
        self.logger.warning("="*70)
    
    def map_symbol(self, symbol: str) -> str:
        """Map signal symbol to broker-specific symbol"""
        if symbol in self.symbol_mapping:
            mapped = self.symbol_mapping[symbol]
            self.logger.info(f"Symbol mapping: {symbol} → {mapped}")
            return mapped
        return symbol
    
    def connect(self) -> bool:
        """Simulate connection"""
        self.connected = True
        if self.symbol_mapping:
            self.logger.info(f"Symbol mapping enabled: {self.symbol_mapping}")
        self._log_action("CONNECT", "MT5 Terminal", {"status": "simulated"})
        return True
    
    def disconnect(self):
        """Simulate disconnection"""
        self.connected = False
        self._log_action("DISCONNECT", "MT5 Terminal", {})
    
    def get_account_info(self) -> Dict[str, Any]:
        """Return simulated account info"""
        info = {
            'balance': self.mock_balance,
            'equity': self.mock_balance,
            'margin': 1000.0,
            'free_margin': 9000.0,
            'currency': 'USD',
            'leverage': 100,
            'profit': 0.0
        }
        self._log_action("GET_ACCOUNT_INFO", "Account", info)
        return info
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Return simulated symbol info"""
        info = {
            'bid': self.mock_price - 0.05,
            'ask': self.mock_price + 0.05,
            'point': 0.01,
            'digits': 2,
            'trade_contract_size': 100.0,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01
        }
        self._log_action("GET_SYMBOL_INFO", symbol, info)
        return info
    
    def get_current_price(self, symbol: str, price_type: str = 'ask') -> float:
        """Return simulated price"""
        if price_type == 'ask':
            price = self.mock_price + 0.05
        elif price_type == 'bid':
            price = self.mock_price - 0.05
        else:
            price = self.mock_price
        
        self._log_action("GET_PRICE", symbol, {
            'type': price_type,
            'price': price
        })
        return price
    
    def place_order(self, signal: Dict[str, Any], position_num: int, 
                    lot_size: float, signal_id: str) -> int:
        """Simulate order placement - THIS IS THE KEY FUNCTION"""
        ticket = self.order_counter
        self.order_counter += 1
        
        # Map symbol to broker-specific name
        symbol = self.map_symbol(signal['symbol'])
        signal_with_mapped_symbol = signal.copy()
        signal_with_mapped_symbol['symbol'] = symbol
        
        # Get trading config
        position_1_tp_setting = self.trading_config.get('position_1_tp', 'TP1').upper()
        staged_entry_enabled = self.trading_config.get('staged_entry_enabled', True)
        position_3_runner_enabled = self.trading_config.get('position_3_runner_enabled', True)
        
        # Determine entry and SL/TP based on position number
        # IMPORTANT: For SELL orders, positions are REVERSED (closest entry closes first)
        # For BUY orders, positions are NORMAL (closest entry closes first)
        direction = signal['direction']
        if direction == 'SELL':
            # SELL: Position 1 = entry_lower (closest, closes at TP1), Position 3 = entry_upper (farthest, runner)
            if position_num == 1:
                entry = signal['entry_lower']  # Closest entry for SELL
                sl = signal.get('sl1')
                # Configurable TP for Position 1
                if position_1_tp_setting == 'TP2':
                    tp = signal.get('tp2')
                    self.logger.info(f"(DRY-RUN) Position 1 targeting TP2 (configured: POSITION_1_TP=TP2)")
                else:
                    tp = signal.get('tp1')
            elif position_num == 2:
                entry = signal['entry_middle']
                # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                sl = signal.get('sl1')
                tp = signal.get('tp2')
            elif position_num == 3:
                entry = signal['entry_upper']  # Farthest entry for SELL (runner)
                # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                sl = signal.get('sl1')
                
                # Position 3 "Runner" Strategy
                if position_3_runner_enabled:
                    # Position 3 is a "runner" - no TP, will use trailing stop after TP2 reached
                    tp = None
                    self.logger.info(f"(DRY-RUN) 🏃 Position 3 configured as RUNNER (no TP, trailing stop after TP2)")
                else:
                    tp = signal.get('tp2')
        else:  # BUY
            # BUY: Position 1 = entry_upper (closest, closes at TP1), Position 3 = entry_lower (farthest, runner)
            if position_num == 1:
                entry = signal['entry_upper']  # Closest entry for BUY
                sl = signal.get('sl1')
                # Configurable TP for Position 1
                if position_1_tp_setting == 'TP2':
                    tp = signal.get('tp2')
                    self.logger.info(f"(DRY-RUN) Position 1 targeting TP2 (configured: POSITION_1_TP=TP2)")
                else:
                    tp = signal.get('tp1')
            elif position_num == 2:
                entry = signal['entry_middle']
                # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                sl = signal.get('sl1')
                tp = signal.get('tp2')
            elif position_num == 3:
                entry = signal['entry_lower']  # Farthest entry for BUY (runner)
                # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                sl = signal.get('sl1')
                
                # Position 3 "Runner" Strategy
                if position_3_runner_enabled:
                    # Position 3 is a "runner" - no TP, will use trailing stop after TP2 reached
                    tp = None
                    self.logger.info(f"(DRY-RUN) 🏃 Position 3 configured as RUNNER (no TP, trailing stop after TP2)")
                else:
                    tp = signal.get('tp2')
        
        # Get current price
        current_price = self.get_current_price(symbol)
        
        # Get entry range for checking if price is within range
        entry_upper = signal.get('entry_upper')
        entry_lower = signal.get('entry_lower')
        
        # CLIENT REQUIREMENT: Smart entry logic based on current price position
        # If current price is WITHIN entry range (entry_lower ≤ current ≤ entry_upper):
        #   - Position 1: MARKET at current price (immediate entry)
        #   - Position 2: LIMIT at middle (wait for better entry)
        #   - Position 3: LIMIT at lower (wait for better entry)
        # If current price is OUTSIDE entry range:
        #   - All positions: LIMIT at their intended levels
        
        # Determine order type based on position and price location
        if direction == 'BUY':
            # Check if current price is within entry range
            price_within_range = (entry_lower is not None and entry_upper is not None and 
                                 entry_lower <= current_price <= entry_upper)
            
            if position_num == 1 and price_within_range:
                # Position 1: If price is within range, use MARKET at current price
                order_type = "BUY MARKET"
                execution_entry = current_price
                self.logger.info(f"(DRY-RUN) Position 1: Price {current_price} is within entry range [{entry_lower}-{entry_upper}] - using MARKET order")
            else:
                # Position 1 (if outside range) or Positions 2&3: Always use LIMIT at intended entry
                order_type = "BUY LIMIT"
                execution_entry = entry
                self.logger.info(f"(DRY-RUN) Position {position_num}: Placing BUY LIMIT at {entry} (current: {current_price})")
        else:  # SELL
            # For SELL, use bid price
            current_bid = self.get_current_price(symbol, 'bid')
            if current_bid is None:
                current_bid = current_price
            
            # Get entry_middle for Position 2 logic
            entry_middle = signal.get('entry_middle')
            
            # Check if current price is within entry range
            price_within_range = (entry_lower is not None and entry_upper is not None and 
                                 entry_lower <= current_bid <= entry_upper)
            
            # Check if price is at entry_upper (start of range) - all positions should open immediately
            at_entry_upper = (entry_upper is not None and abs(current_bid - entry_upper) < 1.0)  # Allow small tolerance
            
            if at_entry_upper:
                # At entry_upper (start of range): All 3 positions use MARKET at current price
                order_type = "SELL MARKET"
                execution_entry = current_bid
                self.logger.info(f"(DRY-RUN) Position {position_num}: Price {current_bid} is at entry_upper {entry_upper} (start of range) - using MARKET order")
            elif position_num == 1 and price_within_range:
                # Position 1: If price is within range, use MARKET at current price
                order_type = "SELL MARKET"
                execution_entry = current_bid
                self.logger.info(f"(DRY-RUN) Position 1: Price {current_bid} is within entry range [{entry_lower}-{entry_upper}] - using MARKET order")
            elif position_num == 2 and entry_middle is not None and current_bid < entry_middle:
                # Position 2: If price is BELOW entry_middle, use MARKET at current price (immediate entry)
                # If price is ABOVE entry_middle, use LIMIT at entry_middle (wait for price to come down)
                order_type = "SELL MARKET"
                execution_entry = current_bid
                self.logger.info(f"(DRY-RUN) Position 2: Price {current_bid} is below entry_middle {entry_middle} - using MARKET order")
            else:
                # Position 1 (if outside range), Position 2 (if above middle), or Position 3: Use LIMIT at intended entry
                order_type = "SELL LIMIT"
                execution_entry = entry
                if position_num == 2 and entry_middle is not None and current_bid >= entry_middle:
                    self.logger.info(f"(DRY-RUN) Position 2: Price {current_bid} is above entry_middle {entry_middle} - placing LIMIT at {entry}")
                else:
                    self.logger.info(f"(DRY-RUN) Position {position_num}: Placing SELL LIMIT at {entry} (current: {current_bid})")
        
        # Use execution_entry for logging (preserve original entry for tracking)
        entry_for_log = execution_entry
        
        # CRITICAL: SL/TP attached to order from the start (simulated)
        # In real MT5, these are in the initial request, not added later!
        if sl:
            self.logger.info(f"✅ (DRY-RUN) SL attached to order: {sl}")
        else:
            self.logger.warning(f"⚠️ (DRY-RUN) No SL - RISKY!")
        
        if tp:
            self.logger.info(f"✅ (DRY-RUN) TP attached to order: {tp}")
        else:
            self.logger.warning(f"⚠️ (DRY-RUN) No TP")
        
        # Log the order details
        order_details = {
            'ticket': ticket,
            'type': order_type,
            'symbol': symbol,
            'volume': lot_size,
            'entry_price': entry,
            'stop_loss': sl,
            'take_profit': tp,
            'position_num': position_num,
            'signal_id': signal_id,
            'comment': f"{signal_id}_pos{position_num}"
        }
        
        self._log_action("PLACE_ORDER", f"Position {position_num}", order_details)
        
        # Add to mock positions
        self.mock_positions.append({
            'ticket': ticket,
            'signal_id': signal_id,
            'type': order_type,
            **order_details
        })
        
        return ticket
    
    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """Simulate position modification"""
        self._log_action("MODIFY_POSITION", f"Ticket #{ticket}", {
            'new_sl': sl,
            'new_tp': tp
        })
        return True
    
    def close_position(self, ticket: int) -> bool:
        """Simulate closing position"""
        self._log_action("CLOSE_POSITION", f"Ticket #{ticket}", {})
        self.mock_positions = [p for p in self.mock_positions if p['ticket'] != ticket]
        return True
    
    def cancel_pending_order(self, ticket: int) -> bool:
        """Simulate canceling order"""
        self._log_action("CANCEL_ORDER", f"Ticket #{ticket}", {})
        return True
    
    def get_positions_by_signal(self, signal_id: str) -> List[Dict[str, Any]]:
        """Return simulated positions"""
        positions = [p for p in self.mock_positions if p.get('signal_id') == signal_id]
        self._log_action("GET_POSITIONS", f"Signal {signal_id}", {
            'count': len(positions),
            'tickets': [p['ticket'] for p in positions]
        })
        
        return [{
            'ticket': p['ticket'],
            'symbol': p['symbol'],
            'type': p['type'],
            'volume': p['volume'],
            'open_price': p['entry_price'],
            'current_price': self.mock_price,
            'sl': p['stop_loss'],
            'tp': p['take_profit'],
            'profit': 10.0,
            'comment': p['comment']
        } for p in positions]
    
    def get_pending_orders_by_signal(self, signal_id: str) -> List[Dict[str, Any]]:
        """Return simulated pending orders"""
        return []
    
    def _log_action(self, action: str, target: str, details: Dict[str, Any]):
        """
        Log what would be executed (simplified format)
        """
        # Only log important actions to console
        important_actions = ['PLACE_ORDER', 'MODIFY_POSITION', 'CLOSE_POSITION', 'CANCEL_ORDER']
        
        if action in important_actions:
            # Format key details
            if action == 'PLACE_ORDER':
                msg = f"🧪 DRY RUN: {details.get('type')} {details.get('symbol')} {details.get('volume')} lot @ {details.get('entry_price')} | SL: {details.get('stop_loss')} | TP: {details.get('take_profit')} | Ticket: #{details.get('ticket')}"
                self.logger.warning(msg)
            elif action == 'MODIFY_POSITION':
                msg = f"🧪 DRY RUN: Modified #{target.split('#')[1]} → SL: {details.get('new_sl')}"
                self.logger.info(msg)
            elif action == 'CLOSE_POSITION':
                msg = f"🧪 DRY RUN: Closed position #{target.split('#')[1]}"
                self.logger.warning(msg)
            elif action == 'CANCEL_ORDER':
                msg = f"🧪 DRY RUN: Cancelled order #{target.split('#')[1]}"
                self.logger.warning(msg)
        else:
            # Just log to file for other actions
            self.logger.debug(f"DRY RUN: {action} -> {target}")


def main():
    """Test dry-run engine"""
    from src.utils import load_config, setup_logging
    
    config = load_config()
    logger = setup_logging(config)
    
    engine = DryRunMT5Engine(config)
    
    # Test signal
    test_signal = {
        'direction': 'BUY',
        'symbol': 'BTCUSD',
        'entry_upper': 2650.50,
        'entry_middle': 2649.35,
        'entry_lower': 2648.20,
        'sl1': 2645.00,
        'sl2': 2643.50,
        'sl3': 2642.00,
        'tp1': 2655.00,
        'tp2': 2660.00
    }
    
    engine.connect()
    engine.get_account_info()
    
    # Place test orders
    for i in range(1, 4):
        ticket = engine.place_order(test_signal, i, 0.33, 'test_signal_001')
        logger.info(f"Placed order #{ticket}")
    
    engine.disconnect()


if __name__ == '__main__':
    main()


