import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bell, Wifi, WifiOff, TrendingUp, AlertTriangle } from "lucide-react"

export interface AlertItem {
  id: string
  type: 'device_discovered' | 'device_status' | 'reading' | 'prediction' | 'anomaly'
  message: string
  timestamp: string
  severity?: 'info' | 'warning' | 'success'
}

interface AlertFeedProps {
  alerts: AlertItem[]
  maxItems?: number
}

const iconMap = {
  device_discovered: Wifi,
  device_status: WifiOff,
  reading: TrendingUp,
  prediction: TrendingUp,
  anomaly: AlertTriangle,
}

const severityColors = {
  info: 'text-zinc-400',
  warning: 'text-amber-500',
  success: 'text-emerald-500',
}

export function AlertFeed({ alerts, maxItems = 10 }: AlertFeedProps) {
  const displayAlerts = alerts.slice(0, maxItems)

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Bell className="h-4 w-4 text-muted-foreground" />
          Activity Feed
          {alerts.length > 0 && (
            <Badge variant="secondary" className="ml-auto">
              {alerts.length}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-[300px] overflow-y-auto">
          {displayAlerts.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No recent activity
            </p>
          ) : (
            displayAlerts.map((alert) => {
              const Icon = iconMap[alert.type] || Bell
              const colorClass = severityColors[alert.severity || 'info']
              const time = new Date(alert.timestamp).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
              })

              return (
                <div
                  key={alert.id}
                  className="flex items-start gap-3 text-sm border-b border-border pb-2 last:border-0"
                >
                  <span className="text-xs text-muted-foreground font-mono min-w-[60px]">
                    {time}
                  </span>
                  <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${colorClass}`} />
                  <span className="text-card-foreground">{alert.message}</span>
                </div>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
