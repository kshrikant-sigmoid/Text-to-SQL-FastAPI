import React, { useState, useEffect } from 'react';
import axios from '../services/axiosConfig'
import './History.css';
import { Link } from 'react-router-dom'

export default function History({ username }) {
  const [history, setHistory] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = document.cookie.split('; ').find(row => row.startsWith('token')).split('=')[1];
    if (token) {
      setIsLoggedIn(true);
    fetchHistory();
  }
  }, [username]);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/history/`);
      setHistory(response.data.history);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    !isLoggedIn ? (
      <div className='notLoggedInContainer'>
      <h2>You are not logged in</h2>
      <p>Please <Link to="/">Login</Link> and try again.</p>
    </div>
    ) : (
    <ul>
      {Object.values(history).map((item, index) => (
        <li key={index} className='history-item'>
          <p><strong>Question:</strong> {item.question}</p>
          <p><strong>Query:</strong> {item.query}</p>
          <p><strong>Result:</strong> {item.result}</p>
          <p><strong>Insights:</strong> {item.insights}</p>
        </li>
      ))}
    </ul>
    )
  );
}