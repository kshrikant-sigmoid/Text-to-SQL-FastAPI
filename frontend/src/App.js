import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './pages/Register.js';
import Login from './pages/Login.js';
import Query from './pages/Query.js';
import History from './pages/History.js';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Login />} />
        <Route path="/query" element={<Query />} />
        <Route path="/history" element={<History />}/>
      </Routes>
    </Router>
  );
}

export default App;