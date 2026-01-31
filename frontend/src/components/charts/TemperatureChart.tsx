import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import type { SensorDataPoint } from "@/lib/api"

interface TemperatureChartProps {
  data: SensorDataPoint[]
  predictions?: { timestamp: string; predicted_temp: number }[]
  setpoint: number
  height?: number
}

export function TemperatureChart({ 
  data, 
  predictions = [], 
  setpoint,
  height = 200 
}: TemperatureChartProps) {
  // Combine actual data with predictions for the chart
  const chartData = data.map((point) => {
    const time = new Date(point.timestamp)
    return {
      time: time.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      }),
      timestamp: point.timestamp,
      currentTemp: point.temperature,
      predictedTemp: null as number | null,
    }
  })

  // Add predictions to chart data
  predictions.forEach((pred) => {
    const time = new Date(pred.timestamp)
    chartData.push({
      time: time.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      }),
      timestamp: pred.timestamp,
      currentTemp: null,
      predictedTemp: pred.predicted_temp,
    })
  })

  // Sort by timestamp
  chartData.sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )

  // If we have current data, extend the prediction line from the last actual point
  if (data.length > 0 && predictions.length > 0) {
    const lastActual = data[data.length - 1]
    // Find the corresponding chart entry and add predicted temp
    const lastActualIdx = chartData.findIndex(
      (d) => d.timestamp === lastActual.timestamp
    )
    if (lastActualIdx !== -1 && lastActual.temperature !== null) {
      chartData[lastActualIdx].predictedTemp = lastActual.temperature
    }
  }

  // Calculate domain
  const temps = chartData
    .flatMap((d) => [d.currentTemp, d.predictedTemp])
    .filter((t): t is number => t !== null)
  
  const minTemp = Math.min(...temps, setpoint) - 2
  const maxTemp = Math.max(...temps, setpoint) + 2

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#27272a"
            vertical={false} 
          />
          <XAxis
            dataKey="time"
            stroke="#71717a"
            fontSize={10}
            tickLine={false}
            axisLine={{ stroke: "#3f3f46" }}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#71717a"
            fontSize={10}
            tickLine={false}
            axisLine={{ stroke: "#3f3f46" }}
            domain={[minTemp, maxTemp]}
            tickFormatter={(value) => `${value}°`}
          />
          
          <ReferenceLine 
            y={setpoint} 
            stroke="#52525b"
            strokeDasharray="8 4"
            label={{
              value: `Set: ${setpoint}°`,
              position: "right",
              fill: "#71717a",
              fontSize: 10,
            }}
          />
          
          {/* Current Temperature Line - SOLID */}
          <Line
            type="monotone"
            dataKey="currentTemp"
            stroke="#d4d4d8"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: "#fafafa", stroke: "#d4d4d8" }}
            name="Current"
            connectNulls={false}
          />
          
          {/* Predicted Temperature Line - DASHED */}
          <Line
            type="monotone"
            dataKey="predictedTemp"
            stroke="#71717a"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            activeDot={{ r: 3, fill: "#71717a", stroke: "#52525b" }}
            name="Predicted"
            connectNulls
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: "#141416",
              border: "1px solid #3f3f46",
              borderRadius: "0.375rem",
              color: "#e4e4e7",
              fontSize: "12px",
            }}
            labelStyle={{ color: "#a1a1aa" }}
            itemStyle={{ color: "#d4d4d8" }}
            formatter={(value: number | string | Array<number | string>, name: string) => {
              if (value === null || value === undefined) return ['-', name]
              const numValue = typeof value === 'number' ? value : parseFloat(String(value))
              if (isNaN(numValue)) return ['-', name]
              return [`${numValue.toFixed(1)}°C`, name]
            }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-2 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-zinc-300" />
          <span>Current</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-zinc-500 border-dashed" style={{ borderTop: "2px dashed #71717a", height: 0 }} />
          <span>Predicted</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 border-t-2 border-dashed border-zinc-600" />
          <span>Setpoint</span>
        </div>
      </div>
    </div>
  )
}
