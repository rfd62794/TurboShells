import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useGameStore } from '../stores';
import { supabase } from '../lib/supabase';
import { createShopTurtle, shopPriceForTurtle } from '../lib/turtleFactory';
import type { RosterTurtle } from '../types';
import '../styles/retro.css';
import './Shop.css';

interface ShopListing {
    turtle: RosterTurtle;
    price: number;
    tier: 'basic' | 'advanced' | 'champion';
}

const TIER_COLORS = { basic: '#aaa', advanced: '#33cc33', champion: '#ffd700' };
const TIER_LABELS = { basic: 'Basic', advanced: 'Advanced', champion: 'Champion' };

export default function Shop() {
    const navigate = useNavigate();
    const { money, persistMoney, fetchRoster } = useGameStore();
    const [listings, setListings] = useState<ShopListing[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [purchased, setPurchased] = useState<string | null>(null);

    useEffect(() => {
        generateListings();
    }, []);

    const generateListings = async () => {
        setIsLoading(true);
        const tiers: Array<'basic' | 'advanced' | 'champion'> = ['basic', 'basic', 'advanced', 'advanced', 'champion'];
        try {
            const created: ShopListing[] = [];
            for (const tier of tiers) {
                // Create temp turtles to show in shop (not inserted yet)
                const rng = (lo: number, hi: number) => lo + Math.random() * (hi - lo);
                const statRanges: Record<string, [number, number]> = {
                    basic: [2, 5], advanced: [4, 7], champion: [6, 10],
                };
                const [lo, hi] = statRanges[tier];
                const preview: RosterTurtle = {
                    id: `preview-${Math.random()}`,
                    name: ['Shellsworth', 'Turbo', 'Blaze', 'Pebbles', 'Rocky', 'Mossy', 'Speedy', 'Ironback'][Math.floor(Math.random() * 8)],
                    speed: rng(lo, hi),
                    max_energy: rng(70 + lo * 5, 100 + hi * 5),
                    recovery: rng(0.5 + lo * 0.05, 1.0 + hi * 0.05),
                    swim: rng(lo, hi),
                    climb: rng(lo, hi),
                    stamina: rng(lo, hi),
                    luck: rng(lo / 2, hi / 2),
                    genome: `B${Math.floor(Math.random()*4)}-S${Math.floor(Math.random()*4)}-P${Math.floor(Math.random()*3)}-C${Math.floor(Math.random()*0xFFFFFF).toString(16).padStart(6,'0')}`,
                    total_races: 0,
                    total_wins: 0,
                    generation: 0,
                    parent_a_id: null,
                    parent_b_id: null,
                    is_retired: false,
                    created_at: new Date().toISOString(),
                };
                created.push({ turtle: preview, price: shopPriceForTurtle(preview), tier });
            }
            setListings(created);
        } catch (e) {
            setError('Failed to generate listings');
        } finally {
            setIsLoading(false);
        }
    };

    const handleBuy = async (listing: ShopListing) => {
        if (money < listing.price) { setError('Not enough money!'); return; }
        setError(null);

        const { data, error: dbErr } = await supabase
            .from('turtles')
            .insert({
                name: listing.turtle.name,
                speed: listing.turtle.speed,
                max_energy: listing.turtle.max_energy,
                recovery: listing.turtle.recovery,
                swim: listing.turtle.swim,
                climb: listing.turtle.climb,
                stamina: listing.turtle.stamina,
                luck: listing.turtle.luck,
                genome: listing.turtle.genome,
                generation: 0,
            })
            .select()
            .single();

        if (dbErr) { setError(dbErr.message); return; }

        await persistMoney(money - listing.price);
        await fetchRoster();
        setPurchased((data as RosterTurtle).name);
        setListings(prev => prev.filter(l => l.turtle.id !== listing.turtle.id));
        setTimeout(() => setPurchased(null), 3000);
    };

    return (
        <div className="shop-view">
            <header className="shop-header pygame-panel">
                <button className="pygame-btn" onClick={() => navigate('/menu')}>← Back</button>
                <h1 className="retro-text">Turtle Shop</h1>
                <div className="money-badge">${money.toLocaleString()}</div>
            </header>

            <main className="shop-main">
                {purchased && (
                    <div className="purchase-banner pygame-panel">
                        🐢 {purchased} added to your roster!
                    </div>
                )}

                {error && <div className="error-message pygame-panel">{error}</div>}

                <div className="shop-actions">
                    <button className="pygame-btn refresh-btn" onClick={generateListings}>
                        🔄 Refresh Stock
                    </button>
                </div>

                {isLoading ? (
                    <div className="shop-loading">Loading stock...</div>
                ) : (
                    <div className="shop-grid">
                        {listings.map((listing, i) => (
                            <div key={i} className="shop-card pygame-panel">
                                <div className="tier-badge" style={{ color: TIER_COLORS[listing.tier] }}>
                                    {TIER_LABELS[listing.tier]}
                                </div>
                                <div className="shop-turtle-name">{listing.turtle.name}</div>
                                <div className="shop-stats">
                                    <div className="stat-row">
                                        <span className="stat-label">Speed</span>
                                        <StatBar value={listing.turtle.speed} max={10} />
                                        <span className="stat-val">{listing.turtle.speed.toFixed(1)}</span>
                                    </div>
                                    <div className="stat-row">
                                        <span className="stat-label">Energy</span>
                                        <StatBar value={listing.turtle.max_energy / 15} max={10} />
                                        <span className="stat-val">{listing.turtle.max_energy.toFixed(0)}</span>
                                    </div>
                                    <div className="stat-row">
                                        <span className="stat-label">Recovery</span>
                                        <StatBar value={listing.turtle.recovery * 5} max={10} />
                                        <span className="stat-val">{listing.turtle.recovery.toFixed(2)}</span>
                                    </div>
                                    <div className="stat-row">
                                        <span className="stat-label">Swim</span>
                                        <StatBar value={listing.turtle.swim} max={10} />
                                        <span className="stat-val">{listing.turtle.swim.toFixed(1)}</span>
                                    </div>
                                    <div className="stat-row">
                                        <span className="stat-label">Climb</span>
                                        <StatBar value={listing.turtle.climb} max={10} />
                                        <span className="stat-val">{listing.turtle.climb.toFixed(1)}</span>
                                    </div>
                                </div>
                                <button
                                    className={`pygame-btn buy-btn ${money < listing.price ? 'disabled' : ''}`}
                                    onClick={() => handleBuy(listing)}
                                    disabled={money < listing.price}
                                >
                                    Buy — ${listing.price}
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}

function StatBar({ value, max }: { value: number; max: number }) {
    const pct = Math.min(100, (value / max) * 100);
    const color = pct > 70 ? '#ffd700' : pct > 40 ? '#33cc33' : '#888';
    return (
        <div className="stat-bar">
            <div className="stat-fill" style={{ width: `${pct}%`, background: color }} />
        </div>
    );
}
