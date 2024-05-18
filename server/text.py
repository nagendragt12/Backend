import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from PyPDF2 import PdfReader

# Set OpenAI API Key
OPENAI_API_KEY = "APIKEYHERE"
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Initialize FastAPI app
app = FastAPI()

vectorstore = None
conversation_chain = None

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf.file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

@app.post("/upload-pdf")
async def upload_pdf(pdf_docs: list[UploadFile] = File(...)):
    global vectorstore, conversation_chain
    raw_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    conversation_chain = get_conversation_chain(vectorstore)
    return JSONResponse(content={"message": "PDFs uploaded and processed successfully"})

@app.post("/ask-question")
async def ask_question(user_question: str = Form(...)):
    global conversation_chain

    if not conversation_chain:
        raise HTTPException(status_code=400, detail="No conversation chain available. Please upload PDFs first.")

    response = conversation_chain({'question': user_question})
    chat_history = response['chat_history']

    return JSONResponse(content={"chat_history": chat_history})

@app.get("/")
async def read_root():
    return {"message": "Welcome to the LangChain FastAPI server"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
