import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from '../services/axiosConfig';


const DocumentQuery = () => {
    const [question, setQuestion] = useState('');
    const [filenames, setFilenames] = useState([]);
    const [selectedFilename, setSelectedFilename] = useState('');
    const [responseQuestion, setResponseQuestion] = useState('');
    const [responseAnswer, setResponseAnswer] = useState('');

  useEffect(() => {
    const fetchFilenames = async () => {
      try {
        const response = await axios.get('http://localhost:8000/index_names/');
        if (response.data.index_names.length === 0) {
            toast.error("No files available")
        } else {
        setFilenames(response.data.index_names);
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    };

    fetchFilenames();
  }, []);

  const onQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  const onFilenameChange = (event) => {
    setSelectedFilename(event.target.value);
  };

  const onQuerySubmit = async () => {
    try {
      const response = await axios.post('http://localhost:8000/document/', {
        question: question ,
        index_name: selectedFilename,
    }, { withCredentials: true });
    
    if (response.status === 200) {
        alert('Query processed successfully');
        setResponseQuestion(response.data.question);
        setResponseAnswer(response.data.answer)
    } else {
        console.error('Failed to process query');
    }
} catch (error) {
    console.error('An error occurred:', error);
}
  };

  return (
    <div>
      <input type="text" placeholder="Question" onChange={onQuestionChange} />
      {filenames.map((filename) => (
        <div key={filename}>
          <input
            type="radio"
            id={filename}
            value={filename}
            checked={selectedFilename === filename}
            onChange={onFilenameChange}
          />
          <label htmlFor={filename}>{filename}</label>
        </div>
      ))}
      <button onClick={onQuerySubmit}>Submit Query</button>
      <div>
        <h2>Question</h2>
        <p>{ responseQuestion}</p>
        <h2>Answer</h2>
        <p>{responseAnswer}</p>
      </div>
    </div>
  );
};

export default DocumentQuery;