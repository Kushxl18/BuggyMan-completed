# BuggyMan – Complete 120 Challenge Catalog & Quality Audit Reference

> Comprehensive, production-grade technical documentation for all **120 debugging challenges** in BuggyMan.
> Every challenge represents an authentic production defect modeled after real software incidents, complete with realistic incident reports, reproduction steps, expected behavior, starter code, challenge-specific constraints, and 3-level progressive non-spoiler hints.

---

## 1. Catalog Architecture & Distribution Summary

| Metric | Configuration | Description |
|---|---|---|
| **Total Challenges** | **120** | IDs 1 to 120 contiguous, zero missing or duplicated |
| **Code Arena** | **50** (IDs 1–50) | Backend logic, state management, concurrency, error boundaries, algorithms |
| **SQL Lab** | **35** (IDs 51–85) | Relational queries, NULL semantics, joins, aggregations, window functions, CTEs |
| **Frontend Studio** | **35** (IDs 86–120) | React component state, lifecycle effects, immutability, DOM events, UI responsiveness |
| **Difficulty Breakdown** | **35 Easy / 50 Medium / 35 Hard** | Distributed difficulty calibrated to real-world debugging complexity |
| **Progressive AI Hints** | **360 Hints (3 per challenge)** | Level 1: Conceptual Guide; Level 2: Directional Clue; Level 3: Root Cause Logic |
| **Quality Audit Pass Rate** | **100% (120/120 Solutions Pass / 120/120 Starters Fail)** | Zero flaky tests, fully deterministic evaluation sandbox |

---

## 2. Difficulty Breakdown Across Arenas

| Arena | Easy (100 XP) | Medium (150–200 XP) | Hard (250–300 XP) | Total Challenges |
|---|---|---|---|---|
| **Code Arena** (IDs 1–50) | 15 (IDs 1–15) | 20 (IDs 16–35) | 15 (IDs 36–50) | **50** |
| **SQL Lab** (IDs 51–85) | 10 (IDs 51–60) | 15 (IDs 61–75) | 10 (IDs 76–85) | **35** |
| **Frontend Studio** (IDs 86–120) | 10 (IDs 86–95) | 15 (IDs 96–110) | 10 (IDs 111–120) | **35** |
| **Total** | **35** | **50** | **35** | **120** |

---

## 3. Full Challenge Catalog (All 120 Challenges)

### Arena 1: Code Challenges (IDs 1 - 50)

#### Tier: Easy (15 Challenges)

##### Challenge 1: API Pagination Truncates Final Dataset Record
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
A compliance auditor reported that when reviewing data access logs across multiple pages, the final record from the total count is missing. The export summary says 25 items were logged, but clicking through pages 1, 2, and 3 only displays 24 items in total.

### Bug Report
Requesting the final page of records returns one fewer item than expected. For a 25-record dataset with page size 10, page 3 only returns 4 items (`[20, 21, 22, 23]`) instead of 5 (`[20, 21, 22, 23, 24]`), dropping record index 24.

### Steps to Reproduce
1. Query a dataset of 25 records with `page_size=10`.
2. Request page 3.
3. Observe that only 4 items are returned, omitting the 25th element.

### Expected Behaviour
`paginate(items, page, page_size)` must return all elements within the slice window, including the final boundary record, and return an empty list for invalid or out-of-bounds requests.

### Actual Behaviour
The slice boundary truncates the final element of the requested page window.

### Starter Files
`pagination.py` - Contains the dataset window slicing routine used by the audit API.

### Task
Investigate `pagination.py` and correct the upper slice boundary calculation so all matching records are returned without out-of-bounds errors.

### Acceptance Criteria
1. Full and partial pages return the exact slice of records requested.
2. Empty item lists and out-of-bounds page numbers return `[]`.
3. Page sizes less than 1 or pages less than 1 return `[]`.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In Python, list slicing syntax `items[start:end]` is exclusive of the `end` index.
- **Level 2 (Directional)**: Examine how the `end` boundary variable is calculated relative to `page * page_size`.
- **Level 3 (Root Cause)**: Because Python slicing is already exclusive of `end`, subtracting 1 from the upper boundary truncates the final element of the slice window.

---

##### Challenge 2: International Search Cursors Fail With Encoding Error
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
A warehouse manager in our Tokyo distribution center reported that attempting to view inventory catalogs crashes with an unexpected server error whenever searching for localized warehouse locations.

### Bug Report
When pagination cursor tokens contain localized names (such as Japanese characters or German umlauts), the cursor serialization routine crashes with a Unicode encoding failure.

### Steps to Reproduce
1. Search for inventory in warehouse "東京_Warehouse_01".
2. Generate cursor token using `encode_cursor`.
3. Server raises unhandled `UnicodeEncodeError`.

### Expected Behaviour
`encode_cursor` and `decode_cursor` must handle arbitrary UTF-8 Unicode strings without crashing.

### Actual Behaviour
The encoder converts input strings using an ASCII-only encoding scheme that cannot handle characters outside the 7-bit ASCII range.

### Starter Files
`cursor_encoder.py` - Contains cursor token serialization functions.

### Task
Update `cursor_encoder.py` to support full international Unicode characters for opaque cursor generation.

### Acceptance Criteria
1. Multi-byte Unicode cursor strings serialize and deserialize without data loss.
2. Empty or None inputs return an empty string.
3. Backward compatibility with standard ASCII strings is preserved.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Character strings must be converted to raw bytes before base64 encoding; consider which encoding format supports global character sets.
- **Level 2 (Directional)**: Inspect the character encoding format specified in `.encode()` and `.decode()` in `cursor_encoder.py`.
- **Level 3 (Root Cause)**: Standard ASCII only supports character codes up to 127; switching to UTF-8 enables full multibyte Unicode support.

---

##### Challenge 3: Market Data Service Crashes on Inactive Ticker Symbols
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
An automated financial dashboard worker crashed overnight when polling real-time quotes for newly registered or halted equities.

### Bug Report
Third-party quote providers return an empty payload `{"items": []}` for inactive equities. The ingestion pipeline crashes immediately with `IndexError: list index out of range`.

### Steps to Reproduce
1. Fetch quote for unlisted symbol "XYZ".
2. Vendor response is `{"items": []}`.
3. Ingestion worker encounters unhandled `IndexError`.

### Expected Behaviour
Return default `{"price": 0.0, "status": "unavailable"}` when items list is empty or missing.

### Actual Behaviour
The parser attempts to access elements in the items collection without verifying whether any items exist.

### Starter Files
`api_client.py` - Parses pricing responses from external financial providers.

### Task
Refactor `extract_latest_price` in `api_client.py` to defensively handle empty or malformed market payloads.

### Acceptance Criteria
1. Valid non-empty payloads return the current price with status `"active"`.
2. Empty items lists, missing keys, or non-dictionary payloads return `{"price": 0.0, "status": "unavailable"}` without crashing.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Defensive programming requires verifying that collections have elements before attempting to read positional indices.
- **Level 2 (Directional)**: Examine what happens in `extract_latest_price` when `payload.get("items", [])` returns an empty list.
- **Level 3 (Root Cause)**: Check whether `items` has elements before accessing `items[0]`, returning the default fallback dictionary if it is empty.

---

##### Challenge 4: European Bank Dates Assigned to Wrong Calendar Month
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
A tax audit discovered that banking transactions imported from European branches were categorized in the wrong fiscal quarter. An invoice dated 05/11/2026 (November 5) was processed as May 11.

### Bug Report
A payment made on `05/11/2026` (5th of November) is categorized by the system as `2026-05-11` (11th of May), shifting end-of-year tax deductions into the wrong fiscal quarter.

### Steps to Reproduce
1. Submit date string "05/11/2026".
2. Call `parse_transaction_date("05/11/2026")`.
3. Output returns date for May 11 instead of November 5.

### Expected Behaviour
`parse_transaction_date("05/11/2026")` should parse as day=5, month=11, year=2026 returning ISO `"2026-11-05"`.

### Actual Behaviour
The date parsing pattern assumes month-first date ordering, swapping the day and month components.

### Starter Files
`date_parser.py` - Converts incoming transaction date strings to standard ISO format.

### Task
Correct the format specifier in `date_parser.py` so European date strings are parsed into the expected ISO date format.

### Acceptance Criteria
1. Date strings like `"05/11/2026"` convert to `"2026-11-05"`.
2. Month and day positions are correctly recognized for international dates.
3. Invalid or non-string inputs safely return `None`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In standard date formatting tokens, `%d` represents day of the month and `%m` represents month number.
- **Level 2 (Directional)**: Inspect the format argument provided to `datetime.strptime` in `date_parser.py`.
- **Level 3 (Root Cause)**: The parser is currently using US ordering (`%m/%d/%Y`); adjust the tokens to match international European ordering (`%d/%m/%Y`).

---

##### Challenge 5: Transient Network Retries Abort Before Final Attempt
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
An operations team noticed that outbound logistics shipments were marked failed after only two attempts, despite a configured policy of three retries.

### Bug Report
When `max_retries=3` is configured, logs show the client only performs 2 attempts total (1 initial + 1 retry) before giving up and flagging orders as failed.

### Steps to Reproduce
1. Configure `execute_with_retry` with `max_retries=3`.
2. Mock an endpoint that fails twice and succeeds on attempt 3.
3. Function returns `None` prematurely without executing the 3rd attempt.

### Expected Behaviour
A `max_retries=3` policy must allow up to 3 total attempts if failures occur.

### Actual Behaviour
The loop control condition stops execution one iteration earlier than the configured limit.

### Starter Files
`retry_handler.py` - Contains the generic retry execution wrapper.

### Task
Adjust the loop boundary in `retry_handler.py` so that all configured retry attempts are executed.

### Acceptance Criteria
1. An operation that succeeds on the final allowed attempt returns the successful result.
2. An operation that succeeds on attempt 1 executes only once.
3. If all retry attempts fail, the function returns `None`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Trace the iteration count carefully from initial attempt to termination condition.
- **Level 2 (Directional)**: Examine the comparison in the `while` loop condition relative to `max_retries`.
- **Level 3 (Root Cause)**: Subtracting 1 from `max_retries` in `attempt < max_retries - 1` stops the loop after `N - 1` iterations instead of `N`.

---

##### Challenge 6: Multi-Clinic Patient Records Overwritten During Deduplication
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
Doctors at regional medical clinics reported missing patient records after daily batch syncs from independent clinic branches merged records into the central electronic health record system.

### Bug Report
When Clinic A and Clinic B both happen to assign local record ID `101`, the deduplication pipeline treats them as identical, permanently dropping one patient's record.

### Steps to Reproduce
1. Ingest `[{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 2, "id": 101, "name": "Bob"}]`.
2. Run deduplication function.
3. Alice's record is completely erased from the output.

### Expected Behaviour
Deduplication must use composite identity `(record["clinic_id"], record["id"])` to preserve records across distinct clinics.

### Actual Behaviour
The deduplicator identifies records using solely the local record ID, conflating distinct patient records across clinic branches.

### Starter Files
`deduplicator.py` - Ingestion filter for removing duplicate medical intake entries.

### Task
Update `deduplicate_records` in `deduplicator.py` to construct a unique composite identity.

### Acceptance Criteria
1. Records with matching local IDs from different clinics are both retained.
2. Genuine duplicates from the same clinic are pruned to a single instance.
3. Original list order is preserved.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In distributed or multi-tenant systems, primary keys generated by separate databases are not globally unique on their own.
- **Level 2 (Directional)**: Look at what is stored in the `seen` set in `deduplicate_records`.
- **Level 3 (Root Cause)**: Create a composite tuple combining `clinic_id` and `id` to ensure unique tracking across multiple branches.

---

##### Challenge 7: Zero Value Configuration Settings Reset to Default Timeout
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
Infrastructure engineers attempting to disable query timeouts for large data warehouse migrations noticed queries were killed after 30 seconds.

### Bug Report
When an operator sets `TIMEOUT_SECONDS=0` to disable timeouts for long-running batch ingestion, the application ignores `0` and falls back to default `30` seconds, causing premature batch termination.

### Steps to Reproduce
1. Configure environment dictionary with `{"TIMEOUT_SECONDS": "0"}`.
2. Call `get_timeout_seconds()`.
3. Returns `30` instead of `0`.

### Expected Behaviour
Setting `TIMEOUT_SECONDS="0"` must return `0`. Only if the variable is unset or empty should it use the fallback `30`.

### Actual Behaviour
The configuration parser evaluates numeric zero as a falsy value and returns the default timeout.

### Starter Files
`config_loader.py` - Parses system runtime environment parameters.

### Task
Modify `config_loader.py` to differentiate between a deliberately configured zero value and an absent configuration.

### Acceptance Criteria
1. An explicit configuration of `"0"` returns numeric `0`.
2. Unset or empty configurations return the fallback `30`.
3. Positive integer values return their exact parsed value.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In Python, the integer `0` evaluates to `False` in boolean conditions like `a or b`.
- **Level 2 (Directional)**: Check where `return parsed or 30` handles the converted integer in `config_loader.py`.
- **Level 3 (Root Cause)**: Distinguish between absence (`val is None` or empty string) and numeric zero: return `int(val)` directly once valid presence is confirmed.

---

##### Challenge 8: Multi-Tenant Cache Returns Data Across Customer Accounts
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
A security vulnerability alert was raised when Store A customers observed Store B's private VIP pricing tiers.

### Bug Report
User 42 belonging to Store A sees the exclusive VIP discount rates belonging to User 42 in Store B.

### Steps to Reproduce
1. Cache profile for `store_id="store_a", user_id="42"` with discount `10%`.
2. Request profile for `store_id="store_b", user_id="42"`.
3. Receives cached `10%` discount from Store A.

### Expected Behaviour
Cache keys must be tenant-isolated so distinct stores produce distinct cache keys for identical user IDs.

### Actual Behaviour
The cache key only identifies the user ID, causing cross-tenant cache collisions in multi-tenant environments.

### Starter Files
`cache_manager.py` - Helper generating cache lookup keys for profile data.

### Task
Refactor `generate_cache_key` in `cache_manager.py` to isolate cache records by merchant store.

### Acceptance Criteria
1. Different stores produce distinct cache keys for identical user IDs.
2. The returned key matches format `store:{store_id}:user:{user_id}`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Multi-tenant caching strategies require strict tenant namespacing to prevent cross-account information leakage.
- **Level 2 (Directional)**: Examine the format string returned by `generate_cache_key` in `cache_manager.py`.
- **Level 3 (Root Cause)**: Incorporate both `store_id` and `user_id` into the cache key pattern to guarantee uniqueness per merchant.

---

##### Challenge 9: Inventory System Rejects Out of Stock Zero Quantity Updates
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
A warehouse stock clerk reported that the inventory management portal throws a validation error saying 'Quantity is required' whenever they try to mark a depleted item as having 0 units in stock.

### Bug Report
When a warehouse manager enters `0` to indicate an item is completely out of stock, the API rejects the request with HTTP 400 `"Quantity is required"`.

### Steps to Reproduce
1. Submit payload `{"item_id": "SKU-99", "quantity": 0}`.
2. Call `validate_inventory_update`.
3. Returns `(False, "Quantity is required")`.

### Expected Behaviour
`quantity=0` is a valid stock count and must be accepted. Negative values and `None` should be rejected.

### Actual Behaviour
The validator treats numerical zero as missing data rather than a valid quantity count.

### Starter Files
`validator.py` - Validates inventory adjustment payloads before database updates.

### Task
Update `validate_inventory_update` in `validator.py` to allow zero while still rejecting negative or missing quantities.

### Acceptance Criteria
1. `quantity=0` returns `(True, "Valid")`.
2. Positive quantities return `(True, "Valid")`.
3. Negative quantities return `(False, "Quantity cannot be negative")`.
4. Missing (`None`) quantities return `(False, "Quantity is required")`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In Python, `not 0` evaluates to `True`, which causes falsy value checks to conflate numerical zero with `None`.
- **Level 2 (Directional)**: Review the condition checking `quantity` in `validator.py`.
- **Level 3 (Root Cause)**: Explicitly check `quantity is None` for missing inputs, allowing zero and positive integers to proceed.

---

##### Challenge 10: Customer Address Export Breaks on Embedded Commas
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
A shipping fulfillment team noted that customer export spreadsheets had scrambled columns, with apartment numbers placed into the city column and zip codes pushed into the country field.

### Bug Report
An imported row `"John Doe","123 Maple St, Suite 4","Springfield"` is split into 4 columns instead of 3, corrupting the address and city fields.

### Steps to Reproduce
1. Pass line `"John Doe","123 Maple St, Suite 4","Springfield"` into `parse_csv_row`.
2. Output array has length 4: `["John Doe", "123 Maple St", " Suite 4", "Springfield"]`.

### Expected Behaviour
Commas enclosed in double quotes must not split the field. The result should be `["John Doe", "123 Maple St, Suite 4", "Springfield"]`.

### Actual Behaviour
The tokenizer splits lines strictly on comma boundaries without evaluating surrounding quotation marks.

### Starter Files
`csv_parser.py` - Lightweight CSV line tokenizer.

### Task
Refactor `parse_csv_row` in `csv_parser.py` to correctly parse quoted CSV fields using Python's standard `csv` reader.

### Acceptance Criteria
1. Fields with embedded commas within quotes remain intact as a single column.
2. Standard unquoted CSV lines continue to parse properly.
3. Empty lines return an empty list.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Splitting strings by commas fails whenever data fields contain punctuation enclosed in quotes.
- **Level 2 (Directional)**: Python includes a standard library `csv` module designed specifically for compliant delimited data parsing.
- **Level 3 (Root Cause)**: Use `csv.reader` together with `io.StringIO` to tokenize the line according to standard CSV quoting rules.

---

##### Challenge 11: Build Priority Queue Orders High Severity Below Low Severity
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
Site reliability engineers discovered that Priority 10 security alerts were processed after Priority 2 routine notifications in the automated build dispatcher.

### Bug Report
Build numbers sort as `["1", "10", "100", "2", "20"]` instead of numeric order `["1", "2", "10", "20", "100"]`.

### Steps to Reproduce
1. Call `sort_priority_levels(["10", "2", "1", "20", "100"])`.
2. Output is sorted lexicographically rather than numerically.

### Expected Behaviour
Numeric strings must be sorted by their actual integer values.

### Actual Behaviour
The sorting function performs character-by-character lexicographical sorting instead of evaluating numeric magnitude.

### Starter Files
`sorter.py` - Ordering utility for task priority tags.

### Task
Update `sort_priority_levels` in `sorter.py` so numeric strings are ordered by their numerical value while preserving string types in the output.

### Acceptance Criteria
1. Numeric string elements are ordered by integer magnitude.
2. Output elements retain their original string representation.
3. Single-element and empty lists are handled safely.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Alphabetical string comparisons compare characters one by one from left to right, meaning `"10"` is evaluated as smaller than `"2"`.
- **Level 2 (Directional)**: Python's `sorted()` function takes a `key` parameter that dictates the comparison criterion.
- **Level 3 (Root Cause)**: Pass `key=int` to `sorted()` so each string is compared based on its integer conversion.

---

##### Challenge 12: Profile API Serializer Omits Account Creation Timestamp
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
Mobile application developers reported that iOS and Android client apps crashed immediately after login with a schema validation exception on the profile view.

### Bug Report
Mobile apps crash with `SchemaValidationError: Missing required property 'created_at'` when reading the `/api/v1/user` response payload.

### Steps to Reproduce
1. Fetch serialized user object from `serialize_user_profile(user)`.
2. Inspect keys present: `id`, `username`, `email`.
3. Notice that `created_at` field is missing.

### Expected Behaviour
Serialized payload must contain all required domain fields: `id`, `username`, `email`, and `created_at`.

### Actual Behaviour
The serialization mapping fails to map the account creation timestamp into the outbound response.

### Starter Files
`serializer.py` - Serializes user models for outbound JSON responses.

### Task
Add the missing `created_at` field to the serialization dictionary in `serializer.py`.

### Acceptance Criteria
1. Serialized output contains `id`, `username`, `email`, and `created_at`.
2. Empty or None user inputs safely return an empty dictionary.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Client contracts depend on strict schema conformance; every required field in the domain model must be mapped.
- **Level 2 (Directional)**: Check the dictionary literal constructed in `serialize_user_profile` in `serializer.py`.
- **Level 3 (Root Cause)**: Extract `created_at` using `.get("created_at")` and include it as a key in the returned dictionary.

---

##### Challenge 13: User Session Tokens Expire Seconds After Generation
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
"Every time I log into my account, I get kicked back to the login screen after just a few seconds. I barely have time to click my profile before seeing 'Session expired. Please log in again.' This is happening on every device across our entire team."

### Bug Report
Newly issued authentication tokens intended to remain valid for 1 hour expire almost immediately after generation, forcing users into continuous re-authentication loops.

### Steps to Reproduce
1. Call `calculate_expiration(current_timestamp=1700000000, seconds_to_live=3600)` with a known base timestamp and duration.
2. Compare the returned timestamp against the expected expiration time.
3. Observe that the calculated expiry timestamp expires almost immediately rather than remaining valid for the requested duration.

### Expected Behaviour
Given a base timestamp in seconds and a validity duration in seconds, the expiration function must return an integer timestamp representing the sum of both values (e.g. `1700000000 + 3600 = 1700003600`).

### Actual Behaviour
The calculated expiration timestamp is significantly smaller than expected, resulting in session tokens that expire after only a few seconds instead of the requested duration.

### Starter Files
`token_service.py` - Computes validity expiration times for authorization tokens.

### Task
Investigate `token_service.py` and correct the session expiration calculation so that authentication tokens return their full validity timestamp as an integer.

### Acceptance Criteria
1. `calculate_expiration(1700000000, 3600)` returns integer timestamp `1700003600`.
2. `calculate_expiration(100, 60)` returns integer timestamp `160`.
3. `calculate_expiration(500, 0)` returns integer timestamp `500`.

### Constraints
- `current_timestamp` is a valid Unix epoch timestamp in seconds (`1_000_000_000 <= current_timestamp <= 2_500_000_000`).
- `seconds_to_live` is a non-negative integer representing session validity duration in seconds (`0 <= seconds_to_live <= 604_800`).
- The returned timestamp must be an integer representing `current_timestamp + seconds_to_live`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Verify the units of measurement for timestamps and durations: both values here represent seconds.
- **Level 2 (Directional)**: Examine how `seconds_to_live` is combined with `current_timestamp` in `token_service.py`.
- **Level 3 (Root Cause)**: Both parameters are already measured in seconds; applying a scaling divisor mistakenly treats the input as milliseconds, reducing 3600 seconds down to only 3 seconds.

---

##### Challenge 14: Background Queue Worker Crashes When Task Buffer Is Empty
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
Our on-call SRE was paged at 03:00 AM because queue consumer pods were stuck in a crash-restart loop during low-traffic periods when no jobs were queued.

### Bug Report
When worker polls an idle queue with no pending messages, it crashes with `IndexError: list index out of range` and exits.

### Steps to Reproduce
1. Call `peek_next_job([])`.
2. Worker crashes with unhandled `IndexError`.

### Expected Behaviour
Return `None` when queue has 0 jobs without throwing an indexing exception.

### Actual Behaviour
The function attempts to read the first element of the job collection without checking if the collection contains any items.

### Starter Files
`queue_processor.py` - Inspects the next pending job in an asynchronous worker queue.

### Task
Add a guard in `queue_processor.py` to handle empty job collections safely.

### Acceptance Criteria
1. An empty job collection safely returns `None`.
2. Non-empty job collections return the first pending job.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Accessing positional index 0 on an empty sequence raises an immediate error in Python.
- **Level 2 (Directional)**: Check `jobs` for truthiness or length before attempting an index lookup.
- **Level 3 (Root Cause)**: Add an initial check: `if not jobs: return None` before reading `jobs[0]`.

---

##### Challenge 15: Invoice Tax Calculation Shows Discrepancy on Summed Line Items
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `Python`

### Incident Report
An enterprise customer contacted billing support because their monthly invoice total was off by one cent compared to their payment gateway charge receipt.

### Bug Report
Customer invoices show a total that is 1 cent off from payment gateway settlements due to rounding line-item tax amounts individually before summing them.

### Steps to Reproduce
1. Calculate tax on 3 line items of $10.04 at 8.25% tax rate.
2. Rounding each item produces $0.83 + $0.83 + $0.83 = $2.49.
3. True tax on total $30.12 is $2.4849 -> rounded to $2.48.

### Expected Behaviour
Sum line item subtotals first, then compute and round the total tax once: `round(sum(items) * tax_rate, 2)`.

### Actual Behaviour
The tax calculator rounds tax amounts at the per-item level before summing, accumulating rounding discrepancies.

### Starter Files
`invoice_calculator.py` - Computes total sales tax on customer order line items.

### Task
Refactor `calculate_total_tax` in `invoice_calculator.py` to sum all line items before applying tax and rounding.

### Acceptance Criteria
1. Line item amounts are summed before tax calculation and rounding.
2. The final total is rounded to 2 decimal places.
3. Empty line item lists return `0.0`.

### Constraints
- Numerical calculations must maintain precision without unintended unit scaling or integer truncation.
- Timestamps and durations are non-negative integer values.
- Character encodings must support full UTF-8 Unicode characters without encoding crashes.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Intermediate rounding during financial calculations compounds precision errors across multiple transactions.
- **Level 2 (Directional)**: Examine where the `round()` function is called inside the comprehension in `invoice_calculator.py`.
- **Level 3 (Root Cause)**: Sum the line items first (`sum(line_items)`), multiply the cumulative subtotal by the tax rate, and round the final result once.

---

#### Tier: Medium (20 Challenges)

##### Challenge 16: Payment Gateway Retries Result in Duplicate Customer Charges
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
"I was purchasing event tickets and got an error modal saying 'Connection lost, retrying'. When the page finally refreshed, I saw two identical charges of $50 on my credit card statement. Why was I billed twice for a single order?"

