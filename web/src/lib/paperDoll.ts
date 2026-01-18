/**
 * Paper Doll Assembler
 * 
 * Takes a genome string (e.g., "B1-S2-P0-CFF0000") and builds composite
 * turtle layers for PixiJS rendering.
 * 
 * The genome format is:
 * - B{n}: Body type (0-3: solid, mottled, speckled, marbled)
 * - S{n}: Shell type (0-3: hex, spots, stripes, rings)
 * - P{n}: Pattern/limb type (0-2: flippers, feet, fins)
 * - C{hex}: Color (6-char hex without #)
 */

import type { ParsedGenome } from '../types';

/** Body pattern names (index matches Python BODY_PATTERNS) */
export const BODY_PATTERNS = ['solid', 'mottled', 'speckled', 'marbled'] as const;

/** Shell pattern names (index matches Python SHELL_PATTERNS) */
export const SHELL_PATTERNS = ['hex', 'spots', 'stripes', 'rings'] as const;

/** Limb shape names (index matches Python LIMB_SHAPES) */
export const LIMB_SHAPES = ['flippers', 'feet', 'fins'] as const;

/**
 * Parse a genome string into structured components.
 * 
 * @param genome - Genome string like "B1-S2-P0-CFF0000"
 * @returns Parsed genome with numeric indices and hex color
 */
export function parseGenome(genome: any): ParsedGenome {
    // Default fallback
    const result: ParsedGenome = {
        bodyType: 0,
        shellType: 0,
        patternType: 0,
        color: '228B22', // Default forest green
    };

    if (!genome) return result;

    // Handle legacy string format "B1-S2-P0-CFF0000"
    if (typeof genome === 'string') {
        if (!genome.includes('-')) return result; // Empty/Invalid string

        const parts = genome.split('-');
        for (const part of parts) {
            if (!part) continue;
            const prefix = part[0];
            const value = part.slice(1);

            switch (prefix) {
                case 'B': result.bodyType = parseInt(value, 10) || 0; break;
                case 'S': result.shellType = parseInt(value, 10) || 0; break;
                case 'P': result.patternType = parseInt(value, 10) || 0; break;
                case 'C': result.color = value || '228B22'; break;
            }
        }
        return result;
    }

    // Handle object format (VisualGenetics dictionary)
    if (typeof genome === 'object') {
        // Mapping from VisualGenetics keys to simplified PaperDoll indices
        // Assuming keys like 'body_pattern_type', 'shell_pattern_type', 'limb_shape'
        if (genome.body_pattern_type !== undefined) result.bodyType = Number(genome.body_pattern_type) || 0;
        if (genome.shell_pattern_type !== undefined) result.shellType = Number(genome.shell_pattern_type) || 0;
        // Map limb shape (string?) or int to pattern Type
        // If VisualGenetics sends strings, we'd need parsing. Assuming fallback for now.

        // Color Handling: Support Hex String OR RGB Tuple/Array
        const rawColor = genome.shell_base_color;
        if (rawColor) {
            if (Array.isArray(rawColor) && rawColor.length >= 3) {
                // Convert [R, G, B] to Hex String
                const r = rawColor[0];
                const g = rawColor[1];
                const b = rawColor[2];
                // basic rgb to hex
                const toHex = (c: number) => c.toString(16).padStart(2, '0');
                result.color = `${toHex(r)}${toHex(g)}${toHex(b)}`;
            } else {
                // Assume string
                const strColor = String(rawColor);
                // Handle tuple string "(r, g, b)" from Python
                if (strColor.includes(',')) {
                    const rgb = strColor.replace(/[()\[\]\s]/g, '').split(',').map(Number);
                    if (rgb.length >= 3) {
                        const toHex = (c: number) => c.toString(16).padStart(2, '0');
                        result.color = `${toHex(rgb[0])}${toHex(rgb[1])}${toHex(rgb[2])}`;
                    }
                } else {
                    // Standard Hex
                    result.color = strColor.replace('#', '');
                }
            }
        }

        return result;
    }

    return result;
}

/**
 * Convert hex color string to numeric value for PIXI tinting.
 * 
 * @param hex - 6-character hex string (no #)
 * @returns Numeric color value
 */
export function hexToNumber(hex: string): number {
    return parseInt(hex, 16);
}

/**
 * Get the body pattern name from the parsed genome.
 */
export function getBodyPatternName(genome: ParsedGenome): string {
    return BODY_PATTERNS[genome.bodyType] ?? 'solid';
}

/**
 * Get the shell pattern name from the parsed genome.
 */
export function getShellPatternName(genome: ParsedGenome): string {
    return SHELL_PATTERNS[genome.shellType] ?? 'hex';
}

/**
 * Get the limb shape name from the parsed genome.
 */
export function getLimbShapeName(genome: ParsedGenome): string {
    return LIMB_SHAPES[genome.patternType] ?? 'flippers';
}

/**
 * Generate layer configuration for a turtle based on genome.
 * This returns the information needed to compose the turtle in PixiJS.
 */
export interface TurtleLayers {
    body: {
        pattern: string;
        tint: number;
    };
    shell: {
        pattern: string;
        tint: number;
    };
    limbs: {
        shape: string;
        tint: number;
    };
    eyes: {
        tint: number;
    };
}

export function buildTurtleLayers(genome: ParsedGenome): TurtleLayers {
    const tint = hexToNumber(genome.color);

    // Slightly darken color for body/limbs (simulate shading)
    const bodyTint = Math.floor(tint * 0.8);
    const limbTint = Math.floor(tint * 0.6);

    return {
        body: {
            pattern: getBodyPatternName(genome),
            tint: bodyTint,
        },
        shell: {
            pattern: getShellPatternName(genome),
            tint: tint,
        },
        limbs: {
            shape: getLimbShapeName(genome),
            tint: limbTint,
        },
        eyes: {
            tint: 0x000000, // Black eyes
        },
    };
}
