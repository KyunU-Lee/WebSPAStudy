import React, {useState, useRef, useEffect} from "react";
import "../styles/ChatWindow.css"

function ChatWindow({selectedId, messages, onSendMessage, isTyping}) {

    const [inputText, setInputText] = useState('');
    const textareaRef = useRef(null)
    const scrollRef = useRef(null)

    useEffect(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
    }, [messages]);
  
    const handleSend = () => {
      if (inputText.trim() === '') return;
  
      const newMessage = {
        id: Date.now(),
        text: inputText,
        isUser: true,
      };
      // onSendMessage(selectedId, newMessage)
      // setInputText("");

      if (textareaRef.current) {
        textareaRef.current.style.height = 'inherit';
      }
      onSendMessage(selectedId, newMessage)
      setInputText("");
    }

    const handleInput = (e) => {
      const target = e.target;
      setInputText(target.value);
      target.style.height = 'inherit';
      target.style.height = `${Math.min(target.scrollHeight, 150)}px`
    }

    return (
        <div className="chat-window-container">
          <h2 className="chat-header">채팅방 {selectedId}</h2>
        <div className="message-area" ref={scrollRef}>
          {messages.map((msg) => (
          <div key={msg.id} className={`message-bubble ${msg.isUser ? 'user' : 'ai'}`}>
            {msg.text}
          </div>
        ))}
        {isTyping && (
          <div className="message-bubble ai typing">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}
        </div>
          <div className="input-area">
            <textarea
              ref={textareaRef}
              className="chat-input-textarea"
              placeholder='메시지를 입력하세요...'
              value={inputText}
              onChange={handleInput}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleSend();                  
                }}}
                rows={1}
            />

            <button className="send-btn" onClick={handleSend}>전송</button>
          </div>
        </div>
    );
}

export default ChatWindow;