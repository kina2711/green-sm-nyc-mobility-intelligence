const FILES = ["summary", "market", "zones", "fares", "hourly", "metadata"];
const COLORS = ["#b8ff3d", "#36e0d0", "#ffc857", "#ff6b98", "#9b8cff"];
const DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
const state = { data: {}, charts: {}, year: "all", borough: "all", service: "all", selectedZone: null };
const number = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 });

async function loadData() {
  const entries = await Promise.all(FILES.map(async (name) => {
    const response = await fetch(`data/${name}.json`);
    if (!response.ok) throw new Error(`Could not load ${name}.json (${response.status})`);
    return [name, await response.json()];
  }));
  state.data = Object.fromEntries(entries);
  validateContracts();
}

function validateContracts() {
  const versions = new Set(FILES.map((name) => state.data[name].schema_version));
  if (versions.size !== 1) throw new Error("Dashboard datasets use incompatible contract versions.");
  for (const name of FILES) {
    if (!Array.isArray(state.data[name].data) || state.data[name].row_count !== state.data[name].data.length) {
      throw new Error(`Invalid ${name} dataset contract.`);
    }
  }
}

function rows(name) { return state.data[name].data; }
function monthYear(value) { return String(value).slice(0, 4); }
function monthLabel(value) { return new Date(`${String(value).slice(0, 10)}T00:00:00`).toLocaleDateString("en-US", { month: "short", year: "2-digit" }); }

function setupFilters() {
  const years = [...new Set(rows("market").map((row) => monthYear(row.pickup_month)))].sort();
  const boroughs = [...new Set(rows("zones").map((row) => row.borough))].sort();
  const services = [...new Set(rows("market").map((row) => row.service_category))].sort();
  fillSelect("year-filter", ["all", ...years], "All years");
  fillSelect("borough-filter", ["all", ...boroughs], "All boroughs");
  fillSelect("service-filter", ["all", ...services], "All services");
  document.querySelector("#year-filter").addEventListener("change", (event) => { state.year = event.target.value; render(); });
  document.querySelector("#borough-filter").addEventListener("change", (event) => { state.borough = event.target.value; render(); });
  document.querySelector("#service-filter").addEventListener("change", (event) => { state.service = event.target.value; render(); });
}

function fillSelect(id, values, allLabel) {
  document.querySelector(`#${id}`).replaceChildren(...values.map((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value === "all" ? allLabel : value;
    return option;
  }));
}

function marketRows() {
  return rows("market").filter((row) => (state.year === "all" || monthYear(row.pickup_month) === state.year) && (state.borough === "all" || row.borough === state.borough) && (state.service === "all" || row.service_category === state.service));
}
function zoneRows() { return rows("zones").filter((row) => state.borough === "all" || row.borough === state.borough); }

function aggregateMarket() {
  const grouped = new Map();
  for (const row of marketRows()) {
    const key = `${row.pickup_month}|${row.operator}`;
    const current = grouped.get(key) || { pickup_month: row.pickup_month, operator: row.operator, completed_trips: 0, observed_fare: 0, fare_trip_count: 0 };
    current.completed_trips += row.completed_trips;
    current.observed_fare += row.observed_fare || 0;
    current.fare_trip_count += row.fare_trip_count || 0;
    grouped.set(key, current);
  }
  return [...grouped.values()].map((row) => ({ ...row, avg_observed_fare: row.fare_trip_count ? row.observed_fare / row.fare_trip_count : null }));
}

