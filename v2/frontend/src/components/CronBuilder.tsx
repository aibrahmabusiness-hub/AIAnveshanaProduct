import React, { useState, useEffect } from 'react';

interface CronBuilderProps {
  value: string;
  onChange: (value: string) => void;
}

const DAYS = [
  { value: '1', label: 'Mon' },
  { value: '2', label: 'Tue' },
  { value: '3', label: 'Wed' },
  { value: '4', label: 'Thu' },
  { value: '5', label: 'Fri' },
  { value: '6', label: 'Sat' },
  { value: '0', label: 'Sun' },
];

const MONTHS = [
  { value: '1', label: 'Jan' },
  { value: '2', label: 'Feb' },
  { value: '3', label: 'Mar' },
  { value: '4', label: 'Apr' },
  { value: '5', label: 'May' },
  { value: '6', label: 'Jun' },
  { value: '7', label: 'Jul' },
  { value: '8', label: 'Aug' },
  { value: '9', label: 'Sep' },
  { value: '10', label: 'Oct' },
  { value: '11', label: 'Nov' },
  { value: '12', label: 'Dec' },
];

export default function CronBuilder({ value, onChange }: CronBuilderProps) {
  const parts = (value || '* * * * *').split(' ');
  const safeParts = parts.length === 5 ? parts : ['*', '*', '*', '*', '*'];

  const [minute, setMinute] = useState(safeParts[0]);
  const [hour, setHour] = useState(safeParts[1]);
  const [months, setMonths] = useState<string[]>(safeParts[3] === '*' ? [] : safeParts[3].split(','));
  const [days, setDays] = useState<string[]>(safeParts[4] === '*' ? [] : safeParts[4].split(','));

  // When props value changes from outside
  useEffect(() => {
    const p = (value || '* * * * *').split(' ');
    if (p.length === 5) {
      if (p[0] !== minute) setMinute(p[0]);
      if (p[1] !== hour) setHour(p[1]);
      const m = p[3] === '*' ? [] : p[3].split(',');
      if (m.join(',') !== months.join(',')) setMonths(m);
      const d = p[4] === '*' ? [] : p[4].split(',');
      if (d.join(',') !== days.join(',')) setDays(d);
    }
  }, [value]);

  const updateCron = (newMin: string, newHr: string, newMon: string[], newDay: string[]) => {
    const monStr = newMon.length === 0 || newMon.length === 12 ? '*' : newMon.join(',');
    const dayStr = newDay.length === 0 || newDay.length === 7 ? '*' : newDay.join(',');
    const newCron = `${newMin} ${newHr} * ${monStr} ${dayStr}`;
    onChange(newCron);
  };

  const handleMinuteChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setMinute(e.target.value);
    updateCron(e.target.value, hour, months, days);
  };

  const handleHourChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setHour(e.target.value);
    updateCron(minute, e.target.value, months, days);
  };

  const toggleDay = (dayVal: string) => {
    const newDays = days.includes(dayVal) ? days.filter(d => d !== dayVal) : [...days, dayVal];
    setDays(newDays);
    updateCron(minute, hour, months, newDays);
  };

  const toggleMonth = (monthVal: string) => {
    const newMonths = months.includes(monthVal) ? months.filter(m => m !== monthVal) : [...months, monthVal];
    setMonths(newMonths);
    updateCron(minute, hour, newMonths, days);
  };

  return (
    <div className="space-y-4 bg-slate-50 border border-slate-200 rounded-lg p-4">
      {/* Time Selection */}
      <div className="flex gap-4">
        <div className="flex-1 space-y-1">
          <label className="text-xs font-semibold text-slate-600">Hour</label>
          <select 
            value={hour} 
            onChange={handleHourChange}
            className="w-full text-sm rounded border border-slate-300 px-2 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="*">Every Hour (*)</option>
            {Array.from({ length: 24 }).map((_, i) => (
              <option key={i} value={i.toString()}>{i.toString().padStart(2, '0')}:00</option>
            ))}
          </select>
        </div>
        <div className="flex-1 space-y-1">
          <label className="text-xs font-semibold text-slate-600">Minute</label>
          <select 
            value={minute} 
            onChange={handleMinuteChange}
            className="w-full text-sm rounded border border-slate-300 px-2 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="*">Every Minute (*)</option>
            {Array.from({ length: 60 }).map((_, i) => (
              <option key={i} value={i.toString()}>{i.toString().padStart(2, '0')}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Days Checkboxes */}
      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-slate-600">Days of Week (Leave empty for every day)</label>
        <div className="flex flex-wrap gap-2">
          {DAYS.map(day => (
            <label key={day.value} className="flex items-center gap-1.5 bg-white border border-slate-200 px-2 py-1 rounded shadow-sm cursor-pointer hover:bg-slate-50">
              <input 
                type="checkbox" 
                checked={days.includes(day.value)} 
                onChange={() => toggleDay(day.value)}
                className="w-3.5 h-3.5 rounded text-blue-600 border-slate-300 focus:ring-blue-500"
              />
              <span className="text-xs text-slate-700">{day.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Months Checkboxes */}
      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-slate-600">Months (Leave empty for every month)</label>
        <div className="flex flex-wrap gap-2">
          {MONTHS.map(mon => (
            <label key={mon.value} className="flex items-center gap-1.5 bg-white border border-slate-200 px-2 py-1 rounded shadow-sm cursor-pointer hover:bg-slate-50">
              <input 
                type="checkbox" 
                checked={months.includes(mon.value)} 
                onChange={() => toggleMonth(mon.value)}
                className="w-3.5 h-3.5 rounded text-blue-600 border-slate-300 focus:ring-blue-500"
              />
              <span className="text-xs text-slate-700">{mon.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="pt-2">
        <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Raw Cron Expression</label>
        <div className="mt-1 flex items-center gap-2">
          <input 
            type="text" 
            value={value || '* * * * *'} 
            onChange={(e) => onChange(e.target.value)}
            className="flex-1 bg-slate-100 border border-slate-200 rounded px-2 py-1 text-xs font-mono text-slate-700 focus:outline-none focus:border-blue-400"
          />
        </div>
      </div>
    </div>
  );
}
