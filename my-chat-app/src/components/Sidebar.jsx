import React from 'react'
import '../styles/Sidebar.css'

  function Sidebar({list, selectedId, onSelect, isOpen, onToggle, onCreateChat, onDeleteChat})
  {
    return (
        <div className={`sidebar-container ${isOpen ? 'open' : 'closed'}`}> 
<div className="sidebar-header">
        {isOpen && <button className="add-chat-btn" onClick={onCreateChat}>+ 새 채팅</button>}
        <button className="toggle-btn" onClick={onToggle}>{isOpen ? '◀' : '▶'}</button>
      </div>

        {isOpen && (
        <div className="chat-list">
          {list.map((chat) => (
            <div 
              key={chat.id} 
              className={`chat-item ${selectedId === chat.id ? 'selected' : ''}`}
              onClick={() => onSelect(chat.id)}
            >
              <span className='chat-title'>{chat.title}</span>
              <button
               className='delete-btn'
               onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
               }}>
              X
              </button>
            </div>
          ))}
        </div>
      )}
        </div>
    );
  }

  export default Sidebar