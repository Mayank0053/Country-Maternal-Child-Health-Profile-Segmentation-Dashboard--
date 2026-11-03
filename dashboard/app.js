/**
 * Country Maternal-Child Health Profile Segmentation
 * Interactive Dashboard Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    const data = window.DHS_PROJECT_DATA;
    if (!data) {
        console.error("DHS_PROJECT_DATA not found. Please ensure data.js is loaded.");
        return;
    }

    const CLUSTER_COLORS = ["#D9381E", "#F4A261", "#2A9D8F", "#264653", "#9B5DE5", "#00B4D8"];
    let currentK = 4;
    let currentMetric = "euclidean";
    let pcaChartInstance = null;
    let radarChartInstance = null;

    // DOM Elements
    const kSelector = document.getElementById("k-selector");
    const metricSelector = document.getElementById("metric-selector");
    const pcaSearchInput = document.getElementById("pca-search");
    const countrySearchInput = document.getElementById("country-search");
    const regionFilter = document.getElementById("region-filter");
    const countryTbody = document.getElementById("country-tbody");
    const valTbody = document.getElementById("val-tbody");
    const typologyCardsContainer = document.getElementById("typology-cards");
    const modal = document.getElementById("country-modal");
    const modalClose = document.getElementById("modal-close");
    const modalBody = document.getElementById("modal-body");

    // Initialize Dashboard
    function init() {
        populateValidationTable();
        updateTypologyCards();
        renderPcaChart();
        renderRadarChart();
        renderCountryTable();
        setupEventListeners();
    }

    // Populate Quantitative Validation Table
    function populateValidationTable() {
        valTbody.innerHTML = "";
        data.metrics_summary.forEach(m => {
            const tr = document.createElement("tr");
            if (m.k === currentK) tr.classList.add("highlight-row");
            
            tr.innerHTML = `
                <td><strong>k = ${m.k}</strong> ${m.k === 4 ? '<span class="badge-tag">Defensible</span>' : ''}</td>
                <td>${m.WCSS_Euclidean.toFixed(1)}</td>
                <td><span style="color:#e67e22; font-weight:600;">-${m.WCSS_Pct_Reduction}%</span></td>
                <td>${m.Silhouette_Euclidean.toFixed(4)}</td>
                <td>${m.Silhouette_Manhattan.toFixed(4)}</td>
                <td>${m.Davies_Bouldin_Index.toFixed(4)}</td>
                <td>${m.ARI_Euclidean_vs_Manhattan !== null ? m.ARI_Euclidean_vs_Manhattan.toFixed(4) : "N/A"}</td>
            `;
            valTbody.appendChild(tr);
        });
    }

    // Update Typology Cards based on selected k
    function updateTypologyCards() {
        typologyCardsContainer.innerHTML = "";
        const profiles = data.cluster_profiles[String(currentK)] || {};
        const kCount = Object.keys(profiles).length;

        Object.keys(profiles).forEach((cId, idx) => {
            const clusterNum = parseInt(cId);
            const prof = profiles[cId];
            const members = data.countries.filter(c => getCountryCluster(c) === clusterNum);
            const color = CLUSTER_COLORS[idx % CLUSTER_COLORS.length];
            const name = data.cluster_typologies[cId] || `Health Profile Tier ${idx + 1}`;

            const sampleNames = members.slice(0, 4).map(m => m.name).join(", ") + (members.length > 4 ? "..." : "");

            const card = document.createElement("div");
            card.className = "typology-card";
            card.style.borderTopColor = color;
            card.innerHTML = `
                <div class="typology-header">
                    <div>
                        <h4 style="color:${color};">${name}</h4>
                        <span style="font-size:0.75rem; color:#64748b;">Cluster ID: ${clusterNum + 1}</span>
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
        });
    }

    // Helper to get cluster assignment for a country
    function getCountryCluster(country) {
        if (currentMetric === "manhattan" && currentK === 4) {
            return country.cluster_manhattan_k4;
        }
        return country[`cluster_k${currentK}`];
    }

    // Render PCA Scatter Plot
    function renderPcaChart() {
        const ctx = document.getElementById("pcaChart").getContext("2d");
        if (pcaChartInstance) pcaChartInstance.destroy();

        const datasets = [];
        const profiles = data.cluster_profiles[String(currentK)] || {};
        const kCount = Object.keys(profiles).length;

        for (let i = 0; i < kCount; i++) {
            const clusterCountries = data.countries.filter(c => getCountryCluster(c) === i);
            const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length];
            const cName = data.cluster_typologies[String(i)] || `Cluster ${i + 1}`;

            datasets.push({
                label: cName,
                data: clusterCountries.map(c => ({
                    x: c.pca_x,
                    y: c.pca_y,
                    country: c
                })),
                backgroundColor: color,
                borderColor: "#ffffff",
                borderWidth: 1,
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
                                    `Survey: ${c.year || 'N/A'}`,
                                    `U5 Mortality: ${c.indicators.Under5_Mortality_Rate.toFixed(1)}/1k`,
                                    `Skilled Birth: ${c.indicators.Skilled_Birth_Attendance.toFixed(1)}%`,
                                    `Child Stunting: ${c.indicators.Child_Stunting_Rate.toFixed(1)}%`
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

        const profiles = data.cluster_profiles[String(currentK)] || {};
        const kCount = Object.keys(profiles).length;

        // Select 7 primary representative features for radar balance
        const radarFeatures = [
            "Under5_Mortality_Rate",
            "Skilled_Birth_Attendance",
            "Total_Fertility_Rate",
            "Child_Stunting_Rate",
            "Modern_Contraceptive_Rate",
            "Measles_Vaccination_Rate",
            "Exclusive_Breastfeeding_Rate"
        ];

        // Compute global min/max for min-max scaling on radar
        const minMax = {};
        radarFeatures.forEach(f => {
            const allVals = data.countries.map(c => c.indicators[f]);
            minMax[f] = { min: Math.min(...allVals), max: Math.max(...allVals) };
        });

        const datasets = [];
        for (let i = 0; i < kCount; i++) {
            const prof = profiles[String(i)];
            if (!prof) continue;
            const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length];
            const cName = data.cluster_typologies[String(i)] || `Cluster ${i + 1}`;

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

        const filtered = data.countries.filter(c => {
            const matchesQuery = c.name.toLowerCase().includes(query);
            const matchesRegion = (selectedRegion === "ALL") || (c.region === selectedRegion);
            return matchesQuery && matchesRegion;
        });

        filtered.forEach(c => {
            const clusterNum = getCountryCluster(c);
            const color = CLUSTER_COLORS[clusterNum % CLUSTER_COLORS.length];
            const clusterName = data.cluster_typologies[String(clusterNum)] || `Cluster ${clusterNum + 1}`;

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

        // Add scorecard button listeners
        document.querySelectorAll(".action-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const cName = btn.getAttribute("data-country");
                const found = data.countries.find(c => c.name === cName);
                if (found) openCountryModal(found);
            });
        });
    }

    // Open Country Scorecard Modal
    function openCountryModal(c) {
        const clusterNum = getCountryCluster(c);
        const color = CLUSTER_COLORS[clusterNum % CLUSTER_COLORS.length];
        const clusterName = data.cluster_typologies[String(clusterNum)] || `Cluster ${clusterNum + 1}`;

        let indHtml = "";
        for (const [key, val] of Object.entries(c.indicators)) {
            const meta = data.features_metadata[key] || { name: key.replace(/_/g, " "), unit: "" };
            indHtml += `
                <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.85rem;">
                    <span style="color:#475569;">${key.replace(/_/g, " ")}:</span>
                    <strong>${val.toFixed(1)} <small style="color:#94a3b8;">${meta.unit || ''}</small></strong>
                </div>
            `;
        }

        modalBody.innerHTML = `
            <div style="margin-bottom:18px;">
                <h2 style="font-size:1.5rem; color:#1e293b; margin-bottom:4px;">${c.name}</h2>
                <p style="color:#64748b; font-size:0.9rem;">Region: <strong>${c.region}</strong> | Survey Year: <strong>${c.year || 'N/A'}</strong></p>
                <div style="margin-top:8px;">
                    <span class="cluster-badge" style="background-color: ${color}; font-size:0.85rem; padding:4px 10px;">${clusterName}</span>
                </div>
            </div>
            <h4 style="margin-bottom:10px; font-size:1rem; border-bottom:2px solid #e2e8f0; padding-bottom:6px;">National Maternal-Child Health Indicators</h4>
            <div style="max-height:360px; overflow-y:auto; padding-right:5px;">
                ${indHtml}
            </div>
        `;
        modal.style.display = "block";
    }

    // Event Listeners
    function setupEventListeners() {
        kSelector.addEventListener("change", (e) => {
            currentK = parseInt(e.target.value);
            updateTypologyCards();
            populateValidationTable();
            renderPcaChart();
            renderRadarChart();
            renderCountryTable();
        });

        metricSelector.addEventListener("change", (e) => {
            currentMetric = e.target.value;
            renderPcaChart();
            renderCountryTable();
        });

        countrySearchInput.addEventListener("input", renderCountryTable);
        regionFilter.addEventListener("change", renderCountryTable);

        pcaSearchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!pcaChartInstance) return;

            pcaChartInstance.data.datasets.forEach(ds => {
                ds.pointRadius = ds.data.map(pt => {
                    if (!query) return 6;
                    return pt.country.name.toLowerCase().includes(query) ? 12 : 3;
                });
                ds.pointBorderWidth = ds.data.map(pt => {
                    if (!query) return 1;
                    return pt.country.name.toLowerCase().includes(query) ? 3 : 0.5;
                });
            });
            pcaChartInstance.update();
        });

        modalClose.addEventListener("click", () => modal.style.display = "none");
        window.addEventListener("click", (e) => {
            if (e.target === modal) modal.style.display = "none";
        });
    }

    init();
});
