import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaperPlane } from '@fortawesome/free-solid-svg-icons';  // Importing the chat icon
import {PlusCircleOutlined,FileOutlined} from '@ant-design/icons';
function App() {
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState('');
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [uploading, setUploading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fileInputRef = useRef(null);

    const handleFileUpload = (e) => {
        setFile(e.target.files[0]);
        setError('');
    };

    const triggerFileInput = () => {
        fileInputRef.current.click();
    };

    const uploadFile = async () => {
        if (!file) {
            setError('Please select a file to upload.');
            return;
        }
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/upload/', formData);
            setFileName(response.data.filename);
            setError('');
        } catch (err) {
            setError('Failed to upload file. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    const askQuestion = async () => {
        if (!fileName) {
            setError('Please upload a file first.');
            return;
        }
        if (!question) {
            setError('Please enter a question.');
            return;
        }
        setLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/ask/', {
                file_name: fileName,
                question: question,
            });
            setAnswer(response.data.answer);
            setError('');
        } catch (err) {
            setError('Failed to get the answer. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <h1 className="header">AI Planet</h1>
            <div className="upload-container">
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileUpload}
                />
                <button onClick={triggerFileInput} disabled={uploading}>
                    {uploading ? 'Uploading...' : <> <PlusCircleOutlined /> Upload PDF
                    </>}
                </button>
               
                    
                
                {fileName && <p>Uploaded File: {fileName}</p>}
            </div>
            <div className="main-content">
                <div className="chat-container">
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a question..."
                        disabled={!fileName}
                        className="chat-input"
                    />
                    <button onClick={askQuestion} disabled={loading || !fileName} className="chat-button">
                        {loading ? 'Processing...' : <><FontAwesomeIcon icon={faPaperPlane} /> Search</>}
                    </button>
                </div>
                {answer && <div className="chat-response"><strong>Answer:</strong> {answer}</div>}
                {error && <div className="error">{error}</div>}
            </div>
        </div>
    );
}

export default App;
