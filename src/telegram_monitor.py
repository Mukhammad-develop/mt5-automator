"""
Telegram Signal Monitor
Monitors specified Telegram channels for trading signals
"""
import asyncio
import os
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Message, MessageMediaPhoto
from src.utils import create_class_logger


class TelegramMonitor:
    """
    Monitor Telegram channels for trading signals
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Telegram monitor
        
        Args:
            config: Configuration dictionary
        """
        self.logger = create_class_logger('TelegramMonitor')
        self.config = config
        self.telegram_config = config.get('telegram', {})
        
        # Telegram credentials
        self.api_id = self.telegram_config.get('api_id')
        self.api_hash = self.telegram_config.get('api_hash')
        self.phone = self.telegram_config.get('phone')
        self.channels = self.telegram_config.get('channels', [])
        
        # Create client
        self.client = TelegramClient('mt5_automator_session', self.api_id, self.api_hash)
        
        # Callback for signal processing
        self.signal_callback: Optional[Callable] = None
        
        # Track processed messages
        self.processed_messages = set()
        
        self.logger.info("TelegramMonitor initialized")
    
    async def connect(self):
        """
        Connect to Telegram
        """
        try:
            await self.client.start(phone=self.phone)
            self.logger.info("Connected to Telegram successfully")
            
            # Log channels to monitor
            for channel in self.channels:
                self.logger.info(f"Monitoring channel: {channel}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Telegram: {e}")
            raise
    
    async def disconnect(self):
        """
        Disconnect from Telegram
        """
        try:
            await self.client.disconnect()
            self.logger.info("Disconnected from Telegram")
        except Exception as e:
            self.logger.error(f"Error disconnecting from Telegram: {e}")
    
    def set_signal_callback(self, callback: Callable):
        """
        Set callback function to process signals
        
        Args:
            callback: Async function that receives signal data
        """
        self.signal_callback = callback
        self.logger.info("Signal callback registered")
    
    async def _handle_new_message(self, event: events.NewMessage.Event):
        """
        Handle new message from monitored channels
        
        Args:
            event: Telegram event
        """
        try:
            message: Message = event.message
            
            # Skip if already processed
            if message.id in self.processed_messages:
                return
            
            # Get channel info
            chat = await event.get_chat()
            channel_username = getattr(chat, 'username', 'Unknown')
            
            self.logger.info(f"New message from {channel_username} (ID: {message.id})")
            
            # Mark as processed
            self.processed_messages.add(message.id)
            
            # Extract signal data
            signal_data = {
                'channel': channel_username,
                'message_id': message.id,
                'timestamp': message.date.isoformat(),
                'text': message.message or '',
                'has_photo': False,
                'photo_path': None
            }
            
            # Check for photo
            if message.media and isinstance(message.media, MessageMediaPhoto):
                signal_data['has_photo'] = True
                self.logger.info(f"Message contains photo")
                
                # Download photo
                photo_path = await self._download_photo(message)
                signal_data['photo_path'] = photo_path
            
            # Process signal if callback is set
            if self.signal_callback:
                try:
                    await self.signal_callback(signal_data)
                except Exception as e:
                    self.logger.error(f"Error in signal callback: {e}", exc_info=True)
            else:
                self.logger.warning("No signal callback set, message not processed")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _download_photo(self, message: Message) -> str:
        """
        Download photo from message
        
        Args:
            message: Telegram message
            
        Returns:
            Path to downloaded photo
        """
        try:
            # Create images directory
            images_dir = 'data/images'
            os.makedirs(images_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{images_dir}/signal_{message.id}_{timestamp}.jpg"
            
            # Download photo
            await self.client.download_media(message.media, filename)
            self.logger.info(f"Photo downloaded: {filename}")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Error downloading photo: {e}")
            return None
    
    async def start_monitoring(self):
        """
        Start monitoring channels for new messages
        """
        try:
            self.logger.info("Starting channel monitoring...")
            
            # Register event handler for new messages
            @self.client.on(events.NewMessage(chats=self.channels))
            async def handler(event):
                await self._handle_new_message(event)
            
            # Keep client running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
            raise
    
    async def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages from monitored channels (for testing/debugging)
        
        Args:
            limit: Number of messages to retrieve per channel
            
        Returns:
            List of message data
        """
        messages = []
        
        for channel in self.channels:
            try:
                async for message in self.client.iter_messages(channel, limit=limit):
                    msg_data = {
                        'channel': channel,
                        'message_id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.message or '',
                        'has_photo': bool(message.media and isinstance(message.media, MessageMediaPhoto))
                    }
                    messages.append(msg_data)
                    
            except Exception as e:
                self.logger.error(f"Error fetching messages from {channel}: {e}")
        
        return messages
    
    async def test_connection(self) -> bool:
        """
        Test Telegram connection
        
        Returns:
            True if connection successful
        """
        try:
            await self.connect()
            me = await self.client.get_me()
            self.logger.info(f"Connected as: {me.first_name} ({me.phone})")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


async def main():
    """
    Test Telegram monitor
    """
    from src.utils import load_config, setup_logging
    
    # Load config
    config = load_config()
    logger = setup_logging(config)
    
    # Create monitor
    monitor = TelegramMonitor(config)
    
    # Test connection
    success = await monitor.test_connection()
    
    if success:
        logger.info("Telegram connection test passed!")
        
        # Get recent messages
        messages = await monitor.get_recent_messages(limit=5)
        logger.info(f"Retrieved {len(messages)} recent messages")
        
        for msg in messages:
            logger.info(f"  - {msg['channel']}: {msg['text'][:50]}...")
    
    await monitor.disconnect()


if __name__ == '__main__':
    asyncio.run(main())

