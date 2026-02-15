import { useState, useEffect, useRef } from 'react';
import { firestore } from '../firebase';
import { collection, doc, onSnapshot, query, orderBy, limit, getDocs } from 'firebase/firestore';

export const useFirebaseData = (collectionName, documentId = null) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const listenerRef = useRef(null);

  useEffect(() => {
    if (!collectionName) return;

    setLoading(true);
    setError(null);

    try {
      if (documentId) {
        // Listen to a specific document
        const docRef = doc(firestore, collectionName, documentId);
        
        listenerRef.current = onSnapshot(
          docRef,
          (snapshot) => {
            const value = snapshot.exists() ? snapshot.data() : null;
            setData(value);
            setLoading(false);
            setError(null);
          },
          (error) => {
            console.error('Firestore document error:', error);
            setError(error);
            setLoading(false);
          }
        );
      } else {
        // Listen to entire collection
        const collectionRef = collection(firestore, collectionName);
        
        listenerRef.current = onSnapshot(
          collectionRef,
          (snapshot) => {
            const value = {};
            snapshot.forEach((doc) => {
              value[doc.id] = doc.data();
            });
            setData(value);
            setLoading(false);
            setError(null);
          },
          (error) => {
            console.error('Firestore collection error:', error);
            setError(error);
            setLoading(false);
          }
        );
      }
    } catch (error) {
      console.error('Error setting up Firestore listener:', error);
      setError(error);
      setLoading(false);
    }

    return () => {
      if (listenerRef.current) {
        listenerRef.current();
      }
    };
  }, [collectionName, documentId]);

  return { data, loading, error };
};

export const useMarketPairs = () => {
  const { data: pairsData, loading, error } = useFirebaseData('pairs');
  
  const [pairs, setPairs] = useState([]);
  const [filteredPairs, setFilteredPairs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    if (pairsData) {
      const pairsArray = Object.entries(pairsData).map(([key, value]) => ({
        id: key,
        ...value
      }));
      setPairs(pairsArray);
    }
  }, [pairsData]);

  useEffect(() => {
    let filtered = pairs;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(pair => 
        pair.id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(pair => 
        pair.category === selectedCategory
      );
    }

    setFilteredPairs(filtered);
  }, [pairs, searchTerm, selectedCategory]);

  const categories = ['all', ...new Set(pairs.map(pair => pair.category).filter(Boolean))];

  return {
    pairs: filteredPairs,
    allPairs: pairs,
    loading,
    error,
    searchTerm,
    setSearchTerm,
    selectedCategory,
    setSelectedCategory,
    categories
  };
};
