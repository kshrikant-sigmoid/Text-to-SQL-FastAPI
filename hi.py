import streamlit as st
import pandas as pd
import ast
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_openai import AzureOpenAI
import os

load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint="https://llmops.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

# Create a database instance
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
# Create a query execution tool
execute_query = QuerySQLDataBaseTool(db=db)

llm = create_sql_query_chain(client, db)
insight_chain = AzureOpenAI(model="gpt-35-turbo")

# Define Streamlit page layout
st.set_page_config(
    page_title="SQL Insights Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# Sidebar for user input
with st.sidebar:
    st.title('User Input')
    question = st.text_input("Enter your question") 

    # List all tables in the database
    st.subheader("Tables in Database")
    tables = db.get_table_names()
    selected_tables = [table for table in tables if st.checkbox(table)]

    # Add selected tables to the question
    if selected_tables:
        selected_tables_str = ", ".join([f"`{table}`" for table in selected_tables])
        question += f" strictly using only the {selected_tables_str} table/s and not other available tables in the database"

result = None
generated_query = None

# When the user presses the 'Run query' button and the input is not empty
if st.sidebar.button('Run query') and question.strip():
    try:
        # Get the generated query without limit
        generated_query = llm.invoke({"question": question})

        # Remove one LIMIT clause if there are multiple
        # Check if any of the words are present in the question
        limit_keywords = ["limit", "top", "last", "highest", "lowest", "max", "min", "maximum", "minimum"]
        if not any(keyword in question.lower() for keyword in limit_keywords):
            if "LIMIT" in generated_query:
                generated_query = generated_query.split("LIMIT")[0] + ";"

        # Attempt to execute the query
        result = execute_query.invoke({"query": generated_query})
        if result:
            # Process the query result if it's not empty
            # Convert the string back to list tuples
            result = ast.literal_eval(result)

            # Convert the result to a pandas DataFrame and display it as a table
            df = pd.DataFrame(result)
            df.index = df.index + 1

            # Store the DataFrame in the session state
            st.session_state.df = df
            st.session_state.result = result
        else:
            st.warning("No results returned from the query.")
    except Exception as e:
        # Log the error message
        st.error(f"An error occurred during query execution: {str(e)}")
        # Print the generated query for debugging purposes
        st.error(f"Generated SQL Query: {generated_query}")

# If the DataFrame is stored in the session state
if 'df' in st.session_state:
    # Display the question asked by the user
    st.header("Question Asked:")
    st.write(question)

    # Display the generated SQL query
    if generated_query:
        st.header("Generated SQL Query:")
        st.code(generated_query)

    # Display the query result with meaningful column names
    st.header("Query Result")
    st.dataframe(st.session_state.df, width=800)

    # Add a download link to download the DataFrame as a CSV file
    csv = st.session_state.df.to_csv(index=False).encode()
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='query_result.csv',
        mime='text/csv'
    )

    # Add radio buttons for visualization options
    visualization = st.radio("Choose type of visualization:", ('Pie Chart', 'Bar Chart', 'Line Graph'))

    # Fetch insights only if the result is not None
    if st.session_state.result:
        st.header("Insights for the fetched result")
        try:
            st.write(insight_chain.invoke(f"You are a good insights generator. Given the data below, generate relevant insights{st.session_state.result}").content)
        except Exception as e:
            st.error(f"An error occurred while fetching insights: {str(e)}")

    # Check if DataFrame has only one column
    if len(st.session_state.df.columns) <= 1:
        st.warning("Chart is not available for this query. The result of query contains only one column.")
    else:
        # Check if DataFrame contains numeric data
        if st.session_state.df.select_dtypes(include='number').empty:
            st.warning("Chart is not available for this query. The result of query does not contain numeric data.")
        else:
            # Create the selected visualization
            label_column = st.session_state.df.columns[0]
            count_column = st.session_state.df.columns[1]

            if visualization == 'Line Graph':
                # Plot the line chart
                fig, ax = plt.subplots(figsize=(8, 6))
                st.session_state.df.plot(kind='line', x=label_column, y=count_column, marker='o', ax=ax)
                plt.xlabel(label_column)
                plt.ylabel(count_column)
                plt.title("Line Graph")
                plt.xticks(rotation=90)
                st.pyplot(fig)

            elif visualization == 'Bar Chart':
                # Plot the bar chart
                plt.figure(figsize=(8, 6))
                st.session_state.df.plot(kind='bar', x=label_column, y=count_column, rot=0)
                plt.xlabel(label_column)
                plt.ylabel(count_column)
                plt.title("Bar Chart")
                plt.xticks(rotation=90)
                plt.tight_layout()
                st.pyplot(plt)

            elif visualization == 'Pie Chart':
                # Plot the pie chart
                plt.figure(figsize=(8, 6))
                st.session_state.df.set_index(label_column)[count_column].plot(kind='pie', autopct='%1.1f%%')
                plt.ylabel('')
                plt.title("Pie Chart")
                plt.tight_layout()
                st.pyplot(plt)

else:
    st.write("No result returned from the query or empty input.")
