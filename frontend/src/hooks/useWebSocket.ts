"use client";
import { useEffect, useRef, useState, useCallback } from "react";

interface WSMessage {
  type: string;
  data?: any;
  message?: string;
  [key: string]: any;
}

export function useWebSocket(path: string = "/ws/live-feed") {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const [messages, setMessages] = useState<WSMessage[]>([]);

  useEffect(() => {
    // Support deployment: use env var if set, otherwise fall back to localhost:8000
    const wsBase = process.env.NEXT_PUBLIC_WS_URL;
    let url: string;
    if (wsBase) {
      url = `${wsBase}${path}`;
    } else {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname;
      url = `${protocol}//${host}:8000${path}`;
    }
    
    const socket = new WebSocket(url);
    socket.onopen = () => setConnected(true);
    socket.onclose = () => { setConnected(false); setTimeout(() => {}, 3000); };
    socket.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        setLastMessage(msg);
        setMessages((prev) => [...prev.slice(-200), msg]); // Keep last 200
      } catch {}
    };
    ws.current = socket;
    return () => { socket.close(); };
  }, [path]);

  const send = useCallback((msg: WSMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(msg));
    }
  }, []);

  return { connected, lastMessage, messages, send };
}
