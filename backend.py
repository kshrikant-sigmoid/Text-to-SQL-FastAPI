from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import ast
import pandas as pd
import re

from langchain_openai import AzureOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI()

class QueryManager:
    def __init__(self):
        # Initialize SQLDatabase and AzureOpenAI
        self.db = SQLDatabase.from_uri("sqlite:///Chinook.db")
        self.llm = AzureOpenAI(
            deployment_name=os.environ.get('OPENAI_DEPLOYMENT_NAME'),
            model_name=os.environ.get('OPENAI_MODEL_NAME'),
            temperature=0
        )

        # Create LangChain processing chain
        self.chain = self.llm | StrOutputParser()

        # Create SQL query execution chain
        self.agent_executor = create_sql_query_chain(self.llm, self.db)
        self.execute_query = QuerySQLDataBaseTool(db=self.db, llm=self.llm)

        # Initialize attributes
        self.query = None
        self.result = None
        self.question = None
        self.insights = None
        self.columns = None

    def get_columns(self, query, result):
        # Generate prompt to extract column names
        prompt = f"Given this SQL query: {query} Give me only names of columns in exact order (in format ColumnName-TableName) as a python list, without any explanation."
        text = self.chain.invoke(prompt)

        # Extract column names from the LangChain response
        first_occurrence_match = re.search(r'\[(.*?)\]', text)
        first_occurrence = first_occurrence_match.group(0) if first_occurrence_match else None
        return eval(first_occurrence)

    def get_insights(self, query, result):
        # Generate prompt to get insights from query result
        prompt = f"As a proficient insights generator, analyze the following SQL query's output: {query}. Generate insightful observations in bullet points based on the provided data: {str(result)}. Avoid delving into the specifics of the query; focus solely on interpreting the data. Give nothing but bullet points thats it."
        return self.chain.invoke(prompt)

query_manager = QueryManager()

# Define endpoints
@app.get("/")
async def homepage():
    return "Welcome to SQL Query with LangChain"

@app.post("/query/")
async def run_query(request: Request):
    data = await request.json()
    question = data.get('query')

    # Pass user input to LangChain to get SQL query
    query = query_manager.agent_executor.invoke({"question": question})

    # Execute SQL query
    result = query_manager.execute_query.invoke({"query": query})

    # Get insights and column names
    insights = query_manager.get_insights(result=result, query=query)
    columns = query_manager.get_columns(result=result, query=query)

    # Convert string representation of list to actual list
    if result and isinstance(result, str):
        result = ast.literal_eval(result)

    # Update query manager state
    query_manager.query = query
    query_manager.result = result
    query_manager.question = question
    query_manager.insights = insights
    query_manager.columns = columns

    return {"question": question, "query": query, "result": [columns] + result, "insights": insights}

@app.get("/query/")
async def get_query_result():
    return {"question": query_manager.question, "query": query_manager.query, "result": query_manager.result, "insights": query_manager.insights}
