/**
 * Firestore helper functions for real-time market data.
 */
import { db } from './firebase';
import {
    collection,
    doc,
    onSnapshot,
    query,
    orderBy,
    where,
    getDocs
} from 'firebase/firestore';

/**
 * Subscribe to all market pairs with real-time updates
 * @param {Function} callback - Called with array of pairs on each update
 * @returns {Function} Unsubscribe function
 */
export function subscribeToAllPairs(callback) {
    if (!db) {
        console.error('Firestore not initialized');
        return () => { };
    }

    const pairsRef = collection(db, 'pairs');
    const q = query(pairsRef, orderBy('name'));

    const unsubscribe = onSnapshot(q, (snapshot) => {
        const pairs = [];
        snapshot.forEach((doc) => {
            pairs.push({
                id: doc.id,
                ...doc.data()
            });
        });
        callback(pairs);
    }, (error) => {
        console.error('Error subscribing to pairs:', error);
    });

    return unsubscribe;
}

/**
 * Subscribe to a single market pair
 * @param {string} pairId - Pair ID to subscribe to
 * @param {Function} callback - Called with pair data on each update
 * @returns {Function} Unsubscribe function
 */
export function subscribeToPair(pairId, callback) {
    if (!db) {
        console.error('Firestore not initialized');
        return () => { };
    }

    const pairRef = doc(db, 'pairs', pairId);

    const unsubscribe = onSnapshot(pairRef, (doc) => {
        if (doc.exists()) {
            callback({
                id: doc.id,
                ...doc.data()
            });
        } else {
            callback(null);
        }
    }, (error) => {
        console.error(`Error subscribing to pair ${pairId}:`, error);
    });

    return unsubscribe;
}

/**
 * Subscribe to pairs filtered by category
 * @param {string} category - Category to filter by (forex, crypto, commodities, stocks)
 * @param {Function} callback - Called with filtered pairs on each update
 * @returns {Function} Unsubscribe function
 */
export function subscribeToPairsByCategory(category, callback) {
    if (!db) {
        console.error('Firestore not initialized');
        return () => { };
    }

    const pairsRef = collection(db, 'pairs');
    const q = query(
        pairsRef,
        where('category', '==', category),
        orderBy('name')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
        const pairs = [];
        snapshot.forEach((doc) => {
            pairs.push({
                id: doc.id,
                ...doc.data()
            });
        });
        callback(pairs);
    }, (error) => {
        console.error(`Error subscribing to ${category} pairs:`, error);
    });

    return unsubscribe;
}

/**
 * Get all pairs once (no real-time updates)
 * @returns {Promise<Array>} Array of all pairs
 */
export async function getAllPairs() {
    if (!db) {
        console.error('Firestore not initialized');
        return [];
    }

    try {
        const pairsRef = collection(db, 'pairs');
        const q = query(pairsRef, orderBy('name'));
        const snapshot = await getDocs(q);

        const pairs = [];
        snapshot.forEach((doc) => {
            pairs.push({
                id: doc.id,
                ...doc.data()
            });
        });

        return pairs;
    } catch (error) {
        console.error('Error getting pairs:', error);
        return [];
    }
}
