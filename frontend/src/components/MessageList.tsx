import React from 'react';
import { Box, Avatar, Typography } from '@mui/material';
import { TypeIt } from './TypeIt';
import { Message } from '../types/Message';

interface MessageListProps {
  messages: Message[];
  isTyping: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isTyping }) => {
  return (
    <Box sx={{ 
      flex: 1, 
      overflowY: 'auto',
      py: 2,
      px: 2
    }}>
      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            display: 'flex',
            mb: 2,
            backgroundColor: message.type === 'user' ? '#343541' : '#444654',
            py: 3,
            px: 2,
            borderRadius: 1,
          }}
        >
          <Avatar
            sx={{
              width: 32,
              height: 32,
              mr: 2,
              backgroundColor: message.type === 'user' ? '#10a37f' : '#f7f7f8',
              color: message.type === 'user' ? '#fff' : '#000',
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            {message.type === 'user' ? 'U' : 'AI'}
          </Avatar>
          
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              component="div"
              sx={{
                color: '#ececf1',
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
                fontFamily: '"Söhne", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
                fontSize: '16px',
              }}
            >
              {message.type === 'ai' ? (
                <TypeIt key={message.id} content={message.content} />
              ) : (
                message.content
              )}
            </Typography>
            
            <Typography
              variant="caption"
              sx={{
                color: '#8e8ea0',
                mt: 1,
                display: 'block',
                fontSize: '12px',
              }}
            >
              {message.timestamp.toLocaleTimeString()}
            </Typography>
          </Box>
        </Box>
      ))}
      
      {isTyping && (
        <Box
          sx={{
            display: 'flex',
            mb: 2,
            backgroundColor: '#444654',
            py: 3,
            px: 2,
            borderRadius: 1,
          }}
        >
          <Avatar
            sx={{
              width: 32,
              height: 32,
              mr: 2,
              backgroundColor: '#f7f7f8',
              color: '#000',
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            AI
          </Avatar>
          
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#ececf1',
                  animation: 'typing 1.4s infinite ease-in-out',
                  '&:nth-of-type(1)': { animationDelay: '0s' },
                  '&:nth-of-type(2)': { animationDelay: '0.2s' },
                  '&:nth-of-type(3)': { animationDelay: '0.4s' },
                  '@keyframes typing': {
                    '0%, 60%, 100%': { transform: 'translateY(0)' },
                    '30%': { transform: 'translateY(-10px)' },
                  },
                }}
              />
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#ececf1',
                  animation: 'typing 1.4s infinite ease-in-out',
                  '&:nth-of-type(1)': { animationDelay: '0s' },
                  '&:nth-of-type(2)': { animationDelay: '0.2s' },
                  '&:nth-of-type(3)': { animationDelay: '0.4s' },
                  '@keyframes typing': {
                    '0%, 60%, 100%': { transform: 'translateY(0)' },
                    '30%': { transform: 'translateY(-10px)' },
                  },
                }}
              />
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#ececf1',
                  animation: 'typing 1.4s infinite ease-in-out',
                  '&:nth-of-type(1)': { animationDelay: '0s' },
                  '&:nth-of-type(2)': { animationDelay: '0.2s' },
                  '&:nth-of-type(3)': { animationDelay: '0.4s' },
                  '@keyframes typing': {
                    '0%, 60%, 100%': { transform: 'translateY(0)' },
                    '30%': { transform: 'translateY(-10px)' },
                  },
                }}
              />
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
}; 