# Backend


# Fullstack Internship Assignment

## Objective
This project is a full-stack application that allows users to upload PDF documents and ask questions regarding the content of these documents. The backend processes these documents using natural language processing to provide answers to the questions posed by the users.

## Technologies Used
- **Backend**: FastAPI
- **NLP Processing**: LangChain/LLamaIndex
- **Frontend**: React.js
- **Database**: SQLite or PostgreSQL
- **File Storage**: Local filesystem or cloud storage (e.g., AWS S3)

## Functional Requirements
### PDF Upload
- Users can upload PDF documents to the application.
- The application stores the PDF and extracts its text content for further processing.

### Asking Questions
- Users can ask questions related to the content of an uploaded PDF.
- The system processes the question and the content of the PDF to provide an answer.

### Displaying Answers
- The application displays the answer to the user’s question.
- Users can ask follow-up or new questions on the same document.

## Non-Functional Requirements
- **Usability**: The user interface is intuitive and easy to navigate.
- **Performance**: The system optimizes the processing of PDF documents and the response time for answering questions.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js (v16 recommended)
- npm (v7+)
- SQLite or PostgreSQL

### Backend Setup
1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/fullstack-assignment.git
    cd fullstack-assignment/backend
    ```

2. **Create and Activate Virtual Environment**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Environment Variables**
    Create a `.env` file in the backend directory with the following content:
    ```
    OPENAI_API_KEY=your_openai_api_key
    DATABASE_URL=sqlite:///./test.db  # or your PostgreSQL connection string
    ```

5. **Run Migrations**
    ```bash
    alembic upgrade head
    ```

6. **Start the Backend Server**
    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup
1. **Navigate to Frontend Directory**
    ```bash
    cd ../frontend
    ```

2. **Install Dependencies**
    ```bash
    npm install
    ```

3. **Start the Frontend Server**
    ```bash
    npm start
    ```

## API Documentation

### Endpoints

#### Upload PDF
- **URL**: `/upload/`
- **Method**: `POST`
- **Description**: Uploads a PDF document and processes it.
- **Request Body**: `multipart/form-data`
    - `file`: The PDF file to upload.

#### Ask Question
- **URL**: `/ask/`
- **Method**: `POST`
- **Description**: Asks a question related to the uploaded PDF document.
- **Request Body**: `application/json`
    - `file_name`: The name of the uploaded PDF.
    - `question`: The question to ask.

### Example Request
```json
{
  "file_name": "example.pdf",
  "question": "What is the main topic of the document?"
}
