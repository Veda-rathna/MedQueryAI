import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message, isUser }) => {
  const highlightContent = (text) => {
    // Highlight dosage-related terms
    text = text.replace(
      /(\d+\s*mg|\d+\s*mcg|once daily|twice daily|dosage|dose)/gi,
      '<span class="highlight-dosage">$1</span>'
    );

    // Highlight warnings
    text = text.replace(
      /(warning|caution|risk|serious|death|fatal)/gi,
      '<span class="highlight-warning">$1</span>'
    );

    // Highlight contraindications
    text = text.replace(
      /(contraindicated|contraindication|should not|do not use)/gi,
      '<span class="highlight-contraindication">$1</span>'
    );

    return text;
  };

  const extractCitations = (text) => {
    const citationRegex = /\(Page\s+(\d+(?:,?\s*(?:and\s+)?\d+)*)\)/gi;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = citationRegex.exec(text)) !== null) {
      // Add text before citation
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: text.slice(lastIndex, match.index)
        });
      }

      // Add citation
      parts.push({
        type: 'citation',
        content: match[0],
        pages: match[1]
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.slice(lastIndex)
      });
    }

    return parts.length > 0 ? parts : [{ type: 'text', content: text }];
  };

  const parts = extractCitations(message.content);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`
          max-w-[80%] rounded-lg px-4 py-3 shadow-sm
          ${isUser
            ? 'bg-primary text-white'
            : 'bg-gray-100 text-gray-800'
          }
        `}
      >
        <div className="flex items-start space-x-2">
          <div className="text-xl">
            {isUser ? '👤' : '🤖'}
          </div>
          <div className="flex-1">
            <div className="markdown-content">
              {parts.map((part, index) => {
                if (part.type === 'citation') {
                  return (
                    <span
                      key={index}
                      className="inline-block bg-white text-primary px-2 py-0.5 rounded text-sm font-semibold ml-1 cursor-pointer hover:bg-blue-50 transition-colors"
                      title={`Reference: Page ${part.pages}`}
                    >
                      {part.content}
                    </span>
                  );
                } else {
                  return (
                    <span
                      key={index}
                      dangerouslySetInnerHTML={{
                        __html: highlightContent(part.content)
                      }}
                    />
                  );
                }
              })}
            </div>
            {message.timestamp && (
              <div className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
