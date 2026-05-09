import { useEffect, useRef, useState } from "react";
import { Application, Container, Graphics, Text, TextStyle } from "pixi.js";

import {
  Avatar,
  MOCK_TRAINS,
  Station,
  STATIONS,
  TRACK_POINTS,
  Train,
  WORLD_HEIGHT,
  WORLD_WIDTH,
  interpolateTrack
} from "./world";

type RailwayCanvasProps = {
  mode: "display" | "controller";
  avatars: Avatar[];
  trains?: Train[];
  focusUserId?: string;
};

const labelStyle = new TextStyle({
  fill: 0x334155,
  fontFamily: "Inter, ui-sans-serif, system-ui",
  fontSize: 20,
  fontWeight: "700"
});

const smallLabelStyle = new TextStyle({
  fill: 0x64748b,
  fontFamily: "Inter, ui-sans-serif, system-ui",
  fontSize: 14,
  fontWeight: "600"
});

const whiteNumberStyle = new TextStyle({
  fill: 0xffffff,
  fontFamily: "Inter, ui-sans-serif, system-ui",
  fontSize: 30,
  fontWeight: "700"
});

const focusedNameStyle = new TextStyle({
  fill: 0x0f172a,
  fontFamily: "Inter, ui-sans-serif, system-ui",
  fontSize: 14,
  fontWeight: "600"
});

export function RailwayCanvas({ mode, avatars, trains = MOCK_TRAINS, focusUserId }: RailwayCanvasProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);

  useEffect(() => {
    setRenderError(null);
    const container = containerRef.current;
    if (!container) {
      return;
    }
    const host: HTMLDivElement = container;

    let disposed = false;
    let app: Application | null = null;

    async function mount() {
      try {
        app = new Application();
        await app.init({
          resizeTo: host,
          antialias: true,
          backgroundAlpha: 0
        });
        if (disposed || app === null) {
          return;
        }

        host.replaceChildren(app.canvas);
        const world = new Container();
        app.stage.addChild(world);

        const focus = avatars.find((avatar) => avatar.id === focusUserId) ?? avatars[0];
        const viewportWidth = host.clientWidth || 1;
        const viewportHeight = host.clientHeight || 1;
        const scale =
          mode === "display"
            ? Math.min(viewportWidth / WORLD_WIDTH, viewportHeight / WORLD_HEIGHT)
            : Math.max(0.78, Math.min(1.1, viewportWidth / 740));

        world.scale.set(scale);
        if (mode === "display") {
          world.position.set((viewportWidth - WORLD_WIDTH * scale) / 2, (viewportHeight - WORLD_HEIGHT * scale) / 2);
        } else {
          world.position.set(viewportWidth / 2 - focus.position.x * scale, viewportHeight / 2 - focus.position.y * scale);
        }

        drawBackdrop(world);
        drawTrack(world);
        STATIONS.forEach((station, index) => drawStation(world, station, index + 1));
        trains.forEach((train, index) => drawTrain(world, train, index));
        avatars.forEach((avatar) => drawAvatar(world, avatar, avatar.id === focusUserId));
      } catch (error) {
        setRenderError(error instanceof Error ? error.message : "Pixi renderer failed");
      }
    }

    void mount();

    return () => {
      disposed = true;
      if (app) {
        try {
          app.destroy(true, { children: true });
        } catch {
          // Pixi cleanup can race with Vite/React dev remounts; the next mount recreates the canvas.
        }
      }
    };
  }, [avatars, focusUserId, mode, trains]);

  return (
    <div className="railway-canvas" ref={containerRef}>
      {renderError ? <div className="canvas-error">Canvas failed to render: {renderError}</div> : null}
    </div>
  );
}

function drawBackdrop(world: Container) {
  const backdrop = new Graphics();
  backdrop
    .rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
    .fill({ color: 0xf8fbff })
    .stroke({ color: 0xe5eef7, width: 2 });

  for (let x = -200; x < WORLD_WIDTH + 200; x += 180) {
    backdrop.moveTo(x, 0).lineTo(x + 540, WORLD_HEIGHT).stroke({ color: 0xdbe8f3, width: 1, alpha: 0.55 });
  }
  for (let y = 90; y < WORLD_HEIGHT; y += 150) {
    backdrop.moveTo(0, y).lineTo(WORLD_WIDTH, y - 90).stroke({ color: 0xe3edf7, width: 1, alpha: 0.7 });
  }
  world.addChild(backdrop);
}

