import { useEffect, useState, useRef } from "react";
import "../components/ChatModule.css"

const PrivateChat = ({ otherUserId }) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [offset, setOffset] = useState(15);
  const [wsReady,setWsReady] = useState(false);

  const token = localStorage.getItem("token")
  const senderId = localStorage.getItem("user_id");
  const wsRef = useRef(null);
  const topRef = useRef(null);

  useEffect(() => {

    wsRef.current = new WebSocket(
      `ws://127.0.0.1:8000/ws/chat/private/${otherUserId}/?token=${token}`
    );

    wsRef.current.onopen = () => {
      console.log("✅ WS conectado")
      setWsReady(true);
    }

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.is_history) {
        setMessages(prev => [...prev, data])
      }else{
        setMessages(prev => [...prev, data])
      }
    };

    wsRef.current.onclose = () => {
      console.log("❌ WS cerrado")
      setWsReady(false);
    }
    wsRef.current.onerror = (e) => console.log("WS error", e)

    setSocket(wsRef);

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    }
  }, [senderId,otherUserId]);

  const sendMessage = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN){
      console.log("ws aun no esta listo")
      return;
    } 

    wsRef.current.send(JSON.stringify({
      type:"message",
      message: text
    }));

    setText("");
  };

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries.isIntersecting &&
        wsRef.current &&
        wsReady.current.readyState === WebSocket.OPEN
      ){
        wsRef.current.send(JSON.stringify({
          type: "load_more",
          offset: offset
        }))
        setOffset(prev => prev + 15);
      }
    })

    if(topRef.current){
      observer.observe(topRef.current);
    }

    return () => observer.disconnect();
  },[offset])

  const senderIdNum = Number(senderId);

  return (
    <div>
      <h3>Chat privado</h3>

      <div ref={topRef} className="chat-container">
        {messages.map((msg, i) => (
          <div key={i} className={msg.sender_id === senderIdNum ? 'message-row' : 'message-row-theirs'}>
            <div className={msg.sender_id === senderIdNum ? 'message-bubble' : 'bubble-theirs'}>
              <b>{msg.sender_id === senderIdNum ? "Yo" : "Él"}:</b>: {msg.message}
            </div>
          </div>
        ))}
      </div>

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      />
      <button onClick={sendMessage}>Enviar</button>
    </div>
  );
};

export default PrivateChat;