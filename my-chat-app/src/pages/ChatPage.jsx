import React, {useState, useEffect, useRef} from "react";
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
    //const [isTyping, setIsTyping] = useState(false);
    const socket = useRef(null);

    const [chatList, setChatList] =useState([
    {id : 1, title:"React 기초 문법"},
    {id : 2, title:"Gemini 레이아웃 따라하기"},
    ])

    const [allMessages, setAllMessages] = useState({
        1 : [{id:1, text: '1번 채팅방입니다.', isUser: false},],
        2 : [{id: 1, text: '2번 채팅방에 오신 걸 환영합니다.', isUser: false},]
    })

    const selectedIdRef = useRef(selectedId);
    useEffect(() => {
        selectedIdRef.current = selectedId;
    }, [selectedId])

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
            if (socket.current) {
                console.log(`Send Data : ${newMessage.text}`)
                socket.current.send(newMessage.text);
            }
        }
    };

    useEffect(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`.trim();
        socket.current = new WebSocket(wsUrl);

        socket.current.onopen = () => {
            console.log('Nginx를 통해 FASTAPI에 연결되었습니다.');
        };
            
        socket.current.onmessage = (event) => {
            const serverChunk = event.data;
            const currentId = selectedIdRef.current; // 현재 채팅방 ID

            setAllMessages((prev) => {
                // 1. 현재 대화방의 기존 메시지 리스트 가져오기
                const currentChatMessages = prev[currentId] || [];
                
                // 2. 마지막 메시지가 AI 메시지인지 확인
                const lastMsg = currentChatMessages[currentChatMessages.length - 1];

                if (lastMsg && !lastMsg.isUser) {
                    // 마지막 메시지가 AI라면: 기존 텍스트에 새로운 조각(chunk) 추가
                    const updatedLastMsg = { 
                        ...lastMsg, 
                        text: lastMsg.text + serverChunk 
                    };
                    return {
                        ...prev,
                        [currentId]: [...currentChatMessages.slice(0, -1), updatedLastMsg]
                    };
                } else {
                    // 마지막 메시지가 유저이거나 메시지가 없다면: 새로운 AI 메시지 객체 생성
                    const newAiMsg = {
                        id: Date.now(),
                        text: serverChunk,
                        isUser: false
                    };
                    return {
                        ...prev,
                        [currentId]: [...currentChatMessages, newAiMsg]
                    };
                }
            });
        };

        socket.current.onclose = () => {
            console.log('연결이 종료되었습니다.');
        };

        return () => {
            socket.current.close();
        };

    },[]);



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
                //isTyping={isTyping}

            />
        </div>
    )
}

export default ChatPage;

