import React, { useState, useEffect } from "react";
import axios from "../services/axiosConfig";
import "./History.css";
import { Link } from "react-router-dom";

export default function History({
  username,
  selectedQuestion: initialSelectQuestion,
}) {
  const [history, setHistory] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(
    initialSelectQuestion
  );
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // console.log(selectedQuestion);

  useEffect(() => {
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("token"))
      .split("=")[1];
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

  const handleQuestionClick = (question) => {
    setSelectedQuestion(question);
  };

  return !isLoggedIn ? (
    <div className="notLoggedInContainer">
      <h2>You are not logged in</h2>
      <p>
        Please <Link to="/">Login</Link> and try again.
      </p>
    </div>
  ) : (
    <div>
      <div className="fixed top-0 left-0 h-screen bg-gray-800 text-white overflow-auto">
        <div className="flex justify-center mt-16">
          <div className="text-center border-b-2 border-gray-500 px-10 py-2">
            History
          </div>
        </div>
        <ul className="pt-4">
          {Object.values(history).map((item, index) => (
            <li
              key={index}
              onClick={() => handleQuestionClick(item)}
              className="px-4 py-2 hover:bg-gray-600 cursor-pointer text-center border-b-2 border-gray-500 px-10 w-56 text-sm overflow-x-auto"
            >
              {item.question}
            </li>
          ))}
        </ul>
      </div>
      {selectedQuestion && (
        <div className="flex flex-wrap justify-around mt-10 ml-10">
          <div className="history-card bg-white shadow-lg rounded-lg m-4 p-4 bg-gray-600 text-white">
            <h3 className="font-bold text-xl mb-2">Question</h3>
            <p>{selectedQuestion.question}</p>
          </div>
          <div className="history-card bg-white shadow-lg rounded-lg m-4 p-4 bg-gray-600 text-white">
            <h3 className="font-bold text-xl mb-2">Query</h3>
            <p>{selectedQuestion.query}</p>
          </div>
          <div className="history-card bg-white shadow-lg rounded-lg m-4 p-4 bg-gray-600 text-white">
            <h3 className="font-bold text-xl mb-2">Result</h3>
            <p>{selectedQuestion.result}</p>
          </div>
          <div className="history-card bg-white shadow-lg rounded-lg m-4 p-4 bg-gray-600 text-white">
            <h3 className="font-bold text-xl mb-2">Insights</h3>
            <p>{selectedQuestion.insights}</p>
          </div>
        </div>
      )}
    </div>
  );
}
