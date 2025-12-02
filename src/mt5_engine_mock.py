"""
Mock MT5 Engine for Development/Testing on non-Windows systems
Use this when MetaTrader5 package is not available
"""
from typing import Dict, Any, Optional, List
from src.utils import create_class_logger


class MT5EngineMock:
    """
    Mock MT5 engine for development and testing
    Simulates MT5 operations without actual connection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize mock MT5 engine"""
        self.logger = create_class_logger('MT5EngineMock')
        self.config = config
        self.connected = False
        
        # Simulated account data
        self.mock_balance = 10000.0
        self.mock_equity = 10000.0
        self.mock_positions = []
        self.mock_orders = []
        
        self.logger.warning("⚠️  Using MOCK MT5 Engine (no real trading)")
        self.logger.info("MT5EngineMock initialized")
    
    def connect(self) -> bool:
        """Simulate MT5 connection"""
        self.logger.info("MOCK: Connecting to MT5...")
        self.connected = True
        self.logger.info("MOCK: Connected successfully (simulated)")
        return True
    
    def disconnect(self):
        """Simulate disconnection"""
        self.connected = False
        self.logger.info("MOCK: Disconnected from MT5")
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Return mock account info"""
        return {
            'balance': self.mock_balance,
            'equity': self.mock_equity,
            'margin': 1000.0,
            'free_margin': 9000.0,
            'currency': 'USD',
            'leverage': 100,
            'profit': 0.0
        }
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Return mock symbol info"""
        return {
            'bid': 2650.00,
            'ask': 2650.10,
            'point': 0.01,
            'digits': 2,
            'trade_contract_size': 100.0,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01
        }
    
    def get_current_price(self, symbol: str, price_type: str = 'ask') -> Optional[float]:
        """Return mock current price"""
        if price_type == 'ask':
            return 2650.10
        elif price_type == 'bid':
            return 2650.00
        else:
            return 2650.05
    
    def place_order(self, signal: Dict[str, Any], position_num: int, 
                    lot_size: float, signal_id: str) -> Optional[int]:
        """Simulate order placement"""
        ticket = len(self.mock_positions) + 1000
        
        self.logger.info(f"MOCK: Order placed #{ticket} - {signal['direction']} "
                        f"{signal['symbol']} {lot_size} lot (position {position_num})")
        
        # Add to mock positions
        self.mock_positions.append({
            'ticket': ticket,
            'signal_id': signal_id,
            'position_num': position_num,
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'volume': lot_size
        })
        
        return ticket
    
    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """Simulate position modification"""
        self.logger.info(f"MOCK: Modified position #{ticket} - SL={sl}, TP={tp}")
        return True
    
    def close_position(self, ticket: int) -> bool:
        """Simulate closing position"""
        self.logger.info(f"MOCK: Closed position #{ticket}")
        # Remove from mock positions
        self.mock_positions = [p for p in self.mock_positions if p['ticket'] != ticket]
        return True
    
    def cancel_pending_order(self, ticket: int) -> bool:
        """Simulate canceling order"""
        self.logger.info(f"MOCK: Cancelled order #{ticket}")
        return True
    
    def get_positions_by_signal(self, signal_id: str) -> List[Dict[str, Any]]:
        """Return mock positions for signal"""
        positions = []
        for pos in self.mock_positions:
            if pos.get('signal_id') == signal_id:
                positions.append({
                    'ticket': pos['ticket'],
                    'symbol': pos['symbol'],
                    'type': pos['direction'],
                    'volume': pos['volume'],
                    'open_price': 2650.0,
                    'current_price': 2651.0,
                    'sl': 2645.0,
                    'tp': 2655.0,
                    'profit': 10.0,
                    'comment': f"{signal_id}_pos{pos['position_num']}"
                })
        return positions
    
    def get_pending_orders_by_signal(self, signal_id: str) -> List[Dict[str, Any]]:
        """Return mock pending orders"""
        return []


def main():
    """Test mock engine"""
    from src.utils import load_config, setup_logging
    
    config = load_config()
    logger = setup_logging(config)
    
    engine = MT5EngineMock(config)
    
    if engine.connect():
        logger.info("Mock engine test passed!")
        
        account = engine.get_account_info()
        logger.info(f"Account: {account}")
        
        engine.disconnect()


if __name__ == '__main__':
    main()

