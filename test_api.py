import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

try:
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    response = llm.invoke("Hello, are you working?")
    print("SUCCESS")
    print(response.content)
except Exception as e:
    print("FAILURE")
    print(e)
