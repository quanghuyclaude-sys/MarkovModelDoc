# Skills: Engineering & Utility

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

Engineering and utility skills from the ZeroOne skills library.

---

## code-simplifier

### Install
```bash
npx skills add jackson-video-resources/skills -s code-simplifier -g -y
```

### What It Does
Analyses recently modified code files and eliminates unnecessary complexity while preserving all existing behaviour.

**Targets:**
- Unnecessary abstractions — helper functions created for single-use cases or over-engineered patterns
- Redundant elements — excessive comments, unreachable code
- Inlinable variables — values that could be merged into their usage point
- Collapsible functions — logic that could be consolidated
- Speculative code — additions made "just in case" that serve no current purpose

**Strict boundaries:** Maintains all public interfaces, exported types, and existing behaviour unchanged. Never introduces new features, documentation, or error handling.

> "If you can delete it without breaking anything, delete it."

---

## commit-push-pr

### Install
```bash
npx skills add jackson-video-resources/skills -s commit-push-pr -g -y
```

### What It Does
Structured git workflow for finalising code changes.

**Steps:**
1. Review changes: `git status`, `git diff`, recent commit history
2. Stage relevant files with `git add` — excludes `.env`, secrets, `node_modules`
3. Commit with message explaining the *reasoning* behind the change
4. Push branch to remote
5. Create pull request via GitHub CLI with formatted description

**Constraints:**
- Never pushes to `main`/`master` without confirmation
- Never uses `--no-verify` to bypass pre-commit hooks — fixes the failing issue instead
- PR titles kept under 70 characters
- PR body includes summary and test plan

---

## security-audit

### Install
```bash
npx skills add jackson-video-resources/skills -s security-audit -g -y
```

### What It Does
Security specialist for trading systems. Six modes.

| Mode | Focus |
|---|---|
| Secrets & Credential Audit | Scans for exposed private keys, mnemonics, API credentials, DB strings. Covers Ethereum, Bitcoin, Solana, and exchange platforms |
| Trading Bot Security Review | Credential handling, transaction signing, input validation, API security, order safety, infrastructure hardening |
| Smart Contract Risk Assessment | Verifies contract on block explorers, ownership structure, rug vectors, audit history |
| Wallet Security Audit | Cold/warm/hot separation, seed phrase storage, private key management for bots |
| DeFi Protocol Risk Audit | Smart contract risk, economic mechanisms, centralization, liquidity, composability vulnerabilities |
| System Hardening Checklist | Secrets management, opsec, code safety, infrastructure hardening, recovery procedures |

> "A single exposed private key or compromised API key can mean total loss of funds. Treat security as a prerequisite, not an afterthought."

---

## seo-optimizer

### Install
```bash
npx skills add jackson-video-resources/skills -s seo-optimizer -g -y
```

### What It Does
SEO analysis across six areas: target keywords, content structure, readability, technical elements, content quality, and recommendations.

**Priority tiers:**
- 🚨 Critical: Missing meta descriptions, absent keywords in titles, broken links, keyword stuffing
- ⚠️ High: Poor readability, weak heading structure, missing alt text
- 📋 Medium: Related keyword opportunities, schema markup potential

**Standards checked:** Meta title 50–60 chars, meta description 150–160 chars, Flesch Reading Ease 60–70, keyword density 1–2%.

---

## Related Files

- [[ClaudeCodeSkills-Trading]] — full skill list and trading skills
