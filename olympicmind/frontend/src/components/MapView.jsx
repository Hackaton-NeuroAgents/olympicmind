import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Center map around Milan initially
const MILAN_CENTER = [45.485, 9.14];

const MapUpdater = ({ venues }) => {
  const map = useMap();
  useEffect(() => {
    if (venues && venues.length > 0) {
      const bounds = L.latLngBounds(venues.map(v => [v.lat, v.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [venues, map]);
  return null;
};

const MapView = ({ venues }) => {
  const getColor = (status) => {
    switch(status) {
      case 'HIGH': return '#EF4444'; // alert red
      case 'MEDIUM': return '#F59E0B'; // warning yellow
      case 'LOW': return '#10B981'; // accent green
      default: return '#3B82F6';
    }
  };

  return (
    <MapContainer 
      center={MILAN_CENTER} 
      zoom={12} 
      className="w-full h-full bg-[#0a0a0a]"
      zoomControl={false}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
      />
      
      {venues.map((venue) => (
        <CircleMarker
          key={venue.id}
          center={[venue.lat, venue.lng]}
          radius={venue.crowd_level > 80 ? 18 : venue.crowd_level > 50 ? 14 : 10}
          pathOptions={{ 
            fillColor: getColor(venue.status),
            fillOpacity: 0.7,
            color: getColor(venue.status),
            weight: 2
          }}
        >
          <Popup className="custom-popup">
            <div className="p-1 min-w-[150px]">
              <h3 className="font-bold text-gray-800 text-sm mb-1">{venue.name}</h3>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-600">Status:</span>
                <span className={`font-bold ${venue.status === 'HIGH' ? 'text-red-500' : venue.status === 'MEDIUM' ? 'text-yellow-500' : 'text-green-500'}`}>
                  {venue.status}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                <div 
                  className={`h-2 rounded-full ${venue.status === 'HIGH' ? 'bg-red-500' : venue.status === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'}`} 
                  style={{ width: `${venue.crowd_level}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 text-right">{venue.crowd_level}% Full</p>
            </div>
          </Popup>
        </CircleMarker>
      ))}
      <MapUpdater venues={venues} />
    </MapContainer>
  );
};

export default MapView;
