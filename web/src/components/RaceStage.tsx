/**
 * RaceStage Component (Vanilla PixiJS + React)
 * 
 * Uses vanilla PixiJS with React useRef pattern for maximum control
 * and compatibility with PixiJS v8.
 */

import { useEffect, useRef } from 'react';
import { Application, Graphics, Container, Text, TextStyle } from 'pixi.js';
import { parseGenome, buildTurtleLayers } from '../lib/paperDoll';
import { lerp } from '../lib/interpolation';
import type { TurtleState } from '../types';

import type { BufferedSnapshot } from '../hooks/useRaceSocket';

export interface RaceStageProps {
    snapshotBuffer: BufferedSnapshot[];
    trackLength: number;
    width?: number;
    height?: number;
}

const DEFAULT_WIDTH = 800;
const DEFAULT_HEIGHT = 400;
const TRACK_MARGIN = 50;
const TURTLE_SIZE = 30;
// No longer need fixed broadcast interval for buffered interpolation
// const BROADCAST_INTERVAL_MS = 33.33; 

// Buffer delay in milliseconds (Server Authority "Memory")
const RENDER_DELAY_MS = 100;

export function RaceStage({
    snapshotBuffer,
    trackLength,
    width = DEFAULT_WIDTH,
    height = DEFAULT_HEIGHT,
}: RaceStageProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const appRef = useRef<Application | null>(null);
    const turtleContainerRef = useRef<Container | null>(null);
    const animationFrameRef = useRef<number>(0);

    // Initialize PixiJS application
    useEffect(() => {
        if (!containerRef.current) return;

        let isMounted = true;
        const app = new Application();

        const initApp = async () => {
            await app.init({
                width,
                height,
                backgroundColor: 0x1a1a1a,
                antialias: true,
                roundPixels: false, // Critical for smooth sub-pixel movement
            });

            if (!isMounted) {
                // Component unmounted during init
                app.destroy(true, { children: true });
                return;
            }

            if (containerRef.current) {
                // Double-safety: Clear container
                while (containerRef.current.firstChild) {
                    containerRef.current.removeChild(containerRef.current.firstChild);
                }
                containerRef.current.appendChild(app.canvas);
            }

            // Draw track background
            const trackGraphics = new Graphics();
            drawTrack(trackGraphics, width, height);
            app.stage.addChild(trackGraphics);

            // Create turtle container
            const turtleContainer = new Container();
            app.stage.addChild(turtleContainer);
            turtleContainerRef.current = turtleContainer;

            appRef.current = app;
        };

        initApp();

        return () => {
            isMounted = false;
            if (appRef.current) {
                appRef.current.destroy(true, { children: true });
                appRef.current = null;
            }
        };
    }, [width, height]);

    // Animation loop for BUFFERED interpolation
    useEffect(() => {
        const animate = () => {
            if (!turtleContainerRef.current) {
                animationFrameRef.current = requestAnimationFrame(animate);
                return;
            }

            // Calculate "Render Time" (100ms in the past)
            const now = performance.now();
            const renderTime = now - RENDER_DELAY_MS;

            // Find bracketing snapshots in buffer
            // We need: prev.receivedAt <= renderTime < next.receivedAt
            let prevSnapshot: BufferedSnapshot | null = null;
            let nextSnapshot: BufferedSnapshot | null = null;

            // Iterate backwards to find the latest snapshot that is older than renderTime
            // Buffer is sorted by receivedAt (oldest first)
            for (let i = snapshotBuffer.length - 1; i >= 0; i--) {
                const s = snapshotBuffer[i];
                if (s.receivedAt <= renderTime) {
                    prevSnapshot = s;
                    // The next one in the array (if exists) is our target
                    if (i + 1 < snapshotBuffer.length) {
                        nextSnapshot = snapshotBuffer[i + 1];
                    }
                    break;
                }
            }

            // Fallback: If we haven't received enough data yet (buffer underflow),
            // or if we are way behind, just use the latest available snapshot?
            // "Loose Jitter" fix: Strict adherence to buffer. If undefined, hold position.

            // If we have a valid bracket, interpolate
            if (prevSnapshot && nextSnapshot) {
                const totalDuration = nextSnapshot.receivedAt - prevSnapshot.receivedAt;
                const elapsed = renderTime - prevSnapshot.receivedAt;
                // Clamp t between 0 and 1 to prevent severe overshoots
                const t = Math.max(0, Math.min(1, elapsed / totalDuration));

                // Clear and redraw
                turtleContainerRef.current.removeChildren();
                const trackWidth = width - TRACK_MARGIN * 2;

                nextSnapshot.turtles.forEach((turtle, index) => {
                    // Find corresponding turtle in prevSnapshot
                    const prevTurtle = prevSnapshot!.turtles.find(pt => pt.id === turtle.id);

                    // If turtle existed in previous frame, lerp. Else snap.
                    // Also handle course change / teleportation check if needed (but buffer flush handles that)
                    const prevX = prevTurtle ? prevTurtle.x : turtle.x;
                    const interpolatedX = lerp(prevX, turtle.x, t);

                    const screenX = TRACK_MARGIN + (interpolatedX / trackLength) * trackWidth;
                    const screenY = 80 + index * 60;

                    const turtleGraphics = drawTurtle(
                        // Create a synthetic state for rendering (interpolated)
                        { ...turtle, current_energy: lerp(prevTurtle?.current_energy ?? turtle.current_energy, turtle.current_energy, t) },
                        TURTLE_SIZE
                    );
                    turtleGraphics.position.set(screenX, screenY);
                    turtleContainerRef.current!.addChild(turtleGraphics);
                });
            } else if (snapshotBuffer.length > 0) {
                // Optimization: If only 1 snapshot or waiting for next, draw latest (or hold)
                // For now, drawing latest in buffer to avoid blank screen, but purely static
                // This effectively "pauses" until buffer fills
                const latest = snapshotBuffer[snapshotBuffer.length - 1];
                turtleContainerRef.current.removeChildren();
                const trackWidth = width - TRACK_MARGIN * 2;

                latest.turtles.forEach((turtle, index) => {
                    const screenX = TRACK_MARGIN + (turtle.x / trackLength) * trackWidth;
                    const screenY = 80 + index * 60;
                    const turtleGraphics = drawTurtle(turtle, TURTLE_SIZE);
                    turtleGraphics.position.set(screenX, screenY);
                    turtleContainerRef.current!.addChild(turtleGraphics);
                });
            }

            animationFrameRef.current = requestAnimationFrame(animate);
        };

        animationFrameRef.current = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrameRef.current);
    }, [snapshotBuffer, trackLength, width]); // Dependency is solely the buffer now

    return <div ref={containerRef} className="race-stage" />;
}

