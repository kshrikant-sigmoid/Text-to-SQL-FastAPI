import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
import pandas as pd
import ast
import sqlite3
from dotenv import load_dotenv
import plotly.express as px

load_dotenv()

# Create a database instance
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

# Create a query execution tool
execute_query = QuerySQLDataBaseTool(db=db)

llm = ChatOpenAI(model="gpt-4", temperature=0)
chain = create_sql_query_chain(llm, db)
insight_chain = ChatOpenAI(model="gpt-4")

# Sidebar layout
st.sidebar.title('Data Explorer')
st.sidebar.header('User Input')
question = st.sidebar.text_area("Enter your question")

# List all tables in the database
st.sidebar.subheader("Tables in Database")
tables = db.get_table_names()
selected_tables = [st.sidebar.checkbox(table) for table in tables]

# Add selected tables to the question
selected_tables_str = ", ".join([f"`{table}`" for table in tables if selected_tables[tables.index(table)]])
question += f"only from the {selected_tables_str} otherwise give a proper reason without retreving data"

# Initialize generated_query and insights_calculated variables
generated_query = None
insights_calculated = False

# Run query button
if st.sidebar.button('Run query') and question.strip():
    with st.spinner('Running query...'):
        try:
            # Create a SQL query chain
            write_query = create_sql_query_chain(llm, db)
            # Get the generated query without limit
            generated_query = write_query.invoke({"question": question})

            # Remove one LIMIT clause if there are multiple
            limit_keywords = ["limit", "top", "last", "highest", "lowest" , "max" , "min", "maximum" , "minimum"]
            if not any(keyword in question.lower() for keyword in limit_keywords):
                if "LIMIT" in generated_query:
                    generated_query = generated_query.split("LIMIT")[0] + ";"

            # Execute the generated query directly
            result = execute_query.invoke({"query": generated_query})

            # Check if result is not None and is a string
            if result and isinstance(result, str):
                # Convert the string back to list tuples
                result = ast.literal_eval(result)

                # Convert the result to a pandas DataFrame and display it as a table
                df = pd.DataFrame(result)
                df.index = df.index + 1

                st.session_state.df = df
                st.session_state.result = result

        except sqlite3.ProgrammingError as e:
            st.error("Error: {}. You can only execute one statement at a time.".format(e))

# Main content area
st.title('SQL Data Explorer')

if 'df' in st.session_state:
    # Display the question asked by the user
    st.header("Question Asked")
    st.write(question)

    # Display the generated SQL query
    if generated_query:
        st.header("Generated SQL Query")
        st.write(generated_query)

    # Display the query result
    st.header("Query Result")
    st.dataframe(st.session_state.df)

    # Visualization options
    st.header("Visualization")
    if len(st.session_state.df.columns) <= 1:
        st.warning("Chart is not available for this query. The result of query contains only one column.")
    else:
        if st.session_state.df.select_dtypes(include='number').empty:
            st.warning("Chart is not available for this query. The result of query does not contain numeric data.")
        else:
            visualization = st.radio("Choose type of visualization:", ('Pie Chart', 'Bar Chart', 'Line Graph'))
            if visualization == 'Line Graph':
                st.line_chart(st.session_state.df)
            elif visualization == 'Bar Chart':
                st.bar_chart(st.session_state.df)
            elif visualization == 'Pie Chart':
                if 'df' in st.session_state:
                    # Convert DataFrame to Plotly-compatible data
                    fig = px.pie(st.session_state.df, values=st.session_state.df.columns[1], names=st.session_state.df[st.session_state.df.columns[0]], title='Pie Chart')
                    st.plotly_chart(fig)
                else:
                    st.warning("No DataFrame available for pie chart.")
            
    # Insights section (calculated only once)
    if not insights_calculated and 'result' in st.session_state:
        st.header("Insights")
        insights_response = insight_chain.invoke("You are a good insights generator. Given the data below, generate relevant insights" + str(st.session_state.result)).content
        st.write(insights_response)
        insights_calculated = True
else:
    st.info("No result returned from the query or empty input.")
