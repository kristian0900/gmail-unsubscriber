from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

chat_model = ChatOpenAI()

response = chat_model.invoke("What steps are required to create a Gmail account? List them clearly.")
print(response.content)

