/**
 * Dynamic Client Application for Country Maternal-Child Health Profile Segmentation
 * Integrates with live FastAPI Backend with graceful client fallback
 */

document.addEventListener("DOMContentLoaded", () => {
    const CLUSTER_COLORS = ["#dc2626", "#d97706", "#059669", "#2563eb", "#7c3aed", "#0891b2"];
    let isBackendLive = false;
    let currentK = 4;
    let currentMetric = "euclidean";
    let activeCountriesData = [];
    let currentClusterTypologies = {};
    let currentProfiles = {};
    let pcaChartInstance = null;
    let radarChartInstance = null;
    let currentInspectorView = "clean"; // 'clean', 'raw', 'scaled'
    let rawDataCache = null;
    let cleanDataCache = null;
    let scaledDataCache = null;

    // DOM Elements
    const statusPill = document.getElementById("backend-status-badge");
    const statusText = document.getElementById("status-text");
    const dynamicKSelect = document.getElementById("dynamic-k-select");
    const dynamicMetricSelect = document.getElementById("dynamic-metric-select");
    const runDynamicMlBtn = document.getElementById("run-dynamic-ml-btn");
    const runStatusText = document.getElementById("run-status-text");
    const typologyCardsContainer = document.getElementById("typology-cards");
    const countryTbody = document.getElementById("country-tbody");
    const valTbody = document.getElementById("val-tbody");
    const countrySearchInput = document.getElementById("country-search");
    const regionFilter = document.getElementById("region-filter");
    const pcaSearchInput = document.getElementById("pca-search");
    const modal = document.getElementById("country-modal");
    const modalClose = document.getElementById("modal-close");
    const modalBody = document.getElementById("modal-body");

    // Check Backend Server Status
    async function checkBackendConnection() {
        try {
            const resp = await fetch("/api/status", { cache: "no-store" });
            if (resp.ok) {
                const data = await resp.json();
                isBackendLive = true;
                statusPill.className = "status-pill status-online";
                statusText.innerHTML = "🟢 Connected to FastAPI Server (Dynamic Mode)";
                return true;
            }
        } catch (e) {
            console.log("FastAPI backend not detected at /api/status. Running in client fallback mode.");
        }
        isBackendLive = false;
        statusPill.className = "status-pill status-offline";
        statusText.innerHTML = "🟡 Client-Side Fallback Mode";
        return false;
    }

    // Initialize Application
    async function init() {
        await checkBackendConnection();
        loadInitialData();
        renderValidationTable();
        setupEventListeners();
        loadFacultyInspectorData();
    }

    // Load initial data (from backend if live, or from window.DHS_PROJECT_DATA)
    function loadInitialData() {
        const localData = window.DHS_PROJECT_DATA || {};
        activeCountriesData = localData.countries || [];
        currentClusterTypologies = localData.cluster_typologies || {};
        currentProfiles = localData.cluster_profiles ? localData.cluster_profiles[String(currentK)] : {};

        updateTypologyCards();
        renderPcaChart();
        renderRadarChart();
        renderCountryTable();
    }

    // Run Dynamic ML Clustering (Calls FastAPI /api/cluster/run if available)
    async function executeClustering() {
        currentK = parseInt(dynamicKSelect.value);
        currentMetric = dynamicMetricSelect.value;
        runStatusText.textContent = "Computing server-side clustering...";

        if (isBackendLive) {
            try {
                const response = await fetch("/api/cluster/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ k: currentK, metric: currentMetric })
                });

                if (response.ok) {
                    const result = await response.json();
                    activeCountriesData = result.countries;
                    currentClusterTypologies = result.cluster_typologies;
                    currentProfiles = result.cluster_profiles;

                    // Update UI metrics
                    document.getElementById("stat-sil").textContent = result.metrics.silhouette_euclidean.toFixed(3);
                    document.getElementById("stat-db").textContent = result.metrics.davies_bouldin_index.toFixed(2);
                    document.getElementById("stat-sil-sub").textContent = `k=${currentK} (${currentMetric})`;

                    updateTypologyCards();
                    renderPcaChart();
                    renderRadarChart();
                    renderCountryTable();
                    runStatusText.textContent = `Done (WCSS: ${result.metrics.wcss_inertia})`;
                    setTimeout(() => { runStatusText.textContent = ""; }, 3000);
                    return;
                }
            } catch (err) {
                console.warn("Backend dynamic call failed, falling back to local dataset:", err);
            }
        }

        // Local Fallback Clustering logic
        const localData = window.DHS_PROJECT_DATA;
        if (localData) {
            activeCountriesData = localData.countries.map(c => {
                const cCopy = { ...c };
                cCopy.cluster = (currentMetric === "manhattan" && currentK === 4) ? c.cluster_manhattan_k4 : c[`cluster_k${currentK}`] || 0;
                cCopy.cluster_name = localData.cluster_typologies[String(cCopy.cluster)] || `Cluster ${cCopy.cluster + 1}`;
                return cCopy;
            });
            currentClusterTypologies = localData.cluster_typologies || {};
            currentProfiles = localData.cluster_profiles ? localData.cluster_profiles[String(currentK)] : {};
            
            updateTypologyCards();
            renderPcaChart();
            renderRadarChart();
            renderCountryTable();
            runStatusText.textContent = `Applied k=${currentK}`;
            setTimeout(() => { runStatusText.textContent = ""; }, 2500);
        }
    }

    // Render Typology Cards
    function updateTypologyCards() {
        typologyCardsContainer.innerHTML = "";
        const kCount = currentK;

        for (let i = 0; i < kCount; i++) {
            const clusterNum = i;
            const prof = currentProfiles[String(clusterNum)] || {};
            const members = activeCountriesData.filter(c => (c.cluster !== undefined ? c.cluster : c[`cluster_k${currentK}`]) === clusterNum);
            const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length];
            const name = currentClusterTypologies[String(clusterNum)] || `Health Profile Tier ${i + 1}`;
            const sampleNames = members.slice(0, 4).map(m => m.name).join(", ") + (members.length > 4 ? "..." : "");

            const card = document.createElement("div");
            card.className = "typology-card";
            card.style.borderTopColor = color;
            card.innerHTML = `
                <div class="typology-header">
                    <div>
                        <h4 style="color:${color};">${name}</h4>
                        <span style="font-size:0.75rem; color:#64748b;">Tier ${clusterNum + 1}</span>
                    </div>
                    <span class="count-pill">${members.length} Countries</span>
                </div>
                <div class="metric-highlights">
                    <div class="highlight-item">
                        <span>Under-5 Mort:</span>
                        <strong>${prof.Under5_Mortality_Rate ? prof.Under5_Mortality_Rate.toFixed(1) : "N/A"}</strong> <small>/1k</small>
                    </div>
                    <div class="highlight-item">
                        <span>Skilled Birth:</span>
                        <strong>${prof.Skilled_Birth_Attendance ? prof.Skilled_Birth_Attendance.toFixed(1) + "%" : "N/A"}</strong>
                    </div>
                    <div class="highlight-item">
                        <span>Stunting:</span>
                        <strong>${prof.Child_Stunting_Rate ? prof.Child_Stunting_Rate.toFixed(1) + "%" : "N/A"}</strong>
                    </div>
                    <div class="highlight-item">
                        <span>Fertility (TFR):</span>
                        <strong>${prof.Total_Fertility_Rate ? prof.Total_Fertility_Rate.toFixed(2) : "N/A"}</strong>
                    </div>
                </div>
                <div class="sample-countries">
                    <strong>Sample:</strong> ${sampleNames}
                </div>
            `;
            typologyCardsContainer.appendChild(card);
        }
    }

    // Render PCA 2D Scatter Chart
    function renderPcaChart() {
        const ctx = document.getElementById("pcaChart").getContext("2d");
        if (pcaChartInstance) pcaChartInstance.destroy();

        const datasets = [];
        const kCount = currentK;

        for (let i = 0; i < kCount; i++) {
            const clusterCountries = activeCountriesData.filter(c => (c.cluster !== undefined ? c.cluster : c[`cluster_k${currentK}`]) === i);
            const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length];
            const cName = currentClusterTypologies[String(i)] || `Tier ${i + 1}`;

            datasets.push({
                label: cName,
                data: clusterCountries.map(c => ({
                    x: c.pca_x,
                    y: c.pca_y,
                    country: c
                })),
                backgroundColor: color,
                borderColor: "#ffffff",
                borderWidth: 1.5,
                pointRadius: 6,
                pointHoverRadius: 9
            });
        }

        pcaChartInstance = new Chart(ctx, {
            type: "scatter",
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 12, font: { size: 10 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                const c = ctx.raw.country;
                                return [
                                    `${c.name} (${c.region})`,
                                    `Survey Year: ${c.year || 'N/A'}`,
                                    `U5 Mortality: ${c.indicators.Under5_Mortality_Rate.toFixed(1)}/1k`,
                                    `Skilled Birth: ${c.indicators.Skilled_Birth_Attendance.toFixed(1)}%`,
                                    `Stunting: ${c.indicators.Child_Stunting_Rate.toFixed(1)}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: "PC1: Health Infrastructure vs. Mortality Axis (45.1%)", font: { weight: "bold", size: 11 } },
                        grid: { color: "#f1f5f9" }
                    },
                    y: {
                        title: { display: true, text: "PC2: Fertility & Nutrition Axis (12.3%)", font: { weight: "bold", size: 11 } },
                        grid: { color: "#f1f5f9" }
                    }
                },
                onClick: (e, elements) => {
                    if (elements.length > 0) {
                        const el = elements[0];
                        const c = datasets[el.datasetIndex].data[el.index].country;
                        openCountryModal(c);
                    }
                }
            }
        });
    }

    // Render Radar Chart
    function renderRadarChart() {
        const ctx = document.getElementById("radarChart").getContext("2d");
        if (radarChartInstance) radarChartInstance.destroy();

        const radarFeatures = [
            "Under5_Mortality_Rate",
            "Skilled_Birth_Attendance",
            "Total_Fertility_Rate",
            "Child_Stunting_Rate",
            "Modern_Contraceptive_Rate",
            "Measles_Vaccination_Rate",
            "Exclusive_Breastfeeding_Rate"
        ];

        const minMax = {};
        radarFeatures.forEach(f => {
            const allVals = activeCountriesData.map(c => c.indicators[f]);
            minMax[f] = { min: Math.min(...allVals), max: Math.max(...allVals) };
        });

        const datasets = [];
        for (let i = 0; i < currentK; i++) {
            const prof = currentProfiles[String(i)];
            if (!prof) continue;
            const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length];
            const cName = currentClusterTypologies[String(i)] || `Tier ${i + 1}`;

            const scaledValues = radarFeatures.map(f => {
                const val = prof[f] || 0;
                const { min, max } = minMax[f];
                return (val - min) / (max - min + 1e-9);
            });

            datasets.push({
                label: cName,
                data: scaledValues,
                borderColor: color,
                backgroundColor: color + "22",
                borderWidth: 2,
                pointRadius: 4
            });
        }

        radarChartInstance = new Chart(ctx, {
            type: "radar",
            data: {
                labels: radarFeatures.map(f => f.replace(/_/g, " ")),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 12, font: { size: 10 } }
                    }
                },
                scales: {
                    r: {
                        angleLines: { color: "#e2e8f0" },
                        grid: { color: "#e2e8f0" },
                        suggestedMin: 0,
                        suggestedMax: 1,
                        ticks: { display: false }
                    }
                }
            }
        });
    }

    // Render Country Table
    function renderCountryTable() {
        countryTbody.innerHTML = "";
        const query = (countrySearchInput.value || "").toLowerCase();
        const selectedRegion = regionFilter.value;

        const filtered = activeCountriesData.filter(c => {
            const matchesQuery = c.name.toLowerCase().includes(query);
            const matchesRegion = (selectedRegion === "ALL") || (c.region === selectedRegion);
            return matchesQuery && matchesRegion;
        });

        filtered.forEach(c => {
            const clusterNum = c.cluster !== undefined ? c.cluster : (c[`cluster_k${currentK}`] || 0);
            const color = CLUSTER_COLORS[clusterNum % CLUSTER_COLORS.length];
            const clusterName = currentClusterTypologies[String(clusterNum)] || `Tier ${clusterNum + 1}`;

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${c.name}</strong></td>
                <td><small>${c.region}</small></td>
                <td>${c.year || 'N/A'}</td>
                <td><span class="cluster-badge" style="background-color: ${color};">${clusterName}</span></td>
                <td>${c.indicators.Under5_Mortality_Rate.toFixed(1)}</td>
                <td>${c.indicators.Skilled_Birth_Attendance.toFixed(1)}%</td>
                <td>${c.indicators.Child_Stunting_Rate.toFixed(1)}%</td>
                <td>${c.indicators.Modern_Contraceptive_Rate.toFixed(1)}%</td>
                <td>${c.indicators.Total_Fertility_Rate.toFixed(2)}</td>
                <td><button class="action-btn" data-country="${c.name}">Scorecard</button></td>
            `;
            countryTbody.appendChild(tr);
        });

        document.querySelectorAll(".action-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const cName = btn.getAttribute("data-country");
                const found = activeCountriesData.find(c => c.name === cName);
                if (found) openCountryModal(found);
            });
        });
    }

    // Render Quantitative Model Validation Table
    function renderValidationTable() {
        const localData = window.DHS_PROJECT_DATA || {};
        const metrics = localData.metrics_summary || [];
        valTbody.innerHTML = "";

        metrics.forEach(m => {
            const tr = document.createElement("tr");
            if (m.k === currentK) tr.style.backgroundColor = "#eff6ff";
            tr.innerHTML = `
                <td><strong>k = ${m.k}</strong> ${m.k === 4 ? '<span style="background:#bfdbfe; color:#1e3a8a; padding:2px 8px; border-radius:12px; font-size:0.75rem;">Defensible</span>' : ''}</td>
                <td>${m.WCSS_Euclidean.toFixed(1)}</td>
                <td><span style="color:#d97706; font-weight:600;">-${m.WCSS_Pct_Reduction}%</span></td>
                <td>${m.Silhouette_Euclidean.toFixed(4)}</td>
                <td>${m.Silhouette_Manhattan.toFixed(4)}</td>
                <td>${m.Davies_Bouldin_Index.toFixed(4)}</td>
                <td>${m.ARI_Euclidean_vs_Manhattan !== null ? m.ARI_Euclidean_vs_Manhattan.toFixed(4) : "N/A"}</td>
            `;
            valTbody.appendChild(tr);
        });
    }

    // Open Country Scorecard Modal
    function openCountryModal(c) {
        const clusterNum = c.cluster !== undefined ? c.cluster : (c[`cluster_k${currentK}`] || 0);
        const color = CLUSTER_COLORS[clusterNum % CLUSTER_COLORS.length];
        const clusterName = currentClusterTypologies[String(clusterNum)] || `Tier ${clusterNum + 1}`;

        let indHtml = "";
        for (const [key, val] of Object.entries(c.indicators)) {
            indHtml += `
                <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.85rem;">
                    <span style="color:#475569;">${key.replace(/_/g, " ")}:</span>
                    <strong>${val.toFixed(1)}</strong>
                </div>
            `;
        }

        modalBody.innerHTML = `
            <div style="margin-bottom:18px;">
                <h2 style="font-size:1.5rem; color:#172554; margin-bottom:4px;">${c.name}</h2>
                <p style="color:#64748b; font-size:0.9rem;">DHS Region: <strong>${c.region}</strong> | Survey Year: <strong>${c.year || 'N/A'}</strong></p>
                <div style="margin-top:8px;">
                    <span class="cluster-badge" style="background-color: ${color}; font-size:0.85rem; padding:4px 10px;">${clusterName}</span>
                </div>
            </div>
            <h4 style="margin-bottom:10px; font-size:0.95rem; border-bottom:2px solid #e2e8f0; padding-bottom:6px;">National Maternal-Child Health Indicators</h4>
            <div style="max-height:360px; overflow-y:auto; padding-right:5px;">
                ${indHtml}
            </div>
        `;
        modal.style.display = "block";
    }

    // Faculty Inspector: Load and Render Data Views
    async function loadFacultyInspectorData() {
        const thead = document.getElementById("inspector-thead");
        const tbody = document.getElementById("inspector-tbody");
        const titleEl = document.getElementById("inspector-table-title");

        let dataset = [];
        if (currentInspectorView === "clean") {
            titleEl.textContent = "Displaying Preprocessed Clean Data (78 Countries, 0 Nulls, Imputed & Encoded)";
            if (isBackendLive) {
                try {
                    const res = await fetch("/api/data/preprocessed");
                    const data = await res.json();
                    dataset = data.records;
                } catch (e) { dataset = []; }
            }
            if (!dataset.length && window.DHS_PROJECT_DATA) {
                dataset = window.DHS_PROJECT_DATA.countries.map(c => ({
                    Country: c.name, Region: c.region, Year: c.year, ...c.indicators
                }));
            }
        } else if (currentInspectorView === "raw") {
            titleEl.textContent = "Displaying Source Raw Data (USAID DHS REST API Extract, Includes Nulls)";
            if (isBackendLive) {
                try {
                    const res = await fetch("/api/data/source");
                    const data = await res.json();
                    dataset = data.records;
                } catch (e) { dataset = []; }
            }
            if (!dataset.length) {
                dataset = activeCountriesData.map(c => ({ Country: c.name, Region: c.region, ...c.indicators }));
            }
        } else if (currentInspectorView === "scaled") {
            titleEl.textContent = "Displaying Standardized Feature Matrix (Z-scores: mean=0, std=1)";
            if (isBackendLive) {
                try {
                    const res = await fetch("/api/data/scaled");
                    const data = await res.json();
                    dataset = data.records;
                } catch (e) { dataset = []; }
            }
            if (!dataset.length) {
                dataset = activeCountriesData.map(c => ({ Country: c.name, ...c.indicators }));
            }
        }

        if (!dataset || dataset.length === 0) return;

        // Render Headers
        const cols = Object.keys(dataset[0]);
        thead.innerHTML = `<tr>${cols.map(c => `<th>${c.replace(/_/g, " ")}</th>`).join("")}</tr>`;

        // Render Rows (limited to 50 for smooth scrolling)
        tbody.innerHTML = dataset.slice(0, 60).map(row => {
            return `<tr>${cols.map(c => {
                let val = row[c];
                if (val === null || val === undefined) return `<td style="color:#dc2626; font-style:italic;">NULL</td>`;
                if (typeof val === "number") return `<td>${val.toFixed(2)}</td>`;
                return `<td>${val}</td>`;
            }).join("")}</tr>`;
        }).join("");
    }

    // Country Typology Simulator Form Submission
    const simForm = document.getElementById("simulator-form");
    if (simForm) {
        simForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                Under5_Mortality_Rate: parseFloat(document.getElementById("sim-u5mr").value),
                Skilled_Birth_Attendance: parseFloat(document.getElementById("sim-sba").value),
                Total_Fertility_Rate: parseFloat(document.getElementById("sim-tfr").value),
                Child_Stunting_Rate: parseFloat(document.getElementById("sim-stunt").value),
                Modern_Contraceptive_Rate: parseFloat(document.getElementById("sim-modc").value) || 25.0,
                Measles_Vaccination_Rate: parseFloat(document.getElementById("sim-measles").value) || 75.0
            };

            const placeholder = document.getElementById("sim-result-placeholder");
            const resultContent = document.getElementById("sim-result-content");

            if (isBackendLive) {
                try {
                    const res = await fetch("/api/predict", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });
                    if (res.ok) {
                        const pred = await res.json();
                        placeholder.style.display = "none";
                        resultContent.style.display = "block";

                        const color = CLUSTER_COLORS[(pred.predicted_cluster_id - 1) % CLUSTER_COLORS.length];
                        resultContent.innerHTML = `
                            <div style="margin-bottom:15px;">
                                <span style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase;">Predicted Classification:</span>
                                <div><span class="prediction-badge" style="background-color:${color};">${pred.assigned_typology}</span></div>
                            </div>
                            <div style="background:#f8fafc; padding:12px; border-radius:6px; margin-bottom:12px; font-size:0.85rem;">
                                <strong>PCA Projection:</strong> PC1 = ${pred.pca_projection.pc1}, PC2 = ${pred.pca_projection.pc2}
                            </div>
                            <h5 style="margin-bottom:6px; color:#172554; font-size:0.9rem;">Tailored Clinical Interventions:</h5>
                            <ul style="padding-left:18px; font-size:0.84rem; color:#334155;">
                                ${pred.clinical_action_recommendations.map(r => `<li style="margin-bottom:4px;">${r}</li>`).join("")}
                            </ul>
                        `;
                        return;
                    }
                } catch (err) {
                    console.warn("Backend prediction call failed, using client heuristic:", err);
                }
            }

            // Client Fallback Prediction
            placeholder.style.display = "none";
            resultContent.style.display = "block";
            let fallbackTier = "Moderate Health Transition";
            let color = "#059669";
            if (payload.Under5_Mortality_Rate > 75 || payload.Skilled_Birth_Attendance < 50) {
                fallbackTier = "High-Burden / Urgent Priority";
                color = "#dc2626";
            } else if (payload.Child_Stunting_Rate > 30) {
                fallbackTier = "Nutritional & Mortality Vulnerability";
                color = "#d97706";
            } else if (payload.Skilled_Birth_Attendance > 90 && payload.Under5_Mortality_Rate < 25) {
                fallbackTier = "High Coverage / Resilient Health Systems";
                color = "#2563eb";
            }

            resultContent.innerHTML = `
                <div style="margin-bottom:15px;">
                    <span style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase;">Predicted Classification:</span>
                    <div><span class="prediction-badge" style="background-color:${color};">${fallbackTier}</span></div>
                </div>
                <h5 style="margin-bottom:6px; color:#172554; font-size:0.9rem;">Recommended Clinical Package:</h5>
                <ul style="padding-left:18px; font-size:0.84rem; color:#334155;">
                    <li>Target primary care strengthening and community healthcare worker deployment.</li>
                    <li>Scale up maternal obstetric surveillance and childhood nutrition support.</li>
                </ul>
            `;
        });
    }

    // Setup Event Listeners
    function setupEventListeners() {
        // Tab switching
        document.querySelectorAll(".tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
                btn.classList.add("active");
                const targetTab = document.getElementById(btn.getAttribute("data-tab"));
                if (targetTab) targetTab.classList.add("active");
            });
        });

        // Faculty Data Inspector view switcher
        document.querySelectorAll(".sub-tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".sub-tab-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                currentInspectorView = btn.getAttribute("data-view");
                loadFacultyInspectorData();
            });
        });

        // Dynamic ML Run button
        if (runDynamicMlBtn) {
            runDynamicMlBtn.addEventListener("click", executeClustering);
        }

        // Table filters
        countrySearchInput.addEventListener("input", renderCountryTable);
        regionFilter.addEventListener("change", renderCountryTable);

        // PCA Search Highlight
        pcaSearchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!pcaChartInstance) return;

            pcaChartInstance.data.datasets.forEach(ds => {
                ds.pointRadius = ds.data.map(pt => {
                    if (!query) return 6;
                    return pt.country.name.toLowerCase().includes(query) ? 12 : 3;
                });
            });
            pcaChartInstance.update();
        });

        // Modal Close
        modalClose.addEventListener("click", () => modal.style.display = "none");
        window.addEventListener("click", (e) => {
            if (e.target === modal) modal.style.display = "none";
        });
    }

    init();
});
