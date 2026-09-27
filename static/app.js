/**
 * CareerLens AI - Frontend Reactive Controller & Mock Interview Engine
 */

// Global Application State
let appState = {
  resumeInputMode: "file",
  selectedFile: null,
  sampleData: null,
  currentAnalysis: null,
  activeTab: "tabGaps",
  mockSessionId: null,
  mockCurrentQuestion: null,
  mockTurnHistory: [],
  radarChartInstance: null,
  speechRecognition: null,
  isRecordingVoice: false
};

// Initialize Application on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  await fetchSampleData();
  setupEventListeners();
  setupVoiceRecognition();
  checkBackendHealth();
});

// Fetch pre-loaded sample profiles & JDs from backend
async function fetchSampleData() {
  try {
    const res = await fetch("/api/samples");
    if (res.ok) {
      appState.sampleData = await res.json();
    }
  } catch (err) {
    console.error("Failed to load sample data:", err);
  }
}

// Check backend status & active LLM engine
async function checkBackendHealth() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      const dot = document.getElementById("providerStatusDot");
      const label = document.getElementById("activeProviderLabel");
      if (label) {
        label.innerText = data.active_provider === "smart_local" ? "Smart Local AI" : data.active_provider.toUpperCase();
      }
      if (dot) {
        dot.className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
      }
    }
  } catch (e) {
    console.warn("Backend health check warning:", e);
  }
}

function setupEventListeners() {
  // JD word counter
  const jdInput = document.getElementById("jdTextInput");
  if (jdInput) {
    jdInput.addEventListener("input", (e) => {
      const words = e.target.value.trim().split(/\s+/).filter(Boolean).length;
      document.getElementById("jdWordCount").innerText = `${words} words entered`;
    });
  }

  // Drag and drop for resume container
  const dropZone = document.querySelector("#resumeFileContainer label");
  if (dropZone) {
    ["dragenter", "dragover"].forEach((event) => {
      dropZone.addEventListener(event, (e) => {
        e.preventDefault();
        dropZone.classList.add("border-brand-500", "bg-slate-900/80");
      });
    });
    ["dragleave", "drop"].forEach((event) => {
      dropZone.addEventListener(event, (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-brand-500", "bg-slate-900/80");
      });
    });
    dropZone.addEventListener("drop", (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleResumeFileSelected(e.dataTransfer.files[0]);
      }
    });
  }

  // Mock answer word count
  const mockInput = document.getElementById("mockAnswerInput");
  if (mockInput) {
    mockInput.addEventListener("input", (e) => {
      const count = e.target.value.trim().split(/\s+/).filter(Boolean).length;
      document.getElementById("mockAnswerWordCount").innerText = `${count} words`;
    });
  }
}

// Voice Recognition using Web Speech API
function setupVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    const btn = document.getElementById("btnVoiceInput");
    if (btn) btn.title = "Speech recognition not supported in this browser.";
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    const input = document.getElementById("mockAnswerInput");
    if (input) {
      input.value = (input.value ? input.value + " " : "") + transcript;
      const count = input.value.trim().split(/\s+/).filter(Boolean).length;
      document.getElementById("mockAnswerWordCount").innerText = `${count} words`;
    }
  };

  recognition.onerror = (e) => {
    console.warn("Speech recognition error:", e);
    stopVoiceRecognition();
  };

  recognition.onend = () => {
    stopVoiceRecognition();
  };

  appState.speechRecognition = recognition;
}

function toggleVoiceRecognition() {
  if (!appState.speechRecognition) {
    alert("Speech recognition is not supported in this browser. Please type your answer.");
    return;
  }
  if (appState.isRecordingVoice) {
    stopVoiceRecognition();
  } else {
    startVoiceRecognition();
  }
}

