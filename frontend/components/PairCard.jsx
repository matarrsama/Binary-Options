/**
 * Individual market pair card component
 */
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import Link from 'next/link';

export default function PairCard({ pair }) {
    const [priceChange, setPriceChange] = useState(null);
    const [prevPrice, setPrevPrice] = useState(pair.price);

    useEffect(() => {
        if (pair.price !== prevPrice) {
            setPriceChange(pair.price > prevPrice ? 'up' : 'down');
            setPrevPrice(pair.price);

            // Reset price change indicator after animation
            const timer = setTimeout(() => setPriceChange(null), 1000);
            return () => clearTimeout(timer);
        }
    }, [pair.price, prevPrice]);

    const getCategoryColor = (category) => {
        switch (category) {
            case 'forex': return 'text-blue-400';
            case 'crypto': return 'text-orange-400';
            case 'commodities': return 'text-yellow-400';
            case 'stocks': return 'text-green-400';
            default: return 'text-dark-400';
        }
    };

    const getCategoryBadge = (category) => {
        switch (category) {
            case 'forex': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            case 'crypto': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
            case 'commodities': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            case 'stocks': return 'bg-green-500/20 text-green-400 border-green-500/30';
            default: return 'bg-dark-700/20 text-dark-400 border-dark-600/30';
        }
    };

    return (
        <Link href={`/pair/${pair.id}`}>
            <div className="card card-hover cursor-pointer">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <h3 className="text-xl font-bold text-dark-50 mb-1">
                            {pair.name || pair.id}
                        </h3>
                        <span className={`text-xs px-2 py-1 rounded-full border ${getCategoryBadge(pair.category)}`}>
                            {pair.category?.toUpperCase() || 'UNKNOWN'}
                        </span>
                    </div>

                    <div className="flex items-center gap-1">
                        {priceChange === 'up' && (
                            <TrendingUp className="w-5 h-5 text-success-light animate-bounce" />
                        )}
                        {priceChange === 'down' && (
                            <TrendingDown className="w-5 h-5 text-danger-light animate-bounce" />
                        )}
                        {!priceChange && pair.isOpen && (
                            <div className="w-2 h-2 rounded-full bg-success-light animate-pulse" />
                        )}
                    </div>
                </div>

                <div className="space-y-3">
                    <div>
                        <p className="text-sm text-dark-400 mb-1">Current Price</p>
                        <p className={`text-3xl font-bold font-mono ${priceChange === 'up' ? 'price-up' :
                                priceChange === 'down' ? 'price-down' :
                                    'text-dark-50'
                            }`}>
                            {pair.price ? pair.price.toFixed(5) : '---'}
                        </p>
                    </div>

                    {pair.payout > 0 && (
                        <div className="flex items-center justify-between pt-3 border-t border-dark-700/50">
                            <span className="text-sm text-dark-400">Payout</span>
                            <span className="text-lg font-semibold text-primary-400">
                                {pair.payout}%
                            </span>
                        </div>
                    )}

                    <div className="flex items-center justify-between text-xs text-dark-500">
                        <span>
                            {pair.isOpen ? (
                                <span className="text-success-light">● Open</span>
                            ) : (
                                <span className="text-danger-light">● Closed</span>
                            )}
                        </span>
                        {pair.lastUpdate && (
                            <span>
                                Updated {new Date(pair.lastUpdate?.seconds * 1000).toLocaleTimeString()}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </Link>
    );
}
