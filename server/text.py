import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS  # Updated import path
from langchain_community.embeddings import OpenAIEmbeddings  # Updated import path
from langchain_community.chat_models.openai import ChatOpenAI  # Updated import path
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
import uvicorn

# Set OpenAI API Key
OPENAI_API_KEY = "APIKEYHERE"
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorstore = None
conversation_chain = None
chat_history = []

async def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf.file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

async def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

async def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

async def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

@app.get('/')
async def index():
    return {'message': 'Welcome to the Document-Based Chatbot!'}

@app.post('/process_documents')
async def process_documents(pdf_docs: list[UploadFile] = File(...)):
    global vectorstore, conversation_chain
    raw_text = await get_pdf_text(pdf_docs)
    text_chunks = await get_text_chunks(raw_text)
    vectorstore = await get_vectorstore(text_chunks)
    conversation_chain = await get_conversation_chain(vectorstore)
    return {'message': 'Documents processed successfully!'}

@app.post('/chat')
async def chat(user_question: str = Form(...)):
    global vectorstore, conversation_chain, chat_history
    if not conversation_chain:
        raise HTTPException(status_code=400, detail="No conversation chain available. Please upload PDFs first.")
    response = conversation_chain({'question': user_question})
    chat_history = response['chat_history']
    return {'message': response['answer']}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