### Bug Report
When network packets drop and the client retries the payment request, customers are charged twice on their credit cards because the gateway treats each attempt as a distinct transaction.

### Steps to Reproduce
1. Execute `charge_with_retry(gateway, order_id="ORD-1", amount=50, max_attempts=3)`.
2. Mock a gateway where attempt 1 experiences a connection drop.
3. Observe that each attempt transmits a newly generated idempotency token.

### Expected Behaviour
The idempotency key must remain identical across all retry attempts for a given order so the gateway can detect and prevent duplicate charges.

### Actual Behaviour
The loop body generates a new random UUID token on every retry iteration.

### Starter Files
`payment_client.py` - Wraps external payment gateway calls with automated retry logic.

### Task
Refactor `charge_with_retry` in `payment_client.py` so that retrying an operation reuses a single, stable idempotency token.

### Acceptance Criteria
1. Subsequent retry attempts for an order submit the exact same idempotency key as the initial attempt.
2. Successful charges return the gateway response.
3. If all retry attempts are exhausted, the terminal exception is propagated.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In distributed systems, idempotency keys must be stable across all retries of the same logical operation.
- **Level 2 (Directional)**: Look at the variable scoping of `idempotency_key` relative to the `while` retry loop in `payment_client.py`.
- **Level 3 (Root Cause)**: Generate the idempotency key once before entering the retry loop so that every subsequent attempt reuses the identical key.

---

##### Challenge 17: Category Browse Page Displays Outdated Product Pricing
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
"Our merchandising team marked down the summer apparel collection from $100 to $60. When clicking the individual product link, the price shows $60, but on the main category browse page, the old $100 price is still showing. Shoppers are complaining about false advertising."

### Bug Report
When an administrator edits a product price from $100 down to $60, the individual product page updates, but the parent category catalog cache remains stale.

### Steps to Reproduce
1. Update product price via `update_product_price(db, cache, "P10", "CAT2", 60)`.
2. Inspect cache deletion calls.
3. Observe that only `product:P10` is purged, leaving `category:CAT2` untouched.

### Expected Behaviour
When an item's price is updated, both the item's individual cache and its parent category cache must be purged to maintain catalog consistency.

### Actual Behaviour
The invalidation logic only deletes the specific item key, ignoring related aggregation keys.

### Starter Files
`pricing_service.py` - Manages database updates and cache invalidation for catalog items.

### Task
Update `pricing_service.py` to ensure all dependent cache entries are properly evicted upon price updates.

### Acceptance Criteria
1. `cache.delete` is invoked for both the product key and category key.
2. The database record is successfully updated.
3. Returns `True` upon successful completion.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Cache invalidation strategies must purge both granular item keys and composite list/category keys.
- **Level 2 (Directional)**: Examine which cache keys are deleted in `update_product_price` in `pricing_service.py`.
- **Level 3 (Root Cause)**: Add an invalidation call targeting `f"category:{category_id}"` alongside the product key deletion.

---

##### Challenge 18: Social Feed Pagination Displays Duplicate Posts Across Pages
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
"As I scroll through the trending feed, post #5 appears on page 1 and then appears again at the top of page 2. Other posts seem to be getting pushed off the feed completely because tied posts keep jumping across page boundaries."

### Bug Report
When posts share identical upvote totals, sorting solely by upvotes produces non-deterministic ordering across page boundaries, shifting items into multiple pages.

### Steps to Reproduce
1. Create posts where multiple items share the same upvote count (e.g. 5 upvotes).
2. Fetch page 1 with page size 2, then fetch page 2.
3. Observe items shifting and appearing across both pages.

### Expected Behaviour
Feed ordering must be completely deterministic by including a secondary unique attribute (such as `id`) as a tie-breaker.

### Actual Behaviour
The sorting function keys only on `upvotes`, leaving relative order of ties undefined.

### Starter Files
`paginator.py` - Ranks community posts and slices them into paginated result sets.

### Task
Modify the sorting key in `paginator.py` to ensure stable, deterministic ordering across pages.

### Acceptance Criteria
1. Posts are sorted primarily by descending upvotes, secondarily by ascending ID.
2. Paginated subsets contain no duplicate items across pages.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: When paginating ordered datasets, sort criteria must produce a total, unambiguous ordering.
- **Level 2 (Directional)**: Inspect the lambda function supplied to `sorted()` in `paginator.py`.
- **Level 3 (Root Cause)**: Use a composite tuple key combining descending upvotes (`-p["upvotes"]`) and ascending ID (`p["id"]`).

---

##### Challenge 19: Order Fulfillment Webhook Triggers Duplicate Shipments on Replay
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Warehouse operators reported duplicate dispatch labels printed for identical orders whenever payment gateway webhooks were re-delivered.

### Bug Report
When network delays cause payment webhooks to be resent, the consumer processes the retransmitted message and triggers warehouse fulfillment actions again.

### Steps to Reproduce
1. Deliver webhook event `{"id": "evt_1", "order_id": "101"}`.
2. Deliver the identical event a second time.
3. Observe that fulfillment action is recorded twice in `order_actions`.

### Expected Behaviour
The webhook handler must check whether the event ID has already been recorded, returning `"ALREADY_PROCESSED"` and ignoring repeated side effects.

### Actual Behaviour
The handler triggers fulfillment actions unconditionally without checking historical event IDs.

### Starter Files
`webhook_dispatcher.py` - Processes incoming payment provider event notifications.

### Task
Add idempotency deduplication to `handle_webhook_event` in `webhook_dispatcher.py`.

### Acceptance Criteria
1. Previously unseen event IDs trigger fulfillment and return `"PROCESSED"`.
2. Seen event IDs return `"ALREADY_PROCESSED"` without duplicate fulfillment actions.
3. The event ID is recorded in the processed set.

### Constraints
- Network retry attempts for a given logical operation must reuse a stable, invariant idempotency token.
- Tenant-isolated caches must partition keys cleanly by tenant identifier.
- Expired sliding window timestamps must be pruned to avoid permanent request starvation.
- Operational errors (such as `ConnectionError`) must propagate rather than being masked as user validation errors.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Webhook consumers must be idempotent because delivery guarantees are typically "at least once".
- **Level 2 (Directional)**: Check `processed_events` before appending new entries to `order_actions`.
- **Level 3 (Root Cause)**: If `event_id` is present in `processed_events`, return `"ALREADY_PROCESSED"`; otherwise register the ID and proceed.

---

##### Challenge 20: Concurrent Profile Edits Silently Overwrite Recent Changes
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Users editing notification preferences from their phone and computer simultaneously reported that recent changes were mysteriously undone.

### Bug Report
When a user updates preferences at version 5, an older offline request at version 3 arriving milliseconds later unconditionally overwrites the newer state.

### Steps to Reproduce
1. Start with record `{"theme": "dark", "version": 5}`.
2. Submit delayed update `{"theme": "light", "version": 3}`.
3. Observe that theme is overwritten to `"light"` and version downgraded.

### Expected Behaviour
Optimistic concurrency must reject incoming updates whose version is less than or equal to the current record version.

### Actual Behaviour
The handler applies incoming updates unconditionally without checking if the incoming version is strictly greater than the currently stored version.

### Starter Files
`preference_manager.py` - Handles state updates for user preferences.

### Task
Implement optimistic locking version checks in `preference_manager.py`.

### Acceptance Criteria
1. Incoming updates with version numbers higher than current are applied and return `True`.
2. Stale updates with version numbers less than or equal to current are rejected and return `False`.
3. Current record values remain unchanged on rejection.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Optimistic locking relies on monotonicity: updates are valid only if their version counter exceeds the current state.
- **Level 2 (Directional)**: Compare `incoming_update.get("version", 0)` with `current_record.get("version", 0)` in `preference_manager.py`.
- **Level 3 (Root Cause)**: Reject the update and return `False` if incoming version is not strictly greater than current version.

---

##### Challenge 21: Scheduled Maintenance Reminders Trigger at Wrong Hour After Timezone Shift
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Patients in New York (UTC-5) complained they were woken up by automated medication reminder SMS messages sent at 03:00 AM instead of 08:00 AM.

### Bug Report
Converting local 08:00 AM in UTC-5 produces 03:00 UTC instead of 13:00 UTC because the timezone offset is added rather than subtracted.

### Steps to Reproduce
1. Schedule a reminder for 8:00 AM in timezone offset -5.
2. Call `convert_local_to_utc_hour(8, -5)`.
3. Observe returned UTC hour is `3` instead of `13`.

### Expected Behaviour
Converting local time to UTC follows `UTC = (Local - Offset) % 24`. For 8:00 AM at UTC-5, `8 - (-5) = 13:00 UTC`.

### Actual Behaviour
The calculation adds the offset directly instead of adjusting backward to UTC for negative offsets, inverting the time difference.

### Starter Files
`scheduler.py` - Converts local patient alert times to normalized UTC hours.

### Task
Correct the timezone offset calculation in `scheduler.py` to properly map local schedule hours into UTC.

### Acceptance Criteria
1. Negative UTC offsets correctly advance UTC hours (e.g. UTC-5 at 8am -> 13).
2. Positive UTC offsets correctly rewind UTC hours across 24-hour boundaries (e.g. UTC+9 at 8am -> 23).
3. Zero offset preserves the identical hour.

### Constraints
- Numerical calculations must maintain precision without unintended unit scaling or integer truncation.
- Timestamps and durations are non-negative integer values.
- Character encodings must support full UTF-8 Unicode characters without encoding crashes.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Remember the standard timezone formula: `UTC = Local - Offset`.
- **Level 2 (Directional)**: Check the arithmetic operator used with `utc_offset_hours` in `scheduler.py`.
- **Level 3 (Root Cause)**: Subtract `utc_offset_hours` from `local_hour` before taking modulo 24: `(local_hour - utc_offset_hours) % 24`.

---

##### Challenge 22: Ingestion Worker Crashes When Upstream API Rate Limit Returns HTTP 429
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
An algorithmic trading daemon crashed in production during market volatility when an exchange API rate-limited requests with HTTP 429.

### Bug Report
When `Retry-After` header is missing or contains non-numeric text, `parse_rate_limit_delay` crashes with `KeyError` or `ValueError`, preventing the client from backing off.

### Steps to Reproduce
1. Receive rate limit response without `Retry-After` header.
2. Call `parse_rate_limit_delay(response_headers={}, attempt=3)`.
3. Function crashes with unhandled exception.

### Expected Behaviour
Safely extract numeric `Retry-After` seconds; if missing or invalid, fall back to exponential backoff `min(60, 2 ** attempt)`.

### Actual Behaviour
The header parser assumes the rate limit header is always present and strictly numeric, crashing on missing or non-standard header formats.

### Starter Files
`http_client.py` - Parses rate limit feedback headers to determine retry delay.

### Task
Refactor `parse_rate_limit_delay` in `http_client.py` to defensively parse headers with safe exponential fallback.

### Acceptance Criteria
1. Valid numeric headers return their integer delay value.
2. Missing or malformed headers return exponential delay `min(60, 2 ** attempt)`.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: API response headers cannot be assumed to always exist or contain valid integer strings.
- **Level 2 (Directional)**: Use safe dictionary `.get()` lookup and verify that the value consists of digits before converting.
- **Level 3 (Root Cause)**: Fall back to calculating `min(60, 2 ** attempt)` whenever the header is absent or non-numeric.

---

##### Challenge 23: Telemetry Ingestion Pipeline Silently Drops Malformed Records
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Payroll audit reported that employees were missing paychecks because timesheet rows with formatting errors were silently erased.

### Bug Report
When a timesheet row has an invalid numerical string (e.g. `"forty"` instead of `40`), a bare `except: pass` discards the record without alerting operators.

### Steps to Reproduce
1. Ingest rows `[{"emp_id": "E1", "hours": "40"}, {"emp_id": "E2", "hours": "forty"}]`.
2. Run `process_timesheets`.
3. Notice that `quarantined` remains empty and record `E2` vanishes from all outputs.

### Expected Behaviour
Valid records are parsed into `valid`, while malformed rows are collected in `quarantined` along with their error description.

### Actual Behaviour
The ingestion routine suppresses parsing failures silently, dropping corrupted records from the audit trail without error tracking.

### Starter Files
`pipeline.py` - Ingestion parser for worker timesheet records.

### Task
Update `process_timesheets` in `pipeline.py` to route failed records into a quarantine dead-letter collection.

### Acceptance Criteria
1. Valid rows are parsed and added to `valid`.
2. Failed rows are placed in `quarantined` with structure `{"record": r, "error": str(e)}`.
3. Processing continues for subsequent rows without halting.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Silent exception swallowing destroys observability and causes unrecoverable data loss.
- **Level 2 (Directional)**: Inspect what happens inside the `except Exception:` block in `pipeline.py`.
- **Level 3 (Root Cause)**: Capture the exception object as `e` and append `{"record": r, "error": str(e)}` to `quarantined_records`.

---

##### Challenge 24: Worker Daemon Permanently Loses Failed Background Jobs
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Operations noticed customer email notification jobs vanished from queue logs whenever downstream mail gateways were unreachable.

### Bug Report
The worker acknowledges completion of the job before invoking the worker task function. If the task crashes, the job is already dequeued and acknowledged, losing it forever.

### Steps to Reproduce
1. Enqueue job `{"id": "JOB-1"}`.
2. Provide a job function that raises `RuntimeError`.
3. Run `execute_job`.
4. Observe that `queue.ack` was already called, and the job was never sent to the Dead-Letter Queue (DLQ).

### Expected Behaviour
Acknowledge completion only after successful execution. If execution raises an exception, send the job to the DLQ (`queue.send_to_dlq(job, str(e))`).

### Actual Behaviour
The queue worker acknowledges the message from the queue before running the task, so any runtime crash permanently destroys the uncompleted job.

### Starter Files
`worker_queue.py` - Manages message acknowledgment and fault routing for background jobs.

### Task
Reorganize `execute_job` in `worker_queue.py` to ensure reliable acknowledgment and dead-letter routing.

### Acceptance Criteria
1. Successful jobs are acknowledged via `queue.ack(job["id"])`.
2. Failed jobs are not acknowledged and are routed to DLQ via `queue.send_to_dlq(job, str(e))`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Reliable queue processing requires "at least once" acknowledgment semantics: acknowledge only after work succeeds.
- **Level 2 (Directional)**: Notice that `queue.ack` is executed before `job_fn(job)` in `worker_queue.py`.
- **Level 3 (Root Cause)**: Wrap `job_fn(job)` in a try/except block; call `queue.ack` on success, and `queue.send_to_dlq` on error.

---

##### Challenge 25: Ledger Transfer Deducts Funds When Recipient Account Does Not Exist
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Banking compliance detected discrepancies in customer ledgers where sender balances were debited even though transfers failed to reach non-existent accounts.

### Bug Report
When sending money to an invalid recipient, `transfer_funds` debits the sender balance first. When crediting the receiver fails with `KeyError`, the sender's balance is not restored.

### Steps to Reproduce
1. Initialize balance `{"Alice": 200}`.
2. Attempt transfer: `transfer_funds(balances, "Alice", "NonExistent", 50)`.
3. Catch the expected `KeyError`.
4. Observe Alice's balance remains at 150 instead of rolling back to 200.

### Expected Behaviour
Money transfers must satisfy atomic all-or-nothing guarantees. If crediting the recipient fails, any prior sender deduction must be rolled back.

### Actual Behaviour
The transfer deducts funds from the sender before confirming that the recipient exists, leaving the sender's account short if the transfer fails.

### Starter Files
`account_transfer.py` - Executes balance transfers between internal accounts.

### Task
Implement transactional rollback in `account_transfer.py` to restore sender balances upon failed credits.

### Acceptance Criteria
1. If the recipient does not exist, the sender balance remains completely unchanged.
2. Successful transfers update both sender and receiver accounts accurately.
3. Insufficient balance checks are enforced.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Financial mutations must adhere to ACID principles: multi-step operations must undo prior steps if later steps fail.
- **Level 2 (Directional)**: Look at the order of state changes relative to the validation check for `receiver in balances`.
- **Level 3 (Root Cause)**: Roll back the sender debit (`balances[sender] += amount`) before raising the error, or validate the recipient prior to debiting.

---

##### Challenge 26: Dashboard Search Box Replaces Fresh Results With Stale Response
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Users searching a document catalog noticed search results frequently flickered and displayed results for older queries they had already backspaced over.

### Bug Report
When a user rapidly types "react" followed by "python", the slower asynchronous request for "react" resolves after "python", overwriting fresh results with stale data.

### Steps to Reproduce
1. Set store `latest_issued_seq = 2`.
2. Apply response with sequence ID 1 (`"stale_react"`).
3. Apply response with sequence ID 2 (`"fresh_python"`).
4. Apply delayed response with sequence ID 1 (`"late_stale_react"`).
5. Notice that `current_result` is overwritten by the stale sequence 1 result.

### Expected Behaviour
Responses with a sequence ID older than the latest issued request sequence must be ignored.

### Actual Behaviour
The response handler updates the active search result with whatever packet arrives last over the network, regardless of which query was initiated first.

### Starter Files
`data_fetcher.py` - Stores and resolves asynchronous search result payloads.

### Task
Implement sequence order verification in `data_fetcher.py` to discard out-of-order responses.

### Acceptance Criteria
1. Responses with sequence IDs matching or exceeding `latest_issued_seq` are applied.
2. Responses with older sequence IDs are discarded without mutating `current_result`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Asynchronous network requests do not guarantee arrival in the order they were dispatched.
- **Level 2 (Directional)**: Examine `response_seq_id` relative to `self.latest_issued_seq` in `apply_response`.
- **Level 3 (Root Cause)**: Add a condition to reject responses if `response_seq_id < self.latest_issued_seq` before updating `self.current_result`.

---

##### Challenge 27: Concurrent API Requests Trigger Redundant Token Refresh Requests
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Security logs detected repeated OAuth token revocation alarms caused by multiple concurrent client threads refreshing expired tokens simultaneously.

### Bug Report
When multiple client requests discover an expired token at the same millisecond, each thread invokes the refresh function independently instead of reusing an active token.

### Steps to Reproduce
1. Create a `TokenManager` with a mock refresh callback.
2. Call `get_token()` twice in succession.
3. Observe that the refresh callback is called twice even though a valid token was already cached.

### Expected Behaviour
`get_token` must return the existing valid `access_token` if one is already cached, invoking `refresh_fn` only when no token is present.

### Actual Behaviour
The token manager issues a fresh authentication exchange on every single request instead of reusing cached active credentials.

### Starter Files
`token_refresh.py` - Token manager maintaining OAuth access credentials.

### Task
Update `get_token` in `token_refresh.py` to reuse the existing access token when present.

### Acceptance Criteria
1. Repeated calls to `get_token` reuse the cached token without re-triggering `refresh_fn`.
2. Initial token acquisition correctly calls `refresh_fn`.

### Constraints
- `current_timestamp` is a valid Unix epoch timestamp in seconds (`1_000_000_000 <= current_timestamp <= 2_500_000_000`).
- `seconds_to_live` is a non-negative integer representing session validity duration in seconds (`0 <= seconds_to_live <= 604_800`).
- The returned timestamp must be an integer representing `current_timestamp + seconds_to_live`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Token managers must cache active credentials to avoid redundant round-trips to identity providers.
- **Level 2 (Directional)**: Examine whether `self.access_token` is checked before calling `self.refresh_fn()` in `token_refresh.py`.
- **Level 3 (Root Cause)**: Return `self.access_token` immediately if it is already populated, calling `self.refresh_fn()` only when absent.

---

##### Challenge 28: Environment Configuration Merge Drops Nested Database Settings
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
After deploying an environment override specifying custom database port `5433`, production containers crashed because the database hostname setting was completely wiped out.

### Bug Report
When supplying a nested dictionary override such as `{"db": {"port": 5433}}`, the merge logic replaces the entire `db` object, destroying unmentioned sibling properties like `host`.

### Steps to Reproduce
1. Base configuration has `{"db": {"host": "localhost", "port": 5432}}`.
2. Override is `{"db": {"port": 5433}}`.
3. Call `deep_merge(base, override)`.
4. Result is `{"db": {"port": 5433}}`, missing `"host"`.

### Expected Behaviour
Nested dictionaries must be recursively merged so sibling keys in the base dictionary are preserved unless explicitly overridden.

### Actual Behaviour
The configuration loader replaces entire nested dictionaries wholesale, erasing unmentioned sibling properties when applying nested overrides.

### Starter Files
`config_merger.py` - Combines default application configurations with environment overrides.

### Task
Implement a recursive deep merge in `config_merger.py` to preserve non-conflicting nested keys.

### Acceptance Criteria
1. Nested dictionaries are merged recursively.
2. Unmentioned sibling keys in nested structures are preserved.
3. Explicit override values take precedence.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Standard Python `dict.update()` performs a shallow replacement of top-level keys.
- **Level 2 (Directional)**: Iterate through the keys in `override` and check if both `result[key]` and `override[key]` are dictionaries.
- **Level 3 (Root Cause)**: Recursively call `deep_merge` for nested dictionaries, assigning primitive values directly.

---

##### Challenge 29: Flash Sale Checkout Allows Negative Warehouse Inventory Stock
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
During a flash clearance sale, an e-commerce platform sold 15 units of an item when only 2 units existed in the physical warehouse, leading to order cancellations.

### Bug Report
When available stock is 2 and an order requests 5 units, `decrement_stock` subtracts the quantity blindly, leaving stock at -3 without throwing an error.

### Steps to Reproduce
1. Initialize inventory `{"SKU1": 2}`.
2. Call `decrement_stock(inv, "SKU1", 5)`.
3. Observe inventory drops to `-3` without raising an exception.

### Expected Behaviour
If the requested quantity exceeds available stock, raise `ValueError("Insufficient stock")` and leave inventory unaltered.

### Actual Behaviour
The function performs unchecked subtraction directly on the inventory dictionary.

### Starter Files
`inventory_service.py` - Decrements warehouse stock allocations during order checkout.

### Task
Add validation guards in `inventory_service.py` to prevent negative inventory balances.

### Acceptance Criteria
1. Requests exceeding available stock raise `ValueError("Insufficient stock")`.
2. Inventory balances remain unchanged when an order is rejected.
3. Valid orders deduct stock correctly and return the remaining count.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Inventory operations must enforce invariants: available quantities cannot drop below zero.
- **Level 2 (Directional)**: Check `inventory.get(item_id, 0)` against `qty` before modifying the dictionary in `inventory_service.py`.
- **Level 3 (Root Cause)**: Raise `ValueError("Insufficient stock")` if requested quantity exceeds current availability.

---

##### Challenge 30: Report Export Corrupts Rows With Embedded Commas and Line Breaks
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Marketing analysts reported that CSV exports of user survey comments were corrupted, with user text wrapping across lines and misaligning spreadsheet columns.

### Bug Report
When survey comments contain commas (e.g. `"Hello, World"`), raw string concatenation joins fields without enclosing quotes, causing spreadsheet tools to split the cell.

### Steps to Reproduce
1. Export row `["Alice", "Hello, World", 100]`.
2. Inspect output string: `"Alice,Hello, World,100\n"`.
3. Note that `"Hello, World"` lacks enclosing quotes.

### Expected Behaviour
Fields containing commas, quotes, or whitespace must be properly quoted and escaped according to RFC 4180.

### Actual Behaviour
The exporter tokenizes and concatenates values with raw delimiters without enclosing quotes around text fields containing commas.

### Starter Files
`csv_exporter.py` - Converts database records into formatted CSV rows.

### Task
Refactor `export_to_csv_row` in `csv_exporter.py` to produce RFC 4180 compliant CSV formatting that properly quotes and escapes complex text fields.

### Acceptance Criteria
1. Fields with embedded commas are wrapped in quotes.
2. Standard fields format correctly with proper delimiters.
3. Trailing newline character is included.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Manual string joining cannot properly handle special characters like delimiters, quotes, or newlines.
- **Level 2 (Directional)**: Use Python's standard `csv` library and `io.StringIO` in `csv_exporter.py`.
- **Level 3 (Root Cause)**: Instantiate a `csv.writer` writing into an in-memory `StringIO` buffer, write the row, and return the buffer value.

---

##### Challenge 31: Bulk Email Notification Batch Halts on First Invalid Address
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Marketing noticed that monthly newsletter delivery stopped halfway through, leaving thousands of customers without scheduled announcements.

### Bug Report
When sending a batch of 100 notifications, an unhandled exception thrown on item #42 crashes the entire loop, leaving items 43-100 completely unprocessed.

### Steps to Reproduce
1. Submit batch `[{"id": 1}, {"id": 2}, {"id": 3}]`.
2. Provide a mock send function where item 2 raises `ValueError`.
3. Observe that execution terminates prematurely, and item 3 is never attempted.

### Expected Behaviour
Individual send failures must be caught and recorded in `failed`, allowing subsequent valid batch items to process normally into `succeeded`.

### Actual Behaviour
An error on a single recipient halts the entire dispatcher loop, abandoning all remaining messages in the batch.

### Starter Files
`batch_processor.py` - Dispatches bulk notification items and aggregates results.

### Task
Isolate item errors in `batch_processor.py` to prevent partial batch failures from abandoning remaining items.

### Acceptance Criteria
1. Successful items are recorded in `succeeded`.
2. Failing items are recorded in `failed` with structure `{"id": item["id"], "error": str(e)}`.
3. Subsequent batch items continue processing after an error.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Batch processors must isolate item-level failures to protect overall pipeline throughput.
- **Level 2 (Directional)**: Examine the exception handling inside the `for item in items:` loop in `batch_processor.py`.
- **Level 3 (Root Cause)**: Wrap `send_fn(item)` in a try/except block, appending successful IDs to `succeeded` and failures to `failed`.

---

