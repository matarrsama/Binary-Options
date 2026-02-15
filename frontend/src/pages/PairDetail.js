import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFirebaseData } from '../hooks/useFirebaseData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowLeft, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const PairDetail = () => {
  const { pairId } = useParams();
  const navigate = useNavigate();
  const { data: pairData, loading, error } = useFirebaseData('pairs', pairId);
  const [priceHistory, setPriceHistory] = useState([]);

  useEffect(() => {
    if (pairData && pairData.price) {
      setPriceHistory(prev => {
        const newEntry = {
          time: new Date().toLocaleTimeString(),
          price: parseFloat(pairData.price),
          timestamp: Date.now()
        };
        
        // Keep only last 50 entries
        const updated = [...prev, newEntry];
        return updated.slice(-50);
      });
    }
  }, [pairData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !pairData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl font-semibold mb-2">Pair not found</div>
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const formatPrice = (price) => {
    if (!price) return '0.00000';
    return parseFloat(price).toFixed(5);
  };

  const formatPayout = (payout) => {
    if (!payout) return 'N/A';
    return `${parseFloat(payout).toFixed(1)}%`;
  };

  const getPriceChange = () => {
    if (priceHistory.length < 2) return 'neutral';
    const current = priceHistory[priceHistory.length - 1].price;
    const previous = priceHistory[priceHistory.length - 2].price;
    return current > previous ? 'up' : current < previous ? 'down' : 'neutral';
  };

  const getPriceIcon = () => {
    const change = getPriceChange();
    switch (change) {
      case 'up':
        return <TrendingUp className="w-6 h-6 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-6 h-6 text-red-500" />;
      default:
        return <Minus className="w-6 h-6 text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mr-6"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back</span>
            </button>
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold text-gray-900">{pairId}</h1>
                {getPriceIcon()}
              </div>
              <p className="text-sm text-gray-600">
                {pairData.category || 'Unknown'} • Live market data
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Price Information */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Price Information</h2>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-600">Current Price</div>
                  <div className="text-3xl font-bold text-gray-900">
                    {formatPrice(pairData.price)}
                  </div>
                </div>

                {pairData.payout && (
                  <div>
                    <div className="text-sm text-gray-600">Payout</div>
                    <div className="text-xl font-semibold text-green-600">
                      {formatPayout(pairData.payout)}
                    </div>
                  </div>
                )}

                <div>
                  <div className="text-sm text-gray-600">Last Update</div>
                  <div className="text-sm text-gray-900">
                    {pairData.lastUpdate 
                      ? new Date(pairData.lastUpdate).toLocaleString()
                      : 'Unknown'
                    }
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-600">Status</div>
                  <div className={`text-sm font-medium ${
                    pairData.enabled !== false ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {pairData.enabled !== false ? 'Active' : 'Inactive'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Price Chart */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Price Chart (Last 50 Updates)</h2>
              
              {priceHistory.length > 1 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={priceHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time" 
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis 
                      tick={{ fontSize: 12 }}
                      domain={['dataMin - 0.00001', 'dataMax + 0.00001']}
                    />
                    <Tooltip 
                      formatter={(value) => [parseFloat(value).toFixed(5), 'Price']}
                      labelFormatter={(label) => `Time: ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-64 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <div className="text-lg">Waiting for price data...</div>
                    <div className="text-sm mt-2">Chart will appear once enough data points are collected</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PairDetail;
