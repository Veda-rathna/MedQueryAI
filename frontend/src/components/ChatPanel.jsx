import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { sendMessage } from '../services/api';

const ChatPanel = ({ documentId, sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendMessage(inputValue, sessionId, documentId);

      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: response.timestamp,
        sources: response.sources
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);

      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure LM Studio is running and try again.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const exampleQuestions = [
    "What is the recommended dosage for ulcerative colitis?",
    "What are the boxed warnings?",
    "Is RINVOQ contraindicated in hepatic impairment?",
    "What are the common adverse reactions?",
    "What should be evaluated before initiating treatment?"
  ];

  return (
    <div className="bg-white rounded-lg shadow-md flex flex-col h-[600px]">
      {/* Header */}
      <div className="border-b px-6 py-4 flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-800">
          💬 Ask Questions
        </h2>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="text-6xl mb-4">🩺</div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Drug Information Assistant
            </h3>
            <p className="text-gray-500 mb-6 max-w-md">
              Ask questions about the uploaded prescribing information.
              I'll answer using only the official document content.
            </p>

            <div className="space-y-2 w-full max-w-md">
              <p className="text-sm font-semibold text-gray-600 mb-2">
                Example questions:
              </p>
              {exampleQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(question)}
                  className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                isUser={message.role === 'user'}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 rounded-lg px-4 py-3 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="text-xl">🤖</div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="border-t px-6 py-4">
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the prescribing information..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            rows="2"
            disabled={!documentId || isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || !documentId || isLoading}
            className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
