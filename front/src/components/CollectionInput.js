import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function CollectionInput() {
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

  const [name, setName] = useState('');
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [collections, setCollections] = useState([])
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchCollections()
  }, [])

  const handleCollectionSelect = (collection) => {
    navigate(`/chat/${collection}`);
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !keyword.trim()) {
      return alert('Please fill out both the name and keyword fields.');
    }
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: name, subject: keyword }),
      });
      const data = await response.json();
      if (data.keyword) {
        navigate(`/chat/${data.keyword}`);
      } else {
        alert('Failed to scrape the collection.');
      }
    } catch (error) {
      console.error('Error submitting the form:', error);
      alert('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Create Collection</h1>
      <form onSubmit={handleSubmit}>
        {/* Form for Name */}
        <div>
          
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter collection name"
            required
          />
        </div>
        {/* Form for Keyword */}
        <div>
          
          <input
            id="keyword"
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Enter a keyword"
            required
          />
        </div>
        {/* Submit Button */}
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Submit'}
        </button>
      </form>
      {collections.map((collection, idx) => (
          <button
            key={idx}
            onClick={() => handleCollectionSelect(collection)}
            style={{
              display: 'block',
              margin: '10px 0',
              padding: '10px',
              width: '100%',
              textAlign: 'center',
              backgroundColor: '#f0f0f0',
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
  );
}

export default CollectionInput;
