import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DeviceStatusBadge } from "./DeviceStatusBadge"
import { Thermometer, Droplets, Zap, Users, Wind } from "lucide-react"

interface SensorCardProps {
  title: string
  value: number | null
  unit: string
  type: 'temperature' | 'humidity' | 'power' | 'occupancy' | 'co2'
  status?: 'online' | 'offline' | 'syncing'
  trend?: 'rising' | 'falling' | 'stable'
}

const iconMap = {
  temperature: Thermometer,
  humidity: Droplets,
  power: Zap,
  occupancy: Users,
  co2: Wind,
}

const colorMap = {
  temperature: "text-zinc-300",
  humidity: "text-zinc-400",
  power: "text-zinc-300",
  occupancy: "text-zinc-400",
  co2: "text-zinc-400",
}

export function SensorCard({ title, value, unit, type, status = 'online', trend }: SensorCardProps) {
  const Icon = iconMap[type]
  const colorClass = colorMap[type]

  const trendIcon = trend === 'rising' ? '↗' : trend === 'falling' ? '↘' : '→'
  const trendColor = trend === 'rising' ? 'text-zinc-400' : trend === 'falling' ? 'text-zinc-500' : 'text-zinc-600'

  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className={`h-4 w-4 ${colorClass}`} />
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-foreground">
              {value !== null ? value.toFixed(1) : '--'}
            </span>
            <span className="text-sm text-muted-foreground">{unit}</span>
            {trend && (
              <span className={`text-sm ml-2 ${trendColor}`}>{trendIcon}</span>
            )}
          </div>
          <DeviceStatusBadge status={status} showLabel={false} />
        </div>
      </CardContent>
    </Card>
  )
}
