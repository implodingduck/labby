import './Chat.css'
import React, {useEffect, useState} from 'react';
import {BackendApi} from './BackendApi';

export default function Chat(props) {

    const api = new BackendApi();
    const [question, setQuestion] = useState('');
    const [apiQuestion, setApiQuestion] = useState('');
    const [messages, setMessages] = useState([
        {"sender": "labby", "message": "Welcome, I am Labby! How can I help you today?"}
    ]);
    

    useEffect(() => {
        if(apiQuestion.length > 0){
            handleApiCall(apiQuestion);
        }
    }, [apiQuestion]);

    const handleChatSend = async (e) => {
        e.preventDefault();
        setMessages([...messages, {"sender": "user", "message": question}]);
        setApiQuestion(question)
        setQuestion('');
    }

    const handleApiCall = async (question) => {
        setApiQuestion('');
        const response = await api.chat(question);
        setMessages([...messages, {"sender": "labby", "message": response.result}]);
        
    }


    return (
        <div className="chat">
            <div className='chatwindow'>
                {messages.map((message, i) => {
                    return (
                        <div key={i} className={`message ${message.sender}`}>
                            {message.message}
                        </div>
                    )
                }
                )}
            </div>
            <textarea placeholder='Ask a question...' onChange={(e)=>{ setQuestion(e.target.value)}} value={question}>
            </textarea>
            <button onClick={handleChatSend}>Send</button>
        </div>
    );
}