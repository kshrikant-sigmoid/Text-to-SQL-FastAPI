from fastapi import FastAPI, Request, HTTPException, UploadFile,File
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import AzureOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain.sql_database import SQLDatabase
from langchain.cache import SQLiteCache
from langchain import hub
from langchain_openai import AzureChatOpenAI
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.vectorstores.azuresearch import AzureSearch
from langchain.globals import set_llm_cache
import os
import ast
from dotenv import load_dotenv
from typing import List
import sqlite3
from sqlite3 import Error as SQLiteError
import secrets
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import redis
from pymongo import MongoClient

load_dotenv()

app = FastAPI()

class DocumentRequest(BaseModel):
    question: str
    index_name: str

class User(BaseModel):
    username: str
    password: str  

origins = [
    "http://localhost:3000",
    "*"  # React's default port
    # add any other origins that need to access the API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
app.add_middleware(SessionMiddleware, secret_key = SECRET_KEY, max_age = 3600)

client = MongoClient("mongodb://localhost:27017/")
db = client["user_db"]
user = db["users"]
sql_history = db["sql_history"]
documents = db["documents"]
documents_history = db["documents_history"]

# def get_db():
#     conn = sqlite3.connect('user_database.db')  # Replace 'database.db' with the path to your database file
#     return conn

# user_db = get_db()
# cursor = user_db.cursor()
# cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
# cursor.execute("CREATE TABLE IF NOT EXISTS history (histroy_id INTEGER PRIMARY KEY AUTOINCREMENT, id INTEGER, question TEXT, query TEXT, result TEXT, insights TEXT, FOREIGN KEY(id) REFERENCES users(id))")
# cursor.execute("CREATE TABLE IF NOT EXISTS documents (index_id INTEGER PRIMARY KEY AUTOINCREMENT,id INTEGER, index_name TEXT, filename TEXT, FOREIGN KEY(id) REFERENCES users(id))")
# cursor.execute("CREATE TABLE IF NOT EXISTS documents_history (history_id INTEGER PRIMARY KEY AUTOINCREMENT, id INTEGER, question TEXT, answer TEXT, index_name TEXT, FOREIGN KEY(id) REFERENCES users(id), FOREIGN KEY(index_name) REFERENCES documents(index_name))")

# Connect to the SQL database and LangChain LLM
cache = SQLiteCache(database_path=".langchain.db")
set_llm_cache(cache)

# client = redis.Redis.from_url('redis://localhost:6379/0')

from langchain.cache import RedisSemanticCache


db = SQLDatabase.from_uri("sqlite:///data/Chinook.db")
llm = AzureOpenAI(deployment_name=os.environ.get('OPENAI_DEPLOYMENT_NAME'), model_name=os.environ.get('OPENAI_DEPLOYMENT_NAME'), temperature=0)

# Create SQL Database toolkit and LangChain Agent Executor
execute_query = QuerySQLDataBaseTool(db=db, llm=llm)
agent_executor = create_sql_query_chain(llm, db)
        
vector_store_address: str = os.environ['VECTOR_STORE_ADDRESS']
vector_store_password: str = os.environ['VECTOR_STORE_PASSWORD']

aoai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment= os.environ['AZURE_EMBEDDING_DEPLOYMENT_NAME'],
    openai_api_version= os.environ['OPENAI_API_VERSION'],
    api_key = os.environ['AZURE_OPENAI_API_KEY'],
    azure_endpoint = os.environ['AZURE_OPENAI_ENDPOINT'], 
)  


# redis_url = "redis://:seVATUzIxp83rc3WBoYCuY70wo2TPFbz@redis-18212.c282.east-us-mz.azure.redns.redis-cloud.com:18212"


# set_llm_cache(RedisSemanticCache(
#     embedding=AzureOpenAIEmbeddings(
#     azure_deployment= os.environ['AZURE_EMBEDDING_DEPLOYMENT_NAME'],
#     openai_api_version= os.environ['OPENAI_API_VERSION'],
#     api_key = os.environ['AZURE_OPENAI_API_KEY'],
#     azure_endpoint = os.environ['AZURE_OPENAI_ENDPOINT'],),
#     redis_url=redis_url,
# ))

