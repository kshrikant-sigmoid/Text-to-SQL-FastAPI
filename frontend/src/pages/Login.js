import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios" ;

function Login() {
  const navigate = useNavigate();
  const [token, setToken] = useState(null);

  const handleGoogleSubmit = () => {
    // Redirect the user to your /login endpoint
    window.location.href = "http://localhost:8000/login/";
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-300 bg-opacity-50">
      <div className="p-6 max-w-sm mx-auto bg-white rounded-xl shadow-md flex flex-col items-center space-y-4">
        <h1>Login Using Google</h1>
        <button
          onClick={handleGoogleSubmit}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded"
        >
          Login with Google
        </button>
      </div>
    </div>
  );
}

export default Login;
