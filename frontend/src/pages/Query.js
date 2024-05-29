import "./Query.css";
import { useState, useEffect } from "react";
import { FaCopy, FaDownload } from "react-icons/fa";
import axios from "../services/axiosConfig";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useNavigate } from "react-router-dom";
import History from "./History";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [query, setQuery] = useState("");
  const [result, setResult] = useState([]);
  const [chartType, setChartType] = useState("pie");
  const [selectedTables, setSelectedTables] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [insights, setInsights] = useState("");
  const [allTables, setAllTables] = useState([]);
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isQuestionSelected, setIsQuestionSelected] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [history, setHistory] = useState([]);

  // console.log(document.cookie);

  const fetchTables = async () => {
    try {
      const response = await axios.get("http://localhost:8000/tables/", {
        withCredentials: true,
      });
      setAllTables(response.data.tables);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/history/`);
      setHistory(response.data.history);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    setIsClient(true);
    fetchTables();
    fetchHistory();
    // console.log(selectedQuestion);
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("token"))
      .split("=")[1];

    if (token) {
      setIsLoggedIn(true);
    }
  }, [selectedQuestion]);

  if (!isLoggedIn) {
    return (
      <div className="notLoggedInContainer">
        <h2>You are not logged in</h2>
        <p>
          Please <Link to="/">Login</Link> and try again.
        </p>
      </div>
    );
  }

  const handleLogout = () => {
    document.cookie = "token=; expired=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    navigate("/");
  };

  const handleQuestionSelect = (question, query, result, insights) => {
    setIsQuestionSelected(true);
    setQuestion(question);
    setQuery(query);
    setResult(result);
    setInsights(insights);
  };

  const copyCode = (code) => {
    if (typeof window !== "undefined") {
      navigator.clipboard.writeText(code);
    }
  };

  const downloadCSV = () => {
    if (typeof window !== "undefined") {
      const csv = result.map((row) => row.join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "result.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:8000/query/",
        {
          question:
            selectedTables.length > 0
              ? `${question} strictly using ${selectedTables.join(
                  ", "
                )} table/s and not other available tables in the database`
              : question,
          selected_tables: selectedTables,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setQuery(response.data.query);
      setResult(response.data.result);
      setInsights(response.data.insights);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuestionClick = (question) => {
    setSelectedQuestion(question);
    setIsQuestionSelected(true);
  };

  // Function to render selected chart based on user's choic
  const renderChart = () => {
    if (!isClient) return null; // Return null if not on client side

    if (Array.isArray(result) && result.length > 0 && result.length <= 2) {
      return <p>Not enough data to generate visualization</p>;
    }

    // Find the first numeric column and the first non-numeric column
    let numericColumnIndex = -1;
    let nonNumericColumnIndex = -1;
    for (let i = 0; i < result.length; i++) {
      if (typeof result[1][i] === "number") {
        numericColumnIndex = i;
        break;
      }
    }
    for (let i = 0; i < result.length; i++) {
      if (typeof result[1][i] !== "number") {
        nonNumericColumnIndex = i;
        break;
      }
    }

    // If either the numeric or non-numeric column is not found, return null
    if (numericColumnIndex === -1 || nonNumericColumnIndex === -1) return null;

    // Import Chart dynamically to ensure it's only imported on the client side
    const Chart = require("react-apexcharts").default;

    // Rest of the function remains the same
    switch (chartType) {
      case "bar":
        return (
          <div style={{ height: "400px" }}>
            <Chart
              type="bar"
              series={[
                { data: result.slice(1).map((row) => row[numericColumnIndex]) },
              ]}
              options={{
                xaxis: {
                  categories: result
                    .slice(1)
                    .map((row) => row[nonNumericColumnIndex]),
                },
              }}
            />
          </div>
        );
      case "line":
        return (
          <div style={{ height: "400px" }}>
            <Chart
              type="line"
              series={[
                {
                  name: "Sales",
                  data: result.slice(1).map((row) => row[numericColumnIndex]),
                },
              ]}
              options={{
                chart: {
                  zoom: {
                    enabled: false,
                  },
                },
                xaxis: {
                  categories: result
                    .slice(1)
                    .map((row) => row[nonNumericColumnIndex]),
                  labels: {
                    rotate: -45,
                    offsetY: 5,
                    offsetX: 0,
                  },
                  tickPlacement: "on",
                },
                yaxis: {
                  labels: {
                    offsetX: 0,
                    offsetY: -5,
                  },
                },
                stroke: {
                  curve: "smooth",
                  colors: ["#000000"], // Black color for the line
                  width: 2, // Width of the line
                },
                markers: {
                  size: 6,
                },
              }}
            />
          </div>
        );
      case "pie":
        return (
          <div style={{ height: "400px" }}>
            <Chart
              type="pie"
              series={result.slice(1).map((row) => row[numericColumnIndex])}
              options={{
                labels: result
                  .slice(1)
                  .map((row) => row[nonNumericColumnIndex]),
              }}
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      {/* <div className="dropdown">
        <button className="dropbtn" onClick={() => setDropdownVisible(!dropdownVisible)}>
            {dropdownVisible ? <MdClose /> : <MdMoreVert />}
        </button>
        {dropdownVisible && (
        <div className={`dropdown-content ${dropdownVisible ? 'show' : ''}`}>
            <Link to="/history">History</Link>
            <Link to="/" onClick={handleLogout}>Logout</Link>
        </div>
        )}
    </div> */}
      {isQuestionSelected ? (
        <div className="history-container">
          <History selectedQuestion={selectedQuestion} />
        </div>
      ) : (
        <div className="container">
          <div className="ml-42 -mr-56">
            <div className="fixed top-0 left-0 h-screen bg-gray-800 text-white overflow-auto">
              <div className="sticky top-0 z-10 flex justify-center mt-16">
                <div className="text-center border-b-2 border-gray-500 px-20 py-2 z-50 bg-black">
                  History
                </div>
              </div>
              <ul className="overflow-auto">
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

            <h1
              style={{
                textAlign: "center",
                fontSize: "2em",
                marginBottom: "20px",
              }}
            >
              SQL Insight Engine
            </h1>
            <form onSubmit={handleSubmit}>
              <label>
                <h2
                  style={{
                    fontSize: "1.5em",
                    color: "#333",
                    marginTop: "20px",
                    marginBottom: "10px",
                  }}
                >
                  Enter your Question:
                </h2>
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="w-full h-18 text-lg"
                />
              </label>

              <div className="query-result" style={{ textAlign: "left" }}>
                <h2
                  style={{
                    fontSize: "1.5em",
                    color: "#333",
                    marginBottom: "10px",
                  }}
                >
                  Select Tables (OPTIONAL):
                </h2>
                <div className="grid grid-cols-3">
                  {allTables.map((table) => (
                    <div key={table} className="pl-24">
                      <input
                        type="checkbox"
                        id={table}
                        checked={selectedTables.includes(table)}
                        onChange={() => {
                          if (selectedTables.includes(table)) {
                            setSelectedTables(
                              selectedTables.filter((t) => t !== table)
                            );
                          } else {
                            setSelectedTables([...selectedTables, table]);
                          }
                        }}
                      />
                      <label htmlFor={table}>&nbsp;{table}</label>
                    </div>
                  ))}
                </div>
              </div>

              <br></br>
              <button
                type="submit"
                className="submit-btn btn-small"
                disabled={isLoading}
              >
                {isLoading ? "Processing..." : "Submit"}
              </button>
            </form>

            <div className="query-result">
              <h2
                style={{
                  fontSize: "1.5em",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                Question:
              </h2>
              <p>{question}</p>
            </div>

            <div className="query-result">
              <h2
                style={{
                  fontSize: "1.5em",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                Selected Tables:
              </h2>
              <p>{selectedTables.join(", ")}</p>
            </div>

            <div className="query-result">
              <h2
                style={{
                  fontSize: "1.5em",
                  color: "#333",
                  marginBottom: "10px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                SQL Query
                <button className="icon-btn" onClick={() => copyCode(query)}>
                  <FaCopy />
                </button>
              </h2>
              <p>{query}</p>
            </div>

            <div className="query-result">
              <h2
                style={{
                  fontSize: "1.5em",
                  color: "#333",
                  marginBottom: "10px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                Result
                <button
                  className="btn btn-download text-sm px-2 py-1"
                  onClick={downloadCSV}
                >
                  <FaDownload /> Download CSV
                </button>
              </h2>
              <table className="result-table">
                <thead>
                  <tr>
                    {Array.isArray(result) &&
                      result.length > 0 &&
                      result[0].map((columnName, index) => (
                        <th key={index}>{columnName}</th>
                      ))}
                  </tr>
                </thead>

                <tbody>
                  {Array.isArray(result) &&
                    result.slice(1).map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            <div className="query-result">
              <h2
                style={{
                  fontSize: "1.5em",
                  color: "#333",
                  marginBottom: "10px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                Insights
                <button className="icon-btn" onClick={() => copyCode(insights)}>
                  <FaCopy />
                </button>
              </h2>
              <div className="prose">
                <ul className="list-disc ml-6">
                  {insights
                    .split(/(?<=\.|\?|\!|\-)\s/)
                    .map((sentence, index) => {
                      if (sentence.trim().length >= 5) {
                        return <li key={index}>{sentence}</li>;
                      } else {
                        return null;
                      }
                    })}
                </ul>
              </div>
            </div>

            <div className="query-result">
              <h2
                style={{
                  fontSize: "1.5em",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                Choose Chart Type:
              </h2>
              <div>
                <div>
                  <input
                    type="radio"
                    id="bar"
                    name="chartType"
                    value="bar"
                    checked={chartType === "bar"}
                    onChange={() => setChartType("bar")}
                  />
                  <label htmlFor="bar"> Bar Chart</label>
                </div>

                <div>
                  <input
                    type="radio"
                    id="line"
                    name="chartType"
                    value="line"
                    checked={chartType === "line"}
                    onChange={() => setChartType("line")}
                  />
                  <label htmlFor="line"> Line Chart</label>
                </div>

                <div>
                  <input
                    type="radio"
                    id="pie"
                    name="chartType"
                    value="pie"
                    checked={chartType === "pie"}
                    onChange={() => setChartType("pie")}
                  />
                  <label htmlFor="pie"> Pie Chart</label>
                </div>
              </div>

              {/* Chart Visualization */}

              <div
                className="chart-container"
                style={{ width: "600px", margin: "0 auto" }}
              >
                {renderChart()}
              </div>
              <br></br>
              <br></br>
              <br></br>
              <br></br>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
