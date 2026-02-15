import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MarketPairCard = ({ pair, onClick }) => {
  const formatPrice = (price) => {
    if (!price) return '0.00000';
    return parseFloat(price).toFixed(5);
  };

  const formatPayout = (payout) => {
    if (!payout) return null;
    return `${parseFloat(payout).toFixed(1)}%`;
  };

  const getPriceChange = () => {
    // This would require historical data for proper calculation
    // For now, we'll just show a neutral indicator
    return 'neutral';
  };

  const getPriceIcon = () => {
    const change = getPriceChange();
    switch (change) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const lastUpdate = pair.lastUpdate ? new Date(pair.lastUpdate).toLocaleTimeString() : null;

  return (
    <div
      onClick={() => onClick && onClick(pair)}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer hover:border-blue-300"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold text-lg text-gray-900">{pair.id}</h3>
          {getPriceIcon()}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">
            {formatPrice(pair.price)}
          </div>
          {pair.payout && (
            <div className="text-sm text-green-600 font-medium">
              {formatPayout(pair.payout)}
            </div>
          )}
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {pair.category || 'Unknown'}
        </span>
        {lastUpdate && (
          <span className="text-xs text-gray-400">
            {lastUpdate}
          </span>
        )}
      </div>
    </div>
  );
};

export default MarketPairCard;
