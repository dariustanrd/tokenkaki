import { StationId } from "../map/world";

const DEFAULT_GATEWAY_BASE = "/api";

export type ChatRunInput = {
  requestId: string;
  sessionId: string;
  userId: string;
  model: string;
  prompt: string;
};

export type TraceTicket = {
  request_id: string;
  session_id: string | null;
  user_id: string | null;
  model: string;
  backend_model: string;
  selected_backend: string;
  routing_policy: string;
  stream: boolean;
  status: "running" | "completed" | "failed";
  status_code: number | null;
  error_class: string | null;
  active_requests_at_start: number;
  streamed_chunk_count: number;
  timings_ms: {
    first_chunk: number | null;
    total: number | null;
  };
};

export type StationFacts = {
  request_id: string;
  station: StationId;
  title: string;
  measurement_basis: string;
  facts: Record<string, unknown>;
  reference_metrics?: Record<string, unknown>;
};

export type StationExplanation = {
  request_id: string;
  station: StationId;
  model: string;
  explanation: string;
  station_facts: StationFacts;
};

export type ChatRunResult = {
  requestId: string;
  answer: string;
};

export function gatewayBaseUrl(): string {
  return import.meta.env.VITE_TOKENKAKI_GATEWAY_BASE_URL ?? DEFAULT_GATEWAY_BASE;
}

export async function submitStreamingChat(input: ChatRunInput, onChunk?: (text: string) => void): Promise<ChatRunResult> {
  const response = await fetch(`${gatewayBaseUrl()}/v1/chat/completions`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-request-id": input.requestId,
      "x-tokenkaki-session-id": input.sessionId,
      "x-tokenkaki-user-id": input.userId
    },
    body: JSON.stringify({
      model: input.model,
      stream: true,
      messages: [{ role: "user", content: input.prompt }],
      temperature: 0,
      max_tokens: 180,
      chat_template_kwargs: { enable_thinking: false }
    })
  });

  if (!response.ok || !response.body) {
    throw new Error(await errorMessage(response, "chat completion failed"));
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const text = parseSseDelta(event);
      if (text) {
        answer += text;
        onChunk?.(text);
      }
    }
  }

  return { requestId: input.requestId, answer };
}

export async function fetchTrace(requestId: string): Promise<TraceTicket> {
  const response = await fetch(`${gatewayBaseUrl()}/demo/runs/${encodeURIComponent(requestId)}`);
  if (!response.ok) {
    throw new Error(await errorMessage(response, "trace lookup failed"));
  }
  return (await response.json()) as TraceTicket;
}

export async function fetchStationFacts(requestId: string, station: StationId): Promise<StationFacts> {
  const response = await fetch(
    `${gatewayBaseUrl()}/demo/runs/${encodeURIComponent(requestId)}/stations/${encodeURIComponent(station)}`
  );
  if (!response.ok) {
    throw new Error(await errorMessage(response, "station lookup failed"));
  }
  return (await response.json()) as StationFacts;
}

export async function explainStation(
  requestId: string,
  station: StationId,
  question: string,
  history: Array<{ role: "user" | "assistant"; content: string }>
): Promise<StationExplanation> {
  const response = await fetch(
    `${gatewayBaseUrl()}/demo/runs/${encodeURIComponent(requestId)}/stations/${encodeURIComponent(station)}/explain`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question, history })
    }
  );
  if (!response.ok) {
    throw new Error(await errorMessage(response, "station explanation failed"));
  }
  return (await response.json()) as StationExplanation;
}

function parseSseDelta(event: string): string {
  const dataLines = event
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice("data:".length).trim());

  let text = "";
  for (const data of dataLines) {
    if (!data || data === "[DONE]") {
      continue;
    }
    try {
      const payload = JSON.parse(data) as {
        choices?: Array<{ delta?: { content?: string } }>;
      };
      text += payload.choices?.[0]?.delta?.content ?? "";
    } catch {
      continue;
    }
  }
  return text;
}

async function errorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { error?: { message?: string } };
    return payload.error?.message ?? `${fallback}: ${response.status}`;
  } catch {
    return `${fallback}: ${response.status}`;
  }
}
