# OriginTrace Security Console

[Open the private live console](https://origintrace-security-console.starage100.chatgpt.site)

![Runtime events correlated to source code](dist/assets/runtime-to-source-architecture.png)

OriginTrace Security Console combines the runtime-to-source evidence workflow from [OriginTrace DevSecOps](https://github.com/ritvikindupuri/OriginTrace_DevSecOps) with the authorized surface-testing routines in the [OWASP Top 10 Vulnerability Scanner](https://github.com/gocar112/the-OWASP-Top-10-Vulnerability-Scanner).

The console is designed for security engineers and developers who need to answer four questions quickly:

1. Did this code path execute in production?
2. Which file, function, and line produced the kernel event?
3. Can untrusted input reach the dangerous sink?
4. What verified rule and review-ready patch should prevent recurrence?

## Included

- Runtime incident queue with search and reachability filters
- Exact source origin, syscall, function, OWASP category, and CWE mapping
- Dual-verdict prioritization for confirmed and static-only findings
- Vulnerable and remediated code comparison
- Generated Semgrep taint-rule inspection
- Interactive reachability calculator
- Authorized OWASP scan-command builder
- Responsive static Site deployment
- Companion DOCX and PDF operator guide in `book/`
- Reusable AIOS skill in `.agents/skills/origintrace-console/`

## Run locally

```powershell
python -m http.server 4173 --directory dist
```

Then open `http://127.0.0.1:4173/`.

## Security boundary

The hosted console visualizes repository-backed evidence and prepares authorized scanner commands. Network tests run from the Python scanner in a trusted environment. Only test systems you own or have explicit permission to assess.
