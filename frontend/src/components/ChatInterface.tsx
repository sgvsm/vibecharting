import React, { useState, useRef, useEffect } from 'react';
import { Box, Container } from '@mui/material';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { Message } from '../types/Message';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! I\'m your Crypto Trend Analysis Assistant. I can help you analyze cryptocurrency trends, detect signals, and provide market insights. Ask me anything about crypto trends!',
      timestamp: new Date(),
      isTyping: false,
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      isTyping: false,
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate AI response
    setIsTyping(true);

    // Simulate API delay
    setTimeout(() => {
      const aiResponse = generateDemoResponse(message);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date(),
        isTyping: false,
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const generateDemoResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes('trend') || lowerQuery.includes('going up') || lowerQuery.includes('uptrend')) {
      return `Here are the top trending cryptocurrencies in the last 24 hours:

🚀 **Bitcoin (BTC)**: +12.5% - Strong uptrend with high volume
📈 **Ethereum (ETH)**: +8.3% - Breaking resistance levels
⚡ **Solana (SOL)**: +15.2% - Volume spike detected
🎯 **Cardano (ADA)**: +6.7% - Gradual uptrend pattern

**Analysis**: Market showing bullish momentum with Bitcoin leading the charge. Volume is above average, indicating strong buying pressure.`;
    }

    if (lowerQuery.includes('pump') || lowerQuery.includes('dump') || lowerQuery.includes('volatile')) {
      return `⚠️ **Pump & Dump Signals Detected**:

🔥 **Kayyo (KYO)**: 100% confidence - Volume spike 2.15x, Price: $0.00198
⚡ **PNP Exchange (PNP)**: 100% confidence - Volume spike 3.01x, Price: $0.00157
🚨 **SuperFriend (SUPFRIEND)**: 100% confidence - Volume spike 2.03x, Price: $0.00030
💥 **FITCOIN (FITCOIN)**: 100% confidence - Volume spike 1.41x, Price: $0.00274
⚡ **ZENKOKU (CDB)**: 100% confidence - Volume spike 2.13x, Price: $0.00215

**Risk Level**: HIGH - These patterns suggest potential pump and dump activity. Exercise extreme caution.

**Analysis**: Multiple signals detected with 100% confidence scores. Volume spikes ranging from 1.4x to 3.0x normal levels. All showing downtrend patterns indicating potential manipulation.`;
    }

    if (lowerQuery.includes('bottom') || lowerQuery.includes('reversal') || lowerQuery.includes('bounce')) {
      return `🔄 **Bottom Out Signals Detected**:

📉 **Kayyo (KYO)**: 92.07% trend confidence - Showing reversal patterns
🔄 **ZENKOKU (CDB)**: 75.42% trend confidence - Mixed signals (downtrend/uptrend)
📊 **SuperFriend (SUPFRIEND)**: 78.20% trend confidence - Support level reached
📈 **FITCOIN (FITCOIN)**: 55.07% trend confidence - Potential bounce levels

**Analysis**: Several coins showing potential reversal signals. KYO has the highest confidence at 92.07%. Monitor for confirmation of trend changes.`;
    }

    if (lowerQuery.includes('volume') || lowerQuery.includes('spike')) {
      return `📊 **Volume Anomaly Detection**:

🔥 **PNP Exchange (PNP)**: 3.01x average volume - SIGNIFICANT SPIKE
⚡ **Kayyo (KYO)**: 2.15x average volume - High activity detected
🚀 **ZENKOKU (CDB)**: 2.13x average volume - Unusual volume pattern
📈 **SuperFriend (SUPFRIEND)**: 2.03x average volume - Volume spike detected
💥 **FITCOIN (FITCOIN)**: 1.41x average volume - Above normal activity

**Analysis**: PNP Exchange showing the highest volume spike at 3.01x normal levels. High volume often precedes major price movements. Multiple coins showing unusual activity patterns.`;
    }

    if (lowerQuery.includes('market') || lowerQuery.includes('overview') || lowerQuery.includes('summary')) {
      return `📈 **Market Overview - Last 24 Hours**:

🟢 **Bullish**: 65% of tracked coins
🔴 **Bearish**: 25% of tracked coins
🟡 **Sideways**: 10% of tracked coins

**Top Performers**:
- Bitcoin (BTC): +12.5%
- Solana (SOL): +15.2%
- Ethereum (ETH): +8.3%

**High Risk Signals**:
- 5 pump & dump signals detected
- Average confidence: 96.8%
- Volume spikes up to 3.01x normal

**Market Sentiment**: Bullish with strong institutional buying detected, but high volatility in smaller cap tokens.`;
    }

    return `I can help you analyze cryptocurrency trends! Try asking me about:

• "What coins are trending up?"
• "Show me pump and dump signals"
• "Which coins have bottomed out?"
• "Detect volume anomalies"
• "Give me a market overview"

I analyze real-time data to provide you with actionable insights!`;
  };

  return (
    <Box sx={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#343541'
    }}>
      <Container maxWidth="lg" sx={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        py: 0
      }}>
        <MessageList
          messages={messages}
          isTyping={isTyping}
        />
        <div ref={messagesEndRef} />
        <ChatInput onSendMessage={handleSendMessage} />
      </Container>
    </Box>
  );
}; 