import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import './App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [showDashboard, setShowDashboard] = useState(false);
  const [codeResponse, setCodeResponse] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = { sender: 'user', text: input };
    setMessages([...messages, newMessage]);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();

      if (data.response.includes('import')) {
        setShowDashboard(true);
        setCodeResponse(data.response);

        const botMessage = {
          sender: 'bot',
          text: 'Please check out the generated code in the Code Dashboard.',
        };
        setMessages(prevMessages => [...prevMessages, botMessage]);
      } else {
        const botMessage = { sender: 'bot', text: data.response };
        setMessages(prevMessages => [...prevMessages, botMessage]);
      }
    } catch (error) {
      console.error('Error:', error);
    }

    setInput('');
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Add success message
        const uploadMessage = {
          sender: 'bot',
          text: `File "${file.name}" uploaded successfully.`,
        };
        setMessages(prevMessages => [...prevMessages, uploadMessage]);

        // Automatically send a message to summarize the uploaded document
        const summaryRequest = `For ${file.name} file, read it from top to bottom and give me a 5 lines of summary`;
        setMessages(prevMessages => [
          ...prevMessages,
          { sender: 'user', text: summaryRequest },
        ]);

        // Fetch the summary from the backend
        const summaryResponse = await fetch('http://localhost:5000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: summaryRequest }),
        });

        const summaryData = await summaryResponse.json();

        const summaryMessage = {
          sender: 'bot',
          text: summaryData.response,
        };
        setMessages(prevMessages => [...prevMessages, summaryMessage]);
      } else {
        throw new Error(data.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = {
        sender: 'bot',
        text: `Error uploading file: ${error.message}`,
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setUploading(false);
    }
  };

  const handleCloseDashboard = () => {
    setShowDashboard(false);
  };

  return (
    <div className="main-container">
      <div className={`chat-container ${showDashboard ? 'compressed' : ''}`}>
        <h1 className="page-title">AI Assistant</h1>
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your message..."
            className="message-input"
            disabled={uploading}
          />
          <label className="upload-button" title="Upload file">
            <input
              type="file"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              disabled={uploading}
            />
            <Upload
              className={`w-5 h-5 ${
                uploading
                  ? 'text-gray-400'
                  : 'text-gray-600 hover:text-gray-800'
              } cursor-pointer`}
            />
          </label>
          <button
            onClick={handleSendMessage}
            className="send-button"
            disabled={uploading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>

      {showDashboard && (
        <div className="dashboard">
          <button className="close-button" onClick={handleCloseDashboard}>
            ×
          </button>
          <h2>Code Snippet</h2>
          <pre>{codeResponse}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
