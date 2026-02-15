/**
 * Search bar component for filtering market pairs
 */
import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';

export default function SearchBar({ onSearch, placeholder = "Search pairs..." }) {
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        // Debounce search
        const timer = setTimeout(() => {
            onSearch(searchTerm);
        }, 300);

        return () => clearTimeout(timer);
    }, [searchTerm, onSearch]);

    const handleClear = () => {
        setSearchTerm('');
        onSearch('');
    };

    return (
        <div className="relative w-full max-w-md">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-dark-400">
                <Search className="w-5 h-5" />
            </div>

            <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={placeholder}
                className="input-field w-full pl-12 pr-12"
            />

            {searchTerm && (
                <button
                    onClick={handleClear}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400 hover:text-dark-200 transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>
            )}
        </div>
    );
}