function drawTrack(world: Container) {
  const bed = new Graphics();
  bed.moveTo(TRACK_POINTS[0].x, TRACK_POINTS[0].y);
  TRACK_POINTS.slice(1).forEach((point) => bed.lineTo(point.x, point.y));
  bed.stroke({ color: 0xc7d7e8, width: 32, alpha: 0.9 });
  world.addChild(bed);

  const rail = new Graphics();
  rail.moveTo(TRACK_POINTS[0].x, TRACK_POINTS[0].y - 7);
  TRACK_POINTS.slice(1).forEach((point) => rail.lineTo(point.x, point.y - 7));
  rail.stroke({ color: 0x42566f, width: 4, alpha: 0.85 });
  rail.moveTo(TRACK_POINTS[0].x, TRACK_POINTS[0].y + 7);
  TRACK_POINTS.slice(1).forEach((point) => rail.lineTo(point.x, point.y + 7));
  rail.stroke({ color: 0x42566f, width: 4, alpha: 0.85 });
  world.addChild(rail);

  for (let i = 0; i < TRACK_POINTS.length - 1; i += 1) {
    const start = TRACK_POINTS[i];
    const end = TRACK_POINTS[i + 1];
    for (let t = 0; t < 1; t += 0.22) {
      const x = start.x + (end.x - start.x) * t;
      const y = start.y + (end.y - start.y) * t;
      const tie = new Graphics();
      tie.rect(-3, -16, 6, 32).fill({ color: 0x6c7f94, alpha: 0.55 });
      tie.position.set(x, y);
      tie.rotation = Math.atan2(end.y - start.y, end.x - start.x) + Math.PI / 2;
      world.addChild(tie);
    }
  }
}

function drawStation(world: Container, station: Station, number: number) {
  const platform = new Graphics();
  platform
    .roundRect(-110, -56, 220, 112, 18)
    .fill({ color: 0xffffff, alpha: 0.96 })
    .stroke({ color: station.color, width: 5, alpha: 0.85 });
  platform.position.set(station.position.x, station.position.y);
  world.addChild(platform);

  const building = new Graphics();
  building
    .roundRect(-54, -92, 108, 112, 16)
    .fill({ color: 0xf8fafc })
    .stroke({ color: station.color, width: 4, alpha: 0.8 })
    .rect(-32, -60, 64, 46)
    .fill({ color: station.color, alpha: 0.18 })
    .stroke({ color: station.color, width: 2, alpha: 0.65 });
  building.position.set(station.position.x, station.position.y);
  world.addChild(building);

  const pin = new Graphics();
  pin.circle(0, 0, 34).fill({ color: station.color }).stroke({ color: 0xffffff, width: 5 });
  pin.moveTo(-14, 26).lineTo(0, 58).lineTo(14, 26).fill({ color: station.color });
  pin.position.set(station.position.x, station.position.y - 150);
  world.addChild(pin);

  const numberText = new Text({ text: String(number), style: whiteNumberStyle });
  numberText.anchor.set(0.5);
  numberText.position.set(station.position.x, station.position.y - 151);
  world.addChild(numberText);

  const label = new Text({ text: station.label, style: labelStyle });
  label.anchor.set(0.5);
  label.position.set(station.position.x, station.position.y + 78);
  world.addChild(label);

  const description = new Text({ text: station.description, style: smallLabelStyle });
  description.anchor.set(0.5);
  description.position.set(station.position.x, station.position.y + 104);
  world.addChild(description);
}

function drawTrain(world: Container, train: Train, index: number) {
  const point = interpolateTrack(train.progress, (index % 4) * 10 - 15);
  const trainBody = new Graphics();
  trainBody.roundRect(-46, -17, 92, 34, 16).fill({ color: 0xffffff }).stroke({ color: train.color, width: 5 });
  trainBody.roundRect(-32, -9, 24, 18, 5).fill({ color: train.color, alpha: 0.24 });
  trainBody.roundRect(4, -9, 24, 18, 5).fill({ color: train.color, alpha: 0.24 });
  trainBody.position.set(point.x, point.y);
  world.addChild(trainBody);
}

function drawAvatar(world: Container, avatar: Avatar, focused: boolean) {
  const shadow = new Graphics();
  shadow.ellipse(0, 22, 22, 8).fill({ color: 0x94a3b8, alpha: 0.35 });
  shadow.position.set(avatar.position.x, avatar.position.y);
  world.addChild(shadow);

  const body = new Graphics();
  body.circle(0, -18, 15).fill({ color: avatar.color }).stroke({ color: 0xffffff, width: focused ? 5 : 3 });
  body.roundRect(-13, -2, 26, 42, 12).fill({ color: avatar.color, alpha: 0.9 }).stroke({ color: 0xffffff, width: focused ? 5 : 3 });
  body.position.set(avatar.position.x, avatar.position.y);
  world.addChild(body);

  const name = new Text({ text: avatar.name, style: focused ? focusedNameStyle : smallLabelStyle });
  name.anchor.set(0.5);
  name.position.set(avatar.position.x, avatar.position.y + 58);
  world.addChild(name);
}
