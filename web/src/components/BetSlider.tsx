import React from 'react';
import '../styles/retro.css';

interface BetSliderProps {
    currentBet: number;
    maxBet: number;
    money: number;
    onChange: (amount: number) => void;
}

export function BetSlider({ currentBet, maxBet, money, onChange }: BetSliderProps) {
    // Clamp max bet to available money and hard limit (e.g. 500)
    const effectiveMax = Math.min(money, maxBet);

    return (
        <div className="bet-slider-container">
            <div className="bet-info">
                <label className="retro-label">Wager:</label>
                <span className="bet-value">${currentBet}</span>
            </div>

            <input
                type="range"
                className="retro-range"
                min={0}
                max={effectiveMax}
                step={10}
                value={currentBet}
                onChange={(e) => onChange(Number(e.target.value))}
                disabled={effectiveMax <= 0}
            />

            <div className="bet-limits">
                <span>$0</span>
                <span>${effectiveMax}</span>
            </div>

            {money === 0 && (
                <p className="error-text blink">BANKRUPT!</p>
            )}
        </div>
    );
}
