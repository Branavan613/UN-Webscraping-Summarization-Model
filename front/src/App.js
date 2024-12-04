import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CollectionInput from './components/CollectionInput';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CollectionInput />} />
        <Route path="/chat/:topic" element={<ChatInterface />} />
      </Routes>
    </Router>
  );
}

export default App;
