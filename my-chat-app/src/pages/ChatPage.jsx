import React, {useState} from "react";
import Sidebar from "../components/sideBar";
import ChatWindow from "../components/chatWindow";

  const styleOutter = {
    width: 'calc(100% - 100px)',
    height: 'calc(100vh - 100px)',
    display: 'flex',
    overflow: 'hidden',
    boxSizing: 'border-box',
  };

function ChatPage() {
    const [selectedId, setSelectedId] = useState(1);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [isTyping, setIsTyping] = useState(false);

    const [chatList, setChatList] =useState([
    {id : 1, title:"React 기초 문법"},
    {id : 2, title:"Gemini 레이아웃 따라하기"},
    ])

    const [allMessages, setAllMessages] = useState({
        1 : [{id:1, text: '1번 채팅방입니다.', isUser: false},],
        2 : [{id: 1, text: '2번 채팅방에 오신 걸 환영합니다.', isUser: false},]
    })


    const CreateNewChat = () => {
        const newId = Date.now();
        const newChat = { id: newId, title: `새 대화 ${chatList.length + 1}`};
        setChatList([...chatList, newChat]);
        setAllMessages({
            ...allMessages,
            [newId] : [{id:1, text:"새로운 대화가 시작되었습니다.!", isUser : false}]
        });
        setSelectedId(newId);
    }

    const deleteChat = (chatId) => {
        if (chatList.length <= 1) {
            alert("최소 하나의 대화방은 유지해야 합니다.");
            return;
        }

        const updateList = chatList.filter((chat) => chat.id !== chatId);
        setChatList(updateList);

        const updatedMessage = {...allMessages};
        delete updatedMessage[chatId];
        setAllMessages(updatedMessage);

        if (selectedId === chatId) {
            setSelectedId(updateList[0].id);
        }
    };

    const addMessage = (chatId, newMessage) => {
        setAllMessages((prev) => ({
            ...prev,
            [chatId]: [...(prev[chatId] || []), newMessage],
        }));

        if (newMessage.isUser) {
            setIsTyping(true);

            setTimeout(() => {
                const aiResponse = {
                id: Date.now() + 1, // ID 중복 방지
                text: `"${newMessage.text}"라고 말씀하셨군요! 더 궁금한 게 있으신가요?`,
                isUser: false, // AI 메시지
                };

                // 다시 setAllMessages를 호출하여 AI 메시지 추가
                setAllMessages((prev) => ({
                ...prev,
                [chatId]: [...(prev[chatId] || []), aiResponse],
                }));
                setIsTyping(false);
            }, 1500); // 1000ms = 1초
        };
    };

    return (
        <div style={styleOutter}>
            <Sidebar 
                list={chatList}
                selectedId={selectedId}
                onSelect={setSelectedId}
                isOpen={isSidebarOpen}
                onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
                onCreateChat = {CreateNewChat}
                onDeleteChat = {deleteChat}
            />
            <ChatWindow 
                selectedId={selectedId}
                messages={allMessages[selectedId] || []}
                onSendMessage={addMessage}
                isTyping={isTyping}

            />
        </div>
    )
}

export default ChatPage;