##### Challenge 32: Exhausted Dataset Slicing Causes Infinite Client Pagination Loop
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
API gateway monitors detected an external client making millions of identical requests overnight, consuming massive server bandwidth.

### Bug Report
When a client reaches the end of paginated results and fewer than `page_size` items remain, the server continues returning a non-null `next_cursor`, trapping clients in an infinite loop.

### Steps to Reproduce
1. Query a page with `page_size=10` containing only 1 record.
2. Call `build_page_response(records=[{"id": 1}], page_size=10, last_id=1)`.
3. Inspect `res["next_cursor"]`: returns `"cur_1"` instead of `None`.

### Expected Behaviour
When the returned record count is strictly less than `page_size`, the dataset is exhausted and `next_cursor` must be `None`.

### Actual Behaviour
The response builder generates an opaque next-page token even when the returned page has fewer items than requested, indicating the dataset is exhausted.

### Starter Files
`cursor_paginator.py` - Formats paginated API responses and cursor tokens.

### Task
Update `build_page_response` in `cursor_paginator.py` to signal pagination completion when records are exhausted.

### Acceptance Criteria
1. Partial pages (record count < page_size) return `next_cursor: None`.
2. Full pages return the formatted cursor string.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Cursor-based pagination signals the end of a collection by returning a null or empty cursor token.
- **Level 2 (Directional)**: Check the count of `records` compared to `page_size` in `build_page_response`.
- **Level 3 (Root Cause)**: Assign `next_cursor` only if `len(records) == page_size`; otherwise set it to `None`.

---

##### Challenge 33: User Profile Enrichment Service Crashes on Missing Optional Addresses
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Customer support reported that newly signed-up users could not access their account settings because the profile page displayed an internal server error.

### Bug Report
When a user profile has no address (`address` is `None` or omitted), formatting throws `TypeError: 'NoneType' object is not subscriptable` when attempting to access city.

### Steps to Reproduce
1. Submit profile `{"name": "Alice", "address": None}`.
2. Call `format_postal_address`.
3. Observe unhandled `TypeError` on nested property lookup.

### Expected Behaviour
Safely handle missing or `None` address objects, defaulting city to `"Unknown City"`.

### Actual Behaviour
The formatter attempts to read nested address properties without verifying that the parent address object exists.

### Starter Files
`transformer.py` - Transforms raw profile records into formatted postal labels.

### Task
Implement safe navigation in `transformer.py` to handle missing address metadata gracefully.

### Acceptance Criteria
1. Profiles with `None` or missing address format with `"Unknown City"`.
2. Profiles with valid address dictionaries format with the actual city name.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Chained indexing on nested dictionaries raises errors whenever an intermediate parent property is missing or `None`.
- **Level 2 (Directional)**: Inspect how `address` is retrieved from `profile` in `transformer.py`.
- **Level 3 (Root Cause)**: Use safe dictionary access: `addr = profile.get("address") or {}`, then retrieve `city` with default `"Unknown City"`.

---

##### Challenge 34: Sliding Window API Rate Limiter Fails to Expire Old Request Counters
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
API users complained that their applications were permanently blocked with rate limit errors even after waiting hours between requests.

### Bug Report
The rate limiter records request timestamps into a history list, but never purges timestamps older than the sliding window, causing the count to grow indefinitely until all future requests are rejected.

### Steps to Reproduce
1. Configure `SlidingWindowLimiter(max_requests=2, window_size=60)`.
2. Send requests at `t=10` and `t=20`.
3. Advance clock to `t=80` (where `t=10` is expired: 80 - 10 = 70 > 60).
4. Send request at `t=80`.
5. Observe that the request is rejected because history length is still 2.

### Expected Behaviour
Before checking request limits, timestamps older than `current_time - window_size` must be evicted from the history list.

### Actual Behaviour
The limiter checks request history size without evicting timestamps that have aged out of the active time window.

### Starter Files
`rate_limiter.py` - Sliding window rate limiter for gateway traffic.

### Task
Implement window pruning in `allow_request` in `rate_limiter.py`.

### Acceptance Criteria
1. Requests outside the active window are pruned, allowing new requests through.
2. Requests within the active window exceeding the limit are blocked.
3. Allowed requests append their timestamp to history.

### Constraints
- Network retry attempts for a given logical operation must reuse a stable, invariant idempotency token.
- Tenant-isolated caches must partition keys cleanly by tenant identifier.
- Expired sliding window timestamps must be pruned to avoid permanent request starvation.
- Operational errors (such as `ConnectionError`) must propagate rather than being masked as user validation errors.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Sliding window rate limiters must filter out expired events before evaluating current traffic volume.
- **Level 2 (Directional)**: Look at `self.history` in `allow_request` in `rate_limiter.py` before the length check.
- **Level 3 (Root Cause)**: Filter `self.history` to keep only entries where `current_time - t < self.window_size` before comparing against `self.max_requests`.

---

##### Challenge 35: Generic Exception Catch Block Conceals Root Cause of Service Failure
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `Python`

### Incident Report
Infrastructure teams spent 48 hours investigating supposed customer credential lockouts, only to find the external authentication server had network outage issues.

### Bug Report
When an LDAP authentication server times out with `ConnectionError`, `verify_credentials` catches broad `Exception` and returns `{"authenticated": False, "error": "Invalid credentials"}`.

### Steps to Reproduce
1. Mock an authentication function that raises `ConnectionError("LDAP timeout")`.
2. Call `verify_credentials(mock_auth, "alice", "secret")`.
3. Observe that network failure is swallowed and reported as user password error.

### Expected Behaviour
Infrastructure errors like `ConnectionError` must propagate upward so monitoring systems detect outages, while credential errors like `ValueError` return bad credential responses.

### Actual Behaviour
Catching generic exceptions silences low-level infrastructure network timeouts and masks them as ordinary validation failures.

### Starter Files
`service_client.py` - Wraps external LDAP authentication service queries.

### Task
Narrow exception handling in `service_client.py` so operational exceptions propagate to system monitors.

### Acceptance Criteria
1. `ConnectionError` and other operational exceptions are allowed to raise.
2. `ValueError` returns `{"authenticated": False, "error": "Invalid credentials"}`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Overly broad exception catching hides severe infrastructure defects under user error messages.
- **Level 2 (Directional)**: Examine the `except Exception:` clause in `service_client.py`.
- **Level 3 (Root Cause)**: Catch `ValueError` specifically for invalid credentials, allowing `ConnectionError` and unexpected exceptions to bubble up.

---

#### Tier: Hard (15 Challenges)

##### Challenge 36: Rapid Double-Tap Submissions Cause Duplicate Checkout Charges
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Customer support reported numerous complaints from mobile shoppers who were charged twice when double-tapping the checkout submission button on slow connections.

### Bug Report
When two requests arrive within milliseconds, both pass the `paid_orders` check before either sets the completed state, charging the customer's payment method twice.

### Steps to Reproduce
1. Dispatch two concurrent payment execution calls for order `"ORD1"`.
2. Notice that both calls check `paid_orders` simultaneously before any charge completes.
3. Observe duplicate charge function invocations.

### Expected Behaviour
The system must acquire an exclusive processing lock for the order ID prior to executing the charge, returning `{"status": "DUPLICATE_IGNORED"}` (or `"ALREADY_PROCESSING"` / `"LOCKED"`) for concurrent attempts.

### Actual Behaviour
Check-then-act race condition executes charges before locking, allowing parallel executions to proceed.

### Starter Files
`payment_gateway.py` - Payment processing service coordinating order status and merchant charges.

### Task
Implement mutually exclusive locking in `payment_gateway.py` so only one worker can process payment for an order at any given time.

### Acceptance Criteria
1. The first request acquires the lock, completes the charge, registers the order in `paid_orders`, and releases the lock.
2. Concurrent requests targeting a locked or already paid order return a duplicate or locked status without charging.
3. Charge exceptions do not leave locks dangling.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In multi-threaded checkout systems, check-then-act sequences must be protected by atomic locks to prevent race conditions.
- **Level 2 (Directional)**: Inspect when `processing_locks` is checked and acquired relative to `charge_fn` in `payment_gateway.py`.
- **Level 3 (Root Cause)**: Check both `paid_orders` and `processing_locks` upfront; acquire the lock before calling `charge_fn`, and release it once complete.

---

##### Challenge 37: Long Video Transcoding Jobs Reassigned Mid-Execution
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Engineering noticed rendering worker clusters producing corrupted, duplicated MP4 assets because long video transcoding jobs were being reassigned to second workers.

### Bug Report
When a high-definition video takes 45 seconds to render, the 30-second worker lease expires. The scheduler marks Worker 1 dead and assigns the job to Worker 2, causing both nodes to render concurrently.

### Steps to Reproduce
1. Assign job `"J1"` with initial lease expiration at `t=100`.
2. Worker processes job actively at `t=90`.
3. Clock reaches `t=105` without heartbeat extension.
4. `should_reassign_job` flags the job for reassignment while Worker 1 is still running.

### Expected Behaviour
Active workers must periodically send heartbeat renewals (`renew_lease`) to extend their expiration deadline by `extension` seconds while processing.

### Actual Behaviour
The heartbeat renewal routine lacks logic to extend expiration deadlines, allowing active worker leases to lapse prematurely.

### Starter Files
`job_scheduler.py` - Coordinates worker leases and dead node task reassignment.

### Task
Implement `renew_lease` in `job_scheduler.py` so active workers can extend their lease expiration.

### Acceptance Criteria
1. `renew_lease` updates the job's `expires_at` timestamp by adding `extension` seconds.
2. A renewed lease prevents `should_reassign_job` from triggering premature reassignment.
3. Unrenewed expired jobs continue to be reassigned.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Distributed leasing algorithms require periodic heartbeats from healthy workers to prove liveness for long-running tasks.
- **Level 2 (Directional)**: Look at the empty `pass` statement in `renew_lease` in `job_scheduler.py`.
- **Level 3 (Root Cause)**: Update the lease dictionary for `job_id` so that `expires_at` is recalculated as `current_time + extension`.

---

##### Challenge 38: Airline Seat Allocation Confirms Tickets Beyond Flight Capacity
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Airport gate agents reported passenger boarding denial emergencies after holiday flash sales allowed more passengers to purchase tickets than seats available.

### Bug Report
When only 1 seat remains on Flight 100, two simultaneous customer booking requests read available seats as 1, decrement stock, and confirm both tickets, overselling the flight.

### Steps to Reproduce
1. Initialize inventory with 1 seat: `inv = {"FL100": 1}`.
2. User A and User B concurrently attempt to book 1 seat each.
3. Observe both allocations return `True`, leaving negative seats or unseated passengers.

### Expected Behaviour
Seat reservations must conditionally allocate stock: only decrement and return `True` if available seats satisfy the request; otherwise return `False`.

### Actual Behaviour
Check-then-act window allows concurrent requests to read stale available counts and oversell.

### Starter Files
`inventory_allocator.py` - Allocates seats from flight inventory batches.

### Task
Implement atomic conditional reservation in `inventory_allocator.py` to prevent capacity overselling.

### Acceptance Criteria
1. The first reservation for the last available seat succeeds and decrements inventory to 0.
2. Subsequent reservations return `False` and do not alter depleted inventory.
3. Requests with insufficient seats leave stock unchanged.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Concurrency bugs in reservation engines arise when reading state and writing state are separated in time.
- **Level 2 (Directional)**: Examine `reserve_seats` in `inventory_allocator.py` to ensure the balance check is validated before mutation.
- **Level 3 (Root Cause)**: Ensure the stock check `inventory.get(flight_id, 0) >= requested_seats` evaluates the live state immediately prior to deduction.

---

##### Challenge 39: Cache-Aside Strategy Restores Stale Bio After Database Update
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Users changing their public profile bio noticed that after refreshing the page, their old bio reverted and remained stuck in production caches for hours.

### Bug Report
When an update runs, it purges the cache before updating the database. A concurrent reader misses cache, reads the still-uncommitted old database value, and repopulates the cache with stale data.

### Steps to Reproduce
1. Call `update_user_bio(db, cache, "u1", "New Bio")`.
2. Observe operation sequence in trace logs.
3. Notice `CACHE_DELETE` is executed prior to `DB_WRITE`.

### Expected Behaviour
In the standard Cache-Aside pattern, the database write must commit first, and cache invalidation must be triggered afterward (`["DB_WRITE", "CACHE_DELETE"]`).

### Actual Behaviour
The code deletes the cache key prior to persisting the new database value.

### Starter Files
`cache_aside.py` - Synchronizes database writes with key-value cache eviction.

### Task
Reorder operations in `update_user_bio` in `cache_aside.py` to follow the standard Cache-Aside invalidation sequence.

### Acceptance Criteria
1. Database mutation executes before cache eviction.
2. Returns `True` upon successful completion.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In cache-aside architecture, deleting cache before database updates creates a window for readers to cache stale database rows.
- **Level 2 (Directional)**: Inspect the execution order in `update_user_bio` in `cache_aside.py`.
- **Level 3 (Root Cause)**: Swap the statements: write to `db[user_id] = new_bio` first, and call `cache.delete(...)` immediately following the write.

---

##### Challenge 40: Delayed Worker Task Releases Unrelated Lock Held by New Owner
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Multiple background analytics workers started executing simultaneously, corrupting data tables despite an explicit mutual-exclusion distributed lock.

### Bug Report
Worker A acquired a 10s lock. Worker A experienced a 12s GC pause. The lock expired and Worker B acquired it. Worker A resumed and called `release_lock`, inadvertently deleting Worker B's lock!

### Steps to Reproduce
1. Lock is currently held by `"owner_B"`.
2. Worker A calls `release_lock(locks, "report_lock", "owner_A")`.
3. Observe lock is deleted, allowing Worker C to acquire it concurrently with Worker B.

### Expected Behaviour
`release_lock` must only delete the lock key if the stored owner token exactly matches the caller's `owner_token`.

### Actual Behaviour
The release function deletes the lock key unconditionally as long as the key exists in storage.

### Starter Files
`distributed_lock.py` - Implements token-validated distributed lock acquisition and release.

### Task
Add token ownership verification in `release_lock` in `distributed_lock.py`.

### Acceptance Criteria
1. Releasing with a mismatched token returns `False` and leaves the lock intact.
2. Releasing with the matching owner token deletes the lock and returns `True`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Distributed locks require fencing tokens: a client must prove it is the current legitimate owner before releasing a lock.
- **Level 2 (Directional)**: Check what condition is evaluated before `del lock_storage[lock_key]` in `distributed_lock.py`.
- **Level 3 (Root Cause)**: Verify that `lock_storage.get(lock_key) == owner_token` before deleting the key and returning `True`.

---

##### Challenge 41: Synchronized Retries Trigger Thundering Herd Request Storm
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
When a payment cluster recovered from a brief 2-second blip, tens of thousands of client devices retried at the exact same second, immediately knocking the servers offline again.

### Bug Report
The retry formula uses deterministic linear backoff (`base_delay * attempt`). Because thousands of clients retry at the exact same delay intervals, they create catastrophic synchronized traffic waves (thundering herd).

### Steps to Reproduce
1. Calculate delay for attempt 3 with `base_delay=2, max_delay=60, jitter=0`.
2. Linear formula returns `2 * 3 = 6` seconds.
3. Observe lack of exponential expansion (expected `2 * (2^3) = 16` seconds).

### Expected Behaviour
Retries must grow exponentially according to `min(max_delay, base_delay * (2 ** attempt)) + jitter` to spread load and give servers breathing room to recover.

### Actual Behaviour
The delay calculation scales linearly without exponential growth.

### Starter Files
`backoff_client.py` - Calculates backoff wait duration for failed network requests.

### Task
Implement truncated exponential backoff in `calculate_backoff` in `backoff_client.py`.

### Acceptance Criteria
1. Delays scale exponentially with attempt number: `base_delay * (2 ** attempt)`.
2. Delays are capped at `max_delay`.
3. Jitter offsets are added to the final delay.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Resilient distributed systems use exponential backoff rather than linear backoff to prevent thundering herd spikes.
- **Level 2 (Directional)**: Examine the multiplier applied to `base_delay` in `calculate_backoff` in `backoff_client.py`.
- **Level 3 (Root Cause)**: Replace the linear multiplication with power of two exponentiation: `base_delay * (2 ** attempt)`.

---

##### Challenge 42: Simultaneous Report Generations Produce Interleaved CSV Output
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Financial compliance officers discovered that nightly ledger export files were corrupted with split rows and mangled headers due to concurrent report tasks writing directly to the target file.

### Bug Report
Writing directly to the target file path without temporary file staging allows concurrent or partial writes to overwrite or interleave data in destination files.

### Steps to Reproduce
1. Execute `write_report_safely(file_system, "report.csv", "DATA", pid=123)`.
2. Inspect file system operations.
3. Observe that no `.tmp.` staging file was utilized.

### Expected Behaviour
Reports must be written to an isolated temporary file path (`f"{dest_path}.tmp.{pid}"`) first, and moved/renamed atomically to the destination path upon completion.

### Actual Behaviour
The export routine writes directly to the shared destination path rather than staging chunks into an isolated temporary workspace.

### Starter Files
`report_writer.py` - File persistence helper for generated regulatory exports.

### Task
Implement temporary file staging and atomic replacement in `report_writer.py`.

### Acceptance Criteria
1. Report content is staged to a temporary file containing `.tmp.{pid}`.
2. The staged content is atomically moved to `dest_path`.
3. Returns `dest_path` upon completion.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Atomic file replacement prevents partial writes and corruption by writing to a hidden temporary file before renaming.
- **Level 2 (Directional)**: Look at how `dest_path` is written directly into `file_system` in `report_writer.py`.
- **Level 3 (Root Cause)**: Write first to `f"{dest_path}.tmp.{pid}"`, then assign `file_system[dest_path] = file_system.pop(temp_path)`.

---

##### Challenge 43: Concurrent Resource Allocation Leads to Worker Thread Deadlock
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
High-performance computing cluster nodes froze completely when running distributed machine learning training jobs that allocate both GPUs and fast NVMe storage.

### Bug Report
Worker 1 requests `["NVMe", "GPU"]` while Worker 2 requests `["GPU", "NVMe"]`. Worker 1 locks NVMe and waits for GPU; Worker 2 locks GPU and waits for NVMe, causing a circular deadlock.

### Steps to Reproduce
1. Worker A calls `determine_lock_order(["NVMe", "GPU", "CPU"])`.
2. Worker B calls `determine_lock_order(["CPU", "NVMe", "GPU"])`.
3. Notice returned lock orders differ (`['NVMe', 'GPU', 'CPU']` vs `['CPU', 'NVMe', 'GPU']`), allowing circular lock acquisition.

### Expected Behaviour
Lock acquisition must enforce a strict, global canonical ordering (e.g. alphabetical) regardless of caller parameter order: `["CPU", "GPU", "NVMe"]`.

### Actual Behaviour
The function converts input to a list without sorting, preserving caller-specified arbitrary order.

### Starter Files
`resource_manager.py` - Determines acquisition order for shared hardware resources.

### Task
Ensure consistent canonical resource acquisition ordering in `resource_manager.py`.

### Acceptance Criteria
1. Resource lists are returned in deterministic sorted order regardless of input permutation.
2. Circular wait conditions are prevented.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Coffman's condition for deadlock (circular wait) can be eliminated by enforcing a total ordering on all shared locks.
- **Level 2 (Directional)**: Inspect what `determine_lock_order` returns in `resource_manager.py`.
- **Level 3 (Root Cause)**: Sort the collection before returning: `return sorted(required_resources)`.

---

##### Challenge 44: Security Guard Runs After Modifying User Role Assignment
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
A security audit flagged a critical vulnerability in the administrative identity portal where unprivileged users could escalate their role to Superuser.

### Bug Report
`elevate_user_role` updates the database role record first, and only then executes the authorization check. When unauthorized actors invoke the function, the database role is already modified.

### Steps to Reproduce
1. Target user has `"guest"` role.
2. Guest user submits role promotion to `"admin"` with failing authorization check.
3. Catch the expected `PermissionError`.
4. Inspect `users["guest_user"]`: user has been elevated to `"admin"`.

### Expected Behaviour
Authorization checks must execute before modifying any protected system state. Unauthorized callers must leave database state completely unchanged.

### Actual Behaviour
State mutation precedes access control verification.

### Starter Files
`access_controller.py` - Assigns administrative roles and executes privilege verification.

### Task
Reorder logic in `access_controller.py` so authorization checks guard state mutations.

### Acceptance Criteria
1. Unauthorized actors trigger `PermissionError` and leave target roles unchanged.
2. Authorized actors update target roles successfully.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Security gates must always validate permissions before executing privileged state mutations.
- **Level 2 (Directional)**: Look at the order of operations in `elevate_user_role` in `access_controller.py`.
- **Level 3 (Root Cause)**: Invoke `if not auth_checker(actor): raise PermissionError(...)` before executing `user_db[target] = new_role`.

---

##### Challenge 45: Interrupted Database Migration Leaves No Resumption Checkpoint
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
During a major database platform upgrade, a network timeout halted the migration job at record 500,000, forcing engineers to start over from record 1 due to lack of checkpoints.

### Bug Report
`migrate_batch` transfers records into the destination database, but fails to record the progress cursor or highest record ID in `checkpoint_store`.

### Steps to Reproduce
1. Ingest batch `[{"id": 10}, {"id": 20}, {"id": 30}]`.
2. Run `migrate_batch(db, cp, batch)`.
3. Check `cp.get("last_id")`.
4. Observe that `cp` is completely empty.

### Expected Behaviour
After persisting a batch of records, the migration runner must record the last processed record's ID into `checkpoint_store["last_id"]`.

### Actual Behaviour
No checkpoint metadata is recorded during batch commits.

### Starter Files
`migration_runner.py` - Migrates records in batches while updating checkpoint state.

### Task
Add checkpoint tracking in `migrate_batch` in `migration_runner.py`.

### Acceptance Criteria
1. The highest record ID in the batch is stored in `checkpoint_store["last_id"]`.
2. Records are persisted to `destination_db`.
3. Returns `True` upon batch completion.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Large-scale data pipelines require persistent checkpoints to enable crash recovery without duplicating work.
- **Level 2 (Directional)**: Examine what `migrate_batch` writes to `checkpoint_store` in `migration_runner.py`.
- **Level 3 (Root Cause)**: After writing records, update `checkpoint_store["last_id"] = batch[-1]["id"]` if the batch contains records.

---

##### Challenge 46: Entity Event Stream Reorders Sequential Account Actions
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
E-commerce customers reported that cancelled orders were still being billed and shipped because order cancellation events processed before creation events.

### Bug Report
The event streaming partitioner assigns incoming events to random shards. As a result, `ORDER_CANCELLED` and `ORDER_CREATED` for the same order route to different worker threads, executing out of sequence.

### Steps to Reproduce
1. Emit creation event `e1` for order `"ORD_99"`.
2. Emit cancellation event `e2` for order `"ORD_99"`.
3. Call `assign_event_shard` on both events.
4. Observe that events for the same order route to different shards.

### Expected Behaviour
Events with identical `entity_id` values must deterministically route to the exact same shard to preserve strict FIFO processing.

### Actual Behaviour
The partitioner distributes incoming events across shards randomly without keying off the entity identifier.

### Starter Files
`event_stream.py` - Assigns incoming event records to processing shards.

### Task
Implement deterministic entity-based hash partitioning in `assign_event_shard` in `event_stream.py`.

### Acceptance Criteria
1. Events with identical `entity_id` consistently route to the exact same shard.
2. Shard numbers are valid integers in range `[0, num_shards - 1]`.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Event streaming platforms preserve per-entity order by routing messages with matching partition keys to the same partition.
- **Level 2 (Directional)**: Notice that `assign_event_shard` uses `random.randint` in `event_stream.py`.
- **Level 3 (Root Cause)**: Use hash partitioning: derive the shard by computing `abs(hash(event["entity_id"])) % num_shards`.

---

##### Challenge 47: Travel Booking Saga Leaves Orphaned Flight After Rental Failure
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Travelers booking vacation packages were charged for standalone flights when their rental car reservation failed, leaving them stranded without a full trip.

### Bug Report
When Step 3 (Car Rental) of a 3-step saga fails, the coordinator only rolls back Step 2 (Hotel), completely neglecting to roll back Step 1 (Flight).

### Steps to Reproduce
1. Execute a saga with steps `[Flight, Hotel, Car]`, where Car fails.
2. Observe rollback actions executed.
3. Notice that `Hotel` is rolled back, but `Flight` remains confirmed and active.

### Expected Behaviour
When any step in a distributed saga fails, the coordinator must roll back all completed steps in reverse order (`["Hotel", "Flight"]`).

### Actual Behaviour
The failure compensation handler only reverts the single most recent action rather than winding down all previously completed transactions in reverse order.

### Starter Files
`saga_coordinator.py` - Orchestrates multi-service transactions and compensating actions.

### Task
Implement complete backward compensation in `saga_coordinator.py` when an execution step fails.

### Acceptance Criteria
1. All completed steps are rolled back in reverse order upon an exception.
2. The triggering exception is re-raised.
3. Fully successful sagas return `True`.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: The Saga pattern ensures eventual consistency by executing compensating transactions for every step completed prior to failure.
- **Level 2 (Directional)**: Inspect what happens inside the `except Exception:` block in `saga_coordinator.py`.
- **Level 3 (Root Cause)**: Iterate through all completed steps in reverse: `for s in reversed(completed): s.rollback()` before re-raising.

---

##### Challenge 48: Multi-Gigabyte Stream Parsing Causes Out-of-Memory Container Crash
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Log monitoring Kubernetes pods were killed by the kernel with `OOMKilled` (out of memory) whenever ingesting large server access log streams.

### Bug Report
The parser accumulates all stream chunks into a list (`all_chunks.append(chunk)`), consuming gigabytes of memory rather than yielding lines on the fly.

