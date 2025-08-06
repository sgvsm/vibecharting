import React, { useState, KeyboardEvent } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  Paper,
  Container,
  Typography
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        position: 'sticky',
        bottom: 0,
        backgroundColor: '#343541',
        borderTop: '1px solid #565869',
        py: 2,
        px: 2,
      }}
    >
      <Container maxWidth="lg">
        <Paper
          elevation={0}
          sx={{
            display: 'flex',
            alignItems: 'flex-end',
            backgroundColor: '#40414f',
            border: '1px solid #565869',
            borderRadius: 2,
            p: 1,
            '&:hover': {
              borderColor: '#10a37f',
            },
            '&:focus-within': {
              borderColor: '#10a37f',
              borderWidth: '2px',
            },
          }}
        >
          <TextField
            multiline
            maxRows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Message Crypto Trend Analysis Assistant..."
            variant="standard"
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                color: '#ececf1',
                fontSize: '16px',
                fontFamily: '"Söhne", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
                '&:before': { borderBottom: 'none' },
                '&:after': { borderBottom: 'none' },
                '&:hover:before': { borderBottom: 'none' },
              },
              '& .MuiInputBase-input': {
                padding: '12px 0',
                '&::placeholder': {
                  color: '#8e8ea0',
                  opacity: 1,
                },
              },
            }}
          />
          <IconButton
            onClick={handleSend}
            disabled={!message.trim()}
            sx={{
              color: message.trim() ? '#10a37f' : '#565869',
              ml: 1,
              mb: 0.5,
              '&:hover': {
                backgroundColor: message.trim() ? 'rgba(16, 163, 127, 0.1)' : 'transparent',
              },
              '&.Mui-disabled': {
                color: '#565869',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Paper>
        
        <Typography
          variant="caption"
          sx={{
            color: '#8e8ea0',
            textAlign: 'center',
            display: 'block',
            mt: 1,
            fontSize: '12px',
          }}
        >
          Press Enter to send, Shift+Enter for new line
        </Typography>
      </Container>
    </Box>
  );
}; 