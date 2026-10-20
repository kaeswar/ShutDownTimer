import React, { useState, useEffect } from 'react';

const PRESETS = [30, 60, 90, 120];
const RADIUS = 110;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return [h, m, s].map((n) => String(n).padStart(2, '0')).join(':');
};

export default function ShutdownTimer() {
  const [total, setTotal] = useState(0);
  const [endsAt, setEndsAt] = useState(0);
  const [now, setNow] = useState(Date.now());
  const [custom, setCustom] = useState('');
  const [error, setError] = useState('');

  const active = endsAt > 0;
  const remaining = active ? Math.max(0, (endsAt - now) / 1000) : 0;
  const fraction = total ? remaining / total : 0;

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 250);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (active && remaining <= 0) cancel();
  }, [remaining, active]);

  const start = (minutes) => {
    setTotal(minutes * 60);
    setEndsAt(Date.now() + minutes * 60000);
    setCustom('');
    setError('');
  };

  const cancel = () => {
    setTotal(0);
    setEndsAt(0);
  };

  const startCustom = () => {
    const minutes = parseInt(custom, 10);
    if (!(minutes >= 1 && minutes <= 1440)) {
      setError('Choose between 1 and 1440 minutes');
      return;
    }
    start(minutes);
  };

  const endTime = active
    ? new Date(endsAt).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
    : null;

  return (
    <div className="min-h-screen bg-[#0f1220] flex items-center justify-center p-4 text-[#e8eaf6]">
      <div className="w-full max-w-sm text-center">
        <h1 className="text-2xl font-bold">Shutdown Timer</h1>
        <p className={`text-sm mt-1 ${active ? 'text-[#6c8cff]' : 'text-[#7b82a8]'}`}>
          {active ? `Shuts down at ${endTime}` : 'No timer active'}
        </p>

        <div className="relative w-64 h-64 mx-auto my-6">
          <svg viewBox="0 0 256 256" className="w-full h-full -rotate-90">
            <circle cx="128" cy="128" r={RADIUS} fill="none" stroke="#171b2e" strokeWidth="12" />
            <circle
              cx="128"
              cy="128"
              r={RADIUS}
              fill="none"
              stroke="#6c8cff"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={CIRCUMFERENCE * (1 - fraction)}
              className="transition-[stroke-dashoffset] duration-300"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-4xl font-bold tabular-nums ${active ? '' : 'text-[#7b82a8]'}`}>
              {formatTime(remaining)}
            </span>
            <span className="text-[10px] font-bold tracking-widest text-[#7b82a8] mt-2">
              {active ? 'UNTIL SHUTDOWN' : 'NO TIMER'}
            </span>
          </div>
        </div>

        {active ? (
          <button
            onClick={cancel}
            className="px-12 py-3 rounded-lg font-bold bg-[#ff5c7a] hover:bg-[#ff7b93] text-white transition-colors"
          >
            Cancel Shutdown
          </button>
        ) : (
          <>
            <div className="flex justify-center gap-2">
              {PRESETS.map((m) => (
                <button
                  key={m}
                  onClick={() => start(m)}
                  className="px-4 py-2 rounded-lg font-bold bg-[#222741] hover:bg-[#2c3254] transition-colors"
                >
                  {m % 60 === 0 ? `${m / 60}h` : `${m}m`}
                </button>
              ))}
            </div>
            <div className="flex justify-center items-center gap-2 mt-4">
              <input
                type="number"
                min="1"
                max="1440"
                value={custom}
                onChange={(e) => setCustom(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && startCustom()}
                className="w-28 px-3 py-2 rounded-lg text-center bg-[#222741] border border-[#222741] focus:border-[#6c8cff] outline-none"
              />
              <span className="text-sm text-[#7b82a8]">min</span>
              <button
                onClick={startCustom}
                className="px-5 py-2 rounded-lg font-bold bg-[#6c8cff] hover:bg-[#839fff] text-white transition-colors"
              >
                Start
              </button>
            </div>
          </>
        )}

        <p className="h-5 mt-4 text-xs text-[#ff5c7a]">{error}</p>
        <p className="text-xs text-[#7b82a8]">
          Demo interface only. The desktop app runs the real shutdown command.
        </p>
      </div>
    </div>
  );
}
