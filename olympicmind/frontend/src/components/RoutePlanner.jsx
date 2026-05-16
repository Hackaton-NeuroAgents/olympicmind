import { useState } from 'react';
import axios from 'axios';
import { MapPin, Navigation, Clock, ShieldAlert, Footprints, TrainFront, Bus, AlertTriangle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const RoutePlanner = ({ venues = [] }) => {
  const [origin, setOrigin] = useState('Fiera');
  const [destination, setDestination] = useState('Duomo');
  const [routeResult, setRouteResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFindRoute = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API_BASE_URL}/route`, {
        origin,
        destination
      });
      setRouteResult(res.data);
    } catch (err) {
      console.error("Failed to find route:", err);
      setRouteResult(null);
      setError('Unable to compute route right now. Please retry in a few moments.');
    } finally {
      setIsLoading(false);
    }
  };

  const getIcon = (routeName) => {
    if (routeName?.includes('Metro')) return <TrainFront size={16} />;
    if (routeName?.includes('Bus')) return <Bus size={16} />;
    return <Footprints size={16} />;
  };

  const getStatusClass = (status) => {
    if (status === 'BLOCKED') return 'bg-alert/20 text-alert border-alert/30';
    if (status === 'CONGESTED') return 'bg-warning/20 text-warning border-warning/30';
    return 'bg-accent/20 text-accent border-accent/30';
  };

  const routeEntries = routeResult?.routes ? Object.entries(routeResult.routes) : [];
  const recommendedRoute = routeResult?.recommended ? routeResult.routes?.[routeResult.recommended] : null;

  return (
    <div className="space-y-4">
      {/* Inputs */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3 bg-surfaceHover/60 border border-white/5 rounded-lg px-3 py-2 shadow-inner">
          <div className="w-6 flex justify-center"><div className="w-3 h-3 rounded-full border-2 border-primary" /></div>
          <select 
            value={origin} 
            onChange={(e) => setOrigin(e.target.value)}
            className="bg-transparent text-sm text-white w-full focus:outline-none appearance-none cursor-pointer"
          >
            {venues && venues.map(v => (
              <option key={v.id} value={v.name} className="bg-surface">{v.name}</option>
            ))}
          </select>
        </div>
        
        <div className="flex items-center gap-3 bg-surfaceHover/60 border border-white/5 rounded-lg px-3 py-2 shadow-inner">
          <div className="w-6 flex justify-center"><MapPin size={16} className="text-alert" /></div>
          <select 
            value={destination} 
            onChange={(e) => setDestination(e.target.value)}
            className="bg-transparent text-sm text-white w-full focus:outline-none appearance-none cursor-pointer"
          >
            {venues && [...venues].reverse().map(v => (
              <option key={v.id} value={v.name} className="bg-surface">{v.name}</option>
            ))}
          </select>
        </div>
        
        <button 
          onClick={handleFindRoute}
          disabled={isLoading || origin === destination}
          className="w-full py-2.5 bg-gradient-to-r from-primary to-primaryHover hover:from-primaryHover hover:to-primary text-white text-sm font-medium rounded-lg shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isLoading ? <span className="animate-pulse">Analyzing Crowds...</span> : <><Navigation size={16} /> Find Best Route</>}
        </button>
      </div>

      {error && (
        <div className="text-xs text-alert bg-alert/10 border border-alert/25 rounded-lg p-2">
          {error}
        </div>
      )}

      {/* Results */}
      {routeResult && routeResult.routes && (
        <div className="mt-4 pt-4 border-t border-white/10 animate-fade-in space-y-3">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Recommended Route</span>
            <span className="text-xs px-2 py-0.5 rounded bg-accent/20 text-accent font-bold uppercase">
              {routeResult.recommended}
            </span>
          </div>

          <div className="bg-surfaceHover/80 border border-accent/30 rounded-xl p-4 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-accent" />
            
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-bold text-white flex items-center gap-2">
                {getIcon(recommendedRoute?.name)}
                {recommendedRoute?.name || 'No route available'}
              </h3>
              <div className="flex items-center gap-1 text-accent text-sm font-bold bg-accent/10 px-2 py-0.5 rounded">
                <Clock size={14} />
                {recommendedRoute?.time}
              </div>
            </div>

            {routeResult.reason && (
              <div className="mb-3 flex items-start gap-1.5 text-xs text-warning bg-warning/10 p-2 rounded border border-warning/20">
                <ShieldAlert size={14} className="shrink-0 mt-0.5" />
                <p>{routeResult.reason}</p>
              </div>
            )}

            <div className="space-y-2 relative">
              <div className="absolute left-1.5 top-2 bottom-2 w-px bg-white/10 z-0" />
              {(recommendedRoute?.steps || []).map((step, idx) => (
                <div key={idx} className="flex gap-3 text-sm text-gray-300 relative z-10">
                  <div className="w-3 h-3 rounded-full bg-surface border-2 border-accent mt-1 shrink-0" />
                  <span>{step}</span>
                </div>
              ))}
            </div>

            {recommendedRoute?.avoid?.length > 0 && (
              <div className="mt-3 text-xs text-warning flex items-start gap-1.5 bg-warning/10 p-2 rounded border border-warning/20">
                <AlertTriangle size={14} className="shrink-0 mt-0.5" />
                <span>Avoid roads: {recommendedRoute.avoid.join(', ')}</span>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">All Alternatives</span>
            {routeEntries.map(([routeKey, route]) => (
              <div key={routeKey} className="bg-surfaceHover/50 border border-white/10 rounded-lg p-3">
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 text-sm text-white font-semibold">
                    {getIcon(route.name)}
                    <span>{route.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-300">{route.time} ({route.delay})</span>
                    <span className={`text-xs px-2 py-0.5 rounded border font-bold ${getStatusClass(route.status)}`}>
                      {route.status}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-400">
                  {route.avoid?.length > 0 ? `Avoid: ${route.avoid.join(', ')}` : 'No major blocked/overloaded roads on this option.'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RoutePlanner;
