import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class QueryParser:
    """Parses natural language queries to detect intent and extract parameters"""
    
    def __init__(self):
        # Define intent patterns and keywords
        self.intent_patterns = {
            'pump_and_dump': {
                'keywords': ['pump', 'dump', 'spike', 'manipulation', 'scam', 'suspicious'],
                'patterns': [
                    r'pump.{0,10}dump',
                    r'price.{0,10}spike',
                    r'suspicious.{0,10}activity',
                    r'manipulat',
                    r'scam.{0,10}coin'
                ],
                'description': 'Find potential pump and dump schemes'
            },
            'bottomed_out': {
                'keywords': ['bottom', 'bottomed', 'low', 'recovery', 'rebound', 'reversal'],
                'patterns': [
                    r'bottom.{0,10}out',
                    r'hit.{0,10}bottom',
                    r'recover.{0,10}from.{0,10}low',
                    r'trend.{0,10}reversal',
                    r'bouncing.{0,10}back'
                ],
                'description': 'Find cryptocurrencies that may have bottomed out'
            },
            'uptrend': {
                'keywords': ['up', 'rising', 'bullish', 'increasing', 'growing', 'gain'],
                'patterns': [
                    r'going.{0,10}up',
                    r'price.{0,10}rising',
                    r'bullish.{0,10}trend',
                    r'upward.{0,10}trend',
                    r'gaining.{0,10}momentum'
                ],
                'description': 'Find cryptocurrencies in uptrend'
            },
            'downtrend': {
                'keywords': ['down', 'falling', 'bearish', 'declining', 'losing', 'drop'],
                'patterns': [
                    r'going.{0,10}down',
                    r'price.{0,10}falling',
                    r'bearish.{0,10}trend',
                    r'downward.{0,10}trend',
                    r'losing.{0,10}value'
                ],
                'description': 'Find cryptocurrencies in downtrend'
            },
            'high_volatility': {
                'keywords': ['volatile', 'volatility', 'unstable', 'swinging', 'fluctuat'],
                'patterns': [
                    r'high.{0,10}volatility',
                    r'very.{0,10}volatile',
                    r'price.{0,10}swings',
                    r'unstable.{0,10}price'
                ],
                'description': 'Find highly volatile cryptocurrencies'
            },
            'volume_spike': {
                'keywords': ['volume', 'trading', 'activity', 'unusual'],
                'patterns': [
                    r'volume.{0,10}spike',
                    r'high.{0,10}volume',
                    r'unusual.{0,10}activity',
                    r'trading.{0,10}volume'
                ],
                'description': 'Find cryptocurrencies with unusual volume activity'
            },
            'trending': {
                'keywords': ['trend', 'trending', 'popular', 'hot', 'active'],
                'patterns': [
                    r'what.{0,10}trending',
                    r'most.{0,10}active',
                    r'popular.{0,10}coin',
                    r'hot.{0,10}crypto'
                ],
                'description': 'Find currently trending cryptocurrencies'
            },
            'performance': {
                'keywords': ['perform', 'best', 'worst', 'top', 'leader'],
                'patterns': [
                    r'best.{0,10}perform',
                    r'worst.{0,10}perform',
                    r'top.{0,10}coin',
                    r'market.{0,10}leader'
                ],
                'description': 'Find best or worst performing cryptocurrencies'
            }
        }
        
        # Cryptocurrency symbol patterns
        self.crypto_patterns = [
            r'\b[A-Z]{2,10}\b',  # 2-10 uppercase letters (likely symbols)
            r'\$[A-Z]{2,10}\b',  # $ prefix
            r'\b(bitcoin|btc|ethereum|eth|cardano|ada|solana|sol|polkadot|dot)\b'
        ]
        
        # Timeframe patterns
        self.timeframe_patterns = {
            '1h': [r'1\s*hour?', r'past\s*hour', r'last\s*hour'],
            '24h': [r'24\s*hours?', r'1\s*day', r'today', r'daily'],
            '7d': [r'7\s*days?', r'1\s*week', r'weekly', r'past\s*week'],
            '30d': [r'30\s*days?', r'1\s*month', r'monthly', r'past\s*month']
        }
        
    def parse_intent(self, query_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse query text to detect intent and extract parameters
        
        Args:
            query_text: Natural language query
            
        Returns:
            Dictionary with intent information or None
        """
        try:
            query_lower = query_text.lower()
            logger.info(f"Parsing query: '{query_text}'")
            
            # Score each intent
            intent_scores = {}
            
            for intent_name, intent_config in self.intent_patterns.items():
                score = self._calculate_intent_score(query_lower, intent_config)
                if score > 0:
                    intent_scores[intent_name] = score
            
            if not intent_scores:
                return None
            
            # Get highest scoring intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_name, confidence = best_intent
            
            # Extract additional parameters
            cryptocurrencies = self._extract_cryptocurrencies(query_text)
            timeframe = self._extract_timeframe(query_lower)
            
            result = {
                'type': intent_name,
                'confidence': round(confidence, 3),
                'cryptocurrencies': cryptocurrencies,
                'timeframe': timeframe,
                'original_query': query_text
            }
            
            logger.info(f"Detected intent: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing intent: {str(e)}")
            return None
    
    def _calculate_intent_score(self, query_lower: str, intent_config: Dict) -> float:
        """
        Calculate score for an intent based on keywords and patterns
        
        Args:
            query_lower: Lowercase query text
            intent_config: Intent configuration with keywords and patterns
            
        Returns:
            Score from 0-1
        """
        score = 0.0
        
        # Check keywords (each match adds 0.2)
        for keyword in intent_config['keywords']:
            if keyword in query_lower:
                score += 0.2
        
        # Check regex patterns (each match adds 0.3)
        for pattern in intent_config['patterns']:
            if re.search(pattern, query_lower, re.IGNORECASE):
                score += 0.3
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _extract_cryptocurrencies(self, query_text: str) -> List[str]:
        """
        Extract cryptocurrency symbols from query text
        
        Args:
            query_text: Original query text
            
        Returns:
            List of detected cryptocurrency symbols
        """
        cryptos = set()
        
        for pattern in self.crypto_patterns:
            matches = re.findall(pattern, query_text, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                clean_match = match.replace('$', '').upper()
                if len(clean_match) >= 2 and len(clean_match) <= 10:
                    cryptos.add(clean_match)
        
        return list(cryptos)
    
    def _extract_timeframe(self, query_lower: str) -> str:
        """
        Extract timeframe from query text
        
        Args:
            query_lower: Lowercase query text
            
        Returns:
            Detected timeframe or default '24h'
        """
        for timeframe, patterns in self.timeframe_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return timeframe
        
        # Default timeframe
        return '24h'
    
    def get_interpretation(self, intent: Dict[str, Any]) -> str:
        """
        Get human-readable interpretation of the detected intent
        
        Args:
            intent: Intent dictionary from parse_intent
            
        Returns:
            Human-readable description
        """
        if not intent:
            return "Could not understand the query"
        
        intent_type = intent.get('type')
        cryptocurrencies = intent.get('cryptocurrencies', [])
        timeframe = intent.get('timeframe', '24h')
        
        # Get base description
        base_description = self.intent_patterns.get(intent_type, {}).get('description', 'Unknown intent')
        
        # Build interpretation
        parts = [base_description]
        
        if cryptocurrencies:
            crypto_str = ', '.join(cryptocurrencies)
            parts.append(f"specifically for {crypto_str}")
        
        # Add timeframe
        timeframe_map = {
            '1h': 'in the last hour',
            '24h': 'in the last 24 hours', 
            '7d': 'in the last week',
            '30d': 'in the last month'
        }
        parts.append(timeframe_map.get(timeframe, f"in the {timeframe} timeframe"))
        
        return ' '.join(parts)
    
    def get_supported_queries(self) -> List[Dict[str, str]]:
        """
        Get list of supported query types with examples
        
        Returns:
            List of query examples
        """
        examples = [
            {
                'intent': 'pump_and_dump',
                'example': 'Show me pump and dump signals',
                'description': 'Find potential market manipulation schemes'
            },
            {
                'intent': 'bottomed_out',
                'example': 'Which coins have bottomed out?',
                'description': 'Find cryptocurrencies that may have hit bottom'
            },
            {
                'intent': 'uptrend',
                'example': 'What coins are trending up?',
                'description': 'Find cryptocurrencies in upward trends'
            },
            {
                'intent': 'downtrend',
                'example': 'Show me coins going down',
                'description': 'Find cryptocurrencies in downward trends'
            },
            {
                'intent': 'high_volatility',
                'example': 'Which coins are most volatile?',
                'description': 'Find highly volatile cryptocurrencies'
            },
            {
                'intent': 'volume_spike',
                'example': 'Show unusual volume activity',
                'description': 'Find cryptocurrencies with volume anomalies'
            },
            {
                'intent': 'trending',
                'example': 'What\'s trending now?',
                'description': 'Find currently popular cryptocurrencies'
            },
            {
                'intent': 'performance',
                'example': 'Show me the best performers',
                'description': 'Find top performing cryptocurrencies'
            }
        ]
        
        return examples 