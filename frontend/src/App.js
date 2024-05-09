import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Register from './pages/Register.js';
import Login from './pages/Login.js';
import Query from './pages/Query.js';
import History from './pages/History.js';
import DocumentQuery from './pages/Document.js';
import FileUpload from './pages/Upload.js';

function App() {
  return (
    <Router>
      <ToastContainer/>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Login />} />
        <Route path="/query" element={<Query />} />
        <Route path="/history" element={<History />}/>
        <Route path="/fileupload" element={<FileUpload />}/>
        <Route path='/document' element={<DocumentQuery/>}/>
      </Routes>
    </Router>
  );
}

export default App;