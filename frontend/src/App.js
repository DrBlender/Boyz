import React, { useState, useEffect } from "react";

const serverUrl = "ws://195.201.34.39:8000/ws/";

function App() {
  const [username, setUsername] = useState("");
  const [ws, setWs] = useState(null);
  const [messages, setMessages] = useState([]);
  const [answer, setAnswer] = useState("");

  useEffect(() => {
    if (username) {
      const socket = new WebSocket(serverUrl + username);
      socket.onmessage = (event) => {
        setMessages((prev) => [...prev, event.data]);
      };
      setWs(socket);
      return () => socket.close();
    }
  }, [username]);

  const sendBuzzer = () => ws?.send("buzzer");
  const sendAnswer = () => ws?.send("answer:" + answer);

  return (
    <div>
      {!username ? (
        <div>
          <input onChange={(e) => setUsername(e.target.value)} placeholder="Name" />
          <button onClick={() => setUsername(username)}>Beitreten</button>
        </div>
      ) : (
        <div>
          <button onClick={sendBuzzer}>Buzzer!</button>
          <input onChange={(e) => setAnswer(e.target.value)} placeholder="Deine Antwort" />
          <button onClick={sendAnswer}>Antwort senden</button>
          <div>
            <h3>Chat:</h3>
            {messages.map((msg, i) => (
              <p key={i}>{msg}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
