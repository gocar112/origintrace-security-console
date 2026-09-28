from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "book"
OUTPUT = BOOK_DIR / "OriginTrace-Security-Console-Operator-Guide.docx"
HERO = ROOT / "dist" / "assets" / "runtime-to-source-architecture.png"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=110, start=110, bottom=110, end=110) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_run_font(run, name: str, size: float, bold=False, color="000000") -> None:
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr_text, fld_char2])
    set_run_font(run, "Aptos", 9, color="666666")


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.68)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.7)
    normal.font.color.rgb = RGBColor(34, 40, 46)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    for style_name, size, space_before, space_after in (
        ("Title", 30, 0, 14),
        ("Heading 1", 22, 14, 8),
        ("Heading 2", 15, 11, 5),
        ("Heading 3", 12, 8, 4),
    ):
        style = styles[style_name]
        style.font.name = "Aptos Display"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(space_before)
        style.paragraph_format.space_after = Pt(space_after)
        style.paragraph_format.keep_with_next = True

    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "OriginTrace Security Console Operator Guide"
    set_run_font(footer_para.runs[0], "Aptos", 8.5, color="6B747D")
    add_page_number(footer.add_paragraph())


def add_cover(doc: Document) -> None:
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.add_run("OriginTrace Security Console")
    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(16)
    run = subtitle.add_run("Runtime to Source DevSecOps Operator Guide")
    set_run_font(run, "Aptos Display", 16, bold=True, color="2D343B")

    picture = doc.add_picture(str(HERO), width=Inches(6.82))
    picture_paragraph = picture._inline.getparent().getparent()
    picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    caption = doc.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_before = Pt(5)
    caption.paragraph_format.space_after = Pt(16)
    run = caption.add_run("Runtime signals flow through AST correlation into verified source controls")
    set_run_font(run, "Aptos", 9, color="606A73")

    intro = doc.add_paragraph()
    intro.paragraph_format.space_after = Pt(10)
    run = intro.add_run(
        "This guide explains how to investigate a kernel-level security event, locate the responsible code, "
        "verify exploit reachability, generate a focused Semgrep rule, and stage a safer implementation for review."
    )
    set_run_font(run, "Aptos", 11.5, color="252B31")

    meta = doc.add_paragraph()
    meta.paragraph_format.space_before = Pt(12)
    meta.add_run("Repository owner  ").bold = True
    meta.add_run("gocar112\n")
    meta.add_run("Edition  ").bold = True
    meta.add_run("2026\n")
    meta.add_run("Live console  ").bold = True
    meta.add_run("origintrace-security-console.starage100.chatgpt.site")
    doc.add_page_break()


def add_contents(doc: Document) -> None:
    doc.add_heading("Contents", level=1)
    entries = [
        ("1", "Why runtime and static evidence must meet"),
        ("2", "System architecture"),
        ("3", "Operating the security console"),
        ("4", "OWASP surface scanning"),
        ("5", "Runtime event ingestion"),
        ("6", "AST source correlation"),
        ("7", "Dual verdict reachability"),
        ("8", "Semgrep rule synthesis"),
        ("9", "Remediation and pull request staging"),
        ("10", "Elastic and Kibana observability"),
        ("11", "MCP and agent workflows"),
        ("12", "Deployment and operational safeguards"),
        ("A", "Incident field reference"),
        ("B", "Source repositories"),
    ]
    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for number, label in entries:
        row = table.add_row()
        row.cells[0].width = Inches(0.5)
        row.cells[1].width = Inches(5.9)
        for cell in row.cells:
            set_cell_margins(cell, top=75, bottom=75)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p0 = row.cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run_font(p0.add_run(number), "Aptos", 10, bold=True, color="3E5E12")
        set_run_font(row.cells[1].paragraphs[0].add_run(label), "Aptos", 10.5)
def add_chapter(doc: Document, number: str, title: str, opening: str) -> None:
    if len(doc.paragraphs) > 0:
        doc.add_page_break()
    doc.add_heading(f"{number}. {title}", level=1)
    lead = doc.add_paragraph(opening)
    lead.paragraph_format.space_after = Pt(12)
    for run in lead.runs:
        set_run_font(run, "Aptos", 11.5, color="252B31")


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.add_run(item)


