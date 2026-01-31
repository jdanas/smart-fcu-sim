import { Badge } from "@/components/ui/badge"

interface DeviceStatusBadgeProps {
  status: 'online' | 'offline' | 'syncing'
  showLabel?: boolean
}

export function DeviceStatusBadge({ status, showLabel = true }: DeviceStatusBadgeProps) {
  const config = {
    online: { variant: 'success' as const, label: 'Online' },
    offline: { variant: 'destructive' as const, label: 'Offline' },
    syncing: { variant: 'secondary' as const, label: 'Syncing' },
  }

  const { variant, label } = config[status]

  return (
    <Badge variant={variant} className="gap-1.5">
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === 'online'
            ? 'bg-success-foreground animate-pulse'
            : status === 'syncing'
            ? 'bg-secondary-foreground animate-pulse'
            : 'bg-destructive-foreground'
        }`}
      />
      {showLabel && <span>{label}</span>}
    </Badge>
  )
}
