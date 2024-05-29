import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { Link } from "react-router-dom";
import "react-toastify/dist/ReactToastify.css";
import axios from "../services/axiosConfig";
import { FaDownload } from "react-icons/fa";

const VideoQuery = () => {
  const [question, setQuestion] = useState("");
  const [filenames, setFilenames] = useState([]);
  const [selectedFilename, setSelectedFilename] = useState("");
  const [responseQuestion, setResponseQuestion] = useState("");
  const [responseAnswer, setResponseAnswer] = useState("");
  const [responseFilename, setResponseFilename] = useState("");
  const [transcript, setTranscript] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [history, setHistory] = useState({});

  const handleQuestionClick = (email) => {
    const selectedQuestion = history[email];
    if (selectedQuestion) {
      setResponseQuestion(selectedQuestion.question);
      setResponseAnswer(selectedQuestion.answer);
      setResponseFilename(selectedQuestion.filename);
    }
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/videoHistory/",
          { withCredentials: true }
        );
        setHistory(response.data.history);
      } catch (error) {
        console.error("An error occurred:", error);
      }
    };

    fetchHistory();
  }, []);

  useEffect(() => {
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("token"))
      .split("=")[1];
    if (token) {
      setIsLoggedIn(true);
    }
    const fetchFilenames = async () => {
      try {
        const response = await axios.get("http://localhost:8000/videoNames");

        if (response.data.video_names.length === 0) {
          toast.error("No files available");
        } else {
          setFilenames(response.data.video_names);
        }
      } catch (error) {
        console.error("An error occurred:", error);
      }
    };

    fetchFilenames();
  }, []);

  const onQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  const onFilenameChange = async (event) => {
    setSelectedFilename(event.target.value);
    try {
      const response = await axios.get(
        `http://localhost:8000/videotranscript/${event.target.value}`,
        { withCredentials: true }
      );

      if (response.status === 200) {
        setTranscript(response.data.transcript);
      } else {
        console.error("Failed to fetch transcript");
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  };

  const onQuerySubmit = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/video",
        {
          question: question,
          filename: selectedFilename,
        },
        { withCredentials: true }
      );

      if (response.status === 200) {
        setResponseQuestion(response.data.question);
        setResponseAnswer(response.data.answer);
      } else {
        console.error("Failed to process query");
      }
    } catch (error) {
      console.error("An error occurred:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadTranscript = () => {
    const element = document.createElement("a");
    const file = new Blob([transcript], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = "transcript.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return !isLoggedIn ? (
    <div className="notLoggedInContainer">
      <h2>You are not logged in</h2>
      <p>
        Please <Link to="/">Login</Link> and try again.
      </p>
    </div>
  ) : (
    <div className="container mx-auto p-4 text-center relative">
      <div className="ml-42 -mr-56">
        <div className="p-4 mb-4">
          <h1
            className="font-bold"
            style={{
              textAlign: "center",
              fontSize: "25px",
              marginBottom: "20px",
            }}
          >
            Video Transcript
          </h1>
        </div>
        <div className="border border-gray-300 rounded-md p-4 mb-4">
          <div className="mb-4">
            <div className="flex justify-between items-center">
              <h2
                style={{
                  fontSize: "1.2em",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                Choose from Below Files:
              </h2>

              <div>
                <Link to="/uploadVideo">
                  <button
                    className="bg-pink-400 hover:bg-pink-500 text-white font-bold py-1 px-2 rounded"
                    style={{ backgroundColor: "#DB7093", fontSize: "0.8rem" }}
                  >
                    Upload New Video File
                  </button>
                </Link>
              </div>
            </div>
            <select
              value={selectedFilename}
              onChange={onFilenameChange}
              className="border border-gray-300 rounded-md px-4 py-2 w-full text-center"
            >
              <option value="">Select an Video File</option>
              {filenames.map((filename) => (
                <option key={filename} value={filename}>
                  {filename}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="border border-gray-300 rounded-md p-4 mb-4">
          <div className="mb-8">
            <div className="mb-4 flex justify-between items-center">
              <h2
                style={{
                  fontSize: "1.2em",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                Transcript:
              </h2>
              <button
                onClick={downloadTranscript}
                className="bg-pink-400 hover:bg-pink-500 text-white font-bold py-1 px-2 rounded-full flex items-center justify-center"
                style={{
                  width: "2.5rem",
                  height: "2.5rem",
                  backgroundColor: "#DB7093",
                }}
              >
                <FaDownload />
              </button>
            </div>
            <div
              style={{
                maxHeight: "7em",
                overflowY: "auto",
                whiteSpace: "pre-wrap",
                lineHeight: "1em",
              }}
            >
              {transcript}
            </div>
          </div>
        </div>
        <div className="border border-gray-300 rounded-md p-4 mb-4">
          <div className="mb-8">
            <div className="mb-4">
              <h2
                style={{
                  fontSize: "1.2em",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                Ask Your Question:
              </h2>

              <input
                type="text"
                placeholder="Your Question"
                onChange={onQuestionChange}
                className="border border-gray-300 rounded-md px-4 py-2 w-full text-center"
              />
            </div>

            <button
              onClick={onQuerySubmit}
              className="bg-pink-400 hover:bg-pink-500 text-white font-bold py-2 px-4 rounded"
              style={{ backgroundColor: "#DB7093" }}
            >
              {isLoading ? "Fetching Answer..." : "Submit Query"}
            </button>
          </div>
        </div>
        <div className="border border-gray-300 rounded-md p-4 mb-4">
          <div className="mb-4">
            <h2
              style={{ fontSize: "1.2em", color: "#333", marginBottom: "10px" }}
            >
              Question Asked:
            </h2>

            <p>{responseQuestion}</p>
          </div>
        </div>

        <div className="border border-gray-300 rounded-md p-4 mb-4">
          <div>
            <h2
              style={{ fontSize: "1.2em", color: "#333", marginBottom: "10px" }}
            >
              Answer Generated:
            </h2>

            <p>{responseAnswer}</p>
          </div>
        </div>
        <div>
          <div className="fixed top-0 left-0 h-full bg-gray-800 text-white overflow-auto w-56">
            <div className="sticky top-0 z-10">
              <div className="flex justify-center mt-16">
                <h2 className="text-center border-b-2 border-gray-500 px-24 py-2 z-50 bg-black">
                  History
                </h2>
              </div>
            </div>
            <div className="overflow-auto">
              {Object.keys(history).map((email) => (
                <div
                  key={email}
                  onClick={() => handleQuestionClick(email)}
                  className={`px-4 py-2 hover:bg-gray-600 cursor-pointer text-center border-b-2 border-gray-500 w-56 text-sm overflow-x-auto`}
                >
                  {history[email].question}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoQuery;