def add_numbered(doc: Document, items: list[str]) -> None:
    for index, item in enumerate(items, start=1):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.left_indent = Inches(0.24)
        paragraph.paragraph_format.first_line_indent = Inches(-0.24)
        paragraph.add_run(f"{index}.  {item}")


def add_code(doc: Document, code: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.18)
    paragraph.paragraph_format.right_indent = Inches(0.18)
    paragraph.paragraph_format.space_before = Pt(5)
    paragraph.paragraph_format.space_after = Pt(9)
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F2F4F5")
    p_pr.append(shd)
    run = paragraph.add_run(code)
    set_run_font(run, "Consolas", 8.5, color="1E252B")


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    header_row = table.rows[0]
    set_repeat_table_header(header_row)
    for index, header in enumerate(headers):
        cell = header_row.cells[index]
        set_cell_shading(cell, "29323A")
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if widths:
            cell.width = Inches(widths[index])
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(header) < 14 else WD_ALIGN_PARAGRAPH.LEFT
        set_run_font(p.add_run(header), "Aptos", 9, bold=True, color="FFFFFF")
    for row_index, values in enumerate(rows):
        row = table.add_row()
        fill = "F5F8F2" if row_index % 2 else "FFFFFF"
        for index, value in enumerate(values):
            cell = row.cells[index]
            set_cell_shading(cell, fill)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if widths:
                cell.width = Inches(widths[index])
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(value) < 12 else WD_ALIGN_PARAGRAPH.LEFT
            set_run_font(p.add_run(value), "Aptos", 8.7, color="2A3036")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def build() -> Path:
    BOOK_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()
    configure_document(doc)
    add_cover(doc)
    add_contents(doc)

    add_chapter(
        doc,
        "1",
        "Why runtime and static evidence must meet",
        "Static analysis finds possible defects, while runtime detection proves that a process performed a sensitive action. "
        "OriginTrace combines these signals so teams can distinguish reachable production risk from code that has never executed.",
    )
    doc.add_heading("The context gap", level=2)
    doc.add_paragraph(
        "SAST findings often identify dangerous functions without knowing whether a route, job, or handler can reach them. "
        "Falco and other eBPF tools detect process and file activity inside containers, but a syscall alone does not name the source file that caused it. "
        "The gap between those systems creates duplicate triage and alert fatigue."
    )
    doc.add_heading("The combined decision", level=2)
    add_bullets(doc, [
        "Use OWASP surface probes to identify externally observable weaknesses and response indicators.",
        "Use Falco runtime events to establish that a sensitive syscall occurred inside a workload.",
        "Use Python AST correlation to resolve the syscall to a dangerous sink in a file and function.",
        "Use Semgrep taint analysis to verify whether untrusted input can reach that sink.",
        "Stage a focused patch for developer review instead of silently changing production code.",
    ])

    add_chapter(
        doc,
        "2",
        "System architecture",
        "The platform preserves evidence as it moves from detection to remediation. Each stage adds context without discarding the original event.",
    )
    add_table(
        doc,
        ["Stage", "Component", "Purpose", "Primary output"],
        [
            ["1", "Falco webhook", "Capture anomalous kernel activity", "Normalized runtime event"],
            ["2", "FastAPI receiver", "Validate and persist telemetry", "Incident JSON"],
            ["3", "Correlation engine", "Map syscall to Python AST sink", "File, line, function"],
            ["4", "Reachability engine", "Combine runtime and static proof", "Score and verdict"],
            ["5", "Rule synthesizer", "Generate a focused taint rule", "Semgrep YAML"],
            ["6", "Remediation stage", "Replace unsafe behavior", "Unified diff"],
            ["7", "Elastic pipeline", "Retain and visualize evidence", "Forensic audit stream"],
        ],
        [0.5, 1.25, 2.65, 1.55],
    )
    doc.add_heading("Evidence continuity", level=2)
    doc.add_paragraph(
        "The incident identifier, command line, workload metadata, source origin, rule identifier, and remediation reference should remain linked. "
        "This allows an analyst to move from a dashboard row to the exact code change without reconstructing the event from several tools."
    )

    add_chapter(
        doc,
        "3",
        "Operating the security console",
        "The console opens on the incident queue because investigation is the primary task. The summary metrics provide context, but the selected incident carries the evidence needed for action.",
    )
    add_numbered(doc, [
        "Filter the queue to confirmed or static-only findings, or search by syscall, rule, source path, OWASP category, or CWE.",
        "Select an incident and verify the severity, reachability score, runtime command, source origin, and function.",
        "Compare the vulnerable sink with the staged remediation before opening the generated Semgrep rule.",
        "Use the reachability lab to test how each evidence gate changes priority.",
        "Move to the OWASP scanner view when an authorized surface assessment is required.",
    ])
    doc.add_heading("Repository evidence mode", level=2)
    doc.add_paragraph(
        "The hosted console contains scenarios documented in the source repositories. It does not claim that a live cluster is connected. "
        "When a backend is added, the interface should label live, replayed, and repository evidence explicitly."
    )

    add_chapter(
        doc,
        "4",
        "OWASP surface scanning",
        "The companion Python scanner performs rate-limited HTTP checks for common OWASP Top 10 indicators. The hosted console prepares a command; the trusted local environment executes the network test.",
    )
    add_table(
        doc,
        ["Check family", "Example signal", "Typical category", "Priority"],
        [
            ["SQL injection", "Database error after crafted parameter", "A03 Injection", "High"],
            ["Reflected XSS", "Payload returned in an executable context", "A03 Injection", "Medium"],
            ["Command injection", "Shell output after command delimiter", "A03 Injection", "High"],
            ["File inclusion", "Sensitive file content in response", "A01 Access control", "High"],
            ["Security headers", "Server or framework details exposed", "A05 Misconfiguration", "Low"],
            ["Component versions", "Version string exposed in content", "A06 Components", "Low"],
            ["Log exposure", "Trace or exception text in response", "A09 Logging", "Low"],
        ],
        [1.35, 2.55, 1.4, 0.7],
    )
    doc.add_heading("Run an authorized scan", level=2)
    add_code(doc, 'python ScannerWebSite.py --url "https://app.example.com" --output scan-report.txt')
    doc.add_paragraph(
        "Only assess systems you own or have explicit permission to test. Keep the scanner delay enabled, preserve TLS verification, and review requests before testing production endpoints."
    )

    add_chapter(
        doc,
        "5",
        "Runtime event ingestion",
        "Falco sends a structured event when a monitored workload performs suspicious process, file, or network activity. The receiver validates the event and stores a normalized incident record.",
    )
    doc.add_heading("Essential event fields", level=2)
    add_table(
        doc,
        ["Field", "Meaning", "Investigation use"],
        [
            ["rule", "Falco detection rule", "Explains why the event fired"],
            ["priority", "Falco severity", "Provides an initial triage signal"],
            ["proc.cmdline", "Observed command line", "Preserves runtime intent and parameters"],
            ["proc.pid", "Process identifier", "Links adjacent process evidence"],
            ["container.name", "Container identity", "Identifies the execution boundary"],
            ["k8s.pod.name", "Kubernetes pod", "Links the event to a workload instance"],
            ["time", "UTC event time", "Supports timeline reconstruction"],
        ],
        [1.35, 2.2, 2.5],
    )
    doc.add_heading("Persistence", level=2)
    doc.add_paragraph(
        "OriginTrace writes normalized incidents to disk using timestamped JSON files. This supports offline triage and provides a simple source for the CLI and MCP server. "
        "Elastic ingestion can run in parallel for search and dashboard use."
    )

    add_chapter(
        doc,
        "6",
        "AST source correlation",
        "The correlation engine walks Python syntax trees and searches for sinks that can explain the observed syscall. The result is an exact file, line, function, and call expression rather than a repository-wide guess.",
    )
    add_table(
        doc,
        ["Runtime syscall", "Representative Python sinks", "Risk class"],
        [
            ["execve", "os.system, subprocess.Popen, subprocess.run", "Command execution"],
            ["openat", "open, Path.read_text, Path.open", "File and secret access"],
            ["connect", "socket.connect, requests.get, subprocess network tools", "Outbound connection or SSRF"],
        ],
        [1.15, 3.15, 1.75],
    )
    doc.add_heading("Correlation constraints", level=2)
    add_bullets(doc, [
        "A sink match is a candidate until runtime metadata and data flow support it.",
        "Generated or vendored code should be separated from first-party application paths.",
        "Line numbers must come from the analyzed revision, not from an unrelated checkout.",
        "Several candidate sinks may require route, process, or command-signature disambiguation.",
    ])

    add_chapter(
        doc,
        "7",
        "Dual verdict reachability",
        "Reachability scoring prevents all findings from competing at the same priority. The score records which forms of evidence are present and produces a verdict that analysts can audit.",
    )
    add_table(
        doc,
        ["Evidence gate", "Weight", "What it proves"],
        [
            ["Runtime observed", "35", "A sensitive action occurred in a monitored workload"],
            ["AST sink matched", "25", "A source call can explain the syscall"],
            ["Semgrep verified", "25", "A taint path reaches the sink"],
            ["External input reachable", "15", "An attacker-controlled entry point reaches the path"],
        ],
        [2.0, 0.75, 3.3],
    )
    doc.add_heading("Verdict guidance", level=2)
    doc.add_paragraph(
        "A high score should not hide its inputs. The console exposes each gate so an analyst can see why an incident is confirmed, under investigation, or static only. "
        "A confirmed verdict requires runtime evidence and a matching source sink, not merely a numeric threshold."
    )

    add_chapter(
        doc,
        "8",
        "Semgrep rule synthesis",
        "For a confirmed path, the synthesizer creates a taint rule that matches the observed sink and likely request sources. The rule records CWE, OWASP, and incident metadata so the control remains explainable in CI.",
    )
    add_code(
        doc,
        "rules:\n"
        "  - id: auto-origintrace-terminal-shell\n"
        "    mode: taint\n"
        "    severity: ERROR\n"
        "    pattern-sources:\n"
        "      - pattern: request.query_params.get(...)\n"
        "    pattern-sinks:\n"
        "      - pattern: subprocess.run(...)\n"
        "    metadata:\n"
        "      cwe: CWE-78\n"
        "      owasp: A03:2021 - Injection",
    )
    doc.add_heading("Verification before adoption", level=2)
    add_numbered(doc, [
        "Validate the generated YAML.",
        "Run the official Semgrep CLI against the affected repository revision.",
        "Confirm the rule finds the intended sink without flooding unrelated code.",
        "Add a positive and negative test case before enforcing the rule in CI.",
    ])

    add_chapter(
        doc,
        "9",
        "Remediation and pull request staging",
        "OriginTrace stages changes for review. A patch should remove the dangerous behavior, validate external input, preserve required functionality, and remain narrow enough for a developer to understand.",
    )
    doc.add_heading("Command execution example", level=2)
    add_code(doc, '- os.system(f"ping -c 1 {host}")\n+ validate_host(host)\n+ subprocess.run(["ping", "-c", "1", host], check=True, shell=False)')
    doc.add_heading("Review checklist", level=2)
    add_bullets(doc, [
        "Confirm the fix addresses the observed runtime path and not only a similar static pattern.",
        "Keep shell execution disabled when an argument-vector API is available.",
        "Validate allowlists, path boundaries, timeouts, and failure behavior.",
        "Run application tests and the synthesized Semgrep rule against the patched revision.",
        "Require human review before merge and preserve the incident reference in the change record.",
    ])

    add_chapter(
        doc,
        "10",
        "Elastic and Kibana observability",
        "The optional Elastic pipeline makes reachability and code-origin fields searchable alongside the original Falco telemetry. Dashboards should help analysts prioritize and reconstruct events, not replace the underlying evidence.",
    )
    add_table(
        doc,
        ["Visualization", "Question answered", "Key fields"],
        [
            ["Reachability donut", "How much of the queue is confirmed?", "verdict, score"],
            ["Severity histogram", "Which priorities dominate?", "falco.priority"],
            ["Audit stream", "What happened and where?", "time, command, file, line"],
            ["Source hot spots", "Which code locations recur?", "file, function, sink"],
        ],
        [1.45, 2.45, 2.2],
    )
    doc.add_heading("Retention considerations", level=2)
    doc.add_paragraph(
        "Runtime commands and file paths can contain sensitive operational data. Limit access, define retention, avoid ingesting secrets, and document whether an event came from production, a replay, or a test workload."
    )

    add_chapter(
        doc,
        "11",
        "MCP and agent workflows",
        "The JSON-RPC MCP server exposes focused tools for incident discovery, correlation, and rule synthesis. The tool boundary helps an AI coding agent request evidence without unrestricted access to the entire security pipeline.",
    )
    add_table(
        doc,
        ["Tool", "Purpose", "Expected result"],
        [
            ["query_runtime_incidents", "List incidents by priority", "Incident identifiers and commands"],
            ["correlate_incident_to_code", "Resolve an incident to source", "File, line, function, sink"],
            ["synthesize_semgrep_rule", "Create a focused prevention rule", "YAML rule and metadata"],
        ],
        [2.1, 2.15, 2.0],
    )
    doc.add_heading("Safe agent use", level=2)
    add_bullets(doc, [
        "Require explicit authorization before scanning external targets or changing repositories.",
        "Keep remediation patches staged until a human reviews them.",
        "Return evidence and uncertainty with every verdict.",
        "Do not expose secrets, full token files, or unnecessary runtime payloads to downstream tools.",
    ])

    add_chapter(
        doc,
        "12",
        "Deployment and operational safeguards",
        "The console is a static interface that can be deployed independently from the Python correlation services. This separation makes the evidence boundary explicit and prevents the browser from claiming capabilities it does not have.",
    )
    doc.add_heading("Deployment checklist", level=2)
    add_numbered(doc, [
        "Validate JavaScript syntax and all local asset references.",
        "Confirm repository evidence is labeled and no production credentials are present.",
        "Preview desktop and mobile layouts before publishing.",
        "Package only the configured static directory and hosting manifest.",
        "Verify the deployment status and retain the returned production URL.",
        "Keep the GitHub repository and AIOS project copy synchronized with the published source.",
    ])
    doc.add_heading("Desktop access", level=2)
    doc.add_paragraph(
        "The included AIOS skill can create a Windows desktop shortcut with the OriginTrace icon. The shortcut opens the private live Site in the user's default browser."
    )

    add_chapter(
        doc,
        "A",
        "Incident field reference",
        "Use these fields as the minimum contract between runtime detection, correlation, the console, and observability systems.",
    )
    add_table(
        doc,
        ["Field", "Type", "Description"],
        [
            ["incident_id", "string", "Stable identifier across the evidence chain"],
            ["timestamp", "UTC datetime", "Time of the runtime event"],
            ["priority", "enum", "Falco severity such as CRITICAL or WARNING"],
            ["rule", "string", "Runtime rule that generated the event"],
            ["command_line", "string", "Observed process command"],
            ["syscall", "enum", "execve, openat, connect, or another mapped syscall"],
            ["source_file", "path", "Repository-relative source location"],
            ["source_line", "integer", "Line number for the matched sink"],
            ["function", "string", "Containing function or route handler"],
            ["sink", "string", "Dangerous call matched by AST analysis"],
            ["reachability_score", "0 to 100", "Weighted evidence score"],
            ["verdict", "enum", "CONFIRMED_EXPLOITABLE or STATIC_ONLY"],
            ["semgrep_rule", "path", "Generated rule location"],
            ["patch", "path", "Staged unified diff"],
        ],
        [1.6, 1.1, 3.55],
    )

    add_chapter(
        doc,
        "B",
        "Source repositories",
        "The console combines concepts and workflows from two repositories and keeps their responsibilities distinct.",
    )
    doc.add_heading("OriginTrace DevSecOps", level=2)
    doc.add_paragraph("https://github.com/ritvikindupuri/OriginTrace_DevSecOps")
    doc.add_paragraph(
        "Provides the runtime webhook receiver, incident store, Python AST correlation, reachability logic, Semgrep rule synthesis, patch staging, MCP server, and Elastic integration."
    )
    doc.add_heading("OWASP Top 10 Vulnerability Scanner", level=2)
    doc.add_paragraph("https://github.com/gocar112/the-OWASP-Top-10-Vulnerability-Scanner")
    doc.add_paragraph(
        "Provides rate-limited HTTP checks for injection, authentication, file inclusion, misconfiguration, component disclosure, and logging indicators."
    )
    doc.add_heading("OriginTrace Security Console", level=2)
    doc.add_paragraph("https://origintrace-security-console.starage100.chatgpt.site")
    doc.add_paragraph(
        "Presents repository-backed incidents, source correlation, reachability evidence, staged remediation, generated controls, and authorized scanner command preparation in one responsive interface."
    )

    doc.core_properties.title = "OriginTrace Security Console Operator Guide"
    doc.core_properties.subject = "Runtime to source DevSecOps operations"
    doc.core_properties.author = "gocar112"
    doc.core_properties.keywords = "OriginTrace, DevSecOps, OWASP, Falco, Semgrep, AST, eBPF"
    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