function updateKpis() {
  const market = aggregateMarket();
  const zones = zoneRows();
  const trips = market.reduce((sum, row) => sum + row.completed_trips, 0);
  const fareTotal = market.reduce((sum, row) => sum + row.observed_fare, 0);
  const fareTrips = market.reduce((sum, row) => sum + row.fare_trip_count, 0);
  document.querySelector("#kpi-trips").textContent = number.format(trips);
  document.querySelector("#kpi-zones").textContent = number.format(zones.length);
  document.querySelector("#kpi-fare").textContent = fareTrips ? money.format(fareTotal / fareTrips) : "—";
  document.querySelector("#kpi-operators").textContent = new Set(market.map((row) => row.operator)).size;
  const months = market.map((row) => String(row.pickup_month).slice(0, 10)).sort();
  document.querySelector("#period-label").textContent = months.length ? `${monthLabel(months[0])} — ${monthLabel(months.at(-1))}` : "No matching records";
}

function chartOptions(extra = {}) {
  return { responsive: true, maintainAspectRatio: false, interaction: { intersect: false, mode: "index" }, plugins: { legend: { labels: { color: "#8ba39a", boxWidth: 9, usePointStyle: true, font: { family: "DM Mono", size: 10 } } } }, scales: { x: { ticks: { color: "#8ba39a", maxRotation: 0, font: { family: "DM Mono", size: 9 } }, grid: { color: "#ffffff08" } }, y: { beginAtZero: true, ticks: { color: "#8ba39a", font: { family: "DM Mono", size: 9 } }, grid: { color: "#ffffff0b" } } }, ...extra };
}

function upsertChart(name, config) {
  state.charts[name]?.destroy();
  state.charts[name] = new Chart(document.querySelector(`#${name}`), config);
}

function renderMarketCharts() {
  const data = aggregateMarket();
  const months = [...new Set(data.map((row) => row.pickup_month))].sort();
  const operators = [...new Set(data.map((row) => row.operator))].sort();
  const datasets = operators.map((operator, index) => ({ label: operator, data: months.map((month) => data.find((row) => row.pickup_month === month && row.operator === operator)?.completed_trips || 0), borderColor: COLORS[index % COLORS.length], backgroundColor: `${COLORS[index % COLORS.length]}22`, tension: .25, pointRadius: 1.5, borderWidth: 2 }));
  upsertChart("market-chart", { type: "line", data: { labels: months.map(monthLabel), datasets }, options: chartOptions() });
  const fareDatasets = operators.map((operator, index) => ({ label: operator, data: months.map((month) => data.find((row) => row.pickup_month === month && row.operator === operator)?.avg_observed_fare || null), borderColor: COLORS[index % COLORS.length], backgroundColor: COLORS[index % COLORS.length], tension: .25, pointRadius: 1.5, borderWidth: 2 }));
  upsertChart("fare-chart", { type: "line", data: { labels: months.map(monthLabel), datasets: fareDatasets }, options: chartOptions({ scales: { x: chartOptions().scales.x, y: { ...chartOptions().scales.y, ticks: { color: "#8ba39a", callback: (value) => `$${value}` } } } }) });
}

function renderZones() {
  const zones = zoneRows().sort((a, b) => b.opportunity_score - a.opportunity_score);
  if (!zones.some((zone) => zone.zone_id === state.selectedZone)) state.selectedZone = zones[0]?.zone_id;
  const top = zones.slice(0, 8).reverse();
  upsertChart("zone-chart", { type: "bar", data: { labels: top.map((row) => row.zone_name), datasets: [{ data: top.map((row) => row.opportunity_score), backgroundColor: top.map((_, index) => index === top.length - 1 ? "#b8ff3d" : "#36e0d088"), borderWidth: 0 }] }, options: chartOptions({ indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { min: 0, max: 100, ticks: { color: "#8ba39a" }, grid: { color: "#ffffff0b" } }, y: { ticks: { color: "#edf7f1", font: { size: 10 } }, grid: { display: false } } } }) });
  const body = document.querySelector("#zone-table");
  body.replaceChildren(...zones.map((zone, index) => {
    const row = document.createElement("tr");
    if (zone.zone_id === state.selectedZone) row.classList.add("active");
    const yoy = zone.yoy_completed_trip_growth == null ? "n/a" : `${(zone.yoy_completed_trip_growth * 100).toFixed(1)}%`;
    row.innerHTML = `<td>${String(index + 1).padStart(2, "0")}</td><td>${zone.zone_name}</td><td>${zone.borough}</td><td>${number.format(zone.completed_trips)}</td><td>${yoy}</td><td>${money.format(zone.avg_observed_fare)}</td><td>${zone.opportunity_score.toFixed(1)}</td>`;
    row.addEventListener("click", () => { state.selectedZone = zone.zone_id; renderZones(); renderHeatmap(); });
    return row;
  }));
  renderSelectedZone(zones.find((zone) => zone.zone_id === state.selectedZone));
}

