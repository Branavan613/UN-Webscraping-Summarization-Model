import React from 'react';

function LinkList({ links }) {
  return (
    <div>
      <h2>Document Links</h2>
      <ul>
        {links.length > 0 ? (
          links.map((link, index) => (
            <li key={index}>
              <strong>{link[0]}</strong> - <a href={link[1]} target="_blank" rel="noopener noreferrer">View Document</a>
            </li>
          ))
        ) : (
          <p>No links available. Click "Fetch Document Links" to load.</p>
        )}
      </ul>
    </div>
  );
}

export default LinkList;
