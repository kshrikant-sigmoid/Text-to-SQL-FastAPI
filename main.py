import streamlit as st
import os
import pandas as pd
import ast
import sqlite3
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI

load_dotenv()

# Create a database instance
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

# Create a query execution tool
execute_query = QuerySQLDataBaseTool(db=db)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
chain = create_sql_query_chain(llm, db)
insight_chain = ChatOpenAI(model="gpt-3.5-turbo")

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
    selected_tables = [st.checkbox(table) for table in tables]

    # Add selected tables to the question
    if selected_tables:
        selected_tables_str = ", ".join([f"`{table}`" for table in tables if selected_tables[tables.index(table)]])
        question += f" strictly using only the {selected_tables_str} table/s and not other available tables in the database" if True in selected_tables else ""

result = None

# When the user presses the 'Run query' button and the input is not empty
if st.sidebar.button('Run query') and question.strip():
    try:
        # Create a SQL query chain
        write_query = create_sql_query_chain(llm, db)

        # Get the generated query without limit
        generated_query = write_query.invoke({"question": question})

        # Remove one LIMIT clause if there are multiple
        # Check if any of the words are present in the question
        limit_keywords = ["limit", "top", "last", "highest", "lowest", "max", "min", "maximum", "minimum"]
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

            # Store the DataFrame in the session state
            st.session_state.df = df
            st.session_state.result = result

    except sqlite3.ProgrammingError as e:
        st.error("Error:", e)
        st.error("You can only execute one statement at a time.")

# If the DataFrame is stored in the session state
if 'df' in st.session_state:

    # Display the question asked by the user
    st.header("Question Asked:")
    st.write(question)

    # Create a SQL query chain
    write_query = create_sql_query_chain(llm, db)
    # Get the generated query without limit
    generated_query = write_query.invoke({"question": question})

    limit_keywords = ["limit", "top", "last", "highest", "lowest", "max", "min", "maximum", "minimum"]
    if not any(keyword in question.lower() for keyword in limit_keywords):
        if "LIMIT" in generated_query:
            generated_query = generated_query.split("LIMIT")[0] + ";"

    # Display the generated SQL query
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
        st.write(insight_chain.invoke(f"You are a good insights generator. Given the data below, generate relevant insights{st.session_state.result}").content)

    # Check if DataFrame has only one column
    if len(st.session_state.df.columns) <= 1:
        st.warning("Chart is not available for this query. The result of query contains only one column.")
    else:
        # Check if DataFrame contains numeric data
        if st.session_state.df.select_dtypes(include='number').empty:
            st.warning("Chart is not available for this query. The result of query does not contain numeric data.")
        else:
            # Create the selected visualization
            if visualization == 'Line Graph':
                # Identify the label column
                label_column = st.session_state.df.columns[0]
                if not st.session_state.df[label_column].dtype == 'object':
                    # If the first column is not string, find the first string column
                    label_column = st.session_state.df.select_dtypes(include='object').columns[0]

                # Identify the numeric column for counts
                count_column = st.session_state.df.columns[1]
                if not pd.api.types.is_numeric_dtype(st.session_state.df[count_column]):
                    # If the second column is not numeric, find the first numeric column
                    count_column = st.session_state.df.select_dtypes(include='number').columns[0]

                # Plot the line chart
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.plot(st.session_state.df[label_column], st.session_state.df[count_column], marker='o')

                # Annotate each point with its value, rotating the text vertically
                for index, row in st.session_state.df.iterrows():
                    ax.annotate(f"{row[count_column]}", (row[label_column], row[count_column]), textcoords="offset points", xytext=(0,10), ha='center', rotation=90)

                plt.xlabel(label_column)
                plt.ylabel(count_column)
                plt.title("Line Graph")

                # Rotate x-axis labels vertically
                plt.xticks(rotation=90)

                st.pyplot(fig)

            elif visualization == 'Bar Chart':
                # Identify the label column
                label_column = st.session_state.df.columns[0]
                if not st.session_state.df[label_column].dtype == 'object':
                    # If the first column is not string, find the first string column
                    label_column = st.session_state.df.select_dtypes(include='object').columns[0]

                # Identify the numeric column for counts
                count_column = st.session_state.df.columns[1]
                if not pd.api.types.is_numeric_dtype(st.session_state.df[count_column]):
                    # If the second column is not numeric, find the first numeric column
                    count_column = st.session_state.df.select_dtypes(include='number').columns[0]

                # Plot the bar chart
                plt = st.session_state.df.plot.bar(x=label_column, y=count_column, rot=0, figsize=(5, 5))  # Rotated x-axis labels by 0 degrees

                # Rotate x-axis labels vertically
                plt.set_xticklabels(st.session_state.df[label_column], rotation=90)

                # Annotate count values above each bar, rotating the text vertically
                for index, value in enumerate(st.session_state.df[count_column]):
                    plt.text(index, value, str(value), ha='center', va='bottom', rotation=90)  # Rotate the text vertically

                plt.figure.tight_layout()  # Adjust layout to prevent clipping of labels
                st.pyplot(plt.get_figure())

            elif visualization == 'Pie Chart':
                # Identify the label column
                label_column = st.session_state.df.columns[0]
                if not st.session_state.df[label_column].dtype == 'object':
                    # If the first column is not string, find the first string column
                    label_column = st.session_state.df.select_dtypes(include='object').columns[0]

                # Identify the numeric column for counts
                count_column = st.session_state.df.columns[1]
                if not pd.api.types.is_numeric_dtype(st.session_state.df[count_column]):
                    # If the second column is not numeric, find the first numeric column
                    count_column = st.session_state.df.select_dtypes(include='number').columns[0]

                # Create the pie chart using Matplotlib
                fig, ax = plt.subplots(figsize=(5, 5))
                wedges, labels, autopct = ax.pie(st.session_state.df[count_column], labels=st.session_state.df[label_column], autopct='%1.1f%%')

                # Get the value counts for each label from the DataFrame result
                value_counts = st.session_state.df.groupby(label_column)[count_column].sum()

                # Generate legend labels with names and counts or percentages
                legend_labels = [f"{label} ({value_counts.get(label, 100*count/len(st.session_state.df)):.1f})" for label, count in zip(st.session_state.df[label_column], st.session_state.df[count_column])]

                # Adjust legend position
                ax.legend(wedges, legend_labels, title="Description", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

                # Display the pie chart
                st.pyplot(fig)

else:
    st.write("No result returned from the query or empty input.")