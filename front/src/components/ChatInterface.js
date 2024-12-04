import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

function Citations({ citations }) {
  return (
    <div className="citations">
      {citations.map((citation, index) => (
        <span key={index}>
          <a
            href={`${citation.url}#page=${citation.page}`}
            target="_blank"
            rel="noopener noreferrer"
            className="citation-link"
            title={`${citation.title} (Page ${citation.page})`}
          >
            {index + 1}
          </a>
          <span>&nbsp;</span> {/* The space outside the link */}
        </span>
      ))}
    </div>
  );
}

function ChatInterface() {
  const { topic } = useParams();
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(topic || '');
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Reference to the chat box container
  const chatBoxRef = useRef(null);

  // Handle collection selection
  const handleCollectionSelect = useCallback(
    (collection) => {
      setSelectedCollection(collection);
      fetchChatHistory(collection);
  }, []);
  
  // Fetch collection list
  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/list-collections', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        setCollections(data.collectionList || []);
      } catch (error) {
        console.error('Error fetching collections:', error);
      }
    };
    fetchCollections();
    handleCollectionSelect(selectedCollection);
  }, [selectedCollection, handleCollectionSelect]);

  // Fetch chat history for a specific collection
  const fetchChatHistory = async (collection) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/chat-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: collection }),
      });
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  // Handle user asking a question
  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, keyword: selectedCollection, history: messages.map((message) => [message.role === 0 ? 'assistant' : 'user', message.content]) }),
      });
      const data = await response.json();
      if (data.error) {
        console.log(data.error)
      } else {
         await fetch('http://127.0.0.1:5000/chat-save', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'keyword': selectedCollection, 'content': [question, data.answer], 'citations': data.citation })
            })
      }
      fetchChatHistory(selectedCollection);
    } catch (error) {
      console.error('Error asking question:', error);
    } finally {
      setLoading(false);
      setQuestion('');
    }
  };

  // Scroll to the bottom on initial render
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]); // Ensure to scroll when messages change

  // Remember the scroll position when the user leaves
  const handleScroll = () => {
    if (chatBoxRef.current) {
      localStorage.setItem('chatScrollPosition', chatBoxRef.current.scrollTop);
    }
  };

  // Restore scroll position when the user returns
  useEffect(() => {
    const savedScrollPosition = localStorage.getItem('chatScrollPosition');
    if (savedScrollPosition && chatBoxRef.current) {
      chatBoxRef.current.scrollTop = savedScrollPosition;
    }
  }, []);

  return (
    <div className="chat-interface-container" style={{ display: 'flex', height: '100vh' }}>
      {/* Left column: Collection list */}
      <div
        className="collection-list"
        style={{
          width: '20%',
          borderRight: '1px solid #ccc',
          padding: '20px',
          overflowY: 'auto',
        }}
      >
        <h2>Collections</h2>
        {collections.map((collection, idx) => (
          <button
            key={idx}
            onClick={() => handleCollectionSelect(collection)}
            style={{
              display: 'block',
              margin: '10px 0',
              padding: '10px',
              width: '100%',
              textAlign: 'left',
              backgroundColor: selectedCollection === collection ? '#fff' : '#f0f0f0',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer',
              color: 'black',
            }}
          >
            {collection}
          </button>
        ))}
      </div>

      {/* Right column: Chat interface */}
      <div className="chat-container" style={{ width: '70%', padding: '20px' }}>
        <h1>Chat - Topic: {selectedCollection}</h1>
        <div
          ref={chatBoxRef}
          className="chat-box"
          style={{
            border: '1px solid #ccc',
            borderRadius: '4px',
            padding: '10px',
            height: '70vh',
            overflowY: 'scroll',
            marginBottom: '20px',
          }}
          onScroll={handleScroll} // Save scroll position on scroll
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={msg.role === 'user' ? 'user-message' : 'bot-message'}
              style={{
                marginBottom: '10px',
                padding: '10px',
                borderRadius: '4px',
                backgroundColor: msg.role === 1 ? '#d1e7dd' : '#f9f9f9',
                textAlign: msg.role === 1 ? 'right' : 'left',
              }}
            >
              <span>
                  {msg.role === 1 ? msg.content : <ReactMarkdown>{msg.content}</ReactMarkdown>}
              </span>
              <Citations citations={ msg.citations } />
            </div>
          ))}
        </div>
        <form onSubmit={handleAsk} className="chat-input">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            style={{ width: '80%', padding: '10px', marginRight: '10px' }}
            required
          />
          <button
            type="submit"
            disabled={loading || !selectedCollection}
            style={{
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatInterface;
