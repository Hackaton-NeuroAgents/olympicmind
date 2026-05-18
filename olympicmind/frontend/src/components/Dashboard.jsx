import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const mockAthletes = [
  { id: 1, name: 'Luca Bianchi', discipline: '100m Sprint', latestScore: 87 },
  { id: 2, name: 'Giulia Rossi', discipline: 'Swimming', latestScore: 78 },
  { id: 3, name: 'Marco Esposito', discipline: 'Cycling', latestScore: 46 },
  { id: 4, name: 'Sara Conti', discipline: 'Gymnastics', latestScore: 92 },
  { id: 5, name: 'Davide Romano', discipline: 'Judo', latestScore: 58 },
];

const getScoreColor = (score) => {
  if (score > 80) return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30';
  if (score < 50) return 'text-red-400 bg-red-400/10 border-red-400/30';
  return 'text-amber-300 bg-amber-400/10 border-amber-400/30';
};

const Dashboard = () => {
  const [athletes, setAthletes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/team-readiness`);
        const incomingAthletes = Array.isArray(res.data?.athletes) ? res.data.athletes : [];
        setAthletes(incomingAthletes.length ? incomingAthletes : mockAthletes);
      } catch (err) {
        console.warn('Using mock team readiness data:', err);
        setAthletes(mockAthletes);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamData();
    const interval = setInterval(fetchTeamData, 15000);
    return () => clearInterval(interval);
  }, []);

  const teamAverageScore = athletes.length
    ? Math.round(athletes.reduce((sum, athlete) => sum + athlete.latestScore, 0) / athletes.length)
    : 0;
  const criticalAlerts = athletes.filter((athlete) => athlete.latestScore < 50).length;
  const progressStyle = {
    background: `conic-gradient(#10B981 ${teamAverageScore * 3.6}deg, rgba(255, 255, 255, 0.12) 0deg)`,
  };

  return (
    <div className="w-full space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass rounded-2xl p-6 shadow-2xl">
          <h2 className="text-lg font-semibold mb-4">Team Average Score</h2>
          <div className="flex items-center gap-5">
            <div
              className="w-28 h-28 rounded-full p-2 shrink-0"
              style={progressStyle}
              role="img"
              aria-label={`Team average score ${teamAverageScore}%`}
            >
              <div className="w-full h-full rounded-full bg-background/95 border border-white/10 flex items-center justify-center">
                <span className="text-2xl font-bold">{teamAverageScore}%</span>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-gray-400">Global readiness overview</p>
              <p className="text-xl font-semibold text-emerald-400">{teamAverageScore >= 80 ? 'Strong form' : 'Needs attention'}</p>
            </div>
          </div>
        </div>

        <div className="glass rounded-2xl p-6 shadow-2xl">
          <h2 className="text-lg font-semibold mb-4">Critical Alerts</h2>
          <div className="flex items-end gap-3">
            <p className="text-4xl font-bold text-red-400">{criticalAlerts}</p>
            <p className="text-sm text-gray-400 pb-1">Athletes below 50% readiness</p>
          </div>
          <div className="mt-5 text-sm text-gray-300">
            {criticalAlerts === 0 ? 'No athletes currently in critical state.' : 'Immediate coach review recommended.'}
          </div>
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden shadow-2xl">
        <div className="px-5 py-4 border-b border-white/5 bg-surface/40">
          <h2 className="text-lg font-semibold">Team Athletes Readiness</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px]">
            <thead className="text-left text-xs uppercase tracking-wider text-gray-400 bg-surface/30">
              <tr>
                <th className="px-5 py-3 font-medium">Athlete</th>
                <th className="px-5 py-3 font-medium">Discipline</th>
                <th className="px-5 py-3 font-medium">Latest Score</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td className="px-5 py-4 text-gray-400" colSpan={3}>
                    Loading team readiness...
                  </td>
                </tr>
              ) : (
                athletes.map((athlete) => (
                  <tr key={athlete.id} className="border-t border-white/5">
                    <td className="px-5 py-3 font-medium">{athlete.name}</td>
                    <td className="px-5 py-3 text-gray-300">{athlete.discipline}</td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-full border text-sm font-semibold ${getScoreColor(athlete.latestScore)}`}>
                        {athlete.latestScore}%
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
