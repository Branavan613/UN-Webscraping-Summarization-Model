import React from 'react';

function Message({ role, content }) {
  return (
    <div>
      {role === 0 ? <strong>{content}</strong> : <p>{content}</p>}
    </div>
  );
}

function MessageList({ returned_messages }) {
  // Ensure `returned_messages` is an array
  const messages = Array.isArray(returned_messages) ? returned_messages : Object.values(returned_messages || {});
  console.log("Messages:", messages);
  return (
    <div>
      <h2>Messages</h2>
      <ul>
        {Array.isArray(messages) && messages.length > 0 ? (
          messages.map((message, index) => (
            <li key={index}>
              <Message role={message.role} content={message.content} />
            </li>
          ))
        ) : (
          <p>No messages available.</p>
        )}
      </ul>
    </div>
  );
}

export default MessageList;
