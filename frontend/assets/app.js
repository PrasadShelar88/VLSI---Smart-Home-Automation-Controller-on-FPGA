const state = {
  baseUrl: localStorage.getItem("vlsiSmartHomeFpgaBackendUrl") || "http://127.0.0.1:8000",
};

const el = (id) => document.getElementById(id);

function apiUrl(path) {
  return `${state.baseUrl.replace(/\/$/, "")}${path}`;
}

function setBadge(ok, text) {
  const badge = el("connectionBadge");
  badge.textContent = text;
  badge.className = `badge ${ok ? "good" : "danger"}`;
}

function showError(message) {
  el("resultBox").textContent = message;
  setBadge(false, "Backend connection error");
}

async function request(path, options = {}) {
  const response = await fetch(apiUrl(path), options);
  const contentType = response.headers.get("Content-Type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof data === "object" ? data.detail || JSON.stringify(data) : data;
    throw new Error(detail || "Request failed");
  }
  return data;
}

async function testBackend() {
  try {
    await request("/health");
    setBadge(true, `Backend connected: ${state.baseUrl}`);
    await refreshLogs();
  } catch (error) {
    showError(`Backend connection error: ${error.message}. Start backend first.`);
  }
}

function payloadFromForm() {
  return {
    motion: el("motion").checked,
    dark: el("dark").checked,
    temperature: Number(el("temperature").value),
    temp_threshold: Number(el("tempThreshold").value),
    door_open: el("doorOpen").checked,
    security_mode: el("securityMode").checked,
    manual_override: el("manualOverride").checked,
    manual_light: el("manualLight").checked,
    manual_fan: el("manualFan").checked,
    manual_socket: el("manualSocket").checked,
    overcurrent: el("overcurrent").checked,
    no_motion_timeout: el("noMotionTimeout").checked,
  };
}

function yesNo(value) {
  return value === true || value === "True" || value === "true" ? "ON" : "OFF";
}

function renderResult(result) {
  el("stateValue").textContent = result.state;
  el("lightValue").textContent = result.light_pwm;
  el("fanValue").textContent = result.fan_pwm;
  el("alarmValue").textContent = yesNo(result.alarm);

  el("socketFlag").textContent = `Socket Relay: ${yesNo(result.socket_relay)}`;
  el("acFlag").textContent = `AC Relay: ${yesNo(result.ac_relay)}`;
  el("energyFlag").textContent = `Energy Saving: ${yesNo(result.energy_saving)}`;
  el("modeFlag").textContent = `Mode: ${result.mode}`;

  el("resultBox").innerHTML = `
    <strong>${result.state}</strong><br>
    Light PWM = ${result.light_pwm}, Fan PWM = ${result.fan_pwm},
    Socket = ${yesNo(result.socket_relay)}, AC = ${yesNo(result.ac_relay)},
    Alarm = ${yesNo(result.alarm)}<br>
    ${result.message}
  `;
}

async function evaluateController(event) {
  event.preventDefault();
  try {
    const result = await request("/api/controller/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payloadFromForm()),
    });
    setBadge(true, `Backend connected: ${state.baseUrl}`);
    renderResult(result);
    await refreshLogs();
  } catch (error) {
    showError(`Evaluate error: ${error.message}`);
  }
}

async function simulate() {
  try {
    const results = await request("/api/controller/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count: 10 }),
    });
    if (results.length) {
      renderResult(results[results.length - 1]);
    }
    setBadge(true, `Backend connected: ${state.baseUrl}`);
    await refreshLogs();
  } catch (error) {
    showError(`Simulation error: ${error.message}`);
  }
}

async function refreshLogs() {
  try {
    const data = await request("/api/logs");
    const rows = Array.isArray(data) ? data : data.logs || [];
    el("logCount").textContent = `${rows.length} records`;
    const body = el("logsBody");
    body.innerHTML = "";

    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="7">No logs yet.</td></tr>';
      return;
    }

    rows.slice(-15).reverse().forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.timestamp}</td>
        <td>${row.state}</td>
        <td>${row.temperature}</td>
        <td>${row.light_pwm}</td>
        <td>${row.fan_pwm}</td>
        <td>${yesNo(row.socket_relay)}</td>
        <td>${yesNo(row.alarm)}</td>
      `;
      body.appendChild(tr);
    });
  } catch (error) {
    showError(`Log error: ${error.message}`);
  }
}

async function clearLogs() {
  try {
    await request("/api/logs", { method: "DELETE" });
    await refreshLogs();
    el("resultBox").textContent = "Logs cleared.";
  } catch (error) {
    showError(`Clear logs error: ${error.message}`);
  }
}

function openEndpoint(path) {
  window.open(apiUrl(path), "_blank", "noopener");
}

function saveBackendUrl() {
  state.baseUrl = el("backendUrl").value.trim() || "http://127.0.0.1:8000";
  localStorage.setItem("vlsiSmartHomeFpgaBackendUrl", state.baseUrl);
  testBackend();
}

function bindEvents() {
  el("backendUrl").value = state.baseUrl;
  el("saveUrlBtn").addEventListener("click", saveBackendUrl);
  el("testBtn").addEventListener("click", testBackend);
  el("controllerForm").addEventListener("submit", evaluateController);
  el("simulateBtn").addEventListener("click", simulate);
  el("refreshLogsBtn").addEventListener("click", refreshLogs);
  el("clearBtn").addEventListener("click", clearLogs);
  el("csvBtn").addEventListener("click", () => openEndpoint("/api/export/csv"));
  el("pdfBtn").addEventListener("click", () => openEndpoint("/api/export/pdf"));
  el("rtlBtn").addEventListener("click", () => openEndpoint("/api/source/rtl"));
  el("tbBtn").addEventListener("click", () => openEndpoint("/api/source/testbench"));
}

bindEvents();
testBackend();
