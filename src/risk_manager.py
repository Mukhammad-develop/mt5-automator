"""
Risk Manager
Calculates lot sizes and validates trades based on risk parameters
"""
from typing import Dict, Any, List, Optional
from src.utils import create_class_logger, calculate_pip_value, calculate_pip_distance, validate_lot_size


class RiskManager:
    """
    Manage risk and calculate lot sizes
    """
    
    def __init__(self, config: Dict[str, Any], mt5_engine):
        """
        Initialize risk manager
        
        Args:
            config: Configuration dictionary
            mt5_engine: MT5Engine instance
        """
        self.logger = create_class_logger('RiskManager')
        self.config = config
        self.trading_config = config.get('trading', {})
        self.mt5_engine = mt5_engine
        
        # Risk settings
        self.risk_percent = self.trading_config.get('risk_percent', 1.0)
        self.num_positions = self.trading_config.get('num_positions', 3)
        
        self.logger.info(f"RiskManager initialized: {self.risk_percent}% risk, {self.num_positions} positions")
    
    def calculate_lot_sizes(self, signal: Dict[str, Any]) -> Optional[List[float]]:
        """
        Calculate lot sizes for all positions based on risk
        
        Args:
            signal: Signal dictionary
            
        Returns:
            List of lot sizes [lot1, lot2, lot3] or None if calculation fails
        """
        try:
            # Get account info
            account_info = self.mt5_engine.get_account_info()
            if not account_info:
                self.logger.error("Could not get account info")
                return None
            
            balance = account_info['balance']
            currency = account_info['currency']
            
            # Get symbol info
            symbol = signal['symbol']
            symbol_info = self.mt5_engine.get_symbol_info(symbol)
            if not symbol_info:
                self.logger.error(f"Could not get symbol info for {symbol}")
                return None
            
            # Calculate risk amount in account currency
            risk_amount = balance * (self.risk_percent / 100)
            risk_per_position = risk_amount / self.num_positions
            
            self.logger.info(f"Balance: {balance} {currency}, Risk: {self.risk_percent}% = {risk_amount} {currency}")
            self.logger.info(f"Risk per position: {risk_per_position} {currency}")
            
            # Calculate lot sizes for each position
            lot_sizes = []
            
            for pos_num in range(1, self.num_positions + 1):
                # Get entry and SL for this position
                if pos_num == 1:
                    entry = signal['entry_upper']
                    sl = signal.get('sl1')
                elif pos_num == 2:
                    entry = signal['entry_middle']
                    sl = signal.get('sl2')
                else:  # pos_num == 3
                    entry = signal['entry_lower']
                    sl = signal.get('sl3') or signal.get('sl2')
                
                if sl is None:
                    # Use first available SL
                    sl = signal.get('sl1') or signal.get('sl2') or signal.get('sl3')
                
                if sl is None:
                    self.logger.warning(f"No stop loss found for position {pos_num}, using default risk")
                    # Default to 50 pips risk
                    if signal['direction'] == 'BUY':
                        sl = entry - (50 * symbol_info['point'] * 10)
                    else:
                        sl = entry + (50 * symbol_info['point'] * 10)
                
                # Calculate pip risk
                pip_distance = calculate_pip_distance(entry, sl, symbol)
                
                self.logger.debug(f"Position {pos_num}: Entry={entry}, SL={sl}, Risk={pip_distance:.1f} pips")
                
                # Calculate lot size
                lot_size = self._calculate_lot_size(
                    symbol=symbol,
                    entry_price=entry,
                    sl_price=sl,
                    risk_amount=risk_per_position,
                    symbol_info=symbol_info
                )
                
                if lot_size is None:
                    self.logger.error(f"Could not calculate lot size for position {pos_num}")
                    return None
                
                lot_sizes.append(lot_size)
            
            self.logger.info(f"Calculated lot sizes: {lot_sizes}")
            return lot_sizes
            
        except Exception as e:
            self.logger.error(f"Error calculating lot sizes: {e}", exc_info=True)
            return None
    
    def _calculate_lot_size(self, symbol: str, entry_price: float, sl_price: float,
                           risk_amount: float, symbol_info: Dict[str, Any]) -> Optional[float]:
        """
        Calculate lot size for a single position
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            sl_price: Stop loss price
            risk_amount: Risk amount in account currency
            symbol_info: Symbol information dictionary
            
        Returns:
            Lot size or None if calculation fails
        """
        try:
            # Calculate pip distance
            pip_distance = calculate_pip_distance(entry_price, sl_price, symbol)
            
            if pip_distance == 0:
                self.logger.error("Pip distance is zero")
                return None
            
            # Get contract size
            contract_size = symbol_info['trade_contract_size']
            
            # Determine pip value per lot
            if 'XAU' in symbol or 'GOLD' in symbol:
                # Gold: 1 lot = 100 oz, pip = 0.01
                pip_value_per_lot = contract_size * 0.01
            elif 'JPY' in symbol:
                # JPY pairs: pip = 0.01
                pip_value_per_lot = contract_size * 0.01
            else:
                # Standard forex: pip = 0.0001
                pip_value_per_lot = contract_size * 0.0001
            
            # Calculate lot size
            # risk_amount = lot_size * pip_distance * pip_value_per_lot
            # lot_size = risk_amount / (pip_distance * pip_value_per_lot)
            lot_size = risk_amount / (pip_distance * pip_value_per_lot)
            
            # Validate and adjust lot size
            min_lot = symbol_info['volume_min']
            max_lot = symbol_info['volume_max']
            lot_step = symbol_info['volume_step']
            
            # Round to nearest step
            lot_size = round(lot_size / lot_step) * lot_step
            
            # Clamp to min/max
            lot_size = max(min_lot, min(lot_size, max_lot))
            
            # Round to 2 decimal places
            lot_size = round(lot_size, 2)
            
            self.logger.debug(f"Lot calculation: risk={risk_amount}, pips={pip_distance:.1f}, pip_value={pip_value_per_lot:.2f}, lot={lot_size}")
            
            return lot_size
            
        except Exception as e:
            self.logger.error(f"Error in lot size calculation: {e}")
            return None
    
    def validate_trade(self, signal: Dict[str, Any], lot_sizes: List[float]) -> bool:
        """
        Validate if trade meets risk requirements
        
        Args:
            signal: Signal dictionary
            lot_sizes: List of lot sizes
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Get account info
            account_info = self.mt5_engine.get_account_info()
            if not account_info:
                return False
            
            # Check free margin
            free_margin = account_info['free_margin']
            
            # Get symbol info
            symbol_info = self.mt5_engine.get_symbol_info(signal['symbol'])
            if not symbol_info:
                return False
            
            # Estimate required margin (simplified)
            total_volume = sum(lot_sizes)
            current_price = self.mt5_engine.get_current_price(signal['symbol'])
            leverage = account_info['leverage']
            
            # Rough margin calculation
            contract_size = symbol_info['trade_contract_size']
            estimated_margin = (total_volume * contract_size * current_price) / leverage
            
            if estimated_margin > free_margin:
                self.logger.warning(f"Insufficient margin: need {estimated_margin:.2f}, have {free_margin:.2f}")
                return False
            
            # Check lot sizes are valid
            for lot in lot_sizes:
                if lot < symbol_info['volume_min'] or lot > symbol_info['volume_max']:
                    self.logger.warning(f"Invalid lot size: {lot} (min={symbol_info['volume_min']}, max={symbol_info['volume_max']})")
                    return False
            
            self.logger.info("Trade validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating trade: {e}")
            return False
    
    def calculate_potential_profit_loss(self, signal: Dict[str, Any], lot_sizes: List[float]) -> Dict[str, float]:
        """
        Calculate potential profit and loss
        
        Args:
            signal: Signal dictionary
            lot_sizes: List of lot sizes
            
        Returns:
            Dictionary with profit/loss estimates
        """
        try:
            symbol = signal['symbol']
            symbol_info = self.mt5_engine.get_symbol_info(symbol)
            
            if not symbol_info:
                return {}
            
            results = {
                'max_loss': 0.0,
                'tp1_profit': 0.0,
                'tp2_profit': 0.0
            }
            
            for i, lot_size in enumerate(lot_sizes):
                pos_num = i + 1
                
                # Get levels
                if pos_num == 1:
                    entry = signal['entry_upper']
                    sl = signal.get('sl1')
                    tp = signal.get('tp1')
                elif pos_num == 2:
                    entry = signal['entry_middle']
                    sl = signal.get('sl2')
                    tp = signal.get('tp2')
                else:
                    entry = signal['entry_lower']
                    sl = signal.get('sl3') or signal.get('sl2')
                    tp = signal.get('tp2')
                
                if sl:
                    pip_loss = calculate_pip_distance(entry, sl, symbol)
                    pip_value = calculate_pip_value(symbol, lot_size)
                    results['max_loss'] += pip_loss * pip_value
                
                if tp:
                    pip_profit = calculate_pip_distance(entry, tp, symbol)
                    pip_value = calculate_pip_value(symbol, lot_size)
                    
                    if pos_num == 1:
                        results['tp1_profit'] += pip_profit * pip_value
                    else:
                        results['tp2_profit'] += pip_profit * pip_value
            
            self.logger.info(f"Potential: Loss=${results['max_loss']:.2f}, TP1=${results['tp1_profit']:.2f}, TP2=${results['tp2_profit']:.2f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating profit/loss: {e}")
            return {}
    
    def adjust_risk_for_multiple_signals(self, active_signals: int) -> float:
        """
        Adjust risk percentage when multiple signals are active
        
        Args:
            active_signals: Number of active signals
            
        Returns:
            Adjusted risk percentage
        """
        if active_signals <= 1:
            return self.risk_percent
        
        # Reduce risk proportionally
        adjusted_risk = self.risk_percent / active_signals
        
        self.logger.info(f"Adjusted risk from {self.risk_percent}% to {adjusted_risk}% ({active_signals} active signals)")
        
        return adjusted_risk


def main():
    """
    Test risk manager
    """
    from src.utils import load_config, setup_logging
    from src.mt5_engine import MT5Engine
    
    # Load config
    config = load_config()
    logger = setup_logging(config)
    
    # Create MT5 engine
    engine = MT5Engine(config)
    
    if not engine.connect():
        logger.error("Failed to connect to MT5")
        return
    
    # Create risk manager
    risk_mgr = RiskManager(config, engine)
    
    # Test signal
    test_signal = {
        'direction': 'BUY',
        'symbol': 'XAUUSD',
        'entry_upper': 2650.50,
        'entry_middle': 2649.35,
        'entry_lower': 2648.20,
        'sl1': 2645.00,
        'sl2': 2643.50,
        'sl3': 2642.00,
        'tp1': 2655.00,
        'tp2': 2660.00
    }
    
    # Calculate lot sizes
    lot_sizes = risk_mgr.calculate_lot_sizes(test_signal)
    
    if lot_sizes:
        logger.info(f"Lot sizes: {lot_sizes}")
        
        # Validate trade
        valid = risk_mgr.validate_trade(test_signal, lot_sizes)
        logger.info(f"Trade valid: {valid}")
        
        # Calculate potential profit/loss
        profit_loss = risk_mgr.calculate_potential_profit_loss(test_signal, lot_sizes)
        logger.info(f"Profit/Loss: {profit_loss}")
    
    engine.disconnect()


if __name__ == '__main__':
    main()

