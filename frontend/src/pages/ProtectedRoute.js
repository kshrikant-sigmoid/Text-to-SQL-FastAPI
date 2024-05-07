// ProtectedRoute.js
import { useNavigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const navigate = useNavigate();
  const token = sessionStorage.getItem('token');

  if (!token) {
    navigate('/login');
    return null;
  }

  return children;
}

export default ProtectedRoute;