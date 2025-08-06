# Crypto Trend Analysis Chatbot - Frontend

## 🚀 Quick Start

This is a React TypeScript frontend for the Crypto Trend Analysis Chatbot, featuring a ChatGPT-like interface.

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```bash
npm install
```

### Development
```bash
npm start
```

The app will open at `http://localhost:3000`

### Build for Production
```bash
npm run build
```

## 🎨 Features

### ChatGPT-like Interface
- **Dark Theme**: Matches ChatGPT's color scheme
- **Typing Animation**: Uses TypeIt for realistic typing effects
- **Responsive Design**: Works on desktop and mobile
- **Real-time Chat**: Instant message display with typing indicators

### Demo Responses
The frontend includes hardcoded demo responses for:
- **Trend Analysis**: "What coins are trending up?"
- **Pump & Dump Detection**: "Show me pump and dump signals"
- **Bottom Out Signals**: "Which coins have bottomed out?"
- **Volume Anomalies**: "Detect volume spikes"
- **Market Overview**: "Give me a market overview"

### Interactive Features
- **Enter to Send**: Press Enter to send messages
- **Shift+Enter**: New line for multi-line messages
- **Auto-scroll**: Messages automatically scroll to bottom
- **Typing Indicators**: Shows when AI is "thinking"

## 🏗️ Architecture

### Components
- **ChatInterface**: Main container component
- **MessageList**: Displays chat messages
- **ChatInput**: Input field with send button
- **TypeIt**: Wrapper for typing animation

### Styling
- **Material-UI**: Component library
- **Dark Theme**: ChatGPT-inspired colors
- **Custom CSS**: Additional styling for chat interface

## 🔧 API Integration

### Current State
- Hardcoded demo responses
- Simulated API delays
- Ready for real API integration

### Future Integration
```typescript
// Example API call (to be implemented)
const response = await fetch('/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: message })
});
```

## 📁 File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── MessageList.tsx      # Message display
│   │   ├── ChatInput.tsx        # Input field
│   │   └── TypeIt.tsx          # Typing animation
│   ├── types/
│   │   └── Message.ts          # TypeScript types
│   ├── App.tsx                 # Main app component
│   └── App.css                 # Global styles
├── public/                     # Static assets
└── package.json               # Dependencies
```

## 🎯 Demo Queries

Try these example queries to see the demo responses:

1. **"What coins are trending up?"** - Shows trending cryptocurrencies
2. **"Show me pump and dump signals"** - Detects volatile patterns
3. **"Which coins have bottomed out?"** - Finds reversal candidates
4. **"Detect volume anomalies"** - Shows volume spikes
5. **"Give me a market overview"** - Market summary

## 🚀 Deployment

### AWS Amplify
This frontend is designed to be deployed on AWS Amplify:

1. **Connect Repository**: Link your Git repository
2. **Build Settings**: 
   - Framework: React
   - Build command: `npm run build`
   - Output directory: `build`
3. **Environment Variables**:
   ```
   REACT_APP_API_URL = [your-api-gateway-url]
   ```

### Environment Variables
```bash
REACT_APP_API_URL=https://api.vibe-charting.com/prod
```

## 🔄 Next Steps

1. **API Integration**: Replace hardcoded responses with real API calls
2. **Error Handling**: Add proper error states and retry logic
3. **Loading States**: Improve loading indicators
4. **Authentication**: Add user authentication if needed
5. **Real-time Updates**: WebSocket integration for live data

## 📞 Support

For issues or questions:
1. Check the console for errors
2. Verify all dependencies are installed
3. Ensure Node.js version is compatible
4. Check the main project documentation