function drawTrack(g: Graphics, width: number, height: number): void {
    // Track background
    g.rect(0, 0, width, height);
    g.fill(0x2d2d2d);

    // Lane lines
    for (let i = 0; i < 3; i++) {
        const laneY = 60 + i * 60;
        g.rect(TRACK_MARGIN, laneY, width - TRACK_MARGIN * 2, 50);
        g.fill({ color: 0x3a3a3a, alpha: 0.3 });
    }

    // Start line
    g.moveTo(TRACK_MARGIN, 40);
    g.lineTo(TRACK_MARGIN, height - 20);
    g.stroke({ width: 3, color: 0xFFFFFF });

    // Finish line
    const finishX = width - TRACK_MARGIN;
    for (let i = 0; i < 10; i++) {
        const y = 40 + i * ((height - 60) / 10);
        g.rect(finishX - 5, y, 10, (height - 60) / 10);
        g.fill(i % 2 === 0 ? 0xFFFFFF : 0x000000);
    }
}

function drawTurtle(turtle: TurtleState, size: number): Container {
    const container = new Container();
    const g = new Graphics();

    const parsedGenome = parseGenome(turtle.genome);
    const layers = buildTurtleLayers(parsedGenome);

    // Body (ellipse)
    g.ellipse(0, 0, size * 0.6, size * 0.4);
    g.fill(layers.body.tint);

    // Shell (circle)
    g.circle(0, -size * 0.1, size * 0.35);
    g.fill(layers.shell.tint);

    // Head
    g.circle(size * 0.5, 0, size * 0.15);
    g.fill(layers.limbs.tint);

    // Eyes
    g.circle(size * 0.55, -size * 0.05, size * 0.06);
    g.fill(0xFFFFFF);
    g.circle(size * 0.57, -size * 0.05, size * 0.03);
    g.fill(0x000000);

    // Flippers
    const limbPositions = [
        { x: -size * 0.3, y: size * 0.2 },
        { x: size * 0.2, y: size * 0.2 },
        { x: -size * 0.3, y: -size * 0.15 },
        { x: size * 0.2, y: -size * 0.15 },
    ];

    for (const limb of limbPositions) {
        g.ellipse(limb.x, limb.y, size * 0.12, size * 0.06);
        g.fill(layers.limbs.tint);
    }

    // Energy bar
    const barWidth = size * 0.8;
    const barHeight = 4;
    const barY = size * 0.5;
    const energyRatio = turtle.current_energy / turtle.max_energy;

    g.rect(-barWidth / 2, barY, barWidth, barHeight);
    g.fill({ color: 0x333333, alpha: 0.5 });

    const energyColor = energyRatio > 0.5 ? 0x22FF22 : energyRatio > 0.25 ? 0xFFFF22 : 0xFF2222;
    g.rect(-barWidth / 2, barY, barWidth * energyRatio, barHeight);
    g.fill(energyColor);

    // Resting indicator
    if (turtle.is_resting) {
        g.circle(0, -size * 0.6, size * 0.1);
        g.fill({ color: 0xFFFFFF, alpha: 0.8 });
    }

    // Finished indicator
    // Finished indicator (Rank based visualization)
    if (turtle.finished && turtle.rank) {
        let ringColor = 0xFFFFFF; // Default finish
        let ringWidth = 2;

        switch (turtle.rank) {
            case 1:
                ringColor = 0xFFD700; // Gold
                ringWidth = 4;
                // Winner Glow / Sunburst
                g.circle(0, 0, size * 0.9);
                g.fill({ color: 0xFFD700, alpha: 0.3 });
                g.circle(0, 0, size * 0.75);
                g.stroke({ width: 2, color: 0xFFD700, alpha: 0.6 });
                break;
            case 2:
                ringColor = 0xC0C0C0; // Silver
                ringWidth = 3;
                break;
            case 3:
                ringColor = 0xCD7F32; // Bronze
                ringWidth = 2;
                break;
        }

        g.circle(0, 0, size * 0.65);
        g.stroke({ width: ringWidth, color: ringColor });
    } else if (turtle.finished) {
        // Fallback if rank not yet assigned (rare)
        g.circle(0, 0, size * 0.6);
        g.stroke({ width: 2, color: 0xFFD700 });
    }

    container.addChild(g);

    // Name label
    const style = new TextStyle({
        fontSize: 10,
        fill: 0xFFFFFF,
        fontFamily: 'sans-serif',
    });
    const nameText = new Text({ text: turtle.name, style });
    nameText.position.set(-size * 0.4, -size * 0.9);
    container.addChild(nameText);

    return container;
}
