import React, { useState, useEffect } from 'react';

interface TypeItProps {
  content: string;
}

export const TypeIt: React.FC<TypeItProps> = ({ content }) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (content && currentIndex < content.length) {
      const timer = setTimeout(() => {
        setDisplayedContent(content.slice(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }, 15); // Speed of typing - reduced from 30ms to 15ms

      return () => clearTimeout(timer);
    }
  }, [content, currentIndex]);

  useEffect(() => {
    setDisplayedContent('');
    setCurrentIndex(0);
  }, [content]);

  return (
    <span style={{ color: '#ececf1' }}>
      {displayedContent}
      {currentIndex < content.length && (
        <span style={{ 
          color: '#ececf1',
          animation: 'blink 1s infinite'
        }}>
          |
        </span>
      )}
      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>
    </span>
  );
}; 