def get_index(name):
    client = SearchIndexClient(os.environ['VECTOR_STORE_ADDRESS'], AzureKeyCredential(os.environ['VECTOR_STORE_PASSWORD']))
    result = client.get_index(name)
    return result

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# # New user registration
# @app.post("/register/")
# async def register_user(user: User):
#     try:
#         cursor.execute(f"INSERT INTO users (username, password) VALUES  (?,?)" ,(user.username, user.password))
#         user_db.commit()
#     except SQLiteError as e:
#         raise HTTPException(status_code=400, detail=str(e))    
#     return {"message": "User registered successfully"}


@app.post("/googlelogin/")
async def google_login(request: Request):
    try:
        data = await request.json()
        jwtToken = data.get('jwtToken')
        
        token = jwt.decode(jwtToken, algorithms=["RS256"], options={"verify_signature":False})
        id = token.get('email')
        username = token.get('given_name')
        try:
            user_in_db = user.find_one({"id": id, "username": username})
            if user_in_db:
                id = str(user_in_db["id"])
            else:
                new_user = {"id": id, "username": username}
                inserted_user = user.insert_one(new_user)
                id = str(inserted_user.inserted_id)
            expire = datetime.utcnow() + timedelta(minutes=15)
            token_data = {"id": id, "username": username, "exp": expire}
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            request.session["user_id"] = id
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 
        return {"message": "Login successful", "token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Something failed, try again")


# # Login
# @app.post("/login/")
# async def login_user(user: User, request: Request):
#     try:
#         cursor.execute(f"SELECT * FROM users WHERE username='{user.username}' AND password='{user.password}'")
#         user_in_db = cursor.fetchone()
#     except SQLiteError as e:
#         raise HTTPException(status_code=400, detail=str(e))    
#     if user_in_db:
#         user_id = user_in_db[0]
#         expire = datetime.utcnow() + timedelta(minutes=15)
#         token_data = {"id": user_id, "username": user.username, "exp": expire}
#         token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
#         request.session["user_id"] = user_id
#         return {"message": "Login successful", "token": token}
#     else:
#         raise HTTPException(status_code=400, detail="Invalid username or password")
    
# Define endpoints
@app.get("/")
async def homepage():
    return "Welcome to SQL Query with LangChain"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id
 
# Define a new endpoint to handle table selection
@app.get("/tables/")
async def get_tables(user_id: int = Depends(get_current_user)):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tables = db.get_usable_table_names()
    return {"tables": tables}
 
# Define the endpoint to handle queries
@app.post("/query/")
async def run_query(request: Request, user_id: int = Depends(get_current_user)):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        data = await request.json()
        question = data.get('question')
        selected_tables = data.get('selected_tables', [])  # Get selected tables from request data

        # Add selected tables to the question prompt
        if selected_tables:
            selected_tables_str = ", ".join([f"`{table}`" for table in selected_tables])
            question += f" strictly using {selected_tables_str} tables"

        # Pass user input to LangChain
        query = agent_executor.invoke({"question": question})

        # Execute the SQL query
        result = execute_query.invoke({"query": query})

        insights = llm.invoke(f"Analyze the following data and provide insights related to sales trends and projections. Do not generate content related to programming concepts or other irrelevant topics. The question asked was: {question}. The data fetched after executing the query is: {result}")
        column_name = llm.invoke(f"Given this SQL query: {query}, and result as {result}.  Provide only the names of columns (in format ColumnName) as a Python list.have the column names in the same sequesnce as the result is being displayed , the result is a list of tuple , check for the first tuple about how much data is there , the no of column should not increase that count . Your response should only contain column names and nothing else, in the format ['column1', 'column2', 'column3', ...], without any additional explanations or prompts.")
        start_index = column_name.find('[')
        end_index = column_name.find(']')

        # Extract the content within the square brackets
        extracted_content = column_name[start_index:end_index+1]  

        # Convert string representation of list to actual list
        if result and isinstance(result, str):
            result = ast.literal_eval(result)

        extracted_content_list = eval(extracted_content)
        combined_result = [tuple(extracted_content_list)] + result

        # Round up numeric values to two decimal places
        for i in range(len(combined_result)):
            if isinstance(combined_result[i], tuple):
                combined_result[i] = tuple(round(val, 2) if isinstance(val, float) else val for val in combined_result[i])      

        combined_result_str = str(combined_result)
        sql_history.insert_one({"id": user_id, "question": question, "query": query, "result": combined_result_str, "insights": insights})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))                    
    
    return {"question": question, "query": query, "result":  combined_result, "insights": insights}

