import { Badge } from "@/components/ui/badge"
import { Cpu, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"

interface HeaderProps {
  isConnected: boolean
}

export function Header({ isConnected }: HeaderProps) {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded bg-muted">
            <Cpu className="h-5 w-5 text-zinc-400" />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight">
              Smart FCU Control
            </h1>
            <p className="text-xs text-muted-foreground">
              Adaptive HVAC System
            </p>
          </div>
        </div>

        {/* Status and Actions */}
        <div className="flex items-center gap-4">
          {/* System Status */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">System:</span>
            <Badge variant={isConnected ? "success" : "destructive"} className="gap-1.5">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  isConnected ? 'bg-success-foreground animate-pulse' : 'bg-destructive-foreground'
                }`}
              />
              {isConnected ? 'Online' : 'Offline'}
            </Badge>
          </div>

          {/* Settings Button */}
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
