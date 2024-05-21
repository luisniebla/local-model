// src/Chat.js
import React, { useEffect, useState } from 'react';

const Chat = () => {
  const [sessionId, setSessionId] = useState('');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);


    useEffect(() => {
        const response = fetch('http://localhost:8000/init', {
        method: 'GET',
      }).then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
          }
        response.json().then((data) => {
          const { session_id, response: chatResponse } = data;
          setSessionId(session_id);
          setMessages([...messages, { role: 'assistant', content: chatResponse }]);
          setInput('');
        })
          
      })

      
    }, [])
  const sendMessage = async () => {
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          input: input,
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const { session_id, response: chatResponse } = data;
      console.log('session_id, session_id', session_id)
      setSessionId(session_id);
      setMessages([...messages, { role: 'user', content: input }, { role: 'assistant', content: chatResponse }]);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div>
      <h1>Chat with Assistant</h1>
      <div style={{ marginBottom: '20px' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ padding: '5px 0' }}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        style={{ marginRight: '10px' }}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};

export default Chat;
