// Placebo Forensic Console Application Logic

document.addEventListener("DOMContentLoaded", () => {
  const hypListEl = document.getElementById("hypothesis-list");
  const hypCountEl = document.getElementById("hyp-count");
  const btnRefresh = document.getElementById("btn-refresh");

  // Funnel counters
  const funnelExplored = document.getElementById("funnel-explored");
  const funnelRaw = document.getElementById("funnel-raw");
  const funnelCorrected = document.getElementById("funnel-corrected");
  const funnelSurvived = document.getElementById("funnel-survived");

  // Audit display elements
  const auditIdBadge = document.getElementById("audit-id-badge");
  const claimTitle = document.getElementById("claim-title");
  const claimDetails = document.getElementById("claim-details");
  const verdictBadge = document.getElementById("verdict-badge");
  const confidenceLabel = document.getElementById("confidence-label");

  const rawP = document.getElementById("raw-p");
  const adjP = document.getElementById("adj-p");
  const effectSize = document.getElementById("effect-size");
  const ciRange = document.getElementById("ci-range");
  const statStatus = document.getElementById("stat-status");

  const placeboStatus = document.getElementById("placebo-status");
  const placeboTableBody = document.getElementById("placebo-table-body");
  const pretrendStatus = document.getElementById("pretrend-status");
  const pretrendDetails = document.getElementById("pretrend-details");
  const looStatus = document.getElementById("loo-status");
  const looDetails = document.getElementById("loo-details");

  const narrativeHeadline = document.getElementById("narrative-headline");
  const narrativeObserved = document.getElementById("narrative-observed");
  const narrativeFalsification = document.getElementById("narrative-falsification");
  const narrativeRec = document.getElementById("narrative-rec");

  let currentHypotheses = [];

  async function fetchHypotheses() {
    try {
      const res = await fetch("/api/v1/hypotheses");
      if (!res.ok) throw new Error("Failed to load hypotheses");
      currentHypotheses = await res.json();
      renderHypothesisList(currentHypotheses);
      updateFunnel(currentHypotheses);
    } catch (e) {
      console.warn("API not reachable, using offline sample data", e);
      renderOfflineSample();
    }
  }

  function updateFunnel(hyps) {
    funnelExplored.textContent = hyps.length;
    hypCountEl.textContent = `${hyps.length} Tracked`;
    const confirmed = hyps.filter(h => h.status === "CONFIRMED").length;
    funnelSurvived.textContent = confirmed;
  }

  function renderHypothesisList(hyps) {
    if (!hyps || hyps.length === 0) {
      hypListEl.innerHTML = '<div class="empty-state">No hypotheses registered yet.</div>';
      return;
    }

    hypListEl.innerHTML = "";
    hyps.forEach((h, idx) => {
      const item = document.createElement("div");
      item.className = `hyp-item ${idx === 0 ? "active" : ""}`;
      const statusClass = h.status === "CONFIRMED" ? "badge-green" : h.status === "REFUTED" ? "badge-red" : "badge-gray";
      
      item.innerHTML = `
        <div class="hyp-top">
          <span class="hyp-id">${h.hypothesis_id}</span>
          <span class="badge ${statusClass}">${h.status}</span>
        </div>
        <div class="hyp-claim">${h.claim_description}</div>
      `;

      item.addEventListener("click", () => {
        document.querySelectorAll(".hyp-item").forEach(el => el.classList.remove("active"));
        item.classList.add("active");
        displayHypothesisDetails(h);
      });

      hypListEl.appendChild(item);
    });

    if (hyps.length > 0) {
      displayHypothesisDetails(hyps[0]);
    }
  }

  function displayHypothesisDetails(h) {
    auditIdBadge.textContent = h.hypothesis_id;
    claimTitle.textContent = h.claim_description;
    claimDetails.textContent = `Metric: ${h.metric.name} | Period: ${h.time_window.start} to ${h.time_window.end} | Event: ${h.time_window.intervention_date || "N/A"}`;

    // Verdict Badge
    const grade = (h.status || "REGISTERED").toLowerCase();
    verdictBadge.textContent = h.status || "REGISTERED";
    verdictBadge.className = `verdict-badge ${grade}`;
    confidenceLabel.textContent = h.status === "CONFIRMED" ? "High Confidence" : h.status === "REFUTED" ? "High Confidence" : "Evaluation in progress";
  }

  function renderOfflineSample() {
    const sample = [
      {
        hypothesis_id: "HYP-0042",
        session_id: "sess_growth_q3",
        claim_description: "TikTok campaign drove +24% lift in French checkout conversion",
        metric: { name: "conversion_rate", column: "is_converted" },
        time_window: { start: "2026-06-01", end: "2026-09-30", intervention_date: "2026-09-01" },
        status: "REFUTED"
      },
      {
        hypothesis_id: "HYP-0043",
        session_id: "sess_infra_opt",
        claim_description: "Redis caching cluster reduced p95 latency by 45ms across EU regions",
        metric: { name: "latency_ms", column: "response_time" },
        time_window: { start: "2026-07-01", end: "2026-10-01", intervention_date: "2026-08-15" },
        status: "CONFIRMED"
      }
    ];

    renderHypothesisList(sample);
    updateFunnel(sample);

    // Populate forensic cards with sample refuted scenario
    rawP.textContent = "0.012";
    adjP.textContent = "0.310";
    effectSize.textContent = "+0.240 (+24.0%)";
    ciRange.textContent = "[-0.03, +0.51]";
    statStatus.textContent = "FAILED";
    statStatus.className = "card-status failed";

    placeboStatus.textContent = "FAILED (4/5 Fake Dates)";
    placeboStatus.className = "card-status failed";
    placeboTableBody.innerHTML = `
      <tr><td>2026-07-01</td><td class="mono">+0.220</td><td class="mono">91.6% of real</td><td><span class="badge badge-red">Spurious</span></td></tr>
      <tr><td>2026-07-15</td><td class="mono">+0.250</td><td class="mono">104.1% of real</td><td><span class="badge badge-red">Spurious</span></td></tr>
      <tr><td>2026-08-01</td><td class="mono">+0.235</td><td class="mono">97.9% of real</td><td><span class="badge badge-red">Spurious</span></td></tr>
      <tr><td>2026-08-15</td><td class="mono">+0.210</td><td class="mono">87.5% of real</td><td><span class="badge badge-red">Spurious</span></td></tr>
      <tr><td>2026-08-25</td><td class="mono">+0.030</td><td class="mono">12.5% of real</td><td><span class="badge badge-green">Clean</span></td></tr>
    `;

    pretrendStatus.textContent = "FAILED";
    pretrendStatus.className = "card-status failed";
    pretrendDetails.innerHTML = `<span class="mono" style="color: var(--color-red)">Pre-trend detected: slope = +0.0042/day (p = 0.0084). Upward drift started months earlier.</span>`;

    looStatus.textContent = "PASSED";
    looStatus.className = "card-status passed";
    looDetails.innerHTML = `<span class="mono" style="color: var(--color-green)">Max drop: 8.2% across top clusters. Finding not driven by single outliers.</span>`;

    narrativeHeadline.textContent = "Refuted: The observed lift is an ongoing seasonal trend, not a campaign effect.";
    narrativeObserved.textContent = "While conversion was nominally higher after Sept 1 (+24%), multiple testing adjustment across 47 queries raises the p-value to 0.31.";
    narrativeFalsification.textContent = "Identical 22-25% shifts occurred at 4 historical placebo dates in July and August. A significant upward pre-trend existed before the campaign launched.";
    narrativeRec.textContent = "Do not allocate incremental marketing budget based on this claim. The observed gain reflects general summer organic acceleration.";
  }

  btnRefresh.addEventListener("click", fetchHypotheses);
  fetchHypotheses();
});
