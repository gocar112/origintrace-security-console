---
name: origintrace-console
description: Operate, extend, verify, publish, or document the OriginTrace Security Console. Use when a request mentions OriginTrace, the runtime-to-source console, Falco or eBPF-to-AST correlation, the OWASP companion scanner, reachability scoring, the OriginTrace operator book, its desktop shortcut, or the origintrace-security-console Site/repository.
---

# OriginTrace Console

Use `C:\Users\ghostman\Desktop\AIOS\AIS-OS\projects\origintrace-security-console` as the canonical project. The Sites deployment checkout is `C:\Users\ghostman\Desktop\AIOS\origintrace-security-console`. The live private Site is `https://origintrace-security-console.starage100.chatgpt.site/`.

## Operating rules

1. Preserve the distinction between repository-backed scenarios, replayed evidence, and live telemetry. Never label sample data as a connected production cluster.
2. Treat network scanning as authorized-only. Keep safe defaults, TLS verification, rate limits, and explicit target review.
3. Stage generated remediation for human review. Never auto-merge or silently change production code.
4. Keep incident IDs, syscall, source file, line, function, reachability gates, rule, and patch linked across views and exports.
5. Edit the canonical AIOS project first. Sync the `dist` output to the Sites checkout before publishing.

## Common workflows

- For UI changes, edit `dist/index.html`, `dist/styles.css`, and `dist/app.js`; validate local asset references and JavaScript syntax.
- For the operator guide, run `scripts/build_book.py` with the bundled workspace Python, export the DOCX to PDF, and visually inspect every page before replacing `dist/book` copies.
- For desktop access, run `scripts/install_desktop_shortcut.py` with an explicit desktop directory and asset directory. It creates a multi-resolution `.ico`, PNG, and URL shortcut.
- For publishing, use the Sites building and hosting skills, preserve the existing private/custom audience, and verify the returned production URL.

## Source boundaries

- Runtime pipeline basis: `https://github.com/ritvikindupuri/OriginTrace_DevSecOps`
- Surface scanner basis: `https://github.com/gocar112/the-OWASP-Top-10-Vulnerability-Scanner`
- Console repository: `https://github.com/gocar112/origintrace-security-console`