### Steps to Reproduce
1. Feed streaming chunks `["line1\nli", "ne2\n", "line3\n"]` into `parse_stream_chunks`.
2. Inspect memory retention.
3. Observe all incoming bytes are held in memory simultaneously.

### Expected Behaviour
The parser must operate as a streaming generator, buffering only incomplete fragments and yielding complete lines as they arrive.

### Actual Behaviour
Full stream retention in an accumulating list.

### Starter Files
`stream_parser.py` - Tokenizes continuous incoming byte chunks into individual log lines.

### Task
Refactor `parse_stream_chunks` in `stream_parser.py` into a memory-efficient line generator.

### Acceptance Criteria
1. Complete lines are yielded as generators without buffering prior lines.
2. Split lines across chunk boundaries are properly reassembled.
3. Trailing newline characters are stripped.

### Constraints
- Slicing and pagination operations must include all items up to the final boundary record.
- Record transformations and exports must preserve embedded delimiters, quotation marks, and line breaks.
- Nested configuration merges must preserve non-conflicting sibling properties.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Streaming parsers should consume constant memory by yielding tokens as soon as delimiters are encountered.
- **Level 2 (Directional)**: Avoid keeping an accumulating list of all previous chunks in `stream_parser.py`.
- **Level 3 (Root Cause)**: Maintain a single `buffer` string; find `\n`, yield lines, and slice `buffer = buffer[idx+1:]`.

---

##### Challenge 49: Account Profile Update Leaves Partially Modified State on Validation Failure
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Security admins reported data inconsistencies where user profiles had updated email addresses but old phone numbers after validation failed during profile submission.

### Bug Report
When a user updates email and phone together, `update_account` modifies `profile["email"]` first. When phone validation fails, the email change remains applied in memory.

### Steps to Reproduce
1. Start with profile `{"email": "old@test.com", "phone": "1111111111"}`.
2. Submit update with valid email `"new@test.com"` and invalid phone `"bad_phone"`.
3. Catch the expected `ValueError`.
4. Inspect `prof["email"]`: observed that email was changed to `"new@test.com"`.

### Expected Behaviour
All input fields must be validated completely before mutating any profile state. If validation fails, profile attributes must remain completely untouched.

### Actual Behaviour
Premature partial mutation applies email changes prior to validating phone numbers.

### Starter Files
`account_service.py` - Updates user account profile attributes.

### Task
Implement pre-validation in `update_account` in `account_service.py` to prevent partial state mutations.

### Acceptance Criteria
1. If phone validation fails, the email property is not modified.
2. If both fields are valid, both email and phone are updated.
3. Returns `True` on success.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: State updates should be atomic: perform all validation checks upfront before making any modifications.
- **Level 2 (Directional)**: Notice that `profile["email"]` is updated before checking `new_phone` in `account_service.py`.
- **Level 3 (Root Cause)**: Validate both `new_email` and `new_phone` first, and only mutate `profile` once both validations succeed.

---

##### Challenge 50: Ticket Checkout Displaces Active Unexpired Seat Reservations
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `Python`

### Incident Report
Concertgoers complained that while completing payment for reserved front-row tickets, another buyer checked out the same seats, canceling their active reservation.

### Bug Report
When User 1 holds a seat reservation expiring at `t=400`, User 2 requesting the same seat at `t=150` overwrites the reservation owner unconditionally.

### Steps to Reproduce
1. User 1 reserves Seat `"A1"` at `t=100` with `ttl=300` (expires `t=400`).
2. User 2 requests Seat `"A1"` at `t=150`.
3. Notice that User 2 successfully claims the seat, displacing User 1 while their hold was active.

### Expected Behaviour
A seat can only be reserved if it is unreserved OR if its previous reservation has expired (`current_time >= existing["expires_at"]`). Active unexpired holds must reject new buyers (`return False`).

### Actual Behaviour
The function overwrites the seat reservation unconditionally without checking existing holds.

### Starter Files
`seat_reservation.py` - Manages temporary hold allocations for event seating.

### Task
Add unexpired reservation protection in `reserve_seat` in `seat_reservation.py`.

### Acceptance Criteria
1. Active reservations block new buyers from reserving the seat (`return False`).
2. Expired reservations allow new buyers to successfully claim the seat (`return True`).
3. Initial reservation of an empty seat succeeds.

### Constraints
- State mutations must enforce mutual exclusion and atomicity against concurrent check-then-act race conditions.
- Distributed locks and leases must require ownership token validation before releasing resources.
- Multi-step transaction sagas must execute compensating rollback actions in reverse order upon step failure.
- Resource locks must be acquired in deterministic order to eliminate worker deadlock conditions.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Time-based lease reservations must check whether an existing lease is active before allowing re-allocation.
- **Level 2 (Directional)**: Look at whether existing reservation state is evaluated in `reserve_seat` in `seat_reservation.py`.
- **Level 3 (Root Cause)**: Check `existing = reservations.get(seat_id)`. If `existing and current_time < existing["expires_at"]: return False`.

---

### Arena 2: SQL Lab (IDs 51 - 85)

#### Tier: Easy (10 Challenges)

##### Challenge 51: Marketing Contact Export Omits Customers With Unset Preferences
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Marketing operations reported that nearly half of their customer contact list vanished from automated email campaign exports.

### Bug Report
Customers whose opt-out status has never been explicitly toggled (stored as `NULL` in the database) are completely omitted from the contact export when using direct inequality comparison.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice only customers with explicit `opt_out = 0` are returned.
3. Customers with `opt_out IS NULL` are omitted.

### Expected Behaviour
The query must return all customers who have not explicitly chosen to opt out (`opt_out = 0` or `opt_out IS NULL`).

### Actual Behaviour
In SQL three-valued logic, `NULL != 1` evaluates to `UNKNOWN` rather than `TRUE`, excluding all customers with unset preferences.

### Starter Files
`schema.sql` - Database table schema and test records.
`query.sql` - Outbound marketing contact extraction query.

### Task
Update `query.sql` so that customers with unset preferences (`NULL`) are included alongside explicit non-opt-out accounts.

### Acceptance Criteria
1. Customers with `opt_out = 0` are included.
2. Customers with `opt_out IS NULL` are included.
3. Customers with `opt_out = 1` are excluded.
4. Output columns are `id`, `name`, `email` ordered by `id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In SQL three-valued logic, comparing NULL against any value using `=` or `!=` evaluates to UNKNOWN rather than TRUE.
- **Level 2 (Directional)**: Examine the WHERE clause in `query.sql` and consider how unset database values behave under standard inequality.
- **Level 3 (Root Cause)**: Use an explicit `IS NULL` check (e.g. `opt_out = 0 OR opt_out IS NULL`) or `COALESCE` to handle missing values.

---

##### Challenge 52: Monthly Revenue Report Truncates Final Day Orders
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Finance reported an accounting discrepancy where October revenue was under-reported by $15,000 compared to merchant bank deposits.

### Bug Report
Orders placed on the afternoon of October 31st (e.g. at 18:30) are excluded from the report because date-only string comparison stops at midnight.

### Steps to Reproduce
1. Ingest an order placed on `'2026-10-31 18:30:00'`.
2. Run `SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date BETWEEN '2026-10-01' AND '2026-10-31';`.
3. Observe the October 31st evening order is omitted from the sum.

### Expected Behaviour
All orders placed during the calendar month of October 2026 (including through 23:59:59 on October 31st) must be included.

### Actual Behaviour
The `BETWEEN` clause with `'2026-10-31'` casts to `'2026-10-31 00:00:00'`, cutting off all transactions later that day.

### Starter Files
`schema.sql` - Orders table definition with timestamped transaction entries.
`query.sql` - Monthly revenue aggregation query.

### Task
Update `query.sql` to capture all transactions occurring up to the start of the next calendar month.

### Acceptance Criteria
1. Transactions from the first day through the entire final day of October are summed.
2. Orders from November 1st are excluded.
3. The result column is aliased as `total_revenue`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Using `BETWEEN` on datetime columns with date-only literals truncates the end date to midnight (00:00:00).
- **Level 2 (Directional)**: Consider how half-open intervals (`>= start` and `< next_period_start`) cleanly capture full time spans.
- **Level 3 (Root Cause)**: Filter with `order_date >= '2026-10-01' AND order_date < '2026-11-01'` to capture all timestamps throughout October 31st.

---

##### Challenge 53: Public Storefront Search Displays Obsolete Archived Products
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Store managers reported that customers were purchasing discontinued items that had been archived years ago, while current catalog items were missing from search.

### Bug Report
The product search query filters for `status = 'archived'` rather than active inventory, showing obsolete items on the public storefront.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Inspect returned items.
3. Observe only archived items are returned.

### Expected Behaviour
Filter exclusively for currently available products where `status = 'active'`, ordered alphabetically by product name.

### Actual Behaviour
The query filters for archived status instead of targeting live inventory items.

### Starter Files
`schema.sql` - Products table containing status flags.
`query.sql` - Public catalog search query.

### Task
Update `query.sql` to filter for active products and order them alphabetically by name.

### Acceptance Criteria
1. Only products with `status = 'active'` are returned.
2. Results are sorted in ascending alphabetical order by `name`.
3. Output columns are `id`, `name`, `price`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Database status flags distinguish between obsolete records and active inventory.
- **Level 2 (Directional)**: Examine the literal string checked in the WHERE clause of `query.sql`.
- **Level 3 (Root Cause)**: Update the predicate to `WHERE status = 'active'`.

---

##### Challenge 54: User Roster Omits Newly Registered Customers Without Orders
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
The customer onboarding team noticed that new users who registered but had not yet made a purchase were completely missing from onboarding follow-up reports.

### Bug Report
An `INNER JOIN` between `customers` and `orders` drops customer rows that have no matching records in the orders table.

### Steps to Reproduce
1. Register customer "Charlie" with 0 orders.
2. Run `query.sql`.
3. Observe "Charlie" is omitted from the result set.

### Expected Behaviour
Every customer must be listed in the report. For customers who haven't ordered yet, `order_id` should show `NULL`.

### Actual Behaviour
The query joins customer accounts with an inner join that drops registered accounts having zero purchase history.

### Starter Files
`schema.sql` - Definitions for customers and orders tables.
`query.sql` - Customer order association query.

### Task
Modify the join type in `query.sql` so all customers appear in the output regardless of order history.

### Acceptance Criteria
1. All registered customers are preserved in the result set.
2. Unmatched customers display `NULL` for `order_id`.
3. Results are ordered by customer `id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: An INNER JOIN requires matches on both sides of the join condition, omitting unmatched left-table rows.
- **Level 2 (Directional)**: Consider which relational join type preserves all rows from the primary table even when no foreign key match exists.
- **Level 3 (Root Cause)**: Change `INNER JOIN` to `LEFT JOIN` (or `LEFT OUTER JOIN`).

---

##### Challenge 55: Department Bonus Metrics Overstate Average by Excluding Zero Bonus Staff
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Executive HR leadership noticed departmental average bonus metrics were artificially inflated because employees receiving $0 bonuses were excluded from calculations.

### Bug Report
The query filters `WHERE bonus > 0` before computing `AVG(bonus)`. For a department of 2 employees where one received 10% and the other 0%, the query reports an average of 10% instead of 5%.

### Steps to Reproduce
1. Department Engineering has Alice (10% bonus) and Bob (0% bonus).
2. Execute query in `query.sql`.
3. Observe Engineering avg_bonus reports `10.0` instead of `5.0`.

### Expected Behaviour
Calculate the true department average bonus across all employees in each department, counting zero bonuses in the denominator.

### Actual Behaviour
Filtering out non-bonus recipients prior to aggregation skews the departmental average upwards.

### Starter Files
`schema.sql` - Employees table with department and bonus percentage columns.
`query.sql` - Departmental bonus aggregation query.

### Task
Update `query.sql` to compute the true average bonus across all department employees.

### Acceptance Criteria
1. All employees in each department are factored into `avg_bonus`.
2. Results are grouped by `department` and sorted by `department` ascending.
3. Output columns are `department` and `avg_bonus`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Filtering rows in a WHERE clause removes them from consideration before aggregate functions like AVG are computed.
- **Level 2 (Directional)**: Review whether employees receiving zero bonus should be counted in the department average denominator.
- **Level 3 (Root Cause)**: Remove `WHERE bonus > 0` so that all department employees are included in `AVG(bonus)`.

---

##### Challenge 56: Registration Cleanup Report Flags Unique Accounts as Duplicates
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Database administrators alerted that an automated deduplication script flagged every single user account in the system for merge or deletion.

### Bug Report
The duplicate detection query uses `HAVING COUNT(*) >= 1`, which matches every email address that appears at least once, including completely unique emails.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe unique email `"unique@test.com"` is returned in the duplicate list.

### Expected Behaviour
Only email addresses that appear more than once (`COUNT(*) > 1`) should be returned as duplicates.

### Actual Behaviour
The threshold `>= 1` captures single-occurrence unique accounts.

### Starter Files
`schema.sql` - User accounts table.
`query.sql` - Duplicate email detection query.

### Task
Update `query.sql` to filter strictly for duplicate email addresses.

### Acceptance Criteria
1. Only emails appearing more than once are returned.
2. Non-duplicate emails with only one occurrence are excluded.
3. Output columns are `email` and `count`, ordered by `email`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: A duplicate item in a relational table is defined by having a frequency count strictly greater than one.
- **Level 2 (Directional)**: Inspect the comparison operator in the `HAVING` clause of `query.sql`.
- **Level 3 (Root Cause)**: Change `COUNT(*) >= 1` to `COUNT(*) > 1`.

---

##### Challenge 57: Customer Invoice Tax Sum Truncates Fractional Pennies
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Billing accounting noted that customer sales tax invoices showed whole dollar amounts (e.g. $2.00) instead of exact cents ($2.95), failing tax audit reconciliation.

### Bug Report
The SQL `ROUND()` function is called with only one argument (`ROUND(SUM(...))`), rounding the tax total to the nearest whole integer dollar rather than 2 decimal places.

### Steps to Reproduce
1. Ingest line items totaling tax $2.94525.
2. Execute query in `query.sql`.
3. Output returns whole integer `3.0` instead of `2.95`.

### Expected Behaviour
Monetary totals must be rounded to exactly 2 decimal places: `ROUND(SUM(subtotal * tax_rate), 2) AS total_tax`.

### Actual Behaviour
Omitting the decimal places parameter defaults to 0 decimal places.

### Starter Files
`schema.sql` - Line items table with subtotal and tax rate columns.
`query.sql` - Invoicing tax calculation query.

### Task
Update `query.sql` to round tax totals to 2 decimal places.

### Acceptance Criteria
1. Total tax is rounded to 2 decimal places.
2. The column is aliased as `total_tax`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In standard SQL, `ROUND(value)` without a second parameter rounds to the nearest integer.
- **Level 2 (Directional)**: Pass the desired scale as a second argument to `ROUND()` for monetary precision.
- **Level 3 (Root Cause)**: Change to `ROUND(SUM(subtotal * tax_rate), 2)`.

---

##### Challenge 58: Executive Sales Metric Dashboard Includes Cancelled Transactions
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Executive leadership noticed daily Gross Merchandise Value (GMV) charts were inflated because cancelled and refunded orders were being summed as valid revenue.

### Bug Report
The revenue calculation sums the `amount` column across all orders unconditionally without filtering by order status.

### Steps to Reproduce
1. Database contains orders with status `'completed'` and `'cancelled'`.
2. Run `SELECT SUM(amount) AS completed_gmv FROM orders;`.
3. Observe cancelled orders are included in the sum.

### Expected Behaviour
Only fulfilled, completed orders (`status = 'completed'`) should contribute to net GMV revenue.

### Actual Behaviour
The aggregation sums every order record in the table without checking whether the transaction status is completed.

### Starter Files
`schema.sql` - Orders table with amount and status attributes.
`query.sql` - Completed GMV aggregation query.

### Task
Add status filtering to `query.sql` so only completed orders are summed.

### Acceptance Criteria
1. Only orders with `status = 'completed'` are summed.
2. Result column is aliased as `completed_gmv`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Financial metrics must filter on status attributes to exclude cancelled, refunded, or fraudulent transactions.
- **Level 2 (Directional)**: Notice that `query.sql` currently has no `WHERE` clause.
- **Level 3 (Root Cause)**: Add `WHERE status = 'completed'` to the query.

---

##### Challenge 59: Emergency Task Dispatch Ordering Misplaces Double-Digit Urgency Levels
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Emergency dispatch technicians noticed that priority level 10 tasks were dispatched before priority level 2 tasks because priority numbers were ordered as text strings.

### Bug Report
The `priority_level` column is stored as `VARCHAR`. Sorting with `ORDER BY priority_level ASC` orders lexicographically as `'10', '100', '2', '20'`, rather than numerically.

### Steps to Reproduce
1. Tasks have priority levels `'10'`, `'2'`, `'100'`, `'20'`.
2. Run `query.sql`.
3. Notice `'10'` appears before `'2'`.

### Expected Behaviour
Tasks must be ordered according to their numerical integer value: `'2', '10', '20', '100'`.

### Actual Behaviour
Lexicographical string sorting compares ASCII character codes left-to-right.

### Starter Files
`schema.sql` - Tasks table with string-typed priority levels.
`query.sql` - Priority task retrieval query.

### Task
Update `query.sql` so that priority values are sorted numerically rather than in lexicographical character order.

### Acceptance Criteria
1. Tasks are ordered by numerical priority level in ascending order.
2. Output columns are `id`, `name`, `priority_level`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: String columns order alphabetically rather than numerically, placing '10' before '2'.
- **Level 2 (Directional)**: SQL allows casting column data types inside the ORDER BY clause.
- **Level 3 (Root Cause)**: Use `CAST(priority_level AS INTEGER)` in the `ORDER BY` clause.

---

##### Challenge 60: Best-Selling Product Card Displays Least-Ordered Inventory Item
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `SQL`

### Incident Report
Marketing operations reported that the homepage "Item of the Week" promotional card showcased a slow-moving item with only 1 sale instead of the top seller with 500 sales.

### Bug Report
The top seller query uses `ORDER BY total_sold ASC LIMIT 1`, which sorts ascending and retrieves the minimum seller rather than the maximum.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Inspect returned item.
3. Observe "Slow Mover" (1 unit) is returned instead of "Hot Item" (500 units).

### Expected Behaviour
Retrieve the single top-selling product by ordering `total_sold` descending (`DESC`) with `LIMIT 1`.

### Actual Behaviour
Ascending sort order returns the lowest sold item.

### Starter Files
`schema.sql` - Product sales table tracking units sold.
`query.sql` - Top seller extraction query.

### Task
Update `query.sql` to sort descending and return the top-selling product.

### Acceptance Criteria
1. The product with highest `total_sold` is returned.
2. The query limits output to 1 row.
3. Output columns are `id`, `name`, `total_sold`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Ascending order (`ASC`) orders from lowest to highest, while finding top performers requires ordering highest to lowest.
- **Level 2 (Directional)**: Examine the sorting direction specified in `query.sql`.
- **Level 3 (Root Cause)**: Change `ORDER BY total_sold ASC` to `ORDER BY total_sold DESC`.

---

#### Tier: Medium (15 Challenges)

##### Challenge 61: Customer Revenue Report Multiplied by Order Line Items Join
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Finance leadership noticed customer total spending figures were inflated by up to 300% on executive dashboards compared to actual bank deposits.

### Bug Report
An order of $100 containing 3 line items counts as $300 in total revenue because joining `orders` with `order_items` duplicates order rows before summing `total_amount`.

### Steps to Reproduce
1. Customer has 1 order of $100 with 2 items in `order_items`.
2. Run `query.sql`.
3. Notice reported revenue is $200 instead of $100.

### Expected Behaviour
Customer revenue must reflect the actual sum of `total_amount` recorded in the `orders` table without cartesian multiplication from joined line item records.

### Actual Behaviour
The query joins `order_items`, multiplying each order row by the count of items purchased.

### Starter Files
`schema.sql` - Orders and order_items table definitions.
`query.sql` - Customer revenue aggregation query.

### Task
Refactor `query.sql` to calculate true total revenue per customer from the `orders` table directly.

### Acceptance Criteria
1. Revenue reflects the exact sum of order amounts per customer.
2. Multiple items per order do not duplicate revenue.
3. Results are grouped by `customer_id` and ordered by `customer_id` ascending.
4. Output columns are `customer_id` and `revenue`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Joining a one-to-many relationship multiplies rows in the parent table before aggregation occurs.
- **Level 2 (Directional)**: Examine whether `order_items` is actually needed if `orders` already contains `total_amount`.
- **Level 3 (Root Cause)**: Query `orders` directly without joining `order_items`: `SELECT customer_id, SUM(total_amount) AS revenue FROM orders GROUP BY customer_id ORDER BY customer_id;`.

---

##### Challenge 62: Average Order Value Metrics Distorted by Day-Level Aggregation
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Marketing analytics reported that VIP customer tier thresholds were miscalculated because Average Order Value (AOV) was reporting sums instead of true averages.

### Bug Report
The AOV query uses `SUM(amount)` instead of `AVG(amount)` across customer orders, conflating total spending with average basket size.

### Steps to Reproduce
1. Customer has 3 orders: $100, $20, and $30 (true average: $50).
2. Execute query in `query.sql`.
3. Observed `aov` is $150 instead of $50.

### Expected Behaviour
Calculate true average order value as `ROUND(AVG(amount), 2)` grouped by `customer_id`.

### Actual Behaviour
The query computes `SUM(amount)`, reporting lifetime total spend rather than average order size.

### Starter Files
`schema.sql` - Orders table tracking transaction amounts.
`query.sql` - Customer AOV calculation query.

### Task
Update `query.sql` to compute the true average order value rounded to 2 decimal places.

### Acceptance Criteria
1. Average order value is computed using `AVG(amount)`.
2. Output is rounded to 2 decimal places.
3. Grouped by `customer_id` and ordered by `customer_id` ascending.
4. Output columns are `customer_id` and `aov`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Average Order Value measures the mean transaction size per customer rather than cumulative total spend.
- **Level 2 (Directional)**: Check the aggregate function used in the SELECT clause of `query.sql`.
- **Level 3 (Root Cause)**: Replace `SUM(amount)` with `ROUND(AVG(amount), 2) AS aov`.

---

##### Challenge 63: Audit Log Pagination Displays Duplicate Events Across Pages
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Security compliance auditors noted that while paginating through security event logs, duplicate log entries appeared across consecutive pages.

### Bug Report
Multiple audit logs share identical timestamps. Because sorting relies solely on `created_at DESC`, row ordering among ties is non-deterministic, causing rows to shift between pagination windows.

### Steps to Reproduce
1. Fetch page 1 with `LIMIT 2 OFFSET 0` ordered by `created_at DESC`.
2. Fetch page 2 with `LIMIT 2 OFFSET 2` ordered by `created_at DESC`.
3. Notice that identical events shift positions and repeat across pages.

### Expected Behaviour
Ordering must include a secondary unique tie-breaker (`id ASC`) so that relative positions among identical timestamps remain stable.

### Actual Behaviour
Sorts only by `created_at DESC`, leaving tie-breaking non-deterministic.

### Starter Files
`schema.sql` - Audit logs table with timestamped event entries.
`query.sql` - Paginated audit log retrieval query.

### Task
Update `query.sql` to ensure deterministic sorting across pagination offsets.

### Acceptance Criteria
1. Events are ordered primarily by `created_at DESC`, secondarily by `id ASC`.
2. Window offsets remain stable without row duplication.
3. Output columns are `id`, `event`, `created_at`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Relational databases do not guarantee deterministic order for duplicate sort keys unless a unique column is included in the ORDER BY.
- **Level 2 (Directional)**: Examine the ORDER BY clause in `query.sql`.
- **Level 3 (Root Cause)**: Append `, id ASC` to `ORDER BY created_at DESC` to guarantee stable pagination.

---

##### Challenge 64: Regional Sales Leaderboard Ranks Executives Across Mixed Regions
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Regional sales directors complained that quarterly performance medals were misallocated because account executives were ranked globally rather than within their assigned region.

### Bug Report
The ranking window function `RANK() OVER (ORDER BY revenue DESC)` omits regional partitioning, comparing EMEA reps against APAC reps.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Inspect `regional_rank` for EMEA reps.
3. Observe ranks 1 through 4 are assigned globally instead of resetting to 1 per region.

### Expected Behaviour
Each sales executive must be ranked within their specific regional group using `RANK() OVER (PARTITION BY region ORDER BY revenue DESC)`.

### Actual Behaviour
The window function ranks all sales reps globally across the entire table.

### Starter Files
`schema.sql` - Sales reps table with region and closed revenue.
`query.sql` - Leaderboard ranking window query.

### Task
Add regional partitioning to the window function in `query.sql`.

### Acceptance Criteria
1. The top revenue generator in each region is awarded rank 1.
2. Ranks are partitioned by `region`.
3. Results are ordered by `region` and `regional_rank` ascending.
4. Output columns are `id`, `name`, `region`, `revenue`, `regional_rank`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Window functions require a PARTITION BY clause to break down calculations into distinct subset groupings.
- **Level 2 (Directional)**: Look inside the `OVER (...)` clause in `query.sql`.
- **Level 3 (Root Cause)**: Insert `PARTITION BY region` before `ORDER BY revenue DESC`.

---

##### Challenge 65: Monthly Payment Grouping Misattributes Midnight UTC Renewals
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Billing reconciliation showed that recurring subscription revenue was misclassified because monthly groupings were derived using fragile string slicing instead of datetime formatters.

### Bug Report
The query extracts month via `substr(payment_date, 6, 2)`, producing two-digit month numbers without year prefixes, which merges September 2025 and September 2026 into the same bucket.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe grouping key is `'09'` rather than `'2026-09'`.

### Expected Behaviour
Group recurring revenue using standardized year-month ISO formatting: `strftime('%Y-%m', payment_date) AS month`.

