/**
 * RaceStage Component (Vanilla PixiJS + React)
 * 
 * Uses vanilla PixiJS with React useRef pattern for maximum control
 * and compatibility with PixiJS v8.
 */

import { useEffect, useRef } from 'react';
import { Application, Graphics, Container, Text, TextStyle } from 'pixi.js';
import { parseGenome, buildTurtleLayers } from '../lib/paperDoll';
import { lerp, getInterpolationFactor } from '../lib/interpolation';
import type { RaceSnapshot, TurtleState } from '../types';

export interface RaceStageProps {
    snapshot: RaceSnapshot | null;
    prevSnapshot: RaceSnapshot | null;
    trackLength: number;
    width?: number;
    height?: number;
}

const DEFAULT_WIDTH = 800;
const DEFAULT_HEIGHT = 400;
const TRACK_MARGIN = 50;
const TURTLE_SIZE = 30;
const BROADCAST_INTERVAL_MS = 33.33;

export function RaceStage({
    snapshot,
    prevSnapshot,
    trackLength,
    width = DEFAULT_WIDTH,
    height = DEFAULT_HEIGHT,
}: RaceStageProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const appRef = useRef<Application | null>(null);
    const turtleContainerRef = useRef<Container | null>(null);
    const lastSnapshotTimeRef = useRef<number>(0);
    const animationFrameRef = useRef<number>(0);

    // Initialize PixiJS application
    useEffect(() => {
        if (!containerRef.current) return;

        const app = new Application();

        const initApp = async () => {
            await app.init({
                width,
                height,
                backgroundColor: 0x1a1a1a,
                antialias: true,
            });

            if (containerRef.current) {
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
            if (appRef.current) {
                appRef.current.destroy(true, { children: true });
                appRef.current = null;
            }
        };
    }, [width, height]);

    // Track when new snapshot arrives
    useEffect(() => {
        if (snapshot) {
            lastSnapshotTimeRef.current = performance.now();
        }
    }, [snapshot?.tick]);

    // Animation loop for interpolation
    useEffect(() => {
        const animate = () => {
            if (!snapshot || !turtleContainerRef.current) {
                animationFrameRef.current = requestAnimationFrame(animate);
                return;
            }

            const now = performance.now();
            const timeSinceSnapshot = now - lastSnapshotTimeRef.current;
            const t = getInterpolationFactor(timeSinceSnapshot, BROADCAST_INTERVAL_MS);

            // Clear turtle container
            turtleContainerRef.current.removeChildren();

            // Map turtle positions to screen coordinates
            const trackWidth = width - TRACK_MARGIN * 2;

            snapshot.turtles.forEach((turtle, index) => {
                const prevTurtle = prevSnapshot?.turtles.find((pt) => pt.id === turtle.id);
                const prevX = prevTurtle?.x ?? turtle.x;
                const interpolatedX = lerp(prevX, turtle.x, t);

                const screenX = TRACK_MARGIN + (interpolatedX / trackLength) * trackWidth;
                const screenY = 80 + index * 60;

                const turtleGraphics = drawTurtle(turtle, TURTLE_SIZE);
                turtleGraphics.position.set(screenX, screenY);
                turtleContainerRef.current!.addChild(turtleGraphics);
            });

            animationFrameRef.current = requestAnimationFrame(animate);
        };

        animationFrameRef.current = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrameRef.current);
    }, [snapshot, prevSnapshot, trackLength, width]);

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
    if (turtle.finished) {
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
