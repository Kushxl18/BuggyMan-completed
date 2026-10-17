# BuggyMan Performance & Benchmark Report

**Document ID:** PERF-REP-2026-v1.0  
**Project:** BuggyMan  
**Environment:** Windows 11 Enterprise (Intel Core / Multi-core, 16GB RAM)  
**Database:** PostgreSQL 16 on Neon Cloud (SSL)  
**Date:** October 16, 2026  

---

## 1. Performance Overview

Performance testing evaluated code execution latency, database query efficiency, frontend bundle download footprint, and API throughput under typical user loads.

---

## 2. Benchmark Metrics & Observations

### 2.1 Backend API Response Times
- **`/api/health`:** < 15ms (Fast path health check)
- **`/api/challenges` (Catalog Query):** ~45ms (Indexed query with category/difficulty filters)
- **`/api/career-insights` (ML Computation):** ~65ms (Calculates role readiness on the fly)
- **`/api/leaderboard` (Sorted Ranking):** ~50ms (Indexed descending sort on total score)

### 2.2 Sandboxed Execution Latency
- **Python Native Evaluation:** ~180ms - 320ms (Spawns subprocess, injects assertions, executes script, parses JSON output)
- **In-Memory SQLite Evaluation:** ~85ms - 140ms (Instant ephemeral SQLite database instantiation, schema injection, and result set comparison)
- **Timeout Termination Overhead:** 5.01s total duration (Clean termination with immediate garbage collection of process handles)

### 2.3 Frontend Bundle & Load Performance
- **Vite Production Bundle:**
  - `dist/index.html`: 1.34 kB (gzip: 0.65 kB)
  - `dist/assets/index-BxNp-SzN.css`: 66.27 kB (gzip: 11.31 kB)
  - `dist/assets/vendor-monaco-BYBarJBh.js`: 14.91 kB (gzip: 5.14 kB)
  - `dist/assets/vendor-icons-XmNLz291.js`: 39.61 kB (gzip: 7.79 kB)
  - `dist/assets/vendor-react-D4ylq4wB.js`: 164.61 kB (gzip: 53.74 kB)
  - `dist/assets/index-BKhBolMC.js`: 363.82 kB (gzip: 76.37 kB)
  - `dist/assets/vendor-charts-BVu-Kpu6.js`: 411.00 kB (gzip: 110.77 kB)
- **Total Bundle Size (gzipped):** ~280 kB total transfer size across all vendor chunks.
- **Vite Build Time:** 9.50 seconds.

---

## 3. Concurrency & Connection Pool Recommendations

1. **Database Connections:** In high-concurrency production deployments, use PgBouncer / Neon pooled connection strings (`?sslmode=require&pooler=true`) to avoid exhausting server connection limits.
2. **Gunicorn Workers:** Default recommended setting: `workers = (2 * CPU_CORES) + 1` with 2 threads per worker.
