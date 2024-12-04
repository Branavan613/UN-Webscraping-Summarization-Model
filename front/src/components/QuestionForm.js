import React, { useState } from 'react';

function QuestionForm({ askQuestion, collection}) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(question, collection);
  };

  return (
    <div>
      <h2>Ask a Question</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question"
          required
        />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default QuestionForm;
