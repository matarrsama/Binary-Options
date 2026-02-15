import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MarketPairsDashboard from './pages/MarketPairsDashboard';
import PairDetail from './pages/PairDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<MarketPairsDashboard />} />
          <Route path="/pair/:pairId" element={<PairDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
