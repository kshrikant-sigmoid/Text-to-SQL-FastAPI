import './Login.css';
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/login/', {
        username,
        password,
      });
      if (response.data.token) {
        // Set the token as a cookie
        const expirationDate = new Date();
        expirationDate.setMinutes(expirationDate.getMinutes() + 30); 
        document.cookie = `token=${response.data.token}; expires=${expirationDate.toUTCString()}; path=/`;
        navigate('/query', {state: {message: response.data.message }});
      }
    } catch (error) {
        if (error.response && error.response.data && error.response.data.detail) {
            alert(error.response.data.detail);
          } else {
            alert('An error occurred while logging in.');
          }  
    }
  };

  return (
    <div>
    <h2>Login</h2>
    <form onSubmit={handleSubmit}>
      <input type="text" placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="password" placeholder='password' value={password} onChange={(e) => setPassword(e.target.value)} />
      <br></br>
      <button type="submit">Login</button><br></br><br></br>
      Don't have an account? <Link to="/register">Register</Link>

    </form>
    </div>
  );
}

export default Login;