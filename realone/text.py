import os
import time
import fitz  # PyMuPDF
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
from openai.error import RateLimitError

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = ""

# FastAPI app
app = FastAPI()

# In-memory database
documents_db = {}

# Text Splitter
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=800,
    chunk_overlap=200,
    length_function=len,
)

# Function to create embeddings with retry logic
def create_embeddings_with_retry(texts, retries=5, delay=10):
    embeddings = OpenAIEmbeddings()
    for attempt in range(retries):
        try:
            document_search = FAISS.from_texts(texts, embeddings)
            return document_search
        except RateLimitError as e:
            if attempt < retries - 1:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

# Endpoint to upload PDF documents
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Read and extract text from PDF
        pdf_content = ''
        pdf_document = fitz.open(stream=await file.read(), filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pdf_content += page.get_text()
        
        # Split the text
        texts = text_splitter.split_text(pdf_content)
        
        # Create FAISS vector store
        document_search = create_embeddings_with_retry(texts)
        
        # Store document information in the database
        document_id = str(uuid4())
        documents_db[document_id] = {
            "filename": file.filename,
            "upload_date": time.time(),
            "document_search": document_search
        }
        
        return {"document_id": document_id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to receive questions and return answers
class QuestionRequest(BaseModel):
    document_id: str
    question: str

@app.post("/ask/")
async def ask_question(request: QuestionRequest):
    try:
        document_data = documents_db.get(request.document_id)
        if not document_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document_search = document_data["document_search"]
        chain = load_qa_chain(OpenAI(), chain_type="stuff")
        
        docs = document_search.similarity_search(request.question)
        answer = chain.run(input_documents=docs, question=request.question)
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