function renderSelectedZone(zone) {
  if (!zone) return;
  document.querySelector("#selected-zone").textContent = zone.zone_name;
  document.querySelector("#selected-score").textContent = zone.opportunity_score.toFixed(1);
  const components = [["Activity · 35%", zone.activity_component], ["Growth · 30%", zone.growth_component], ["Fare · 20%", zone.fare_component], ["Airport · 15%", zone.airport_component]];
  document.querySelector("#score-components").innerHTML = components.map(([label, value]) => `<div class="component"><header><span>${label}</span><span>${value.toFixed(1)}</span></header><div><i style="width:${value}%"></i></div></div>`).join("");
}

function renderHeatmap() {
  const allowed = new Set(zoneRows().map((zone) => zone.zone_id));
  const scoped = rows("hourly").filter((row) => allowed.has(row.zone_id) && (!state.selectedZone || row.zone_id === state.selectedZone));
  const values = new Map();
  for (const row of scoped) {
    const key = `${row.day_of_week}|${row.pickup_hour}`;
    values.set(key, (values.get(key) || 0) + row.avg_completed_trips_per_observed_day);
  }
  const max = Math.max(...values.values(), 1);
  const heatmap = document.querySelector("#heatmap");
  const nodes = [Object.assign(document.createElement("span"), { className: "heat-label" })];
  for (let hour = 0; hour < 24; hour += 1) nodes.push(Object.assign(document.createElement("span"), { className: "heat-hour", textContent: hour % 3 === 0 ? String(hour).padStart(2, "0") : "" }));
  DAYS.forEach((day, dayIndex) => {
    nodes.push(Object.assign(document.createElement("span"), { className: "heat-label", textContent: day }));
    for (let hour = 0; hour < 24; hour += 1) {
      const value = values.get(`${dayIndex}|${hour}`) || 0;
      const cell = document.createElement("span");
      cell.className = "heat-cell";
      cell.style.setProperty("--level", Math.max(.03, value / max));
      cell.dataset.tip = `${day} ${String(hour).padStart(2, "0")}:00 · ${value.toFixed(2)} trips/day`;
      nodes.push(cell);
    }
  });
  heatmap.replaceChildren(...nodes);
}

function renderProvenance() {
  const metadata = rows("metadata");
  const modes = [...new Set(metadata.map((row) => row.source_mode))].join(", ");
  const latest = metadata.map((row) => row.loaded_at).sort().at(-1);
  document.querySelector("#source-mode").textContent = `${modes.toUpperCase()} DATA · ${number.format(metadata.reduce((sum, row) => sum + row.row_count, 0))} RAW ROWS`;
  document.querySelector("#freshness-note").textContent = `${modes === "sample" ? "Deterministic synthetic sample" : "TLC source extract"}; warehouse loaded ${latest}. Results support portfolio analysis, not an investment decision.`;
  document.querySelector("#schema-version").textContent = `CONTRACT v${state.data.summary.schema_version}`;
}

function render() { updateKpis(); renderMarketCharts(); renderZones(); renderHeatmap(); }

async function init() {
  try { await loadData(); setupFilters(); renderProvenance(); render(); }
  catch (error) { const banner = document.querySelector("#error-banner"); banner.hidden = false; banner.textContent = `${error.message} Generate dashboard JSON and serve this directory over HTTP.`; console.error(error); }
}

init();
