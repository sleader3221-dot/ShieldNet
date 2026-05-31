import { useEffect, useRef, useState, useCallback } from 'react';

type EventHandler = (...args: any[]) => void;

interface UseWebSocketOptions {
  url?: string;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

interface QueuedMessage {
  event: string;
  data: any;
  timestamp: number;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
    autoConnect = true,
    reconnectAttempts = 10,
    reconnectDelay = 2000,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const eventHandlersRef = useRef<Map<string, Set<EventHandler>>>(new Map());
  const messageQueueRef = useRef<QueuedMessage[]>([]);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) return;

    setStatus('connecting');
    setError(null);

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (!mountedRef.current) { ws.close(); return; }
        setStatus('connected');
        setError(null);
        reconnectCountRef.current = 0;
        flushMessageQueue();
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          const type = data.type;
          if (type) {
            const handlers = eventHandlersRef.current.get(type);
            if (handlers) {
              handlers.forEach((handler) => handler(data));
            }
          }

          const allHandlers = eventHandlersRef.current.get('*');
          if (allHandlers) {
            allHandlers.forEach((handler) => handler(data));
          }
        } catch {
          setLastMessage({ raw: event.data });
        }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setStatus('disconnected');
        if (reconnectCountRef.current < reconnectAttempts) {
          attemptReconnect();
        }
      };

      ws.onerror = () => {
        if (!mountedRef.current) return;
        setError(new Error('WebSocket connection error'));
        setStatus('error');
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to create WebSocket'));
      setStatus('error');
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('disconnected');
  }, []);

  const attemptReconnect = useCallback(() => {
    if (reconnectCountRef.current >= reconnectAttempts || !mountedRef.current) return;

    reconnectCountRef.current += 1;
    const delay = reconnectDelay * Math.min(reconnectCountRef.current, 5);

    reconnectTimerRef.current = setTimeout(() => {
      if (mountedRef.current) connect();
    }, delay);
  }, [connect, reconnectAttempts, reconnectDelay]);

  const flushMessageQueue = useCallback(() => {
    const queue = messageQueueRef.current;
    messageQueueRef.current = [];
    queue.forEach((msg) => {
      sendMessage(msg.event, msg.data);
    });
  }, []);

  const sendMessage = useCallback((event: string, data?: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'object' ? { ...data, type: event } : { type: event, data };
      wsRef.current.send(JSON.stringify(payload));
    } else {
      messageQueueRef.current.push({
        event,
        data,
        timestamp: Date.now(),
      });
    }
  }, []);

  const send = useCallback((event: string, data?: any) => {
    sendMessage(event, data);
  }, [sendMessage]);

  const emit = sendMessage;

  const on = useCallback((event: string, handler: EventHandler) => {
    if (!eventHandlersRef.current.has(event)) {
      eventHandlersRef.current.set(event, new Set());
    }
    eventHandlersRef.current.get(event)!.add(handler);

    return () => {
      const handlers = eventHandlersRef.current.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          eventHandlersRef.current.delete(event);
        }
      }
    };
  }, []);

  const off = useCallback((event: string, handler?: EventHandler) => {
    if (handler) {
      const handlers = eventHandlersRef.current.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          eventHandlersRef.current.delete(event);
        }
      }
    } else {
      eventHandlersRef.current.delete(event);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    if (autoConnect) connect();

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    status,
    lastMessage,
    error,
    isConnected: status === 'connected',
    connect,
    disconnect,
    emit,
    on,
    off,
    send,
  };
}