# History of user
@app.get("/history/")
async def get_history(user_id: int = Depends(get_current_user)):
    try:
        history_records = sql_history.find({"id": user_id})
        history = {str(record["_id"]): dict(id=record["id"], question=record["question"], query=record["query"], result=record["result"], insights=record["insights"]) for record in history_records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

    return {"history": history}


# Document endpoint
@app.post("/upload/")
async def upload(user_id: int = Depends(get_current_user), file: UploadFile = File(...)):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        contents = await file.read()

        file_path = os.path.abspath(file.filename)

        with open(file_path, 'wb') as f:
            f.write(contents)

        # Initiate Azure AI Document Intelligence to load the document. You can either specify file_path or url_path to load the document.
        loader = AzureAIDocumentIntelligenceLoader(file_path=file_path, api_key = os.environ['AZURE_DOCUMENT_INTELLIGENCE_KEY'], api_endpoint = os.environ['AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'], api_model="prebuilt-layout")
        docs = loader.load()

        # Split the document into chunks base on markdown headers.
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        docs_string = docs[0].page_content
        splits = text_splitter.split_text(docs_string)

        # Embed the splitted documents and insert into Azure Search vector store
        index_name = file.filename.lower().replace('.', '-').replace('-pdf','').replace(' ','')

        try:
            get_index(index_name)
        except Exception:
            index_name: str = index_name
            vector_store: AzureSearch = AzureSearch(
                azure_search_endpoint=vector_store_address,
                azure_search_key=vector_store_password,
                index_name=index_name,
                embedding_function=aoai_embeddings.embed_query,
            )    
            vector_store.add_documents(documents=splits)

        index_result = documents.find_one({"index_name": index_name, "id": user_id})

        if index_result is None:
            documents.insert_one({"id": user_id, "index_name": index_name, "filename": file.filename.replace('.pdf','')})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return{"message":"File process successfully"}

@app.get("/index_names/")
async def index_names(user_id: int = Depends(get_current_user)):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        index_names_cursor = documents.find({"id": user_id}, {"index_name": 1, "_id": 0})
        index_names = [doc["index_name"] for doc in index_names_cursor]

        return {"index_names": index_names}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/document/")
async def document_rag(request: DocumentRequest, user_id: int = Depends(get_current_user)):
    if user_id is None:    
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        index_name: str = request.index_name
        vector_store: AzureSearch = AzureSearch(
            azure_search_endpoint=vector_store_address,
            azure_search_key=vector_store_password,
            index_name=index_name,
            embedding_function=aoai_embeddings.embed_query,
        )
        
        # Retrieve relevant chunks based on the question

        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
        prompt = hub.pull("rlm/rag-prompt")
        doc_llm = AzureChatOpenAI(
            openai_api_version= os.environ['OPENAI_API_VERSION'],
            azure_deployment= os.environ['OPENAI_DEPLOYMENT_NAME'],
            temperature=0,
        )

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | doc_llm
            | StrOutputParser()
        )

        answer = rag_chain.invoke(request.question)

        documents_history.insert_one({"id": user_id, "question": request.question, "answer": answer, "index_name": request.index_name})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return{"question": request.question, "answer": answer}


# History of user
@app.get("/documentHistory/")
async def get_history(user_id: int = Depends(get_current_user)):
    try:
        history_records_cursor = documents_history.find({"id": user_id})
        history = {str(record["_id"]): dict(id=record["id"], question=record["question"], answer=record["answer"], filename=record["index_name"]) for record in history_records_cursor}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e)) 
    return {"history": history}

@app.get("/get-user")
async def read_current_user(current_user_id: User = Depends(get_current_user)):
    current_user = user.find_one({"id": current_user_id}, {"username": 1, "_id": 0})
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": current_user["username"]}