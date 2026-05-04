"use client";

import { useState, useRef, useEffect, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  emotion?: { emotion: string; intensity: number };
  timestamp: Date;
  crisis?: { level: string; resources: string[] };
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [voiceState, setVoiceState] = useState<"idle" | "listening" | "processing" | "speaking">("idle");
  const [userId] = useState(() => {
    if (typeof window !== "undefined") {
      let id = localStorage.getItem("mindos_user_id");
      if (!id) {
        id = "user_" + generateId();
        localStorage.setItem("mindos_user_id", id);
      }
      return id;
    }
    return "user_" + generateId();
  });
  const [sessionId, setSessionId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // WebSocket connection
  useEffect(() => {
    const connectWs = () => {
      const wsUrl = API_BASE.replace("http", "ws") + `/ws/voice/${userId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          handleWsMessage(msg);
        } catch (e) {
          console.error("WS parse error:", e);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket closed, reconnecting in 3s...");
        setTimeout(connectWs, 3000);
      };

      ws.onerror = () => {
        console.log("WebSocket error — backend may not be running");
      };

      wsRef.current = ws;
    };

    connectWs();

    return () => {
      wsRef.current?.close();
    };
  }, [userId]);

  const handleWsMessage = useCallback((msg: { type: string; data: unknown; memories_used?: number }) => {
    switch (msg.type) {
      case "status":
        if (msg.data === "processing") setVoiceState("processing");
        else if (msg.data === "speaking") setVoiceState("speaking");
        else if (msg.data === "idle") setVoiceState("idle");
        break;

      case "transcription":
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            role: "user",
            content: msg.data as string,
            timestamp: new Date(),
          },
        ]);
        break;

      case "emotion":
        // Update last user message with emotion
        setMessages((prev) => {
          const updated = [...prev];
          const lastUser = [...updated].reverse().find((m) => m.role === "user");
          if (lastUser) {
            lastUser.emotion = msg.data as { emotion: string; intensity: number };
          }
          return updated;
        });
        break;

      case "reply":
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            role: "assistant",
            content: msg.data as string,
            timestamp: new Date(),
          },
        ]);
        setIsLoading(false);
        break;

      case "crisis":
        const crisisData = msg.data as { level: string; resources: string[] };
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last) last.crisis = crisisData;
          return updated;
        });
        break;

      case "audio":
        // Play audio response
        playAudio(msg.data as string);
        break;

      case "error":
        setIsLoading(false);
        setVoiceState("idle");
        break;
    }
  }, []);

  const playAudio = (base64Audio: string) => {
    try {
      const audioBytes = atob(base64Audio);
      const arrayBuffer = new ArrayBuffer(audioBytes.length);
      const view = new Uint8Array(arrayBuffer);
      for (let i = 0; i < audioBytes.length; i++) {
        view[i] = audioBytes.charCodeAt(i);
      }
      const blob = new Blob([arrayBuffer], { type: "audio/mpeg" });
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.onended = () => {
        setVoiceState("idle");
        URL.revokeObjectURL(url);
      };
      audio.play().catch(() => setVoiceState("idle"));
    } catch {
      setVoiceState("idle");
    }
  };

  // Send text message via REST API
  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    setInput("");
    setIsLoading(true);

    const userMsg: Message = {
      id: generateId(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    // Try WebSocket first
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "text", data: text }));
      return;
    }

    // Fallback to REST
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, message: text, session_id: sessionId || undefined }),
      });

      if (!res.ok) throw new Error("API error");
      const data = await res.json();

      if (data.session_id) setSessionId(data.session_id);

      const botMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: data.reply,
        emotion: data.emotion,
        timestamp: new Date(),
        crisis: data.crisis?.level !== "none" ? data.crisis : undefined,
      };

      // Update user message with emotion
      setMessages((prev) => {
        const updated = prev.map((m) =>
          m.id === userMsg.id ? { ...m, emotion: data.emotion } : m
        );
        return [...updated, botMsg];
      });
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "assistant",
          content: "I'm having trouble connecting. Please make sure the backend server is running on localhost:8000.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Voice recording
  const toggleVoice = async () => {
    if (voiceState === "listening") {
      // Stop recording
      mediaRecorderRef.current?.stop();
      setVoiceState("processing");
      return;
    }

    if (voiceState !== "idle") return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });

        if (wsRef.current?.readyState === WebSocket.OPEN) {
          const arrayBuffer = await audioBlob.arrayBuffer();
          wsRef.current.send(arrayBuffer);
          setIsLoading(true);
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(250); // 250ms chunks
      setVoiceState("listening");
    } catch (err) {
      console.error("Microphone access denied:", err);
      setVoiceState("idle");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const voiceIcon = {
    idle: "🎤",
    listening: "⏹️",
    processing: "⏳",
    speaking: "🔊",
  }[voiceState];

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Chat with MindOS</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: wsRef.current?.readyState === WebSocket.OPEN ? "var(--mint-500)" : "var(--text-muted)",
            }}
          />
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
            {wsRef.current?.readyState === WebSocket.OPEN ? "Connected" : "Connecting..."}
          </span>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <h2>Hello, I&apos;m MindOS 🧠</h2>
            <p>Your AI wellness companion. I&apos;m here to listen, support, and remember. How are you feeling today?</p>
            <div className="welcome-features">
              <div className="welcome-feature glass-card">
                <div className="feature-icon">🎤</div>
                <div className="feature-text">Voice Conversations</div>
              </div>
              <div className="welcome-feature glass-card">
                <div className="feature-icon">🧠</div>
                <div className="feature-text">Long-term Memory</div>
              </div>
              <div className="welcome-feature glass-card">
                <div className="feature-icon">💚</div>
                <div className="feature-text">Emotion Aware</div>
              </div>
              <div className="welcome-feature glass-card">
                <div className="feature-icon">🛡️</div>
                <div className="feature-text">Safe & Private</div>
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            <div className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === "assistant" ? "🧠" : "👤"}
              </div>
              <div className="message-body">
                <div className="message-content">{msg.content}</div>
                <div className="message-meta">
                  <span className="message-time">
                    {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                  {msg.emotion && msg.emotion.emotion !== "neutral" && (
                    <span className={`emotion-badge ${msg.emotion.emotion}`}>
                      {msg.emotion.emotion}
                    </span>
                  )}
                </div>
              </div>
            </div>
            {msg.crisis && msg.crisis.level !== "none" && (
              <div className="crisis-banner">
                <h3>🆘 Support Resources</h3>
                <ul>
                  {msg.crisis.resources.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="typing-indicator">
            <div className="message-avatar" style={{
              width: 36, height: 36, borderRadius: "50%",
              background: "linear-gradient(135deg, var(--purple-600), var(--purple-400))",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "0.9rem", boxShadow: "0 0 12px var(--purple-glow)",
            }}>🧠</div>
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="typing-label">MindOS is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <button
            className={`voice-btn ${voiceState}`}
            onClick={toggleVoice}
            title={voiceState === "idle" ? "Start voice input" : voiceState === "listening" ? "Stop recording" : ""}
          >
            {voiceIcon}
          </button>
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message or click 🎤 to speak..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="btn-send"
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            title="Send message"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
