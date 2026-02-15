import React from 'react';
import { Wifi, WifiOff, Loader2 } from 'lucide-react';

const ConnectionStatus = ({ isConnected, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-yellow-600 bg-yellow-50 px-3 py-2 rounded-lg">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm font-medium">Connecting to data feed...</span>
      </div>
    );
  }

  if (isConnected) {
    return (
      <div className="flex items-center space-x-2 text-green-600 bg-green-50 px-3 py-2 rounded-lg">
        <Wifi className="w-4 h-4" />
        <span className="text-sm font-medium">Live data connected</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-red-600 bg-red-50 px-3 py-2 rounded-lg">
      <WifiOff className="w-4 h-4" />
      <span className="text-sm font-medium">Connection lost</span>
    </div>
  );
};

export default ConnectionStatus;
