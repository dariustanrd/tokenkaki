# TB5/TB6 Plan: Realtime Railway UI

## Summary
Build the hackathon UI as a realtime inference railway client on top of the
existing demo trace, station, explanation, and benchmark endpoints.

The shared display shows the full isometric railway world: stations, active
trains, and all user avatars. Each phone acts primarily as a controller: users
move a free-roaming avatar, submit prompts, see nearby avatars, and tap an
interact button at stations to inspect eligible runs. Chat appears only from a
station interaction.

This plan refines the current hackathon plan's TB5 and TB6. The implementation
should remain demo-scoped and keep `tokenkaki.gateway` as the only backend
runtime service.

## Key Decisions
- Frontend: Vite, React, TypeScript, and PixiJS.
- Backend realtime: FastAPI WebSocket room state, plus existing HTTP endpoints
  for run submission, station facts, benchmark references, and station
  explanations.
- Movement: free avatar movement, clamped to map bounds.
- Interaction: station cards open only after the user taps an interact button
  inside a station radius.
- Phones show own avatar, immediate surroundings, nearby avatars, prompt
  controls, eligible station cards, and station chat.
- Shared display shows the whole map, all avatars, all active trains, and no
  chat.
- Target scale: 10 concurrent users in one room.
- Multiple trains per user are allowed; visually stacking or overlap is
  acceptable for hackathon energy.
- Generated assets are committed to the repo and overlaid with live PixiJS text
  and state. Do not bake station labels, numbers, metrics, or user text into
  generated images.

## Repo Integration
- Add frontend under `web/railway-demo/`, not under top-level `services/`.
- Keep generated or final raster assets under
  `web/railway-demo/public/assets/railway/`.
- Add demo realtime backend code under `src/tokenkaki/demo/`, keeping it
  process-local and in-memory for v1.
- Mount demo WebSocket and static/demo routes from `tokenkaki.gateway`.
- Existing completed and pending demo APIs remain the source of truth:
  - `GET /demo/runs/{request_id}`
  - `GET /demo/runs/{request_id}/stations/{station}`
  - `POST /demo/runs/{request_id}/stations/{station}/explain`
  - `GET /demo/benchmarks/latest`

## Tracer-Bullet Slices
1. **TB5.1: Static Railway World**
   - Dependency: none beyond existing repo.
   - Add the Vite/React/PixiJS app scaffold.
   - Render a full shared-display map with five fixed station zones:
     Gateway, Queue, Prefill, Decode, Metrics.
   - Render a phone controller view with the same coordinate system but a
     camera cropped around the current avatar.
   - Use placeholder shapes first, then replace with committed generated
     isometric assets matching the attached pale technical railway style.
   - Demoable result: shared display and phone view show the same station map.

2. **TB5.2: Realtime Room And Avatar Sync**
   - Dependency: TB5.1.
   - Add in-memory room state for one demo session with up to 10 users.
   - Add a WebSocket endpoint for joining a room, sending avatar movement, and
     broadcasting throttled avatar positions.
   - Backend clamps positions to the map bounds and broadcasts nearby users to
     controllers while the shared display receives all users.
   - Demoable result: multiple phones move avatars freely and the shared screen
     shows all movement.

3. **TB5.3: Prompt Submit Creates Trains**
   - Dependency: existing trace ticket path plus TB5.2.
   - Phone submits prompts through the gateway with `x-tokenkaki-session-id` and
     `x-tokenkaki-user-id`.
   - Each accepted request becomes a train keyed by `request_id`.
   - WebSocket broadcasts `run_created` and `train_position` updates.
   - Multiple active or completed trains per user are allowed.
   - Demoable result: submitting prompts creates visible trains on the shared
     track while the underlying model request remains real.

