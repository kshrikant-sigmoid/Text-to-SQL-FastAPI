# functions/query.py

from langchain_openai import AzureOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.sql_database import SQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_TYPE = os.getenv('OPENAI_API_TYPE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
OPENAI_DEPLOYMENT_NAME = os.getenv('OPENAI_DEPLOYMENT_NAME')
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME')

# Connect to the SQL database and LangChain LLM
db = SQLDatabase.from_uri("sqlite:///data/Chinook.db")
llm = AzureOpenAI(deployment_name=os.environ.get('OPENAI_DEPLOYMENT_NAME'), model_name=os.environ.get('OPENAI_MODEL_NAME'), temperature=0)

# Create SQL Database toolkit and LangChain Agent Executor
agent_executor = create_sql_query_chain(llm, db)
execute_query = QuerySQLDataBaseTool(db=db, llm=llm)

def get_sql_query(user_input: str) -> str:
    try:
        response = agent_executor.invoke({"question": user_input})
        sql_query = response if isinstance(response, str) else response.get('query')
        query_result = execute_query.invoke({"query": sql_query})
        return {"user_input":user_input,"sql_query": sql_query, "query_result": query_result}
    except Exception as e:
        return {"error": str(e)}