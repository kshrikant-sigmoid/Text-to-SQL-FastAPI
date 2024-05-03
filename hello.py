import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    azure_endpoint = "https://mlopstest.openai.azure.com/", 
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview"
)

while True:
    Question = input(">> ")
    response = client.chat.completions.create(
        model="gpt35-turbo",
        messages=[
        {"role": "user", "content": Question}
    ]
    )

    print(response.choices[0].message.content)