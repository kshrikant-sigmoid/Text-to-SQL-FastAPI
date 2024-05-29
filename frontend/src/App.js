import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Register from "./pages/Register.js";
import Login from "./pages/Login.js";
import Query from "./pages/Query.js";
import History from "./pages/History.js";
import DocumentQuery from "./pages/Document.js";
import FileUpload from "./pages/Upload.js";
import DocumentHistory from "./pages/DocumentHistory.js";
import AudioFileUpload from "./pages/AudioUpload.js";
import AudioQuery from "./pages/Audio.js";
import VideoFileUpload from "./pages/VideoUpload.js";
import VideoQuery from "./pages/Video.js";
import { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [showHistory, setShowHistory] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    if (loggedIn) {
      fetchUsername();
    }
  }, [loggedIn]);

  useEffect(() => {
    const isLoggedIn = () => {
      const token = document.cookie
        .split(";")
        .find((cookie) => cookie.trim().startsWith("token="));
      return token ? true : false;
    };

    setLoggedIn(isLoggedIn());
  }, []);

  const fetchUsername = async () => {
    try {
      const token = document.cookie
        .split("; ")
        .find((row) => row.startsWith("token="))
        .split("=")[1];
      const response = await axios.get("http://localhost:8000/get-user", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUsername(response.data.username);
    } catch (error) {
      toast.error(error);
    }
  };

  const handleLogin = () => {
    setLoggedIn(true);
  };

  const handleLogout = () => {
    // Clear the token from the cookie
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    setLoggedIn(false);
    window.location.href = "/"; // Redirect to home page
  };

  return (
    <Router>
      <ToastContainer />
      <div className="bg-gray-800">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center ml-48 h-16">
          <ul className="flex">
            {loggedIn && (
              <li>
                <Link to="/query">
                  <button
                    onClick={() => {
                      setShowHistory(!showHistory);
                    }}
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-6 py-2 rounded-md text-sm font-medium"
                  >
                    SQL Insight Engine
                  </button>
                </Link>
              </li>
            )}
            {loggedIn && (
              <li>
                <Link to="/document">
                  <button
                    onClick={() => {
                      setShowHistory(false);
                    }}
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-2 py-2 rounded-md text-sm font-medium"
                  >
                    Document
                  </button>
                </Link>
              </li>
            )}
            {loggedIn && (
              <li>
                <Link to="/audio">
                  <button
                    onClick={() => {
                      setShowHistory(false);
                    }}
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-2 py-2 rounded-md text-sm font-medium"
                  >
                    Audio
                  </button>
                </Link>
              </li>
            )}
            {loggedIn && (
              <li>
                <Link to="/video">
                  <button
                    onClick={() => {
                      setShowHistory(false);
                    }}
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-2 py-2 rounded-md text-sm font-medium"
                  >
                    Video
                  </button>
                </Link>
              </li>
            )}
          </ul>
          {loggedIn ? (
            <>
              <p className="text-gray-300 text-sm font-medium mr-28">{`Welcome ${username}`}</p>
              <button
                onClick={handleLogout}
                className="text-gray-300 hover:bg-gray-700 hover:text-white py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </>
          ) : (
            <a
              href="http://localhost:3000"
              className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
            >
              Login
            </a>
          )}
        </nav>
      </div>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Login />} />
        <Route path="/query" element={<Query />} />
        <Route path="/history" element={<History />} />
        <Route path="/fileupload" element={<FileUpload />} />
        <Route path="/document" element={<DocumentQuery />} />
        <Route path="/documenthistory" element={<DocumentHistory />} />
        <Route path="/uploadAudio" element={<AudioFileUpload />} />
        <Route path="/audio" element={<AudioQuery />} />
        <Route path="/uploadVideo" element={<VideoFileUpload />} />
        <Route path="/video" element={<VideoQuery />} />
      </Routes>
    </Router>
  );
}
