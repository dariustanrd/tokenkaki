import { FormEvent, useMemo, useState } from "react";

import {
  StationExplanation,
  StationFacts,
  TraceTicket,
  explainStation,
  fetchStationFacts,
  fetchTrace,
  gatewayBaseUrl,
  submitStreamingChat
} from "./api/tokenkaki";
import { RailwayCanvas } from "./map/RailwayCanvas";
import { Avatar, INITIAL_AVATARS, STATIONS, Train, clampToWorld, nearbyAvatars, nearestStation } from "./map/world";

type ViewMode = "display" | "controller";

const STEP = 38;
const SESSION_ID = "hackathon-demo";
const USER_ID = "user-1";
const MODEL = "qwen3-8b";

type RunState = {
  requestId: string;
  prompt: string;
  answer: string;
  status: "running" | "completed" | "failed";
  trace?: TraceTicket;
  error?: string;
};

export function App() {
  const initialMode: ViewMode = window.location.pathname.includes("controller") ? "controller" : "display";
  const [mode, setMode] = useState<ViewMode>(initialMode);
  const [avatars, setAvatars] = useState<Avatar[]>(INITIAL_AVATARS);
  const [prompt, setPrompt] = useState("Explain what continuous batching means in one short paragraph.");
  const [runs, setRuns] = useState<RunState[]>([]);
  const [trains, setTrains] = useState<Train[]>([]);
  const [selectedStationFacts, setSelectedStationFacts] = useState<StationFacts | null>(null);
  const [stationExplanation, setStationExplanation] = useState<StationExplanation | null>(null);
  const [stationQuestion, setStationQuestion] = useState("Explain this station for a beginner.");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const currentUser = avatars[0];
  const station = nearestStation(currentUser.position);
  const nearby = useMemo(() => nearbyAvatars(avatars.slice(1), currentUser.position, 210), [avatars, currentUser.position]);
  const latestCompletedRun = [...runs].reverse().find((run) => run.status === "completed");
  const latestRun = runs[runs.length - 1];

  function move(dx: number, dy: number) {
    setAvatars((current) =>
      current.map((avatar, index) =>
        index === 0
          ? {
              ...avatar,
              position: clampToWorld({ x: avatar.position.x + dx, y: avatar.position.y + dy })
            }
          : avatar
      )
    );
  }

  async function submitPrompt(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!prompt.trim() || busy) {
      return;
    }

    const requestId = `railway-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
    const nextRun: RunState = {
      requestId,
      prompt,
      answer: "",
      status: "running"
    };
    setRuns((current) => [...current, nextRun]);
    setTrains((current) => [...current, { id: requestId, userId: USER_ID, color: currentUser.color, progress: 0.12 }]);
    setSelectedStationFacts(null);
    setStationExplanation(null);
    setError(null);
    setBusy(true);

    try {
      const result = await submitStreamingChat(
        {
          requestId,
          sessionId: SESSION_ID,
          userId: USER_ID,
          model: MODEL,
          prompt
        },
        (chunk) => {
          setRuns((current) =>
            current.map((run) => (run.requestId === requestId ? { ...run, answer: `${run.answer}${chunk}` } : run))
          );
          setTrains((current) =>
            current.map((train) =>
              train.id === requestId ? { ...train, progress: Math.min(0.86, train.progress + 0.035) } : train
            )
          );
        }
      );
      const trace = await fetchTrace(requestId);
      setRuns((current) =>
        current.map((run) =>
          run.requestId === requestId
            ? {
                ...run,
                answer: result.answer || run.answer,
                status: "completed",
                trace
              }
            : run
        )
      );
      setTrains((current) => current.map((train) => (train.id === requestId ? { ...train, progress: 1 } : train)));
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "request failed";
      setError(message);
      setRuns((current) => current.map((run) => (run.requestId === requestId ? { ...run, status: "failed", error: message } : run)));
      setTrains((current) => current.map((train) => (train.id === requestId ? { ...train, progress: 1 } : train)));
    } finally {
      setBusy(false);
    }
  }

  async function inspectStation() {
    if (!station || !latestCompletedRun) {
      return;
    }

    setError(null);
    setStationExplanation(null);
    try {
      const facts = await fetchStationFacts(latestCompletedRun.requestId, station.id);
      setSelectedStationFacts(facts);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "station lookup failed");
    }
  }

  async function askStation() {
    if (!selectedStationFacts) {
      return;
    }
    setError(null);
    try {
      const explanation = await explainStation(
        selectedStationFacts.request_id,
        selectedStationFacts.station,
        stationQuestion,
        stationExplanation
          ? [
              { role: "user", content: stationQuestion },
              { role: "assistant", content: stationExplanation.explanation }
            ]
          : []
      );
      setStationExplanation(explanation);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "station explanation failed");
    }
  }

  return (
    <main className={`app-shell app-shell--${mode}`}>
      <section className="topbar">
        <div>
          <p className="eyebrow">TokenKaki Hackathon Demo</p>
          <h1>Inference Railway</h1>
        </div>
        <div className="mode-switch" aria-label="View mode">
          <button className={mode === "display" ? "active" : ""} onClick={() => setMode("display")}>
            Shared display
          </button>
          <button className={mode === "controller" ? "active" : ""} onClick={() => setMode("controller")}>
            Phone controller
          </button>
        </div>
      </section>

      <section className="stage">
        <RailwayCanvas mode={mode} avatars={avatars} trains={trains} focusUserId={USER_ID} />
        {mode === "controller" ? (
          <ControllerPanel
            stationName={station?.label ?? null}
            nearbyNames={nearby.map((avatar) => avatar.name)}
            prompt={prompt}
            busy={busy}
            latestRun={latestRun}
            latestCompletedRun={latestCompletedRun}
            selectedStationFacts={selectedStationFacts}
            stationQuestion={stationQuestion}
            stationExplanation={stationExplanation}
            error={error}
            onPromptChange={setPrompt}
            onStationQuestionChange={setStationQuestion}
            onSubmitPrompt={submitPrompt}
            onInspectStation={inspectStation}
            onAskStation={askStation}
            onMove={move}
          />
        ) : (
          <DisplayLegend runCount={runs.length} gatewayBase={gatewayBaseUrl()} />
        )}
      </section>
    </main>
  );
}

type ControllerPanelProps = {
  stationName: string | null;
  nearbyNames: string[];
  prompt: string;
  busy: boolean;
  latestRun?: RunState;
  latestCompletedRun?: RunState;
  selectedStationFacts: StationFacts | null;
  stationQuestion: string;
  stationExplanation: StationExplanation | null;
  error: string | null;
  onPromptChange: (value: string) => void;
  onStationQuestionChange: (value: string) => void;
  onSubmitPrompt: (event: FormEvent<HTMLFormElement>) => void;
  onInspectStation: () => void;
  onAskStation: () => void;
  onMove: (dx: number, dy: number) => void;
};

function ControllerPanel({
  stationName,
  nearbyNames,
  prompt,
  busy,
  latestRun,
  latestCompletedRun,
  selectedStationFacts,
  stationQuestion,
  stationExplanation,
  error,
  onPromptChange,
  onStationQuestionChange,
  onSubmitPrompt,
  onInspectStation,
  onAskStation,
  onMove
}: ControllerPanelProps) {
  return (
    <aside className="controller-panel" aria-label="Phone controller">
      <form className="controller-card prompt-card" onSubmit={onSubmitPrompt}>
        <p className="card-label">Real vLLM request</p>
        <h2>Launch a train</h2>
        <textarea value={prompt} onChange={(event) => onPromptChange(event.target.value)} rows={4} />
        <button className="primary-button" disabled={busy || !prompt.trim()}>
          {busy ? "Running through TokenKaki..." : "Submit prompt"}
        </button>
        {latestRun ? (
          <p className="run-status">
            Latest train: <strong>{latestRun.status}</strong> <code>{latestRun.requestId}</code>
          </p>
        ) : null}
      </form>

      <div className="controller-card">
        <p className="card-label">Controller</p>
        <h2>{stationName ? `${stationName} station` : "Explore the railway"}</h2>
        <p className="card-copy">
          {stationName
            ? latestCompletedRun
              ? "Tap Interact to inspect this station for your latest completed real run."
              : "You are inside a station radius. Submit and complete a real run before station facts unlock."
            : "Move your avatar near a station. The shared display keeps the full world view."}
        </p>
        <button className="interact-button" disabled={!stationName || !latestCompletedRun} onClick={onInspectStation}>
          Interact
        </button>
      </div>

      <div className="dpad" aria-label="Avatar movement controls">
        <button onClick={() => onMove(0, -STEP)} aria-label="Move up">
          ↑
        </button>
        <button onClick={() => onMove(-STEP, 0)} aria-label="Move left">
          ←
        </button>
        <button onClick={() => onMove(STEP, 0)} aria-label="Move right">
          →
        </button>
        <button onClick={() => onMove(0, STEP)} aria-label="Move down">
          ↓
        </button>
      </div>

      <div className="nearby">
        <p className="card-label">Nearby avatars</p>
        <p>{nearbyNames.length > 0 ? nearbyNames.join(", ") : "No one nearby yet."}</p>
      </div>

      {selectedStationFacts ? (
        <div className="station-panel">
          <p className="card-label">Station facts</p>
          <h2>{selectedStationFacts.title}</h2>
          <p>
            Basis: <strong>{selectedStationFacts.measurement_basis}</strong>
          </p>
          <FactList facts={selectedStationFacts.facts} />
          {selectedStationFacts.reference_metrics ? (
            <>
              <p className="card-label">Benchmark reference</p>
              <FactList facts={selectedStationFacts.reference_metrics} compact />
            </>
          ) : null}
          <textarea
            value={stationQuestion}
            onChange={(event) => onStationQuestionChange(event.target.value)}
            rows={3}
            aria-label="Station question"
          />
          <button className="primary-button" onClick={onAskStation}>
            Ask station
          </button>
          {stationExplanation ? <p className="explanation">{stationExplanation.explanation}</p> : null}
        </div>
      ) : null}

      {latestRun?.answer ? (
        <div className="station-panel answer-panel">
          <p className="card-label">Model answer</p>
          <p>{latestRun.answer}</p>
        </div>
      ) : null}

      {error ? <p className="error-message">{error}</p> : null}
    </aside>
  );
}

function DisplayLegend({ runCount, gatewayBase }: { runCount: number; gatewayBase: string }) {
  return (
    <aside className="display-legend">
      <p className="card-label">Real gateway integration</p>
      <h2>Shared railway world</h2>
      <p>
        Controller prompts call TokenKaki through the Vite proxy at <code>{gatewayBase}</code>. Completed requests become trains
        with station facts from the gateway trace store.
      </p>
      <p>
        Active session trains: <strong>{runCount}</strong>
      </p>
      <ol>
        {STATIONS.map((station) => (
          <li key={station.id}>{station.label}</li>
        ))}
      </ol>
    </aside>
  );
}

function FactList({ facts, compact = false }: { facts: Record<string, unknown>; compact?: boolean }) {
  return (
    <dl className={compact ? "fact-list fact-list--compact" : "fact-list"}>
      {Object.entries(facts).map(([key, value]) => (
        <div key={key}>
          <dt>{key}</dt>
          <dd>{formatValue(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "not available";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}
