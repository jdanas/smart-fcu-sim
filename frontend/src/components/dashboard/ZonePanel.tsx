import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SensorCard } from "./SensorCard"
import { FCUControlPanel } from "./FCUControlPanel"
import { TemperatureChart } from "@/components/charts/TemperatureChart"
import { 
  fetchSensorHistory, 
  fetchDevices, 
  fetchPrediction,
  type Zone, 
  type Device, 
  type SensorDataPoint,
  type ZonePrediction 
} from "@/lib/api"
import { Server, Building2 } from "lucide-react"

interface ZonePanelProps {
  zone: Zone
  onZoneUpdate?: (zone: Zone) => void
  latestReading?: SensorDataPoint | null
  latestPrediction?: ZonePrediction | null
}

const zoneIcons: Record<string, typeof Server> = {
  'server-room': Server,
  'open-office': Building2,
}

export function ZonePanel({ zone, onZoneUpdate, latestReading, latestPrediction }: ZonePanelProps) {
  const [devices, setDevices] = useState<Device[]>([])
  const [history, setHistory] = useState<SensorDataPoint[]>([])
  const [prediction, setPrediction] = useState<ZonePrediction | null>(null)

  const fcu = devices.find(d => d.type === 'fcu') || null
  const sensor = devices.find(d => d.type === 'sensor') || null

  const Icon = zoneIcons[zone.id] || Building2

  // Use latest reading if available, otherwise use last history point
  const currentReading = latestReading || history[history.length - 1] || null
  const currentPrediction = latestPrediction || prediction

  const loadData = useCallback(async () => {
    try {
      const [devicesData, historyData, predictionData] = await Promise.all([
        fetchDevices(zone.id),
        fetchSensorHistory(zone.id, 30),
        fetchPrediction(zone.id),
      ])
      setDevices(devicesData)
      setHistory(historyData.readings)
      setPrediction(predictionData)
    } catch (error) {
      console.error(`Failed to load data for zone ${zone.id}:`, error)
    }
  }, [zone.id])

  useEffect(() => {
    loadData()
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [loadData])

  // Update history when we get a new reading
  useEffect(() => {
    if (latestReading) {
      setHistory(prev => {
        const updated = [...prev, latestReading]
        // Keep only last 30 minutes of data (assuming 5s intervals = ~360 points)
        return updated.slice(-360)
      })
    }
  }, [latestReading])

  // Update prediction when we get a new one
  useEffect(() => {
    if (latestPrediction) {
      setPrediction(latestPrediction)
    }
  }, [latestPrediction])

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Icon className="h-5 w-5 text-muted-foreground" />
          {zone.name}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Sensor Cards Grid */}
        <div className="grid grid-cols-2 gap-3">
          <SensorCard
            title="Temperature"
            value={currentReading?.temperature ?? null}
            unit="°C"
            type="temperature"
            status={sensor?.status || 'offline'}
            trend={currentPrediction?.trend}
          />
          <SensorCard
            title="Humidity"
            value={currentReading?.humidity ?? null}
            unit="%"
            type="humidity"
            status={sensor?.status || 'offline'}
          />
          {zone.id === 'open-office' && (
            <>
              <SensorCard
                title="CO₂ Level"
                value={currentReading?.co2_level ?? null}
                unit="ppm"
                type="co2"
                status={sensor?.status || 'offline'}
              />
              <SensorCard
                title="Occupancy"
                value={currentReading?.occupancy ?? null}
                unit="people"
                type="occupancy"
                status={sensor?.status || 'offline'}
              />
            </>
          )}
          {zone.id === 'server-room' && (
            <SensorCard
              title="Power"
              value={currentReading?.power_kw ?? null}
              unit="kW"
              type="power"
              status={sensor?.status || 'offline'}
            />
          )}
        </div>

        {/* Temperature Chart */}
        <div className="pt-2">
          <h4 className="text-sm font-medium text-muted-foreground mb-2">
            Temperature Trend
          </h4>
          <TemperatureChart
            data={history}
            setpoint={zone.setpoint}
            height={180}
          />
        </div>

        {/* FCU Control Panel */}
        <FCUControlPanel
          zone={zone}
          fcu={fcu}
          onZoneUpdate={onZoneUpdate}
        />
      </CardContent>
    </Card>
  )
}