### Actual Behaviour
The query uses `substr(payment_date, 6, 2)`, dropping the calendar year.

### Starter Files
`schema.sql` - Payments table with ISO timestamp strings.
`query.sql` - Monthly revenue aggregation query.

### Task
Update `query.sql` to group and order payments by full `YYYY-MM` month strings.

### Acceptance Criteria
1. Months are formatted as `YYYY-MM` using `strftime('%Y-%m', payment_date)`.
2. Payments are grouped and ordered by `month` ascending.
3. Output columns are `month` and `total`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Deriving date buckets via manual string substrings breaks across year boundaries.
- **Level 2 (Directional)**: SQL includes built-in datetime formatting functions like `strftime` for extracting date components.
- **Level 3 (Root Cause)**: Use `strftime('%Y-%m', payment_date) AS month` and group by month.

---

##### Challenge 66: Free Tier Accounts Filtered Out of Customer Directory by WHERE Clause
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Customer support agents reported that free-tier users were missing from the administrative directory, preventing staff from looking up user profiles.

### Bug Report
The query joins `users` to `subscriptions` using `LEFT JOIN`, but includes `WHERE s.status = 'active'`. For users without subscriptions, `s.status` is `NULL`. The WHERE clause filters out NULL, converting the LEFT JOIN into an accidental INNER JOIN!

### Steps to Reproduce
1. User "Bob" has no active subscription.
2. Run `query.sql`.
3. Notice Bob is completely absent from the results.

### Expected Behaviour
All users must appear in the directory. Users without active subscriptions should display `NULL` for `plan_name`.

### Actual Behaviour
Filtering subscription attributes in the query predicate drops churned and free-tier accounts from the output.

### Starter Files
`schema.sql` - Users and subscriptions tables.
`query.sql` - Customer directory query.

### Task
Update the subscription join in `query.sql` so active subscription attributes are attached without filtering out non-paying users.

### Acceptance Criteria
1. All users appear in the output.
2. Users without an active plan show `plan_name: NULL`.
3. Results are ordered by user `id` ascending.
4. Output columns are `id`, `name`, `plan_name`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Placing a filter on the right table in a WHERE clause filters out NULL rows produced by a LEFT JOIN, turning it into an INNER JOIN.
- **Level 2 (Directional)**: Conditions placed in the ON clause dictate what rows are joined, whereas WHERE filters the entire combined result set.
- **Level 3 (Root Cause)**: Move `AND s.status = 'active'` into the `ON` clause and remove the `WHERE` clause.

---

##### Challenge 67: Unreserved Warehouse Inventory Displays NULL Availability
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
E-commerce inventory feeds reported in-stock keyboards as unavailable because products with zero reservations showed `NULL` available units.

### Bug Report
When an item has no reserved stock (`reserved_stock = NULL`), calculating `physical_stock - reserved_stock` produces `NULL` because arithmetic operations on NULL yield NULL.

### Steps to Reproduce
1. Product "Keyboard" has `physical_stock = 25` and `reserved_stock = NULL`.
2. Run `query.sql`.
3. Notice `available_stock` evaluates to `NULL` instead of 25.

### Expected Behaviour
If `reserved_stock` is unset or `NULL`, treat it as 0 so that `available_stock` equals full physical inventory.

### Actual Behaviour
Unchecked NULL arithmetic causes availability to evaluate to NULL.

### Starter Files
`schema.sql` - Inventory table tracking physical and reserved stock quantities.
`query.sql` - Stock availability calculation query.

### Task
Use `COALESCE` in `query.sql` to handle unset reserved stock quantities safely.

### Acceptance Criteria
1. Items with NULL reservations compute availability as physical stock minus 0.
2. Items with positive reservations subtract accurately.
3. Output columns are `id`, `name`, `available_stock` ordered by `id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In SQL arithmetic expressions, any number operated on with NULL results in NULL (e.g. `25 - NULL = NULL`).
- **Level 2 (Directional)**: Use a null-coalescing function to substitute a default numerical value of zero.
- **Level 3 (Root Cause)**: Wrap `reserved_stock` in `COALESCE(reserved_stock, 0)`.

---

##### Challenge 68: Delivery Success Rate Metric Inflated by Counting Non-Delivered Rows
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Logistics executives questioned warehouse reporting when the shipment dashboard showed a 100% on-time delivery rate despite thousands of returned packages.

### Bug Report
The query calculates delivery totals using `COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`. In SQL, `COUNT()` counts all non-null values—including `0`—counting returned shipments as delivered!

### Steps to Reproduce
1. Table contains 2 delivered and 1 returned shipment.
2. Run `query.sql`.
3. Notice reported `delivered_count` is 3 instead of 2.

### Expected Behaviour
Only shipments with `status = 'delivered'` should be counted toward the delivered total.

### Actual Behaviour
The `COUNT` aggregate counts the `ELSE 0` branch as a non-null row.

### Starter Files
`schema.sql` - Shipments table with delivery statuses.
`query.sql` - Delivery success metrics aggregation query.

### Task
Update conditional aggregation in `query.sql` to accurately tally delivered shipments.

### Acceptance Criteria
1. Delivered count equals 2 for the sample dataset.
2. Returned or non-delivered shipments are not counted.
3. Output column is aliased as `delivered_count`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In SQL, `COUNT(x)` counts every non-null value; numerical 0 is not null and is therefore counted.
- **Level 2 (Directional)**: Consider whether `SUM()` with 1 and 0, or `COUNT()` with NULL as the fallback, is the appropriate aggregation function.
- **Level 3 (Root Cause)**: Change `COUNT(...)` to `SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`.

---

##### Challenge 69: High-Value Customer Loyalty Tier Excludes Frequent Repeat Buyers
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Marketing noticed loyal customers who placed multiple $300 orders were excluded from the $500 VIP loyalty rewards program, while single-order customers qualified.

### Bug Report
The CTE filters individual transactions where `amount >= 500` before grouping by customer. As a result, customers whose cumulative spend exceeds $500 across multiple smaller orders are omitted.

### Steps to Reproduce
1. Customer 101 placed two $300 orders (total $600).
2. Execute query in `query.sql`.
3. Notice Customer 101 is excluded from the high-value list.

### Expected Behaviour
Aggregate total spending across all orders per customer first in the CTE, then filter for customers whose cumulative `total_spent >= 500`.

### Actual Behaviour
The query filters individual transactions prior to customer aggregation.

### Starter Files
`schema.sql` - Orders table tracking transaction amounts.
`query.sql` - Loyalty program qualification CTE query.

### Task
Refactor `query.sql` to aggregate all customer orders before applying the $500 qualification threshold.

### Acceptance Criteria
1. Customers with cumulative spend >= 500 are included.
2. Customers with cumulative spend < 500 are excluded.
3. Results are ordered by `customer_id` ascending.
4. Output columns are `customer_id` and `total_spent`.

### Constraints
- Target Database: SQLite 3.35+ with Recursive Common Table Expression (CTE) support.
- Hierarchical traversal must safely terminate upon reaching maximum designated depth or cycle boundary.
- Tree levels must maintain correct parent-child relationship tracking across levels.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Filtering row values before aggregation prevents calculating the total sum across multiple smaller events.
- **Level 2 (Directional)**: Compute `SUM(amount) AS total_spent` grouped by `customer_id` inside the CTE first.
- **Level 3 (Root Cause)**: Filter `WHERE total_spent >= 500` in the outer query.

---

##### Challenge 70: Multi-Account Fraud Filter Groups Legitimate Users With Missing Phones
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Security alerts erroneously locked thousands of user accounts because an automated multi-account fraud detection query flagged all users with missing phone numbers as a syndicate.

### Bug Report
The duplicate detection query groups by `phone` without checking for NULL. In SQL `GROUP BY`, all `NULL` phone numbers collapse into a single cluster with count > 1, flagging legitimate users as fraud rings.

### Steps to Reproduce
1. Ingest users where multiple records have `phone = NULL`.
2. Run `query.sql`.
3. Notice `NULL` is returned with count = 2 in the duplicate list.

### Expected Behaviour
Exclude `NULL` and empty phone strings from the duplicate scan, returning only genuine non-null duplicate phone numbers.

### Actual Behaviour
The query groups `NULL` records together and counts them as duplicate accounts.

### Starter Files
`schema.sql` - Users table with phone number columns.
`query.sql` - Duplicate phone number fraud detection query.

### Task
Add a pre-aggregation filter in `query.sql` to exclude missing or empty phone numbers.

### Acceptance Criteria
1. Only non-null, non-empty duplicate phone numbers are returned.
2. Users with `phone IS NULL` are excluded from duplicate clusters.
3. Output columns are `phone` and `count`, ordered by `phone`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In SQL GROUP BY operations, NULL values are treated as matching each other and form a single combined group.
- **Level 2 (Directional)**: Filter out missing records before grouping to avoid false duplicate matches.
- **Level 3 (Root Cause)**: Add `WHERE phone IS NOT NULL AND phone != ''` before the `GROUP BY phone` clause.

---

##### Challenge 71: Competition Leaderboard Skips Placing Positions After Tied Scores
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Hackathon judges reported leaderboard placement anomalies where a participant who scored lower than two tied 1st-place finishers was displayed as 2nd place instead of 3rd place.

### Bug Report
The leaderboard query uses `DENSE_RANK()`, which assigns consecutive integers without gaps after ties (e.g. 1, 1, 2), violating Olympic competition ranking rules (1, 1, 3).

### Steps to Reproduce
1. Alice and Bob both score 95 points. Charlie scores 90 points.
2. Execute query in `query.sql`.
3. Notice Charlie receives rank 2 instead of rank 3.

### Expected Behaviour
Use standard competition ranking (`RANK()`) so that tied positions leave subsequent rank gaps (1, 1, 3).

### Actual Behaviour
The ranking function assigns consecutive ranking values without leaving gaps for ties, contradicting competition ranking rules.

### Starter Files
`schema.sql` - Leaderboard scores table.
`query.sql` - Hackathon standings ranking query.

### Task
Update the ranking window function in `query.sql` to apply standard competition ranking.

### Acceptance Criteria
1. Tied participants receive the same rank.
2. Subsequent finishers skip ranks accordingly (e.g. 1, 1, 3).
3. Output columns are `id`, `name`, `score`, `rank` ordered by `rank`, `id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: DENSE_RANK leaves no gaps after ties, whereas standard competition ranking (RANK) skips ranks corresponding to tied entries.
- **Level 2 (Directional)**: Examine the window function name used in `query.sql`.
- **Level 3 (Root Cause)**: Replace `DENSE_RANK()` with `RANK()`.

---

##### Challenge 72: Product Catalog Crashes When Category Discounts Return Multiple Rows
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Storefront API monitors raised 500 error alerts on category pages whenever merchandising configured more than one promotional coupon for the tech department.

### Bug Report
The query uses scalar comparison `WHERE discount_id = (SELECT id FROM discounts WHERE category = 'tech')`. When multiple coupons exist for `'tech'`, the database throws `subquery returns more than 1 row`.

### Steps to Reproduce
1. Two discount records exist for category `'tech'`.
2. Run `query.sql`.
3. Database engine raises an error due to scalar equality comparison against multi-row subquery.

### Expected Behaviour
Use set-membership predicate `IN` so that any products matching any active category discount are returned without errors.

### Actual Behaviour
The scalar equality operator `=` expects exactly one returned value.

### Starter Files
`schema.sql` - Products and discounts table definitions.
`query.sql` - Discounted product retrieval query.

### Task
Update `query.sql` to support subqueries returning multiple matching rows.

### Acceptance Criteria
1. Products matching any active category discount ID are returned.
2. Multi-row discount results do not cause database errors.
3. Results are ordered by product `id` ascending.
4. Output columns are `id`, `name`, `discount_id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Comparing a scalar column to a subquery using `=` fails whenever the subquery returns more than one row.
- **Level 2 (Directional)**: Consider which SQL operator evaluates membership within a set of values returned by a subquery.
- **Level 3 (Root Cause)**: Change `=` to `IN`: `WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech')`.

---

##### Challenge 73: Historical Revenue Audit Distorted by Modern Catalog Price Updates
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
Financial auditors discovered that audited fiscal revenue from previous years shifted whenever catalog product prices were updated in the current quarter.

### Bug Report
The revenue calculation joins `products` and multiplies quantity by `p.current_price` instead of the historical price recorded in `order_items.price_at_purchase`.

### Steps to Reproduce
1. Item purchased in 2025 at $50.00. Current 2026 catalog price is $80.00.
2. Run `query.sql`.
3. Notice historical total computes as 2 * 80 = $160 instead of 2 * 50 = $100.

### Expected Behaviour
Calculate revenue using historical purchase prices: `SUM(quantity * price_at_purchase) AS total_revenue`.

### Actual Behaviour
The query joins `products` and calculates revenue using modern catalog prices.

### Starter Files
`schema.sql` - Products and order_items tables.
`query.sql` - Product revenue audit query.

### Task
Update `query.sql` to compute revenue using immutable historical purchase prices.

### Acceptance Criteria
1. Revenue is computed using `price_at_purchase`.
2. Grouped by `product_id`.
3. Output columns are `product_id` and `total_revenue`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Historical financial metrics must rely on immutable snapshot values captured at transaction time rather than mutable master records.
- **Level 2 (Directional)**: Check which price column is referenced in the arithmetic multiplication in `query.sql`.
- **Level 3 (Root Cause)**: Compute `SUM(quantity * price_at_purchase) AS total_revenue` from `order_items` directly.

---

##### Challenge 74: Unique Active Customer Metric Multiplies Repeat Order Buyers
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
An investor deck metric reported 10,000 active monthly buyers, but customer analytics revealed there were only 3,000 unique individuals because repeat orders were counted multiple times.

### Bug Report
The metric query calculates `COUNT(customer_id)` without deduplicating customers, tallying total orders placed rather than unique purchasing individuals.

### Steps to Reproduce
1. Ingest 3 orders placed by 2 distinct customers.
2. Run `query.sql`.
3. Notice `unique_customers` reports 3 instead of 2.

### Expected Behaviour
Count distinct customer accounts using `COUNT(DISTINCT customer_id) AS unique_customers`.

### Actual Behaviour
The aggregation counts all customer ID rows rather than deduplicating distinct purchaser accounts.

### Starter Files
`schema.sql` - Orders table tracking customer IDs.
`query.sql` - Unique customer metric KPI query.

### Task
Update `query.sql` to count unique individual customers.

### Acceptance Criteria
1. Repeat customer orders are deduplicated.
2. The result count matches unique customer entities (2 for sample data).
3. Output column is aliased as `unique_customers`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: `COUNT(column)` tallies the total number of non-null rows, whereas measuring user populations requires counting distinct IDs.
- **Level 2 (Directional)**: Examine the aggregation function in `query.sql`.
- **Level 3 (Root Cause)**: Insert the `DISTINCT` keyword inside the count function: `COUNT(DISTINCT customer_id) AS unique_customers`.

---

##### Challenge 75: Organizational Hierarchy Chart Cuts Off Sub-Team Employee Reports
- **Difficulty**: `Medium` | **Points**: `150 XP` | **Estimated Time**: `15 mins` | **Tech**: `SQL`

### Incident Report
HR reported that company org charts cut off after direct reports to the CEO, completely omitting sub-team managers and individual contributors.

### Bug Report
The recursive join condition in the CTE matches `e.manager_id = org.manager_id` (peers) instead of `e.manager_id = org.id` (ancestor node), terminating tree traversal prematurely.

### Steps to Reproduce
1. Table contains a 4-level reporting chain: CEO -> VP -> Lead -> Junior.
2. Execute query in `query.sql`.
3. Notice only level 1 and direct peers appear; levels 3 and 4 are missing.

### Expected Behaviour
The recursive step must join employees whose `manager_id` equals the parent node's primary key `org.id` to descend the complete reporting tree.

### Actual Behaviour
Joins on identical manager IDs, failing to recurse downward.

### Starter Files
`schema.sql` - Employees table with manager ID self-referencing relationship.
`query.sql` - Recursive organizational chart query.

### Task
Correct the recursive join condition in `query.sql` to traverse the full employee hierarchy.

### Acceptance Criteria
1. All 4 levels of the employee hierarchy are traversed.
2. The tree descends from CEO down to junior developers.
3. Results are ordered by `level` and `id` ascending.
4. Output columns are `id`, `name`, `level`.

### Constraints
- Target Database: SQLite 3.35+ with Recursive Common Table Expression (CTE) support.
- Hierarchical traversal must safely terminate upon reaching maximum designated depth or cycle boundary.
- Tree levels must maintain correct parent-child relationship tracking across levels.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In a recursive tree CTE, the recursive step must link child foreign keys to the parent primary key produced by the previous iteration.
- **Level 2 (Directional)**: Check the join condition linking `employees e` with `org_tree org` in `query.sql`.
- **Level 3 (Root Cause)**: Change `ON e.manager_id = org.manager_id` to `ON e.manager_id = org.id`.

---

#### Tier: Hard (10 Challenges)

##### Challenge 76: Warehouse Reservation Allows Negative Stock Count
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
During a high-demand flash sale promotion, warehouse operations reported critical physical inventory deficits. For several popular consoles with only one unit remaining in inventory, multiple shoppers checked out at the exact same moment. Both orders were approved, leaving the warehouse inventory stock at negative numbers and forcing customer support to cancel confirmed paid orders.

### Bug Report
The reservation routine in `query.sql` executes a blind decrement against the `inventory` table without asserting that available stock is sufficient before committing the reduction. When two concurrent requests run, both reduce the balance below zero.

### Steps to Reproduce
1. Load physical inventory where available units are `0` or `1`.
2. Execute the decrement query in `query.sql` for an item ID.
3. Observe that stock drops to `-1` instead of blocking or skipping when stock is exhausted.

### Expected Behaviour
The update operation must only decrement physical quantity if sufficient available stock exists (`stock >= 1`), preventing inventory levels from dropping below zero.

### Actual Behaviour
The update decrements blindly without verifying remaining balance in the predicate, driving `stock` into negative numbers.

### Starter Files
- `schema.sql`: Table structure for `inventory` with an item containing `0` remaining units.
- `query.sql`: Unchecked decrement update followed by an inventory status inspection.

### Task
Investigate `query.sql` and add a safety condition to the `UPDATE` statement so that inventory is only decremented when stock is available (`stock >= 1`).

### Acceptance Criteria
1. The inventory update ensures stock does not drop below zero.
2. Depleted items with zero stock are not decremented.
3. The subsequent verification query reflects the guarded inventory balance.

### Constraints
- Target Database: SQLite 3.35+ / ACID compliant database transactions.
- Inventory and balance mutations must enforce non-negative floor constraints (`balance >= amount` or `stock >= qty`).
- Partial updates must not commit without corresponding audit log entries.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Consider optimistic concurrency control: an update should only succeed if the current state satisfies availability preconditions.
- **Level 2 (Directional)**: Look at the WHERE clause of the UPDATE statement. Currently it only filters by record ID without checking whether remaining stock is positive.
- **Level 3 (Root Cause)**: Append a condition checking that stock is at least 1 (e.g. `AND stock >= 1`) so that out-of-stock items are not decremented.

---

##### Challenge 77: Direct Transfer Drops Funds During Partial Write Failure
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
A banking customer reported a loss of $50 after attempting a peer-to-peer transfer. The sender's account was debited immediately, but the receiving account was nonexistent due to a typo in the target account ID. Because the statements ran without atomic coordination and ledger safeguards, the money vanished from the sender without ever being credited to anyone.

### Bug Report
In `query.sql`, the transfer script decrements the sender's balance and attempts to credit a nonexistent account ID (`999`). Additionally, the debit statement executes without verifying that the source account actually has sufficient balance (`balance >= 50`).

### Steps to Reproduce
1. Inspect the initial account balances in `schema.sql`.
2. Run `query.sql` to execute the balance updates.
3. Notice that account 1 loses $50 while account 2 receives nothing because the credit was sent to an invalid target ID.

### Expected Behaviour
Funds must only be debited from account 1 if sufficient balance exists (`balance >= 50`), and the credit must target the valid recipient account (`id = 2`).

### Actual Behaviour
The debit executes unconditionally and the credit statement attempts to update invalid account `999`.

### Starter Files
- `schema.sql`: Table structure and initial balances for `accounts` (Alice with 100.00, Bob with 50.00).
- `query.sql`: Unchecked debit update followed by an erroneous credit statement targeting id `999`.

### Task
Modify `query.sql` so that the debit is guarded with a balance check (`AND balance >= 50`) and the credit accurately deposits $50 into the recipient account (`id = 2`).

### Acceptance Criteria
1. The sender balance is debited only when sufficient funds exist.
2. The receiver account is credited with the transfer amount.
3. The final query returns all accounts showing balanced amounts.

### Constraints
- Target Database: SQLite 3.35+ / ACID compliant database transactions.
- Inventory and balance mutations must enforce non-negative floor constraints (`balance >= amount` or `stock >= qty`).
- Partial updates must not commit without corresponding audit log entries.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Financial ledger operations must ensure both sides of the transfer match valid entity keys and balance constraints.
- **Level 2 (Directional)**: Examine the recipient ID in the credit UPDATE statement and check whether the debit ensures sufficient funds exist.
- **Level 3 (Root Cause)**: Update the debit query to verify `AND balance >= 50` on account 1, and direct the credit update to valid recipient `WHERE id = 2`.

---

##### Challenge 78: Customer Summary Query Multiplies Order and Ticket Totals
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
Account managers complained that customer overview dashboards display absurdly inflated numbers. A customer who placed only two orders totaling $150 and opened three support tickets is reported as having spent $450 with six support tickets. The finance and support teams are unable to trust the summary metrics.

### Bug Report
The dashboard query joins `customers` simultaneously to two independent one-to-many child tables (`orders` and `tickets`). This creates a Cartesian product between the orders and tickets for each customer (2 orders * 3 tickets = 6 joined rows). Aggregating `SUM(o.amount)` and `COUNT(t.id)` over this joined set multiplies order sums by the number of tickets and multiplies ticket counts by the number of orders.

### Steps to Reproduce
1. Populate a customer with 2 orders ($50, $100) and 3 support tickets.
2. Run the join query in `query.sql`.
3. Inspect `total_spent` and `total_tickets`: total spent appears as $450 instead of $150, and ticket count appears as 6 instead of 3.

### Expected Behaviour
Orders and tickets must be aggregated independently so that total spending equals $150 and total tickets equal 3.

### Actual Behaviour
The direct multi-table join produces intermediate Cartesian duplicates, multiplying aggregate measures.

### Starter Files
- `schema.sql`: Tables for `customers`, `orders`, and `tickets` with sample records.
- `query.sql`: Problematic multi-table JOIN query aggregating both child tables simultaneously.

### Task
Refactor `query.sql` to pre-aggregate `orders` and `tickets` independently in Common Table Expressions (CTEs) or subqueries grouped by `customer_id`, then join those pre-aggregated summaries back to `customers`.

### Acceptance Criteria
1. Order totals and ticket counts are computed in independent CTEs (`o_summary` and `t_summary`).
2. `customers` is left joined to both summaries, using `COALESCE` to default missing totals to 0.
3. The final output reports `total_spent` of 150.00 and `total_tickets` of 3.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Joining two separate one-to-many child tables to the same parent table creates a Cartesian product across the child rows.
- **Level 2 (Directional)**: Compute aggregates for orders and tickets in separate queries or Common Table Expressions (CTEs) before joining them.
- **Level 3 (Root Cause)**: Define `WITH o_summary AS (...)` and `WITH t_summary AS (...)` grouping by `customer_id`, then join both to `customers` with `COALESCE`.

---

##### Challenge 79: Settled Invoice Workflow Omits Audit Journal Entry
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
During a quarterly financial compliance audit, external regulators flagged an integrity violation. Several commercial invoices had been marked as settled in the system, but the mandatory audit journal records detailing the settlement event were missing. The compliance failure resulted in flagged reporting and an audit penalty.

### Bug Report
The invoice reconciliation script in `query.sql` executes an update statement to set invoice status to `'paid'`, but fails to create the required audit tracking record in `audit_journal`.

### Steps to Reproduce
1. Inspect the initial state in `schema.sql` where invoice 1 is in `'pending'` status.
2. Run `query.sql`.
3. Notice that `audit_journal` contains zero rows for invoice 1 (`journal_count = 0`), violating audit trail requirements.

### Expected Behaviour
When an invoice is marked as `'paid'`, an audit row must also be inserted into `audit_journal` with `invoice_id = 1` and action `'INVOICE_PAID'`.

### Actual Behaviour
The invoice status is modified, but no corresponding audit journal row is written.

### Starter Files
- `schema.sql`: Table definitions for `invoices` and `audit_journal` with a pending invoice.
- `query.sql`: Solitary status update without the accompanying audit journal write.

### Task
Update `query.sql` to insert an audit record into `audit_journal` with values `(1, 1, 'INVOICE_PAID')` alongside the invoice status update.

### Acceptance Criteria
1. The invoice status is marked as paid.
2. A corresponding entry is recorded in the audit journal with the invoice reference.
3. The final verification query outputs the paid status and an audit count of 1.

### Constraints
- Target Database: SQLite 3.35+ / ACID compliant database transactions.
- Inventory and balance mutations must enforce non-negative floor constraints (`balance >= amount` or `stock >= qty`).
- Partial updates must not commit without corresponding audit log entries.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Financial compliance operations require that every status transition is paired with an immutable journal entry.
- **Level 2 (Directional)**: Look at the verification query: it expects `journal_count` to reflect an entry in `audit_journal` for invoice 1.
- **Level 3 (Root Cause)**: Add `INSERT INTO audit_journal VALUES (1, 1, 'INVOICE_PAID');` immediately following the invoice UPDATE statement.

---

