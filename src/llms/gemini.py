import os
from langchain_google_genai import ChatGoogleGenerativeAI

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDgAlnEdV-wwLc41VtAvD3p4NvmmVrJIro"

def gemini_client():
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDgAlnEdV-wwLc41VtAvD3p4NvmmVrJIro"

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.5,
        max_tokens=None,
        timeout=None,
    )
    return llm