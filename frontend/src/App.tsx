import { useState, useEffect, useCallback } from 'react'
import { Header } from "@/components/layout/Header"
import { ZonePanel } from "@/components/dashboard/ZonePanel"
import { AlertFeed, type AlertItem } from "@/components/dashboard/AlertFeed"
import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/hooks/use-toast"
import { useWebSocket, type WebSocketMessage } from "@/hooks/useWebSocket"
import { fetchZones, type Zone, type SensorDataPoint, type ZonePrediction } from "@/lib/api"

function App() {
  const [zones, setZones] = useState<Zone[]>([])
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [latestReadings, setLatestReadings] = useState<Record<string, SensorDataPoint>>({})
  const [latestPredictions, setLatestPredictions] = useState<Record<string, ZonePrediction>>({})
  const { toast } = useToast()

  const addAlert = useCallback((alert: AlertItem) => {
    setAlerts(prev => [alert, ...prev].slice(0, 50))
  }, [])

  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    const alertId = `${Date.now()}-${Math.random().toString(36).slice(2)}`
    const timestamp = message.timestamp || new Date().toISOString()

    if (message.type === 'reading') {
      if (message.zone_id && message.data) {
        setLatestReadings(prev => ({
          ...prev,
          [message.zone_id!]: {
            timestamp,
            temperature: message.data?.temperature as number ?? null,
            humidity: message.data?.humidity as number ?? null,
            co2_level: message.data?.co2_level as number ?? null,
            power_kw: message.data?.power_kw as number ?? null,
            occupancy: message.data?.occupancy as number ?? null,
          }
        }))
      }
    } else if (message.type === 'prediction') {
      if (message.zone_id) {
        setLatestPredictions(prev => ({
          ...prev,
          [message.zone_id!]: {
            zone_id: message.zone_id!,
            current_temp: message.current_temp!,
            predicted_temp: message.predicted_temp!,
            confidence: message.confidence!,
            prediction_horizon_minutes: 15,
            trend: message.trend as 'rising' | 'falling' | 'stable',
            timestamp,
          }
        }))
      }
    } else if (message.type === 'device_discovered') {
      const deviceName = (message.device as Record<string, unknown>)?.name || 'Unknown Device'
      const zoneId = (message.device as Record<string, unknown>)?.zone_id || 'unknown'
      
      addAlert({
        id: alertId,
        type: 'device_discovered',
        message: `New device detected: ${deviceName} in ${zoneId}`,
        timestamp,
        severity: 'success',
      })

      toast({
        title: "Device Discovered",
        description: `${deviceName} has been detected`,
        variant: "default",
      })
    } else if (message.type === 'device_status') {
      const statusMessage = message.status === 'online' 
        ? `${message.device_id} is now online`
        : `${message.device_id} went ${message.status}`
      
      addAlert({
        id: alertId,
        type: 'device_status',
        message: statusMessage,
        timestamp,
        severity: message.status === 'online' ? 'success' : 'warning',
      })

      if (message.status !== 'online') {
        toast({
          title: "Device Status Change",
          description: statusMessage,
          variant: message.status === 'offline' ? "destructive" : "default",
        })
      }
    }
  }, [toast, addAlert])

  const { isConnected } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onConnect: () => {
      addAlert({
        id: `${Date.now()}-connect`,
        type: 'device_status',
        message: 'Connected to server',
        timestamp: new Date().toISOString(),
        severity: 'success',
      })
    },
    onDisconnect: () => {
      addAlert({
        id: `${Date.now()}-disconnect`,
        type: 'device_status',
        message: 'Disconnected from server',
        timestamp: new Date().toISOString(),
        severity: 'warning',
      })
    },
  })

  // Load initial zones
  useEffect(() => {
    const loadZones = async () => {
      try {
        const zonesData = await fetchZones()
        setZones(zonesData)
      } catch (error) {
        console.error('Failed to load zones:', error)
      }
    }
    loadZones()
  }, [])

  const handleZoneUpdate = (updatedZone: Zone) => {
    setZones(prev => 
      prev.map(z => z.id === updatedZone.id ? updatedZone : z)
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Header isConnected={isConnected} />
      
      <main className="container mx-auto px-4 py-6">
        {/* Zone Panels - Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {zones.map(zone => (
            <ZonePanel
              key={zone.id}
              zone={zone}
              onZoneUpdate={handleZoneUpdate}
              latestReading={latestReadings[zone.id]}
              latestPrediction={latestPredictions[zone.id]}
            />
          ))}
        </div>

        {/* Activity Feed */}
        <AlertFeed alerts={alerts} maxItems={15} />
      </main>

      <Toaster />
    </div>
  )
}

export default App
