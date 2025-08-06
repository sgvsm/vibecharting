import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ChatInterface } from './components/ChatInterface';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#10a37f', // ChatGPT green
    },
    background: {
      default: '#343541',
      paper: '#444654',
    },
    text: {
      primary: '#ececf1',
      secondary: '#d1d5db',
    },
  },
  typography: {
    fontFamily: '"Söhne", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <ChatInterface />
      </div>
    </ThemeProvider>
  );
}

export default App;