4. **TB5.4: Live Motion And Slow Replay**
   - Dependency: TB5.3.
   - Live mode moves trains using real trace timing where available.
   - Learning mode replays saved trace timing at a slower fixed scale for
     station inspection.
   - Unlock stations only after the train reaches that station for the selected
     run. If the newest run has not reached a station, the phone may offer older
     completed runs eligible for that station.
   - Demoable result: a fast real request can still be inspected slowly without
     changing the recorded trace.

5. **TB5.5: Station Proximity And Inspect Flow**
   - Dependency: TB5.4.
   - Phone shows an interact button only inside a station radius.
   - Tapping interact fetches station facts for the selected eligible run.
   - Station card displays live trace facts, `measurement_basis`, benchmark
     reference metrics, and explicit provenance labels.
   - Demoable result: one user can walk to all five stations and inspect the
     same run through each station lens.

6. **TB5.6: Station Conversation**
   - Dependency: TB5.5 and existing explanation endpoint.
   - Chat panel appears only after station interaction.
   - Send capped local station conversation history to the existing grounded
     explanation endpoint.
   - Keep the station facts visible next to the answer so the user can see what
     evidence the base model used.
   - Demoable result: the phone acts like a controller most of the time, then
     becomes a station-specific explainer when the user asks.

7. **TB5.7: Asset Pass And Demo Polish**
   - Dependency: TB5.1 through TB5.6.
   - Commit generated assets:
     - `backdrop.png`
     - `station-gateway.png`
     - `station-queue.png`
     - `station-prefill.png`
     - `station-decode.png`
     - `station-metrics.png`
     - `train.png`
     - `avatar-set.png`
     - `asset-manifest.json`
   - Overlay dynamic station names, labels, user IDs, train state, and metrics
     in PixiJS rather than embedding text in images.
   - Add a simple QR/join route and display-session URL.
   - Demoable result: the UI matches the intended isometric railway style while
     remaining data-driven.

## Realtime Message Contract
Initial WebSocket messages should stay small and explicit:

```json
{ "type": "join", "session_id": "demo-001", "user_id": "user-7", "role": "controller" }
{ "type": "avatar_move", "x": 420, "y": 310, "vx": 0.4, "vy": -0.1 }
{ "type": "avatar_position", "user_id": "user-7", "x": 420, "y": 310 }
{ "type": "run_created", "request_id": "req-123", "user_id": "user-7" }
{ "type": "train_position", "request_id": "req-123", "station": "prefill", "progress": 0.45 }
{ "type": "station_unlocked", "request_id": "req-123", "station": "prefill" }
{ "type": "run_completed", "request_id": "req-123", "status": "completed" }
```

HTTP remains responsible for heavier or request/response interactions:

```text
POST /v1/chat/completions
GET  /demo/runs/{request_id}
GET  /demo/runs/{request_id}/stations/{station}
POST /demo/runs/{request_id}/stations/{station}/explain
GET  /demo/benchmarks/latest
```

## Test Plan
- Backend tests:
  - room join and leave
  - avatar position clamp and broadcast
  - nearby-avatar filtering for phone controllers
  - all-avatar broadcast for shared display
  - train creation from trace IDs
  - station unlock ordering
- Frontend checks:
  - shared display renders map, stations, avatars, and trains
  - phone controller moves avatar and sees nearby users
  - prompt submit creates a visible train
  - station interact button appears only inside a station radius
  - station facts and explanation render with provenance labels
- Acceptance demo:
  - 10 browser clients can join one room.
  - At least one real model request creates a visible train.
  - The train moves live, can be replayed slowly, and unlocks all five stations.
  - A phone can inspect a station and receive a grounded base-model answer.

## Assumptions
- The frontend is a hackathon demo client, not a new production service.
- In-memory room state is acceptable for one gateway process and one hackathon
  room.
- Active train count remains gateway-observed and must not be described as vLLM
  internal queue depth.
- Train segment timing is driven by trace events where available and labeled as
  inferred when it maps gateway timing onto conceptual prefill/decode stations.
- Generated images are used as visual assets only; all live labels and metrics
  are rendered by the app.
