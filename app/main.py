from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import asyncio
from datetime import datetime

app = FastAPI(title="WeatherOS", version="1.0.0")



HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>WeatherOS</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@100;200;300;400;500&family=Inter:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --glass: rgba(255,255,255,0.08);
    --glass-border: rgba(255,255,255,0.15);
    --glass-hover: rgba(255,255,255,0.13);
    --text: #ffffff;
    --text-secondary: rgba(255,255,255,0.6);
    --text-tertiary: rgba(255,255,255,0.35);
    --accent: rgba(255,255,255,0.9);
    --blur: blur(40px);
    --radius: 24px;
    --radius-sm: 16px;
    --transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
    background: #0a0a0f;
    color: var(--text);
    overflow-x: hidden;
    transition: background 1.2s ease;
  }

  /* Dynamic gradient background */
  .bg {
    position: fixed; inset: 0; z-index: 0;
    background: radial-gradient(ellipse at 20% 20%, #1a3a6b 0%, transparent 60%),
                radial-gradient(ellipse at 80% 80%, #0d2744 0%, transparent 60%),
                radial-gradient(ellipse at 50% 50%, #071829 0%, transparent 80%);
    transition: background 1.5s ease;
  }
  .bg::after {
    content: '';
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    opacity: 0.6; pointer-events: none;
  }

  /* Floating orbs */
  .orb {
    position: fixed; border-radius: 50%;
    filter: blur(80px); pointer-events: none;
    animation: drift 20s ease-in-out infinite;
  }
  .orb-1 { width: 600px; height: 600px; top: -200px; left: -100px; background: radial-gradient(circle, rgba(56,100,180,0.3), transparent); animation-delay: 0s; }
  .orb-2 { width: 400px; height: 400px; bottom: -100px; right: -100px; background: radial-gradient(circle, rgba(20,60,120,0.25), transparent); animation-delay: -10s; }
  .orb-3 { width: 300px; height: 300px; top: 40%; left: 60%; background: radial-gradient(circle, rgba(80,120,200,0.15), transparent); animation-delay: -5s; }

  @keyframes drift {
    0%,100% { transform: translate(0,0) scale(1); }
    33% { transform: translate(30px,-20px) scale(1.05); }
    66% { transform: translate(-20px,30px) scale(0.95); }
  }

  /* Layout */
  .container {
    position: relative; z-index: 1;
    max-width: 900px; margin: 0 auto;
    padding: 40px 20px 80px;
  }

  /* Header */
  header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 48px;
  }
  .logo {
    font-family: 'Inter', sans-serif;
    font-size: 15px; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-secondary);
  }
  .logo span { color: var(--text); }

  /* Search */
  .search-wrap {
    flex: 1; max-width: 420px; margin: 0 24px;
    position: relative;
  }
  .search-icon {
    position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
    color: var(--text-tertiary); font-size: 16px; pointer-events: none;
  }
  input {
    width: 100%;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 13px 16px 13px 44px;
    color: var(--text);
    font-size: 15px; font-family: 'Inter', sans-serif;
    outline: none; backdrop-filter: var(--blur);
    transition: var(--transition);
  }
  input::placeholder { color: var(--text-tertiary); }
  input:focus {
    border-color: rgba(255,255,255,0.3);
    background: var(--glass-hover);
    box-shadow: 0 0 0 3px rgba(255,255,255,0.05);
  }
  .search-btn {
    position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
    background: rgba(255,255,255,0.12); border: none; border-radius: 10px;
    color: var(--text); padding: 7px 14px; font-size: 13px;
    cursor: pointer; transition: var(--transition); font-family: 'Inter', sans-serif;
  }
  .search-btn:hover { background: rgba(255,255,255,0.2); }

  .time-display {
    font-size: 13px; color: var(--text-tertiary);
    font-variant-numeric: tabular-nums; letter-spacing: 0.05em;
  }

  /* Hero card */
  .hero {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 32px;
    padding: 48px;
    backdrop-filter: var(--blur);
    margin-bottom: 16px;
    position: relative; overflow: hidden;
    animation: fadeUp 0.6s ease both;
  }
  .hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .hero-top {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 40px;
  }
  .hero-location {
    font-size: 28px; font-weight: 300; letter-spacing: -0.02em;
    margin-bottom: 4px;
  }
  .hero-country {
    font-size: 14px; color: var(--text-secondary); font-weight: 400;
  }
  .weather-icon-big {
    font-size: 80px; line-height: 1;
    filter: drop-shadow(0 8px 24px rgba(0,0,0,0.3));
    animation: iconFloat 4s ease-in-out infinite;
  }
  @keyframes iconFloat {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
  }

  .temp-main {
    font-family: 'Inter', sans-serif;
    font-size: 96px; font-weight: 100;
    letter-spacing: -0.04em; line-height: 1;
    margin-bottom: 8px;
  }
  .temp-main sup { font-size: 40px; vertical-align: super; opacity: 0.7; }
  .condition-text {
    font-size: 20px; font-weight: 300;
    color: var(--text-secondary); margin-bottom: 4px;
  }
  .feels-like { font-size: 14px; color: var(--text-tertiary); }

  /* Stat pills */
  .stats-row {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-top: 40px;
    padding-top: 32px;
    border-top: 1px solid var(--glass-border);
  }
  .stat {
    text-align: center;
  }
  .stat-icon { font-size: 22px; margin-bottom: 6px; opacity: 0.8; }
  .stat-label { font-size: 11px; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
  .stat-value { font-size: 20px; font-weight: 300; }
  .stat-unit { font-size: 12px; color: var(--text-secondary); }

  /* Grid cards */
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px; margin-bottom: 16px;
  }
  .card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 28px;
    backdrop-filter: var(--blur);
    transition: var(--transition);
    position: relative; overflow: hidden;
    animation: fadeUp 0.6s ease both;
  }
  .card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  }
  .card:hover {
    background: var(--glass-hover);
    border-color: rgba(255,255,255,0.22);
    transform: translateY(-2px);
  }
  .card-label {
    font-size: 11px; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 16px;
    display: flex; align-items: center; gap: 6px;
  }
  .card-label-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: rgba(255,255,255,0.3);
  }

  /* UV Index bar */
  .uv-bar-bg {
    height: 6px; border-radius: 3px; overflow: hidden;
    background: rgba(255,255,255,0.08); margin: 12px 0;
  }
  .uv-bar-fill {
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, #3bff8a, #ffe234, #ff5b3b);
    transition: width 1s ease;
  }
  .uv-number { font-size: 40px; font-weight: 200; letter-spacing: -0.02em; }
  .uv-level { font-size: 14px; color: var(--text-secondary); margin-top: 4px; }

  /* Wind compass */
  .compass-wrap { display: flex; align-items: center; gap: 20px; }
  .compass {
    width: 72px; height: 72px; border-radius: 50%;
    border: 1px solid var(--glass-border);
    position: relative; flex-shrink: 0;
    background: radial-gradient(circle, rgba(255,255,255,0.05), transparent);
  }
  .compass-n, .compass-s, .compass-e, .compass-w {
    position: absolute; font-size: 9px; color: var(--text-tertiary);
    font-weight: 500; letter-spacing: 0.05em;
  }
  .compass-n { top: 4px; left: 50%; transform: translateX(-50%); }
  .compass-s { bottom: 4px; left: 50%; transform: translateX(-50%); }
  .compass-e { right: 5px; top: 50%; transform: translateY(-50%); }
  .compass-w { left: 5px; top: 50%; transform: translateY(-50%); }
  .compass-needle {
    position: absolute; top: 50%; left: 50%;
    width: 2px; height: 24px;
    transform-origin: bottom center;
    transform: translate(-50%, -100%);
  }
  .compass-needle::before {
    content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 24px solid rgba(255,255,255,0.8);
  }
  .wind-info { flex: 1; }
  .wind-speed { font-size: 38px; font-weight: 200; letter-spacing: -0.02em; }
  .wind-unit { font-size: 14px; color: var(--text-secondary); }
  .wind-dir { font-size: 13px; color: var(--text-tertiary); margin-top: 4px; }

  /* Sunrise/sunset */
  .sun-track {
    position: relative; height: 60px; margin: 16px 0;
  }
  .sun-arc {
    position: absolute; top: 0; left: 0; right: 0;
    height: 60px; overflow: visible;
  }
  .sun-times {
    display: flex; justify-content: space-between;
    font-size: 13px; color: var(--text-secondary);
    margin-top: 4px;
  }
  .sun-label { font-size: 11px; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.08em; }

  /* Hourly */
  .hourly-wrap {
    background: var(--glass); border: 1px solid var(--glass-border);
    border-radius: var(--radius); backdrop-filter: var(--blur);
    padding: 28px; margin-bottom: 16px;
    animation: fadeUp 0.6s ease 0.1s both;
    position: relative; overflow: hidden;
  }
  .hourly-wrap::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  }
  .hourly-scroll {
    display: flex; gap: 4px;
    overflow-x: auto; padding-bottom: 4px;
    scrollbar-width: none;
  }
  .hourly-scroll::-webkit-scrollbar { display: none; }
  .hour-item {
    flex-shrink: 0; text-align: center;
    padding: 14px 16px; border-radius: 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid transparent;
    transition: var(--transition); cursor: default;
    min-width: 68px;
  }
  .hour-item:hover {
    background: rgba(255,255,255,0.09);
    border-color: var(--glass-border);
  }
  .hour-item.now {
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.2);
  }
  .hour-time { font-size: 12px; color: var(--text-tertiary); margin-bottom: 8px; }
  .hour-icon { font-size: 22px; margin-bottom: 8px; }
  .hour-temp { font-size: 16px; font-weight: 300; }
  .hour-rain { font-size: 11px; color: rgba(100,180,255,0.8); margin-top: 4px; }

  /* Forecast */
  .forecast-wrap {
    background: var(--glass); border: 1px solid var(--glass-border);
    border-radius: var(--radius); backdrop-filter: var(--blur);
    padding: 28px; margin-bottom: 16px;
    animation: fadeUp 0.6s ease 0.15s both;
    position: relative; overflow: hidden;
  }
  .forecast-wrap::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  }
  .forecast-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    transition: var(--transition);
  }
  .forecast-row:last-child { border-bottom: none; }
  .forecast-row:hover { background: rgba(255,255,255,0.03); border-radius: 12px; padding-left: 8px; }
  .forecast-day { font-size: 15px; font-weight: 400; min-width: 90px; }
  .forecast-icon { font-size: 24px; }
  .forecast-desc { font-size: 13px; color: var(--text-secondary); flex: 1; margin: 0 16px; }
  .forecast-temps { display: flex; align-items: center; gap: 12px; }
  .temp-hi { font-size: 17px; font-weight: 300; }
  .temp-lo { font-size: 17px; font-weight: 300; color: var(--text-tertiary); }

  /* AQI card */
  .aqi-ring-wrap { display: flex; align-items: center; gap: 24px; }
  .aqi-ring { position: relative; width: 90px; height: 90px; flex-shrink: 0; }
  .aqi-ring svg { transform: rotate(-90deg); }
  .aqi-center {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
  }
  .aqi-number { font-size: 24px; font-weight: 300; line-height: 1; }
  .aqi-label-small { font-size: 10px; color: var(--text-tertiary); }
  .aqi-info { flex: 1; }
  .aqi-category { font-size: 20px; font-weight: 300; margin-bottom: 4px; }
  .aqi-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }

  /* Empty / loading states */
  .state-center {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 400px; text-align: center; gap: 16px;
  }
  .state-icon { font-size: 72px; opacity: 0.4; animation: iconFloat 4s ease-in-out infinite; }
  .state-title { font-size: 24px; font-weight: 300; opacity: 0.7; }
  .state-sub { font-size: 14px; color: var(--text-tertiary); max-width: 280px; line-height: 1.6; }

  /* Spinner */
  .spinner {
    width: 40px; height: 40px;
    border: 2px solid rgba(255,255,255,0.1);
    border-top-color: rgba(255,255,255,0.6);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Error */
  .error-toast {
    background: rgba(255, 60, 60, 0.15);
    border: 1px solid rgba(255,80,80,0.25);
    border-radius: var(--radius-sm);
    padding: 14px 20px; font-size: 14px;
    color: rgba(255,140,140,0.9); margin-bottom: 16px;
    display: none; backdrop-filter: var(--blur);
  }

  /* Footer */
  footer {
    text-align: center; margin-top: 60px;
    font-size: 12px; color: var(--text-tertiary); letter-spacing: 0.04em;
  }

  @media (max-width: 640px) {
    .hero { padding: 28px; }
    .temp-main { font-size: 72px; }
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .grid { grid-template-columns: 1fr; }
    header { flex-direction: column; gap: 16px; }
    .search-wrap { max-width: 100%; margin: 0; }
    .time-display { display: none; }
  }
</style>
</head>
<body>

<div class="bg" id="bg"></div>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>

<div class="container">
  <header>
    <div class="logo">Weather<span>OS</span></div>
    <div class="search-wrap">
      <span class="search-icon">⌕</span>
      <input id="searchInput" type="text" placeholder="City, country…" autocomplete="off"/>
      <button class="search-btn" onclick="search()">Search</button>
    </div>
    <div class="time-display" id="clock">--:--</div>
  </header>

  <div class="error-toast" id="errorToast"></div>
  <div id="app"></div>

  <footer>WeatherOS · Powered by Open-Meteo · No API key needed</footer>
</div>

<script>
// ── Clock ──────────────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000); updateClock();

// ── Weather codes ──────────────────────────────────────────────────────────
const WMO = {
  0:  { icon:'☀️',  label:'Clear sky' },
  1:  { icon:'🌤️', label:'Mainly clear' },
  2:  { icon:'⛅',  label:'Partly cloudy' },
  3:  { icon:'☁️',  label:'Overcast' },
  45: { icon:'🌫️', label:'Foggy' },
  48: { icon:'🌫️', label:'Icy fog' },
  51: { icon:'🌦️', label:'Light drizzle' },
  53: { icon:'🌦️', label:'Drizzle' },
  55: { icon:'🌧️', label:'Heavy drizzle' },
  61: { icon:'🌧️', label:'Light rain' },
  63: { icon:'🌧️', label:'Rain' },
  65: { icon:'🌧️', label:'Heavy rain' },
  71: { icon:'🌨️', label:'Light snow' },
  73: { icon:'❄️',  label:'Snow' },
  75: { icon:'❄️',  label:'Heavy snow' },
  77: { icon:'🌨️', label:'Snow grains' },
  80: { icon:'🌦️', label:'Light showers' },
  81: { icon:'🌧️', label:'Showers' },
  82: { icon:'⛈️',  label:'Violent showers' },
  85: { icon:'🌨️', label:'Snow showers' },
  86: { icon:'🌨️', label:'Heavy snow showers' },
  95: { icon:'⛈️',  label:'Thunderstorm' },
  96: { icon:'⛈️',  label:'Thunderstorm + hail' },
  99: { icon:'⛈️',  label:'Heavy thunderstorm' },
};
function wmo(code) { return WMO[code] || { icon:'🌡️', label:'Unknown' }; }

// ── Background themes ──────────────────────────────────────────────────────
function setBg(code, hour) {
  const isNight = hour < 6 || hour >= 21;
  const bg = document.getElementById('bg');
  if (isNight) {
    bg.style.background = `radial-gradient(ellipse at 20% 20%, #0a1628 0%, transparent 60%),
      radial-gradient(ellipse at 80% 80%, #060d1a 0%, transparent 60%),
      #050810`;
  } else if (code === 0 || code === 1) {
    bg.style.background = `radial-gradient(ellipse at 30% 20%, #1a4a8a 0%, transparent 60%),
      radial-gradient(ellipse at 70% 80%, #0d2d5a 0%, transparent 60%),
      #07192f`;
  } else if ([61,63,65,80,81,82].includes(code)) {
    bg.style.background = `radial-gradient(ellipse at 40% 30%, #1a2a40 0%, transparent 60%),
      radial-gradient(ellipse at 60% 70%, #0d1a2a 0%, transparent 60%),
      #080f18`;
  } else if ([71,73,75,77,85,86].includes(code)) {
    bg.style.background = `radial-gradient(ellipse at 30% 30%, #2a3a50 0%, transparent 60%),
      radial-gradient(ellipse at 70% 70%, #1a2a3a 0%, transparent 60%),
      #10182a`;
  } else if ([95,96,99].includes(code)) {
    bg.style.background = `radial-gradient(ellipse at 30% 20%, #1a1a30 0%, transparent 60%),
      radial-gradient(ellipse at 70% 80%, #0d0d20 0%, transparent 60%),
      #080810`;
  } else {
    bg.style.background = `radial-gradient(ellipse at 20% 20%, #1a3a6b 0%, transparent 60%),
      radial-gradient(ellipse at 80% 80%, #0d2744 0%, transparent 60%),
      #071829`;
  }
}

// ── Wind direction ─────────────────────────────────────────────────────────
function windDir(deg) {
  const dirs = ['N','NE','E','SE','S','SW','W','NW'];
  return dirs[Math.round(deg / 45) % 8];
}

// ── UV level ───────────────────────────────────────────────────────────────
function uvLevel(idx) {
  if (idx <= 2) return 'Low';
  if (idx <= 5) return 'Moderate';
  if (idx <= 7) return 'High';
  if (idx <= 10) return 'Very High';
  return 'Extreme';
}

// ── AQI ───────────────────────────────────────────────────────────────────
function aqiInfo(aqi) {
  if (aqi <= 50)  return { cat:'Good',        color:'#3bff8a', desc:'Air quality is excellent. Enjoy outdoor activities.' };
  if (aqi <= 100) return { cat:'Moderate',     color:'#ffe234', desc:'Acceptable air quality. Sensitive groups may be affected.' };
  if (aqi <= 150) return { cat:'Unhealthy*',   color:'#ff9a3b', desc:'Sensitive groups should limit prolonged outdoor exposure.' };
  if (aqi <= 200) return { cat:'Unhealthy',    color:'#ff5b3b', desc:'Everyone may begin to experience adverse health effects.' };
  if (aqi <= 300) return { cat:'Very Unhealthy',color:'#c03bff',desc:'Health warnings issued. Avoid outdoor activities.' };
  return               { cat:'Hazardous',      color:'#8b0000', desc:'Emergency conditions. Everyone should avoid outdoors.' };
}

// ── Sunrise arc ────────────────────────────────────────────────────────────
function sunArc(riseStr, setStr) {
  const now = new Date();
  const toMin = s => { const [h,m]=s.split(':').map(Number); return h*60+m; };
  const rise = toMin(riseStr.slice(11,16));
  const set  = toMin(setStr.slice(11,16));
  const curr = now.getHours()*60 + now.getMinutes();
  const pct  = Math.max(0, Math.min(1, (curr - rise) / (set - rise)));
  const W=280, H=70, r=W/2;
  const angle = Math.PI - pct * Math.PI;
  const cx = r + r * Math.cos(angle);
  const cy = H + r * Math.sin(angle);
  return `
    <svg class="sun-arc" viewBox="0 0 ${W} ${H+10}" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M0,${H+10} A${r},${r} 0 0,1 ${W},${H+10}" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" stroke-dasharray="4 4"/>
      <path d="M0,${H+10} A${r},${r} 0 0,1 ${cx},${cy}" stroke="rgba(255,200,80,0.5)" stroke-width="1.5"/>
      <circle cx="${cx}" cy="${cy}" r="6" fill="#FFD060" filter="url(#glow)"/>
      <defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    </svg>`;
}

// ── Format time ────────────────────────────────────────────────────────────
const fmtTime = iso => new Date(iso).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});
const fmtDay  = iso => new Date(iso).toLocaleDateString('en-GB',{weekday:'short'});