function startVoiceRecognition() {
  try {
    appState.speechRecognition.start();
    appState.isRecordingVoice = true;
    const btn = document.getElementById("btnVoiceInput");
    const statusText = document.getElementById("voiceStatusText");
    if (btn) btn.classList.add("recording-active");
    if (statusText) statusText.innerText = "Listening...";
  } catch (e) {
    console.error("Could not start speech recognition:", e);
  }
}

function stopVoiceRecognition() {
  try {
    if (appState.speechRecognition) {
      appState.speechRecognition.stop();
    }
  } catch (e) {}
  appState.isRecordingVoice = false;
  const btn = document.getElementById("btnVoiceInput");
  const statusText = document.getElementById("voiceStatusText");
  if (btn) btn.classList.remove("recording-active");
  if (statusText) statusText.innerText = "Voice Input";
}

// Resume Input Mode Switcher
function setResumeInputMode(mode) {
  appState.resumeInputMode = mode;
  const btnFile = document.getElementById("btnResumeModeFile");
  const btnText = document.getElementById("btnResumeModeText");
  const fileContainer = document.getElementById("resumeFileContainer");
  const textContainer = document.getElementById("resumeTextContainer");

  if (mode === "file") {
    btnFile.className = "px-3 py-1 rounded-md font-medium bg-brand-600 text-white transition";
    btnText.className = "px-3 py-1 rounded-md font-medium text-slate-400 hover:text-slate-200 transition";
    fileContainer.classList.remove("hidden");
    textContainer.classList.add("hidden");
  } else {
    btnText.className = "px-3 py-1 rounded-md font-medium bg-brand-600 text-white transition";
    btnFile.className = "px-3 py-1 rounded-md font-medium text-slate-400 hover:text-slate-200 transition";
    textContainer.classList.remove("hidden");
    fileContainer.classList.add("hidden");
  }
}

function handleResumeFileSelected(file) {
  if (!file) return;
  appState.selectedFile = file;
  document.getElementById("selectedFileName").innerText = file.name;
  document.getElementById("selectedFileSize").innerText = `(${(file.size / 1024).toFixed(1)} KB)`;
  document.getElementById("selectedFileInfo").classList.remove("hidden");
  document.getElementById("selectedFileInfo").classList.add("flex");
}

function clearSelectedFile() {
  appState.selectedFile = null;
  document.getElementById("resumeFileInput").value = "";
  document.getElementById("selectedFileInfo").classList.add("hidden");
  document.getElementById("selectedFileInfo").classList.remove("flex");
}

// Preset Loader Functions
function loadSelectedSample(sampleKey) {
  if (!sampleKey || !appState.sampleData) return;
  const sample = appState.sampleData.resumes[sampleKey];
  if (!sample) return;

  // Set mode to text and fill resume
  setResumeInputMode("text");
  document.getElementById("resumeTextInput").value = sample.text;
  document.getElementById("targetRoleInput").value = sample.role || "";

  // Auto-pair with sensible target JD
  if (sampleKey === "sde_fresher") {
    loadSelectedJd("google_sde");
  } else if (sampleKey === "fullstack_dev") {
    loadSelectedJd("frontend_react");
  } else if (sampleKey === "data_analyst") {
    loadSelectedJd("aiml_engineer");
  }

  // Scroll gently to analysis trigger
  document.getElementById("btnRunAnalysis").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function loadSelectedJd(jdKey) {
  if (!jdKey || !appState.sampleData) return;
  const jd = appState.sampleData.job_descriptions[jdKey];
  if (!jd) return;

  const jdInput = document.getElementById("jdTextInput");
  jdInput.value = jd.text;
  const words = jd.text.trim().split(/\s+/).filter(Boolean).length;
  document.getElementById("jdWordCount").innerText = `${words} words entered`;
  document.getElementById("jdPresetSelect").value = jdKey;
}

// MAIN ANALYSIS EXECUTION
async function executeAnalysis() {
  const jdText = document.getElementById("jdTextInput").value.trim();
  const targetRole = document.getElementById("targetRoleInput").value.trim() || "Software Engineer";

  if (!jdText) {
    alert("Please paste or select a Job Description (JD) to analyze against.");
    document.getElementById("jdTextInput").focus();
    return;
  }

  const formData = new FormData();
  formData.append("jd_text", jdText);
  formData.append("target_role", targetRole);

  if (appState.resumeInputMode === "file") {
    if (!appState.selectedFile) {
      alert("Please upload a resume file (.pdf, .docx) or switch to 'Paste Text' tab.");
      return;
    }
    formData.append("resume_file", appState.selectedFile);
  } else {
    const resumeText = document.getElementById("resumeTextInput").value.trim();
    if (!resumeText) {
      alert("Please paste your resume text in the text area.");
      document.getElementById("resumeTextInput").focus();
      return;
    }
    formData.append("resume_text", resumeText);
  }

  // Show loading spinner
  const loading = document.getElementById("analysisLoadingState");
  const results = document.getElementById("analysisSection");
  loading.classList.remove("hidden");
  results.classList.add("hidden");
  loading.scrollIntoView({ behavior: "smooth", block: "center" });

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Analysis request failed.");
    }

    const data = await response.json();
    appState.currentAnalysis = data;
    renderAnalysisResults(data);

    // Reveal results
    loading.classList.add("hidden");
    results.classList.remove("hidden");
    results.scrollIntoView({ behavior: "smooth", block: "start" });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    loading.classList.add("hidden");
    alert("Error performing analysis: " + err.message);
    console.error(err);
  }
}

