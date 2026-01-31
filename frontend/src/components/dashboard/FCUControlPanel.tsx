import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { DeviceStatusBadge } from "./DeviceStatusBadge"
import type { Zone, Device } from "@/lib/api"
import { updateSetpoint, updateAdaptiveMode } from "@/lib/api"
import { Settings2 } from "lucide-react"

interface FCUControlPanelProps {
  zone: Zone
  fcu: Device | null
  onZoneUpdate?: (zone: Zone) => void
}

export function FCUControlPanel({ zone, fcu, onZoneUpdate }: FCUControlPanelProps) {
  const [localSetpoint, setLocalSetpoint] = useState(zone.setpoint)
  const [isUpdating, setIsUpdating] = useState(false)

  const handleSetpointChange = (value: number[]) => {
    setLocalSetpoint(value[0])
  }

  const handleSetpointCommit = async () => {
    if (localSetpoint === zone.setpoint) return
    
    setIsUpdating(true)
    try {
      const updated = await updateSetpoint(zone.id, localSetpoint)
      onZoneUpdate?.(updated)
    } catch (error) {
      console.error('Failed to update setpoint:', error)
      setLocalSetpoint(zone.setpoint)
    } finally {
      setIsUpdating(false)
    }
  }

  const handleAdaptiveModeToggle = async (checked: boolean) => {
    try {
      const updated = await updateAdaptiveMode(zone.id, checked)
      onZoneUpdate?.(updated)
    } catch (error) {
      console.error('Failed to update adaptive mode:', error)
    }
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Settings2 className="h-4 w-4 text-muted-foreground" />
            FCU Control
          </CardTitle>
          {fcu && <DeviceStatusBadge status={fcu.status} />}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Setpoint Control */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Setpoint</span>
            <span className="text-sm font-mono font-medium">
              {localSetpoint.toFixed(1)}°C
            </span>
          </div>
          <Slider
            value={[localSetpoint]}
            onValueChange={handleSetpointChange}
            onValueCommit={handleSetpointCommit}
            min={15}
            max={28}
            step={0.5}
            disabled={isUpdating}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>15°C</span>
            <span>28°C</span>
          </div>
        </div>

        <Separator className="bg-border" />

        {/* Adaptive Mode Toggle */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <span className="text-sm font-medium">Adaptive Control</span>
            <p className="text-xs text-muted-foreground">
              AI-powered temperature optimization
            </p>
          </div>
          <Switch
            checked={zone.adaptive_mode}
            onCheckedChange={handleAdaptiveModeToggle}
          />
        </div>

        <Separator className="bg-border" />

        {/* FCU Info */}
        {fcu && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Device</span>
              <span className="font-mono text-xs">{fcu.id}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Name</span>
              <span className="text-xs truncate max-w-[120px]">{fcu.name}</span>
            </div>
          </div>
        )}

        {/* Manual Override Button */}
        <Button
          variant="outline"
          size="sm"
          className="w-full mt-2"
          disabled={!zone.adaptive_mode}
        >
          Manual Override
        </Button>
      </CardContent>
    </Card>
  )
}
