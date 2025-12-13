"""
MT5 Trading Engine
Handles MetaTrader 5 connection and trade execution
"""
import MetaTrader5 as mt5
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.utils import create_class_logger


class MT5Engine:
    """
    MetaTrader 5 trading engine
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MT5 engine
        
        Args:
            config: Configuration dictionary
        """
        self.logger = create_class_logger('MT5Engine')
        self.config = config
        self.mt5_config = config.get('mt5', {})
        self.trading_config = config.get('trading', {})
        
        # MT5 credentials
        self.login = int(self.mt5_config.get('login', 0))
        self.password = self.mt5_config.get('password', '')
        self.server = self.mt5_config.get('server', '')
        self.path = self.mt5_config.get('path', '')
        
        # Trading settings
        self.default_symbol = self.trading_config.get('default_symbol', 'BTCUSD')
        self.symbol_mapping = self.trading_config.get('symbol_mapping', {})
        
        # Connection status
        self.connected = False
        
        self.logger.info("MT5Engine initialized")
        if self.symbol_mapping:
            self.logger.info(f"Symbol mapping enabled: {self.symbol_mapping}")
    
    def connect(self) -> bool:
        """
        Connect to MT5 terminal
        
        Returns:
            True if connected successfully
        """
        try:
            # Initialize MT5
            if self.path:
                if not mt5.initialize(path=self.path):
                    self.logger.error(f"MT5 initialize failed: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize():
                    self.logger.error(f"MT5 initialize failed: {mt5.last_error()}")
                    return False
            
            self.logger.info("MT5 initialized")
            
            # Login
            if self.login and self.password and self.server:
                if not mt5.login(self.login, self.password, self.server):
                    self.logger.error(f"MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
                
                self.logger.info(f"Logged in to MT5 account: {self.login}")
            else:
                self.logger.warning("No login credentials provided, using current MT5 session")
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.error("Failed to get account info")
                return False
            
            self.logger.info(f"Account balance: {account_info.balance} {account_info.currency}")
            self.logger.info(f"Account leverage: 1:{account_info.leverage}")
            
            self.connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to MT5: {e}", exc_info=True)
            return False
    
    def disconnect(self):
        """
        Disconnect from MT5
        """
        try:
            mt5.shutdown()
            self.connected = False
            self.logger.info("Disconnected from MT5")
        except Exception as e:
            self.logger.error(f"Error disconnecting from MT5: {e}")
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get account information
        
        Returns:
            Account info dictionary or None
        """
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
            
            return {
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'currency': account_info.currency,
                'leverage': account_info.leverage,
                'profit': account_info.profit
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get symbol information
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Symbol info dictionary or None
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"Symbol not found: {symbol}")
                return None
            
            # Enable symbol if not visible
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    self.logger.error(f"Failed to enable symbol: {symbol}")
                    return None
            
            return {
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'trade_contract_size': symbol_info.trade_contract_size,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step
            }
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def map_symbol(self, symbol: str) -> str:
        """
        Map signal symbol to broker-specific symbol
        Uses manual mapping from config if available, otherwise returns as-is
        
        Args:
            symbol: Signal symbol (e.g., XAUUSD)
            
        Returns:
            Broker symbol (e.g., XAUUSD+ or mapped symbol)
        """
        # Check manual mapping first (for user overrides)
        if symbol in self.symbol_mapping:
            mapped = self.symbol_mapping[symbol]
            self.logger.debug(f"Manual symbol mapping: {symbol} → {mapped}")
            return mapped
        return symbol
    
    def get_current_price(self, symbol: str, price_type: str = 'ask') -> Optional[float]:
        """
        Get current price for symbol
        
        Args:
            symbol: Trading symbol
            price_type: 'ask' or 'bid'
            
        Returns:
            Current price or None
        """
        try:
            # Map symbol to broker-specific name
            symbol = self.map_symbol(symbol)
            
            symbol_info = mt5.symbol_info_tick(symbol)
            if symbol_info is None:
                return None
            
            if price_type == 'ask':
                return symbol_info.ask
            elif price_type == 'bid':
                return symbol_info.bid
            else:
                return (symbol_info.ask + symbol_info.bid) / 2
                
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def place_order(self, signal: Dict[str, Any], position_num: int, lot_size: float, 
                    signal_id: str) -> Optional[int]:
        """
        Place order based on signal
        
        Args:
            signal: Signal dictionary
            position_num: Position number (1, 2, or 3)
            lot_size: Lot size
            signal_id: Unique signal ID for tracking
            
        Returns:
            Order ticket number or None if failed
        """
        try:
            symbol = signal['symbol']
            # Map to broker-specific symbol name
            symbol = self.map_symbol(symbol)
            direction = signal['direction']
            
            # Get trading config
            trading_config = self.config.get('trading', {})
            position_1_tp_setting = trading_config.get('position_1_tp', 'TP1').upper()
            staged_entry_enabled = trading_config.get('staged_entry_enabled', True)
            position_3_runner_enabled = trading_config.get('position_3_runner_enabled', True)
            
            # Determine entry price and SL/TP based on position number
            # IMPORTANT: For SELL orders, positions are REVERSED (closest entry closes first)
            # For BUY orders, positions are NORMAL (closest entry closes first)
            if direction == 'SELL':
                # SELL: Position 1 = entry_lower (closest, closes at TP1), Position 3 = entry_upper (farthest, runner)
                if position_num == 1:
                    entry_price = signal['entry_lower']  # Closest entry for SELL
                    sl = signal.get('sl1')
                    # Configurable TP for Position 1
                    if position_1_tp_setting == 'TP2':
                        tp = signal.get('tp2')
                        self.logger.info(f"Position 1 targeting TP2 (configured: POSITION_1_TP=TP2)")
                    else:
                        tp = signal.get('tp1')
                elif position_num == 2:
                    entry_price = signal['entry_middle']
                    # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                    sl = signal.get('sl1')
                    tp = signal.get('tp2')
                elif position_num == 3:
                    entry_price = signal['entry_upper']  # Farthest entry for SELL (runner)
                    # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                    sl = signal.get('sl1')
                    
                    # Position 3 "Runner" Strategy
                    if position_3_runner_enabled:
                        # Position 3 is a "runner" - no TP, will use trailing stop after TP2 reached
                        tp = None
                        self.logger.info(f"🏃 Position 3 configured as RUNNER (no TP, trailing stop after TP2)")
                    else:
                        tp = signal.get('tp2')
                else:
                    self.logger.error(f"Invalid position number for SELL: {position_num} (must be 1, 2, or 3)")
                    return None
            else:  # BUY
                # BUY: Position 1 = entry_upper (closest, closes at TP1), Position 3 = entry_lower (farthest, runner)
                if position_num == 1:
                    entry_price = signal['entry_upper']  # Closest entry for BUY
                    sl = signal.get('sl1')
                    # Configurable TP for Position 1
                    if position_1_tp_setting == 'TP2':
                        tp = signal.get('tp2')
                        self.logger.info(f"Position 1 targeting TP2 (configured: POSITION_1_TP=TP2)")
                    else:
                        tp = signal.get('tp1')
                elif position_num == 2:
                    entry_price = signal['entry_middle']
                    # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                    sl = signal.get('sl1')
                    tp = signal.get('tp2')
                elif position_num == 3:
                    entry_price = signal['entry_lower']  # Farthest entry for BUY (runner)
                    # Use SL1 for all positions (client requirement: "set a fixed SL for all")
                    sl = signal.get('sl1')
                    
                    # Position 3 "Runner" Strategy
                    if position_3_runner_enabled:
                        # Position 3 is a "runner" - no TP, will use trailing stop after TP2 reached
                        tp = None
                        self.logger.info(f"🏃 Position 3 configured as RUNNER (no TP, trailing stop after TP2)")
                    else:
                        tp = signal.get('tp2')
                else:
                    self.logger.error(f"Invalid position number for BUY: {position_num} (must be 1, 2, or 3)")
                    return None
            
            # Get current price (simplified like dry-run: use ask for simplicity)
            # Note: Using ask works for both BUY and SELL for order type determination
            current_price = self.get_current_price(symbol, 'ask')
            if current_price is None:
                self.logger.error(f"Could not get current price for {symbol}")
                return None
            
            # STAGED ENTRY LOGIC: Prevents all 3 positions from filling at once
            # Only place LIMIT orders at prices that haven't been touched yet
            # If price has passed entry, allow MARKET order (client requirement)
            if staged_entry_enabled:
                if direction == 'BUY':
                    # For BUY: only place LIMIT if current price is BELOW entry
                    # If price already passed this entry, allow MARKET order (don't skip)
                    if current_price >= entry_price:
                        # Price passed entry - will place MARKET order below
                        self.logger.info(f"Staged Entry: Price passed entry {entry_price} (current: {current_price}) - will place MARKET order")
                else:  # SELL
                    # For SELL: only place LIMIT if current price is BELOW entry
                    # SELL LIMIT: sell at entry_price when price goes UP to it
                    # If current_price < entry_price: We CAN place SELL LIMIT (price will rise to entry)
                    # If current_price >= entry_price: Price already at or above entry, allow MARKET order (don't skip)
                    if current_price >= entry_price:
                        # Price passed entry - will place MARKET order below
                        self.logger.info(f"Staged Entry: Price passed entry {entry_price} (current: {current_price}) - will place MARKET order")
            
            # Get symbol info for stop level validation
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"Cannot get symbol info for {symbol}")
                return None
            
            # Get stop level (minimum distance from current price for limit orders)
            stop_level = symbol_info.trade_stops_level * symbol_info.point
            if stop_level == 0:
                stop_level = symbol_info.point * 10  # Default to 10 points if not specified
            
            # Determine order type with stop level validation
            if direction == 'BUY':
                # For BUY LIMIT: price must be BELOW current ASK by at least stop_level
                if current_price < entry_price:
                    # Check if entry_price meets minimum distance requirement
                    min_limit_price = current_price - stop_level
                    if entry_price >= min_limit_price:
                        # Entry price too close to current price - use MARKET instead
                        self.logger.warning(f"BUY LIMIT price {entry_price} too close to current {current_price} (min distance: {stop_level:.2f}) - using MARKET order")
                        order_type = mt5.ORDER_TYPE_BUY
                        action = "BUY MARKET"
                        entry_price = current_price
                    else:
                        order_type = mt5.ORDER_TYPE_BUY_LIMIT
                        action = "BUY LIMIT"
                else:
                    order_type = mt5.ORDER_TYPE_BUY
                    action = "BUY MARKET"
                    entry_price = current_price
            else:  # SELL
                # For SELL LIMIT: price must be ABOVE current BID by at least stop_level
                # Get BID price for SELL orders
                current_bid = self.get_current_price(symbol, 'bid')
                if current_bid is None:
                    current_bid = current_price  # Fallback to ask if bid unavailable
                
                if current_bid < entry_price:
                    # Check if entry_price meets minimum distance requirement
                    min_limit_price = current_bid + stop_level
                    if entry_price <= min_limit_price:
                        # Entry price too close to current price - use MARKET instead
                        self.logger.warning(f"SELL LIMIT price {entry_price} too close to current {current_bid} (min distance: {stop_level:.2f}) - using MARKET order")
                        order_type = mt5.ORDER_TYPE_SELL
                        action = "SELL MARKET"
                        entry_price = current_bid
                    else:
                        order_type = mt5.ORDER_TYPE_SELL_LIMIT
                        action = "SELL LIMIT"
                else:
                    order_type = mt5.ORDER_TYPE_SELL
                    action = "SELL MARKET"
                    entry_price = current_bid
            
            # Prepare request
            # Symbol info already retrieved above for stop level validation
            
            # Determine filling type (use RETURN for compatibility, fallback to FOK)
            filling_type = symbol_info.filling_mode
            if filling_type & 1:  # FOK available
                filling = mt5.ORDER_FILLING_FOK
            elif filling_type & 2:  # IOC available
                filling = mt5.ORDER_FILLING_IOC
            else:  # RETURN (most compatible)
                filling = mt5.ORDER_FILLING_RETURN
            
            # CRITICAL: SL and TP MUST be in the initial request
            # This ensures protection from the FIRST MOMENT order fills
            # Never set SL/TP after - that creates a dangerous gap!
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL if 'MARKET' in action else mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": entry_price,
                "deviation": 50,  # Increased for volatile instruments like gold
                "magic": 234000,
                "comment": f"{signal_id}_pos{position_num}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling,
            }
            
            # ALWAYS attach SL/TP to order (CRITICAL for safety!)
            if sl:
                request["sl"] = float(sl)
                self.logger.info(f"✅ SL attached to order: {sl} (will be active immediately when filled)")
            else:
                self.logger.warning(f"⚠️ No SL provided for position {position_num} - RISKY!")
            
            if tp:
                request["tp"] = float(tp)
                self.logger.info(f"✅ TP attached to order: {tp} (will be active immediately when filled)")
            else:
                self.logger.warning(f"⚠️ No TP provided for position {position_num}")
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                self.logger.error("Order send failed: result is None")
                return None
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Order failed: {result.retcode} - {result.comment}")
                return None
            
            ticket = result.order if hasattr(result, 'order') else result.deal
            
            # Confirm SL/TP are attached
            if sl and tp:
                self.logger.info(f"✅ {action} #{ticket}: {symbol} {lot_size} lot @ {entry_price} | SL={sl} TP={tp} ATTACHED")
            elif sl:
                self.logger.info(f"⚠️ {action} #{ticket}: {symbol} {lot_size} lot @ {entry_price} | SL={sl} (NO TP)")
            elif tp:
                self.logger.info(f"⚠️ {action} #{ticket}: {symbol} {lot_size} lot @ {entry_price} | TP={tp} (NO SL - DANGEROUS!)")
            else:
                self.logger.warning(f"❌ {action} #{ticket}: {symbol} {lot_size} lot @ {entry_price} | NO SL/TP - UNPROTECTED!")
            
            return ticket
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}", exc_info=True)
            return None
    
    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """
        Modify stop loss and/or take profit of position
        
        Args:
            ticket: Position ticket
            sl: New stop loss (None to keep current)
            tp: New take profit (None to keep current)
            
        Returns:
            True if successful
        """
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                self.logger.error(f"Position {ticket} not found")
                return False
            
            position = position[0]
            
            # Use current values if not specified
            if sl is None:
                sl = position.sl
            if tp is None:
                tp = position.tp
            
            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "sl": sl,
                "tp": tp,
            }
            
            # Send request
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Modify failed: {result.retcode} - {result.comment}")
                return False
            
            self.logger.info(f"Position #{ticket} modified: SL={sl}, TP={tp}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error modifying position: {e}")
            return False
    
    def close_position(self, ticket: int) -> bool:
        """
        Close position
        
        Args:
            ticket: Position ticket
            
        Returns:
            True if successful
        """
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                self.logger.error(f"Position {ticket} not found")
                return False
            
            position = position[0]
            
            # Prepare close request
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "price": mt5.symbol_info_tick(position.symbol).bid if close_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask,
                "deviation": 20,
                "magic": 234000,
                "comment": "Close position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Close failed: {result.retcode} - {result.comment}")
                return False
            
            self.logger.info(f"Position #{ticket} closed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            return False
    
    def cancel_pending_order(self, ticket: int) -> bool:
        """
        Cancel pending order
        
        Args:
            ticket: Order ticket
            
        Returns:
            True if successful
        """
        try:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Cancel failed: {result.retcode} - {result.comment}")
                return False
            
            self.logger.info(f"Pending order #{ticket} cancelled")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_positions_by_direction(self, symbol: str, direction: str) -> List[Dict[str, Any]]:
        """
        Get all open positions for a symbol in a specific direction
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            
        Returns:
            List of position dictionaries
        """
        try:
            # Map symbol to broker-specific name
            symbol = self.map_symbol(symbol)
            
            positions = mt5.positions_get(symbol=symbol)
            if positions is None:
                return []
            
            direction_positions = []
            for pos in positions:
                # Check position type
                pos_direction = 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL'
                if pos_direction == direction:
                    direction_positions.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': pos.type,
                        'volume': pos.volume,
                        'open_price': pos.price_open,
                        'current_price': pos.price_current,
                        'sl': pos.sl,
                        'tp': pos.tp,
                        'profit': pos.profit,
                        'comment': pos.comment
                    })
            
            return direction_positions
            
        except Exception as e:
            self.logger.error(f"Error getting positions by direction: {e}")
            return []
    
    def get_positions_by_signal(self, signal_id: str) -> List[Dict[str, Any]]:
        """
        Get all positions for a specific signal
        
        Args:
            signal_id: Signal ID
            
        Returns:
            List of position dictionaries
        """
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            signal_positions = []
            for pos in positions:
                if signal_id in pos.comment:
                    signal_positions.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                        'volume': pos.volume,
                        'open_price': pos.price_open,
                        'current_price': pos.price_current,
                        'sl': pos.sl,
                        'tp': pos.tp,
                        'profit': pos.profit,
                        'comment': pos.comment
                    })
            
            return signal_positions
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    def get_pending_orders_by_signal(self, signal_id: str) -> List[Dict[str, Any]]:
        """
        Get all pending orders for a specific signal
        
        Args:
            signal_id: Signal ID
            
        Returns:
            List of order dictionaries
        """
        try:
            orders = mt5.orders_get()
            if orders is None:
                return []
            
            signal_orders = []
            for order in orders:
                if signal_id in order.comment:
                    signal_orders.append({
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type,
                        'volume': order.volume,
                        'price_open': order.price_open,
                        'sl': order.sl,
                        'tp': order.tp,
                        'comment': order.comment
                    })
            
            return signal_orders
            
        except Exception as e:
            self.logger.error(f"Error getting pending orders: {e}")
            return []


def main():
    """
    Test MT5 engine
    """
    from src.utils import load_config, setup_logging
    
    # Load config
    config = load_config()
    logger = setup_logging(config)
    
    # Create engine
    engine = MT5Engine(config)
    
    # Test connection
    if engine.connect():
        logger.info("MT5 connection test passed!")
        
        # Get account info
        account_info = engine.get_account_info()
        if account_info:
            logger.info(f"Account: {account_info}")
        
        # Get symbol info
        symbol_info = engine.get_symbol_info('BTCUSD')
        if symbol_info:
            logger.info(f"BTCUSD: Bid={symbol_info['bid']}, Ask={symbol_info['ask']}")
        
        # Disconnect
        engine.disconnect()
    else:
        logger.error("MT5 connection test failed")


if __name__ == '__main__':
    main()

