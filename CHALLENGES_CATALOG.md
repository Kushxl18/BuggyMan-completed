# BuggyMan — Complete 120 Challenges Catalog & Specification Guide

> **Comprehensive Reference**: Exhaustive documentation of all 120 authentic production debugging challenges stored in the BuggyMan database, categorized across **Code Challenges**, **SQL Lab**, and **Frontend Studio**.

## Table of Contents

1. [Executive Summary & Difficulty Matrix](#1-executive-summary--difficulty-matrix)
2. [Arena 1: Code Challenges (Backend, Concurrency & APIs — IDs 1–50)](#2-arena-1-code-challenges-backend-concurrency--apis)
3. [Arena 2: SQL Lab (Databases, Query Optimization & Isolation — IDs 51–85)](#3-arena-2-sql-lab-databases-query-optimization--isolation)
4. [Arena 3: Frontend Studio (React, DOM & State Management — IDs 86–120)](#4-arena-3-frontend-studio-react-dom--state-management)
5. [Master Index Table (All 120 Challenges)](#5-master-index-table-all-120-challenges)

---

## 1. Executive Summary & Difficulty Matrix

BuggyMan challenges are designed around **real-world production incidents** rather than theoretical leetcode puzzles. Each challenge places the developer inside an existing codebase containing a subtle bug (race condition, memory leak, incorrect SQL aggregation, React state desynchronization, off-by-one boundary, etc.) with failing integration tests.

| Arena | ID Range | Total | Easy | Medium | Hard | Primary Technologies | Core Focus Areas |
|---|---|---|---|---|---|---|---|
| **Code Challenges** | 1 – 50 | 50 | 15 | 20 | 15 | Python, NodeJS, Django, FastAPI | Concurrency, distributed locks, rate limiters, pagination, transactions, parsing |
| **SQL Lab** | 51 – 85 | 35 | 10 | 15 | 10 | PostgreSQL, SQLite, SQL | Joins, GROUP BY aggregations, recursive CTEs, deadlocks, window functions, NULL semantics |
| **Frontend Studio** | 86 – 120 | 35 | 10 | 15 | 10 | React, JavaScript, HTML5, CSS | State immutability, async race conditions, useEffect closures, controlled forms, layout reflows |
| **Platform Total** | **1 – 120** | **120** | **35** | **50** | **35** | **Polyglot Full-Stack** | **Production Defect Triage, Remediation & Verification** |

---

## 2. Arena 1: Code Challenges (Backend, Concurrency & APIs)

Covering Challenges **1 through 50**. These challenges test backend software engineering, API resilience, concurrency control, distributed systems concepts, serialization, and algorithmic boundary handling.

### Challenge 1: [CODE-E01] API Pagination Skips the Final Record

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Pagination`, `Slicing`, `APIs`, `Python`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `end = min(len(items), page * page_size) - 1`
- **Suspected Component**: `pagination.py`

**Scenario & Defect Overview:**
A document portal API slices audit log records into paginated windows.
Due to an incorrect upper boundary calculation, the slicing expression terminates one element early, omitting the final record on each page and dropping the last item of the dataset.

For example, when requesting page 3 with 25 total records and a page size of 10, the endpoint returns only 4 records (`[20, 21, 22, 23]`) instead of 5 (`[20, 21, 22, 23, 24]`), dropping record index 24.

Correct `paginate(items, page, page_size)` in `pagination.py` so that full page ranges and partial final pages return all expected records, while handling empty datasets and out-of-bounds page requests safely.

**Files in Sandbox:**
- `pagination.py`

**Verification Criteria (4 Test Cases):**
- [Visible Sample Test] **Visible: Full Page Slice Includes Final Record**
- [Visible Sample Test] **Visible: First Page Exact Boundary**
- [Hidden Test] **Hidden: Out of bounds page returns empty list**
- [Hidden Test] **Hidden: Empty dataset handling**

---

### Challenge 2: [CODE-E02] Base64 Cursor Encoding Breaks for Unicode Input

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Unicode`, `Base64`, `Encoding`, `Python`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `raw_bytes = cursor_str.encode("ascii")`
- **Suspected Component**: `cursor_encoder.py`

**Scenario & Defect Overview:**
### Company Scenario
An international logistics platform encodes search pagination cursors into opaque strings for clients. Cursors often contain localized warehouse names in Japanese, German, or Arabic.

### Bug Report
Pagination requests fail with HTTP 500 error `UnicodeEncodeError: 'ascii' codec can't encode characters` when paginating search results for non-English warehouse locations.

### Steps to Reproduce
1. Search for items in warehouse "東京_Warehouse_01".
2. Generate cursor token using `encode_cursor`.
3. Server raises `UnicodeEncodeError`.

### Expected Behavior
`encode_cursor` and `decode_cursor` must handle arbitrary UTF-8 Unicode strings without crashing.

### Actual Behavior
The encoder forces ASCII encoding (`cursor.encode("ascii")`), which throws on any character with ord > 127.

### Impact
International users and regional distribution centers cannot page through warehouse inventories.

### Requirements
- Update `encode_cursor` to encode strings using UTF-8 before base64 encoding.
- Update `decode_cursor` to decode bytes using UTF-8 back to a string.
- Return empty string if cursor is empty or None.

### Learning Objectives
- UTF-8 vs ASCII byte serialization in web APIs.
- Base64 encoding for URL-safe opaque cursor tokens.

**Files in Sandbox:**
- `cursor_encoder.py`

**Verification Criteria (4 Test Cases):**
- [Visible Sample Test] **Visible: Japanese Kanji Location Cursor**
- [Visible Sample Test] **Visible: German Umlaut Cursor**
- [Hidden Test] **Hidden: Empty cursor handling**
- [Hidden Test] **Hidden: Plain ASCII backward compatibility**

---

### Challenge 3: [CODE-E03] Empty API Responses Cause a Runtime Error

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Error Handling`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Error Handling`, `Defensive Programming`, `APIs`
- **Skills Tested**: `Python`, `Error Handling`, `Backend`
- **Bug Signature**: `first_item = items[0]`
- **Suspected Component**: `api_client.py`

**Scenario & Defect Overview:**
### Company Scenario
A financial dashboard pulls real-time stock ticker quote summaries from a third-party market data service.

### Bug Report
When market quotes are requested for a newly listed stock or after market close, the vendor API returns an empty payload `{"items": []}`. The parser throws `IndexError: list index out of range`, crashing the ticker worker.

### Steps to Reproduce
1. Fetch quote for unlisted symbol `XYZ`.
2. Vendor response is `{"items": []}`.
3. Parser directly indexes `payload["items"][0]["price"]`.

### Expected Behavior
Return `None` or default `{"price": 0.0, "status": "unavailable"}` when items list is empty or missing.

### Actual Behavior
Unchecked zero-index access `payload["items"][0]` triggers an unhandled `IndexError`.

### Impact
Background pricing daemon crashes, preventing subsequent stock symbols from updating.

### Requirements
- Safely check if `items` is present and non-empty before accessing index 0.
- Return `{"price": 0.0, "status": "unavailable"}` on empty or invalid payload.

**Files in Sandbox:**
- `api_client.py`

**Verification Criteria (4 Test Cases):**
- [Visible Sample Test] **Visible: Normal active payload**
- [Visible Sample Test] **Visible: Empty items list**
- [Hidden Test] **Hidden: Missing items key**
- [Hidden Test] **Hidden: Non-dict payload**

---

### Challenge 4: [CODE-E04] Incorrect Date Parsing Shifts Records to the Wrong Day

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Datetime`, `Parsing`, `Data Processing`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")`
- **Suspected Component**: `date_parser.py`

**Scenario & Defect Overview:**
### Company Scenario
An accounting SaaS application parses bank transaction timestamps formatted as `DD/MM/YYYY` from European and Australian banks.

### Bug Report
A payment made on `05/11/2026` (5th of November) is categorized by the system as `2026-05-11` (11th of May), shifting end-of-year tax deductions into the wrong fiscal quarter.

### Steps to Reproduce
1. Submit date string `"05/11/2026"`.
2. Call `parse_transaction_date`.
3. Output returns date for May 11 instead of November 5.

### Expected Behavior
`parse_transaction_date("05/11/2026")` should parse as `day=5, month=11, year=2026` returning ISO `"2026-11-05"`.

### Actual Behavior
The format string uses `%m/%d/%Y` (US format) instead of `%d/%m/%Y`.

### Impact
Financial quarterly reconciliation fails audit compliance due to misdated revenue entries.

### Requirements
- Correct the strptime format string to `%d/%m/%Y`.
- Return formatted ISO date string `YYYY-MM-DD`.

**Files in Sandbox:**
- `date_parser.py`

**Verification Criteria (4 Test Cases):**
- [Visible Sample Test] **Visible: 5th of November**
- [Visible Sample Test] **Visible: 24th of July**
- [Hidden Test] **Hidden: 1st of January**
- [Hidden Test] **Hidden: Invalid format returns None**

---

### Challenge 5: [CODE-E05] A Retry Counter Stops One Attempt Too Early

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Retries`, `Resilience`, `Loops`
- **Skills Tested**: `Python`, `Backend`, `Error Handling`
- **Bug Signature**: `while attempt < max_retries - 1:`
- **Suspected Component**: `retry_handler.py`

**Scenario & Defect Overview:**
### Company Scenario
An order fulfillment system transmits shipments to an external carrier API that experiences intermittent gateway timeouts.

### Bug Report
When `max_retries=3` is configured, logs show the client only performs 2 attempts total (1 initial + 1 retry) before giving up and flagging orders as failed.

### Steps to Reproduce
1. Configure `execute_with_retry` with `max_retries=3`.
2. Mock an endpoint that fails twice and succeeds on attempt 3.
3. Function returns `None` prematurely without executing the 3rd attempt.

### Expected Behavior
A `max_retries=3` policy must allow up to 3 total attempts if failures occur.

### Actual Behavior
Loop condition `attempt < max_retries - 1` stops execution after 2 attempts.

### Impact
Transient network blips cause premature shipment creation failures and manual support overhead.

### Requirements
- Ensure loop executes up to `max_retries` attempts.
- Return function result on success, or `None` if all retries are exhausted.

**Files in Sandbox:**
- `retry_handler.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Succeeds on attempt 3**
- [Visible Sample Test] **Visible: Succeeds on attempt 1**
- [Hidden Test] **Hidden: Fails all 3 attempts returns None**

---

### Challenge 6: [CODE-E06] Duplicate IDs Cause Incorrect Deduplication

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Deduplication`, `Data Integrity`, `Multi-Tenancy`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `key = r.get("id")`
- **Suspected Component**: `deduplicator.py`

**Scenario & Defect Overview:**
### Company Scenario
A multi-tenant healthcare system imports patient check-in records across regional clinics. Each clinic assigns record IDs independently.

### Bug Report
When ingesting check-ins, patient records from Clinic B overwrite patient records from Clinic A whenever both clinics happen to issue ID `101`.

### Steps to Reproduce
1. Ingest `[{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 2, "id": 101, "name": "Bob"}]`.
2. Deduplication function keys only on `"id"`.
3. Alice's record is completely erased from the output.

### Expected Behavior
Deduplication must use composite identity `(record["clinic_id"], record["id"])` to preserve records across distinct clinics.

### Actual Behavior
The deduplicator keys solely on `record["id"]`.

### Impact
Critical patient diagnostic records are silently overwritten and lost.

### Requirements
- Key unique records by tuple `(record["clinic_id"], record["id"])`.
- Return list of preserved records in original order.

**Files in Sandbox:**
- `deduplicator.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Different clinics with same local ID**
- [Visible Sample Test] **Visible: Same clinic true duplicate removed**
- [Hidden Test] **Hidden: Empty records list**

---

### Challenge 7: [CODE-E07] An Environment Variable Fallback Ignores Valid Configuration

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Configuration`, `Environment Variables`, `Boolean Logic`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `return parsed or 30`
- **Suspected Component**: `config_loader.py`

**Scenario & Defect Overview:**
### Company Scenario
A microservices gateway configures worker connection pool timeouts and port listeners via environment variables.

### Bug Report
When an operator sets `TIMEOUT_SECONDS=0` to disable timeouts for long-running batch ingestion, the application ignores `0` and falls back to default `30` seconds, causing premature batch termination.

### Steps to Reproduce
1. Configure env dict with `{"TIMEOUT_SECONDS": "0"}`.
2. Call `get_timeout_seconds()`.
3. Returns `30` instead of `0`.

### Expected Behavior
Setting `TIMEOUT_SECONDS="0"` must return `0`. Only if the variable is unset or `None` should it use the fallback `30`.

### Actual Behavior
Falsy check `val = os_env.get("TIMEOUT_SECONDS") or 30` evaluates `"0"` in falsy context or `int(val) or 30`.

### Impact
Engineers cannot disable timeouts for batch data migrations, causing repeated pipeline aborts.

### Requirements
- Check explicitly if the variable exists and is not empty.
- Correctly parse `"0"` as integer `0`.

**Files in Sandbox:**
- `config_loader.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Valid zero timeout**
- [Visible Sample Test] **Visible: Unset timeout uses fallback**
- [Hidden Test] **Hidden: Positive timeout preserved**

---

### Challenge 8: [CODE-E08] An Incorrect Cache Key Returns Another Request's Result

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Caching`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Caching`, `Multi-Tenancy`, `Security`
- **Skills Tested**: `Python`, `Caching`, `Backend`
- **Bug Signature**: `return f"user_profile:{user_id}"`
- **Suspected Component**: `cache_manager.py`

**Scenario & Defect Overview:**
### Company Scenario
A multi-tenant e-commerce platform caches customer profile discount rates using Redis key-value storage.

### Bug Report
User 42 belonging to Store A sees the exclusive VIP discount rates belonging to User 42 in Store B!

### Steps to Reproduce
1. Cache profile for `store_id="store_a", user_id="42"` with discount `10%`.
2. Request profile for `store_id="store_b", user_id="42"`.
3. Receives cached `10%` discount from Store A.

### Expected Behavior
Cache keys must be tenant-isolated: `f"store:{store_id}:user:{user_id}"`.

### Actual Behavior
The cache key only includes `user_id`, causing cross-tenant cache collisions.

### Impact
Severe data leak and financial loss from unauthorized discounts applied across separate merchants.

### Requirements
- Update `generate_cache_key(store_id, user_id)` to include both `store_id` and `user_id`.

**Files in Sandbox:**
- `cache_manager.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Different stores produce different keys**
- [Visible Sample Test] **Visible: Key includes both store and user**
- [Hidden Test] **Hidden: Sanitized string format check**

---

### Challenge 9: [CODE-E09] Input Validation Rejects Valid Zero Values

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Validation`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Validation`, `Boolean Logic`, `APIs`
- **Skills Tested**: `Python`, `Validation`, `Backend`
- **Bug Signature**: `if not quantity:`
- **Suspected Component**: `validator.py`

**Scenario & Defect Overview:**
### Company Scenario
An inventory adjustment endpoint allows warehouse managers to update stock counts when physical counts are conducted.

### Bug Report
When a warehouse manager enters `0` to indicate an item is completely out of stock, the API rejects the request with HTTP 400 `"Quantity is required"`.

### Steps to Reproduce
1. Submit payload `{"item_id": "SKU-99", "quantity": 0}`.
2. Call `validate_inventory_update`.
3. Returns `(False, "Quantity is required")`.

### Expected Behavior
`quantity=0` is a valid stock count and must be accepted. Negative values and `None` should be rejected.

### Actual Behavior
`if not quantity:` rejects `0` because 0 is falsy in Python.

### Impact
Warehouse staff cannot zero out out-of-stock items, resulting in false inventory listed online and order cancellations.

### Requirements
- Check `if quantity is None or quantity < 0:` instead of `if not quantity:`.
- Return `(True, "Valid")` for `quantity >= 0`.

**Files in Sandbox:**
- `validator.py`

**Verification Criteria (4 Test Cases):**
- [Visible Sample Test] **Visible: Zero quantity accepted**
- [Visible Sample Test] **Visible: Positive quantity accepted**
- [Hidden Test] **Hidden: Negative quantity rejected**
- [Hidden Test] **Hidden: None quantity rejected**

---

### Challenge 10: [CODE-E10] A CSV Parser Mishandles Quoted Fields

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `CSV`, `Parsing`, `Standard Library`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `return [field.strip().strip('"') for field in row_str.split(",")]`
- **Suspected Component**: `csv_parser.py`

**Scenario & Defect Overview:**
### Company Scenario
A customer relationship manager (CRM) allows users to import contacts via CSV files. Addresses often contain commas enclosed in quotation marks.

### Bug Report
An imported row `"John Doe","123 Maple St, Suite 4","Springfield"` is split into 4 columns instead of 3, corrupting the address and city fields.

### Steps to Reproduce
1. Pass line `"John Doe","123 Maple St, Suite 4","Springfield"` into `parse_csv_row`.
2. Output array has length 4: `["John Doe", "123 Maple St", " Suite 4", "Springfield"]`.

### Expected Behavior
Commas enclosed in double quotes must not split the field. The result should be `["John Doe", "123 Maple St, Suite 4", "Springfield"]`.

### Actual Behavior
Naive `line.split(",")` splits inside quoted substrings.

### Impact
Customer database is populated with malformed addresses and broken postal data.

### Requirements
- Use standard library `csv.reader` (or `io.StringIO`) to parse the CSV row conforming to RFC 4180.

**Files in Sandbox:**
- `csv_parser.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Quoted field with embedded comma**
- [Visible Sample Test] **Visible: Simple CSV line without quotes**
- [Hidden Test] **Hidden: Empty line handling**

---

### Challenge 11: [CODE-E11] Sorting Produces Incorrect Results for Numeric Strings

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Sorting`, `Data Types`, `Algorithms`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `return sorted(levels)`
- **Suspected Component**: `sorter.py`

**Scenario & Defect Overview:**
### Company Scenario
An app store ranking service sorts firmware build versions or priority queues stored in JSON database columns.

### Bug Report
Build numbers sort as `["1", "10", "100", "2", "20"]` instead of numeric order `["1", "2", "10", "20", "100"]`.

### Steps to Reproduce
1. Call `sort_priority_levels(["10", "2", "1", "20", "100"])`.
2. Output is sorted lexicographically rather than numerically.

### Expected Behavior
Numeric strings must be sorted by their actual integer values.

### Actual Behavior
Standard string sort compares character codes ASCII `'1'` < `'2'`, placing `'100'` before `'2'`.

### Impact
High-priority alerts (level 10) are processed after lower-priority alerts (level 2).

### Requirements
- Sort list using `key=int` so numeric strings order by numerical magnitude.

**Files in Sandbox:**
- `sorter.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Numeric magnitude order**
- [Visible Sample Test] **Visible: Single element list**
- [Hidden Test] **Hidden: Empty list handling**

---

### Challenge 12: [CODE-E12] A Response Serializer Omits a Required Field

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Serialization`, `APIs`, `JSON`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `"email": user_model.get("email")
    }`
- **Suspected Component**: `serializer.py`

**Scenario & Defect Overview:**
### Company Scenario
A public REST API publishes user profile endpoints consumed by client SDKs that enforce strict schema validation.

### Bug Report
Mobile apps crash with `SchemaValidationError: Missing required property 'created_at'` when reading the `/api/v1/user` response.

### Steps to Reproduce
1. Fetch serialized user object from `serialize_user_profile(user)`.
2. Observe keys present: `id`, `username`, `email`.
3. `created_at` field is missing.

### Expected Behavior
Serialized payload must contain: `id`, `username`, `email`, `created_at`.

### Actual Behavior
The serializer dictionary omits `created_at`.

### Impact
Client applications crash across iOS and Android on login.

### Requirements
- Include `created_at` in the serialized output dictionary.

**Files in Sandbox:**
- `serializer.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Serializer output includes created_at**
- [Visible Sample Test] **Visible: Exact value serialized**
- [Hidden Test] **Hidden: Empty input handling**

---

### Challenge 13: [CODE-E13] An Incorrect Timeout Conversion Causes Premature Expiration

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Authentication`, `Math & Units`, `Tokens`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `return current_timestamp + int(seconds_to_live / 1000)`
- **Suspected Component**: `token_service.py`

**Scenario & Defect Overview:**
### Company Scenario
An authentication service issues ephemeral short-lived access tokens configured to expire after `seconds_to_live` (default 3600 seconds = 1 hour).

### Bug Report
Users are logged out within 3.6 seconds of logging in!

### Steps to Reproduce
1. Call `calculate_expiration(current_timestamp=1000000, seconds_to_live=3600)`.
2. Notice the calculated timestamp is `1000003` instead of `1003600`.

### Expected Behavior
`calculate_expiration(now, seconds)` must add the full number of seconds: `now + seconds`.

### Actual Behavior
The code incorrectly divides seconds by 1000 (`seconds_to_live / 1000`), treating seconds as if they were milliseconds.

### Impact
Mass user session disconnection and login loops across the production website.

### Requirements
- Add `seconds_to_live` directly to `current_timestamp` without dividing.

**Files in Sandbox:**
- `token_service.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: 1 hour token expiration**
- [Visible Sample Test] **Visible: 60 second token**
- [Hidden Test] **Hidden: Zero duration token**

---

### Challenge 14: [CODE-E14] An Empty List Causes an Indexing Error

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Error Handling`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Defensive Programming`, `Lists`, `Queue`
- **Skills Tested**: `Python`, `Error Handling`
- **Bug Signature**: `return jobs[0]`
- **Suspected Component**: `queue_processor.py`

**Scenario & Defect Overview:**
### Company Scenario
An asynchronous queue worker polls pending notification messages to batch send emails.

### Bug Report
When worker polls an idle queue with no pending messages, it crashes with `IndexError: list index out of range` and exits.

### Steps to Reproduce
1. Call `peek_next_job([])`.
2. Observe unhandled `IndexError`.

### Expected Behavior
Return `None` when queue has 0 jobs.

### Actual Behavior
Accesses `jobs[0]` directly without checking `len(jobs)`.

### Impact
Worker processes exit, triggering alerting noise and leaving system in degraded state.

### Requirements
- Check `if not jobs: return None` before indexing.

**Files in Sandbox:**
- `queue_processor.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Non-empty queue returns first job**
- [Visible Sample Test] **Visible: Empty queue safely returns None**
- [Hidden Test] **Hidden: Single item queue**

---

### Challenge 15: [CODE-E15] Incorrect Rounding Produces Wrong Invoice Totals

- **Arena Domain**: Code Challenges
- **Difficulty**: `Easy` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `Finance`, `Rounding`, `Precision`
- **Skills Tested**: `Python`, `Backend`, `Data Processing`
- **Bug Signature**: `tax_sum = sum(round(item * tax_rate, 2) for item in line_items)`
- **Suspected Component**: `invoice_calculator.py`

**Scenario & Defect Overview:**
### Company Scenario
An enterprise billing service calculates sales tax across line items on customer invoices.

### Bug Report
Customer invoices show a total that is 1 cent off from payment gateway settlements due to rounding line-item tax amounts individually before summing them.

### Steps to Reproduce
1. Calculate tax on 3 line items of $10.05 at 8.25% tax rate.
2. Rounding each item produces $0.83 + $0.83 + $0.83 = $2.49.
3. True tax on total $30.15 is $2.487375 -> rounded to $2.49, but on other amounts like $10.04 it drifts.

### Expected Behavior
Sum line item subtotals first, then compute and round the total tax once: `round(sum(items) * tax_rate, 2)`.

### Actual Behavior
The calculator rounds each individual item's tax before summing: `sum(round(i * tax_rate, 2) for i in items)`.

### Impact
Discrepancies in billing reconciliation cause automated bank audit rejections.

### Requirements
- Compute total subtotal first, then apply tax and round once to 2 decimal places.

**Files in Sandbox:**
- `invoice_calculator.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Total tax calculation without intermediate rounding**
- [Visible Sample Test] **Visible: Single item invoice**
- [Hidden Test] **Hidden: Empty invoice handling**

---

### Challenge 16: [CODE-M01] API Retries Accidentally Repeat a Non-Idempotent Operation

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Idempotency`, `Retries`, `Payments`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `idempotency_key = f"idem_{uuid.uuid4().hex[:8]}"`
- **Suspected Component**: `payment_client.py`

**Scenario & Defect Overview:**
### Company Scenario
A billing microservice sends charge requests to Stripe. To prevent duplicate charges upon network drops, each payment must carry a stable idempotency key.

### Bug Report
When network packets drop and the client retries the charge, customers are charged twice on their credit cards!

### Steps to Reproduce
1. Execute `charge_with_retry(order_id="ord_100", amount=50, max_retries=2)`.
2. Observe that each retry loop iteration generates a brand new `uuid4()` idempotency key.
3. The payment processor treats each attempt as a distinct transaction.

### Expected Behavior
The idempotency key must be generated once before the retry loop and reused across all retry attempts.

### Actual Behavior
`idempotency_key = str(uuid.uuid4())` is inside the loop body, generating new keys for each retry.

### Impact
Double billing of customers, surge in chargeback fees, and payment merchant disputes.

### Requirements
- Generate or derive the idempotency key once outside the retry loop so all attempts for the order share the identical key.

**Files in Sandbox:**
- `payment_client.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Retries reuse identical idempotency key**
- [Visible Sample Test] **Visible: Successful first attempt**

---

### Challenge 17: [CODE-M02] Cache Invalidation Leaves Stale Product Prices

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Caching`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Caching`, `Cache Invalidation`, `Data Consistency`
- **Skills Tested**: `Python`, `Caching`
- **Suspected Component**: `pricing_service.py`

**Scenario & Defect Overview:**
### Company Scenario
A flash-sale retail store caches individual product details as well as category catalog summaries.

### Bug Report
When an administrator edits a product price from $100 down to $60, the category browse page still shows the old $100 price for hours.

### Steps to Reproduce
1. Update product price via `update_product_price(product_id, new_price, category_id)`.
2. Notice `cache.delete(f"product:{product_id}")` is called.
3. Category listing cache `f"category:{category_id}"` is never invalidated!

### Expected Behavior
Both the item cache and the parent category catalog cache must be invalidated when a product price changes.

### Actual Behavior
Only the specific product cache key is deleted.

### Impact
Customers see contradictory pricing between catalog search and checkout, causing cart abandonment.

### Requirements
- Invalidate both `f"product:{product_id}"` and `f"category:{category_id}"` in cache.

**Files in Sandbox:**
- `pricing_service.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Invalidate both product and category keys**

---

### Challenge 18: [CODE-M03] Pagination Produces Duplicates When Sorting is Applied

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Sorting`, `Pagination`, `Determinism`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `sorted_posts = sorted(posts, key=lambda p: p["upvotes"], reverse=True)`
- **Suspected Component**: `paginator.py`

**Scenario & Defect Overview:**
### Company Scenario
A community feed ranks posts by upvote counts. Multiple posts frequently have identical upvote numbers.

### Bug Report
When users scroll through the feed, the same post appears on both Page 1 and Page 2!

### Steps to Reproduce
1. Feed has 10 posts, all with 5 upvotes.
2. Slicing with non-deterministic ordering shifts identical elements between pages.

### Expected Behavior
Sorting must have a secondary deterministic tie-breaker: sort primarily by `upvotes` descending, then secondarily by `id` ascending.

### Actual Behavior
Sorts only by `post["upvotes"]` without a tie-breaker.

### Impact
Users see duplicate posts in feeds and review lists.

### Requirements
- Update sort key to `(-post["upvotes"], post["id"])`.

**Files in Sandbox:**
- `paginator.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Deterministic sort with tie-breaker**

---

### Challenge 19: [CODE-M04] A Webhook Handler Processes the Same Event More Than Once

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Webhooks`, `Idempotency`, `Deduplication`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `order_actions.append(f"FULFILL_{event.get('order_id')}")`
- **Suspected Component**: `webhook_dispatcher.py`

**Scenario & Defect Overview:**
### Company Scenario
A payment webhook consumer processes `payment.succeeded` events sent by Stripe.

### Bug Report
Stripe retries webhook delivery if an ACK is delayed. The handler processes the duplicate event and ships the order twice!

### Steps to Reproduce
1. Deliver event `{"id": "evt_001", "type": "payment.succeeded"}` twice.
2. Handler executes side effect both times.

### Expected Behavior
The handler must check if `event_id` was already processed, record it in processed set/DB, and skip duplicate processing.

### Actual Behavior
The handler executes side effects unconditionally without checking or recording `processed_event_ids`.

### Impact
Duplicate physical orders shipped to customers for a single payment.

### Requirements
- Check `if event_id in processed_events: return "ALREADY_PROCESSED"`.
- Otherwise add `event_id` to `processed_events` and proceed with processing.

**Files in Sandbox:**
- `webhook_dispatcher.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Duplicate event skipped**

---

### Challenge 20: [CODE-M05] Concurrent Updates Overwrite Newer User Preferences

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Optimistic Locking`, `Concurrency`, `Versioning`
- **Skills Tested**: `Python`, `Concurrency`, `Backend`
- **Bug Signature**: `current_record.update(incoming_update)
    return True`
- **Suspected Component**: `preference_manager.py`

**Scenario & Defect Overview:**
### Company Scenario
Users update notification preferences from mobile devices and desktop browsers simultaneously.

### Bug Report
A user toggles dark mode at 10:00:05. A delayed sync request sent at 10:00:01 arrives late and overwrites the newer preference!

### Steps to Reproduce
1. Current profile has `version=3, updated_at=100`.
2. Stale request arrives with `version=2, updated_at=90`.
3. Handler accepts the stale request and overwrites current profile.

### Expected Behavior
Reject or ignore incoming updates if `incoming["version"] <= current["version"]`.

### Actual Behavior
Unconditional overwrite: `current.update(incoming)`.

### Impact
User changes are lost and overwritten by delayed background sync packets.

### Requirements
- Implement optimistic concurrency version check: only update if `incoming["version"] > current["version"]`.
- Return `True` if applied, `False` if rejected due to stale version.

**Files in Sandbox:**
- `preference_manager.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Stale version rejected**
- [Visible Sample Test] **Visible: Newer version accepted**

---

### Challenge 21: [CODE-M06] Timezone Conversion Breaks Scheduled Notifications

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Timezones`, `Datetime`, `Scheduling`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `return (local_hour + utc_offset_hours) % 24`
- **Suspected Component**: `scheduler.py`

**Scenario & Defect Overview:**
### Company Scenario
A medical reminder app sends SMS notifications at 08:00 AM local patient time.

### Bug Report
Patients in New York (UTC-5) receive medication alerts at 03:00 AM in the middle of the night!

### Steps to Reproduce
1. Schedule alert for 08:00 AM in timezone `UTC-5`.
2. Convert to UTC timestamp.
3. System subtracts 5 hours instead of adding 5 hours to reach UTC.

### Expected Behavior
Local time 08:00 at UTC-5 equals 13:00 UTC (8 - (-5) = 13).

### Actual Behavior
Code applies offset in reverse direction: `local_hour - offset` -> `8 - 5 = 3` AM UTC.

### Impact
Patients woken up by late-night alerts, resulting in compliance complaints and unsubscribes.

### Requirements
- Correctly convert scheduled local notification hours into a 24-hour UTC format.
- Ensure positive and negative timezone offsets shift hours properly across day boundaries.

**Files in Sandbox:**
- `scheduler.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: NYC (UTC-5) 8am local -> 1pm UTC**
- [Visible Sample Test] **Visible: Tokyo (UTC+9) 8am local -> 11pm previous day (23)**
- [Hidden Test] **Hidden: London (UTC+0) 8am -> 8am**

---

### Challenge 22: [CODE-M07] An API Client Incorrectly Handles HTTP 429 Responses

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `HTTP`, `Rate Limiting`, `Resilience`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `raw_delay = response_headers["Retry-After"]`
- **Suspected Component**: `http_client.py`

**Scenario & Defect Overview:**
### Company Scenario
An algorithmic trading service fetches market depth feeds from a third-party crypto exchange API.

### Bug Report
When exchange returns HTTP 429 Too Many Requests with header `Retry-After: 5`, client crashes with `ValueError: could not convert string to float` when header is missing or non-numeric, or immediately hammers server with 0 delay.

### Steps to Reproduce
1. Simulate 429 response without `Retry-After` header.
2. Client throws `KeyError` or crashes.

### Expected Behavior
Parse `Retry-After` safely as integer seconds; if missing or invalid, default to a safe exponential backoff (e.g. `default_backoff = 2 ** attempt`).

### Actual Behavior
Unsafe dictionary lookup and lack of default fallback.

### Impact
Trading bot crashes during high market volatility.

### Requirements
- Safely extract `Retry-After` header. If missing or non-digit, return `min(60, 2 ** attempt)`.

**Files in Sandbox:**
- `http_client.py`

**Verification Criteria (3 Test Cases):**
- [Visible Sample Test] **Visible: Valid Retry-After header**
- [Visible Sample Test] **Visible: Missing header uses exponential backoff**
- [Hidden Test] **Hidden: Non-numeric header fallback**

---

### Challenge 23: [CODE-M08] A File-Processing Pipeline Silently Drops Malformed Records

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Data Pipelines`, `Error Handling`, `Auditability`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `except Exception:
            pass`
- **Suspected Component**: `pipeline.py`

**Scenario & Defect Overview:**
### Company Scenario
A payroll pipeline imports weekly employee timesheets from CSV rows.

### Bug Report
When an employee enters their hours as `"forty"` instead of `40`, their entire timesheet is silently deleted without notifying HR!

### Steps to Reproduce
1. Ingest row `{"emp_id": "E100", "hours": "forty"}`.
2. Broad `except: pass` silently discards the row.
3. Employee receives a $0 paycheck on Friday.

### Expected Behavior
Capture errors in a quarantine list: `{"emp_id": emp_id, "error": str(err)}` so HR is alerted to fix the row.

### Actual Behavior
Bare `except: pass` suppresses the exception and drops the record from both successful and error outputs.

### Impact
Employees underpaid, triggering wage compliance law penalties.

### Requirements
- Valid records added to `valid_records`.
- Invalid records captured in `quarantined_records` with `{"record": r, "error": str(e)}`.

**Files in Sandbox:**
- `pipeline.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Malformed row quarantined**

---

### Challenge 24: [CODE-M09] A Background Worker Loses Failed Jobs

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Queues`, `Resilience`, `Dead-Letter Queue`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `queue.ack(job["id"])
    job_fn(job)`
- **Suspected Component**: `worker_queue.py`

**Scenario & Defect Overview:**
### Company Scenario
An order processing background queue executes customer notification and inventory reservation tasks.

### Bug Report
When an unhandled database lock error occurs during job execution, the job vanishes forever instead of being sent to the Dead-Letter Queue (DLQ).

### Steps to Reproduce
1. Dequeue job.
2. Worker marks job as "COMPLETED" before executing.
3. Job crashes, leaving it marked finished.

### Expected Behavior
Acknowledge completion only after successful execution. If execution raises, route job to DLQ.

### Actual Behavior
Early acknowledgment removes the job from recovery mechanisms.

### Impact
Orders remain in pending state indefinitely with no retry attempt.

### Requirements
- Execute job in try block.
- On success: `queue.ack(job["id"])`.
- On exception: `queue.send_to_dlq(job, str(e))`.

**Files in Sandbox:**
- `worker_queue.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Failed job sent to DLQ**

---

### Challenge 25: [CODE-M10] A Database Transaction Partially Updates Related Records

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Transactions`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Transactions`, `Atomicity`, `Rollback`
- **Skills Tested**: `Python`, `Backend`, `Transactions`
- **Bug Signature**: `if receiver not in balances:
        return False`
- **Suspected Component**: `account_transfer.py`

**Scenario & Defect Overview:**
### Company Scenario
A banking service transfers money between customer balances.

### Bug Report
$100 is deducted from Sender account, but a database constraint error occurs when crediting Receiver account. The transaction does not rollback, and $100 simply disappears into thin air!

### Steps to Reproduce
1. Execute `transfer_funds(db, sender_id, receiver_id, amount)`.
2. Step 1 deducts from sender.
3. Step 2 raises exception.
4. Sender balance remains deducted without receiver receiving funds.

### Expected Behavior
Both debit and credit must be atomic. If either fails, sender balance must be restored to its original value.

### Actual Behavior
Lack of rollback restores sender balance.

### Impact
Account balance discrepancies and regulatory auditing non-compliance.

### Requirements
- Save initial balance snapshot.
- If receiver credit fails, rollback sender balance to initial value and re-raise.

**Files in Sandbox:**
- `account_transfer.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Sender balance restored on receiver failure**
- [Visible Sample Test] **Visible: Successful transfer**

---

### Challenge 26: [CODE-M11] An Asynchronous Request Returns Stale Data

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Race Conditions`, `Async`, `Sequence Ordering`
- **Skills Tested**: `Python`, `Concurrency`
- **Bug Signature**: `self.current_result = data
        return True`
- **Suspected Component**: `data_fetcher.py`

**Scenario & Defect Overview:**
### Company Scenario
An async search suggestion service dispatches backend lookups as the user types queries into a search bar.

### Bug Report
User quickly types "react", then deletes and types "python". The slower "react" request completes after "python", overwriting the search results with "react"!

### Steps to Reproduce
1. Issue Request 1 for "react" (takes 200ms).
2. Issue Request 2 for "python" (takes 50ms).
3. Request 1 finishes last and overwrites the state.

### Expected Behavior
Only apply the response if the request sequence ID matches or exceeds the latest issued sequence ID.

### Actual Behavior
Every response writes to `state["result"]` regardless of sequence order.

### Impact
Users see search results for previous queries they already deleted.

### Requirements
- Track `latest_seq_id`.
- Ignore responses where `response_seq_id < latest_seq_id`.

**Files in Sandbox:**
- `data_fetcher.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Stale response discarded**

---

### Challenge 27: [CODE-M12] A Token Refresh Process Creates Intermittent Authentication Failures

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Authentication`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Authentication`, `Token Management`, `Concurrency`
- **Skills Tested**: `Python`, `Backend`, `Security`
- **Bug Signature**: `self.access_token = self.refresh_fn()`
- **Suspected Component**: `token_refresh.py`

**Scenario & Defect Overview:**
### Company Scenario
An OAuth client issues refresh token requests when access tokens expire.

### Bug Report
When 5 API calls return 401 at the same millisecond, 5 separate refresh requests are launched concurrently. The authorization server detects reuse of the same refresh token and revokes user access entirely!

### Steps to Reproduce
1. Call `get_active_token` concurrently from multiple threads.
2. Observe 5 separate refresh calls executed.

### Expected Behavior
A single refresh request must be shared (single-flight / mutex) across all concurrent callers.

### Actual Behavior
No synchronization lock, triggering multiple duplicate refresh token calls.

### Impact
Legitimate users logged out and account sessions invalidated.

### Requirements
- Use a flag / in-flight token check to ensure only one refresh runs, and subsequent calls reuse the refreshed token.

**Files in Sandbox:**
- `token_refresh.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Reuses cached token when valid**

---

### Challenge 28: [CODE-M13] An Incorrect Merge Algorithm Loses Configuration Fields

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Deep Merge`, `Recursion`, `Configuration`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `result.update(override)
    return result`
- **Suspected Component**: `config_merger.py`

**Scenario & Defect Overview:**
### Company Scenario
A Kubernetes operator merges user-provided Helm chart override values with default cluster configurations.

### Bug Report
User supplies `{"database": {"port": 5433}}`. The merged config completely deletes `{"database": {"host": "localhost", "name": "prod"}}`!

### Steps to Reproduce
1. Default: `{"db": {"host": "localhost", "port": 5432}}`.
2. Override: `{"db": {"port": 5433}}`.
3. Output: `{"db": {"port": 5433}}` (host is missing!).

### Expected Behavior
Deeply merge nested dictionaries so non-conflicting sibling keys are preserved.

### Actual Behavior
Shallow `dict.update()` replaces the entire nested `db` dictionary.

### Impact
Production clusters fail to start because database hosts and connection settings are wiped.

### Requirements
- Implement recursive deep merge of nested dictionaries.

**Files in Sandbox:**
- `config_merger.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Sibling nested keys preserved**

---

### Challenge 29: [CODE-M14] An Inventory Update Produces Incorrect Stock Totals

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Inventory`, `Validation`, `Business Logic`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `inventory[item_id] -= qty
    return inventory[item_id]`
- **Suspected Component**: `inventory_service.py`

**Scenario & Defect Overview:**
### Company Scenario
An order checkout processor decrements warehouse stock when an order is placed.

### Bug Report
When available stock is 2 and customer orders 5, stock becomes `-3`, allowing customer to buy non-existent goods.

### Steps to Reproduce
1. Stock is 2.
2. Call `decrement_stock(item_id, requested_qty=5)`.
3. Stock decremented to -3 without raising error.

### Expected Behavior
If `requested_qty > available_qty`, raise `ValueError("Insufficient stock")` and do not alter stock.

### Actual Behavior
Blind subtraction without verifying availability.

### Impact
Overselling physical stock resulting in unfulfillable orders and customer refunds.

### Requirements
- Check `if current_stock < qty: raise ValueError("Insufficient stock")`.

**Files in Sandbox:**
- `inventory_service.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Oversell raises ValueError**
- [Visible Sample Test] **Visible: Valid decrement**

---

### Challenge 30: [CODE-M15] A CSV Export Corrupts Embedded Commas and Newlines

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `CSV`, `Export`, `RFC 4180`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `return ",".join(str(f) for f in fields) + "\n"`
- **Suspected Component**: `csv_exporter.py`

**Scenario & Defect Overview:**
### Company Scenario
An admin panel exports user support feedback comments to CSV for analytical reporting in Excel.

### Bug Report
When user feedback contains commas or line breaks (e.g., `"Great service,
fast delivery"`), the exported CSV breaks across lines and shifts columns in Excel.

### Steps to Reproduce
1. Export row with comment `"Great service,
fast delivery"`.
2. Raw string join produces broken unquoted text.

### Expected Behavior
Fields with commas, quotes, or newlines must be enclosed in quotes according to RFC 4180.

### Actual Behavior
Naive string join `",".join(row)`.

### Impact
Corrupted spreadsheets in corporate accounting and analytics teams.

### Requirements
- Use Python standard library `csv.writer` and `io.StringIO` to format CSV rows properly.

**Files in Sandbox:**
- `csv_exporter.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Escaped field with comma**

---

### Challenge 31: [CODE-M16] A Batch Processor Mishandles Partial Failures

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Batch Processing`, `Resilience`, `Error Isolation`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `for item in items:
        send_fn(item)`
- **Suspected Component**: `batch_processor.py`

**Scenario & Defect Overview:**
### Company Scenario
A bulk notification engine delivers SMS messages in batches of 100 recipients.

### Bug Report
If recipient #42 has an invalid phone number, the entire batch aborts, and recipients 43-100 never receive their alerts!

### Steps to Reproduce
1. Send batch with 5 items where item 3 throws an error.
2. Whole function throws, aborting remaining items.

### Expected Behavior
Catch individual item exceptions, collect success and failed items separately, and continue processing the rest of the batch.

### Actual Behavior
Uncaught exception aborts the loop.

### Impact
Single invalid user input disrupts alerts for thousands of unaffected users.

### Requirements
- Return `{"succeeded": [...], "failed": [{"id": ..., "error": ...}]}`.

**Files in Sandbox:**
- `batch_processor.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Sibling items processed despite middle failure**

---

### Challenge 32: [CODE-M17] Incorrect Pagination Cursors Produce Infinite Loops

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Pagination`, `Cursors`, `Infinite Loops`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `next_cursor = f"cur_{last_id}"
    return`
- **Suspected Component**: `cursor_paginator.py`

**Scenario & Defect Overview:**
### Company Scenario
A data sync crawler fetches external CRM records page-by-page until no more records remain.

### Bug Report
The sync crawler runs for 24 hours in an infinite loop, continuously requesting the same empty page millions of times.

### Steps to Reproduce
1. Fetch final page (returns 0 items).
2. API response continues to return `next_cursor="cur_end"` instead of `None`.
3. Client continues requesting `next_cursor` endlessly.

### Expected Behavior
When returned items count is 0 or less than `page_size`, `next_cursor` must be `None`.

### Actual Behavior
Always returns a non-null `next_cursor`.

### Impact
Server CPU exhaustion, API rate-limit exhaustion, and runaway cloud infrastructure costs.

### Requirements
- If fewer records than page_size are returned, terminate pagination by setting the next cursor to None.

**Files in Sandbox:**
- `cursor_paginator.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Final page next_cursor is None**
- [Visible Sample Test] **Visible: Full page generates next cursor**

---

### Challenge 33: [CODE-M18] A Data Transformation Fails for Optional Nested Properties

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Data Transformation`, `Defensive Programming`, `Null Safety`
- **Skills Tested**: `Python`, `Data Processing`
- **Bug Signature**: `city = profile["address"]["city"]`
- **Suspected Component**: `transformer.py`

**Scenario & Defect Overview:**
### Company Scenario
An address formatting service processes user profile forms to produce postal labels.

### Bug Report
When a user profile has no secondary address (`address["secondary"]` is `None` or omitted), formatting throws `TypeError: 'NoneType' object is not subscriptable`.

### Steps to Reproduce
1. Pass profile `{"name": "Alice", "address": None}`.
2. Call `format_postal_address`.
3. Crash on `profile["address"]["city"]`.

### Expected Behavior
Safely handle missing or None address fields, defaulting city to `"Unknown City"`.

### Actual Behavior
Direct nested indexing without null safety.

### Impact
Users without full address details cannot access checkout screens.

### Requirements
- Safely extract nested properties using `.get()` with dictionary default: `(profile.get("address") or {}).get("city", "Unknown City")`.

**Files in Sandbox:**
- `transformer.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Missing address safely handled**
- [Visible Sample Test] **Visible: Full address formatted**

---

### Challenge 34: [CODE-M19] A Rate Limiter Resets Counters Incorrectly

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Rate Limiting`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Rate Limiting`, `Sliding Window`, `Algorithms`
- **Skills Tested**: `Python`, `Backend`, `Security`
- **Bug Signature**: `if len(self.history) >= self.max_requests:
            return False`
- **Suspected Component**: `rate_limiter.py`

**Scenario & Defect Overview:**
### Company Scenario
An API gateway limits free-tier API clients to 100 requests per minute to protect upstream services from DDoS traffic.

### Bug Report
A client sends 100 requests at 12:00:59, and another 100 requests at 12:01:01. The server receives 200 requests within a 2-second window without rate limiting!

### Steps to Reproduce
1. Fix-window counter resets exactly at the minute mark.
2. Burst across the minute boundary allows 2x limit.

### Expected Behavior
A sliding-window rate limiter must purge timestamps older than `now - 60` and check if remaining requests exceed limit.

### Actual Behavior
Fixed-window resets counter to 0 on every minute rollover.

### Impact
API servers overwhelmed by boundary burst attacks.

### Requirements
- Prune timestamps older than `current_time - window_size`.
- If `len(timestamps) >= max_requests`, return `False` (rate limited).
- Otherwise append `current_time` and return `True`.

**Files in Sandbox:**
- `rate_limiter.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Expired timestamps pruned allowing new request**
- [Visible Sample Test] **Visible: Active window limit enforced**

---

### Challenge 35: [CODE-M20] An Exception Handler Hides a Meaningful Application Failure

- **Arena Domain**: Code Challenges
- **Difficulty**: `Medium` | **Technology**: `Python` | **Category**: `Error Handling`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `Error Handling`, `Exceptions`, `Observability`
- **Skills Tested**: `Python`, `Error Handling`, `Backend`
- **Bug Signature**: `except Exception:
        return False`
- **Suspected Component**: `service_client.py`

**Scenario & Defect Overview:**
### Company Scenario
An authentication service queries an external LDAP server for corporate credentials.

### Bug Report
When LDAP server credentials expire, the service catches `Exception` and returns `{"authenticated": False, "reason": "Bad credentials"}`. Administrators spend days resetting user passwords when LDAP service was actually unreachable.

### Steps to Reproduce
1. LDAP server raises `ConnectionRefusedError`.
2. Generic handler masks the server error as user password failure.

### Expected Behavior
Differentiate operational errors (`ConnectionError`) from authentication errors (`AuthenticationError`), re-raising operational errors.

### Actual Behavior
Catches broad `Exception` and treats system failure as user error.

### Impact
Misdiagnosis of production infrastructure outages as end-user mistakes.

### Requirements
- Re-raise `ConnectionError` or infrastructure exceptions.
- Only return `{"authenticated": False}` for expected `ValueError` / invalid password.

**Files in Sandbox:**
- `service_client.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: ConnectionError re-raised**
- [Visible Sample Test] **Visible: Bad credentials handled cleanly**

---

### Challenge 36: [CODE-H01] Concurrent Payment Requests Cause Duplicate Charges

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Concurrency`, `Distributed Locks`, `Fintech`, `Race Conditions`
- **Skills Tested**: `Python`, `Concurrency`, `Security`
- **Bug Signature**: `if order_id in paid_orders:
        return {"status": "ALREADY_PAID"}`
- **Suspected Component**: `payment_gateway.py`

**Scenario & Defect Overview:**
### Company Scenario
A high-volume fintech gateway processes credit card checkout submissions. Users on mobile apps frequently double-tap the "Pay Now" button.

### Bug Report
When two requests arrive within 5 milliseconds of each other, both requests pass the `is_order_paid` check before either sets the paid flag, charging the customer's card twice!

### Steps to Reproduce
1. Two concurrent threads execute `process_payment(order_id)`.
2. Thread 1 checks `is_paid` -> False.
3. Thread 2 checks `is_paid` -> False.
4. Both charge credit card and mark paid.

### Expected Behavior
Use an atomic lock (or test-and-set primitive) to ensure only one thread can process payment for a given order ID.

### Actual Behavior
Check-then-act race condition (TOCTOU) allows parallel executions.

### Impact
Double payments, cardholder disputes, and merchant processing account penalties.

### Requirements
- Acquire lock with `lock_set.add(order_id)`. If order is already in `lock_set` or `paid_set`, return `{"status": "DUPLICATE_IGNORED"}`.
- Upon completion, add to `paid_set` and remove from `lock_set`.

**Files in Sandbox:**
- `payment_gateway.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Concurrent lock prevents duplicate charge**

---

### Challenge 37: [CODE-H02] A Distributed Job Processor Executes Non-Idempotent Jobs Twice

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Backend`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Distributed Systems`, `Leases`, `Heartbeats`
- **Skills Tested**: `Python`, `Backend`, `Architecture`
- **Bug Signature**: `def renew_lease(leases, job_id, current_time, extension=30):
    pass`
- **Suspected Component**: `job_scheduler.py`

**Scenario & Defect Overview:**
### Company Scenario
A video transcoding cluster distributes heavy rendering jobs across worker nodes with a 30-second lease timeout.

### Bug Report
When a video takes 45 seconds to transcode, the cluster scheduler assumes worker 1 died, revokes its lease, and assigns the job to worker 2, causing both workers to write conflicting output files!

### Steps to Reproduce
1. Worker 1 starts long-running job.
2. Lease expires after 30s while worker 1 is still processing.
3. Scheduler re-queues job to worker 2.

### Expected Behavior
Long-running jobs must periodically send heartbeats to extend their lease while active.

### Actual Behavior
Fixed timeout without heartbeat extension causes false-positive dead worker assumptions.

### Impact
Wasted compute, corrupted multi-part video uploads, and doubled cloud rendering bills.

### Requirements
- Provide `heartbeat(lease_tracker, job_id, extension_seconds)` method to extend the expiration deadline during execution.

**Files in Sandbox:**
- `job_scheduler.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Heartbeat renews lease preventing reassignment**

---

### Challenge 38: [CODE-H03] Incorrect Transaction Isolation Causes Inconsistent Inventory

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Concurrency`, `Inventory`, `Race Conditions`
- **Skills Tested**: `Python`, `Concurrency`
- **Bug Signature**: `current_seats = inventory.get(flight_id, 0)
    if current_seats < requested_seats:`
- **Suspected Component**: `inventory_allocator.py`

**Scenario & Defect Overview:**
### Company Scenario
An airline seat allocation service processes flight bookings during holiday flash sales.

### Bug Report
Two customers buy the last seat on Flight 302 simultaneously. The system confirms both tickets, leading to passenger boarding denial at the gate!

### Steps to Reproduce
1. Available seats = 1.
2. User A and User B check availability concurrently.
3. Both read 1, decrement to 0, and confirm.

### Expected Behavior
Perform atomic compare-and-swap or conditional reservation: only decrement if `available > 0`.

### Actual Behavior
Unsynchronized read followed by separate write.

### Impact
Oversold flights, regulatory passenger compensation penalties, and reputational damage.

### Requirements
- Atomically check and reserve: if `stock[flight_id] >= seats`, decrement and return `True`. Otherwise return `False`.

**Files in Sandbox:**
- `inventory_allocator.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Second allocation fails when stock exhausted**

---

### Challenge 39: [CODE-H04] Cache Invalidation Races with Concurrent Database Updates

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Caching`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Cache-Aside`, `Concurrency`, `Data Consistency`
- **Skills Tested**: `Python`, `Caching`
- **Bug Signature**: `cache.delete(f"user:{user_id}")
    db[user_id] = new_bio`
- **Suspected Component**: `cache_aside.py`

**Scenario & Defect Overview:**
### Company Scenario
A social media platform caches user profile bios using the cache-aside pattern.

### Bug Report
User updates bio from "Dev" to "Senior Dev". A concurrent read request repopulates the cache with the old value "Dev", where it stays stuck forever!

### Steps to Reproduce
1. Update starts: deletes cache.
2. Concurrent read misses cache, reads old DB value "Dev", and puts "Dev" into cache.
3. Update writes "Senior Dev" to DB.
4. Cache is now permanently out of sync with DB!

### Expected Behavior
Write to the database first, and delete the cache AFTER the database commit succeeds.

### Actual Behavior
Deletes cache BEFORE writing to the database.

### Impact
Permanent cache drift where users see stale profiles until the next manual cache purge.

### Requirements
- Ensure database write executes first: `db.write(key, value)`.
- Then invalidate cache: `cache.delete(key)`.

**Files in Sandbox:**
- `cache_aside.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: DB write precedes cache deletion**

---

### Challenge 40: [CODE-H05] A Distributed Lock is Released by the Wrong Request

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Distributed Locks`, `Redis`, `Concurrency`
- **Skills Tested**: `Python`, `Concurrency`, `Security`
- **Bug Signature**: `if lock_key in lock_storage:
        del lock_storage[lock_key]`
- **Suspected Component**: `distributed_lock.py`

**Scenario & Defect Overview:**
### Company Scenario
A microservices system uses distributed Redis locks to serialize critical report generation tasks.

### Bug Report
Request A acquires the lock with TTL=10s. Request A runs slow (12s). The lock expires and Request B acquires it. Request A finally finishes and calls `release_lock`, inadvertently releasing Request B's lock!

### Steps to Reproduce
1. Client A acquires lock with token `"token_A"`.
2. Lock expires, Client B acquires with `"token_B"`.
3. Client A calls `release_lock(key)` without passing token.
4. Client B's lock is prematurely released.

### Expected Behavior
`release_lock(key, token)` must check that the stored lock value matches the caller's unique token before releasing.

### Actual Behavior
Unconditional deletion of the lock key.

### Impact
Multiple workers execute critical mutual-exclusion tasks concurrently.

### Requirements
- Only delete the lock if `lock_storage.get(key) == token`.

**Files in Sandbox:**
- `distributed_lock.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Wrong token cannot release lock**
- [Visible Sample Test] **Visible: Valid owner releases lock**

---

### Challenge 41: [CODE-H06] A Retry Mechanism Causes a Request Storm During an Outage

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `API & Web`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Resilience`, `Exponential Backoff`, `Jitter`, `Thundering Herd`
- **Skills Tested**: `Python`, `Backend`, `APIs`
- **Bug Signature**: `return min(max_delay, base_delay * attempt + jitter)`
- **Suspected Component**: `backoff_client.py`

**Scenario & Defect Overview:**
### Company Scenario
A mobile banking application connects to payment backend clusters during peak sale events.

### Bug Report
When an upstream server encounters a 1-second lag, 50,000 mobile apps retry on exact synchronized 2-second intervals, creating massive spike waves (thundering herd) that crash the database.

### Steps to Reproduce
1. Execute retry delay formula `delay = base_delay * attempt`.
2. All clients calculate exact identical delays without randomization.

### Expected Behavior
Add exponential backoff with randomized jitter to spread retry attempts over time.

### Actual Behavior
Deterministic linear backoff with zero jitter.

### Impact
Self-inflicted DDoS preventing upstream servers from recovering from outages.

### Requirements
- Implement exponential backoff with jitter: `min(max_delay, base_delay * (2 ** attempt)) + jitter`.

**Files in Sandbox:**
- `backoff_client.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Exponential growth at attempt 3**
- [Visible Sample Test] **Visible: Capped at max_delay**

---

### Challenge 42: [CODE-H07] Concurrent File Writes Corrupt Generated Reports

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `File I/O`, `Atomicity`, `Concurrency`
- **Skills Tested**: `Python`, `Backend`
- **Bug Signature**: `file_system[dest_path] = content
    return dest_path`
- **Suspected Component**: `report_writer.py`

**Scenario & Defect Overview:**
### Company Scenario
An automated financial reporting system generates end-of-day summary CSV files.

### Bug Report
When two scheduled reports generate simultaneously, they append lines to the same target file at the same time, producing interleaved, corrupted CSV records.

### Steps to Reproduce
1. Two processes write to `report.csv` simultaneously in append mode.
2. Rows interleave mid-line.

### Expected Behavior
Write to a unique temporary file first, and atomically replace the destination file upon completion.

### Actual Behavior
Direct non-atomic write to destination path.

### Impact
Corrupted financial compliance reports sent to regulators.

### Requirements
- Generate unique temp filename `f"{dest_path}.tmp.{pid}"`.
- Write content to temp file, then rename/replace to `dest_path`.

**Files in Sandbox:**
- `report_writer.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Writes to temp file then renames**

---

### Challenge 43: [CODE-H08] An Asynchronous Task Deadlocks Under Concurrent Execution

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Deadlocks`, `Concurrency`, `Lock Ordering`
- **Skills Tested**: `Python`, `Concurrency`
- **Bug Signature**: `return list(required_resources)`
- **Suspected Component**: `resource_manager.py`

**Scenario & Defect Overview:**
### Company Scenario
A resource allocator manages access to GPU clusters and high-speed NVMe storage arrays.

### Bug Report
Task 1 acquires GPU, then waits for NVMe. Task 2 acquires NVMe, then waits for GPU. Both tasks hang forever in a circular deadlock!

### Steps to Reproduce
1. Worker 1 locks resources in order `['GPU', 'NVMe']`.
2. Worker 2 locks resources in order `['NVMe', 'GPU']`.
3. System deadlocks.

### Expected Behavior
Enforce a global canonical ordering (e.g. alphabetical) on lock acquisition so all workers acquire resources in the identical sequence.

### Actual Behavior
Arbitrary resource locking sequence.

### Impact
Entire cluster worker pool freezes, halting all computational jobs.

### Requirements
- Sort resource IDs alphabetically before acquisition: `sorted(required_resources)`.

**Files in Sandbox:**
- `resource_manager.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Deterministic sorted lock order**

---

### Challenge 44: [CODE-H09] A Permission Check Occurs After a Sensitive State Change

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Security`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Security`, `Authorization`, `Defensive Programming`
- **Skills Tested**: `Python`, `Security`, `Backend`
- **Bug Signature**: `user_db[target] = new_role
    if not auth_checker(actor):`
- **Suspected Component**: `access_controller.py`

**Scenario & Defect Overview:**
### Company Scenario
An enterprise access management portal processes role upgrades and administrative privilege assignments.

### Bug Report
An unprivileged user submits a request to promote themselves to Superuser. The handler grants the role in the database before running the authorization check. If the check throws, the user still remains Superuser!

### Steps to Reproduce
1. Call `elevate_user_role(actor="guest", target_user="guest", new_role="admin")`.
2. State changed before authorization guard.

### Expected Behavior
Check permissions first. If unauthorized, reject immediately without touching user state.

### Actual Behavior
Modifies user state before checking authorization.

### Impact
Privilege escalation vulnerability allowing ordinary users to seize administrator rights.

### Requirements
- Verify `is_authorized(actor, "ADMIN_UPGRADE")` at the beginning of the function.

**Files in Sandbox:**
- `access_controller.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Unauthorized attempt leaves target role unchanged**

---

### Challenge 45: [CODE-H10] A Batch Migration Loses Records After a Partial Failure

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Data & Processing`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Migrations`, `Checkpoints`, `Fault Tolerance`
- **Skills Tested**: `Python`, `Backend`, `Data Processing`
- **Bug Signature**: `for record in batch:
            self.transform(record)
        return True`
- **Suspected Component**: `migration_runner.py`

**Scenario & Defect Overview:**
### Company Scenario
A customer database migration script transfers 1,000,000 user rows to a new cloud datastore in batches of 1,000.

### Bug Report
At batch 500, a transient network error terminates the migration. When re-run, the script starts over from batch 1 without checkpointing, creating duplicate rows and missing records.

### Steps to Reproduce
1. Execute migration without saving checkpoint.
2. Interruption leaves no record of the last successful cursor.

### Expected Behavior
After each batch commits, persist the last processed record ID to a checkpoint store. On resume, start from `checkpoint_id`.

### Actual Behavior
No checkpoint persistence.

### Impact
Corrupted migrations and multi-day manual database recovery operations.

### Requirements
- Persist the last processed record identifier in the checkpoint store after each successful batch write.

**Files in Sandbox:**
- `migration_runner.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Checkpoint updated after batch**

---

### Challenge 46: [CODE-H11] An Event-Processing Pipeline Reorders Dependent Events

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Event Sourcing`, `Partitioning`, `Concurrency`
- **Skills Tested**: `Python`, `Concurrency`, `Architecture`
- **Bug Signature**: `return random.randint(0, num_shards - 1)`
- **Suspected Component**: `event_stream.py`

**Scenario & Defect Overview:**
### Company Scenario
An e-commerce order event processor receives `ORDER_CREATED` followed by `ORDER_CANCELLED`.

### Bug Report
Because events are assigned to random thread pool workers, `ORDER_CANCELLED` executes before `ORDER_CREATED`, failing with "Order not found", and the order is created afterward and remains active!

### Steps to Reproduce
1. Emit `ORDER_CREATED` and `ORDER_CANCELLED` for `order_id="101"`.
2. Random worker assignment processes them out of order.

### Expected Behavior
Events with the same partition key (`order_id`) must route to the same worker shard to preserve FIFO sequence.

### Actual Behavior
Random round-robin routing breaks entity event sequencing.

### Impact
Cancelled orders are fulfilled and shipped to customers.

### Requirements
- Compute partition shard assignments deterministically from the entity identifier so all events for the same entity route to the same worker in order.

**Files in Sandbox:**
- `event_stream.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Same entity ID always routes to identical shard**

---

### Challenge 47: [CODE-H12] Incorrect Rollback Logic Leaves Related Resources Inconsistent

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Transactions`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Saga Pattern`, `Distributed Transactions`, `Compensating Actions`
- **Skills Tested**: `Python`, `Architecture`, `Transactions`
- **Bug Signature**: `if completed:
                completed[-1].rollback()`
- **Suspected Component**: `saga_coordinator.py`

**Scenario & Defect Overview:**
### Company Scenario
A multi-service travel booking saga coordinates Flight, Hotel, and Car Rental reservations.

### Bug Report
Flight succeeds, Hotel succeeds, but Car Rental fails. The rollback coordinator cancels the Hotel but forgets to cancel the Flight!

### Steps to Reproduce
1. Execute multi-step booking.
2. Step 3 fails.
3. Flight reservation is never cancelled.

### Expected Behavior
A saga rollback must iterate through all completed steps in reverse and invoke their corresponding compensating transactions.

### Actual Behavior
Hardcoded partial rollback only cleans up the immediately preceding step.

### Impact
Customers charged hundreds of dollars for orphaned flights after rental car booking failed.

### Requirements
- Iterate through `completed_steps` in reverse order: `for step in reversed(completed_steps): step.rollback()`.

**Files in Sandbox:**
- `saga_coordinator.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: All completed steps rolled back in reverse**

---

### Challenge 48: [CODE-H13] A Streaming Parser Leaks Memory for Large Inputs

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Performance`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Memory Management`, `Streaming`, `Generators`
- **Skills Tested**: `Python`, `Performance`
- **Bug Signature**: `all_chunks = []
    lines = []
    for chunk in chunks:
        all_chunks.append(chunk)`
- **Suspected Component**: `stream_parser.py`

**Scenario & Defect Overview:**
### Company Scenario
A log analysis pipeline streams multi-gigabyte server access logs to count 500 error spikes.

### Bug Report
The parser process runs out of memory (`OOMKilled`) when parsing a 2GB file, despite being intended as a streaming generator.

### Steps to Reproduce
1. Feed 100,000 chunks to `stream_lines`.
2. Notice `all_chunks.append(chunk)` accumulates all previous chunks into memory.

### Expected Behavior
Keep only the trailing unparsed remainder in memory, discarding consumed bytes.

### Actual Behavior
Appends all incoming chunks to a persistent list.

### Impact
Server container memory exhaustion and pod crash-looping in Kubernetes.

### Requirements
- Maintain only `buffer` string. When newline is found, yield line and retain only `buffer[idx+1:]`.

**Files in Sandbox:**
- `stream_parser.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Streaming generator yields lines without full accumulation**

---

### Challenge 49: [CODE-H14] A Multi-Step Account Update Leaves Partially Modified State

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Transactions`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Transactions`, `Validation`, `Atomicity`
- **Skills Tested**: `Python`, `Backend`, `Validation`
- **Bug Signature**: `if "@" in new_email:
        profile["email"] = new_email
    if not (new_phone`
- **Suspected Component**: `account_service.py`

**Scenario & Defect Overview:**
### Company Scenario
A customer portal allows users to update both their account email and phone number in a single action.

### Bug Report
Email updates successfully, but phone number fails regex validation. The user profile is left with updated email but unchanged phone, creating inconsistent state.

### Steps to Reproduce
1. Profile: `email="old@test.com", phone="111-222"`.
2. Submit `email="new@test.com", phone="invalid_phone"`.
3. Profile has `new@test.com` and `111-222`.

### Expected Behavior
Validate all fields completely BEFORE modifying any profile fields. If any field fails validation, do not modify the user profile.

### Actual Behavior
Modifies email before validating phone number.

### Impact
Inconsistent user profiles and failed two-factor SMS verification delivery.

### Requirements
- Validate both email and phone first.
- Only mutate `profile` if both fields are valid.

**Files in Sandbox:**
- `account_service.py`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Invalid phone leaves email untouched**

---

### Challenge 50: [CODE-H15] A Concurrent Reservation System Oversells Limited Inventory

- **Arena Domain**: Code Challenges
- **Difficulty**: `Hard` | **Technology**: `Python` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `Concurrency`, `Reservations`, `Timeouts`
- **Skills Tested**: `Python`, `Concurrency`, `Backend`
- **Bug Signature**: `reservations[seat_id] = {"user": user_id, "expires_at": current_time + ttl}
    return True`
- **Suspected Component**: `seat_reservation.py`

**Scenario & Defect Overview:**
### Company Scenario
A concert ticketing system reserves front-row seats for buyers during a 5-minute checkout window.

### Bug Report
Seat A1 is reserved by User 1 at 12:00:00. At 12:00:01, User 2 submits a reservation for Seat A1 and succeeds, displacing User 1!

### Steps to Reproduce
1. User 1 reserves Seat A1.
2. User 2 requests Seat A1 before User 1's reservation expires.
3. System overwrites reservation owner.

### Expected Behavior
A seat can only be reserved if it is currently unreserved OR if its previous reservation has expired: `now > res["expires_at"]`.

### Actual Behavior
Unconditional assignment: `reservations[seat_id] = {"user": user, "expires_at": now + ttl}`.

### Impact
Double booked concert seats leading to customer disputes at box office.

### Requirements
- Check `if seat_id in reservations and current_time < reservations[seat_id]["expires_at"]: return False`.
- Otherwise reserve and return `True`.

**Files in Sandbox:**
- `seat_reservation.py`

**Verification Criteria (2 Test Cases):**
- [Visible Sample Test] **Visible: Active reservation blocks new buyer**
- [Visible Sample Test] **Visible: Expired reservation allows new buyer**

---

## 3. Arena 2: SQL Lab (Databases, Query Optimization & Isolation)

Covering Challenges **51 through 85**. These challenges test relational database query writing, schema constraints, multi-table joins, NULL logic, window functions, recursive CTE hierarchies, concurrent transaction anomalies, and indexing.

### Challenge 51: [SQL-E01] Customer Report Excludes Records Containing NULL Values

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Filtering`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `NULL Handling`, `Three-Valued Logic`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `WHERE opt_out != 1`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer success team generates a contact list of all registered clients who have not opted out of marketing updates (`opt_out = 0` or NULL).

### Bug Report
Customers whose opt-out preference is unset (stored as `NULL` in the database) are completely missing from the campaign export.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe only customers with explicit `opt_out = 0` are returned.
3. Customers with `opt_out IS NULL` are omitted.

### Expected Behavior
Include both `opt_out = 0` and `opt_out IS NULL`.

### Actual Behavior
Clients whose opt-out preference is unset evaluate to UNKNOWN under direct inequality comparisons and are omitted.

### Impact
Over 40% of the customer base is omitted from critical service announcements.

### Requirements
- Update `query.sql` to select `id`, `name`, and `email` for all clients who have not explicitly chosen to opt out of marketing updates.
- Clients whose preference is unset (NULL) must be included in the export.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Includes NULL and 0 opt-out records**

---

### Challenge 52: [SQL-E02] Monthly Revenue Report Uses the Wrong Date Boundary

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Filtering`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Dates`, `Half-Open Intervals`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `BETWEEN '2026-10-01' AND '2026-10-31'`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A finance team generates the October 2026 revenue statement.

### Bug Report
Transactions processed on October 31st at 18:30 are missing from the report, under-reporting monthly revenue by $15,000!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `WHERE order_date BETWEEN '2026-10-01' AND '2026-10-31'`.
3. Datetime values on October 31st (e.g. `'2026-10-31 18:30:00'`) are excluded because `'2026-10-31'` evaluates to `'2026-10-31 00:00:00'`.

### Expected Behavior
Include all transactions belonging to the calendar month of October 2026, including orders placed on October 31st with non-zero timestamps.

### Actual Behavior
BETWEEN with date-only string cuts off the final day at midnight.

### Impact
Incorrect revenue reported to investors and fiscal regulators.

### Requirements
- Ensure query.sql includes all orders placed within the calendar month of October 2026, capturing transactions through the end of October 31st.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Total includes October 31st afternoon order**

---

### Challenge 53: [SQL-E03] Product Search Filters the Wrong Status

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Filtering`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Filtering`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `WHERE status = 'archived'`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An online catalog displays currently available products to customers.

### Bug Report
Items that are archived or pending approval appear in customer search, while in-stock active items are hidden.

### Steps to Reproduce
1. Query in `query.sql` uses `WHERE status = 'archived'`.
2. Active products are excluded.

### Expected Behavior
Filter specifically for `status = 'active'`.

### Actual Behavior
Filters for `status = 'archived'`.

### Impact
Customers cannot purchase active inventory; archived obsolete items are erroneously ordered.

### Requirements
- Ensure query.sql filters exclusively for active catalog products.
- Sort active products in ascending alphabetical order by product name.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Returns active products ordered by name**

---

### Challenge 54: [SQL-E04] An INNER JOIN Removes Customers Without Orders

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Joins`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Joins`, `LEFT JOIN`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `INNER JOIN orders o`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer marketing team wants a complete user roster showing their order counts, including new users who haven't placed an order yet.

### Bug Report
New users (0 orders) are completely omitted from the user roster!

### Steps to Reproduce
1. Customer "Charlie" registered yesterday and has 0 orders.
2. Query in `query.sql` uses `INNER JOIN orders`.
3. Charlie is omitted from the result set.

### Expected Behavior
All customers must appear. Customers without orders should show `order_id = NULL` or `0` orders.

### Actual Behavior
`INNER JOIN` drops customers who have no matching rows in the `orders` table.

### Impact
Customer onboarding emails are not triggered for new signups who haven't bought yet.

### Requirements
- Change `INNER JOIN` to `LEFT JOIN` to preserve all customers.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: LEFT JOIN includes Charlie with NULL order_id**

---

### Challenge 55: [SQL-E05] A GROUP BY Query Calculates the Wrong Average

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Aggregation`, `AVG`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `WHERE bonus > 0 GROUP BY`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An HR performance dashboard calculates the average bonus percentage awarded across departments.

### Bug Report
Employees who received $0 bonus are omitted from the average, artificially inflating the department's bonus metric.

### Steps to Reproduce
1. Department has 2 employees: Alice received 10%, Bob received 0% (or NULL).
2. Query filters `WHERE bonus > 0` before running `AVG(bonus)`.
3. Average returns 10% instead of true average 5%.

### Expected Behavior
Average must include all department employees, counting zero/missing bonus as 0.

### Actual Behavior
Filters out 0 values before aggregation.

### Impact
HR leadership relies on inflated compensation metrics during budget planning.

### Requirements
- Calculate the true department average bonus across all employees, accounting for employees with no bonus as 0.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Department average includes 0% bonus**

---

### Challenge 56: [SQL-E06] Duplicate Email Records Are Not Detected Correctly

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Duplicates`, `HAVING`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `HAVING COUNT(*) >= 1`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A data cleanup pipeline scans user registration databases to identify accounts sharing duplicate email addresses.

### Bug Report
The duplicate detection script returns every single email address in the database, including unique ones!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `HAVING COUNT(*) >= 1`.
3. Unique accounts with count = 1 are incorrectly returned.

### Expected Behavior
Only emails with `COUNT(*) > 1` (more than one occurrence) are duplicates.

### Actual Behavior
Uses `>= 1` which matches every single row.

### Impact
Unique accounts are incorrectly flagged for deletion or account merge.

### Requirements
- Change condition to `HAVING COUNT(*) > 1`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Only true duplicate emails returned**

---

### Challenge 57: [SQL-E07] An Invoice Query Incorrectly Rounds Monetary Totals

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Math`, `ROUND`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `ROUND(SUM(subtotal * tax_rate))`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An invoicing database computes tax totals across order line items.

### Bug Report
Invoices report fractional penny differences from bank statements because line items are rounded to integer dollars rather than 2 decimal places.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `ROUND(SUM(subtotal * tax_rate))` without decimal argument.
3. Totals are truncated to whole dollars.

### Expected Behavior
Round currency to exactly 2 decimal places: `ROUND(..., 2)`.

### Actual Behavior
Rounds to 0 decimal places.

### Impact
Accounting ledger totals fail to reconcile with stripe merchant payouts.

### Requirements
- Update query to `ROUND(SUM(subtotal * tax_rate), 2) AS total_tax`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Monetary total rounded to 2 decimal places**

---

### Challenge 58: [SQL-E08] A Report Includes Cancelled Orders

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Filtering`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Filtering`, `Revenue`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT SUM(amount) AS completed_gmv FROM orders;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An executive sales metric dashboard calculates daily net gross merchandise value (GMV).

### Bug Report
Cancelled and refunded orders are included in the sales GMV calculation, inflating daily performance numbers.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice cancelled orders with `status = 'cancelled'` are summed.

### Expected Behavior
Only orders with `status = 'completed'` (or `status != 'cancelled'`) should be summed.

### Actual Behavior
Sums all rows in `orders` regardless of status.

### Impact
Management bases hiring decisions on inflated gross sales numbers.

### Requirements
- Filter the total revenue query to include only fulfilled, completed orders.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Total only includes completed orders**

---

### Challenge 59: [SQL-E09] A Query Orders Numeric Values Stored as Text Incorrectly

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Sorting`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Sorting`, `Type Casting`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `ORDER BY priority_level ASC;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A priority dispatch queue sorts tasks by urgency score (`priority_level`), which is stored in a `VARCHAR` column in a legacy table.

### Bug Report
Tasks order as `'10', '100', '2', '20'` instead of `'2', '10', '20', '100'`!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe alphabetical string sorting of numbers.

### Expected Behavior
Order rows by numerical value: `ORDER BY CAST(priority_level AS INTEGER) ASC`.

### Actual Behavior
Orders by textual lexicographical ASCII value.

### Impact
Urgent priority 100 emergency repairs are placed after minor priority 2 maintenance requests.

### Requirements
- Cast `priority_level` to `INTEGER` in the `ORDER BY` clause.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Tasks ordered by numerical priority level**

---

### Challenge 60: [SQL-E10] A Query Returns the Wrong Top-Selling Product Because of Incorrect Sorting

- **Arena Domain**: SQL Lab
- **Difficulty**: `Easy` | **Technology**: `SQL` | **Category**: `Sorting`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `SQL`, `Sorting`, `LIMIT`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `ORDER BY total_sold ASC LIMIT 1;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An inventory re-ordering dashboard highlights the #1 best-selling product of the week.

### Bug Report
The dashboard displays the least-sold item (1 unit sold) as the "Top Seller" instead of the actual best-selling item (500 units sold)!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `ORDER BY total_sold ASC LIMIT 1`.
3. Lowest seller is returned.

### Expected Behavior
Order by `total_sold DESC LIMIT 1` to retrieve the highest seller.

### Actual Behavior
Sorts `ASC` (ascending).

### Impact
Factory re-orders large batches of unsold inventory while popular stock runs out.

### Requirements
- Update sort direction to `DESC` to return top seller.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Returns top selling item with highest count**

---

### Challenge 61: [SQL-M01] A JOIN Duplicates Revenue Because of Multiple Order Items

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Joins`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Joins`, `Aggregation`, `Cartesian Product`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `JOIN order_items i ON o.id = i.order_id GROUP BY o.customer_id`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An analytics query reports total customer spending by joining the `orders` table with the `order_items` table.

### Bug Report
An order of $100 containing 3 line items counts as $300 revenue, tripling customer spending metrics!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `orders` table has `total_amount = 100.00`.
3. Joining with `order_items` replicates the order row for every item.
4. `SUM(o.total_amount)` multiplies order totals.

### Expected Behavior
Sum `o.total_amount` directly from `orders` without joining `order_items`, OR sum `item_price * quantity` from `order_items`.

### Actual Behavior
Joins `order_items` and sums `orders.total_amount`.

### Impact
Revenue reports inflated by up to 400%, misleading financial stakeholders.

### Requirements
- Calculate true total revenue per customer from `orders` table directly, grouped by `customer_id`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Accurate customer revenue without join duplication**

---

### Challenge 62: [SQL-M02] Customer Lifetime Value is Inflated by an Incorrect Aggregation

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Aggregation`, `AVG`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT customer_id, SUM(amount) AS aov FROM orders`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer intelligence report calculates average order value (AOV) per customer across multiple stores.

### Bug Report
Customer average order value calculation averages the daily averages, which skews metrics toward low-volume days.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `AVG(order_amount)` over aggregated day totals rather than individual orders.

### Expected Behavior
Calculate true AOV as `SUM(amount) / COUNT(id)` directly across all individual orders.

### Actual Behavior
Averages the pre-aggregated daily sums.

### Impact
Inaccurate lifetime value projections in VIP customer retention tiers.

### Requirements
- Compute true average order value: `ROUND(AVG(amount), 2)` grouped by `customer_id`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: True average order value per customer**

---

### Challenge 63: [SQL-M03] Pagination Skips or Duplicates Rows When Ordering is Not Deterministic

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Sorting`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Pagination`, `Deterministic Ordering`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `ORDER BY created_at DESC LIMIT 2 OFFSET 0;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An audit log viewer paginates system events in chunks of 2 rows using `LIMIT 2 OFFSET n`.

### Bug Report
Events with identical timestamps randomly shift positions between queries, so Page 1 and Page 2 display duplicate rows.

### Steps to Reproduce
1. Query `LIMIT 2 OFFSET 0` ordered by `created_at DESC`.
2. Query `LIMIT 2 OFFSET 2` ordered by `created_at DESC`.
3. Records with identical `created_at` values appear on both pages.

### Expected Behavior
Add `id ASC` as a secondary deterministic sort column to guarantee stable row order: `ORDER BY created_at DESC, id ASC`.

### Actual Behavior
Sorts solely by `created_at DESC`.

### Impact
Compliance auditors miss critical security events due to unstable pagination windows.

### Requirements
- Add secondary unique sort key `id ASC` to the `ORDER BY` clause.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Deterministic sort with id tie-breaker**

---

### Challenge 64: [SQL-M04] A Window Function Uses the Wrong Partition

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Window Functions`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Window Functions`, `RANK`, `PARTITION BY`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `RANK() OVER (ORDER BY revenue DESC) AS regional_rank`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An enterprise sales leaderboard ranks account executives by closed revenue within their respective global sales regions.

### Bug Report
Sales reps in the EMEA region are ranked against reps in APAC and Americas, rather than competing solely within their regional teams.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `RANK() OVER (ORDER BY revenue DESC)` lacks `PARTITION BY region`.
3. Rankings are global instead of regional.

### Expected Behavior
Rank sales executives partitioned by regional division: `RANK() OVER (PARTITION BY region ORDER BY revenue DESC)`.

### Actual Behavior
Omits `PARTITION BY region`.

### Impact
Regional sales quarterly performance bonuses distributed to the wrong employees.

### Requirements
- Add `PARTITION BY region` to the window ranking function.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Regional partition ranks top rep in each region as #1**

---

### Challenge 65: [SQL-M05] A Monthly Report Mishandles Timezone Boundaries

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Dates`, `strftime`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `substr(payment_date, 6, 2) AS month`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A subscription billing portal groups recurring payments by calendar month using UTC timestamps.

### Bug Report
Subscriptions renewed on September 1st at 00:30 UTC are placed into August because query attempts manual offset subtraction without boundary validation.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice manual string slicing cuts off date without `strftime('%Y-%m', payment_date)`.

### Expected Behavior
Extract standard year-month group key: `strftime('%Y-%m', payment_date)`.

### Actual Behavior
Manual substring parsing shifts dates.

### Impact
Revenue numbers misattributed between fiscal months.

### Requirements
- Use `strftime('%Y-%m', payment_date) AS month` and group by month.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Grouped by YYYY-MM formatted month**

---

### Challenge 66: [SQL-M06] A LEFT JOIN Becomes an Accidental INNER JOIN

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Joins`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Joins`, `LEFT JOIN`, `WHERE vs ON`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `LEFT JOIN subscriptions s ON u.id = s.user_id WHERE s.status = 'active'`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer directory query displays user account profiles along with their most recent premium subscription plan. Users without premium plans must still be displayed.

### Bug Report
Users with no subscription are excluded from the directory despite using a `LEFT JOIN`!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `WHERE s.status = 'active'`.
3. Users with no subscription have `s.status = NULL`. The `WHERE` clause filters out `NULL`, converting the `LEFT JOIN` into an `INNER JOIN`!

### Expected Behavior
Move the condition `s.status = 'active'` into the `ON` clause of the `LEFT JOIN`: `LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'`.

### Actual Behavior
Filters `s.status = 'active'` in the `WHERE` clause.

### Impact
Free-tier users disappear from administrative moderation lists.

### Requirements
- Move filter into `ON` clause so unmatched users remain with NULL subscription details.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Preserves Bob with NULL plan_name**

---

### Challenge 67: [SQL-M07] An Inventory Report Calculates Incorrect Available Stock

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `NULL Handling`, `COALESCE`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `(physical_stock - reserved_stock) AS available_stock`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A warehouse management system computes available stock as `physical_stock - reserved_stock`.

### Bug Report
Items with zero pending reservations (`reserved_stock = NULL`) show `available_stock = NULL` instead of their physical stock!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `physical_stock - reserved_stock`.
3. In SQL arithmetic, `10 - NULL` evaluates to `NULL`.

### Expected Behavior
Use `COALESCE(reserved_stock, 0)` so unreserved items subtract 0.

### Actual Behavior
Subtracts raw NULL, wiping out availability numbers.

### Impact
In-stock items show as unavailable in product catalog, halting sales.

### Requirements
- Compute available inventory by subtracting reserved stock from physical stock, handling unset reserved quantities as 0.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Keyboard shows available_stock = 25**

---

### Challenge 68: [SQL-M08] A Query Incorrectly Handles NULL Values in Conditional Aggregation

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Conditional Aggregation`, `CASE WHEN`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer engagement dashboard counts how many orders were successfully delivered vs returned.

### Bug Report
The delivered orders column count is inaccurate because `COUNT(CASE WHEN status = 'delivered' THEN 0 ELSE NULL END)` evaluates `0` as non-null!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`.
3. `COUNT()` counts non-null values, including `0`, so returned orders are counted as delivered!

### Expected Behavior
Use `SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)` OR `COUNT(CASE WHEN status = 'delivered' THEN 1 END)`.

### Actual Behavior
Uses `COUNT()` with `ELSE 0`, counting all rows.

### Impact
Executive dashboard shows a 100% delivery rate despite thousands of returned packages.

### Requirements
- Accurately calculate delivered order counts without miscounting non-delivered orders in the aggregate.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: True delivered count is 2**

---

### Challenge 69: [SQL-M09] A CTE Filters Records Before Aggregation When Filtering Should Occur Afterward

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `CTE`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `CTE`, `HAVING vs WHERE`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT customer_id, amount FROM orders WHERE amount >= 500`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer loyalty tier report identifies high-value accounts whose total annual spending exceeds $500.

### Bug Report
The report filters out individual purchases under $500 in the CTE before summing, omitting loyal customers who made ten $60 purchases!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `WITH large_orders AS (SELECT * FROM orders WHERE amount >= 500)`.
3. Customers with multiple smaller orders totalling > $500 are omitted.

### Expected Behavior
Sum all orders first per customer in the CTE, then filter `WHERE total_spent >= 500`.

### Actual Behavior
Filters individual transaction amounts in the initial CTE.

### Impact
High-value repeat customers excluded from VIP perks and loyalty reward distributions.

### Requirements
- Aggregate total spending per customer across all orders first in the CTE, then filter for qualifying high-value clients in the outer query.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Customers 101 and 102 both have total >= 500**

---

### Challenge 70: [SQL-M10] A Duplicate-Detection Query Flags Valid Records

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Duplicates`, `NULL Handling`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT phone, COUNT(*) AS count FROM users GROUP BY phone`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A fraud-detection system flags accounts suspected of multi-accounting by matching identical telephone numbers.

### Bug Report
Over 15,000 legitimate users who have empty or unset phone numbers (`phone IS NULL`) are all grouped together and flagged as a fraudulent syndicate!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `GROUP BY phone HAVING COUNT(*) > 1`.
3. `NULL` phone values group together into a single cluster.

### Expected Behavior
Exclude `NULL` and empty phone strings from the duplicate scan: `WHERE phone IS NOT NULL AND phone != ''`.

### Actual Behavior
Groups all NULL records into a single false-positive duplicate cluster.

### Impact
Thousands of legitimate user accounts locked by automated security filters.

### Requirements
- Exclude missing, null, and empty phone values before evaluating duplicate phone counts.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Only non-null duplicate phone 555-0100 returned**

---

### Challenge 71: [SQL-M11] A Ranking Query Assigns Incorrect Positions to Tied Values

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Window Functions`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Window Functions`, `RANK vs DENSE_RANK`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `DENSE_RANK() OVER (ORDER BY score DESC) AS rank`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A hackathon scoring platform displays leaderboard ranks based on judge scores.

### Bug Report
Two competitors tied for 1st place with 95 points. The next participant with 90 points is displayed as 2nd place instead of 3rd place!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `DENSE_RANK() OVER (ORDER BY score DESC)`.
3. Scores 95, 95, 90 receive ranks 1, 1, 2 (dense rank does not skip ranks).

### Expected Behavior
Standard competition ranking must skip ranks after ties: 1, 1, 3. Use `RANK()`.

### Actual Behavior
Uses `DENSE_RANK()`.

### Impact
Award ceremony medals and prize distributions given to wrong placement tiers.

### Requirements
- Review the difference between RANK() and DENSE_RANK(): RANK leaves gaps after tied positions, whereas DENSE_RANK does not.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Competition rank assigns Charlie rank 3**

---

### Challenge 72: [SQL-M12] A Subquery Returns Multiple Rows Unexpectedly

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Subqueries`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Subqueries`, `IN vs EQUALS`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `WHERE discount_id = (SELECT id FROM discounts`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A product pricing query applies store discounts by matching eligible category promotions.

### Bug Report
The product API crashes with `OperationalError: subquery returns more than 1 row` whenever a category has multiple active discount coupons.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice scalar comparison `WHERE discount_id = (SELECT id FROM discounts WHERE category = 'tech')`.
3. When multiple discounts exist, scalar equality `=` throws a database error.

### Expected Behavior
Use `IN` instead of `=` for multi-row subqueries: `WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech')`.

### Actual Behavior
Uses scalar `=` operator against a multi-row subquery.

### Impact
Product catalog crashes across major retail categories.

### Requirements
- Use a set-membership operator rather than scalar equality to safely handle subqueries that return multiple matching discount records.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: IN operator matches all eligible products**

---

### Challenge 73: [SQL-M13] A Report Combines Historical and Current Prices Incorrectly

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Joins`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Historical Data`, `Data Integrity`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SUM(oi.quantity * p.current_price) AS total_revenue`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An order line item audit checks sales totals. Prices change over time, so past orders must multiply by historical unit price, not the current catalog price.

### Bug Report
A customer bought an item in 2025 for $50. In 2026, the price was raised to $80. The 2025 sales report recalculates the past order at $80, distorting historical revenue!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice query joins `products` table and uses `p.current_price` instead of historical `oi.price_at_purchase`.

### Expected Behavior
Use `oi.price_at_purchase * oi.quantity` recorded at the time of purchase.

### Actual Behavior
Multiplies by `p.current_price`.

### Impact
Audited historical balance sheets are altered every time modern catalog prices change.

### Requirements
- Multiply quantity by historical price: `SUM(oi.quantity * oi.price_at_purchase) AS total_revenue`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Total reflects historical purchase price (2 * 50 = 100)**

---

### Challenge 74: [SQL-M14] A Query Counts Orders Instead of Distinct Customers

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `Aggregation`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `COUNT DISTINCT`, `Metrics`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT COUNT(customer_id) AS unique_customers FROM orders;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An executive KPI dashboard reports monthly active unique purchasing customers.

### Bug Report
If 1 customer places 10 orders in a day, the dashboard reports 10 active customers instead of 1!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `COUNT(customer_id)`.
3. Multiple orders by the same customer are counted repeatedly.

### Expected Behavior
Count distinct customers: `COUNT(DISTINCT customer_id) AS unique_customers`.

### Actual Behavior
Uses `COUNT(customer_id)` without `DISTINCT`.

### Impact
Customer base size inflated by 300% on investor quarterly reports.

### Requirements
- Use `COUNT(DISTINCT customer_id) AS unique_customers`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Distinct customers count is 2**

---

### Challenge 75: [SQL-M15] A Recursive Query Omits Part of an Organizational Hierarchy

- **Arena Domain**: SQL Lab
- **Difficulty**: `Medium` | **Technology**: `SQL` | **Category**: `CTE`
- **Points**: `150 XP` | **Time Estimate**: `15 mins`
- **Topics**: `SQL`, `Recursive CTE`, `Hierarchies`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `ON e.manager_id = org.manager_id`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An HR organizational chart application displays all employees reporting under the CEO (including indirect reports).

### Bug Report
Only direct reports to the CEO appear; second-level managers and individual contributors are omitted!

### Steps to Reproduce
1. Execute recursive query in `query.sql`.
2. Notice recursive term joins `WHERE e.manager_id = org.manager_id` instead of `WHERE e.manager_id = org.id`.
3. Hierarchy stops descending after level 1.

### Expected Behavior
The recursive join must match employee `manager_id` with parent `org.id`.

### Actual Behavior
Joins on identical manager_id, failing to recurse down the tree.

### Impact
Department heads cannot view full staffing headcount across sub-teams.

### Requirements
- Correct the recursive join condition so employee manager relationships properly link to the ancestor node's primary key.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Full 4-level tree generated**

---

### Challenge 76: [SQL-H01] Concurrent Inventory Reservations Oversell Stock

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Concurrency`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Concurrency`, `Conditional UPDATE`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `UPDATE inventory SET stock = stock - 1 WHERE id = 10;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A flash-sale ticketing engine executes warehouse deductions when checkout begins.

### Bug Report
When stock is 1, two concurrent buyers both execute `UPDATE inventory SET stock = stock - 1 WHERE id = 10`, setting stock to -1 and overselling the item.

### Steps to Reproduce
1. Stock = 1.
2. Two updates execute without condition `stock >= requested_qty`.
3. Stock becomes negative.

### Expected Behavior
Guarded update: only decrement if `stock >= 1`: `UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1`.

### Actual Behavior
Blind decrement without checking availability in WHERE clause.

### Impact
Over-allocated physical inventory and canceled customer orders.

### Requirements
- Add guard condition `AND stock >= 1` (or `stock > 0`) to the UPDATE query.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Guarded update only decrements when stock available**

---

### Challenge 77: [SQL-H02] A Payment Transaction Updates Balances Without Maintaining Consistency

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Transactions`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Transactions`, `Ledger Consistency`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `WHERE id = 999;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A banking ledger transfers $50 from Account 1 to Account 2.

### Bug Report
Debit executes, but credit fails due to an invalid account ID. Because the statements are not wrapped in a transaction, Account 1 loses $50 permanently while Account 2 receives nothing!

### Steps to Reproduce
1. Execute debit without BEGIN TRANSACTION / ROLLBACK.
2. Receiver update fails.
3. Total bank ledger is out of balance.

### Expected Behavior
Wrap statements in a database transaction with consistency checks.

### Actual Behavior
Unmanaged auto-commit executes partial state modifications.

### Impact
Financial ledger audit failure and lost customer money.

### Requirements
- Execute atomic update using conditional verification to ensure ledger balance.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Balances reflect successful atomic transfer**

---

### Challenge 78: [SQL-H03] A Multi-Table JOIN Multiplies Aggregates Across Independent Relationships

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Joins`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Cartesian Product`, `Multi-Table Joins`, `CTEs`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN tickets t`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer summary report calculates both total order spending AND total support tickets opened for each customer.

### Bug Report
Customer with 2 orders and 3 support tickets produces 2 x 3 = 6 joined rows. Order total is multiplied by 3, and support tickets count is multiplied by 2!

### Steps to Reproduce
1. Customer has orders totaling $150 (2 orders) and 3 tickets.
2. Query joins `customers` to `orders` AND to `tickets`.
3. Output reports revenue = $450 and tickets = 6.

### Expected Behavior
Aggregate `orders` and `tickets` independently in separate subqueries/CTEs before joining to `customers`.

### Actual Behavior
Joins multiple independent 1-to-many child tables in a single query.

### Impact
Customer lifetime value and support costs wildly inflated.

### Requirements
- Pre-aggregate `orders` by `customer_id` and `tickets` by `customer_id` in CTEs, then join to `customers`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Independent aggregation reports total_spent=150, tickets=3**

---

### Challenge 79: [SQL-H04] A Transaction Failure Leaves Related Financial Records Inconsistent

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Transactions`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Audit Trail`, `Transactions`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `UPDATE invoices SET status = 'paid' WHERE id = 1;
SELECT i.status`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An invoice closing script marks invoices as `'paid'` and creates matching audit records.

### Bug Report
An invoice is marked paid, but the corresponding audit journal row was missing, failing SOX compliance audits.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice audit logging statement is omitted or failing.

### Expected Behavior
Insert matching entry in `audit_journal` verifying invoice payment.

### Actual Behavior
Invoice status updated without journal ledger entry.

### Impact
SOX compliance violation leading to audit fines.

### Requirements
- Update invoice to `'paid'` and insert corresponding row into `audit_journal`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Both invoice updated and audit journal written**

---

### Challenge 80: [SQL-H05] A Database Migration Incorrectly Handles Existing NULL and Duplicate Values

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Schema`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Migrations`, `NULL Backfill`
- **Skills Tested**: `SQL`, `Database`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A schema migration prepares to add a `NOT NULL` constraint and default value to a `user_settings.notification_email` column.

### Bug Report
Running `ALTER TABLE` crashes or produces corrupted profiles because existing rows contain `NULL` values!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe NULL values must be backfilled before adding constraints.

### Expected Behavior
Backfill existing `NULL` emails with `'no-reply@domain.com'` (or account fallback email).

### Actual Behavior
Leaves NULL values unmigrated.

### Impact
Failed database migrations during deployment causing production downtime.

### Requirements
- Update existing records with missing notification emails to a default fallback address prior to applying constraints.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Backfills NULL notification emails**

---

### Challenge 81: [SQL-H06] A Running-Total Query Produces Incorrect Results for Tied Timestamps

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Window Functions`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Window Functions`, `Running Total`, `ROWS vs RANGE`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SUM(amount) OVER (ORDER BY trans_time) AS running_balance`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A financial ledger calculates account running balance after each transaction.

### Bug Report
When two transactions occur at the identical second (`2026-10-19 12:00:00`), the running total jumps ahead and shows the cumulative sum of BOTH transactions on the first row!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `SUM(amount) OVER (ORDER BY trans_time)`.
3. Default window frame for tied values groups peers together (`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`).

### Expected Behavior
Include `id` in `ORDER BY` OR specify `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` to process transactions strictly row by row.

### Actual Behavior
Tied timestamps cause peer grouping jump.

### Impact
Ledger audit mismatch during concurrent transactions.

### Requirements
- Use `ORDER BY trans_time, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Strict row-by-row running balance (100.00 then 150.00)**

---

### Challenge 82: [SQL-H07] A Reporting Query Uses Incorrect Isolation Assumptions During Concurrent Updates

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Transactions`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Isolation`, `Data Integrity`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT SUM(amount) AS total_sales FROM orders;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
An analytics query reports confirmed orders.

### Bug Report
The report includes half-completed cart checkout drafts that are in status `'draft'`, skewing daily performance metrics.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice missing status filter allows non-committed drafts into reporting tables.

### Expected Behavior
Filter strictly for confirmed, committed orders: `WHERE status = 'confirmed'`.

### Actual Behavior
Reads unconfirmed cart rows.

### Impact
Reports include abandoned carts as confirmed sales.

### Requirements
- Filter sales revenue calculations to reflect only confirmed orders.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Only confirmed orders summed**

---

### Challenge 83: [SQL-H08] A Soft-Delete Implementation Leaks Logically Deleted Records

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Filtering`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Soft Deletes`, `Security`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `SELECT id, title FROM documents ORDER BY id;`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer portal allows users to soft-delete archived documents (`deleted_at IS NOT NULL`).

### Bug Report
Soft-deleted documents continue to appear in search queries and public document listings!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice query omits `WHERE deleted_at IS NULL`.
3. Deleted records are returned.

### Expected Behavior
Filter strictly for active, non-deleted records: `WHERE deleted_at IS NULL`.

### Actual Behavior
Omits soft-delete check.

### Impact
Privacy violation: users see documents that were deleted by other administrators.

### Requirements
- Exclude logically deleted records from active customer listings and order by id.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Only non-deleted documents returned**

---

### Challenge 84: [SQL-H09] A Recursive Hierarchy Query Mishandles Cycles

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `CTE`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Recursive CTE`, `Cycles`, `Safety`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id
)`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A category hierarchy explorer queries nested product taxonomy trees.

### Bug Report
An invalid database relationship created a circular reference (Category A is parent of Category B, which is parent of Category A). The query runs infinitely until the database crashes with `RecursionError`!

### Steps to Reproduce
1. Execute recursive query on table with circular reference.
2. Query runs infinitely without depth bound.

### Expected Behavior
Add a depth boundary `WHERE depth < 5` to safeguard against infinite loops in recursive CTEs.

### Actual Behavior
No depth limiter.

### Impact
Database hangs and connection pool exhaustion.

### Requirements
- Add `AND depth < 5` (or `level < 5`) in the recursive step.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Hierarchy traversed safely with depth limit**

---

### Challenge 85: [SQL-H10] An Analytics Query Becomes Extremely Slow Because of Incorrect Query Structure and Indexing Assumptions

- **Arena Domain**: SQL Lab
- **Difficulty**: `Hard` | **Technology**: `SQL` | **Category**: `Performance`
- **Points**: `250 XP` | **Time Estimate**: `25 mins`
- **Topics**: `SQL`, `Query Optimization`, `EXISTS vs IN`, `Performance`
- **Skills Tested**: `SQL`, `Database`
- **Bug Signature**: `WHERE c.id IN (SELECT o.customer_id FROM orders o)`
- **Suspected Component**: `query.sql`

**Scenario & Defect Overview:**
### Company Scenario
A customer metrics query finds all customers who have placed an order in the last 30 days.

### Bug Report
The query uses `IN (SELECT customer_id FROM orders)` on millions of rows, causing a full table scan and locking the database.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice un-indexed `IN (SELECT ...)` subquery.

### Expected Behavior
Use `EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` or an indexed `INNER JOIN`.

### Actual Behavior
Slow correlated `IN` subquery.

### Impact
Query timeouts across executive reporting portals.

### Requirements
- Optimize the query using a semi-join or existence check rather than an unindexed full table join.

**Files in Sandbox:**
- `schema.sql`
- `query.sql`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Efficient EXISTS returns Alice and Bob**

---

## 4. Arena 3: Frontend Studio (React, DOM & State Management)

Covering Challenges **86 through 120**. These challenges test interactive UI engineering, React lifecycle and hook patterns, state mutability pitfalls, asynchronous event races, DOM accessibility, forms, and responsive CSS debugging.

### Challenge 86: [FE-E01] A Form Submits Even When Required Fields Are Empty

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `Forms`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Forms`, `Validation`
- **Skills Tested**: `React`, `Frontend`
- **Suspected Component**: `RegistrationForm.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A SaaS onboarding registration form collects user name and organization.

### Bug Report
When a user clicks "Submit" without filling in their name, the form dispatches an API request with an empty payload, causing backend 400 Bad Request errors.

### Steps to Reproduce
1. Load `RegistrationForm.jsx`.
2. Leave `name` empty and click Submit.
3. Form dispatches `onSubmit` event without validating.

### Expected Behavior
`handleSubmit` must verify `name.trim().length > 0`. If empty, prevent submission and set `error = "Name is required"`.

### Actual Behavior
Submits unconditionally without validation.

### Impact
Server logs flooded with 400 bad request errors from incomplete registrations.

### Requirements
- Check `if (!name.trim()) { setError("Name is required"); return; }` before dispatching `onSubmit`.

**Files in Sandbox:**
- `RegistrationForm.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Validates empty name before submission**

---

### Challenge 87: [FE-E02] A React Component Displays Stale or Incorrect Conditional Content

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `Conditional Rendering`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Conditional Rendering`, `JSX`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `{stock && <span className="in-stock">`
- **Suspected Component**: `Banner.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An e-commerce banner component notifies users when an item is in stock vs sold out.

### Bug Report
When `item.stock` is `0`, the component displays `"0"` on screen instead of the `"Sold Out"` badge because of how JavaScript evaluates `0 && <Component />`!

### Steps to Reproduce
1. Pass `stock = 0` to `Banner.jsx`.
2. Notice React renders raw text number `0` on screen.

### Expected Behavior
Render `<span className="badge-soldout">Sold Out</span>` when stock is 0, or boolean ternary `stock > 0 ? ... : ...`.

### Actual Behavior
`stock && <span>In Stock</span>` evaluates to `0` and renders literal "0".

### Impact
Broken visual layout with raw digits rendered in place of status badges.

### Requirements
- Use explicit boolean condition `stock > 0 ? ... : ...` or `Boolean(stock) && ...`.

**Files in Sandbox:**
- `Banner.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses explicit numeric comparison stock > 0**

---

### Challenge 88: [FE-E03] A Product Card Shows the Wrong Price After a State Update

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `React State`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `State`, `Derived State`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `setTotalPrice(price * quantity);`
- **Suspected Component**: `ProductCard.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A product card displays unit price and calculates total price when the quantity selector increments.

### Bug Report
User clicks `+` to increase quantity from 1 to 2. The total price continues to display the price for 1 item!

### Steps to Reproduce
1. Load `ProductCard.jsx`.
2. Click "+" button.
3. Total price lags by 1 step because state is read synchronously right after `setQuantity`.

### Expected Behavior
Derive `totalPrice = price * quantity` during render rather than storing redundant stale derived state.

### Actual Behavior
Maintains duplicate state variable `totalPrice` that reads previous `quantity` value.

### Impact
Customers see outdated price totals during cart selection.

### Requirements
- Compute total price directly from current props and state during render to prevent stale derived state.

**Files in Sandbox:**
- `ProductCard.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Total price derived cleanly from quantity**

---

### Challenge 89: [FE-E04] A Button Fires the Wrong Event Handler

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `DOM & Events`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Events`, `Event Handlers`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `<button onClick={onDelete} className="bg-emerald-600`
- **Suspected Component**: `ActionButton.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A task management toolbar contains "Save" and "Delete" buttons.

### Bug Report
When a user clicks "Save Draft", the task is permanently deleted!

### Steps to Reproduce
1. Click the "Save" button in `ActionButton.jsx`.
2. Notice `onClick={onDelete}` is bound to the save button instead of `onClick={onSave}`.

### Expected Behavior
Save button triggers `onSave`; Delete button triggers `onDelete`.

### Actual Behavior
Save button is wired to `onDelete`.

### Impact
Catastrophic accidental data loss when users intend to save their work.

### Requirements
- Connect `onClick={onSave}` to the Save button.

**Files in Sandbox:**
- `ActionButton.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Save button triggers onSave**

---

### Challenge 90: [FE-E05] A Search Field Ignores Uppercase/Lowercase Normalization

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `Validation`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Search`, `Normalization`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `item.name.includes(query)`
- **Suspected Component**: `SearchBar.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An internal employee directory provides live text filtering by employee name.

### Bug Report
Typing `"ALICE"` or `"alice"` fails to match employee `"Alice Smith"` due to strict case-sensitive matching.

### Steps to Reproduce
1. Type `"alice"` in search bar.
2. Filter uses `item.name.includes(query)`.
3. Zero results returned.

### Expected Behavior
Search should be case-insensitive: compare `.toLowerCase()`.

### Actual Behavior
Case-sensitive substring check.

### Impact
Users fail to find valid contacts in company directory.

### Requirements
- Apply `.toLowerCase()` to both `item.name` and `query`.

**Files in Sandbox:**
- `SearchBar.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Case-insensitive search using toLowerCase**

---

### Challenge 91: [FE-E06] A Loading Indicator Never Disappears After an API Error

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `React State`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Async`, `Loading States`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `setError(err.message);
      });`
- **Suspected Component**: `DataViewer.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A metrics dashboard fetches telemetry data on mount.

### Bug Report
When the server returns an HTTP 500 error, the spinner keeps spinning endlessly and the error message never displays.

### Steps to Reproduce
1. Fetch API fails.
2. Catch block sets `setError(err.message)`, but forgets `setLoading(false)`.
3. Spinner remains visible forever.

### Expected Behavior
`setLoading(false)` must be executed in both success and error cases (or in `finally`).

### Actual Behavior
`loading` remains `true` on error.

### Impact
Users stare at an endless loading screen and assume their connection is frozen.

### Requirements
- Add `setLoading(false)` to the error catch block or use `try/finally`.

**Files in Sandbox:**
- `DataViewer.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Loading set to false on catch**

---

### Challenge 92: [FE-E07] A Responsive Layout Overflows on Mobile

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `CSS` | **Category**: `CSS & Styling`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `CSS`, `Responsive Design`, `Mobile`
- **Skills Tested**: `CSS`, `Frontend`
- **Bug Signature**: `product-card {
    width: 600px;`
- **Suspected Component**: `ResponsiveCard.css`

**Scenario & Defect Overview:**
### Company Scenario
A product detail card contains title, description, and pricing for mobile and desktop screens.

### Bug Report
On mobile devices (screen width 375px), the card overflows horizontally, causing horizontal scrollbars and breaking page layout.

### Steps to Reproduce
1. Open layout on 375px screen width.
2. Observe `width: 600px;` forces horizontal overflow.

### Expected Behavior
Use fluid responsive sizing: `max-width: 600px; width: 100%; box-sizing: border-box;`.

### Actual Behavior
Hardcoded fixed `width: 600px;`.

### Impact
Broken mobile responsiveness and poor Google mobile search ranking.

### Requirements
- Ensure the container adapts fluidly across mobile and desktop viewport sizes using responsive width constraints.

**Files in Sandbox:**
- `ResponsiveCard.css`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses max-width for responsive scaling**

---

### Challenge 93: [FE-E08] A Form Displays an Incorrect Validation Message

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `Validation`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Forms`, `Validation Messages`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `setError('Password must be at least 8 characters');`
- **Suspected Component**: `EmailInput.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A customer newsletter subscription widget validates email syntax.

### Bug Report
When user enters an invalid email missing `@`, the error displays `"Password must be at least 8 characters"`!

### Steps to Reproduce
1. Type `"invalidemail"` into newsletter input.
2. Observe copy-paste error in validation message.

### Expected Behavior
Display `"Please enter a valid email address."`.

### Actual Behavior
Displays copy-paste password error message.

### Impact
Confused users cannot figure out why their email is being rejected.

### Requirements
- Update error text to `"Please enter a valid email address."`.

**Files in Sandbox:**
- `EmailInput.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Displays valid email error message**

---

### Challenge 94: [FE-E09] A Modal Cannot Be Closed Using the Escape Key

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `Accessibility`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Accessibility`, `Keyboard Events`, `WCAG`
- **Skills Tested**: `React`, `Frontend`, `Accessibility`
- **Suspected Component**: `Modal.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An accessible modal dialog component displays order confirmations.

### Bug Report
Keyboard users and screen readers cannot close the modal by pressing the Escape key, violating WCAG accessibility guidelines.

### Steps to Reproduce
1. Open modal dialog.
2. Press "Escape" key.
3. Modal remains open because keydown listener is missing or checks wrong key.

### Expected Behavior
Pressing Escape (`e.key === "Escape"`) invokes `onClose()`.

### Actual Behavior
No Escape key listener attached to document.

### Impact
Accessibility compliance violation (WCAG 2.1 Level AA) for keyboard-only navigation.

### Requirements
- Add `useEffect` listening for `keydown` where `e.key === 'Escape'` triggers `onClose()`.

**Files in Sandbox:**
- `Modal.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Attaches Escape key listener in useEffect**

---

### Challenge 95: [FE-E10] A List Uses an Unstable or Incorrect React Key, Causing UI Inconsistencies

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Easy` | **Technology**: `React` | **Category**: `DOM & Events`
- **Points**: `100 XP` | **Time Estimate**: `10 mins`
- **Topics**: `React`, `Keys`, `Reconciliation`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `<li key={index}`
- **Suspected Component**: `UserList.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A user list allows administrators to reorder and delete team members.

### Bug Report
When an admin deletes the first user in the list, input values and checkbox states from the deleted row jump onto the next row!

### Steps to Reproduce
1. Check checkbox on item 0.
2. Delete item 0.
3. Item 1 now has its checkbox checked because array index `index` was used as key!

### Expected Behavior
Use stable unique entity ID `key={user.id}`.

### Actual Behavior
Uses array index: `key={index}`.

### Impact
State corruption in form inputs and reordered lists.

### Requirements
- Change `key={index}` to `key={user.id}`.

**Files in Sandbox:**
- `UserList.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses stable user.id as key**

---

### Challenge 96: [FE-M01] Rapid Search Requests Overwrite Newer Results

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Asynchronous UI`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Async`, `Race Conditions`, `useEffect`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `fetchResults(query).then(data => {
      setResults(data);`
- **Suspected Component**: `LiveSearch.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An enterprise documentation portal provides a live typeahead search across thousands of API endpoints.

### Bug Report
When typing quickly (e.g. searching for "users" by typing "u", "us", "use", "user", "users"), the query for "us" took 350ms while "users" took 80ms. The earlier slow response arrived last and overwrote the results, leaving stale results for "us" visible on the screen even though the input displays "users".

### Steps to Reproduce
1. Open `LiveSearch.jsx`.
2. Type query rapidly into the search field.
3. Observe race condition where network latency differences cause out-of-order state updates.

### Expected Behavior
The search component must ignore responses from stale queries or abort previous in-flight requests using an `active` flag or `AbortController`.

### Actual Behavior
Component unconditionally calls `setResults(data)` in the `.then()` callback regardless of whether the query is still the latest one.

### Impact
Users see irrelevant search results that do not match the text in the search input, causing confusion and incorrect navigation.

### Requirements
- Implement a request cancellation flag or controller to ignore responses from stale or superseded search requests.
- Only update state if the request is still current.

**Files in Sandbox:**
- `LiveSearch.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses cancellation flag or AbortController to prevent race conditions**

---

### Challenge 97: [FE-M02] React State Updates Lose Changes During Batched Operations

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `State Management`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `State`, `Batching`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `setCount(count + 1);
    setCount(count + 1);
    setCount(count + 1);`
- **Suspected Component**: `CounterBatch.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An inventory ticketing application allows warehouse workers to quickly increment box counts by +3 using a shortcut button.

### Bug Report
Clicking "+3" only increments the box count by 1 instead of 3.

### Steps to Reproduce
1. In `CounterBatch.jsx`, click the "+3" button.
2. The button calls `incrementByThree()`, which invokes `setCount(count + 1)` three times in a row.
3. Box count changes from 0 to 1 instead of 0 to 3.

### Expected Behavior
Each sequential update must incorporate the latest queued state transition so the counter increments by the full expected amount.

### Actual Behavior
All three `setCount(count + 1)` calls read the same snapshot value of `count` from the current render closure.

### Impact
Warehouse staff submit incorrect inventory counts, leading to stock discrepancies.

### Requirements
- Use functional state updates to ensure all increments are applied correctly during batched state transitions.

**Files in Sandbox:**
- `CounterBatch.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses functional state updater prev => prev + 1**

---

### Challenge 98: [FE-M03] useEffect Dependency Causes Stale Values or Missing Updates

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `React Hooks`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Hooks`, `useEffect`, `Dependencies`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `}, []);`
- **Suspected Component**: `UserProfileLoader.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A customer support portal displays user details in a sidebar drawer. As support agents click different ticket owners, `userId` changes.

### Bug Report
When an agent clicks between User A and User B, the drawer continues to show User A's details because the effect dependency array is empty `[]`.

### Steps to Reproduce
1. Mount `UserProfileLoader.jsx` with `userId = "usr_101"`. Profile loads.
2. Parent changes prop to `userId = "usr_202"`.
3. Profile does not reload and keeps showing data for `usr_101`.

### Expected Behavior
Effect must re-run whenever `userId` changes by declaring `userId` in the dependency array: `[userId, fetchUser]`.

### Actual Behavior
Dependency array is `[]`, closing over initial `userId` and never refetching.

### Impact
Agents take actions on wrong customer accounts due to stale profile displays.

### Requirements
- Add `userId` (and `fetchUser`) to the `useEffect` dependency array.

**Files in Sandbox:**
- `UserProfileLoader.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Declares userId in dependency array**

---

### Challenge 99: [FE-M04] Shopping Cart Calculates Totals Incorrectly After Mutation

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `State Immutability`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Immutability`, `State`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `items[index].qty = newQty;
      setItems(items);`
- **Suspected Component**: `ShoppingCart.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An online grocery checkout component allows customers to update item quantities.

### Bug Report
Modifying item quantity directly mutates the state array object `items[index].qty = newQty`. React fails to trigger re-renders reliably because the array reference remains identical, and cart total calculation falls out of sync.

### Steps to Reproduce
1. In `ShoppingCart.jsx`, call `updateQuantity(itemId, 5)`.
2. The code mutates the existing item in place: `items[index].qty = newQty; setItems(items);`.
3. Component doesn't re-render or produces stale totals.

### Expected Behavior
State must be updated immutably using `.map()` to return a new array with newly created item objects.

### Actual Behavior
Mutates item in place and passes identical array reference to `setItems`.

### Impact
Shoppers see incorrect order totals and get charged mismatched amounts.

### Requirements
- Use immutable state update: `setItems(items.map(item => item.id === id ? { ...item, qty: newQty } : item));`.

**Files in Sandbox:**
- `ShoppingCart.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Immutably maps items using object spread**

---

### Challenge 100: [FE-M05] Paginated List Does Not Reset Page When Filter Changes

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Pagination`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Pagination`, `Filtering`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `const handleFilterChange = (newCategory) => {
    setCategory(newCategory);
  };`
- **Suspected Component**: `FilterPagination.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An admin product catalog provides category filtering and pagination.

### Bug Report
An admin navigates to Page 6 of "All Products". They then filter by "Furniture", which only has 2 pages of results. The view displays "No products found" because the table stayed on `page = 6`, which is out of range for the filtered results!

### Steps to Reproduce
1. In `FilterPagination.jsx`, navigate to page 5.
2. Select a different category from the dropdown.
3. The catalog displays an empty state because `page` remained 5 instead of resetting to 1.

### Expected Behavior
Changing `category` must reset `page` back to 1.

### Actual Behavior
`handleFilterChange` updates category without touching `page`.

### Impact
Users believe products are missing or deleted when changing search filters.

### Requirements
- Call `setPage(1)` whenever the filter changes.

**Files in Sandbox:**
- `FilterPagination.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Resets page to 1 on filter change**

---

### Challenge 101: [FE-M06] Event Listener Registered Repeatedly Without Cleanup

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Memory Leaks`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `useEffect`, `Cleanup`, `DOM Events`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `window.addEventListener('resize', handleResize);
    // BUG: Missing cleanup function to removeEventListener
  }, []);`
- **Suspected Component**: `ResizeListener.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A charting widget listens for browser window resize events to recalculate SVG canvas dimensions.

### Bug Report
Every time the user navigates between dashboard tabs, browser memory consumption increases steadily. Profiling reveals that thousands of `resize` listeners remain attached to `window`, leading to sluggish responsiveness.

### Steps to Reproduce
1. Inspect `ResizeListener.jsx`.
2. Notice `window.addEventListener('resize', handleResize)` is registered in `useEffect`.
3. No cleanup function is returned.

### Expected Behavior
`useEffect` must return a cleanup function: `return () => window.removeEventListener('resize', handleResize);`.

### Actual Behavior
Omits cleanup, leaking event listeners on every unmount and re-mount.

### Impact
Severe memory leak causing browser tab crashes on long-lived sessions.

### Requirements
- Return `() => window.removeEventListener('resize', handleResize)` from `useEffect`.

**Files in Sandbox:**
- `ResizeListener.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Cleans up event listener with removeEventListener**

---

### Challenge 102: [FE-M07] Authentication Refresh Request Creates Redirect Loops

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Authentication`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Authentication`, `Routing`, `Loading States`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `export default function ProtectedRoute({ user, isLoading, children }) {
  if (!user) {`
- **Suspected Component**: `ProtectedRoute.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A cloud dashboard implements route guarding to protect user settings and billing.

### Bug Report
When an authenticated user refreshes `/settings`, the page flickers and immediately redirects to `/login`. Upon arriving at `/login`, the auth provider finishes hydrating and redirects them back to `/settings`, causing an infinite redirect loop.

### Steps to Reproduce
1. In `ProtectedRoute.jsx`, observe the auth check.
2. When the app first boots, `isLoading` is `true` while the session token is validated, but `user` is initially `null`.
3. `ProtectedRoute` immediately executes `if (!user) return <Navigate to="/login" />` before checking `isLoading`.

### Expected Behavior
If `isLoading` is true, render a loading spinner `<LoadingSpinner />` and wait until authentication state resolves before redirecting.

### Actual Behavior
Treats unhydrated state (`user === null` while `isLoading === true`) as unauthenticated and redirects immediately.

### Impact
Authenticated users cannot reload or deep-link to protected pages without getting kicked out.

### Requirements
- Add `if (isLoading) return <LoadingSpinner />;` before checking `if (!user)`.

**Files in Sandbox:**
- `ProtectedRoute.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Checks isLoading before redirecting**

---

### Challenge 103: [FE-M08] File-Upload Component Mishandles Progress and Failed Requests

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Error Handling`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Async`, `Error Handling`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `} catch (err) {
      console.error('Upload failed', err);
    }`
- **Suspected Component**: `FileUploader.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A customer portal allows users to upload PDF receipts for reimbursement.

### Bug Report
If an upload fails (e.g. 500 server error or dropped connection), the UI remains stuck showing "Uploading 65%..." and the upload button stays disabled forever. The user is unable to retry without refreshing the entire page.

### Steps to Reproduce
1. In `FileUploader.jsx`, simulate an upload failure.
2. The `try/catch` catches the error, but only calls `console.error`.
3. `isUploading` remains `true` and `error` state is never populated.

### Expected Behavior
Inside the `catch` block, set `setIsUploading(false)` and `setError(err.message || 'Upload failed')`.

### Actual Behavior
Leaves `isUploading: true` and does not set user-facing error message.

### Impact
Users assume their documents are still uploading and abandon their expense submissions.

### Requirements
- Update `catch` block to set `setIsUploading(false)` and set `setError(...)`.

**Files in Sandbox:**
- `FileUploader.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Resets isUploading and sets error state on failure**

---

### Challenge 104: [FE-M09] Multi-Step Form Loses User Values When Navigating Backward

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Form Architecture`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Lifting State`, `Forms`, `Multi-step`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `export function Step1({ formData = {}, onChange }) {
  const [name, setName] = useState('');`
- **Suspected Component**: `WizardForm.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An insurance quote onboarding flow consists of Step 1 (Personal Info) and Step 2 (Vehicle Details).

### Bug Report
A user fills out Step 1, proceeds to Step 2, and then clicks "Back" to fix a typo in their name. When Step 1 re-mounts, all previously entered fields are blank!

### Steps to Reproduce
1. In `WizardForm.jsx`, notice that `Step1` maintains local `useState` for `fullName` and `email` instead of lifting state to parent.
2. Moving to Step 2 unmounts `Step1`, destroying its local state.
3. Returning to Step 1 re-mounts with empty initial strings.

### Expected Behavior
Form data must be lifted up to parent `WizardForm` and passed down as props (`formData` and `onChange`) to persist between step transitions.

### Actual Behavior
Child step component owns its own state, discarding it upon unmount.

### Impact
High checkout abandonment rates due to users having to re-type form inputs.

### Requirements
- Lift state to `WizardForm` and pass `formData.fullName` and `formData.email` into `Step1`.

**Files in Sandbox:**
- `WizardForm.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Step1 initializes with formData.name**

---

### Challenge 105: [FE-M10] Dashboard Renders Inconsistent Data After Parallel API Calls

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Asynchronous Data`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Async`, `Promise.allSettled`, `Resilience`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `Promise.all([fetchRevenue(), fetchHealth()])`
- **Suspected Component**: `MetricsDashboard.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An executive analytics dashboard fetches Revenue Metrics and Server Health in parallel.

### Bug Report
If the Server Health endpoint encounters a minor 503 outage, `Promise.all` fails immediately, causing the entire dashboard to crash and display an error screen—even though the critical Revenue Metrics were returned successfully!

### Steps to Reproduce
1. In `MetricsDashboard.jsx`, observe `Promise.all([fetchRevenue(), fetchHealth()])`.
2. Rejecting `fetchHealth()` causes the entire try block to fail.
3. No revenue numbers are shown to the executive.

### Expected Behavior
Use `Promise.allSettled` or individual try/catch blocks so successful metrics are displayed with an isolated fallback banner for the degraded service.

### Actual Behavior
All-or-nothing `Promise.all` fails completely on single endpoint errors.

### Impact
Total service interruption on dashboard when non-critical endpoints fail.

### Requirements
- Use `Promise.allSettled` to independently evaluate each endpoint result.

**Files in Sandbox:**
- `MetricsDashboard.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses Promise.allSettled for resilient data fetching**

---

### Challenge 106: [FE-M11] Frontend Cache Displays Outdated Profile Information

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Caching`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Caching`, `Cache Invalidation`
- **Skills Tested**: `React`, `Frontend`
- **Suspected Component**: `ProfileCache.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A social networking platform caches user profile payloads in an in-memory map to reduce redundant API roundtrips.

### Bug Report
When a user updates their profile name and clicks "Save", the update API returns 200 OK. However, navigating back to their profile view still displays their old name until the page is hard refreshed.

### Steps to Reproduce
1. In `ProfileCache.jsx`, save an updated name via `handleUpdateName`.
2. Notice the code calls `api.updateName(newName)`, but never invalidates or updates the `cache` entry for `userId`.
3. Subsequent reads from `cache.get(userId)` return the old profile object.

### Expected Behavior
After a successful update, the cache entry must be invalidated or updated with the new profile data.

### Actual Behavior
The cache is not mutated or cleared, leading to stale reads.

### Impact
Users repeatedly submit duplicate update requests thinking their changes were lost.

### Requirements
- Update `cache.set(userId, updated)` or delete `cache.delete(userId)` after saving.

**Files in Sandbox:**
- `ProfileCache.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Updates or deletes the cache entry on save**

---

### Challenge 107: [FE-M12] Component Submits Duplicate Requests After Repeated Clicks

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Form Submission`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Forms`, `Debounce`, `Double Submission`
- **Skills Tested**: `React`, `Frontend`
- **Suspected Component**: `SubmitButton.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A food delivery app features an "Order Now" checkout button.

### Bug Report
Impatient users double-click the "Place Order" button. The server receives two parallel order requests and charges the customer twice for the same meal!

### Steps to Reproduce
1. In `SubmitButton.jsx`, observe the `handleSubmit` click handler.
2. The button lacks a `disabled` attribute tied to `isSubmitting`, and `handleSubmit` does not check if a submission is already pending.

### Expected Behavior
The button must be disabled when `isSubmitting` is true (`disabled={isSubmitting}`), and `handleSubmit` must guard against re-entry.

### Actual Behavior
Button stays clickable during the async network request.

### Impact
Duplicate financial transactions and customer chargeback disputes.

### Requirements
- Set `disabled={isSubmitting}` on `<button>`.
- Check `if (isSubmitting) return;` at the start of `handleSubmit`.

**Files in Sandbox:**
- `SubmitButton.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Disables button when isSubmitting is true**

---

### Challenge 108: [FE-M13] Date Picker Displays Incorrect Date Due to Timezone Offset

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Date & Time`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Dates`, `Timezones`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `const d = new Date(dateString);
    const formatted = d.toISOString().split('T')[0];
    setSelectedDate(formatted);`
- **Suspected Component**: `DatePicker.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A hotel booking system displays selected check-in and check-out dates.

### Bug Report
Users in the Americas (e.g. UTC-5, UTC-8) select "October 15, 2026" on the calendar. After selecting, the confirmation text shows "October 14, 2026"—one day behind!

### Steps to Reproduce
1. In `DatePicker.jsx`, `new Date("2026-10-15")` parses the string at midnight UTC.
2. In America/New_York (UTC-4), midnight UTC corresponds to 8:00 PM on October 14.
3. Calling `date.getDate()` or `toISOString()` renders October 14 instead of October 15.

### Expected Behavior
Format dates using local components or parse without midnight UTC shifting (e.g. `dateString.split('-')` or `new Date(year, month - 1, day)`).

### Actual Behavior
Converts through `new Date(isoDateString).toISOString().split('T')[0]`, shifting timezone by negative UTC offset.

### Impact
Guests book rooms for the wrong night, causing booking errors and lost revenue.

### Requirements
- Parse date inputs using local calendar date parts to avoid unexpected timezone shifts.

**Files in Sandbox:**
- `DatePicker.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Retains raw dateString without UTC shifting**

---

### Challenge 109: [FE-M14] Form Does Not Preserve Field-Level Server Validation Errors

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Form Validation`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Forms`, `Validation`, `Error Handling`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `} catch (err) {
      setGeneralError('Submission failed');
    }`
- **Suspected Component**: `ServerErrorForm.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A SaaS account creation form validates workspace subdomain and company tax ID on the backend.

### Bug Report
When submitting with a taken subdomain, the backend returns HTTP 422: `{ errors: { subdomain: "Subdomain already in use" } }`. The frontend replaces the entire form with a generic message `"An error occurred"` rather than highlighting the `subdomain` field with its specific server error message.

### Steps to Reproduce
1. In `ServerErrorForm.jsx`, simulate a 422 response with `err.response.data.errors`.
2. Notice `catch (err)` discards `err.response.data.errors` and sets a single string error.
3. No field-specific error messages are rendered next to the offending input.

### Expected Behavior
Catch block must inspect `err.response?.data?.errors` and store them in `fieldErrors` state (`setFieldErrors(err.response.data.errors)`).

### Actual Behavior
Wipes out detailed field-level error messages in favor of a vague banner.

### Impact
Users cannot tell which field was invalid or how to fix it, abandoning signup.

### Requirements
- Set `setFieldErrors(err.response?.data?.errors || {})` inside the catch handler.

**Files in Sandbox:**
- `ServerErrorForm.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Populates fieldErrors from server error response**

---

### Challenge 110: [FE-M15] Accessible Dropdown Fails to Close on Escape Key

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Medium` | **Technology**: `React` | **Category**: `Accessibility`
- **Points**: `200 XP` | **Time Estimate**: `15 mins`
- **Topics**: `React`, `Accessibility`, `WCAG`, `Keyboard Events`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {`
- **Suspected Component**: `AccessibleDropdown.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An enterprise banking application requires compliance with WCAG 2.1 AA accessibility guidelines.

### Bug Report
When a blind or motor-impaired user opens a custom dropdown menu using keyboard navigation, pressing the "Escape" key does not close the dropdown menu, trapping focus and violating accessibility standards.

### Steps to Reproduce
1. In `AccessibleDropdown.jsx`, open the dropdown.
2. Press the Escape key.
3. The dropdown remains open because `handleKeyDown` ignores `e.key === 'Escape'`.

### Expected Behavior
When `e.key === 'Escape'` is pressed, `setIsOpen(false)` must be called to dismiss the dropdown.

### Actual Behavior
`handleKeyDown` ignores the Escape key.

### Impact
Fails WCAG 2.1 AA audit, blocking users who rely on assistive technologies.

### Requirements
- Add `if (e.key === 'Escape') setIsOpen(false);` in `handleKeyDown`.

**Files in Sandbox:**
- `AccessibleDropdown.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Closes dropdown when Escape key is pressed**

---

### Challenge 111: [FE-H01] Concurrent Frontend Requests Create Inconsistent Checkout State

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Concurrency`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Concurrency`, `State Machine`, `E-commerce`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `const handleCheckout = async () => {
    setStatus('processing');`
- **Suspected Component**: `CheckoutFlow.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A high-volume ticket sales portal allows users to purchase concert tickets.

### Bug Report
During flash sales, customers click "Checkout" while background cart inventory verification is still in flight. Because there is no atomic state lock or mutex, two concurrent checkout requests are dispatched with the same cart items, creating duplicate bookings and split billing charges.

### Steps to Reproduce
1. In `CheckoutFlow.jsx`, click Checkout.
2. Trigger a second checkout action before the first returns.
3. Both proceed because state transition is not locked atomically.

### Expected Behavior
A checkout mutex/lock (`isProcessing` state or ref) must prevent any subsequent checkout attempt until the current one finishes or fails.

### Actual Behavior
Component allows overlapping checkout invocations, creating duplicate transactions.

### Impact
Overbooking of allocated seats and severe financial reconciliation overhead.

### Requirements
- Implement an execution guard or atomic lock to block concurrent overlapping checkout requests.

**Files in Sandbox:**
- `CheckoutFlow.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Guards against concurrent checkout with processing lock**

---

### Challenge 112: [FE-H02] Memory Leak Develops After Repeated Mount/Unmount Cycles

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Memory Management`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Memory Leaks`, `useEffect Cleanup`, `Event Bus`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `eventBus.subscribe(symbol, handleTick);
  }, [symbol, eventBus]);`
- **Suspected Component**: `SubscriptionWidget.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A financial trading platform streams real-time cryptocurrency price updates into dashboard widgets.

### Bug Report
When users switch between different coin tabs, browser memory continuously increases until the tab crashes with an "Out of Memory" error. The React DevTools console also outputs warnings: `"Can't perform a React state update on an unmounted component"`.

### Steps to Reproduce
1. In `SubscriptionWidget.jsx`, `eventBus.subscribe(symbol, handleTick)` is called in `useEffect`.
2. When the user navigates away, the component unmounts.
3. No unsubscribe callback is registered. The event bus keeps a reference to `handleTick`, retaining the unmounted component in memory indefinitely.

### Expected Behavior
The `useEffect` hook must return a cleanup function: `return () => eventBus.unsubscribe(symbol, handleTick);`.

### Actual Behavior
Omits the unsubscribe call, creating a permanent memory leak and zombie callback listeners.

### Impact
Browser tab crashes on prolonged usage; multiple zombie listeners fire simultaneously.

### Requirements
- Return a cleanup function from `useEffect` invoking `eventBus.unsubscribe(symbol, handleTick)`.

**Files in Sandbox:**
- `SubscriptionWidget.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Cleans up subscription on unmount**

---

### Challenge 113: [FE-H03] Shared Client-Side Cache Exposes Data Between Sessions

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `JavaScript` | **Category**: `Security`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Security`, `Caching`, `Authentication`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `localStorage.removeItem('authToken');
    // BUG: Leaves sensitive records in sessionCache across user logout`
- **Suspected Component**: `SessionCache.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A hospital kiosk workstation allows doctors and nurses to access confidential patient health records.

### Bug Report
Nurse Sarah logs into the kiosk, reviews Patient X's records, and clicks "Log Out". When Doctor Robert logs in next on the same workstation, the app reads from the client-side session cache before network validation completes, displaying Patient X's confidential records under Doctor Robert's session!

### Steps to Reproduce
1. In `SessionCache.jsx`, inspect the `logoutUser` implementation.
2. `logoutUser` calls `authApi.logout()` and clears local tokens, but fails to invoke `sessionCache.clear()`.
3. Subsequent logins reuse cached records belonging to the prior user.

### Expected Behavior
`logoutUser` must purge the client-side `sessionCache` completely (`sessionCache.clear()`) to prevent data leakage across sessions.

### Actual Behavior
Cached data remains in memory across different user sessions.

### Impact
Critical HIPAA / privacy violation exposing patient medical data across user boundaries.

### Requirements
- Call `sessionCache.clear()` inside `logoutUser`.

**Files in Sandbox:**
- `SessionCache.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Clears sessionCache on logout**

---

### Challenge 114: [FE-H04] Optimistic UI Update Corrupts State After Failed Requests

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Optimistic UI`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Optimistic UI`, `State Snapshots`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `setLikes(likes + 1);
    setIsLiked(true);

    try {
      await api.likePost();
    } catch (err) {
      setLikes(likes - 1);`
- **Suspected Component**: `OptimisticFeed.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A social media platform uses optimistic UI updates to instantly toggle "Like" counts.

### Bug Report
A user clicks "Like" twice quickly under poor network conditions. The first request fails on the server. The rollback logic blindly subtracts 1 from the *current* count, but because the user had already clicked again, the like count drops below zero (`likes: -1`), permanently corrupting the counter.

### Steps to Reproduce
1. In `OptimisticFeed.jsx`, click like.
2. State is optimistically incremented: `setLikes(likes + 1)`.
3. Server returns an error. The catch block blindly calls `setLikes(likes - 1)` or decrements from stale closure, corrupting the counter.

### Expected Behavior
Capture a snapshot of the previous state before the optimistic mutation, and revert to that exact snapshot if the request fails.

### Actual Behavior
Reverts by subtracting from a stale or mutated counter value.

### Impact
Incorrect like counters and desynchronized like states across users.

### Requirements
- Snapshot previous state prior to optimistic updates and revert accurately to the snapshot if the network request fails.

**Files in Sandbox:**
- `OptimisticFeed.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Captures previousLikes snapshot and restores on error**

---

### Challenge 115: [FE-H05] Complex Dashboard Produces Inconsistent Derived State

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Performance & Memoization`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `useMemo`, `Derived State`, `Performance`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `return { totalMRR, avgMRR, count: filtered.length };
  }, []);`
- **Suspected Component**: `AnalyticsHub.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An executive KPI dashboard computes Monthly Recurring Revenue (MRR) and Average Revenue Per User (ARPU) based on transactions and active tier filter.

### Bug Report
When an executive switches the tier filter from "Enterprise" to "Starter", the transaction table updates, but the KPI Summary cards continue to display Enterprise MRR! Profiling shows `useMemo` closed over an empty dependency array `[]`.

### Steps to Reproduce
1. In `AnalyticsHub.jsx`, view the `mrr` computation.
2. `useMemo` is declared with `[]` instead of `[transactions, tierFilter]`.
3. Changing filters does not recalculate the summary metrics.

### Expected Behavior
`useMemo` must include `[transactions, tierFilter]` in its dependencies so derived metrics update when data or filters change.

### Actual Behavior
Derived metrics stay frozen on initial calculation due to missing dependencies.

### Impact
Executives make strategic pricing decisions based on incorrect and outdated metrics.

### Requirements
- Add `[transactions, tierFilter]` to the `useMemo` dependency array.

**Files in Sandbox:**
- `AnalyticsHub.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Includes transactions and tierFilter in useMemo dependencies**

---

### Challenge 116: [FE-H06] Concurrent API Calls Trigger Multiple Token Refreshes

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `JavaScript` | **Category**: `Authentication Architecture`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `JavaScript`, `Authentication`, `Token Refresh`, `Concurrency`
- **Skills Tested**: `JavaScript`, `Frontend Architecture`
- **Bug Signature**: `if (err.status === 401) {
      const newTokens = await refreshApi();`
- **Suspected Component**: `AuthManager.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A Single Page Application initiates multiple parallel API calls when loading the dashboard (user profile, notifications, metrics, and alerts).

### Bug Report
When the user's access token expires, all 4 concurrent requests return 401 Unauthorized simultaneously. Each response interceptor independently calls `refreshTokenApi()`. The backend implements refresh token rotation (one-time use per refresh token). The first refresh succeeds, but the subsequent 3 requests arrive with the now-invalidated old refresh token, causing the backend to flag a replay attack and terminate the user's session!

### Steps to Reproduce
1. In `AuthManager.jsx`, four concurrent requests fail with 401.
2. `refreshToken()` is executed 4 separate times instead of reusing a single in-flight refresh promise.
3. User gets abruptly logged out.

### Expected Behavior
Implement refresh token deduplication: if a refresh is already in flight, all subsequent 401 interceptors must await the same shared promise (`refreshPromise`).

### Actual Behavior
Fires uncoordinated parallel refresh requests.

### Impact
Users get randomly logged out whenever tokens expire during dashboard navigation.

### Requirements
- Share an in-flight token refresh promise across concurrent requests to avoid duplicate refresh calls.

**Files in Sandbox:**
- `AuthManager.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Shares single in-flight refreshPromise across calls**

---

### Challenge 117: [FE-H07] Virtualized List Renders Incorrect Items After Filtering

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Virtualization`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Virtualization`, `Keys`, `Reconciliation`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `key={startIndex + index}`
- **Suspected Component**: `VirtualList.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A server log monitoring tool uses a virtualized list to render 50,000 log lines with high performance.

### Bug Report
When filtering logs from "ALL" to "ERROR", log messages from other levels stay visible in the viewport or jump to wrong rows. Inspecting the DOM reveals the virtual list mapped array index `index` as the React `key`, confusing React's reconciliation engine.

### Steps to Reproduce
1. In `VirtualList.jsx`, inspect the rendered rows.
2. The virtual slice maps items using `key={startIndex + index}` instead of unique entity id `item.id`.
3. Filter or reorder items; DOM node recycling displays incorrect contents.

### Expected Behavior
Rows must be keyed by stable unique entity identifier: `key={item.id}`.

### Actual Behavior
Uses calculated row index as key.

### Impact
Engineers read wrong error timestamps and corrupted stack traces during production outages.

### Requirements
- Ensure virtualized list items use unique stable entity keys rather than computed window offsets.

**Files in Sandbox:**
- `VirtualList.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Uses stable item.id for virtualized row key**

---

### Challenge 118: [FE-H08] Multi-Step Checkout Loses Consistency on Partial Failure

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Compensating Transactions`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Compensating Transactions`, `Error Recovery`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `} catch (err) {
      setError(err.message || 'Payment failed');`
- **Suspected Component**: `MultiStepCheckout.jsx`

**Scenario & Defect Overview:**
### Company Scenario
An airline ticket booking engine executes two sequential transactions:
1. `reserveSeat(flightId, seatNumber)` - holds seat for 10 minutes.
2. `processPayment(paymentDetails)` - charges credit card.

### Bug Report
If the credit card fails (e.g. insufficient funds), the checkout displays an error, but never releases the held seat (`releaseSeat(reservationId)`). The seat remains locked for 10 minutes, preventing the passenger from retrying with another card and blocking other customers from booking that seat.

### Steps to Reproduce
1. In `MultiStepCheckout.jsx`, simulate payment failure after seat reservation succeeds.
2. In the catch block, error message is set, but no compensating rollback request is sent to release the reserved seat.

### Expected Behavior
If step 2 fails, invoke compensating rollback `await api.releaseSeat(reservation.id)` before showing the error.

### Actual Behavior
Leaves reserved inventory orphaned and locked in the backend.

### Impact
Lost flight bookings and stranded seat reservations.

### Requirements
- Call `await api.releaseSeat(reservation.id)` in the catch block if `reservation` exists.

**Files in Sandbox:**
- `MultiStepCheckout.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Releases reserved seat on payment failure**

---

### Challenge 119: [FE-H09] Real-Time Interface Applies Out-Of-Order Events

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Real-Time State`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `WebSockets`, `Sequence Numbers`, `Event Ordering`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `const handleIncomingMessage = (event) => {
      setContent(event.text);`
- **Suspected Component**: `RealtimeChat.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A collaborative live document editor receives character edit events over WebSockets from multiple peers.

### Bug Report
Under spotty cellular network connections, packets arrive out of sequence. An older event packet with `seq: 14` arrives after a newer packet with `seq: 15`. The editor blindly sets document content from the arriving payload, reverting recent changes and causing text to jump backwards.

### Steps to Reproduce
1. In `RealtimeChat.jsx`, notice `handleIncomingMessage(event)`.
2. Component receives `event = { seq: 15, text: "Hello World" }`, then later receives delayed `event = { seq: 14, text: "Hello" }`.
3. The editor renders "Hello", overwriting newer text.

### Expected Behavior
Maintain a sequence tracker (`lastSeqRef.current`). Ignore any incoming event where `event.seq <= lastSeqRef.current`.

### Actual Behavior
Applies all incoming events regardless of sequence numbers.

### Impact
Content loss and confusing cursor jumping during collaborative editing sessions.

### Requirements
- Track `lastSeqRef` and discard packets if `event.seq <= lastSeqRef.current`.

**Files in Sandbox:**
- `RealtimeChat.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Rejects out-of-order events using sequence comparison**

---

### Challenge 120: [FE-H10] Frontend Fails to Gracefully Handle 403 Forbidden Responses

- **Arena Domain**: Frontend Studio
- **Difficulty**: `Hard` | **Technology**: `React` | **Category**: `Security & Error Handling`
- **Points**: `300 XP` | **Time Estimate**: `20 mins`
- **Topics**: `React`, `Security`, `Error Boundaries`, `HTTP 403`
- **Skills Tested**: `React`, `Frontend`
- **Bug Signature**: `const handleDelete = async () => {
    setIsDeleting(true);
    setErrorMessage('');
    await api.deleteAccount(user.id);
    setIsDeleting(false);
  };`
- **Suspected Component**: `AdminPanel.jsx`

**Scenario & Defect Overview:**
### Company Scenario
A multi-tenant enterprise administration dashboard manages user permissions.

### Bug Report
If an organization's billing plan expires or an admin's session permissions are revoked in another tab, clicking "Delete Account" returns HTTP 403 Forbidden. Because `handleDelete` lacks a catch handler for 403, an uncaught rejection bubbles up, triggering React's unhandled rejection boundary and crashing the entire application into a blank white screen!

### Steps to Reproduce
1. In `AdminPanel.jsx`, trigger `handleDelete`.
2. Mock an HTTP 403 response (`{ status: 403, message: "Forbidden" }`).
3. Application crashes with unhandled promise error instead of showing an access-denied toast.

### Expected Behavior
Catch the error, check `err.status === 403`, and set `setErrorMessage("Access Denied: You do not have permission to perform this action.")` while keeping the interface intact.

### Actual Behavior
Unhandled error crashes the page.

### Impact
Total UI crash forcing users to perform a hard refresh and lose unsaved workspace data.

### Requirements
- Wrap `api.deleteAccount()` in `try/catch` and gracefully handle 403 status with appropriate user feedback.

**Files in Sandbox:**
- `AdminPanel.jsx`

**Verification Criteria (1 Test Case):**
- [Visible Sample Test] **Visible: Handles 403 Forbidden with try/catch and error message**

---

## 5. Master Index Table (All 120 Challenges)

| ID | Title | Arena | Difficulty | Technology | Category | Points |
|---|---|---|---|---|---|---|
| 1 | [CODE-E01] API Pagination Skips the Final Record | Code | Easy | Python | API & Web | 100 |
| 2 | [CODE-E02] Base64 Cursor Encoding Breaks for Unicode Input | Code | Easy | Python | API & Web | 100 |
| 3 | [CODE-E03] Empty API Responses Cause a Runtime Error | Code | Easy | Python | Error Handling | 100 |
| 4 | [CODE-E04] Incorrect Date Parsing Shifts Records to the Wrong Day | Code | Easy | Python | Data & Processing | 100 |
| 5 | [CODE-E05] A Retry Counter Stops One Attempt Too Early | Code | Easy | Python | Backend | 100 |
| 6 | [CODE-E06] Duplicate IDs Cause Incorrect Deduplication | Code | Easy | Python | Data & Processing | 100 |
| 7 | [CODE-E07] An Environment Variable Fallback Ignores Valid Configuration | Code | Easy | Python | Backend | 100 |
| 8 | [CODE-E08] An Incorrect Cache Key Returns Another Request's Result | Code | Easy | Python | Caching | 100 |
| 9 | [CODE-E09] Input Validation Rejects Valid Zero Values | Code | Easy | Python | Validation | 100 |
| 10 | [CODE-E10] A CSV Parser Mishandles Quoted Fields | Code | Easy | Python | Data & Processing | 100 |
| 11 | [CODE-E11] Sorting Produces Incorrect Results for Numeric Strings | Code | Easy | Python | Data & Processing | 100 |
| 12 | [CODE-E12] A Response Serializer Omits a Required Field | Code | Easy | Python | API & Web | 100 |
| 13 | [CODE-E13] An Incorrect Timeout Conversion Causes Premature Expiration | Code | Easy | Python | Backend | 100 |
| 14 | [CODE-E14] An Empty List Causes an Indexing Error | Code | Easy | Python | Error Handling | 100 |
| 15 | [CODE-E15] Incorrect Rounding Produces Wrong Invoice Totals | Code | Easy | Python | Data & Processing | 100 |
| 16 | [CODE-M01] API Retries Accidentally Repeat a Non-Idempotent Operation | Code | Medium | Python | API & Web | 150 |
| 17 | [CODE-M02] Cache Invalidation Leaves Stale Product Prices | Code | Medium | Python | Caching | 150 |
| 18 | [CODE-M03] Pagination Produces Duplicates When Sorting is Applied | Code | Medium | Python | Data & Processing | 150 |
| 19 | [CODE-M04] A Webhook Handler Processes the Same Event More Than Once | Code | Medium | Python | API & Web | 150 |
| 20 | [CODE-M05] Concurrent Updates Overwrite Newer User Preferences | Code | Medium | Python | Concurrency | 150 |
| 21 | [CODE-M06] Timezone Conversion Breaks Scheduled Notifications | Code | Medium | Python | Data & Processing | 150 |
| 22 | [CODE-M07] An API Client Incorrectly Handles HTTP 429 Responses | Code | Medium | Python | API & Web | 150 |
| 23 | [CODE-M08] A File-Processing Pipeline Silently Drops Malformed Records | Code | Medium | Python | Data & Processing | 150 |
| 24 | [CODE-M09] A Background Worker Loses Failed Jobs | Code | Medium | Python | Backend | 150 |
| 25 | [CODE-M10] A Database Transaction Partially Updates Related Records | Code | Medium | Python | Transactions | 150 |
| 26 | [CODE-M11] An Asynchronous Request Returns Stale Data | Code | Medium | Python | Concurrency | 150 |
| 27 | [CODE-M12] A Token Refresh Process Creates Intermittent Authentication Failures | Code | Medium | Python | Authentication | 150 |
| 28 | [CODE-M13] An Incorrect Merge Algorithm Loses Configuration Fields | Code | Medium | Python | Data & Processing | 150 |
| 29 | [CODE-M14] An Inventory Update Produces Incorrect Stock Totals | Code | Medium | Python | Backend | 150 |
| 30 | [CODE-M15] A CSV Export Corrupts Embedded Commas and Newlines | Code | Medium | Python | Data & Processing | 150 |
| 31 | [CODE-M16] A Batch Processor Mishandles Partial Failures | Code | Medium | Python | Backend | 150 |
| 32 | [CODE-M17] Incorrect Pagination Cursors Produce Infinite Loops | Code | Medium | Python | API & Web | 150 |
| 33 | [CODE-M18] A Data Transformation Fails for Optional Nested Properties | Code | Medium | Python | Data & Processing | 150 |
| 34 | [CODE-M19] A Rate Limiter Resets Counters Incorrectly | Code | Medium | Python | Rate Limiting | 150 |
| 35 | [CODE-M20] An Exception Handler Hides a Meaningful Application Failure | Code | Medium | Python | Error Handling | 150 |
| 36 | [CODE-H01] Concurrent Payment Requests Cause Duplicate Charges | Code | Hard | Python | Concurrency | 250 |
| 37 | [CODE-H02] A Distributed Job Processor Executes Non-Idempotent Jobs Twice | Code | Hard | Python | Backend | 250 |
| 38 | [CODE-H03] Incorrect Transaction Isolation Causes Inconsistent Inventory | Code | Hard | Python | Concurrency | 250 |
| 39 | [CODE-H04] Cache Invalidation Races with Concurrent Database Updates | Code | Hard | Python | Caching | 250 |
| 40 | [CODE-H05] A Distributed Lock is Released by the Wrong Request | Code | Hard | Python | Concurrency | 250 |
| 41 | [CODE-H06] A Retry Mechanism Causes a Request Storm During an Outage | Code | Hard | Python | API & Web | 250 |
| 42 | [CODE-H07] Concurrent File Writes Corrupt Generated Reports | Code | Hard | Python | Data & Processing | 250 |
| 43 | [CODE-H08] An Asynchronous Task Deadlocks Under Concurrent Execution | Code | Hard | Python | Concurrency | 250 |
| 44 | [CODE-H09] A Permission Check Occurs After a Sensitive State Change | Code | Hard | Python | Security | 250 |
| 45 | [CODE-H10] A Batch Migration Loses Records After a Partial Failure | Code | Hard | Python | Data & Processing | 250 |
| 46 | [CODE-H11] An Event-Processing Pipeline Reorders Dependent Events | Code | Hard | Python | Concurrency | 250 |
| 47 | [CODE-H12] Incorrect Rollback Logic Leaves Related Resources Inconsistent | Code | Hard | Python | Transactions | 250 |
| 48 | [CODE-H13] A Streaming Parser Leaks Memory for Large Inputs | Code | Hard | Python | Performance | 250 |
| 49 | [CODE-H14] A Multi-Step Account Update Leaves Partially Modified State | Code | Hard | Python | Transactions | 250 |
| 50 | [CODE-H15] A Concurrent Reservation System Oversells Limited Inventory | Code | Hard | Python | Concurrency | 250 |
| 51 | [SQL-E01] Customer Report Excludes Records Containing NULL Values | SQL Lab | Easy | SQL | Filtering | 100 |
| 52 | [SQL-E02] Monthly Revenue Report Uses the Wrong Date Boundary | SQL Lab | Easy | SQL | Filtering | 100 |
| 53 | [SQL-E03] Product Search Filters the Wrong Status | SQL Lab | Easy | SQL | Filtering | 100 |
| 54 | [SQL-E04] An INNER JOIN Removes Customers Without Orders | SQL Lab | Easy | SQL | Joins | 100 |
| 55 | [SQL-E05] A GROUP BY Query Calculates the Wrong Average | SQL Lab | Easy | SQL | Aggregation | 100 |
| 56 | [SQL-E06] Duplicate Email Records Are Not Detected Correctly | SQL Lab | Easy | SQL | Aggregation | 100 |
| 57 | [SQL-E07] An Invoice Query Incorrectly Rounds Monetary Totals | SQL Lab | Easy | SQL | Aggregation | 100 |
| 58 | [SQL-E08] A Report Includes Cancelled Orders | SQL Lab | Easy | SQL | Filtering | 100 |
| 59 | [SQL-E09] A Query Orders Numeric Values Stored as Text Incorrectly | SQL Lab | Easy | SQL | Sorting | 100 |
| 60 | [SQL-E10] A Query Returns the Wrong Top-Selling Product Because of Incorrect Sorting | SQL Lab | Easy | SQL | Sorting | 100 |
| 61 | [SQL-M01] A JOIN Duplicates Revenue Because of Multiple Order Items | SQL Lab | Medium | SQL | Joins | 150 |
| 62 | [SQL-M02] Customer Lifetime Value is Inflated by an Incorrect Aggregation | SQL Lab | Medium | SQL | Aggregation | 150 |
| 63 | [SQL-M03] Pagination Skips or Duplicates Rows When Ordering is Not Deterministic | SQL Lab | Medium | SQL | Sorting | 150 |
| 64 | [SQL-M04] A Window Function Uses the Wrong Partition | SQL Lab | Medium | SQL | Window Functions | 150 |
| 65 | [SQL-M05] A Monthly Report Mishandles Timezone Boundaries | SQL Lab | Medium | SQL | Aggregation | 150 |
| 66 | [SQL-M06] A LEFT JOIN Becomes an Accidental INNER JOIN | SQL Lab | Medium | SQL | Joins | 150 |
| 67 | [SQL-M07] An Inventory Report Calculates Incorrect Available Stock | SQL Lab | Medium | SQL | Aggregation | 150 |
| 68 | [SQL-M08] A Query Incorrectly Handles NULL Values in Conditional Aggregation | SQL Lab | Medium | SQL | Aggregation | 150 |
| 69 | [SQL-M09] A CTE Filters Records Before Aggregation When Filtering Should Occur Afterward | SQL Lab | Medium | SQL | CTE | 150 |
| 70 | [SQL-M10] A Duplicate-Detection Query Flags Valid Records | SQL Lab | Medium | SQL | Aggregation | 150 |
| 71 | [SQL-M11] A Ranking Query Assigns Incorrect Positions to Tied Values | SQL Lab | Medium | SQL | Window Functions | 150 |
| 72 | [SQL-M12] A Subquery Returns Multiple Rows Unexpectedly | SQL Lab | Medium | SQL | Subqueries | 150 |
| 73 | [SQL-M13] A Report Combines Historical and Current Prices Incorrectly | SQL Lab | Medium | SQL | Joins | 150 |
| 74 | [SQL-M14] A Query Counts Orders Instead of Distinct Customers | SQL Lab | Medium | SQL | Aggregation | 150 |
| 75 | [SQL-M15] A Recursive Query Omits Part of an Organizational Hierarchy | SQL Lab | Medium | SQL | CTE | 150 |
| 76 | [SQL-H01] Concurrent Inventory Reservations Oversell Stock | SQL Lab | Hard | SQL | Concurrency | 250 |
| 77 | [SQL-H02] A Payment Transaction Updates Balances Without Maintaining Consistency | SQL Lab | Hard | SQL | Transactions | 250 |
| 78 | [SQL-H03] A Multi-Table JOIN Multiplies Aggregates Across Independent Relationships | SQL Lab | Hard | SQL | Joins | 250 |
| 79 | [SQL-H04] A Transaction Failure Leaves Related Financial Records Inconsistent | SQL Lab | Hard | SQL | Transactions | 250 |
| 80 | [SQL-H05] A Database Migration Incorrectly Handles Existing NULL and Duplicate Values | SQL Lab | Hard | SQL | Schema | 250 |
| 81 | [SQL-H06] A Running-Total Query Produces Incorrect Results for Tied Timestamps | SQL Lab | Hard | SQL | Window Functions | 250 |
| 82 | [SQL-H07] A Reporting Query Uses Incorrect Isolation Assumptions During Concurrent Updates | SQL Lab | Hard | SQL | Transactions | 250 |
| 83 | [SQL-H08] A Soft-Delete Implementation Leaks Logically Deleted Records | SQL Lab | Hard | SQL | Filtering | 250 |
| 84 | [SQL-H09] A Recursive Hierarchy Query Mishandles Cycles | SQL Lab | Hard | SQL | CTE | 250 |
| 85 | [SQL-H10] An Analytics Query Becomes Extremely Slow Because of Incorrect Query Structure and Indexing Assumptions | SQL Lab | Hard | SQL | Performance | 250 |
| 86 | [FE-E01] A Form Submits Even When Required Fields Are Empty | Frontend | Easy | React | Forms | 100 |
| 87 | [FE-E02] A React Component Displays Stale or Incorrect Conditional Content | Frontend | Easy | React | Conditional Rendering | 100 |
| 88 | [FE-E03] A Product Card Shows the Wrong Price After a State Update | Frontend | Easy | React | React State | 100 |
| 89 | [FE-E04] A Button Fires the Wrong Event Handler | Frontend | Easy | React | DOM & Events | 100 |
| 90 | [FE-E05] A Search Field Ignores Uppercase/Lowercase Normalization | Frontend | Easy | React | Validation | 100 |
| 91 | [FE-E06] A Loading Indicator Never Disappears After an API Error | Frontend | Easy | React | React State | 100 |
| 92 | [FE-E07] A Responsive Layout Overflows on Mobile | Frontend | Easy | CSS | CSS & Styling | 100 |
| 93 | [FE-E08] A Form Displays an Incorrect Validation Message | Frontend | Easy | React | Validation | 100 |
| 94 | [FE-E09] A Modal Cannot Be Closed Using the Escape Key | Frontend | Easy | React | Accessibility | 100 |
| 95 | [FE-E10] A List Uses an Unstable or Incorrect React Key, Causing UI Inconsistencies | Frontend | Easy | React | DOM & Events | 100 |
| 96 | [FE-M01] Rapid Search Requests Overwrite Newer Results | Frontend | Medium | React | Asynchronous UI | 200 |
| 97 | [FE-M02] React State Updates Lose Changes During Batched Operations | Frontend | Medium | React | State Management | 200 |
| 98 | [FE-M03] useEffect Dependency Causes Stale Values or Missing Updates | Frontend | Medium | React | React Hooks | 200 |
| 99 | [FE-M04] Shopping Cart Calculates Totals Incorrectly After Mutation | Frontend | Medium | React | State Immutability | 200 |
| 100 | [FE-M05] Paginated List Does Not Reset Page When Filter Changes | Frontend | Medium | React | Pagination | 200 |
| 101 | [FE-M06] Event Listener Registered Repeatedly Without Cleanup | Frontend | Medium | React | Memory Leaks | 200 |
| 102 | [FE-M07] Authentication Refresh Request Creates Redirect Loops | Frontend | Medium | React | Authentication | 200 |
| 103 | [FE-M08] File-Upload Component Mishandles Progress and Failed Requests | Frontend | Medium | React | Error Handling | 200 |
| 104 | [FE-M09] Multi-Step Form Loses User Values When Navigating Backward | Frontend | Medium | React | Form Architecture | 200 |
| 105 | [FE-M10] Dashboard Renders Inconsistent Data After Parallel API Calls | Frontend | Medium | React | Asynchronous Data | 200 |
| 106 | [FE-M11] Frontend Cache Displays Outdated Profile Information | Frontend | Medium | React | Caching | 200 |
| 107 | [FE-M12] Component Submits Duplicate Requests After Repeated Clicks | Frontend | Medium | React | Form Submission | 200 |
| 108 | [FE-M13] Date Picker Displays Incorrect Date Due to Timezone Offset | Frontend | Medium | React | Date & Time | 200 |
| 109 | [FE-M14] Form Does Not Preserve Field-Level Server Validation Errors | Frontend | Medium | React | Form Validation | 200 |
| 110 | [FE-M15] Accessible Dropdown Fails to Close on Escape Key | Frontend | Medium | React | Accessibility | 200 |
| 111 | [FE-H01] Concurrent Frontend Requests Create Inconsistent Checkout State | Frontend | Hard | React | Concurrency | 300 |
| 112 | [FE-H02] Memory Leak Develops After Repeated Mount/Unmount Cycles | Frontend | Hard | React | Memory Management | 300 |
| 113 | [FE-H03] Shared Client-Side Cache Exposes Data Between Sessions | Frontend | Hard | JavaScript | Security | 300 |
| 114 | [FE-H04] Optimistic UI Update Corrupts State After Failed Requests | Frontend | Hard | React | Optimistic UI | 300 |
| 115 | [FE-H05] Complex Dashboard Produces Inconsistent Derived State | Frontend | Hard | React | Performance & Memoization | 300 |
| 116 | [FE-H06] Concurrent API Calls Trigger Multiple Token Refreshes | Frontend | Hard | JavaScript | Authentication Architecture | 300 |
| 117 | [FE-H07] Virtualized List Renders Incorrect Items After Filtering | Frontend | Hard | React | Virtualization | 300 |
| 118 | [FE-H08] Multi-Step Checkout Loses Consistency on Partial Failure | Frontend | Hard | React | Compensating Transactions | 300 |
| 119 | [FE-H09] Real-Time Interface Applies Out-Of-Order Events | Frontend | Hard | React | Real-Time State | 300 |
| 120 | [FE-H10] Frontend Fails to Gracefully Handle 403 Forbidden Responses | Frontend | Hard | React | Security & Error Handling | 300 |