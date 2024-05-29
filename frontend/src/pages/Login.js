import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";

function Login() {
  const [jwtToken, setJwtToken] = useState("");
  const navigate = useNavigate();

  const handleGoogleSubmit = async (event) => {
    if (event) event.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/googlelogin/", {
        jwtToken,
      });
      if (response.data.token) {
        // Set the token as a cookie
        document.cookie = `token=${response.data.token}; max-age=1800`; // expires after 30 minutes
        navigate("/query", { state: { message: response.data.message } });
        window.location.reload();
      }
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error("An error occurred while logging in.");
      }
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-300 bg-opacity-50">
      <div className="p-6 max-w-sm mx-auto bg-white rounded-xl shadow-md flex flex-col items-center space-y-4">
        <h1>Login Using Google</h1>
        <GoogleLogin
          onSuccess={(credentialResponse) => {
            setJwtToken(credentialResponse.credential);
            handleGoogleSubmit();
          }}
          onError={() => {
            toast.err("Login Failed");
          }}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded"
        />
      </div>
    </div>
  );
}

export default Login;
