/**
 * Category filter component for filtering market pairs by category
 */
import { TrendingUp, Bitcoin, Coins, Building2 } from 'lucide-react';

const categories = [
    { id: 'all', name: 'All', icon: TrendingUp },
    { id: 'forex', name: 'Forex', icon: Coins },
    { id: 'crypto', name: 'Crypto', icon: Bitcoin },
    { id: 'commodities', name: 'Commodities', icon: TrendingUp },
    { id: 'stocks', name: 'Stocks', icon: Building2 },
];

export default function CategoryFilter({ selectedCategory, onCategoryChange }) {
    return (
        <div className="flex flex-wrap gap-2">
            {categories.map((category) => {
                const Icon = category.icon;
                const isSelected = selectedCategory === category.id;

                return (
                    <button
                        key={category.id}
                        onClick={() => onCategoryChange(category.id)}
                        className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium
              transition-all duration-300 active:scale-95
              ${isSelected
                                ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/30'
                                : 'bg-dark-800/50 text-dark-300 border border-dark-700 hover:bg-dark-700/50 hover:border-dark-600'
                            }
            `}
                    >
                        <Icon className="w-4 h-4" />
                        <span>{category.name}</span>
                    </button>
                );
            })}
        </div>
    );
}
