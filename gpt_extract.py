from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

chat_model = ChatOpenAI()

# User input clearly
user_instruction = "Create a Gmail account with username my.test.user and password Test123!"

# GPT prompt explicitly structured clearly
prompt = f"""
Extract the username and password from the following instruction explicitly. 
Respond ONLY in JSON format like this clearly:
{{
    "username": "extracted-username",
    "password": "extracted-password"
}}

Instruction clearly: {user_instruction}
"""

response = chat_model.invoke(prompt)

# Clearly print structured data
print(response.content)