##### Challenge 80: Settings Migration Fails on Unmigrated Missing Emails
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
During a scheduled production maintenance window, a database migration script failed abruptly when attempting to apply a `NOT NULL` constraint to the `user_settings` table. The failure rolled back the deployment pipeline, delayed a critical release, and left the team scrambling to clean up missing data in historical customer profiles.

### Bug Report
The data migration script in `query.sql` queries user settings without backfilling existing `NULL` entries in the `notification_email` column. Before adding mandatory schema constraints, historical records with missing emails must be backfilled to a safe default fallback.

### Steps to Reproduce
1. Inspect the sample records in `schema.sql`: user accounts 102 and 103 have `NULL` notification emails.
2. Run `query.sql`.
3. Notice that `NULL` values persist, which would violate incoming non-nullable constraints.

### Expected Behaviour
All records with `NULL` in `notification_email` must be backfilled with `'no-reply@domain.com'` prior to displaying the finalized records.

### Actual Behaviour
The script simply queries the table without executing the necessary backfill update.

### Starter Files
- `schema.sql`: Table structure and initial data containing NULL email addresses.
- `query.sql`: Standalone SELECT statement without backfill logic.

### Task
Add an `UPDATE` statement to `query.sql` that sets `notification_email = 'no-reply@domain.com'` for all rows where `notification_email IS NULL` before the final query.

### Acceptance Criteria
1. Unset notification emails are backfilled with the default system fallback address.
2. Existing configured emails remain untouched.
3. The final query returns all rows with no empty notification addresses.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Applying NOT NULL constraints to legacy tables requires backfilling default values for all existing NULL entries first.
- **Level 2 (Directional)**: Identify which records have missing emails using `WHERE notification_email IS NULL`.
- **Level 3 (Root Cause)**: Prepend an `UPDATE user_settings SET notification_email = 'no-reply@domain.com' WHERE notification_email IS NULL;` before the SELECT.

---

##### Challenge 81: Ledger Running Balance Jumps on Tied Transaction Timestamps
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
Accountants auditing an automated payment ledger noticed anomalies in transaction statements. When two transactions arrived in the same exact second (`2026-10-19 12:00:00`), the running balance printed on the statement jumped ahead, showing the combined cumulative sum of both transactions immediately on the first line instead of incrementing row by row.

### Bug Report
The window function in `query.sql` uses `SUM(amount) OVER (ORDER BY trans_time)`. By default in SQL standard window specifications, `ORDER BY` without an explicit frame clause defaults to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. Under `RANGE`, rows with identical timestamps are treated as peers and aggregated together in a single step.

### Steps to Reproduce
1. Inspect the test records in `schema.sql`: transactions 1 and 2 share the identical timestamp `'2026-10-19 12:00:00'`.
2. Run `query.sql`.
3. Observe that row 1 already shows a running balance of `150.00` instead of `100.00`.

### Expected Behaviour
The running balance must accumulate strictly row-by-row in deterministic order: transaction 1 should show 100.00, transaction 2 should show 150.00, and transaction 3 should show 175.00.

### Actual Behaviour
Tied timestamps cause the default `RANGE` window frame to lump peer rows together, skipping individual intermediate totals.

### Starter Files
- `schema.sql`: Table structure for `ledger` with transactions occurring at identical timestamps.
- `query.sql`: Window function using default `RANGE` framing without tie-breaking columns.

### Task
Update the window function specification in `query.sql` to include `id` in the sort order and explicitly declare `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` for strict row-by-row accumulation.

