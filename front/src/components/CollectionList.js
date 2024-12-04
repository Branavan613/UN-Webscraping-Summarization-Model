import React from 'react';

function CollectionList({ collections }) {
  return (
    <div>
      <h2>Messages</h2>
      <ul>
        {Array.isArray(collections) && collections.length > 0 ? (
          collections.map((col, index) => (
            <li key={index}>
              <h2>{col}</h2>
            </li>
          ))
        ) : (
          <p>No collections available.</p>
        )}
      </ul>
    </div>
  );
}

export default CollectionList;
