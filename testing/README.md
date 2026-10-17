# BuggyMan QA & Testing Documentation Portal

Welcome to the comprehensive Quality Assurance, Automation, and Testing documentation suite for **BuggyMan**.

---

## 1. Quick Navigation Guide

| Category | Document / Workbook | Purpose |
| :--- | :--- | :--- |
| **Architecture** | [`PROJECT_ARCHITECTURE.md`](PROJECT_ARCHITECTURE.md) | Full system design, components, and data flow |
| **Features** | [`FEATURE_INVENTORY.md`](FEATURE_INVENTORY.md) | Catalog of all implemented features and out-of-scope items |
| **APIs** | [`API_INVENTORY.md`](API_INVENTORY.md) | Endpoint specifications, HTTP methods, and auth requirements |
| **Strategy** | [`TEST_STRATEGY.md`](TEST_STRATEGY.md) | Testing philosophy, test pyramid, and defect severity levels |
| **Plan** | [`TEST_PLAN.md`](TEST_PLAN.md) | Scope, phases, and entry/exit criteria |
| **Test Cases** | [`TEST_CASES.md`](TEST_CASES.md) | Detailed test specifications and steps |
| **Execution** | [`TEST_EXECUTION_REPORT.md`](TEST_EXECUTION_REPORT.md) | Categorized test execution metrics and findings |
| **Final Sign-off** | [`FINAL_TEST_SUMMARY.md`](FINAL_TEST_SUMMARY.md) | Executive summary, metrics dashboard, and release verdict |
| **Environment** | [`TEST_ENVIRONMENT.md`](TEST_ENVIRONMENT.md) | Host, runtime, database, and sanitized environment variables |
| **Limitations** | [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | Documented constraints and accepted risks |

### Excel Workbooks
- **Traceability Matrix:** [`REQUIREMENT_TRACEABILITY_MATRIX.xlsx`](REQUIREMENT_TRACEABILITY_MATRIX.xlsx)
- **Test Cases:** [`TEST_CASES.xlsx`](TEST_CASES.xlsx)
- **Execution Results:** [`TEST_EXECUTION_RESULTS.xlsx`](TEST_EXECUTION_RESULTS.xlsx)
- **Defect Log:** [`BUG_REPORTS.xlsx`](BUG_REPORTS.xlsx)

### Specialized Reports
- **API Test Report:** [`API_TEST_REPORT.md`](API_TEST_REPORT.md)
- **Security Report:** [`SECURITY_TEST_REPORT.md`](SECURITY_TEST_REPORT.md)
- **Performance Report:** [`PERFORMANCE_TEST_REPORT.md`](PERFORMANCE_TEST_REPORT.md)
- **Automation Report:** [`AUTOMATION_TEST_REPORT.md`](AUTOMATION_TEST_REPORT.md)
- **Regression Report:** [`REGRESSION_TEST_REPORT.md`](REGRESSION_TEST_REPORT.md)
- **Smoke Test Report:** [`DEPLOYMENT_SMOKE_TEST_REPORT.md`](DEPLOYMENT_SMOKE_TEST_REPORT.md)
- **Evidence Index:** [`evidence/README.md`](evidence/README.md)

---

## 2. How to Run the Automated Test Suite

### Running Backend Unit & Integration Tests
Ensure Python 3.13 is active and dependencies are installed:
```powershell
# From project root
cd backend
python manage.py test --keepdb
```

### Running Frontend Production Build & Bundle Checks
```powershell
# From project root
cd frontend
npm run build
```

### Running Django Static System Checks
```powershell
# From project root
cd backend
python manage.py check
```

### Regenerating QA Workbooks
```powershell
# From project root
python testing/generate_workbooks.py
```
