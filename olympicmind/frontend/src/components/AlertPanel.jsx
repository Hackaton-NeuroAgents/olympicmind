import React from 'react';
import { AlertTriangle, CheckCircle2, MapPin } from 'lucide-react';

const AlertPanel = ({ incidents }) => {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-3 opacity-60">
        <div className="w-12 h-12 rounded-full bg-surfaceHover flex items-center justify-center">
          <CheckCircle2 size={24} className="text-accent" />
        </div>
        <p className="text-sm font-medium">No active incidents. Milan is clear.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {incidents.map((incident, idx) => (
        <div key={idx} className="bg-alert/10 border border-alert/20 rounded-xl p-3 flex gap-3 shadow-lg shadow-alert/5">
          <div className="shrink-0 mt-0.5">
            <AlertTriangle className="text-alert animate-pulse" size={20} />
          </div>
          <div className="flex-1">
            <div className="flex justify-between items-start mb-1">
              <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                <MapPin size={14} className="text-gray-400" />
                {incident.venue}
              </h4>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-alert/20 text-alert">
                {incident.level}% Full
              </span>
            </div>
            <p className="text-xs text-gray-300 mb-2">{incident.message}</p>
            <div className="flex items-center gap-1.5 text-xs text-accent font-medium">
              <CheckCircle2 size={12} />
              <span>WhatsApp Alert Sent to Team</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertPanel;
