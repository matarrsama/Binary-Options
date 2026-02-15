/**
 * Pair detail page - Shows detailed information for a specific market pair
 */
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { subscribeToPair } from '../../lib/firestore';
import PriceChart from '../../components/PriceChart';
import ConnectionStatus from '../../components/ConnectionStatus';
import { ArrowLeft, TrendingUp, TrendingDown, Activity, Clock } from 'lucide-react';

export default function PairDetail() {
    const router = useRouter();
    const { id } = router.query;

    const [pair, setPair] = useState(null);
    const [priceHistory, setPriceHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        if (!id) return;

        // Subscribe to real-time updates for this pair
        const unsubscribe = subscribeToPair(id, (updatedPair) => {
            if (updatedPair) {
                setPair(updatedPair);
                setIsConnected(true);

                // Add to price history for chart
                setPriceHistory(prev => {
                    const newHistory = [...prev, {
                        time: new Date().toLocaleTimeString(),
                        price: updatedPair.price
                    }];
                    // Keep last 20 data points
                    return newHistory.slice(-20);
                });
            }
            setIsLoading(false);
        });

        return () => {
            if (unsubscribe) unsubscribe();
        };
    }, [id]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <Activity className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
                    <p className="text-dark-400">Loading pair data...</p>
                </div>
            </div>
        );
    }

    if (!pair) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <p className="text-dark-400 text-lg mb-4">Pair not found</p>
                    <Link href="/">
                        <button className="btn-primary">
                            Back to Dashboard
                        </button>
                    </Link>
                </div>
            </div>
        );
    }

    const getCategoryColor = (category) => {
        switch (category) {
            case 'forex': return 'text-blue-400';
            case 'crypto': return 'text-orange-400';
            case 'commodities': return 'text-yellow-400';
            case 'stocks': return 'text-green-400';
            default: return 'text-dark-400';
        }
    };

    return (
        <>
            <Head>
                <title>{pair.name || pair.id} | Live Market Data</title>
                <meta name="description" content={`Real-time price data for ${pair.name || pair.id}`} />
            </Head>

            <div className="min-h-screen">
                <ConnectionStatus isConnected={isConnected} isReconnecting={false} />

                {/* Header */}
                <header className="border-b border-dark-800 bg-dark-900/50 backdrop-blur-md">
                    <div className="container mx-auto px-4 py-4">
                        <Link href="/">
                            <button className="flex items-center gap-2 text-dark-400 hover:text-dark-200 transition-colors">
                                <ArrowLeft className="w-5 h-5" />
                                <span>Back to Dashboard</span>
                            </button>
                        </Link>
                    </div>
                </header>

                {/* Main Content */}
                <main className="container mx-auto px-4 py-8">
                    <div className="max-w-6xl mx-auto space-y-6">
                        {/* Pair Header */}
                        <div className="card">
                            <div className="flex items-start justify-between mb-6">
                                <div>
                                    <h1 className="text-4xl font-bold text-dark-50 mb-2">
                                        {pair.name || pair.id}
                                    </h1>
                                    <span className={`text-sm px-3 py-1 rounded-full bg-dark-700/50 ${getCategoryColor(pair.category)}`}>
                                        {pair.category?.toUpperCase() || 'UNKNOWN'}
                                    </span>
                                </div>

                                <div className="text-right">
                                    {pair.isOpen ? (
                                        <span className="inline-flex items-center gap-2 text-success-light">
                                            <div className="w-2 h-2 rounded-full bg-success-light animate-pulse" />
                                            Market Open
                                        </span>
                                    ) : (
                                        <span className="inline-flex items-center gap-2 text-danger-light">
                                            <div className="w-2 h-2 rounded-full bg-danger-light" />
                                            Market Closed
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Current Price */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="md:col-span-2">
                                    <p className="text-sm text-dark-400 mb-2">Current Price</p>
                                    <p className="text-6xl font-bold font-mono text-dark-50">
                                        {pair.price ? pair.price.toFixed(5) : '---'}
                                    </p>
                                </div>

                                {pair.payout > 0 && (
                                    <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-6 flex flex-col justify-center">
                                        <p className="text-sm text-primary-400 mb-2">Payout</p>
                                        <p className="text-4xl font-bold text-primary-400">
                                            {pair.payout}%
                                        </p>
                                    </div>
                                )}
                            </div>

                            {/* Last Update */}
                            {pair.lastUpdate && (
                                <div className="flex items-center gap-2 text-sm text-dark-500 mt-6 pt-6 border-t border-dark-700/50">
                                    <Clock className="w-4 h-4" />
                                    <span>
                                        Last updated: {new Date(pair.lastUpdate?.seconds * 1000).toLocaleString()}
                                    </span>
                                </div>
                            )}
                        </div>

                        {/* Price Chart */}
                        <div className="card">
                            <h2 className="text-2xl font-bold text-dark-50 mb-4">
                                Price History
                            </h2>
                            <PriceChart data={priceHistory} />
                            <p className="text-sm text-dark-500 mt-4">
                                Showing last {priceHistory.length} price updates
                            </p>
                        </div>

                        {/* Additional Info */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="card">
                                <h3 className="text-xl font-bold text-dark-50 mb-4">Market Info</h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between">
                                        <span className="text-dark-400">Pair ID</span>
                                        <span className="text-dark-50 font-mono">{pair.id}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-dark-400">Category</span>
                                        <span className={getCategoryColor(pair.category)}>
                                            {pair.category?.toUpperCase() || 'UNKNOWN'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-dark-400">Status</span>
                                        <span className={pair.isOpen ? 'text-success-light' : 'text-danger-light'}>
                                            {pair.isOpen ? 'Open' : 'Closed'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="card">
                                <h3 className="text-xl font-bold text-dark-50 mb-4">Trading Info</h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between">
                                        <span className="text-dark-400">Current Price</span>
                                        <span className="text-dark-50 font-mono">
                                            {pair.price ? pair.price.toFixed(5) : '---'}
                                        </span>
                                    </div>
                                    {pair.payout > 0 && (
                                        <div className="flex justify-between">
                                            <span className="text-dark-400">Payout</span>
                                            <span className="text-primary-400 font-semibold">
                                                {pair.payout}%
                                            </span>
                                        </div>
                                    )}
                                    <div className="flex justify-between">
                                        <span className="text-dark-400">Data Source</span>
                                        <span className="text-dark-50">Pocket Option</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </>
    );
}
