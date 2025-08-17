// SocketIO stats updates (2s)
const socket = io({ transports: ["websocket"] });

socket.on("stats", (s) => {
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  if (s.distance_m != null) set("stat-distance", `${s.distance_m.toFixed ? s.distance_m.toFixed(1) : s.distance_m} m`);
  if (s.battery) {
    set("stat-batt-v", `${s.battery.voltage.toFixed(2)} V`);
    set("stat-batt-i", `${s.battery.current.toFixed(2)} A`);
    set("stat-batt-p", `${s.battery.power.toFixed(2)} W`);
    set("stat-batt-pct", `${Math.round(s.battery.percent)}%`);
  }
  if (s.cpu_temp != null) set("stat-cpu-temp", `${s.cpu_temp.toFixed(1)} °C`);
  if (s.cpu_load != null) set("stat-cpu-load", `${s.cpu_load.toFixed(0)}%`);
  if (s.wifi != null) set("stat-wifi", `${s.wifi} dBm`);
  if (s.led) set("stat-led", s.led);
});

// Mode toggle
async function setMode(mode) {
  await fetch("/api/mode", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({mode})});
  location.reload();
}

// Manual record controls
async function record(cmd) {
  await fetch(`/api/record/${cmd}`, { method:"POST" });
  if (cmd === "stop") alert("Recording stopped and saved.");
}

// Save settings (generic)
async function saveForm(formId, apiPath) {
  const form = document.getElementById(formId);
  const data = Object.fromEntries(new FormData(form).entries());
  await fetch(apiPath, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data) });
  alert("Saved.");
}

// Canvas overlay helpers (distance/battery)
export function drawOverlay(canvas, data) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width = canvas.clientWidth;
  const h = canvas.height = canvas.clientHeight;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.fillRect(w-210, h-80, 200, 70);
  ctx.fillStyle = "#e7f0ff"; ctx.font = "18px system-ui";
  const distTxt = data.distance_m!=null ? `${data.distance_m.toFixed(1)} m` : "--";
  ctx.fillText(`Distance: ${distTxt}`, w-200, h-50);
  const batt = data.battery || {};
  ctx.fillText(`Batt: ${batt.voltage?batt.voltage.toFixed(2):"--"}V ${batt.percent?Math.round(batt.percent):"--"}%`, w-200, h-28);
}