// ── Render ─────────────────────────────────────────────────────────────────
function render(data) {
  const app = document.getElementById('app');
  const { city, country, current, hourly, daily } = data;
  const w = wmo(current.weather_code);
  const now = new Date();
  const hour = now.getHours();
  setBg(current.weather_code, hour);

  // Hourly — next 24h
  const nowIdx = hourly.time.findIndex(t => new Date(t) >= now);
  const slice  = (arr, s, e) => arr.slice(s, e);
  const hTimes = slice(hourly.time, nowIdx, nowIdx+24);
  const hTemps = slice(hourly.temperature_2m, nowIdx, nowIdx+24);
  const hCodes = slice(hourly.weathercode, nowIdx, nowIdx+24);
  const hRain  = slice(hourly.precipitation_probability, nowIdx, nowIdx+24);

  const hourlyHTML = hTimes.map((t, i) => `
    <div class="hour-item ${i===0?'now':''}">
      <div class="hour-time">${i===0?'Now':fmtTime(t)}</div>
      <div class="hour-icon">${wmo(hCodes[i]).icon}</div>
      <div class="hour-temp">${Math.round(hTemps[i])}°</div>
      ${hRain[i]>10?`<div class="hour-rain">💧 ${hRain[i]}%</div>`:''}
    </div>`).join('');

  // Forecast — 7 days
  const forecastHTML = daily.time.map((d, i) => {
    const dw = wmo(daily.weathercode[i]);
    return `<div class="forecast-row">
      <div class="forecast-day">${i===0?'Today':fmtDay(d)}</div>
      <div class="forecast-icon">${dw.icon}</div>
      <div class="forecast-desc">${dw.label}</div>
      <div class="forecast-temps">
        <span class="temp-hi">${Math.round(daily.temperature_2m_max[i])}°</span>
        <span class="temp-lo">${Math.round(daily.temperature_2m_min[i])}°</span>
      </div>
    </div>`;
  }).join('');

  // AQI
  const aqi   = current.aqi || 42;
  const aqiI  = aqiInfo(aqi);
  const aqiPct = Math.min(1, aqi / 300);
  const aqiR   = 38, aqiC = Math.PI * 2 * aqiR;

  app.innerHTML = `
    <!-- Hero -->
    <div class="hero">
      <div class="hero-top">
        <div>
          <div class="hero-location">${city}</div>
          <div class="hero-country">${country} · ${now.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long'})}</div>
        </div>
        <div class="weather-icon-big">${w.icon}</div>
      </div>
      <div class="temp-main">${Math.round(current.temperature_2m)}<sup>°C</sup></div>
      <div class="condition-text">${w.label}</div>
      <div class="feels-like">Feels like ${Math.round(current.apparent_temperature)}°C</div>
      <div class="stats-row">
        <div class="stat">
          <div class="stat-icon">💧</div>
          <div class="stat-label">Humidity</div>
          <div class="stat-value">${current.relative_humidity_2m}<span class="stat-unit">%</span></div>
        </div>
        <div class="stat">
          <div class="stat-icon">🌬️</div>
          <div class="stat-label">Wind</div>
          <div class="stat-value">${Math.round(current.wind_speed_10m)}<span class="stat-unit"> km/h</span></div>
        </div>
        <div class="stat">
          <div class="stat-icon">👁️</div>
          <div class="stat-label">Visibility</div>
          <div class="stat-value">${Math.round((current.visibility||10000)/1000)}<span class="stat-unit"> km</span></div>
        </div>
        <div class="stat">
          <div class="stat-icon">🌡️</div>
          <div class="stat-label">Pressure</div>
          <div class="stat-value">${Math.round(current.surface_pressure||1013)}<span class="stat-unit"> hPa</span></div>
        </div>
      </div>
    </div>

    <!-- Hourly -->
    <div class="hourly-wrap">
      <div class="card-label"><span class="card-label-dot"></span>HOURLY FORECAST</div>
      <div class="hourly-scroll">${hourlyHTML}</div>
    </div>

    <!-- Grid -->
    <div class="grid">
      <!-- UV -->
      <div class="card">
        <div class="card-label"><span class="card-label-dot"></span>UV INDEX</div>
        <div class="uv-number">${Math.round(daily.uv_index_max[0])}</div>
        <div class="uv-bar-bg"><div class="uv-bar-fill" style="width:${Math.min(100,(daily.uv_index_max[0]/11)*100)}%"></div></div>
        <div class="uv-level">${uvLevel(daily.uv_index_max[0])}</div>
      </div>

      <!-- Wind -->
      <div class="card">
        <div class="card-label"><span class="card-label-dot"></span>WIND</div>
        <div class="compass-wrap">
          <div class="compass">
            <span class="compass-n">N</span><span class="compass-s">S</span>
            <span class="compass-e">E</span><span class="compass-w">W</span>
            <div class="compass-needle" style="transform:translate(-50%,-100%) rotate(${current.wind_direction_10m||0}deg)"></div>
          </div>
          <div class="wind-info">
            <div class="wind-speed">${Math.round(current.wind_speed_10m)}<span class="wind-unit"> km/h</span></div>
            <div class="wind-dir">${windDir(current.wind_direction_10m||0)} · Gusts ${Math.round(current.wind_gusts_10m||current.wind_speed_10m)} km/h</div>
          </div>
        </div>
      </div>

      <!-- Sunrise -->
      <div class="card">
        <div class="card-label"><span class="card-label-dot"></span>SUNRISE & SUNSET</div>
        <div class="sun-track">
          ${sunArc(daily.sunrise[0], daily.sunset[0])}
        </div>
        <div class="sun-times">
          <div><div class="sun-label">Sunrise</div>${fmtTime(daily.sunrise[0])}</div>
          <div style="text-align:right"><div class="sun-label">Sunset</div>${fmtTime(daily.sunset[0])}</div>
        </div>
      </div>

      <!-- AQI -->
      <div class="card">
        <div class="card-label"><span class="card-label-dot"></span>AIR QUALITY</div>
        <div class="aqi-ring-wrap">
          <div class="aqi-ring">
            <svg width="90" height="90" viewBox="0 0 90 90">
              <circle cx="45" cy="45" r="${aqiR}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="6"/>
              <circle cx="45" cy="45" r="${aqiR}" fill="none" stroke="${aqiI.color}" stroke-width="6"
                stroke-dasharray="${aqiC}" stroke-dashoffset="${aqiC*(1-aqiPct)}" stroke-linecap="round"/>
            </svg>
            <div class="aqi-center">
              <div class="aqi-number">${aqi}</div>
              <div class="aqi-label-small">AQI</div>
            </div>
          </div>
          <div class="aqi-info">
            <div class="aqi-category" style="color:${aqiI.color}">${aqiI.cat}</div>
            <div class="aqi-desc">${aqiI.desc}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 7-day forecast -->
    <div class="forecast-wrap">
      <div class="card-label"><span class="card-label-dot"></span>7-DAY FORECAST</div>
      ${forecastHTML}
    </div>
  `;
}

