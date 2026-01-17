import { useEffect, useState, useRef } from "react";

const PrivateChat = ({ otherUserId }) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  const token = localStorage.getItem("token")
  const senderId = localStorage.getItem("user_id");
  const wsRef = useRef(null);

  useEffect(() => {

    const ws = new WebSocket(
      `ws://127.0.0.1:8000/ws/chat/private/${otherUserId}/?token=${token}`
    );

    ws.onopen = () => console.log("✅ WS conectado")

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("📩 Mensaje recibido:", data)

      if (data.is_history) {
        setMessages(prev => [...prev, data])
      }else{
        setMessages(prev => [...prev, data])
      }
    };

    ws.onclose = () => console.log("❌ WS cerrado")
    ws.onerror = (e) => console.log("WS error", e)

    console.log(ws.url)

    setSocket(ws);

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    }
  }, [senderId,otherUserId]);

  const sendMessage = () => {
    if (!text.trim()) return;

    socket.send(JSON.stringify({
      message: text
    }));

    setText("");
  };

  const senderIdNum = Number(senderId);

  return (
    <div>
      <h3>Chat privado</h3>

      <div style={{ height: 300, overflowY: "auto" }}>
        {messages.map((msg, i) => (
          <div key={i}>
            <b>{msg.sender_id === senderIdNum ? "Yo" : "Él"}:</b>: {msg.message}
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