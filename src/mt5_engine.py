"""
MT5 Trading Engine
Handles MetaTrader 5 connection and trade execution
"""
import MetaTrader5 as mt5
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
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
        # Login can be numeric (account ID) or string (username) depending on broker
        login_value = self.mt5_config.get('login', '0')
        try:
            # Try to convert to int if it's numeric
            self.login = int(login_value)
        except (ValueError, TypeError):
            # If it's a string username, keep it as string
            # Note: Some brokers use string usernames, but MT5 API typically requires int
            # This will be handled in connect() method
            self.login = login_value
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
            # Check if MT5 process is running (Windows only)
            mt5_running = self._check_mt5_running()
            if not mt5_running:
                self.logger.error("="*60)
                self.logger.error("MT5 TERMINAL IS NOT RUNNING!")
                self.logger.error("")
                self.logger.error("Please:")
                self.logger.error("1. Open MetaTrader 5 terminal")
                self.logger.error("2. Log in to your account")
                self.logger.error("3. Keep the MT5 window open")
                self.logger.error("4. Then run the bot again")
                self.logger.error("="*60)
                return False
            
            # Initialize MT5 with retry mechanism
            # Sometimes MT5 needs a moment to be ready, so we retry a few times
            import time
            max_retries = 3
            retry_delay = 2  # seconds
            
            initialized = False
            for attempt in range(1, max_retries + 1):
                if attempt > 1:
                    self.logger.info(f"Retry attempt {attempt}/{max_retries} after {retry_delay} seconds...")
                    time.sleep(retry_delay)
                
                # Try without path first (auto-detect) - this is more reliable
                self.logger.info(f"Attempting to initialize MT5 (auto-detect, attempt {attempt}/{max_retries})...")
                if mt5.initialize():
                    initialized = True
                    break
                
                # If auto-detect fails, try with explicit path
                if self.path and os.path.exists(self.path):
                    self.logger.info(f"Auto-detect failed, trying explicit path: {self.path}")
                    if mt5.initialize(path=self.path):
                        initialized = True
                        break
            
            if not initialized:
                error = mt5.last_error()
                self.logger.error(f"MT5 initialize failed after {max_retries} attempts: {error}")
                self._handle_initialization_error(error)
                return False
            
            self.logger.info("MT5 initialized successfully")
            
            # Login
            if self.login and self.password and self.server:
                # Convert login to int if it's a string (for brokers that use usernames)
                # MT5 API requires integer login, but we'll try the string first
                login_param = self.login
                if isinstance(login_param, str):
                    try:
                        login_param = int(login_param)
                    except ValueError:
                        # If it's a non-numeric string, log warning and try anyway
                        self.logger.warning(f"Login '{login_param}' is not numeric. Some brokers require numeric account IDs.")
                        # Try to use as-is (MT5 might handle it, or will give a clear error)
                        pass
                
                if not mt5.login(login_param, self.password, self.server):
                    error_msg = mt5.last_error()
                    self.logger.error(f"MT5 login failed: {error_msg}")
                    if isinstance(self.login, str) and not self.login.isdigit():
                        self.logger.error(f"Note: Login '{self.login}' is not numeric. MT5 typically requires a numeric account ID.")
                        self.logger.error("Please check your MT5_LOGIN in config.env - it should be your account number (integer), not username.")
                    mt5.shutdown()
                    return False
                
                self.logger.info(f"Logged in to MT5 account: {login_param}")
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
    
    def _check_mt5_running(self) -> bool:
        """
        Check if MT5 terminal process is running (Windows only)
        
        Returns:
            True if MT5 process is found, False otherwise
        """
        try:
            import subprocess
            import platform
            
            # Only check on Windows
            if platform.system() != 'Windows':
                # On non-Windows, assume it might be running (can't check easily)
                return True
            
            # Use tasklist on Windows to check for MT5 processes
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq terminal64.exe'], 
                                      capture_output=True, text=True, timeout=5)
                if 'terminal64.exe' in result.stdout:
                    self.logger.info("Found MT5 terminal64.exe process")
                    return True
            except Exception:
                pass
            
            # Also check for terminal.exe (32-bit or alternative name)
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq terminal.exe'], 
                                      capture_output=True, text=True, timeout=5)
                if 'terminal.exe' in result.stdout:
                    self.logger.info("Found MT5 terminal.exe process")
                    return True
            except Exception:
                pass
            
            # Check for any process with "metatrader" in the name
            try:
                result = subprocess.run(['tasklist'], 
                                      capture_output=True, text=True, timeout=5)
                if 'metatrader' in result.stdout.lower() or 'mt5' in result.stdout.lower():
                    self.logger.info("Found MT5-related process")
                    return True
            except Exception:
                pass
            
            return False
        except Exception as e:
            self.logger.warning(f"Could not check if MT5 is running: {e}")
            # If we can't check, assume it might be running (don't block connection attempt)
            return True
    
    def _handle_initialization_error(self, error: Tuple[int, str]):
        """
        Provide helpful guidance for common MT5 initialization errors
        
        Args:
            error: Tuple of (error_code, error_message) from mt5.last_error()
        """
        error_code, error_msg = error
        
        if error_code == -10005:  # IPC timeout
            self.logger.error("="*60)
            self.logger.error("IPC TIMEOUT ERROR - Common causes:")
            self.logger.error("")
            self.logger.error("1. MT5 terminal is NOT running or not fully loaded")
            self.logger.error("   -> Solution: Open MetaTrader 5 terminal, wait for it to fully load")
            self.logger.error("   -> Make sure you can see the MT5 window (not just in system tray)")
            self.logger.error("   -> Then run the bot again")
            self.logger.error("")
            self.logger.error("2. MT5 terminal needs to be restarted")
            self.logger.error("   -> Solution: Close MT5 completely (File → Exit)")
            self.logger.error("   -> Wait 5 seconds")
            self.logger.error("   -> Open MT5 again and log in")
            self.logger.error("   -> Then run the bot")
            self.logger.error("")
            self.logger.error("3. MT5 is running but API connection is blocked")
            self.logger.error("   -> Solution: Try running MT5 as Administrator")
            self.logger.error("   -> Or: Check Windows Firewall/Antivirus settings")
            self.logger.error("   -> Or: Try removing MT5_PATH from config.env (let it auto-detect)")
            self.logger.error("")
            if self.path:
                self.logger.error(f"4. Current MT5 path: {self.path}")
                self.logger.error(f"   -> Path exists: {os.path.exists(self.path)}")
                self.logger.error("   -> Try removing MT5_PATH from config.env to use auto-detect")
            self.logger.error("="*60)
        elif error_code == -10001:  # Common initialization error
            self.logger.error("MT5 initialization failed - check if MT5 is installed and path is correct")
        else:
            self.logger.error(f"MT5 error code: {error_code}, message: {error_msg}")
    
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

    def get_atr(self, symbol: str, timeframe=mt5.TIMEFRAME_M5, period: int = 14) -> Optional[float]:
        """
        Compute ATR for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: MT5 timeframe (default M5)
            period: ATR period
            
        Returns:
            ATR value or None on failure
        """
        try:
            symbol = self.map_symbol(symbol)
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 1)
            if rates is None or len(rates) < period + 1:
                self.logger.debug(f"ATR: insufficient data for {symbol} (need {period + 1}, got {0 if rates is None else len(rates)})")
                return None
            
            true_ranges = []
            prev_close = None
            for r in rates:
                high = r['high']
                low = r['low']
                close = r['close']
                if prev_close is None:
                    tr = high - low
                else:
                    tr = max(
                        high - low,
                        abs(high - prev_close),
                        abs(low - prev_close)
                    )
                true_ranges.append(tr)
                prev_close = close
            
            # Drop the first bar (has no prev_close reference)
            if len(true_ranges) > 1:
                true_ranges = true_ranges[1:]
            
            if not true_ranges:
                return None
            
            atr = sum(true_ranges[-period:]) / min(period, len(true_ranges))
            return atr
        except Exception as e:
            self.logger.error(f"Error calculating ATR for {symbol}: {e}")
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
            
            # Get entry range for checking if price is within range
            entry_upper = signal.get('entry_upper')
            entry_lower = signal.get('entry_lower')
            
            # Get symbol info for order filling type
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"Cannot get symbol info for {symbol}")
                return None
            
            # Store original entry price for tracking (before any modifications)
            original_entry_price = entry_price
            
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
                    order_type = mt5.ORDER_TYPE_BUY
                    action = "BUY MARKET"
                    order_execution_price = current_price
                    self.logger.info(f"Position 1: Price {current_price} is within entry range [{entry_lower}-{entry_upper}] - using MARKET order at current price")
                else:
                    # Position 1 (if outside range) or Positions 2&3: Always use LIMIT at intended entry
                    order_type = mt5.ORDER_TYPE_BUY_LIMIT
                    action = "BUY LIMIT"
                    order_execution_price = entry_price
                    if price_within_range and position_num == 1:
                        # This shouldn't happen, but log it
                        self.logger.warning(f"Position 1: Price within range but using LIMIT - unexpected")
                    else:
                        self.logger.info(f"Position {position_num}: Placing BUY LIMIT at {entry_price} (current: {current_price})")
            else:  # SELL
                # Get BID price for SELL orders
                current_bid = self.get_current_price(symbol, 'bid')
                if current_bid is None:
                    current_bid = current_price  # Fallback to ask if bid unavailable
                
                # Get entry_middle for Position 2 logic
                entry_middle = signal.get('entry_middle')
                
                # Check if current price is within entry range (for SELL, entry_upper is higher, entry_lower is lower)
                price_within_range = (entry_lower is not None and entry_upper is not None and 
                                     entry_lower <= current_bid <= entry_upper)
                
                # Check if price is at entry_upper (start of range) - all positions should open immediately
                at_entry_upper = (entry_upper is not None and abs(current_bid - entry_upper) < 1.0)  # Allow small tolerance
                
                if at_entry_upper:
                    # At entry_upper (start of range): All 3 positions use MARKET at current price
                    order_type = mt5.ORDER_TYPE_SELL
                    action = "SELL MARKET"
                    order_execution_price = current_bid
                    self.logger.info(f"Position {position_num}: Price {current_bid} is at entry_upper {entry_upper} (start of range) - using MARKET order for all positions")
                elif position_num == 1 and price_within_range:
                    # Position 1: If price is within range, use MARKET at current price
                    order_type = mt5.ORDER_TYPE_SELL
                    action = "SELL MARKET"
                    order_execution_price = current_bid
                    self.logger.info(f"Position 1: Price {current_bid} is within entry range [{entry_lower}-{entry_upper}] - using MARKET order at current price")
                elif position_num == 2 and entry_middle is not None and current_bid < entry_middle:
                    # Position 2: If price is BELOW entry_middle, use MARKET at current price (immediate entry)
                    # If price is ABOVE entry_middle, use LIMIT at entry_middle (wait for price to come down)
                    order_type = mt5.ORDER_TYPE_SELL
                    action = "SELL MARKET"
                    order_execution_price = current_bid
                    self.logger.info(f"Position 2: Price {current_bid} is below entry_middle {entry_middle} - using MARKET order at current price")
                else:
                    # Position 1 (if outside range), Position 2 (if above middle), or Position 3: Use LIMIT at intended entry
                    order_type = mt5.ORDER_TYPE_SELL_LIMIT
                    action = "SELL LIMIT"
                    order_execution_price = entry_price
                    if position_num == 2 and entry_middle is not None and current_bid >= entry_middle:
                        self.logger.info(f"Position 2: Price {current_bid} is above entry_middle {entry_middle} - placing LIMIT at {entry_price}")
                    else:
                        self.logger.info(f"Position {position_num}: Placing SELL LIMIT at {entry_price} (current: {current_bid})")
            
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
            
            # Use order_execution_price for the order (current_price for MARKET, entry_price for LIMIT)
            # But preserve original_entry_price for logging and tracking
            request = {
                "action": mt5.TRADE_ACTION_DEAL if 'MARKET' in action else mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": order_execution_price,  # Use execution price (current for MARKET, entry for LIMIT)
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
                self.logger.error(f"Order send failed: result is None for Position {position_num} ({action} {symbol} @ {order_execution_price})")
                return None
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = result.comment if hasattr(result, 'comment') else 'Unknown error'
                self.logger.error(f"❌ Order failed for Position {position_num}: {result.retcode} - {error_msg}")
                self.logger.error(f"   Details: {action} {symbol} {lot_size} lot @ {order_execution_price} (entry: {entry_price}, current: {current_price})")
                self.logger.error(f"   SL: {sl}, TP: {tp}")
                
                # Provide helpful guidance for common errors
                if result.retcode == 10015:  # Invalid price
                    self.logger.error(f"   💡 Error 10015 (Invalid price) - Possible causes:")
                    self.logger.error(f"      - Entry price {order_execution_price} is too far from current price {current_price}")
                    self.logger.error(f"      - Price violates broker's minimum/maximum levels")
                    self.logger.error(f"      - For LIMIT orders, price must be better than current (BUY LIMIT < current, SELL LIMIT > current)")
                    if order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT]:
                        if direction == 'BUY' and order_execution_price >= current_price:
                            self.logger.error(f"      - BUY LIMIT price {order_execution_price} must be BELOW current price {current_price}")
                        elif direction == 'SELL' and order_execution_price <= current_price:
                            self.logger.error(f"      - SELL LIMIT price {order_execution_price} must be ABOVE current price {current_price}")
                
                return None
            
            ticket = result.order if hasattr(result, 'order') else result.deal
            
            # Confirm SL/TP are attached
            # entry_price is preserved at intended level (90130, 90094, 90058) for proper tracking
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
            # Get ALL pending orders (not filtered by symbol)
            orders = mt5.orders_get()
            if orders is None:
                self.logger.debug(f"No pending orders found (orders_get returned None)")
                return []
            
            if len(orders) == 0:
                self.logger.debug(f"No pending orders found (empty list)")
                return []
            
            signal_orders = []
            self.logger.debug(f"Checking {len(orders)} pending order(s) for signal_id: {signal_id}")
            
            for order in orders:
                order_comment = order.comment if hasattr(order, 'comment') else ''
                # Check if signal_id is in comment (format: {signal_id}_pos{position_num})
                if signal_id in order_comment:
                    volume = None
                    if hasattr(order, 'volume'):
                        volume = order.volume
                    elif hasattr(order, 'volume_current'):
                        volume = order.volume_current
                    elif hasattr(order, 'volume_initial'):
                        volume = order.volume_initial
                    signal_orders.append({
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type,
                        'volume': volume,
                        'price_open': order.price_open,
                        'sl': order.sl,
                        'tp': order.tp,
                        'comment': order_comment
                    })
                    self.logger.debug(f"Found pending order #{order.ticket} for signal {signal_id}: {order_comment} at {order.price_open}")
                else:
                    self.logger.debug(f"Order #{order.ticket} comment '{order_comment}' doesn't match signal_id '{signal_id}'")
            
            if signal_orders:
                self.logger.warning(f"Found {len(signal_orders)} pending order(s) for signal {signal_id}")
            else:
                self.logger.debug(f"No pending orders found for signal {signal_id}")
            
            return signal_orders
            
        except Exception as e:
            self.logger.error(f"Error getting pending orders: {e}", exc_info=True)
            return []

    def was_tp_hit(self, signal_id: str, symbol: str, tp_price: float, direction: str,
                   position_num: int = None, lookback_minutes: int = 120) -> bool:
        """
        Check history to see if TP was hit for a signal.
        
        Args:
            signal_id: Signal ID to match in deal comments
            symbol: Trading symbol
            tp_price: TP price to check
            direction: BUY/SELL
            position_num: Optional position number to match comment
            lookback_minutes: How far back to scan history
        """
        try:
            if tp_price is None:
                return False
            
            symbol = self.map_symbol(symbol)
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False
            
            tolerance = symbol_info.point * 2
            end = datetime.now()
            start = end - timedelta(minutes=lookback_minutes)
            
            deals = mt5.history_deals_get(start, end)
            if not deals:
                return False
            
            pos_tag = f"_pos{position_num}" if position_num else ""
            
            for deal in deals:
                comment = getattr(deal, 'comment', '') or ''
                if signal_id not in comment:
                    continue
                if pos_tag and pos_tag not in comment:
                    continue
                
                entry_type = getattr(deal, 'entry', None)
                if entry_type not in [mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT]:
                    continue
                
                price = getattr(deal, 'price', None)
                if price is None:
                    continue
                
                if direction == 'BUY':
                    if price + tolerance >= tp_price:
                        return True
                else:
                    if price - tolerance <= tp_price:
                        return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking TP hit from history: {e}", exc_info=True)
            return False


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