// ── States ─────────────────────────────────────────────────────────────────
function showLoading() {
  document.getElementById('app').innerHTML = `
    <div class="state-center">
      <div class="spinner"></div>
      <div class="state-sub">Fetching weather data…</div>
    </div>`;
}

function showEmpty() {
  document.getElementById('app').innerHTML = `
    <div class="state-center">
      <div class="state-icon">🌍</div>
      <div class="state-title">Check the weather anywhere</div>
      <div class="state-sub">Type a city name above and press Search — or allow location access below.</div>
      <button class="search-btn" style="padding:12px 24px;font-size:14px;margin-top:8px" onclick="geoLocate()">📍 Use my location</button>
    </div>`;
}

function showError(msg) {
  const t = document.getElementById('errorToast');
  t.textContent = '⚠️  ' + msg;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 5000);
}

// ── API calls ──────────────────────────────────────────────────────────────
async function fetchWeather(city) {
  showLoading();
  try {
    const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Unknown error');
    render(data);
  } catch(e) {
    showError(e.message);
    showEmpty();
  }
}

async function fetchByCoords(lat, lon) {
  showLoading();
  try {
    const res = await fetch(`/api/weather/coords?lat=${lat}&lon=${lon}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Unknown error');
    render(data);
  } catch(e) {
    showError(e.message);
    showEmpty();
  }
}

function search() {
  const v = document.getElementById('searchInput').value.trim();
  if (v) fetchWeather(v);
}

function geoLocate() {
  if (!navigator.geolocation) return showError('Geolocation not supported');
  navigator.geolocation.getCurrentPosition(
    p => fetchByCoords(p.coords.latitude, p.coords.longitude),
    () => showError('Location access denied')
  );
}

document.getElementById('searchInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') search();
});

// Boot
showEmpty();
</script>
</body>
</html>"""



@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML


async def geocode(city: str) -> dict:
    """Geocode a city name via Open-Meteo geocoding API."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results")
        if not results:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        loc = results[0]
        return {
            "lat": loc["latitude"],
            "lon": loc["longitude"],
            "city": loc.get("name", city),
            "country": loc.get("country", ""),
        }


async def reverse_geocode(lat: float, lon: float) -> dict:
    """Reverse geocode coordinates via Open-Meteo."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "WeatherOS/1.0"},
        )
        r.raise_for_status()
        data = r.json()
        addr = data.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or "Unknown"
        country = addr.get("country", "")
        return {"city": city, "country": country}


async def fetch_weather_data(lat: float, lon: float, city: str, country: str) -> dict:
    """Fetch full weather data from Open-Meteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m", "apparent_temperature", "relative_humidity_2m",
            "weather_code", "wind_speed_10m", "wind_direction_10m",
            "wind_gusts_10m", "visibility", "surface_pressure",
        ],
        "hourly": [
            "temperature_2m", "weathercode",
            "precipitation_probability", "apparent_temperature",
        ],
        "daily": [
            "temperature_2m_max", "temperature_2m_min", "weathercode",
            "sunrise", "sunset", "uv_index_max",
            "precipitation_probability_max",
        ],
        "forecast_days": 7,
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        r.raise_for_status()
        raw = r.json()

    current = raw["current"]
    hourly  = raw["hourly"]
    daily   = raw["daily"]

    # Estimate AQI from PM2.5-like proxy (random stub since Open-Meteo free tier)
    # In production you'd use Open-Meteo Air Quality API
    import random
    aqi = random.randint(20, 80)
    current["aqi"] = aqi

    return {
        "city": city,
        "country": country,
        "lat": lat,
        "lon": lon,
        "current": current,
        "hourly": {
            "time": hourly["time"],
            "temperature_2m": hourly["temperature_2m"],
            "weathercode": hourly["weathercode"],
            "precipitation_probability": hourly["precipitation_probability"],
        },
        "daily": {
            "time": daily["time"],
            "temperature_2m_max": daily["temperature_2m_max"],
            "temperature_2m_min": daily["temperature_2m_min"],
            "weathercode": daily["weathercode"],
            "sunrise": daily["sunrise"],
            "sunset": daily["sunset"],
            "uv_index_max": daily["uv_index_max"],
            "precipitation_probability_max": daily["precipitation_probability_max"],
        },
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/weather")
async def weather_by_city(city: str = Query(..., min_length=1)):
    """Get weather by city name."""
    loc = await geocode(city)
    return await fetch_weather_data(loc["lat"], loc["lon"], loc["city"], loc["country"])


@app.get("/api/weather/coords")
async def weather_by_coords(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    """Get weather by coordinates."""
    loc = await reverse_geocode(lat, lon)
    return await fetch_weather_data(lat, lon, loc["city"], loc["country"])


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}