// Render Analysis Results into Dashboard
function renderAnalysisResults(data) {
  const match = data.match_analysis;
  const critique = data.career_critique;
  const candidate = data.candidate || {};

  // 1. Render Top Score Gauges
  animateCircularGauge("overallScoreRing", "metricOverallScore", match.overall_score);
  
  document.getElementById("metricSkillsScore").innerText = `${match.skills_score}%`;
  document.getElementById("barSkillsScore").style.width = `${match.skills_score}%`;
  document.getElementById("metricSkillsCount").innerText = `${match.summary.matched_count} of ${match.summary.total_jd_skills} JD skills matched`;

  document.getElementById("metricExpScore").innerText = `${match.experience_score}%`;
  document.getElementById("barExpScore").style.width = `${match.experience_score}%`;

  document.getElementById("metricProjectScore").innerText = `${match.project_score}%`;
  document.getElementById("barProjectScore").style.width = `${match.project_score}%`;

  document.getElementById("metricAtsScore").innerText = `${match.ats_score}%`;
  document.getElementById("metricAtsGrade").innerText = `Grade ${match.ats_grade}`;

  // 2. Render Matching, Missing, and Bonus Skill Badges
  renderSkillBadges("matchingSkillsContainer", match.matching_skills, "match");
  document.getElementById("matchingCountBadge").innerText = `${match.matching_skills.length} Matched`;

  renderSkillBadges("missingSkillsContainer", match.missing_skills, "missing");
  document.getElementById("missingCountBadge").innerText = `${match.missing_skills.length} Missing`;

  renderSkillBadges("bonusSkillsContainer", match.bonus_skills, "bonus");
  document.getElementById("bonusCountBadge").innerText = `${match.bonus_skills.length} Bonus`;

  // 3. Render ATS Checklist
  renderAtsChecklist(match.ats_checks);

  // 4. Render Radar Chart
  renderRadarChart(match.category_radar);

  // 5. Render Recruiter Critique
  document.getElementById("critiqueSummaryText").innerText = critique.executive_summary;
  renderListItems("critiqueStrengthsList", critique.strengths, "check-circle", "text-emerald-400");
  renderListItems("critiqueRedFlagsList", critique.red_flags, "alert-circle", "text-rose-400");
  renderQuickWins("critiqueQuickWinsContainer", critique.quick_wins);

  // 6. Render Roadmap Timeline
  renderRoadmapTimeline(data.roadmap);

  // 7. Render Interview Question Bank
  renderInterviewQuestions(data.interview_questions);

  // Re-sync icons
  if (window.lucide) lucide.createIcons();
}

