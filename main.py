"""
MT5 Trading Automator - Main Controller
Orchestrates all components of the trading system
"""
import asyncio
import sys
import signal
from typing import Dict, Any
from src.utils import load_config, setup_logging, generate_signal_id, save_signal_to_db
from src.telegram_monitor import TelegramMonitor
from src.ocr_processor import OCRProcessor
from src.signal_parser import SignalParser
from src.ai_signal_parser import AISignalParser
from src.dry_run_mode import DryRunMT5Engine

# Import MT5 engine based on availability
try:
    from src.mt5_engine import MT5Engine
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️  MT5 package not available - will use dry-run mode")

from src.risk_manager import RiskManager
from src.position_tracker import PositionTracker
from src.tp_protection import TP2Protection


class MT5Automator:
    """
    Main trading automation controller
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize the automator
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        self.logger = setup_logging(self.config)
        self.logger.info("="*60)
        self.logger.info("MT5 Trading Automator Starting...")
        self.logger.info("="*60)
        
        # Initialize components
        self.telegram_monitor = TelegramMonitor(self.config)
        self.ocr_processor = OCRProcessor(self.config)
        self.signal_parser = SignalParser(self.config)
        self.ai_signal_parser = AISignalParser(self.config)
        
        # Determine mode
        mode_config = self.config.get('mode', {})
        self.dry_run = mode_config.get('dry_run', True)
        
        # Initialize MT5 engine based on mode and availability
        if self.dry_run:
            self.logger.warning("🧪 DRY RUN MODE - Commands will be logged, not executed")
            self.mt5_engine = DryRunMT5Engine(self.config)
        elif MT5_AVAILABLE:
            self.logger.info("Production mode - Real trading enabled")
            self.mt5_engine = MT5Engine(self.config)
        else:
            self.logger.error("Production mode requested but MT5 not available!")
            self.logger.warning("Falling back to dry-run mode")
            self.mt5_engine = DryRunMT5Engine(self.config)
            self.dry_run = True
        
        # Risk manager and trackers (initialized after MT5 connection)
        self.risk_manager = None
        self.position_tracker = None
        self.tp2_protection = None
        
        # System state
        self.running = False
        self.shutting_down = False
        
        self.logger.info("All components initialized")
    
    async def start(self):
        """
        Start the automation system
        """
        try:
            self.logger.info("Connecting to MT5...")
            if not self.mt5_engine.connect():
                self.logger.error("Failed to connect to MT5. Exiting.")
                return False
            
            self.logger.info("MT5 connected successfully")
            
            # Initialize risk manager and trackers
            self.risk_manager = RiskManager(self.config, self.mt5_engine)
            self.position_tracker = PositionTracker(self.config, self.mt5_engine)
            self.tp2_protection = TP2Protection(self.config, self.mt5_engine, self.position_tracker)
            
            self.logger.info("Connecting to Telegram...")
            await self.telegram_monitor.connect()
            self.logger.info("Telegram connected successfully")
            
            # Set signal callback
            self.telegram_monitor.set_signal_callback(self.process_signal)
            
            self.running = True
            self.logger.info("="*60)
            self.logger.info("MT5 Automator is RUNNING")
            self.logger.info("="*60)
            
            # Start monitoring tasks
            tasks = [
                asyncio.create_task(self.telegram_monitor.start_monitoring()),
                asyncio.create_task(self.position_tracker.monitor_positions()),
                asyncio.create_task(self.tp2_protection.monitor_tp2())
            ]
            
            # Wait for tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting automator: {e}", exc_info=True)
            return False
    
    async def stop(self):
        """
        Stop the automation system
        """
        if self.shutting_down:
            return
        
        self.shutting_down = True
        self.running = False
        
        self.logger.info("="*60)
        self.logger.info("Shutting down MT5 Automator...")
        self.logger.info("="*60)
        
        try:
            # Disconnect from Telegram
            if self.telegram_monitor:
                await self.telegram_monitor.disconnect()
            
            # Disconnect from MT5
            if self.mt5_engine:
                self.mt5_engine.disconnect()
            
            self.logger.info("Shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def process_signal(self, signal_data: Dict[str, Any]):
        """
        Process incoming signal from Telegram
        
        Args:
            signal_data: Signal data from Telegram
        """
        try:
            self.logger.info("="*60)
            self.logger.info(f"Processing new signal from {signal_data['channel']}")
            self.logger.info("="*60)
            
            # Extract text
            text = signal_data['text']
            signal = None  # Initialize signal variable
            
            # If photo, try AI vision first, fallback to OCR
            if signal_data['has_photo'] and signal_data['photo_path']:
                self.logger.info("Signal contains image, processing...")
                
                # Try AI vision first (can understand images directly)
                signal = self.ai_signal_parser.parse_signal_from_image(signal_data['photo_path'])
                
                if signal:
                    self.logger.info("AI Vision successfully parsed image directly!")
                    # Skip text parsing, we already have the signal
                else:
                    # Fallback to OCR if AI vision fails
                    self.logger.info("AI Vision failed, trying OCR...")
                    ocr_text = self.ocr_processor.process_image(signal_data['photo_path'])
                    
                    if ocr_text:
                        # Combine text from message and OCR
                        text = f"{text}\n{ocr_text}"
                        self.logger.info(f"OCR extracted {len(ocr_text)} characters")
                    else:
                        self.logger.warning("OCR also failed to extract text")
            
            # If we don't have signal from image, parse text
            if not signal:
                if not text or len(text.strip()) < 10:
                    self.logger.warning("Insufficient text to parse signal")
                    return
                
                # Parse signal - Try AI first, fallback to regex
                self.logger.info("Parsing signal from text...")
                
                # Try AI parser first (handles complex formats)
                signal = self.ai_signal_parser.parse_signal(text)
                
                # Fallback to regex parser if AI fails or disabled
                if not signal:
                    ai_config = self.config.get('ai', {})
                    if ai_config.get('fallback_to_regex', True):
                        self.logger.info("Trying regex parser as fallback...")
                        signal = self.signal_parser.parse_signal(text)
            
            if not signal:
                self.logger.warning("Failed to parse signal")
                return
            
            self.logger.info("Signal parsed successfully:")
            self.logger.info(self.signal_parser.format_signal(signal))
            
            # Generate unique signal ID
            signal_id = generate_signal_id(signal)
            signal['signal_id'] = signal_id
            
            # Check TP2 protection
            if self.tp2_protection.is_protected(signal_id):
                self.logger.warning(f"Signal {signal_id} is protected by TP2, skipping")
                return
            
            # Save signal to database
            save_signal_to_db(signal)
            
            # Calculate lot sizes
            self.logger.info("Calculating lot sizes...")
            lot_sizes = self.risk_manager.calculate_lot_sizes(signal)
            
            if not lot_sizes:
                self.logger.error("Failed to calculate lot sizes")
                return
            
            # Validate trade
            if not self.risk_manager.validate_trade(signal, lot_sizes):
                self.logger.error("Trade validation failed")
                return
            
            # Calculate potential profit/loss
            profit_loss = self.risk_manager.calculate_potential_profit_loss(signal, lot_sizes)
            
            # Register signal for tracking
            self.position_tracker.register_signal(signal_id, signal)
            
            # Place orders
            self.logger.info(f"Placing {len(lot_sizes)} orders...")
            
            num_positions = len(lot_sizes)
            successful_orders = 0
            
            for i, lot_size in enumerate(lot_sizes, 1):
                self.logger.info(f"Placing order {i}/{num_positions}: {lot_size} lot")
                
                ticket = self.mt5_engine.place_order(signal, i, lot_size, signal_id)
                
                if ticket:
                    self.position_tracker.add_position(signal_id, ticket, i)
                    successful_orders += 1
                    self.logger.info(f"Order {i} placed successfully: #{ticket}")
                else:
                    self.logger.error(f"Failed to place order {i}")
            
            if successful_orders > 0:
                self.logger.info(f"Successfully placed {successful_orders}/{num_positions} orders")
                self.logger.info("="*60)
                self.logger.info(f"TRADE EXECUTED: {signal['direction']} {signal['symbol']}")
                self.logger.info(f"Signal ID: {signal_id}")
                self.logger.info(f"Orders: {successful_orders}")
                self.logger.info(f"Total volume: {sum(lot_sizes[:successful_orders])} lots")
                self.logger.info("="*60)
            else:
                self.logger.error("Failed to place any orders")
            
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}", exc_info=True)


async def main():
    """
    Main entry point
    """
    automator = None
    
    def signal_handler(sig, frame):
        """Handle shutdown signals"""
        if automator:
            asyncio.create_task(automator.stop())
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start automator
        automator = MT5Automator()
        await automator.start()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if automator:
            await automator.stop()


if __name__ == '__main__':
    asyncio.run(main())

