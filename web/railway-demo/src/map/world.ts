export type Point = {
  x: number;
  y: number;
};

export type StationId = "gateway" | "queue" | "prefill" | "decode" | "metrics";

export type Station = {
  id: StationId;
  label: string;
  shortLabel: string;
  color: number;
  position: Point;
  radius: number;
  description: string;
};

export type Avatar = {
  id: string;
  name: string;
  color: number;
  position: Point;
};

export type Train = {
  id: string;
  userId: string;
  color: number;
  progress: number;
};

export const WORLD_WIDTH = 1920;
export const WORLD_HEIGHT = 920;

export const STATIONS: Station[] = [
  {
    id: "gateway",
    label: "Gateway",
    shortLabel: "1",
    color: 0x42a65a,
    position: { x: 360, y: 410 },
    radius: 118,
    description: "Request enters TokenKaki and selects a backend."
  },
  {
    id: "queue",
    label: "Queue",
    shortLabel: "2",
    color: 0xf1a21f,
    position: { x: 700, y: 430 },
    radius: 112,
    description: "Gateway-observed crowd load and active trains."
  },
  {
    id: "prefill",
    label: "Prefill",
    shortLabel: "3",
    color: 0x2bb9bd,
    position: { x: 1040, y: 395 },
    radius: 120,
    description: "First-token timing lens for prompt processing."
  },
  {
    id: "decode",
    label: "Decode",
    shortLabel: "4",
    color: 0x2f7bde,
    position: { x: 1380, y: 425 },
    radius: 120,
    description: "Streaming chunks and generation progress."
  },
  {
    id: "metrics",
    label: "Metrics",
    shortLabel: "5",
    color: 0x7750ce,
    position: { x: 1700, y: 390 },
    radius: 118,
    description: "Run status, latency, and benchmark references."
  }
];

export const TRACK_POINTS: Point[] = [
  { x: 180, y: 650 },
  { x: 360, y: 635 },
  { x: 560, y: 665 },
  { x: 700, y: 640 },
  { x: 900, y: 665 },
  { x: 1040, y: 625 },
  { x: 1220, y: 650 },
  { x: 1380, y: 630 },
  { x: 1540, y: 660 },
  { x: 1700, y: 630 },
  { x: 1840, y: 650 }
];

export const INITIAL_AVATARS: Avatar[] = [
  { id: "user-1", name: "You", color: 0x2f7bde, position: { x: 150, y: 520 } },
  { id: "user-2", name: "Ari", color: 0xf1a21f, position: { x: 210, y: 560 } },
  { id: "user-3", name: "Kim", color: 0x42a65a, position: { x: 260, y: 520 } },
  { id: "user-4", name: "Sam", color: 0x7750ce, position: { x: 310, y: 570 } }
];

export const MOCK_TRAINS: Train[] = [
  { id: "req-001", userId: "user-1", color: 0x2f7bde, progress: 0.18 },
  { id: "req-002", userId: "user-2", color: 0xf1a21f, progress: 0.42 },
  { id: "req-003", userId: "user-3", color: 0x42a65a, progress: 0.66 },
  { id: "req-004", userId: "user-4", color: 0x7750ce, progress: 0.86 }
];

export function clampToWorld(point: Point): Point {
  return {
    x: Math.max(70, Math.min(WORLD_WIDTH - 70, point.x)),
    y: Math.max(120, Math.min(WORLD_HEIGHT - 90, point.y))
  };
}

export function nearestStation(point: Point): Station | null {
  for (const station of STATIONS) {
    const dx = point.x - station.position.x;
    const dy = point.y - station.position.y;
    if (Math.sqrt(dx * dx + dy * dy) <= station.radius) {
      return station;
    }
  }
  return null;
}

export function nearbyAvatars(avatars: Avatar[], point: Point, radius: number): Avatar[] {
  return avatars.filter((avatar) => {
    const dx = avatar.position.x - point.x;
    const dy = avatar.position.y - point.y;
    return Math.sqrt(dx * dx + dy * dy) <= radius;
  });
}

export function interpolateTrack(progress: number, laneOffset: number): Point {
  const clamped = Math.max(0, Math.min(1, progress));
  const scaled = clamped * (TRACK_POINTS.length - 1);
  const index = Math.min(TRACK_POINTS.length - 2, Math.floor(scaled));
  const local = scaled - index;
  const start = TRACK_POINTS[index];
  const end = TRACK_POINTS[index + 1];
  return {
    x: start.x + (end.x - start.x) * local,
    y: start.y + (end.y - start.y) * local + laneOffset
  };
}
