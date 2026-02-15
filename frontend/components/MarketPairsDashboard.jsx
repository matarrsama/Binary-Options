/**
 * Market pairs dashboard component
 */
import { useState, useEffect, useMemo } from 'react';
import PairCard from './PairCard';
import SearchBar from './SearchBar';
import CategoryFilter from './CategoryFilter';
import { Loader2 } from 'lucide-react';

export default function MarketPairsDashboard({ pairs, isLoading }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');

    // Filter pairs based on search and category
    const filteredPairs = useMemo(() => {
        let filtered = pairs;

        // Filter by search term
        if (searchTerm) {
            filtered = filtered.filter(pair =>
                (pair.name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (pair.id?.toLowerCase().includes(searchTerm.toLowerCase()))
            );
        }

        // Filter by category
        if (selectedCategory !== 'all') {
            filtered = filtered.filter(pair => pair.category === selectedCategory);
        }

        return filtered;
    }, [pairs, searchTerm, selectedCategory]);

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
                <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
                <p className="text-dark-400">Loading market pairs...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold text-gradient mb-2">
                        Live Market Pairs
                    </h1>
                    <p className="text-dark-400">
                        {filteredPairs.length} {filteredPairs.length === 1 ? 'pair' : 'pairs'} available
                    </p>
                </div>

                <SearchBar
                    onSearch={setSearchTerm}
                    placeholder="Search pairs..."
                />
            </div>

            {/* Category Filter */}
            <CategoryFilter
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
            />

            {/* Pairs Grid */}
            {filteredPairs.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-dark-400 text-lg">
                        {searchTerm || selectedCategory !== 'all'
                            ? 'No pairs match your filters'
                            : 'No market pairs available'}
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {filteredPairs.map((pair) => (
                        <PairCard key={pair.id} pair={pair} />
                    ))}
                </div>
            )}
        </div>
    );
}
