import { useState, useEffect } from 'react';
import axios from 'axios';
import MapView from './MapView';
import ChatInterface from './ChatInterface';
import AlertPanel from './AlertPanel';
import RoutePlanner from './RoutePlanner';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  const [crowdData, setCrowdData] = useState({ venues: [] });
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Poll backend for crowd updates
  useEffect(() => {
    const fetchCrowdData = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/crowd`);
        setCrowdData(res.data.crowd_data);
        setIncidents(res.data.incidents);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching crowd data:", err);
      }
    };

    fetchCrowdData();
    const interval = setInterval(fetchCrowdData, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      {/* Left Column: Map and Alerts */}
      <div className="lg:col-span-8 flex flex-col gap-6">
        <div className="glass rounded-2xl overflow-hidden relative shadow-2xl flex flex-col h-[500px]">
          <div className="px-5 py-4 border-b border-white/5 bg-surface/40 flex justify-between items-center z-10">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span className="text-xl">🗺️</span> Milan Venues Live Map
            </h2>
            <div className="text-xs font-medium text-gray-400 bg-surface/60 px-2 py-1 rounded">Live Updates</div>
          </div>
          <div className="flex-1 bg-[#1a1a1a] relative z-0">
            {!loading && <MapView venues={crowdData.venues} />}
          </div>
        </div>

        <div className="glass rounded-2xl overflow-hidden shadow-2xl flex flex-col min-h-[300px]">
          <div className="px-5 py-3 border-b border-white/5 bg-surface/40">
            <h2 className="text-md font-semibold flex items-center gap-2">
              <span className="text-lg">🚨</span> Active Alerts & Incidents
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <AlertPanel incidents={incidents} />
          </div>
        </div>
      </div>

      {/* Right Column: AI Chat and Routing */}
      <div className="lg:col-span-4 flex flex-col gap-6">
        
        <div className="glass rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[500px]">
          <div className="px-5 py-4 border-b border-white/5 bg-surface/40">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span className="text-xl">🤖</span> Ask OlympicMind
            </h2>
          </div>
          <div className="flex-1 overflow-hidden relative">
            <ChatInterface />
          </div>
        </div>

        <div className="glass rounded-2xl overflow-hidden shadow-2xl flex flex-col">
          <div className="px-5 py-4 border-b border-white/5 bg-surface/40">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span className="text-xl">📍</span> Smart Route Planner
            </h2>
          </div>
          <div className="p-4">
            <RoutePlanner venues={crowdData.venues} />
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
