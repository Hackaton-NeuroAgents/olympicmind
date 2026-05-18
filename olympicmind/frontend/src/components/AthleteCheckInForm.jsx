import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const metricFields = [
  { key: 'sleepQuality', label: 'Sleep Quality' },
  { key: 'stressLevel', label: 'Stress Level' },
  { key: 'physicalFatigue', label: 'Physical Fatigue' }
];

const toggleFields = [
  { key: 'followedNutritionPlan', label: 'Did you follow your nutrition plan?' },
  { key: 'hasJetlagSymptoms', label: 'Are you experiencing jetlag symptoms?' }
];

const AthleteCheckInForm = () => {
  const [formData, setFormData] = useState({
    sleepQuality: 7,
    stressLevel: 4,
    physicalFatigue: 5,
    followedNutritionPlan: true,
    hasJetlagSymptoms: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  const handleMetricChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: Number(value) }));
  };

  const handleToggleChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await axios.post(`${API_BASE_URL}/api/v1/audit`, {
        sleep_quality: formData.sleepQuality,
        stress_level: formData.stressLevel,
        physical_fatigue: formData.physicalFatigue,
        followed_nutrition_plan: formData.followedNutritionPlan,
        has_jetlag_symptoms: formData.hasJetlagSymptoms
      });
      showToast('success', 'Check-in submitted successfully.');
    } catch (err) {
      console.error('Failed to submit check-in:', err?.message || 'Unknown error');
      showToast('error', 'Unable to submit check-in. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {metricFields.map((field) => (
        <div key={field.key} className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <label htmlFor={field.key} className="font-medium text-gray-100">{field.label}</label>
            <span className="font-semibold text-accent">{formData[field.key]} / 10</span>
          </div>
          <input
            id={field.key}
            type="range"
            min="1"
            max="10"
            value={formData[field.key]}
            onChange={(e) => handleMetricChange(field.key, e.target.value)}
            className="w-full accent-primary"
          />
        </div>
      ))}

      {toggleFields.map((field) => (
        <div key={field.key} className="space-y-2">
          <p className="text-sm font-medium text-gray-100">{field.label}</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleToggleChange(field.key, true)}
              className={`px-3 py-2 rounded-lg border text-sm font-medium transition ${
                formData[field.key]
                  ? 'bg-accent/20 border-accent/40 text-accent'
                  : 'bg-surfaceHover/50 border-white/10 text-gray-300 hover:bg-surfaceHover/70'
              }`}
            >
              Yes
            </button>
            <button
              type="button"
              onClick={() => handleToggleChange(field.key, false)}
              className={`px-3 py-2 rounded-lg border text-sm font-medium transition ${
                !formData[field.key]
                  ? 'bg-accent/20 border-accent/40 text-accent'
                  : 'bg-surfaceHover/50 border-white/10 text-gray-300 hover:bg-surfaceHover/70'
              }`}
            >
              No
            </button>
          </div>
        </div>
      ))}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full py-2.5 bg-gradient-to-r from-primary to-primaryHover hover:from-primaryHover hover:to-primary text-white text-sm font-semibold rounded-lg shadow-lg shadow-primary/20 transition-all disabled:opacity-50"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Daily Check-in'}
      </button>

      {toast && (
        <div
          role="alert"
          aria-live="polite"
          className={`fixed bottom-4 right-4 z-50 px-4 py-3 rounded-lg border text-sm shadow-2xl ${
            toast.type === 'success'
              ? 'bg-accent/20 border-accent/40 text-accent'
              : 'bg-alert/20 border-alert/40 text-alert'
          }`}
        >
          {toast.message}
        </div>
      )}
    </form>
  );
};

export default AthleteCheckInForm;
