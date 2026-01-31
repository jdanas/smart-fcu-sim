const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export interface Zone {
  id: string;
  name: string;
  setpoint: number;
  adaptive_mode: boolean;
  created_at: string;
  updated_at: string;
}

export interface Device {
  id: string;
  name: string;
  type: 'fcu' | 'sensor';
  zone_id: string | null;
  status: 'online' | 'offline' | 'syncing';
  discovered_at: string;
  last_seen: string | null;
  metadata_json: Record<string, unknown> | null;
}

export interface SensorDataPoint {
  timestamp: string;
  temperature: number | null;
  humidity: number | null;
  co2_level: number | null;
  power_kw: number | null;
  occupancy: number | null;
}

export interface ZonePrediction {
  zone_id: string;
  current_temp: number;
  predicted_temp: number;
  confidence: number;
  prediction_horizon_minutes: number;
  trend: 'rising' | 'falling' | 'stable';
  timestamp: string;
}

// API functions
export async function fetchZones(): Promise<Zone[]> {
  const response = await fetch(`${API_BASE_URL}/api/zones`);
  if (!response.ok) throw new Error('Failed to fetch zones');
  return response.json();
}

export async function fetchDevices(zoneId?: string): Promise<Device[]> {
  const url = zoneId 
    ? `${API_BASE_URL}/api/devices?zone_id=${zoneId}`
    : `${API_BASE_URL}/api/devices`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch devices');
  return response.json();
}

export async function fetchSensorHistory(zoneId: string, minutes = 60): Promise<{ zone_id: string; readings: SensorDataPoint[] }> {
  const response = await fetch(`${API_BASE_URL}/api/sensors/zones/${zoneId}/history?minutes=${minutes}`);
  if (!response.ok) throw new Error('Failed to fetch sensor history');
  return response.json();
}

export async function fetchLatestReading(zoneId: string): Promise<SensorDataPoint> {
  const response = await fetch(`${API_BASE_URL}/api/sensors/zones/${zoneId}/latest`);
  if (!response.ok) throw new Error('Failed to fetch latest reading');
  return response.json();
}

export async function fetchPrediction(zoneId: string): Promise<ZonePrediction> {
  const response = await fetch(`${API_BASE_URL}/api/predictions/${zoneId}`);
  if (!response.ok) throw new Error('Failed to fetch prediction');
  return response.json();
}

export async function updateSetpoint(zoneId: string, setpoint: number): Promise<Zone> {
  const response = await fetch(`${API_BASE_URL}/api/zones/${zoneId}/setpoint`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ setpoint }),
  });
  if (!response.ok) throw new Error('Failed to update setpoint');
  return response.json();
}

export async function updateAdaptiveMode(zoneId: string, adaptive_mode: boolean): Promise<Zone> {
  const response = await fetch(`${API_BASE_URL}/api/zones/${zoneId}/adaptive`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ adaptive_mode }),
  });
  if (!response.ok) throw new Error('Failed to update adaptive mode');
  return response.json();
}

// Chat API
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatResponse {
  response: string
  error: string | null
}

export interface ChatStatus {
  available: boolean
  model: string
}

export async function sendChatMessage(messages: ChatMessage[]): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  });
  if (!response.ok) throw new Error('Failed to send message');
  return response.json();
}

export async function getChatStatus(): Promise<ChatStatus> {
  const response = await fetch(`${API_BASE_URL}/api/chat/status`);
  if (!response.ok) throw new Error('Failed to get chat status');
  return response.json();
}
