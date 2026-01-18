/**
 * Interpolation utilities for smooth rendering.
 * 
 * Since server broadcasts at 30Hz but screen refreshes at 60Hz+,
 * we need to interpolate turtle positions between snapshots.
 */

/**
 * Linear interpolation between two values.
 * 
 * @param a - Start value
 * @param b - End value  
 * @param t - Interpolation factor (0-1)
 * @returns Interpolated value
 */
export function lerp(a: number, b: number, t: number): number {
    return a + (b - a) * t;
}

/**
 * Clamp a value between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
}

/**
 * Smooth step interpolation (eased version of lerp).
 * Provides smoother transitions at the start and end.
 */
export function smoothstep(a: number, b: number, t: number): number {
    t = clamp(t, 0, 1);
    t = t * t * (3 - 2 * t); // Hermite interpolation
    return lerp(a, b, t);
}

/**
 * Calculate interpolation factor based on time since last snapshot.
 * 
 * @param timeSinceSnapshot - Time in ms since last snapshot was received
 * @param snapshotInterval - Expected interval between snapshots in ms (1000/broadcast_hz)
 * @returns Interpolation factor (0-1), clamped
 */
export function getInterpolationFactor(
    timeSinceSnapshot: number,
    snapshotInterval: number = 33.33 // 30Hz default
): number {
    return clamp(timeSinceSnapshot / snapshotInterval, 0, 1);
}

/**
 * Interpolate turtle position between two snapshots.
 */
export interface InterpolatedPosition {
    x: number;
    y: number;
    angle: number;
}

export function interpolatePosition(
    prev: { x: number; y: number; angle: number },
    current: { x: number; y: number; angle: number },
    t: number
): InterpolatedPosition {
    return {
        x: lerp(prev.x, current.x, t),
        y: lerp(prev.y, current.y, t),
        angle: lerp(prev.angle, current.angle, t),
    };
}

/**
 * Calculate visual scale from track position.
 * Turtles further along track could appear larger (perspective effect).
 */
export function getProgressScale(
    distance: number,
    trackLength: number,
    minScale: number = 0.8,
    maxScale: number = 1.2
): number {
    const progress = clamp(distance / trackLength, 0, 1);
    return lerp(minScale, maxScale, progress);
}

/**
 * Energy bar width calculation.
 */
export function getEnergyBarWidth(
    currentEnergy: number,
    maxEnergy: number,
    maxWidth: number = 40
): number {
    return (currentEnergy / maxEnergy) * maxWidth;
}