### Acceptance Criteria
1. The window function orders by `trans_time, id`.
2. The frame specification explicitly declares `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
3. Row 1 yields a balance of 100.00 and row 2 yields 150.00.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In standard SQL, window ordering without a frame clause defaults to RANGE mode, which aggregates tied order values together.
- **Level 2 (Directional)**: To calculate a true running total for every row, break ties deterministically and switch from RANGE to ROWS framing.
- **Level 3 (Root Cause)**: Specify `ORDER BY trans_time, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` inside the `OVER(...)` clause.

---

##### Challenge 82: Revenue Summary Mistakenly Aggregates Uncommitted Draft Carts
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
The executive sales dashboard reported a 20% spike in daily gross merchandise volume. However, when finance reconciled the reported figures against actual payment gateway receipts, the numbers did not match. Further inspection revealed that abandoned checkout carts were being counted as completed sales revenue.

### Bug Report
The sales aggregation query in `query.sql` calculates `SUM(amount)` across all rows in the `orders` table without filtering by order state. Carts currently in `'draft'` state are erroneously included in official sales figures.

### Steps to Reproduce
1. Check the table records in `schema.sql`: order 2 is in `'draft'` status with amount 50.00, while orders 1 and 3 are `'confirmed'`.
2. Run `query.sql`.
3. Notice that `total_sales` returns 350.00 instead of the actual confirmed total of 300.00.

### Expected Behaviour
The revenue summary must exclusively calculate revenue for completed, confirmed orders (`status = 'confirmed'`), returning 300.00.

### Actual Behaviour
The query computes a blind sum across all records, conflating uncommitted drafts with confirmed transactions.

### Starter Files
- `schema.sql`: Table structure and sample order records with both `'confirmed'` and `'draft'` statuses.
- `query.sql`: Unfiltered aggregation query calculating total sales.

### Task
Update `query.sql` so that revenue metrics count only confirmed transactions.

### Acceptance Criteria
1. Draft transactions are excluded from the aggregate sum.
2. The calculated sales total reflects strictly confirmed orders.
3. The total outputs 300.00.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Financial and numerical aggregates must preserve decimal precision without truncation.
- Transactions or records filtered out by status or date boundaries must not contribute to calculated totals.
- Output column names, aliases, and ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Business financial reporting must always isolate committed transactional records from temporary workflow states.
- **Level 2 (Directional)**: Review the columns of the `orders` table to identify which field tracks order lifecycle state.
- **Level 3 (Root Cause)**: Add `WHERE status = 'confirmed'` to the query to restrict the calculation to completed purchases.

---

##### Challenge 83: Archived Customer Documents Surface in Active Document Search
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
A compliance and privacy incident was raised when an enterprise client discovered that confidential documents marked as deleted by workspace administrators were still appearing in search results and document listings. Under privacy retention policies, soft-deleted documents must be strictly hidden from standard user listings.

### Bug Report
The document retrieval query in `query.sql` queries the `documents` table without evaluating the soft-delete marker column (`deleted_at`). Consequently, archived and decommissioned records remain visible.

### Steps to Reproduce
1. Inspect `schema.sql`: document 2 (`Deprecated Draft`) has a non-null `deleted_at` timestamp.
2. Run `query.sql`.
3. Notice that document 2 is returned along with active documents.

### Expected Behaviour
The query must filter for active documents only (`WHERE deleted_at IS NULL`), returning only records 1 and 3 ordered by `id`.

### Actual Behaviour
The query returns all documents indiscriminately, leaking soft-deleted items.

### Starter Files
- `schema.sql`: Table structure for `documents` with populated `deleted_at` values.
- `query.sql`: Unfiltered SELECT query returning all documents.

### Task
Update `query.sql` to include a filter ensuring only documents where `deleted_at IS NULL` are returned.

### Acceptance Criteria
1. Soft-deleted document rows are filtered out from the active listing.
2. Active documents are ordered deterministically by primary identifier.
3. Decommissioned documents with recorded deletion timestamps are excluded.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `NULL` denotes missing or unrecorded attributes; evaluate status with explicit `IS NULL` / `IS NOT NULL` checks.
- Left joins must preserve parent records having zero matched child rows without unintended row elimination.
- Output column names and row ordering must strictly match requirements.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In soft-delete schemas, records are marked as removed using a timestamp column rather than being physically deleted.
- **Level 2 (Directional)**: Check which column indicates deletion state and what value it holds for active records.
- **Level 3 (Root Cause)**: Add `WHERE deleted_at IS NULL` before the `ORDER BY id` clause to filter out archived documents.

---

##### Challenge 84: Recursive Category Navigation Causes Unbounded CTE Loop
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
During peak hours, product navigation on an e-commerce catalog froze and backend database CPU spiked to 100%. Database administrators discovered that a data entry error had introduced an indirect circular reference into product category parent links. The recursive navigation query looped indefinitely, exhausting server memory and dropping database connections.

### Bug Report
The Common Table Expression (CTE) in `query.sql` traverses the category hierarchy recursively without an upper bound on traversal depth. If circular dependencies or deep hierarchies occur, the recursion executes indefinitely.

### Steps to Reproduce
1. Inspect the recursive CTE definition in `query.sql`.
2. Notice that the recursive branch joins child categories without restricting traversal depth.
3. In databases with cycle checks or recursion limits, unbounded traversal risks server exhaustion.

### Expected Behaviour
The recursive member of the CTE must impose a safety threshold (`WHERE ct.depth < 5`) to prevent runaway recursive cycles.

### Actual Behaviour
The recursive union runs without a depth guard, vulnerable to infinite loops on cyclic data.

### Starter Files
- `schema.sql`: Table structure and category relationships for `categories`.
- `query.sql`: Recursive CTE `cat_tree` without a depth threshold in the recursive step.

### Task
Add a recursion depth limit in `query.sql` to prevent cyclic hierarchies from generating infinite loop execution.

### Acceptance Criteria
1. Recursive traversal terminates when the depth boundary is reached.
2. Category hierarchy rows up to the depth threshold are returned.
3. Results are ordered by depth and category identifier.

### Constraints
- Target Database: SQLite 3.35+ with Recursive Common Table Expression (CTE) support.
- Hierarchical traversal must safely terminate upon reaching maximum designated depth or cycle boundary.
- Tree levels must maintain correct parent-child relationship tracking across levels.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Recursive CTEs that traverse graph structures require a termination condition or max-depth guard to prevent infinite loops from circular references.
- **Level 2 (Directional)**: Look at the recursive query term after `UNION ALL`: it increments `depth` by 1 at each iteration.
- **Level 3 (Root Cause)**: Add `WHERE ct.depth < 5` to the recursive SELECT statement to enforce a safe upper depth limit.

---

##### Challenge 85: Customer Activity Query Scans Full Orders Table
- **Difficulty**: `Hard` | **Points**: `250 XP` | **Estimated Time**: `25 mins` | **Tech**: `SQL`

### Incident Report
Marketing operations reported that their weekly active customer sync job was timing out after running for over twenty minutes. Engineering analysis revealed that an un-indexed subquery in the filtering clause was triggering repeated full table scans over millions of historical order rows, locking memory buffers and exhausting query execution quotas.

### Bug Report
The customer filtering query in `query.sql` uses `WHERE c.id IN (SELECT o.customer_id FROM orders o)`. In many SQL database engines, unconstrained `IN (SELECT ...)` subqueries materialize large intermediate result sets or fail to utilize semi-join index seeks efficiently compared to correlated existence tests.

### Steps to Reproduce
1. Inspect the database schema in `schema.sql`: `customers` and `orders` tables.
2. Run `query.sql` containing the `IN (SELECT ...)` expression.
3. Review query execution plans: notice the inefficient table scan pattern instead of a fast semi-join check.

### Expected Behaviour
The query should use an efficient existence predicate: `WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)`, allowing the optimizer to perform an early-exit semi-join seek.

### Actual Behaviour
The query uses an unoptimized `IN` subquery that requires materializing order customer keys.

### Starter Files
- `schema.sql`: Table structure and seed records for `customers` and `orders`.
- `query.sql`: Query using `IN (SELECT customer_id FROM orders o)`.

### Task
Refactor `query.sql` to optimize customer order validation using an efficient semi-join existence check.

### Acceptance Criteria
1. Customer rows are evaluated against order records using an existence semi-join rather than an unbounded set lookup.
2. Only customers with at least one matching order (`Alice` and `Bob`) are returned.
3. Output is ordered deterministically by customer ID.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Priority and numerical ranks must sort in mathematical magnitude order rather than lexicographical character ordering.
- Window function partitions and tie-breaking order specifications must conform to ranking rules.
- Output ordering must be deterministic and fully reproducible.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Correlated existence checks allow the database engine to short-circuit upon finding the first matching record rather than collecting all values.
- **Level 2 (Directional)**: Replace the `IN` subquery with an `EXISTS` predicate that links the inner and outer customer identifiers.
- **Level 3 (Root Cause)**: Change the predicate to `WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` while maintaining the order by clause.

---

### Arena 3: Frontend Studio (IDs 86 - 120)

#### Tier: Easy (10 Challenges)

##### Challenge 86: Registration Form Submits With Blank Account Fields
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Customer support reported that newly signed-up user accounts were appearing in the administration console with blank names and corrupted profile records. Backend telemetry showed a surge of HTTP 400 Bad Request errors originating from the new registration page whenever prospective users clicked submit before entering their details.

### Bug Report
In `RegistrationForm.jsx`, the form submission handler invokes `onSubmit` immediately without validating whether the required name input contains non-whitespace characters. An empty string payload is dispatched to the backend service.

### Steps to Reproduce
1. Render `RegistrationForm.jsx` in the browser or test suite.
2. Leave the name input field completely empty (or whitespace only).
3. Click the "Register" submit button.
4. Observe that `onSubmit` fires with `{ name: '' }` and no validation error is displayed.

### Expected Behaviour
If the user attempts to submit without entering a name, submission must be halted, `onSubmit` must not be invoked, and the validation error message `"Name is required"` must be displayed.

### Actual Behaviour
The form dispatches empty values unconditionally without client-side verification.

### Starter Files
- `RegistrationForm.jsx`: Controlled React form component with unvalidated submission handler.

### Task
Refactor `handleSubmit` in `RegistrationForm.jsx` to validate input presence, blocking submissions that contain only whitespace and displaying 'Name is required'.

### Acceptance Criteria
1. Submissions containing empty or whitespace-only names are prevented.
2. An error message 'Name is required' is displayed when attempting to submit blank inputs.
3. Valid non-empty names invoke the submission callback.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Client forms should validate required fields before dispatching API requests or parent callbacks.
- **Level 2 (Directional)**: Inspect `handleSubmit`: check whether `name` contains non-whitespace characters before executing `onSubmit`.
- **Level 3 (Root Cause)**: Add a condition `if (!name.trim()) { setError('Name is required'); return; }` prior to calling `onSubmit`.

---

##### Challenge 87: Stock Availability Banner Renders Raw Zero on Depleted Inventory
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Shoppers browsing the online store alerted support that product catalog items with zero remaining stock were displaying a raw "0" character directly on the page instead of the styled "Sold Out" badge. The visual glitch distorted the product card layout and created confusion about product availability.

### Bug Report
In `Banner.jsx`, the component uses the logical AND operator `{stock && <span className="in-stock">...</span>}` for conditional rendering. In JavaScript, `0 && <Component />` evaluates to the falsy number `0`, which React renders as a literal text node rather than omitting it.

### Steps to Reproduce
1. Pass `stock = 0` as a prop to `StockBanner` in `Banner.jsx`.
2. Inspect the rendered DOM container.
3. Observe that the character `"0"` is displayed alongside or in place of the expected badge.

### Expected Behaviour
When `stock` is greater than 0, render `<span className="in-stock">In Stock ({stock})</span>`. When `stock` is 0 or less, render `<span className="sold-out">Sold Out</span>`.

### Actual Behaviour
The expression evaluates to numeric `0`, which React displays as raw text on screen.

### Starter Files
- `Banner.jsx`: Component using numeric short-circuit evaluation in JSX.

### Task
Refactor the conditional rendering in `Banner.jsx` using an explicit numeric comparison (such as a ternary `stock > 0 ? ... : ...`) so that numeric zero is never rendered as raw text.

### Acceptance Criteria
1. When `stock > 0`, the in-stock badge with item count is rendered.
2. When `stock <= 0`, the sold-out badge is rendered.
3. No raw number "0" is outputted to the DOM.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In JavaScript JSX, numeric expressions like `0 && <Tag />` evaluate to the number `0`, which React renders as text.
- **Level 2 (Directional)**: Avoid relying on short-circuit evaluation with numbers in JSX when the number can be zero.
- **Level 3 (Root Cause)**: Use an explicit comparison or ternary: `{stock > 0 ? <span className="in-stock">...</span> : <span className="sold-out">...</span>}`.

---

##### Challenge 88: Cart Item Card Total Price Fails to Refresh on Quantity Change
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Shoppers reported an irritating lag when adjusting item quantities in their order summary. When clicking the `+` button to increment quantity from 1 to 2, the displayed total price remained at the 1-item price. Only on the subsequent click did it reflect the previous quantity, leaving the displayed total consistently one step out of sync.

### Bug Report
In `ProductCard.jsx`, the component maintains redundant state `totalPrice` alongside `quantity`. In the increment handler, `setTotalPrice(price * quantity)` reads `quantity` synchronously right after `setQuantity(...)`. Because React state updates are scheduled asynchronously, `quantity` holds its old value at calculation time.

### Steps to Reproduce
1. Render `ProductCard.jsx` with `price = 25`.
2. Click the `+` increment button once (quantity becomes 2).
3. Observe that Total still displays `$25` instead of `$50`.

### Expected Behaviour
The total price must update immediately in lockstep with the quantity, always displaying `price * quantity`.

### Actual Behaviour
The component reads stale state synchronously during the event handler, causing redundant state desynchronization.

### Starter Files
- `ProductCard.jsx`: Card component storing both `quantity` and redundant `totalPrice` in local state.

### Task
Refactor `ProductCard.jsx` to remove the redundant `totalPrice` state variable and derive total price directly during render (`price * quantity`).

### Acceptance Criteria
1. Total price computes directly from current price and quantity.
2. Modifying quantity immediately updates the displayed total amount.
3. State remains unified without out-of-sync intermediate values.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Avoid storing values in state that can be derived directly from existing props or state during render.
- **Level 2 (Directional)**: React state setter calls do not update variables immediately within the same synchronous event cycle.
- **Level 3 (Root Cause)**: Remove the `totalPrice` state and calculate `const totalPrice = price * quantity;` directly in the component body.

---

##### Challenge 89: Save Draft Toolbar Button Inadvertently Deletes Active Document
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
A critical severity ticket was logged after several content creators lost hours of work. When users clicked the green "Save" button in the document toolbar to preserve their drafts, the document disappeared from their workspace and was permanently deleted from the database.

### Bug Report
In `ActionButton.jsx`, a copy-paste error caused the "Save" button to bind `onClick={onDelete}` instead of `onClick={onSave}`. As a result, clicking Save executes the document deletion callback.

### Steps to Reproduce
1. Render `ActionButton.jsx` with mock callbacks for `onSave` and `onDelete`.
2. Click the "Save" button.
3. Observe that `onDelete` is invoked instead of `onSave`.

### Expected Behaviour
Clicking the "Save" button must trigger the `onSave` handler. The "Delete" button should trigger `onDelete`.

### Actual Behaviour
The "Save" button is mistakenly wired to the destructive `onDelete` handler.

### Starter Files
- `ActionButton.jsx`: Toolbar component with inverted event handler binding.

### Task
Inspect `ActionButton.jsx` and rebind the Save button's click handler so that it executes `onSave`.

### Acceptance Criteria
1. The "Save" button has `onClick={onSave}`.
2. The "Delete" button maintains `onClick={onDelete}`.
3. Clicking Save executes only `onSave`.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Check event callback bindings to ensure user actions trigger their intended handlers.
- **Level 2 (Directional)**: Review the `onClick` prop passed to the Save button.
- **Level 3 (Root Cause)**: Change `onClick={onDelete}` on the Save button to `onClick={onSave}`.

---

##### Challenge 90: Employee Directory Filter Excludes Names on Mixed-Case Queries
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Employees looking up colleagues in the company staff directory complained that search was broken. Typing lowercase names like `"alice"` or uppercase abbreviations returned zero results, even when employee records such as `"Alice Smith"` were clearly listed on the page.

### Bug Report
In `SearchBar.jsx`, the filtering predicate uses standard JavaScript `item.name.includes(query)`. Because `.includes()` performs strict case-sensitive character comparisons, any difference in casing between query input and stored records produces false negatives.

### Steps to Reproduce
1. Render `SearchBar.jsx` with an employee list containing `"Alice"`.
2. Type `"alice"` into the search input.
3. Notice that the employee list renders empty.

### Expected Behaviour
Search matching must be case-insensitive, allowing users to find records regardless of whether they type in uppercase, lowercase, or mixed case.

### Actual Behaviour
The search filter requires exact casing match, discarding valid matches.

### Starter Files
- `SearchBar.jsx`: Search filter component performing case-sensitive substring matching.

### Task
Update search filtering in `SearchBar.jsx` so that matching operates in a case-insensitive manner.

### Acceptance Criteria
1. Searches match names regardless of upper or lowercase query input.
2. Submitting uppercase, lowercase, or mixed-case queries returns all matching records.
3. Filtered results update accurately in the component.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: User-facing text searches should be case-insensitive to ensure reliable discovery.
- **Level 2 (Directional)**: Normalize both the source text and the search query before performing substring checks.
- **Level 3 (Root Cause)**: Update the filter predicate to: `item.name.toLowerCase().includes(query.toLowerCase())`.

---

##### Challenge 91: Telemetry Viewer Leaves Loading Spinner Trapped on API Error
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Monitoring team operators noted that when upstream telemetry APIs suffered transient 500 errors, the metric viewer dashboard remained stuck on an infinite spinning loading animation. Operators were unable to see the actual error notification or retry the action without manually reloading the entire browser tab.

### Bug Report
In `DataViewer.jsx`, the asynchronous fetch chain handles errors in `.catch()`, updating `setError(err.message)`. However, it neglects to call `setLoading(false)`. Because `loading` remains `true` and the render check prioritizes `if (loading) return <Spinner />`, the error message is never displayed.

### Steps to Reproduce
1. Render `DataViewer.jsx` with a `fetchFn` that rejects with an error.
2. Wait for the rejected Promise to complete.
3. Observe that the loading spinner remains visible indefinitely while the error message is hidden.

### Expected Behaviour
When an API error occurs, `loading` must be set to `false` and the error message must be presented to the user.

### Actual Behaviour
When a network or server error occurs, the loading indicator remains active indefinitely, preventing the error message from displaying.

### Starter Files
- `DataViewer.jsx`: Async data display component with incomplete error state handling.

### Task
Update error handling in `DataViewer.jsx` so that the loading indicator is dismissed when an error occurs.

### Acceptance Criteria
1. Network or server errors terminate the loading indicator.
2. The error message is rendered clearly when requests fail.
3. Successful requests continue to load data correctly.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Asynchronous operations must reset loading state in both success and error outcomes.
- **Level 2 (Directional)**: Look at the `.catch(err => { ... })` block in the `useEffect` hook.
- **Level 3 (Root Cause)**: Add `setLoading(false);` within the catch handler alongside `setError(err.message)`.

---

##### Challenge 92: Product Detail Card Causes Horizontal Overflow on Mobile Screens
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `CSS`

### Incident Report
Mobile e-commerce shoppers reported that product detail pages were distorted on smartphones. The product card spilled outside the device viewport, triggering an annoying horizontal scroll bar, hiding right-hand buttons, and failing Google Mobile-Friendly usability checks.

### Bug Report
In `ResponsiveCard.css`, the `.product-card` class declares a fixed width `width: 600px;`. On screens narrower than 600px (such as standard 375px mobile displays), the fixed pixel width forces the container to overflow the viewport boundaries.

### Steps to Reproduce
1. View the component on a mobile viewport (e.g., width 375px).
2. Inspect the computed styles on `.product-card`.
3. Notice the card extends 225px beyond the screen edge, creating horizontal overflow.

### Expected Behaviour
The container should fluidly adapt to narrower screens while maintaining a maximum width of 600px on larger desktop viewports.

### Actual Behaviour
The card specifies a rigid `width: 600px;` regardless of screen dimensions.

### Starter Files
- `ResponsiveCard.css`: Stylesheet containing rigid fixed width styling.

### Task
Replace the fixed `width: 600px;` property in `ResponsiveCard.css` with responsive sizing using `max-width: 600px;` and `width: 100%;` (or fluid width constraints).

### Acceptance Criteria
1. The `.product-card` style uses `max-width: 600px;` instead of fixed `width: 600px;`.
2. The component fits cleanly inside narrow mobile viewports without horizontal scrolling.
3. Desktop layout maintains optimal reading width up to 600px.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Fixed pixel widths on container elements frequently cause horizontal overflow on mobile viewports.
- **Level 2 (Directional)**: Use responsive constraints that allow containers to shrink to 100% of the available viewport width.
- **Level 3 (Root Cause)**: Replace `width: 600px;` with `max-width: 600px; width: 100%;`.

---

##### Challenge 93: Newsletter Form Displays Password Error on Invalid Email
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Marketing noticed a high drop-off rate on the email newsletter subscription box. Users who mistyped their email address submitted feedback stating that the site complained their "password must be at least 8 characters", even though the newsletter widget has no password field whatsoever.

### Bug Report
In `EmailInput.jsx`, the validation function checks if `email.includes('@')`. When the check fails, `setError` is invoked with a copy-pasted string from a password component: `'Password must be at least 8 characters'`.

### Steps to Reproduce
1. Type `"johndoe"` (without `@`) into the input field in `EmailInput.jsx`.
2. Trigger the blur event by clicking outside the input.
3. Observe the confusing error message `'Password must be at least 8 characters'`.

### Expected Behaviour
When an invalid email address is entered, display a clear, contextually relevant error message: `'Please enter a valid email address.'`.

### Actual Behaviour
The component displays an irrelevant password length validation error.

### Starter Files
- `EmailInput.jsx`: Form input component with copy-paste validation message error.

### Task
Update `EmailInput.jsx` so that `setError` sets the message to `'Please enter a valid email address.'` when validation fails.

### Acceptance Criteria
1. The error message explicitly states `'Please enter a valid email address.'`.
2. Valid emails clear the error message.
3. The input properly notifies users of email syntax issues.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Form validation messages should accurately describe the field and the specific requirement that failed.
- **Level 2 (Directional)**: Inspect the string passed to `setError(...)` inside the `validate` function.
- **Level 3 (Root Cause)**: Replace the password error message with `setError('Please enter a valid email address.');`.

---

##### Challenge 94: Confirmation Dialog Trap Ignores Escape Key Dismissal
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
During a digital accessibility audit, the company was cited for non-compliance with WCAG 2.1 AA criteria. Power users and visually impaired individuals using keyboard-only navigation reported being trapped inside confirmation modals because pressing the standard Escape key failed to dismiss the dialog.

### Bug Report
In `Modal.jsx`, the modal attaches click handlers to its backdrop and close button, but registers no keyboard event listener for the Escape key on the window or document.

### Steps to Reproduce
1. Open the modal dialog by passing `isOpen = true`.
2. Press the Escape key on the physical keyboard.
3. Observe that the modal remains open and `onClose` is never invoked.

### Expected Behaviour
Pressing the Escape key (`e.key === 'Escape'`) while the modal is open must trigger `onClose()`.

### Actual Behaviour
The modal only closes via mouse clicks, ignoring keyboard dismissal.

### Starter Files
- `Modal.jsx`: Modal dialog component lacking keyboard event listeners.

### Task
Update `Modal.jsx` to support dismissing open modals when the user presses the Escape key, ensuring listeners are cleaned up when the modal closes.

### Acceptance Criteria
1. Pressing the Escape key triggers the modal close callback.
2. Event listeners are properly detached when the modal unmounts or closes.
3. Keyboard navigation operates consistently.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Accessible modal dialogs must provide keyboard support for closing, specifically listening for the Escape key.
- **Level 2 (Directional)**: Use a `useEffect` hook to attach a `keydown` listener to the global `window` object.
- **Level 3 (Root Cause)**: Inside the listener, check `if (e.key === "Escape") onClose();` and return a cleanup function that calls `window.removeEventListener`.

---

##### Challenge 95: Team Member List Reorders Input Focus and Checkbox State
- **Difficulty**: `Easy` | **Points**: `100 XP` | **Estimated Time**: `10 mins` | **Tech**: `React`

### Incident Report
Workspace administrators reported an alarming bug in the team management screen. When deleting an unwanted user from the top of the team list, checkbox selections, toggle states, and text input values from the deleted row jumped down onto the next team member, causing accidental permission changes.

### Bug Report
In `UserList.jsx`, the map iteration uses the array index as the React key: `<li key={index}>`. When an item is removed from the array, subsequent items shift indices, causing React's reconciliation engine to mistakenly preserve internal DOM state and form inputs across different entities.

### Steps to Reproduce
1. Render `UserList.jsx` with three team members.
2. Focus or modify an input associated with the first item (index 0).
3. Click "Delete" on the first item.
4. Observe that the second item inherits the DOM state of the deleted first item because index 0 was retained.

### Expected Behaviour
Each list item must use a permanent, unique entity identifier (`key={user.id}`) to guarantee accurate virtual DOM reconciliation during additions, removals, and reordering.

### Actual Behaviour
The component uses array positions as reconciliation keys, causing checkbox selections to shift to incorrect users when items are deleted.

### Starter Files
- `UserList.jsx`: List component mapping users with index-based keys.

### Task
Update `UserList.jsx` to use persistent unique item identifiers for list keys rather than array indices.

### Acceptance Criteria
1. List elements use unique stable entity identifiers for item keys.
2. Deleting an item preserves the checked state of remaining items.
3. Component identity remains stable across list reorder operations.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Using array indices as React keys causes state bugs when items are reordered, filtered, or deleted.
- **Level 2 (Directional)**: React keys must uniquely identify an item across renders so the diffing algorithm tracks the correct DOM node.
- **Level 3 (Root Cause)**: Change `key={index}` to `key={user.id}` on the `<li>` element.

---

#### Tier: Medium (15 Challenges)

##### Challenge 96: Documentation Typeahead Discards Newest Query Results on Latency Spikes
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Developers searching the enterprise documentation portal reported that live typeahead search was frequently displaying completely wrong search results. For example, after typing `"users"` quickly, the results list showed matches for `"us"` while the input field clearly showed `"users"`. The discrepancy caused developers to navigate into incorrect documentation sections.

### Bug Report
In `LiveSearch.jsx`, an asynchronous race condition occurs when subsequent keystrokes dispatch concurrent network requests. If an earlier request (e.g., for `"us"`) takes longer to resolve than a later request (e.g., for `"users"`), the older slow response resolves last and overwrites the newer search results unconditionally.

### Steps to Reproduce
1. Render `LiveSearch.jsx` with a mock search function that simulates variable network latency.
2. Type a multi-character search term quickly into the search input.
3. Observe that when the slower preliminary request resolves after the latest request, the preliminary results overwrite the current results list.

### Expected Behaviour
The search effect must track active request status or use an abort mechanism so that responses from outdated or superseded queries are ignored.

### Actual Behaviour
Every resolved promise unconditionally invokes `setResults(data)` regardless of whether the query that initiated it is still the latest user input.

### Starter Files
- `LiveSearch.jsx`: Search typeahead component vulnerable to asynchronous race conditions.

### Task
Refactor `LiveSearch.jsx` to prevent race conditions from out-of-order asynchronous responses overwriting newer search results.

### Acceptance Criteria
1. Fast-typing queries discard stale responses from previously initiated slower requests.
2. Only the results for the most recent search query are displayed.
3. In-flight requests are properly ignored when new queries are submitted.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Asynchronous network requests initiated inside `useEffect` must be guarded against out-of-order resolution race conditions.
- **Level 2 (Directional)**: Maintain a boolean flag (such as `let active = true;`) scoped inside the effect that gets flipped to `false` in the effect cleanup return function.
- **Level 3 (Root Cause)**: Verify `if (active)` before calling `setResults(data)`, and return `() => { active = false; };` from the effect.

---

##### Challenge 97: Warehouse Quick-Add Action Discards Batched Inventory Increments
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Warehouse floor operators packing outgoing shipments noticed that clicking the "+3 Quick Add" shortcut button on inventory terminals only increased the item box count by 1 instead of 3. Operators were forced to repeatedly click the button, resulting in incorrect box counts and packaging delays.

### Bug Report
In `CounterBatch.jsx`, the `incrementByThree` handler calls `setCount(count + 1)` three times sequentially. Because each call closes over the same render's snapshot value of `count`, React batches all three updates and evaluates `setCount(0 + 1)` three times, resulting in a net increase of only 1.

### Steps to Reproduce
1. Render `CounterBatch.jsx` with an initial count of 0.
2. Click the "+3 Quick Add" button.
3. Observe that the displayed box count increments to 1 instead of 3.

### Expected Behaviour
Each sequential update in a batch must receive and operate on the previous queued state value, properly incrementing the count by 3.

### Actual Behaviour
All three state updates read the stale closure variable `count`, overwriting one another.

### Starter Files
- `CounterBatch.jsx`: Counter component using repeated direct state updates.

### Task
Refactor `incrementByThree` in `CounterBatch.jsx` so that consecutive queued state updates build upon the most recent state value.

### Acceptance Criteria
1. State updates use updater functions to avoid reading stale closure state.
2. Triggering the batch increment increases the counter by exactly 3.
3. The displayed count accurately reflects all queued modifications.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Multiple consecutive state updates within the same event execution read from the same render closure unless updater functions are used.
- **Level 2 (Directional)**: React queues updater functions and passes the pending state as the first argument to each subsequent updater.
- **Level 3 (Root Cause)**: Replace `setCount(count + 1)` with `setCount(prev => prev + 1)` across all three calls.

---

##### Challenge 98: Customer Support Drawer Retains Prior User Profile Across Ticket Switches
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Customer support agents reported an urgent security and privacy issue: while triaging support tickets, clicking from Customer A's ticket to Customer B's ticket left Customer A's contact info, email address, and billing details displayed in the profile sidebar drawer. An agent inadvertently emailed Customer A regarding Customer B's ticket.

### Bug Report
In `UserProfileLoader.jsx`, the `useEffect` hook that fetches profile information specifies an empty dependency array `[]`. Because `userId` is omitted from dependencies, the effect runs only once when mounted and never refetches when the parent component passes a new `userId` prop.

### Steps to Reproduce
1. Render `UserProfileLoader.jsx` with `userId = "usr_101"`. Profile loads.
2. Change the incoming prop to `userId = "usr_202"`.
3. Observe that no network request is dispatched and the component continues to display data for `usr_101`.

### Expected Behaviour
The component must fetch and display the updated profile whenever the `userId` prop changes.

### Actual Behaviour
The effect ignores prop changes due to an empty dependency array, closing over stale profile data.

### Starter Files
- `UserProfileLoader.jsx`: Profile loader component with omitted hook dependencies.

### Task
Update `UserProfileLoader.jsx` so that changing the active user prop re-fetches and displays the selected user's profile.

### Acceptance Criteria
1. The dependency array includes `userId`.
2. Changing `userId` re-triggers loading and retrieves the correct profile.
3. Component cleanup remains intact to prevent state updates on unmounted instances.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: All props and variables referenced inside a `useEffect` must be specified in its dependency array.
- **Level 2 (Directional)**: Look at the empty dependency array `[]` at the bottom of the effect: it prevents the effect from executing when props change.
- **Level 3 (Root Cause)**: Change the dependency array from `[]` to `[userId, fetchUser]` or `[userId]`.

---

##### Challenge 99: Checkout Cart Subtotal Freezes on In-Place Item Mutation
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Online shoppers complained that altering product quantities in the grocery checkout cart left the overall subtotal stuck on the initial balance. Only after navigating back and forth between different checkout steps did the price refresh, leading shoppers to believe discounts or items were missing.

### Bug Report
In `ShoppingCart.jsx`, `updateQuantity` mutates the existing state array in place via `items[index].qty = newQty` and then calls `setItems(items)`. Because the array reference has not changed, React's shallow comparison treats the state as unchanged, failing to trigger a re-render.

### Steps to Reproduce
1. Render `ShoppingCart.jsx` with sample line items.
2. Modify the quantity of an item using the number input.
3. Observe that the subtotal does not recalculate immediately because React skipped re-rendering the mutated array.

### Expected Behaviour
Updating an item's quantity must produce a new array containing a new item object, preserving state immutability and triggering immediate re-render.

### Actual Behaviour
The handler directly mutates `items[index].qty` and passes the existing reference back to `setItems`.

### Starter Files
- `ShoppingCart.jsx`: Cart component with direct in-place state mutation.

### Task
Refactor `updateQuantity` in `ShoppingCart.jsx` to treat state immutably when modifying item quantities.

### Acceptance Criteria
1. The update creates a new array reference without modifying the previous array.
2. The modified item is cloned with the updated `qty`.
3. The cart subtotal updates immediately upon quantity changes.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Direct mutation of React state structures prevents re-renders because React relies on reference equality.
- **Level 2 (Directional)**: Do not assign properties directly onto objects inside state arrays like `items[index].qty = ...`.
- **Level 3 (Root Cause)**: Use `setItems(items.map(item => item.id === id ? { ...item, qty: newQty } : item))`.

---

##### Challenge 100: Catalog Pagination Leaves Filtered Views Trapped on Nonexistent Page
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Store managers managing product inventory reported that category filters were returning "No products found" even for categories with dozens of items. Investigation showed that if a manager was on page 5 of "All Categories" and then clicked "Furniture" (which only has 1 page of items), the view remained stuck on page 5, which had zero items.

### Bug Report
In `FilterPagination.jsx`, `handleFilterChange` updates `category` via `setCategory(newCategory)`. However, it neglects to reset `page` back to `1`. If the filtered category has fewer total pages than the current page index, the user is stranded on an out-of-range empty page.

### Steps to Reproduce
1. Navigate to page 3 or higher under "All Categories".
2. Select a category with few items (e.g. "Furniture").
3. Notice that the catalog displays "No products found" because `page` is still set to 3.

### Expected Behaviour
Whenever the user changes the filter category, `page` must reset to `1`.

### Actual Behaviour
The page index persists across filter changes, causing out-of-bounds pagination errors.

### Starter Files
- `FilterPagination.jsx`: Filterable paginated catalog component without page reset logic.

### Task
Update `handleFilterChange` in `FilterPagination.jsx` to call `setPage(1)` whenever `newCategory` is selected.

### Acceptance Criteria
1. Changing the category filter sets `page` to 1.
2. Filtered results render starting from the first page.
3. Pagination controls recalculate total pages accurately.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: When changing dataset filters, the current page number must be reset to prevent pointing past the end of the new result set.
- **Level 2 (Directional)**: Examine `handleFilterChange`: it only updates the category state.
- **Level 3 (Root Cause)**: Add `setPage(1);` inside `handleFilterChange` right after `setCategory(newCategory);`.

---

##### Challenge 101: SVG Dashboard Widget Accumulates Leaked Window Resize Listeners
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Performance monitoring flagged client memory leaks in the operational analytics dashboard. Users who left the browser tab open throughout their work shift experienced severe browser tab lag and eventual tab crashes. Profiling showed tens of thousands of duplicate `resize` listeners accumulated on `window`.

### Bug Report
In `ResizeListener.jsx`, `window.addEventListener('resize', handleResize)` is registered in `useEffect`. However, the effect omits a cleanup function. Every time the component mounts or unmounts, a new listener is permanently attached to `window`.

### Steps to Reproduce
1. Mount and unmount `ResizeListener.jsx` repeatedly across tab switches.
2. Inspect the `window` event listeners using Chrome DevTools.
3. Observe that resize event listeners continuously accumulate without being removed.

### Expected Behaviour
The effect must return a cleanup callback that invokes `window.removeEventListener('resize', handleResize)` to detach the listener on unmount.

### Actual Behaviour
The effect has no cleanup return statement, causing memory leaks.

### Starter Files
- `ResizeListener.jsx`: Dimension tracking component omitting event listener cleanup.

### Task
Update `ResizeListener.jsx` to detach its window resize event listener when the component unmounts.

### Acceptance Criteria
1. A cleanup function removes the window resize listener when unmounting.
2. Event listener references match between registration and deregistration.
3. Memory leaks from lingering event listeners are eliminated.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Global event listeners attached to `window` or `document` inside effects must be cleaned up to avoid memory leaks.
- **Level 2 (Directional)**: React `useEffect` supports returning a cleanup callback function that executes when the component unmounts.
- **Level 3 (Root Cause)**: Return `() => window.removeEventListener("resize", handleResize);` from the effect function.

---

##### Challenge 102: Settings Route Guard Triggers Infinite Login Redirect on Cold Refresh
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Logged-in users reloading their account settings page (`/settings`) reported being abruptly redirected to `/login`. Upon reaching `/login`, the session hydration completed and immediately redirected them back to `/settings`, triggering an infinite redirect loop that made the application unusable.

### Bug Report
In `ProtectedRoute.jsx`, the guard immediately evaluates `if (!user) return <Navigate to="/login" />`. On application launch or page reload, `user` is initially `null` while `isLoading` is `true`. The guard fails to verify `isLoading` first, mistakenly kicking valid sessions out before auth initialization completes.

### Steps to Reproduce
1. Render `ProtectedRoute.jsx` with `user = null` and `isLoading = true`.
2. Observe that the component renders `<Navigate to="/login" />` instead of waiting for loading to finish.
3. The premature redirection creates an authentication loop.

### Expected Behaviour
If `isLoading` is true, the route guard must display a loading spinner `<LoadingSpinner />` and defer redirect decisions until auth state resolves.

### Actual Behaviour
The guard assumes uninitialized auth state represents an unauthenticated visitor.

### Starter Files
- `ProtectedRoute.jsx`: Authentication wrapper component lacking initial loading check.

### Task
Update `ProtectedRoute.jsx` to check `if (isLoading) return <LoadingSpinner />;` before checking `if (!user)`.

### Acceptance Criteria
1. The component checks `isLoading` before checking `user`.
2. When `isLoading` is true, `<LoadingSpinner />` is returned.
3. Unauthenticated requests (`!user && !isLoading`) redirect to `/login`.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Asynchronous authentication systems take time to hydrate session tokens from storage or backend endpoints.
- **Level 2 (Directional)**: A protected route should never redirect until session verification is finished.
- **Level 3 (Root Cause)**: Add `if (isLoading) return <LoadingSpinner />;` prior to the `if (!user)` check.

---

##### Challenge 103: Reimbursement Receipt Uploader Locks Up on Network Disruption
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Employees filing travel expense reports reported that when an upload failed due to a spotty Wi-Fi connection, the file uploader widget stayed permanently frozen showing `"Uploading... 20%"`. The submit button remained disabled, and no error message appeared, preventing employees from retrying without reloading the entire page.

### Bug Report
In `FileUploader.jsx`, the `handleUpload` asynchronous function handles errors with `catch (err) { console.error('Upload failed', err); }`. It forgets to reset `setIsUploading(false)` or populate `setError(err.message || 'Upload failed')`. As a result, the component remains permanently locked in uploading mode.

### Steps to Reproduce
1. Render `FileUploader.jsx` with a mock `uploadApi` that throws an error.
2. Click the "Upload Document" button.
3. Observe that after the error occurs, the UI remains permanently stuck on "Uploading... 20%" with no error banner.

### Expected Behaviour
When an upload error occurs, `isUploading` must be reset to `false` and `error` must be set so the user is informed and can retry.

### Actual Behaviour
The `catch` block logs to console without clearing loading state or updating user-facing error state.

### Starter Files
- `FileUploader.jsx`: File upload component with incomplete error state handling.

### Task
Update the `catch` block in `FileUploader.jsx` to call `setIsUploading(false)` and set `setError(err.message || 'Upload failed')`.

### Acceptance Criteria
1. On failure, `setIsUploading(false)` is invoked.
2. `setError` is set with an informative error string.
3. The upload button becomes re-enabled so the user can attempt another upload.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Error handlers in async UI components must restore interactive state so users can retry failed actions.
- **Level 2 (Directional)**: Inspect the `catch (err)` block in `handleUpload`.
- **Level 3 (Root Cause)**: Add `setIsUploading(false);` and `setError(err.message || "Upload failed");` inside the catch handler.

---

##### Challenge 104: Multi-Step Onboarding Form Clears Inputs on Previous Step Navigation
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Prospective insurance policy buyers abandoned an onboarding questionnaire in high numbers. Users reported that after filling out Step 1 with their personal information and moving to Step 2, clicking "Back" to correct their address cleared all input fields in Step 1, forcing them to re-type everything.

### Bug Report
In `WizardForm.jsx`, child component `Step1` initializes local state `const [name, setName] = useState('')` without reading from the passed `formData` prop. When moving to Step 2, `Step1` unmounts and its local state is destroyed. When returning to Step 1, it re-mounts with an empty string.

### Steps to Reproduce
1. In `WizardForm.jsx`, type a name into Step 1.
2. Click "Next" to navigate to Step 2.
3. Click "Back" to return to Step 1.
4. Notice the name input field is blank.

### Expected Behaviour
Step 1 inputs must initialize with and display values from `formData.name` so that navigating backward preserves previously entered values.

### Actual Behaviour
Step 1 uses uninitialized local state, losing user data upon unmount.

### Starter Files
- `WizardForm.jsx`: Multi-step form component whose child steps do not initialize from parent state.

### Task
Update `Step1` in `WizardForm.jsx` so its state initializes from `formData.name || ''` (or reads controlled values directly from `formData.name`).

### Acceptance Criteria
1. `Step1` initializes its input state from `formData.name`.
2. Navigating back and forth between steps retains entered text.
3. Changes propagate cleanly to the parent `formData` container.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In multi-step wizards, child steps that unmount must receive their initial state from a lifted parent state object.
- **Level 2 (Directional)**: Look at `Step1`: it receives `formData` as a prop but ignores it in its `useState` declaration.
- **Level 3 (Root Cause)**: Initialize state with `useState(formData.name || "")`.

---

##### Challenge 105: Executive Overview Dashboard Crashes Entirely on Minor Health Check Timeout
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
During a brief database maintenance blip, the server health check endpoint returned an HTTP 503 while critical revenue systems remained fully operational. However, executive users viewing the overview dashboard saw a full red error screen with zero metrics displayed, completely obscuring their revenue numbers.

### Bug Report
In `MetricsDashboard.jsx`, the data loader uses `Promise.all([fetchRevenue(), fetchHealth()])`. Because `Promise.all` follows fail-fast semantics, if the secondary `fetchHealth()` promise rejects, the entire promise chain rejects immediately, hiding the successfully fetched revenue data.

### Steps to Reproduce
1. Render `MetricsDashboard.jsx` with a working `fetchRevenue` and a failing `fetchHealth`.
2. Notice the `catch` handler runs and sets `error = "Failed to load dashboard metrics"`.
3. The dashboard renders an error banner rather than displaying the available revenue card.

### Expected Behaviour
The component should use `Promise.allSettled` to independently evaluate each endpoint, displaying revenue metrics even if health checks fail.

### Actual Behaviour
A single endpoint failure causes all dashboard widgets to collapse into an error state, hiding data from healthy services.

### Starter Files
- `MetricsDashboard.jsx`: Dashboard component using fail-fast `Promise.all` for parallel queries.

### Task
Refactor `MetricsDashboard.jsx` to retrieve dashboard metrics independently so that healthy widgets display their data even if sibling endpoints fail.

### Acceptance Criteria
1. Available metrics render successfully even when some endpoints fail.
2. Failing widgets display individual error notices without breaking the entire view.
3. Partial system degradations preserve visible operational metrics.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: `Promise.all` rejects immediately if any single promise fails, which is inappropriate for dashboards composed of independent widgets.
- **Level 2 (Directional)**: Use `Promise.allSettled` to inspect the settlement status (`status === "fulfilled"`) of each call independently.
- **Level 3 (Root Cause)**: Replace `Promise.all` with `Promise.allSettled` and extract `results[0].value` and `results[1].value` when fulfilled.

---

##### Challenge 106: Profile Settings Card Displays Cached Name Following Successful Save
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Users changing their display name in account preferences reported that after seeing a green "Saved successfully" toast notification, their old name continued to appear whenever they navigated back to their profile overview. The stale name persisted until they performed a hard browser cache refresh.

### Bug Report
In `ProfileCache.jsx`, the component maintains an in-memory client `cache` map to minimize redundant HTTP fetches. In `handleUpdateName`, the API call updates the backend and local state, but fails to update or invalidate the cached entry in `cache`. When the component re-mounts, it reads the stale name from `cache.get(userId)`.

### Steps to Reproduce
1. Render `ProfileCache.jsx` with a populated cache entry for `userId`.
2. Type a new name and click "Save".
3. Notice that `cache.get(userId)` still returns the previous name because the cache was not updated.

### Expected Behaviour
Following a successful update, the client cache must be synchronized with the new profile data via `cache.set(userId, updated)`.

### Actual Behaviour
The component updates its local React state but leaves the stale entry in the shared cache.

### Starter Files
- `ProfileCache.jsx`: Profile component utilizing a shared client-side cache without cache synchronization.

### Task
Update `handleUpdateName` in `ProfileCache.jsx` to update the cache entry using `cache.set(userId, updated)` following a successful API call.

### Acceptance Criteria
1. The cache is updated with `cache.set(userId, updated)`.
2. Subsequent cache reads return the newly saved profile data.
3. Display state and cache remain in sync.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Client-side caches must be updated or invalidated whenever mutation requests succeed.
- **Level 2 (Directional)**: Inspect `handleUpdateName`: it updates local state `setProfile(updated)` but forgets to update the shared `cache` instance.
- **Level 3 (Root Cause)**: Add `cache.set(userId, updated);` immediately after obtaining the updated profile from the API.

---

##### Challenge 107: Food Ordering Form Executes Duplicate Payments on Double Click
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
A high-volume food delivery app received customer complaints regarding double billing. Impatient diners frequently double-clicked the "Place Order" button during checkout, causing two identical orders to be processed concurrently and billing the customer's credit card twice for the same meal.

### Bug Report
In `SubmitButton.jsx`, the button element lacks a `disabled={isSubmitting}` attribute. Furthermore, `handleSubmit` does not check whether an existing submission is already in flight. Multiple rapid clicks initiate parallel network requests.

### Steps to Reproduce
1. In `SubmitButton.jsx`, click "Place Order" twice in rapid succession.
2. Notice that the button remains clickable while `isSubmitting` is true.
3. Observe that `onOrder` is invoked twice.

### Expected Behaviour
While an order submission is in progress, the button must be disabled (`disabled={isSubmitting}`) and `handleSubmit` must prevent re-entrant execution.

### Actual Behaviour
The button remains active throughout the network call, permitting duplicate submissions.

### Starter Files
- `SubmitButton.jsx`: Order button component lacking disable attribute and submission guard.

### Task
Update `SubmitButton.jsx` to disable the button when `isSubmitting` is true (`disabled={isSubmitting}`) and add a guard `if (isSubmitting) return;` at the beginning of `handleSubmit`.

### Acceptance Criteria
1. The `<button>` element includes `disabled={isSubmitting}`.
2. `handleSubmit` guards against re-entry if `isSubmitting` is already true.
3. Double-clicking the button triggers only a single submission.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Prevent duplicate form submissions by disabling buttons and checking pending state flags.
- **Level 2 (Directional)**: Look at the `<button>` element props: it currently lacks a `disabled` attribute.
- **Level 3 (Root Cause)**: Add `disabled={isSubmitting}` to `<button>` and prepend `if (isSubmitting) return;` inside `handleSubmit`.

---

##### Challenge 108: Hotel Reservation Calendar Shifts Selected Check-In Date Backwards
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Hotel guests booking vacation rooms from North and South America reported arriving at hotels to find their reservations were booked for the wrong day. A guest who explicitly clicked "October 15, 2026" on the calendar widget discovered that their confirmed booking showed "October 14, 2026", resulting in denied check-ins and angry guests.

### Bug Report
In `DatePicker.jsx`, `handleDateChange` receives a string formatted as `"2026-10-15"`. It parses this string via `new Date(dateString)` and formats it using `d.toISOString().split('T')[0]`. In Western timezones (e.g. UTC-5), midnight local time parses as the previous day at 7:00 PM or 8:00 PM UTC, causing `toISOString()` to roll the calendar date backward by one full day.

### Steps to Reproduce
1. Render `DatePicker.jsx` in a browser configured with a negative UTC offset (e.g. US/Eastern).
2. Select `"2026-10-15"`.
3. Observe that `selectedDate` outputs `"2026-10-14"`.

### Expected Behaviour
The selected calendar date string (`"YYYY-MM-DD"`) provided by the HTML5 date input must be used directly without passing through timezone-shifting UTC conversions.

### Actual Behaviour
Constructing a `Date` object and converting back to ISO string shifts the date backward in negative timezones.

### Starter Files
- `DatePicker.jsx`: Date picker component with erroneous Date constructor UTC serialization.

### Task
Update `handleDateChange` in `DatePicker.jsx` to directly pass and store the raw `dateString` (`setSelectedDate(dateString); onSelect(dateString);`) without constructing a timezone-sensitive `Date` object.

### Acceptance Criteria
1. The raw `dateString` is stored and propagated directly.
2. No timezone date shifting occurs across different client timezones.
3. The selected date displays identically to the chosen calendar date.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Native HTML date inputs (`<input type="date">`) already supply clean `"YYYY-MM-DD"` formatted date strings.
- **Level 2 (Directional)**: Constructing `new Date("YYYY-MM-DD")` and converting to ISO string shifts dates backwards in timezones west of UTC.
- **Level 3 (Root Cause)**: Directly use `setSelectedDate(dateString); onSelect(dateString);` without parsing into a `Date` object.

---

##### Challenge 109: Workspace Signup Form Conceals Field-Level Validation Errors
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
Marketing and product teams identified a sharp drop in enterprise signup completions. When prospective clients attempted to create a workspace with an unavailable subdomain name, the backend responded with HTTP 422 and a detailed error message. However, the registration form wiped out all context and displayed only a vague "Submission failed" banner, leaving users unable to determine what went wrong.

### Bug Report
In `ServerErrorForm.jsx`, the catch handler catches the submission error but only executes `setGeneralError('Submission failed')`. It ignores the field-level errors provided in `err.response.data.errors`, preventing the input-specific error message (`fieldErrors.subdomain`) from rendering.

### Steps to Reproduce
1. Submit a taken subdomain in `ServerErrorForm.jsx` that rejects with `{ response: { data: { errors: { subdomain: 'Subdomain already in use' } } } }`.
2. Observe that only the generic error "Submission failed" appears.
3. The specific subdomain error text is never displayed beneath the input.

### Expected Behaviour
The catch handler must inspect `err.response?.data?.errors` and pass them to `setFieldErrors` so that specific validation messages appear next to invalid inputs.

### Actual Behaviour
Field-specific error structures are discarded in favor of a generic string message.

### Starter Files
- `ServerErrorForm.jsx`: Form component discarding field-level API error responses.

### Task
Update `handleSubmit` in `ServerErrorForm.jsx` to populate `setFieldErrors(err.response?.data?.errors || {})` inside the catch block.

### Acceptance Criteria
1. The catch block extracts `err.response?.data?.errors`.
2. `setFieldErrors` is populated with the field error map.
3. The specific error message is displayed beneath the subdomain input field.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: API validation errors (HTTP 422) provide structured per-field error maps that should be routed to their respective form inputs.
- **Level 2 (Directional)**: Check `err.response?.data?.errors` inside the catch block.
- **Level 3 (Root Cause)**: Add `if (err.response?.data?.errors) setFieldErrors(err.response.data.errors);`.

---

##### Challenge 110: Accessible Selection Menu Traps Keyboard Focus by Ignoring Escape
- **Difficulty**: `Medium` | **Points**: `200 XP` | **Estimated Time**: `15 mins` | **Tech**: `React`

### Incident Report
During a mandatory Section 508 and WCAG 2.1 compliance audit for a government contractor, the web application failed automated and manual accessibility testing. Keyboard-only users opening the custom dropdown menu were trapped inside the listbox because pressing the Escape key had no effect.

### Bug Report
In `AccessibleDropdown.jsx`, the keyboard listener `handleKeyDown` handles `'Enter'` and `' '` (Space) to toggle the menu, but completely omits a handler for `e.key === 'Escape'`. When the dropdown is open, pressing Escape does not close it.

### Steps to Reproduce
1. Render `AccessibleDropdown.jsx` and open the menu by pressing Space or clicking the button.
2. Press the Escape key.
3. Observe that the dropdown remains open and focus is trapped.

### Expected Behaviour
Pressing the Escape key while the dropdown is open must dismiss the menu by calling `setIsOpen(false)`.

### Actual Behaviour
The keydown handler ignores the Escape key, leaving the menu open.

### Starter Files
- `AccessibleDropdown.jsx`: Custom dropdown component lacking Escape key handler.

### Task
Update `handleKeyDown` in `AccessibleDropdown.jsx` to check if `e.key === 'Escape'` and dismiss the dropdown with `setIsOpen(false)`.

### Acceptance Criteria
1. `handleKeyDown` checks `if (e.key === 'Escape')`.
2. When Escape is pressed, `setIsOpen(false)` is invoked.
3. The menu closes cleanly without disturbing selection state.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: WCAG criteria require custom dropdowns and dialogs to be dismissable via the standard Escape key.
- **Level 2 (Directional)**: Examine `handleKeyDown`: it currently only checks for Enter and Space.
- **Level 3 (Root Cause)**: Add `if (e.key === "Escape") setIsOpen(false);` inside `handleKeyDown`.

---

#### Tier: Hard (10 Challenges)

##### Challenge 111: Concert Ticket Checkout Permits Overlapping Order Submissions
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
During a high-demand concert ticket release, customer support and accounting were flooded with duplicate ticket purchases and split-billing disputes. Frustrated fans experiencing brief checkout latency clicked the "Confirm Checkout" button multiple times, causing two separate order creation requests to hit the payment gateway in parallel.

### Bug Report
In `CheckoutFlow.jsx`, `handleCheckout` initiates an order request without checking if an authorization request is already pending. Furthermore, the button's disabled condition only checks `status === 'completed'`, leaving the action fully clickable while `status === 'processing'`.

### Steps to Reproduce
1. In `CheckoutFlow.jsx`, trigger `handleCheckout`.
2. Before the asynchronous network call resolves, invoke `handleCheckout` a second time.
3. Observe that both requests dispatch concurrently to the order creation endpoint.

### Expected Behaviour
The checkout action must be protected by an execution lock (such as checking `if (status === 'processing') return;`) and disabling the submit button whenever `status === 'processing'`.

### Actual Behaviour
The component allows overlapping order submissions, leading to duplicate transactions and inventory over-allocation.

### Starter Files
- `CheckoutFlow.jsx`: Order authorization component lacking concurrency locks and pending state guards.

### Task
Update `CheckoutFlow.jsx` to guard against concurrent requests: check `if (status === 'processing') return;` at the beginning of `handleCheckout`, and disable the button while `status === 'processing'` or `status === 'completed'`.

### Acceptance Criteria
1. `handleCheckout` aborts immediately if `status === 'processing'`.
2. The `<button>` is disabled when `status === 'processing'`.
3. Overlapping checkout clicks dispatch exactly one authorization request.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Financial workflows must enforce an atomic mutex or lock preventing concurrent requests on user-facing controls.
- **Level 2 (Directional)**: Inspect the entry point of `handleCheckout` and the button `disabled` condition.
- **Level 3 (Root Cause)**: Add `if (status === "processing") return;` at the start of `handleCheckout` and disable the button when `status === "processing"`.

---

##### Challenge 112: Trading Dashboard Ticker Retains Zombie Listeners on Tab Switch
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
Day traders using the cryptocurrency charting platform reported that after several hours of monitoring market movements and switching between different currency tabs, browser tabs became increasingly unresponsive and ultimately crashed with an "Out of Memory" error. Console logs showed continuous React warnings: `"Can't perform a React state update on an unmounted component"`.

### Bug Report
In `SubscriptionWidget.jsx`, `eventBus.subscribe(symbol, handleTick)` is called inside `useEffect`. When the user navigates away or switches tabs, the component unmounts without calling `unsubscribe`. The singleton event bus retains a reference to `handleTick`, keeping the entire unmounted component tree alive in memory.

### Steps to Reproduce
1. Mount `SubscriptionWidget.jsx` with a coin symbol.
2. Unmount the widget by switching tabs or un-rendering it.
3. Observe that the event bus still invokes `handleTick`, attempting state updates on the unmounted instance.

### Expected Behaviour
The `useEffect` hook must return a cleanup callback that invokes `eventBus.unsubscribe(symbol, handleTick)` when the component unmounts or when dependencies change.

### Actual Behaviour
The effect omits the cleanup callback, leaving zombie callbacks permanently registered.

### Starter Files
- `SubscriptionWidget.jsx`: Streaming price ticker component without event unsubscription logic.

### Task
Update `SubscriptionWidget.jsx` to unsubscribe from live market data streams when the component unmounts.

### Acceptance Criteria
1. The event listener subscription is cancelled upon component unmount.
2. Background ticker feeds stop delivering updates to detached components.
3. Memory overhead remains stable across component lifecycles.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Components subscribing to global publish/subscribe buses must unsubscribe when unmounting to prevent memory leaks.
- **Level 2 (Directional)**: React effects can return a cleanup function that runs before re-running the effect and when the component unmounts.
- **Level 3 (Root Cause)**: Return `() => { eventBus.unsubscribe(symbol, handleTick); };` from the `useEffect` body.

---

##### Challenge 113: Shared Kiosk Client Cache Exposes Preceding Patient Records
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `JavaScript`

### Incident Report
A critical HIPAA data breach incident was reported at a shared hospital ward kiosk. A nurse logged out of the terminal after charting patient vitals. When a doctor subsequently signed into the terminal to examine an unrelated patient, the application pulled cached diagnostic records from memory, displaying the previous patient's confidential health data under the doctor's session.

### Bug Report
In `SessionCache.jsx`, the exported `sessionCache` map holds sensitive user-scoped records in memory. In `logoutUser`, the handler clears `localStorage` tokens and notifies the backend, but fails to purge `sessionCache`. Subsequent logins on the same client workstation read cached records left by the previous session.

### Steps to Reproduce
1. Populate `sessionCache` with patient records during user session 1.
2. Call `logoutUser(authApi, onLoggedOut)`.
3. Inspect `sessionCache.size`: observe that entries remain in memory.

### Expected Behaviour
`logoutUser` must invalidate and purge all entries from `sessionCache` via `sessionCache.clear()` prior to concluding the sign-out flow.

### Actual Behaviour
The in-memory cache persists across logout transitions, causing cross-tenant data leakage.

### Starter Files
- `SessionCache.jsx`: Client authentication and caching utility failing to clear in-memory cache on sign-out.

### Task
Update user sign-out in `SessionCache.jsx` to purge cached in-memory user data upon logging out.

### Acceptance Criteria
1. In-memory session caches are emptied when the user logs out.
2. Sensitive customer data is not retained across user sessions.
3. Subsequent logins begin with a fresh, unpolluted cache.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Client session caches storing personal or confidential data must be purged on user logout to prevent session crossover.
- **Level 2 (Directional)**: Look at `logoutUser`: it removes auth tokens from localStorage but does not clear `sessionCache`.
- **Level 3 (Root Cause)**: Add `sessionCache.clear();` inside `logoutUser` alongside `localStorage.removeItem('authToken');`.

---

##### Challenge 114: Optimistic Feed Like Counter Decrements Below Zero on Network Drop
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
Social feed users browsing in areas with intermittent connectivity noticed post like counters turning negative (`-1 Likes`). When users tapped like while walking through cellular dead zones, the network call failed, but the UI rollback logic subtracted from a mutated count, corrupting the feed statistics.

### Bug Report
In `OptimisticFeed.jsx`, `handleToggleLike` optimistically applies `setLikes(likes + 1)`. If the network request fails, the catch block blindly executes `setLikes(likes - 1)`. If the user tapped the button again or if `likes` changed in the interim, subtracting 1 from the stale or altered count drives the metric below zero.

### Steps to Reproduce
1. Render `OptimisticFeed.jsx` with `initialLikes = 0`.
2. Click the like button.
3. Simulate an API rejection in `api.likePost()`.
4. Observe that the rollback math calculates `0 - 1 = -1` or desynchronizes state.

### Expected Behaviour
Before applying an optimistic state mutation, capture exact snapshots of the current state (`previousLikes = likes`, `previousIsLiked = isLiked`), and revert strictly to those snapshots if the API fails.

### Actual Behaviour
The error handler relies on blind arithmetic rollback (`likes - 1`), causing desynchronized state.

### Starter Files
- `OptimisticFeed.jsx`: Like toggle component with brittle arithmetic rollback.

### Task
Update `handleToggleLike` in `OptimisticFeed.jsx` to capture snapshot variables (`previousLikes` and `previousIsLiked`) before the optimistic update, and restore those snapshot values in the `catch` block.

### Acceptance Criteria
1. Snapshots of `likes` and `isLiked` are stored before the state update.
2. On API error, `setLikes(previousLikes)` and `setIsLiked(previousIsLiked)` are invoked.
3. The counter never drops below the baseline state on failed requests.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Optimistic mutations should save an immutable snapshot of state before changing it, rather than computing inverse arithmetic.
- **Level 2 (Directional)**: Store `const previousLikes = likes;` and `const previousIsLiked = isLiked;` prior to the optimistic update.
- **Level 3 (Root Cause)**: In the `catch` block, revert with `setLikes(previousLikes); setIsLiked(previousIsLiked);`.

---

##### Challenge 115: Executive KPI Summary Freezes on Outdated Monthly Revenue Filter
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
C-suite executives reviewing company revenue performance reported a discrepancies bug in their quarterly KPI portal. When switching tier filters from "Enterprise" to "Starter", the underlying transaction table updated, but the main Monthly Recurring Revenue (MRR) headline metrics remained frozen on the Enterprise numbers, leading to skewed financial analyses.

### Bug Report
In `AnalyticsHub.jsx`, the `metrics` calculation is wrapped in `useMemo`. However, its dependency array is declared as `[]` (empty). As a result, the memoized metrics are computed only once during initial mount and never recompute when `tierFilter` or `transactions` change.

### Steps to Reproduce
1. Render `AnalyticsHub.jsx` with transactions spanning multiple tiers.
2. Select a different tier from the dropdown (e.g. "Enterprise").
3. Observe that Total MRR and Transaction count remain unchanged from the initial view.

### Expected Behaviour
The `useMemo` hook must declare `[transactions, tierFilter]` in its dependencies, recalculating metrics whenever transactions or active filters change.

### Actual Behaviour
The empty dependency array prevents memoization recalculation, presenting stale metrics.

### Starter Files
- `AnalyticsHub.jsx`: Analytics summary component with missing memoization dependencies.

### Task
Update the memoized calculation in `AnalyticsHub.jsx` so that metrics recompute whenever transaction lists or filter criteria change.

### Acceptance Criteria
1. Analytics metrics recompute automatically when filter criteria change.
2. Updated transaction data triggers fresh metric aggregation.
3. Summary values accurately reflect the selected tier filter.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Values computed with `useMemo` must specify all outer variables referenced inside the calculation function in their dependency array.
- **Level 2 (Directional)**: Inspect the dependencies of `useMemo`: the empty array `[]` tells React never to recompute the value after initial render.
- **Level 3 (Root Cause)**: Change `useMemo(..., [])` to `useMemo(..., [transactions, tierFilter])`.

---

##### Challenge 116: Concurrent Dashboard Requests Trigger Replay-Flagged Token Rotation
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `JavaScript`

### Incident Report
Users logging into the cloud dashboard were unexpectedly logged out within minutes. Security logs revealed that when access tokens expired, the client dashboard fired multiple simultaneous API requests (user profile, notifications, billing status). Each request received an HTTP 401 and independently initiated a refresh token exchange. Because the backend enforces refresh token rotation (one-time use), subsequent parallel requests sent invalidated refresh tokens, triggering security alarms and terminating the session.

### Bug Report
In `AuthManager.jsx`, `requestWithAuth` handles 401 errors by directly awaiting `refreshApi()`. It does not coordinate concurrent requests using a shared `refreshPromise`. When four requests fail simultaneously with 401, four separate token refreshes are executed in parallel.

### Steps to Reproduce
1. Execute multiple concurrent calls to `requestWithAuth` with an expired token.
2. Observe that each 401 handler calls `refreshApi()` independently.
3. The multiple refresh attempts trigger backend replay detection.

### Expected Behaviour
If a token refresh is already in progress, subsequent 401 requests must await the existing shared `refreshPromise` rather than creating new ones.

### Actual Behaviour
Every 401 response executes an uncoordinated token refresh call.

### Starter Files
- `AuthManager.jsx`: HTTP client interceptor lacking refresh request deduplication.

### Task
Refactor token refresh in `AuthManager.jsx` so that concurrent requests share a single in-flight refresh promise rather than initiating duplicate refresh calls.

### Acceptance Criteria
1. Concurrent 401 responses share a single in-flight `refreshPromise`.
2. When the refresh completes, all pending requests use the new access token.
3. `refreshPromise` is cleared upon completion.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Token refresh calls must be deduplicated across concurrent HTTP interceptors to support refresh token rotation.
- **Level 2 (Directional)**: Check if a module-level `refreshPromise` already exists before starting a new refresh request.
- **Level 3 (Root Cause)**: Assign `refreshPromise = refreshApi().finally(() => { refreshPromise = null; });` if null, then `await refreshPromise`.

---

##### Challenge 117: Virtualized Log Viewer Reassigns Log Messages on Severity Filter
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
DevOps engineers investigating a critical production incident were misled by the server log viewer. When filtering from "ALL" logs to "ERROR" logs, the virtualized list retained cached DOM nodes with old warning messages or assigned wrong log timestamps to error traces, wasting hours of debugging time.

### Bug Report
In `VirtualList.jsx`, the virtual slice maps visible items using `key={startIndex + index}`. Because keys represent the window offset index rather than the identity of the log entity, filtering or reordering logs causes React to reuse old DOM nodes and their internal state for entirely different log records.

### Steps to Reproduce
1. Render `VirtualList.jsx` with a list of log items containing unique `id` properties.
2. Filter the items list.
3. Observe that React's virtual DOM reconciliation reuses previous element nodes because keys correspond to array offsets rather than entity IDs.

### Expected Behaviour
Virtualized list items must use stable, unique entity identifiers (`key={item.id}`) to guarantee that elements are correctly mapped during filtering, sorting, and dynamic slicing.

### Actual Behaviour
The list uses computed window row indices as keys (`startIndex + index`), causing reconciliation mismatches.

### Starter Files
- `VirtualList.jsx`: Virtualized list component using index-based window keys.

### Task
Update the virtualization list in `VirtualList.jsx` to assign persistent unique item identifiers to rendered list rows rather than virtual index offsets.

### Acceptance Criteria
1. Virtualized list elements use stable item identifiers for element keys.
2. Scrolling and filtering operations maintain correct element-to-data mapping.
3. Visual jumpiness and mismatched row attributes are resolved.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: In virtualized lists, using computed index offsets as keys leads to rendering glitches when the underlying data is filtered or sorted.
- **Level 2 (Directional)**: React keys must identify the underlying entity, not its temporary position inside the viewport window.
- **Level 3 (Root Cause)**: Replace `key={startIndex + index}` with `key={item.id}` on the rendered row container.

---

##### Challenge 118: Flight Reservation Abort Leaves Locked Seats Unreleased
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
An airline reservation platform experienced a surge in abandoned seats and customer complaints. Passengers whose credit cards were declined during checkout discovered that the system kept their selected seat locked for fifteen minutes, preventing them from immediately retrying with an alternate payment card and blocking other flyers from booking the seat.

### Bug Report
In `MultiStepCheckout.jsx`, the booking sequence first calls `api.reserveSeat(flightId, seatNumber)` and then `api.processPayment(...)`. If payment processing fails, the catch block sets the error message but never initiates a compensating transaction to release the seat reservation (`api.releaseSeat(reservation.id)`).

### Steps to Reproduce
1. In `MultiStepCheckout.jsx`, simulate a successful seat reservation followed by a rejected payment.
2. Observe that `api.releaseSeat` is never invoked in the error handler.
3. The reserved seat remains held on the backend inventory.

### Expected Behaviour
If payment fails after a reservation has been successfully acquired, the catch handler must invoke a compensating action: `await api.releaseSeat(reservation.id)` before presenting the error.

### Actual Behaviour
The seat remains held in pending state without cancellation.

### Starter Files
- `MultiStepCheckout.jsx`: Multi-phase transaction component lacking compensating rollback logic.

### Task
Update `handleBook` in `MultiStepCheckout.jsx` to verify if `reservation` exists inside the `catch` block and invoke `await api.releaseSeat(reservation.id)`.

### Acceptance Criteria
1. The catch handler checks `if (reservation)`.
2. When present, `await api.releaseSeat(reservation.id)` is executed.
3. The user is informed of the payment failure and the seat is released for re-selection.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Multi-step workflows that acquire distributed resources must execute compensating actions if downstream steps fail.
- **Level 2 (Directional)**: Check whether `reservation` was successfully established prior to the payment exception.
- **Level 3 (Root Cause)**: Inside `catch (err)`, add `if (reservation) { await api.releaseSeat(reservation.id); }` before setting error state.

---

##### Challenge 119: Collaborative Document Buffer Reverts Recent Edits on Out-Of-Order Packets
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
Content editors working together in the real-time collaborative workspace reported erratic cursor jumps and disappearing paragraphs. When editing over cellular or high-jitter network connections, older text revisions frequently overwrote newer sentences, causing content loss and confusion among collaborating writers.

### Bug Report
In `RealtimeChat.jsx`, the WebSocket listener `handleIncomingMessage` updates document content with `setContent(event.text)` for every packet received. Because UDP/network jitter can deliver packets out of order, an older packet with sequence number 14 arriving after packet 15 overwrites the latest state.

### Steps to Reproduce
1. In `RealtimeChat.jsx`, dispatch event `{ seq: 15, text: 'Final Title' }`.
2. Dispatch a delayed event `{ seq: 14, text: 'Draft Title' }`.
3. Notice that the editor displays `'Draft Title'`, discarding the newer edit.

### Expected Behaviour
The component must track the highest sequence number processed (`lastSeq.current`). If an incoming event has `event.seq <= lastSeq.current`, it must be ignored.

### Actual Behaviour
Every incoming event is applied unconditionally without sequence validation.

### Starter Files
- `RealtimeChat.jsx`: Real-time text component applying events without monotonic sequence verification.

### Task
Update `handleIncomingMessage` in `RealtimeChat.jsx` to discard events if `event.seq <= lastSeq.current` before updating state and updating `lastSeq.current`.

### Acceptance Criteria
1. The message handler checks `if (event.seq <= lastSeq.current) return;`.
2. Out-of-order delayed packets are rejected.
3. The editor strictly maintains monotonically increasing sequence state.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Real-time streaming event handlers must enforce sequence ordering to prevent late-arriving packets from overwriting newer state.
- **Level 2 (Directional)**: Examine `handleIncomingMessage`: it immediately updates `content` without comparing `event.seq` against `lastSeq.current`.
- **Level 3 (Root Cause)**: Add `if (event.seq <= lastSeq.current) return;` before calling `setContent(event.text)`.

---

##### Challenge 120: Revoked Admin Session Triggers White-Screen Crash on Account Action
- **Difficulty**: `Hard` | **Points**: `300 XP` | **Estimated Time**: `20 mins` | **Tech**: `React`

### Incident Report
An enterprise IT administrator logged into a management portal had their elevated privileges revoked by an organization owner in a different browser tab. When the administrator attempted to click "Delete Account", the backend responded with HTTP 403 Forbidden. Instead of displaying a polite "Access Denied" notice, the entire frontend crashed into a blank white screen due to an uncaught promise rejection.

### Bug Report
In `AdminPanel.jsx`, `handleDelete` calls `await api.deleteAccount(user.id)` without a `try/catch` wrapper. When the API returns a 403 error, the unhandled rejection bubbles to the root React error boundary, tearing down the UI.

### Steps to Reproduce
1. In `AdminPanel.jsx`, invoke `handleDelete` while mocking an HTTP 403 response.
2. Observe that the uncaught rejection causes a complete application crash.
3. No user-friendly error message is displayed.

### Expected Behaviour
The API call must be wrapped in `try/catch`. On an HTTP 403 error, set `setErrorMessage('Access Denied: You do not have permission to perform this action.')` while keeping the interface intact.

### Actual Behaviour
The API call runs unguarded, crashing the application on unauthorized access.

### Starter Files
- `AdminPanel.jsx`: Administration panel component lacking exception handling for unauthorized actions.

### Task
Wrap the `api.deleteAccount` call in `AdminPanel.jsx` in a `try/catch` block, setting `errorMessage` and resetting `isDeleting` gracefully.

### Acceptance Criteria
1. `api.deleteAccount` is enclosed in a `try/catch` statement.
2. In the catch block, an informative error message is stored in state.
3. `isDeleting` is reset to `false` and the UI remains responsive without crashing.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.

**Progressive AI Hints:**
- **Level 1 (Conceptual)**: Privileged UI actions must anticipate HTTP 403 authorization failures gracefully rather than letting unhandled rejections crash the view.
- **Level 2 (Directional)**: Enclose the asynchronous `api.deleteAccount(user.id)` call within a `try/catch` structure.
- **Level 3 (Root Cause)**: Inside `catch (err)`, update `setErrorMessage(err.message || "Access Denied")` and reset `setIsDeleting(false)`.

---
