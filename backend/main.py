# Replace the run_query endpoint in your main.py file

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
import ast
import pandas as pd
from langchain_openai import AzureOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",  # React's default port
    # add any other origins that need to access the API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to the SQL database and LangChain LLM
db = SQLDatabase.from_uri("sqlite:///data/Chinook.db")
llm = AzureOpenAI(deployment_name=os.environ.get('OPENAI_DEPLOYMENT_NAME'), model_name=os.environ.get('OPENAI_MODEL_NAME'), temperature=0)

# Create SQL Database toolkit and LangChain Agent Executor
execute_query = QuerySQLDataBaseTool(db=db, llm=llm)
agent_executor = create_sql_query_chain(llm, db)

# Define endpoints
@app.get("/")
async def homepage():
    return "Welcome to SQL Query with LangChain"

@app.post("/query/")
async def run_query(request: Request):
    data = await request.json()
    question = data.get('query')

    # Pass user input to LangChain
    query = agent_executor.invoke({"question": question})

    # Execute the SQL query
    result = execute_query.invoke({"query": query})

    insights = llm.invoke(f"Analyze the following data and provide insights related to sales trends and projections. Do not generate content related to programming concepts or other irrelevant topics. The question asked was: {question}. The data fetched after executing the query is: {result}")
    insights = insights.replace("<|im_end|>","")
    # Convert string representation of list to actual list

    if result and isinstance(result, str):
        result = ast.literal_eval(result)

    return {"question": question, "query": query, "result": result, "insights" :  insights}