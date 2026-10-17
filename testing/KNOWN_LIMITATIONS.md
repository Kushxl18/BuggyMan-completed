# BuggyMan Known Limitations & Operational Constraints

**Document ID:** LIMIT-2026-v1.0  
**Project:** BuggyMan  
**Version:** 1.0.0  
**Date:** October 16, 2026  

---

## 1. Scope & Ecosystem Boundaries

This document records the verified limitations, intentional architectural compromises, and out-of-scope capabilities discovered during the QA validation phase.

---

## 2. Documented Limitations

### LIM-001: Simulated Payment Integration (Deferred)
- **Description:** Real financial transactions via Razorpay / Stripe are not active.
- **Root Cause / Requirement:** Explicit user constraint (`dont do real payment integration yet`).
- **Current Behavior:** The `/api/store/checkout` and `/api/store/confirm-payment` endpoints use high-fidelity simulation with mock order IDs and instant signature verification.
- **Production Impact:** Users can test purchasing BugBytes and testing the timed challenge refund mechanism without debiting real bank accounts.

### LIM-002: External AI Cloud Service Dependencies
- **Description:** AI-assisted hints and automated solution feedback rely on Groq Llama 3 cloud endpoints.
- **Mitigation:** When `GROQ_API_KEY` is omitted or rate limits are reached, the system gracefully falls back to deterministic heuristic hints based on AST and error parsing, avoiding crashes or blank hint displays.

### LIM-003: Subprocess Code Execution Environment
- **Description:** On local developer environments without Docker running, code execution uses native OS process spawning (`subprocess.run`) with enforced 5.0-second timeout constraints.
- **Mitigation:** Comprehensive sandbox restrictions check ASTs and prohibit harmful system calls (`os.system`, `subprocess`, file modifications outside temp dirs). For production deployments, the containerized runtime (`docker-compose.yml`) provides complete kernel-level namespace isolation.

### LIM-004: Exclusion of LinkedIn OAuth 2.0
- **Description:** LinkedIn Single Sign-On is deliberately absent from the project.
- **Root Cause:** User explicitly requested complete purge (`remove login through linkedin completely`).
- **Current Behavior:** Only Google Cloud Identity and GitHub Developer OAuth are active. All backend serializers, views, routes, and frontend buttons for LinkedIn have been deleted.

### LIM-005: Vector RAG / ChromaDB Document Store (Out of Scope)
- **Description:** The project does not currently employ ChromaDB or vector embedding databases.
- **Status:** Out of Scope. The application's AI features operate via direct contextual challenge prompting rather than document retrieval augmented generation.
