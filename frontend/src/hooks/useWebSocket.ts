import { useEffect, useRef, useCallback, useState } from 'react'

export interface WebSocketMessage {
  type: 'reading' | 'prediction' | 'device_discovered' | 'device_status' | 'keepalive'
  zone_id?: string
  device_id?: string
  data?: Record<string, unknown>
  device?: Record<string, unknown>
  status?: string
  current_temp?: number
  predicted_temp?: number
  confidence?: number
  trend?: string
  timestamp?: string
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  reconnectInterval?: number
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    reconnectInterval = 3000,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/sensors`

    try {
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        setIsConnected(true)
        onConnect?.()
      }

      wsRef.current.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()
        
        // Attempt to reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, reconnectInterval)
      }

      wsRef.current.onerror = () => {
        wsRef.current?.close()
      }

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          if (message.type !== 'keepalive') {
            onMessage?.(message)
          }
        } catch {
          // Ignore invalid JSON
        }
      }
    } catch {
      // Connection failed, will retry
      reconnectTimeoutRef.current = setTimeout(() => {
        connect()
      }, reconnectInterval)
    }
  }, [onMessage, onConnect, onDisconnect, reconnectInterval])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const sendMessage = useCallback((message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    isConnected,
    sendMessage,
    disconnect,
    reconnect: connect,
  }
}