function animateCircularGauge(circleId, textId, score) {
  const circle = document.getElementById(circleId);
  const text = document.getElementById(textId);
  const circumference = 2 * Math.PI * 40; // r=40 -> 251.2
  const offset = circumference - (score / 100) * circumference;

  circle.style.strokeDashoffset = offset;
  
  // Color coding gauge based on score
  if (score >= 75) {
    circle.style.stroke = "#10b981"; // emerald
  } else if (score >= 55) {
    circle.style.stroke = "#6366f1"; // indigo
  } else {
    circle.style.stroke = "#f59e0b"; // amber
  }

  // Count up animation
  let curr = 0;
  const step = Math.ceil(score / 30);
  const timer = setInterval(() => {
    curr += step;
    if (curr >= score) {
      curr = score;
      clearInterval(timer);
    }
    text.innerText = `${curr}%`;
  }, 25);
}

function renderSkillBadges(containerId, skills, type) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!skills || skills.length === 0) {
    container.innerHTML = `<span class="text-xs text-slate-500 italic">None detected.</span>`;
    return;
  }

  skills.forEach(skill => {
    const span = document.createElement("span");
    const name = skill.name || skill;
    const cat = skill.category || "";
    
    if (type === "match") {
      span.className = "badge-pill badge-match";
      span.innerHTML = `<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i><span>${name}</span> <span class="text-[10px] text-emerald-400/70 border-l border-emerald-400/30 pl-1.5">${cat}</span>`;
    } else if (type === "missing") {
      const isHigh = skill.priority === "High";
      span.className = `badge-pill ${isHigh ? "badge-missing-high" : "badge-missing-medium"}`;
      span.title = skill.importance || "Required in JD";
      span.innerHTML = `<i data-lucide="${isHigh ? 'alert-triangle' : 'help-circle'}" class="w-3 h-3"></i><span>${name}</span> <span class="text-[10px] opacity-75 border-l border-slate-700 pl-1.5">${skill.priority || 'Req'}</span>`;
    } else {
      span.className = "badge-pill badge-bonus";
      span.innerHTML = `<i data-lucide="sparkles" class="w-3 h-3 text-blue-400"></i><span>${name}</span>`;
    }
    container.appendChild(span);
  });
}

function renderAtsChecklist(checks) {
  const container = document.getElementById("atsChecksContainer");
  container.innerHTML = "";
  if (!checks) return;

  checks.forEach(c => {
    const isPass = c.status === "pass";
    const card = document.createElement("div");
    card.className = "p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1";
    card.innerHTML = `
      <div class="flex items-center justify-between text-xs font-semibold">
        <span class="text-slate-200">${c.name}</span>
        <i data-lucide="${isPass ? 'check-circle' : 'alert-circle'}" class="w-4 h-4 ${isPass ? 'text-emerald-400' : 'text-amber-400'}"></i>
      </div>
      <p class="text-[11px] text-slate-400 leading-tight">${c.detail}</p>
    `;
    container.appendChild(card);
  });
}

function renderListItems(containerId, items, icon, iconColorClass) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  if (!items) return;

  items.forEach(item => {
    const li = document.createElement("li");
    li.className = "flex items-start space-x-2.5";
    li.innerHTML = `
      <i data-lucide="${icon}" class="w-4 h-4 ${iconColorClass} shrink-0 mt-0.5"></i>
      <span>${item}</span>
    `;
    container.appendChild(li);
  });
}

function renderQuickWins(containerId, wins) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  if (!wins) return;

  wins.forEach((win, idx) => {
    const div = document.createElement("div");
    div.className = "p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-slate-200 flex items-start space-x-2.5";
    div.innerHTML = `
      <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-300 font-bold flex items-center justify-center shrink-0 text-[10px] mt-0.5">${idx + 1}</span>
      <span class="leading-relaxed">${win}</span>
    `;
    container.appendChild(div);
  });
}

