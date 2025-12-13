"""
AI-Powered Signal Parser using DeepSeek API
Handles complex Telegram formats with emojis, markdown, and unusual layouts
Also processes images directly using vision capabilities
"""
import os
import json
import base64
import requests
from typing import Dict, Any, Optional
from src.utils import create_class_logger


class AISignalParser:
    """
    Parse trading signals using DeepSeek AI API
    Handles complex formats that regex can't parse
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AI signal parser
        
        Args:
            config: Configuration dictionary
        """
        self.logger = create_class_logger('AISignalParser')
        self.config = config
        self.ai_config = config.get('ai', {})
        
        # DeepSeek API settings
        self.api_key = os.getenv('DEEPSEEK_API_KEY', self.ai_config.get('api_key', ''))
        self.api_base = self.ai_config.get('api_base', 'https://api.deepseek.com/v1')
        self.model = self.ai_config.get('model', 'deepseek-chat')
        self.enabled = self.ai_config.get('enabled', False)
        
        if self.enabled and not self.api_key:
            self.logger.warning("AI parsing enabled but no API key found. Will fallback to regex.")
            self.enabled = False
        
        self.logger.info(f"AISignalParser initialized (enabled={self.enabled})")
    
    def parse_signal_from_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse trading signal directly from image using DeepSeek Vision
        
        Args:
            image_path: Path to image file
            
        Returns:
            Parsed signal dictionary or None
        """
        if not self.enabled:
            self.logger.debug("AI parsing disabled, skipping image")
            return None
        
        try:
            self.logger.info(f"Parsing signal from image with DeepSeek Vision: {image_path}")
            
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create vision prompt
            prompt = self._create_vision_prompt()
            
            # Call DeepSeek Vision API
            response = self._call_deepseek_vision_api(prompt, image_base64)
            
            if not response:
                return None
            
            # Parse AI response
            signal = self._parse_ai_response(response)
            
            if signal:
                signal['parsed_by'] = 'AI_Vision'
                self.logger.info(f"Vision AI parsed: {signal['direction']} {signal.get('symbol', 'N/A')} "
                               f"{signal['entry_upper']}-{signal['entry_lower']}")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in image AI parsing: {e}", exc_info=True)
            return None
    
    def parse_signal(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse trading signal using AI
        
        Args:
            text: Raw signal text (can include emojis, markdown, etc.)
            
        Returns:
            Parsed signal dictionary or None
        """
        if not self.enabled:
            self.logger.debug("AI parsing disabled, skipping")
            return None
        
        try:
            self.logger.info("Parsing signal with DeepSeek AI...")
            
            # Create prompt for AI
            prompt = self._create_prompt(text)
            
            # Call DeepSeek API
            response = self._call_deepseek_api(prompt)
            
            if not response:
                return None
            
            # Parse AI response
            signal = self._parse_ai_response(response)
            
            if signal:
                self.logger.info(f"AI parsed: {signal['direction']} {signal.get('symbol', 'N/A')} "
                               f"{signal['entry_upper']}-{signal['entry_lower']}")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in AI parsing: {e}", exc_info=True)
            return None
    
    def _create_prompt(self, text: str) -> str:
        """
        Create prompt for DeepSeek API
        
        Args:
            text: Raw signal text
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a trading signal parser. Extract trading information from the following message.

Message (may contain emojis, markdown, stickers text, or unusual formatting):
```
{text}
```

Extract and return ONLY a JSON object with these fields (no other text):
{{
  "direction": "BUY" or "SELL",
  "symbol": "trading symbol (e.g. BTCUSD, bitcoin, XAUUSD, EURUSD)" or null if not found,
  "entry_upper": upper entry price as float,
  "entry_lower": lower entry price as float,
  "sl1": stop loss 1 as float or null,
  "sl2": stop loss 2 as float or null,
  "sl3": stop loss 3 as float or null,
  "tp1": take profit 1 as float or null,
  "tp2": take profit 2 as float or null,
  "tp3": take profit 3 as float or null
}}

Rules:
- Ignore emojis, formatting, decorations
- "Long" or "Buy" = BUY, "Short" or "Sell" = SELL
- Entry can be called: Entry, Zone, Price, @price1 price2, etc.
- Examples: "@4218 4220" means entry range 4218-4220 (lower-upper for SELL, upper-lower for BUY)
- TP can be called: TP, Target, Take Profit, etc.
- SL can be called: SL, Stop, Stop Loss, etc.
- If only one entry price given, use it for both upper and lower
- For SELL: entry_upper should be higher price, entry_lower should be lower price
- For BUY: entry_upper should be higher price, entry_lower should be lower price
- Return null for missing values
- Return ONLY valid JSON, no explanations

JSON:"""
        
        return prompt
    
    def _create_vision_prompt(self) -> str:
        """
        Create prompt for DeepSeek Vision API
        
        Returns:
            Vision prompt
        """
        prompt = """Analyze this trading signal image and extract the trading information.

The image may contain:
- Emojis, decorations, stickers
- Text in any format or layout
- Tables, charts, or fancy designs
- Any language or symbols

Extract and return ONLY a JSON object (no other text):
{
  "direction": "BUY" or "SELL",
  "symbol": "trading symbol" or null,
  "entry_upper": upper entry price as float,
  "entry_lower": lower entry price as float,
  "sl1": stop loss 1 as float or null,
  "sl2": stop loss 2 as float or null,
  "sl3": stop loss 3 as float or null,
  "tp1": take profit 1 as float or null,
  "tp2": take profit 2 as float or null,
  "tp3": take profit 3 as float or null
}

Rules:
- Look for BUY/SELL, Long/Short indicators
- Find entry prices (may be labeled: Entry, Zone, Price, Range, etc.)
- Find TP levels (Target, Take Profit, TP1, TP2, etc.)
- Find SL levels (Stop Loss, SL, Stop, etc.)
- Ignore decorative elements
- If only one entry, use for both upper/lower
- Return null for missing values
- Return ONLY valid JSON

JSON:"""
        
        return prompt
    
    def _call_deepseek_vision_api(self, prompt: str, image_base64: str) -> Optional[str]:
        """
        Call DeepSeek Vision API
        
        Args:
            prompt: Text prompt
            image_base64: Base64 encoded image
            
        Returns:
            API response text or None
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'deepseek-chat',  # Vision model
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': prompt
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{image_base64}'
                                }
                            }
                        ]
                    }
                ],
                'temperature': 0.1,
                'max_tokens': 500
            }
            
            self.logger.debug(f"Calling DeepSeek Vision API")
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60  # Longer timeout for vision
            )
            
            if response.status_code != 200:
                self.logger.error(f"DeepSeek Vision API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            self.logger.debug(f"Vision AI response: {content[:200]}...")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error calling DeepSeek Vision API: {e}")
            return None
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """
        Call DeepSeek API
        
        Args:
            prompt: Prompt text
            
        Returns:
            API response text or None
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.1,  # Low temperature for consistent parsing
                'max_tokens': 500
            }
            
            self.logger.debug(f"Calling DeepSeek API: {self.api_base}/chat/completions")
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                self.logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            self.logger.debug(f"AI response: {content[:200]}...")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error calling DeepSeek API: {e}")
            return None
    
    def _parse_ai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response into signal dictionary
        
        Args:
            response: AI response text
            
        Returns:
            Signal dictionary or None
        """
        try:
            # Try to extract JSON from response (AI might add extra text)
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                self.logger.error("No JSON found in AI response")
                return None
            
            json_str = response[start:end]
            data = json.loads(json_str)
            
            # Validate required fields
            if not data.get('direction') or not data.get('entry_upper') or not data.get('entry_lower'):
                self.logger.error("Missing required fields in AI response")
                return None
            
            # Calculate middle entry
            entry_upper = float(data['entry_upper'])
            entry_lower = float(data['entry_lower'])
            
            # If entry range is the same (single entry price), create a spread for staged entry
            # This ensures 3 positions are placed at different levels (upper, middle, lower)
            if entry_upper == entry_lower:
                # Create a spread: for gold, use ~2 pips (0.2) spread
                # For other pairs, adjust based on typical pip size
                spread = 0.2  # Default 2 pips for gold
                entry_upper = entry_upper + spread / 2  # Upper entry
                entry_lower = entry_lower - spread / 2  # Lower entry
                self.logger.info(f"Single entry price detected - created spread: {entry_lower:.2f} - {entry_upper:.2f}")
            
            entry_middle = (entry_upper + entry_lower) / 2
            
            # Normalize symbol (map BTC/BITCOIN to BTCUSD, GOLD to XAUUSD, etc.)
            symbol = data.get('symbol')
            if symbol:
                symbol = symbol.upper()
                if symbol == 'BTC':
                    symbol = 'BTCUSD'
                elif symbol == 'BITCOIN' or symbol == 'BITCOIN USD' or symbol == 'BITCOIN/USD':
                    symbol = 'BTCUSD'
                elif symbol == 'GOLD':
                    symbol = 'XAUUSD'
                elif symbol == 'SILVER':
                    symbol = 'XAGUSD'
            else:
                symbol = 'BTCUSD'  # Default fallback
            
            # Build signal
            signal = {
                'direction': data['direction'].upper(),
                'symbol': symbol,
                'entry_upper': entry_upper,
                'entry_middle': entry_middle,
                'entry_lower': entry_lower,
                'sl1': float(data['sl1']) if data.get('sl1') else None,
                'sl2': float(data['sl2']) if data.get('sl2') else None,
                'sl3': float(data['sl3']) if data.get('sl3') else None,
                'tp1': float(data['tp1']) if data.get('tp1') else None,
                'tp2': float(data['tp2']) if data.get('tp2') else None,
                'tp3': float(data['tp3']) if data.get('tp3') else None,
                'raw_text': '',
                'parsed_by': 'AI'
            }
            
            return signal
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            self.logger.debug(f"Response was: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
            return None


def main():
    """Test AI parser"""
    from src.utils import load_config, setup_logging
    
    config = load_config()
    logger = setup_logging(config)
    
    parser = AISignalParser(config)
    
    # Test with complex format
    test_signal = """
    🔥 𝐆𝐎𝐋𝐃 𝐒𝐈𝐆𝐍𝐀𝐋 🔥
    
    ➡️ LONG XAUUSD
    📍 Zone: 2648.50 - 2650.20
    🎯 Targets:
       TP1: 2655.00
       TP2: 2660.50
    🛑 Stop: 2645.00
    """
    
    signal = parser.parse_signal(test_signal)
    
    if signal:
        logger.info("AI Parsing successful!")
        logger.info(json.dumps(signal, indent=2))
    else:
        logger.warning("AI parsing failed or disabled")


if __name__ == '__main__':
    main()


