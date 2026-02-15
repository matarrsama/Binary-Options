import React, { useState } from 'react';
import { useMarketPairs } from '../hooks/useFirebaseData';
import MarketPairCard from '../components/MarketPairCard';
import SearchFilter from '../components/SearchFilter';
import ConnectionStatus from '../components/ConnectionStatus';
import { useNavigate } from 'react-router-dom';

const MarketPairsDashboard = () => {
  const navigate = useNavigate();
  const { 
    pairs, 
    loading, 
    error, 
    searchTerm, 
    setSearchTerm, 
    selectedCategory, 
    setSelectedCategory, 
    categories 
  } = useMarketPairs();

  const handlePairClick = (pair) => {
    navigate(`/pair/${pair.id}`);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl font-semibold mb-2">Error loading data</div>
          <div className="text-gray-600">{error.message}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Pocket Option Live Markets</h1>
              <p className="text-sm text-gray-600">Real-time market data and pricing</p>
            </div>
            <ConnectionStatus isConnected={!loading && pairs.length > 0} loading={loading} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filter */}
        <SearchFilter
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          categories={categories}
        />

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Total Pairs</div>
            <div className="text-2xl font-bold text-gray-900">{pairs.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Active Pairs</div>
            <div className="text-2xl font-bold text-green-600">
              {pairs.filter(pair => pair.enabled !== false).length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Categories</div>
            <div className="text-2xl font-bold text-blue-600">{categories.length - 1}</div>
          </div>
        </div>

        {/* Market Pairs Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : pairs.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-600 text-lg">No market pairs found</div>
            <div className="text-gray-400 text-sm mt-2">
              {searchTerm || selectedCategory !== 'all' 
                ? 'Try adjusting your filters' 
                : 'Waiting for data from Pocket Option...'}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {pairs.map((pair) => (
              <MarketPairCard
                key={pair.id}
                pair={pair}
                onClick={handlePairClick}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default MarketPairsDashboard;