// Chart.js Radar Chart
function renderRadarChart(categoryRadar) {
  const ctx = document.getElementById("skillRadarChart");
  if (!ctx || !categoryRadar) return;

  if (appState.radarChartInstance) {
    appState.radarChartInstance.destroy();
  }

  const labels = categoryRadar.map(c => c.category);
  const data = categoryRadar.map(c => c.score);

  appState.radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [{
        label: "Candidate Match %",
        data: data,
        backgroundColor: "rgba(99, 102, 241, 0.25)",
        borderColor: "#818cf8",
        pointBackgroundColor: "#6366f1",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "#6366f1",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: "rgba(255, 255, 255, 0.08)" },
          grid: { color: "rgba(255, 255, 255, 0.08)" },
          pointLabels: {
            color: "#94a3b8",
            font: { size: 10, family: "Inter" }
          },
          ticks: {
            display: false,
            backdropColor: "transparent",
            stepSize: 25,
            max: 100
          },
          suggestedMin: 0,
          suggestedMax: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Roadmap Timeline Renderer
function renderRoadmapTimeline(roadmap) {
  const container = document.getElementById("roadmapTimelineContainer");
  container.innerHTML = "";
  if (!roadmap) return;

  roadmap.forEach((phase, idx) => {
    const card = document.createElement("div");
    card.className = "timeline-stem space-y-3";
    card.innerHTML = `
      <div class="timeline-dot">
        <span class="text-[10px] font-bold text-brand-400">${idx + 1}</span>
      </div>

      <div class="glass-card rounded-2xl p-5 space-y-3 border border-slate-800">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-slate-800/80 pb-2.5">
          <div>
            <span class="text-xs font-semibold text-brand-400 uppercase tracking-wider">${phase.phase}</span>
            <h4 class="font-bold text-sm text-slate-100">${phase.title}</h4>
          </div>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono shrink-0">${phase.duration}</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          <!-- Syllabus Topics -->
          <div class="space-y-1.5">
            <span class="text-xs font-semibold text-slate-400 flex items-center space-x-1.5">
              <i data-lucide="book-open" class="w-3.5 h-3.5 text-brand-400"></i>
              <span>Core Topics & Concepts:</span>
            </span>
            <ul class="text-xs text-slate-300 space-y-1 pl-4 list-disc marker:text-brand-500">
              ${phase.topics.map(t => `<li>${t}</li>`).join("")}
            </ul>
          </div>

          <!-- Suggested Portfolio Mini-Project -->
          <div class="bg-brand-950/20 border border-brand-500/20 rounded-xl p-3.5 space-y-1.5">
            <span class="text-xs font-bold text-accent-400 flex items-center space-x-1.5">
              <i data-lucide="folder-plus" class="w-3.5 h-3.5 text-accent-400"></i>
              <span>Portfolio Mini-Project: ${phase.mini_project.title}</span>
            </span>
            <p class="text-xs text-slate-300">${phase.mini_project.description}</p>
            <div class="text-[11px] text-slate-400 pt-1 font-mono">
              <span class="text-slate-500">Tech Stack:</span> ${phase.mini_project.tech_stack}
            </div>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Interview Questions Renderer
function renderInterviewQuestions(questions) {
  const container = document.getElementById("interviewQuestionsContainer");
  container.innerHTML = "";
  if (!questions) return;

  questions.forEach(q => {
    const card = document.createElement("div");
    card.className = "glass-card rounded-2xl p-5 space-y-3 border border-slate-800 question-item";
    card.setAttribute("data-category", q.category);

    const categoryBadgeClass = {
      "Technical": "bg-brand-500/20 text-brand-300 border-brand-500/30",
      "Resume Project": "bg-purple-500/20 text-purple-300 border-purple-500/30",
      "Behavioral": "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
      "System Design": "bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
    }[q.category] || "bg-slate-800 text-slate-300";

    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full border ${categoryBadgeClass}">${q.category}</span>
        <button onclick="toggleAnswerTip('tip-${q.id}')" class="text-xs text-brand-400 hover:text-brand-300 flex items-center space-x-1">
          <i data-lucide="eye" class="w-3.5 h-3.5"></i>
          <span>Model Tip</span>
        </button>
      </div>

      <p class="font-medium text-sm text-slate-100">${q.question}</p>

      <div class="text-xs text-slate-400 italic">
        <span class="text-slate-500 not-italic font-medium">Why Asked:</span> ${q.why_asked}
      </div>

      <div class="flex flex-wrap items-center gap-1.5 pt-1 text-[11px]">
        <span class="text-slate-500 font-medium">Expected Concepts:</span>
        ${q.expected_keywords.map(kw => `<span class="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">${kw}</span>`).join("")}
      </div>

      <!-- Expandable Model Tip -->
      <div id="tip-${q.id}" class="hidden pt-3 border-t border-slate-800/80 bg-slate-900/50 p-3 rounded-xl space-y-1">
        <span class="text-xs font-bold text-accent-400 flex items-center space-x-1.5">
          <i data-lucide="lightbulb" class="w-3.5 h-3.5"></i>
          <span>Exemplary Answer Structure & Coaching Advice:</span>
        </span>
        <p class="text-xs text-slate-300 leading-relaxed">${q.model_answer_tip}</p>
      </div>
    `;
    container.appendChild(card);
  });
}

function toggleAnswerTip(tipId) {
  const el = document.getElementById(tipId);
  if (el) {
    el.classList.toggle("hidden");
    if (window.lucide) lucide.createIcons();
  }
}

function filterInterviewQuestions(category) {
  const buttons = document.querySelectorAll(".q-filter-btn");
  buttons.forEach(btn => {
    if (btn.getAttribute("data-filter") === category) {
      btn.className = "q-filter-btn px-3 py-1.5 rounded-lg bg-brand-600 text-white font-medium transition";
    } else {
      btn.className = "q-filter-btn px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white transition";
    }
  });

  const cards = document.querySelectorAll(".question-item");
  cards.forEach(card => {
    if (category === "all" || card.getAttribute("data-category") === category) {
      card.classList.remove("hidden");
    } else {
      card.classList.add("hidden");
    }
  });
}

// AI MOCK INTERVIEW SIMULATOR LOGIC
async function startMockSession() {
  if (!appState.currentAnalysis || !appState.currentAnalysis.interview_questions) {
    alert("Please analyze a resume and job description first to initialize mock questions.");
    return;
  }

  const role = appState.currentAnalysis.target_role || "Software Engineer";
  const candidateName = appState.currentAnalysis.candidate ? appState.currentAnalysis.candidate.name : "Candidate";
  const questions = appState.currentAnalysis.interview_questions;

  try {
    const res = await fetch("/api/mock-interview/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: role,
        candidate_name: candidateName,
        questions: questions
      })
    });

    if (!res.ok) throw new Error("Could not start mock interview session.");
    const data = await res.json();

    appState.mockSessionId = data.session_id;
    appState.mockCurrentQuestion = data.current_question;
    appState.mockTurnHistory = [];

    // Switch view to interview room
    document.getElementById("mockInterviewRoom").classList.remove("hidden");
    document.getElementById("mockEvaluationCard").classList.add("hidden");
    document.getElementById("mockFinalReportCard").classList.add("hidden");
    document.getElementById("btnStartMockSession").innerText = "Restart Session";

    renderMockTurn(data.current_question, data.progress);
    if (window.lucide) lucide.createIcons();
  } catch (e) {
    alert("Failed to initialize mock session: " + e.message);
  }
}

