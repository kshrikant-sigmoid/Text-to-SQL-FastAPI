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

load_dotenv()

app = FastAPI()

# Connect to the SQL database and LangChain LLM
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
llm = AzureOpenAI(deployment_name=os.environ.get('OPENAI_DEPLOYMENT_NAME'), model_name=os.environ.get('OPENAI_MODEL_NAME'), temperature=0)

# Create SQL Database toolkit and LangChain Agent Executor
execute_query = QuerySQLDataBaseTool(db=db, llm=llm)
agent_executor = create_sql_query_chain(llm, db)

# Initialize session state variables
query = None
result = None
question = None

# Define endpoints
@app.get("/")
async def homepage():
    return "Welcome to SQL Query with LangChain"

@app.post("/query/")
async def run_query(request: Request):
    global query, result, question
    
    data = await request.json()
    question = data.get('query')

    # Pass user input to LangChain
    query = agent_executor.invoke({"question": question})
    result = execute_query.invoke({"query": query})

    # Convert string representation of list to actual list
    if result and isinstance(result, str):
        result = ast.literal_eval(result)

    return {"question": question, "query": query, "result": result, }

@app.get("/query/")
async def get_query_result():
    global query, result, question
    return {"question": question, "query": query, "result": result, }
