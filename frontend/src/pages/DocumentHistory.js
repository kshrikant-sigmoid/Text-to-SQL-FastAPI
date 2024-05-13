import React, { useState, useEffect } from "react";
import axios from "../services/axiosConfig";

const DocumentHistory = () => {
  const [history, setHistory] = useState({});

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/documentHistory/",
          { withCredentials: true }
        );
        setHistory(response.data.history);
      } catch (error) {
        console.error("An error occurred:", error);
      }
    };

    fetchHistory();
  }, []);

  return (
    <div>
      <h2>User History</h2>
      {Object.keys(history).map((key) => (
        <div key={key}>
          <h2 style={{ textAlign: "left" }}>
            Question: {history[key].question}
          </h2>
          <p>Answer: {history[key].answer}</p>
          <p>Filename: {history[key].filename}</p>
        </div>
      ))}
    </div>
  );
};

export default DocumentHistory;
