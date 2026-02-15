/**
 * Home page - Market Pairs Dashboard
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import MarketPairsDashboard from '../components/MarketPairsDashboard';
import ConnectionStatus from '../components/ConnectionStatus';
import { subscribeToAllPairs } from '../lib/firestore';
import { Activity } from 'lucide-react';

export default function Home() {
    const [pairs, setPairs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Subscribe to real-time updates from Firestore
        const unsubscribe = subscribeToAllPairs((updatedPairs) => {
            setPairs(updatedPairs);
            setIsLoading(false);
            setIsConnected(true);
        });

        // Cleanup subscription on unmount
        return () => {
            if (unsubscribe) unsubscribe();
        };
    }, []);

    return (
        <>
            <Head>
                <title>Live Market Pairs | Pocket Option</title>
                <meta name="description" content="Real-time market pairs and price data from Pocket Option" />
            </Head>

            <div className="min-h-screen">
                {/* Connection Status Indicator */}
                <ConnectionStatus isConnected={isConnected} isReconnecting={false} />

                {/* Header */}
                <header className="border-b border-dark-800 bg-dark-900/50 backdrop-blur-md sticky top-0 z-40">
                    <div className="container mx-auto px-4 py-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center shadow-lg shadow-primary-500/30">
                                <Activity className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-dark-50">Pocket Option</h1>
                                <p className="text-xs text-dark-400">Live Market Data</p>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <main className="container mx-auto px-4 py-8">
                    <MarketPairsDashboard pairs={pairs} isLoading={isLoading} />
                </main>

                {/* Footer */}
                <footer className="border-t border-dark-800 bg-dark-900/50 backdrop-blur-md mt-16">
                    <div className="container mx-auto px-4 py-6">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                            <p className="text-sm text-dark-400">
                                © 2026 Pocket Option Live Market Data
                            </p>
                            <div className="flex items-center gap-2 text-sm text-dark-400">
                                <div className="w-2 h-2 rounded-full bg-success-light animate-pulse" />
                                <span>Real-time updates via Firebase</span>
                            </div>
                        </div>
                    </div>
                </footer>
            </div>
        </>
    );
}