function renderMockTurn(question, progress) {
  document.getElementById("mockProgressLabel").innerText = `Question ${progress.current} of ${progress.total}`;
  document.getElementById("mockProgressBar").style.width = `${(progress.current / progress.total) * 100}%`;
  document.getElementById("mockCategoryLabel").innerText = question.category || "Technical";

  document.getElementById("mockCurrentQuestionText").innerText = question.question;
  document.getElementById("mockQuestionWhy").innerText = `Interviewer Context: ${question.why_asked}`;

  // Reset input
  document.getElementById("mockAnswerInput").value = "";
  document.getElementById("mockAnswerWordCount").innerText = "0 words";
  document.getElementById("mockEvaluationCard").classList.add("hidden");
  document.getElementById("mockAnswerInput").focus();
}

async function submitMockAnswer() {
  const answer = document.getElementById("mockAnswerInput").value.trim();
  if (!answer) {
    alert("Please provide an answer before submitting for AI review.");
    document.getElementById("mockAnswerInput").focus();
    return;
  }

  stopVoiceRecognition();
  const btn = document.getElementById("btnSubmitAnswer");
  btn.disabled = true;
  btn.innerHTML = `<span class="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span> <span>Evaluating...</span>`;

  try {
    const res = await fetch("/api/mock-interview/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: appState.mockSessionId,
        candidate_answer: answer
      })
    });

    if (!res.ok) throw new Error("Evaluation failed.");
    const result = await res.json();

    const evaluation = result.evaluated_entry.evaluation;
    renderMockEvaluation(evaluation);

    // Store progress state
    appState.mockNextQuestion = result.next_question;
    appState.mockProgress = result.progress;

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    alert("Error evaluating answer: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="send" class="w-3.5 h-3.5"></i><span>Submit Answer for AI Review</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderMockEvaluation(evaluation) {
  const evalCard = document.getElementById("mockEvaluationCard");
  evalCard.classList.remove("hidden");

  // Score Badge
  const scoreBadge = document.getElementById("mockScoreBadge");
  scoreBadge.innerText = `${evaluation.score} / 10`;
  scoreBadge.className = `text-base font-extrabold text-white px-3 py-1 rounded-lg ${
    evaluation.score >= 8 ? "bg-emerald-600" : (evaluation.score >= 6 ? "bg-brand-600" : "bg-amber-600")
  }`;

  // Verdict Badge
  const verdictBadge = document.getElementById("mockVerdictBadge");
  verdictBadge.innerText = evaluation.verdict;

  // Strengths
  renderListItems("mockStrengthsList", evaluation.strengths, "check", "text-emerald-400");

  // Improvements
  renderListItems("mockImprovementsList", evaluation.improvement_areas, "arrow-right", "text-amber-400");

  // Exemplary Answer
  document.getElementById("mockExemplaryText").innerText = evaluation.exemplary_answer;

  evalCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function proceedToNextQuestion() {
  if (appState.mockProgress && appState.mockProgress.is_finished) {
    // Finished! Show report card
    displayMockReport();
  } else if (appState.mockNextQuestion) {
    renderMockTurn(appState.mockNextQuestion, appState.mockProgress);
  }
}

async function displayMockReport() {
  try {
    const res = await fetch(`/api/mock-interview/report/${appState.mockSessionId}`);
    if (!res.ok) throw new Error("Could not fetch final report.");
    const report = await res.json();

    document.getElementById("finalAvgScore").innerText = `${report.average_score} / 10`;
    document.getElementById("finalQuestionsCount").innerText = report.completed_questions;
    document.getElementById("finalVerdictText").innerText = report.performance_verdict;

    document.getElementById("mockEvaluationCard").classList.add("hidden");
    document.getElementById("mockFinalReportCard").classList.remove("hidden");
    document.getElementById("mockFinalReportCard").scrollIntoView({ behavior: "smooth", block: "center" });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Error fetching report:", err);
  }
}

// ATS BULLET REWRITER LOGIC
async function executeBulletRewrite() {
  const bullet = document.getElementById("bulletInputText").value.trim();
  if (!bullet) {
    alert("Please enter a bullet point to rewrite.");
    return;
  }

  const container = document.getElementById("bulletRewritesContainer");
  container.classList.remove("hidden");
  container.innerHTML = `<div class="p-4 text-xs text-slate-400 animate-pulse">Generating Google X-Y-Z formula variations...</div>`;

  try {
    const targetKeywords = appState.currentAnalysis 
      ? appState.currentAnalysis.match_analysis.matching_skills.slice(0, 3).map(s => s.name)
      : ["Java", "Scalability", "APIs"];

    const res = await fetch("/api/rewrite-bullet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        bullet_point: bullet,
        target_keywords: targetKeywords
      })
    });

    if (!res.ok) throw new Error("Rewrite failed.");
    const data = await res.json();

    container.innerHTML = "";
    data.rewrites.forEach((rw, idx) => {
      const card = document.createElement("div");
      card.className = "p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2";
      card.innerHTML = `
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-brand-400">${rw.style}</span>
          <button onclick="copyToClipboard(this, \`${encodeURIComponent(rw.text)}\`)" class="text-slate-400 hover:text-white flex items-center space-x-1">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
            <span>Copy</span>
          </button>
        </div>
        <p class="text-xs sm:text-sm text-slate-100 font-medium leading-relaxed font-mono">"${rw.text}"</p>
        <p class="text-[11px] text-slate-400 italic">${rw.highlight}</p>
      `;
      container.appendChild(card);
    });

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    container.innerHTML = `<div class="p-3 text-xs text-rose-400">Rewrite failed: ${e.message}</div>`;
  }
}

