/**
 * Connection status indicator component
 */
import { useState, useEffect } from 'react';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';

export default function ConnectionStatus({ isConnected, isReconnecting }) {
    const [showStatus, setShowStatus] = useState(true);

    useEffect(() => {
        // Auto-hide after 5 seconds if connected
        if (isConnected && !isReconnecting) {
            const timer = setTimeout(() => setShowStatus(false), 5000);
            return () => clearTimeout(timer);
        } else {
            setShowStatus(true);
        }
    }, [isConnected, isReconnecting]);

    if (!showStatus && isConnected) return null;

    return (
        <div className="fixed top-4 right-4 z-50">
            <div className={`
        flex items-center gap-2 px-4 py-2 rounded-lg shadow-lg
        backdrop-blur-md border transition-all duration-300
        ${isConnected && !isReconnecting
                    ? 'bg-success-dark/20 border-success-light/30 text-success-light'
                    : isReconnecting
                        ? 'bg-yellow-900/20 border-yellow-500/30 text-yellow-500'
                        : 'bg-danger-dark/20 border-danger-light/30 text-danger-light'
                }
      `}>
                {isConnected && !isReconnecting ? (
                    <>
                        <div className="status-indicator status-connected" />
                        <Wifi className="w-4 h-4" />
                        <span className="text-sm font-medium">Connected</span>
                    </>
                ) : isReconnecting ? (
                    <>
                        <div className="status-indicator status-reconnecting" />
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span className="text-sm font-medium">Reconnecting...</span>
                    </>
                ) : (
                    <>
                        <div className="status-indicator status-disconnected" />
                        <WifiOff className="w-4 h-4" />
                        <span className="text-sm font-medium">Disconnected</span>
                    </>
                )}
            </div>
        </div>
    );
}