function copyToClipboard(button, encodedText) {
  const text = decodeURIComponent(encodedText);
  navigator.clipboard.writeText(text).then(() => {
    const original = button.innerHTML;
    button.innerHTML = `<span class="text-emerald-400">Copied!</span>`;
    setTimeout(() => {
      button.innerHTML = original;
      if (window.lucide) lucide.createIcons();
    }, 2000);
  });
}

// TAB SWITCHER
function switchTab(tabId) {
  appState.activeTab = tabId;

  // Toggle button styles
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.className = "tab-btn px-4 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 whitespace-nowrap transition";
  });
  const activeBtn = document.getElementById(`tabBtn-${tabId}`);
  if (activeBtn) {
    activeBtn.className = "tab-btn px-4 py-2.5 rounded-xl bg-brand-600/20 text-brand-300 border border-brand-500/30 flex items-center space-x-2 whitespace-nowrap transition";
  }

  // Toggle contents
  document.querySelectorAll(".tab-content").forEach(content => {
    content.classList.add("hidden");
  });
  const activeContent = document.getElementById(tabId);
  if (activeContent) {
    activeContent.classList.remove("hidden");
  }

  if (window.lucide) lucide.createIcons();
}

// PROVIDER CONFIG MODAL
function openProviderModal() {
  document.getElementById("providerConfigModal").classList.remove("hidden");
  const provSelect = document.getElementById("modalProviderSelect");
  provSelect.addEventListener("change", (e) => {
    const keyContainer = document.getElementById("modalApiKeyContainer");
    if (e.target.value === "smart_local") {
      keyContainer.classList.add("hidden");
    } else {
      keyContainer.classList.remove("hidden");
    }
  });
}

function closeProviderModal() {
  document.getElementById("providerConfigModal").classList.add("hidden");
}

async function saveProviderConfig() {
  const provider = document.getElementById("modalProviderSelect").value;
  const apiKey = document.getElementById("modalApiKeyInput").value.trim();

  try {
    const res = await fetch("/api/set-provider", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: provider,
        api_key: apiKey || null
      })
    });

    if (res.ok) {
      closeProviderModal();
      checkBackendHealth();
      alert(`Provider successfully switched to: ${provider}`);
    }
  } catch (err) {
    alert("Failed to update provider: " + err.message);
  }
}
