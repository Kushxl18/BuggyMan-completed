"""
Code Arena: Easy Challenges (1 to 15)
Audited and standardized into realistic production incident debugging tickets.
"""

def get_code_easy():
    challenges = []

    # 1. API pagination truncates final dataset record
    challenges.append({
        'id': 1,
        'title': 'API Pagination Truncates Final Dataset Record',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A data analyst reported that daily order exports were consistently missing the last record on each page when paginating through store shipments. On a 25-order day with 10 records per page, page 3 only contained 4 items instead of the expected 5."

### Bug Report
When paginating datasets, the final record of each page slice is excluded, resulting in data loss across paged queries.

### Steps to Reproduce
1. Call `paginate(list(range(25)), page=3, page_size=10)`.
2. Inspect the number of returned records.
3. Observe that the returned list contains only 4 elements instead of the expected 5 elements.

### Expected Behaviour
Given an items list, a 1-indexed page number, and page size, the function must return all items falling within `[(page - 1) * page_size, page * page_size)`.

### Actual Behaviour
The upper boundary index of the slice excludes the last element in the window.

### Starter Files
`pagination.py` - Splits dataset collections into paged slices.

### Task
Investigate `pagination.py` and fix the slice boundary calculation so that all items in the requested page window are returned.

### Acceptance Criteria
1. `paginate(list(range(25)), page=3, page_size=10)` returns `[20, 21, 22, 23, 24]`.
2. `paginate(list(range(10)), page=1, page_size=5)` returns `[0, 1, 2, 3, 4]`.
3. `paginate(list(range(5)), page=4, page_size=5)` returns `[]`.

### Constraints
- `page` is a positive integer (`page >= 1`).
- `page_size` is a positive integer (`1 <= page_size <= 100`).
- `items` is a list of sequential integers or records.
- Out of bounds or empty queries return an empty list `[]`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'pagination.py',
            'content': '''def paginate(items, page=1, page_size=10):
    if not items or page < 1 or page_size < 1:
        return []
    start = (page - 1) * page_size
    end = min(len(items), page * page_size) - 1
    if start >= len(items) or start > end:
        return []
    return items[start:end]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Final page returns remaining 5 elements [20..24]', 'input': 'paginate(list(range(25)), page=3, page_size=10)', 'expected': '[20, 21, 22, 23, 24]', 'hidden': False},
            {'id': 2, 'name': 'First page returns first 5 elements [0..4]', 'input': 'paginate(list(range(10)), page=1, page_size=5)', 'expected': '[0, 1, 2, 3, 4]', 'hidden': False},
            {'id': 3, 'name': 'Out of bounds page returns empty list []', 'input': 'paginate(list(range(5)), page=4, page_size=5)', 'expected': '[]', 'hidden': True},
            {'id': 4, 'name': 'Empty dataset returns empty list []', 'input': 'paginate([], page=1, page_size=10)', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'end = min(len(items), page * page_size) - 1',
        'suspected_component': 'pagination.py',
        'ai_suggestions': [
            'In Python, list slicing syntax `items[start:end]` is exclusive of the `end` index.',
            'Examine how the `end` boundary variable is calculated relative to `page * page_size`.',
            'Because Python slicing is already exclusive of `end`, subtracting 1 from the upper boundary truncates the final element of the slice window.'
        ],
        'topics': ['Pagination', 'Slicing', 'APIs', 'Python'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Python Basics', 'List Slicing'],
        'status': 'published'
    })

    # 2. International search cursors fail with encoding error
    challenges.append({
        'id': 2,
        'title': 'International Search Cursors Fail With Encoding Error',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Our logistics team in Tokyo reported that inventory lookup URLs crashed with a 500 Internal Server Error whenever searching for warehouses with Japanese characters like '東京_Warehouse_01'."

### Bug Report
Opaque pagination cursor generation crashes with an unhandled encoding error when processing international Unicode characters.

### Steps to Reproduce
1. Call `encode_cursor("東京_Warehouse_01")` with a non-ASCII warehouse identifier.
2. Attempt to generate the base64 cursor token.
3. Observe an unhandled Unicode encoding exception.

### Expected Behaviour
The cursor encoder and decoder must handle arbitrary UTF-8 characters and roundtrip transparently (`decode_cursor(encode_cursor(s)) == s`).

### Actual Behaviour
The encoder converts input strings using an ASCII-restricted byte conversion that rejects characters outside the standard 7-bit ASCII range.

### Starter Files
`cursor_encoder.py` - Encodes and decodes pagination cursor strings using base64.

### Task
Update `cursor_encoder.py` to support full UTF-8 Unicode characters during cursor encoding and decoding.

### Acceptance Criteria
1. `decode_cursor(encode_cursor("東京_Warehouse_01"))` returns `'東京_Warehouse_01'`.
2. `decode_cursor(encode_cursor("München_Hub"))` returns `'München_Hub'`.
3. `encode_cursor("")` returns `""`.

### Constraints
- `cursor_str` is a string containing ASCII or multibyte Unicode characters.
- Encoding scheme must comply with UTF-8 byte representation.
- Empty input strings return an empty string `""`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'cursor_encoder.py',
            'content': '''import base64

def encode_cursor(cursor_str):
    if not cursor_str:
        return ""
    raw_bytes = cursor_str.encode("ascii")
    return base64.b64encode(raw_bytes).decode("ascii")

def decode_cursor(encoded_cursor):
    if not encoded_cursor:
        return ""
    raw_bytes = base64.b64decode(encoded_cursor.encode("ascii"))
    return raw_bytes.decode("ascii")'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Japanese Kanji location roundtrips accurately', 'input': 'decode_cursor(encode_cursor("東京_Warehouse_01"))', 'expected': '東京_Warehouse_01', 'hidden': False},
            {'id': 2, 'name': 'German Umlaut location roundtrips accurately', 'input': 'decode_cursor(encode_cursor("München_Hub"))', 'expected': 'München_Hub', 'hidden': False},
            {'id': 3, 'name': 'Empty cursor returns empty string', 'input': 'encode_cursor("")', 'expected': '', 'hidden': True},
            {'id': 4, 'name': 'Plain ASCII cursor backward compatibility preserved', 'input': 'decode_cursor(encode_cursor("item_id_1092"))', 'expected': 'item_id_1092', 'hidden': True}
        ],
        'bug_signature': 'raw_bytes = cursor_str.encode("ascii")',
        'suspected_component': 'cursor_encoder.py',
        'ai_suggestions': [
            'Character strings must be converted to raw bytes before base64 encoding; consider which encoding format supports global character sets.',
            'Inspect the character encoding format specified in `.encode()` and `.decode()` in `cursor_encoder.py`.',
            'Standard ASCII only supports character codes up to 127; switching to UTF-8 enables full multibyte Unicode support.'
        ],
        'topics': ['Unicode', 'Base64', 'Encoding', 'Python'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['String Encoding'],
        'status': 'published'
    })

    # 3. Market data service crashes on inactive ticker symbols
    challenges.append({
        'id': 3,
        'title': 'Market Data Service Crashes on Inactive Ticker Symbols',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Error Handling',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"The market ingestion dashboard crashed unexpectedly during morning startup when processing newly delisted or inactive ticker symbols that returned an empty array of price items."

### Bug Report
The price extraction function raises an unhandled IndexError when parsing vendor payloads that contain empty items lists.

### Steps to Reproduce
1. Call `extract_latest_price({"items": []})` with an empty items array.
2. Inspect application behavior.
3. Observe that an unhandled indexing exception crashes the extraction pipeline.

### Expected Behaviour
The function must return `{"price": 0.0, "status": "unavailable"}` whenever the payload is invalid, empty, or missing price items.

### Actual Behaviour
The parser reads the first index directly without checking whether the collection contains any items.

### Starter Files
`api_client.py` - Parses market quotation payloads from third-party vendor APIs.

### Task
Refactor `extract_latest_price` in `api_client.py` to handle empty or missing item collections safely.

### Acceptance Criteria
1. `extract_latest_price({"items": [{"price": 142.5}]})` returns `{'price': 142.5, 'status': 'active'}`.
2. `extract_latest_price({"items": []})` returns `{'price': 0.0, 'status': 'unavailable'}`.
3. `extract_latest_price({})` returns `{'price': 0.0, 'status': 'unavailable'}`.

### Constraints
- `payload` is a JSON-compatible dictionary or `None`.
- Returned price is a `float`, and status is `'active'` or `'unavailable'`.
- Invalid or non-dict payloads return the fallback structure safely without crashing.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'api_client.py',
            'content': '''def extract_latest_price(payload):
    if not isinstance(payload, dict):
        return {"price": 0.0, "status": "unavailable"}
    
    items = payload.get("items", [])
    first_item = items[0]
    return {"price": first_item.get("price", 0.0), "status": "active"}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Active payload extracts price with active status', 'input': 'extract_latest_price({"items": [{"price": 142.5}]})', 'expected': "{'price': 142.5, 'status': 'active'}", 'hidden': False},
            {'id': 2, 'name': 'Empty items list returns fallback unavailable status', 'input': 'extract_latest_price({"items": []})', 'expected': "{'price': 0.0, 'status': 'unavailable'}", 'hidden': False},
            {'id': 3, 'name': 'Missing items key returns fallback unavailable status', 'input': 'extract_latest_price({})', 'expected': "{'price': 0.0, 'status': 'unavailable'}", 'hidden': True},
            {'id': 4, 'name': 'Non-dict payload safely returns fallback structure', 'input': 'extract_latest_price(None)', 'expected': "{'price': 0.0, 'status': 'unavailable'}", 'hidden': True}
        ],
        'bug_signature': 'first_item = items[0]',
        'suspected_component': 'api_client.py',
        'ai_suggestions': [
            'Defensive programming requires verifying that collections have elements before attempting to read positional indices.',
            'Examine what happens in `extract_latest_price` when `payload.get("items", [])` returns an empty list.',
            'Check whether `items` has elements before accessing `items[0]`, returning the default fallback dictionary if it is empty.'
        ],
        'topics': ['Error Handling', 'Defensive Programming', 'APIs'],
        'skills_tested': ['Python', 'Error Handling', 'Backend'],
        'prerequisites': ['Python Dictionaries and Lists'],
        'status': 'published'
    })

    # 4. European bank dates assigned to wrong calendar month
    challenges.append({
        'id': 4,
        'title': 'European Bank Dates Assigned to Wrong Calendar Month',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"An accounting manager at our Berlin subsidiary noticed that transaction dates imported from European bank statements showed the 11th of May instead of the 5th of November."

### Bug Report
Date parsing assumes US month-first ordering (`MM/DD/YYYY`), misinterpreting international day-first transaction dates (`DD/MM/YYYY`).

### Steps to Reproduce
1. Call `parse_transaction_date("05/11/2026")` with a European day-first date string.
2. Compare the output ISO date against the actual transaction date.
3. Observe that the day and month are transposed in the parsed result.

### Expected Behaviour
Given an international date string formatted as `DD/MM/YYYY`, the parser must output standard ISO `YYYY-MM-DD` (e.g. `2026-11-05`).

### Actual Behaviour
The date formatting string parses the first component as month and the second component as day.

### Starter Files
`date_parser.py` - Normalizes transaction date strings to ISO 8601 format.

### Task
Update `date_parser.py` to interpret date strings using standard European day-first ordering.

### Acceptance Criteria
1. `parse_transaction_date("05/11/2026")` returns `'2026-11-05'`.
2. `parse_transaction_date("24/07/2026")` returns `'2026-07-24'`.
3. `parse_transaction_date("01/01/2026")` returns `'2026-01-01'`.

### Constraints
- `date_str` is a string formatted as `DD/MM/YYYY`.
- Output is an ISO 8601 string `YYYY-MM-DD` or `None` on invalid formats.
- Days `01` through `31`, months `01` through `12`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'date_parser.py',
            'content': '''from datetime import datetime

def parse_transaction_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
    return dt.strftime("%Y-%m-%d")'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Day-first format parses 5th of November accurately', 'input': 'parse_transaction_date("05/11/2026")', 'expected': '2026-11-05', 'hidden': False},
            {'id': 2, 'name': 'Day exceeding 12 parses 24th of July without error', 'input': 'parse_transaction_date("24/07/2026")', 'expected': '2026-07-24', 'hidden': False},
            {'id': 3, 'name': 'New year date 1st of January parses accurately', 'input': 'parse_transaction_date("01/01/2026")', 'expected': '2026-01-01', 'hidden': True},
            {'id': 4, 'name': 'Malformed non-date string returns None gracefully', 'input': 'parse_transaction_date("invalid")', 'expected': 'None', 'hidden': True}
        ],
        'bug_signature': 'dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")',
        'suspected_component': 'date_parser.py',
        'ai_suggestions': [
            'In standard date formatting tokens, `%d` represents day of the month and `%m` represents month number.',
            'Inspect the format argument provided to `datetime.strptime` in `date_parser.py`.',
            'The parser is currently using US ordering (`%m/%d/%Y`); adjust the tokens to match international European ordering (`%d/%m/%Y`).'
        ],
        'topics': ['Datetime', 'Parsing', 'Data Processing'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Python datetime'],
        'status': 'published'
    })

    # 5. Transient network retries abort before final attempt
    challenges.append({
        'id': 5,
        'title': 'Transient Network Retries Abort Before Final Attempt',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A payment service reported intermittent transaction failures during minor network spikes because the retry client gave up after only 2 attempts, even though maximum retries was configured to 3."

### Bug Report
The retry handler terminates the attempt loop one iteration prematurely, abandoning transient requests before exhausting all permitted retries.

### Steps to Reproduce
1. Configure `execute_with_retry` with `max_retries=3`.
2. Pass an operation that fails on attempts 1 and 2, but succeeds on attempt 3.
3. Observe that the function returns `None` without attempting the 3rd permitted execution.

### Expected Behaviour
The handler must retry up to `max_retries` inclusive, returning the result if any attempt succeeds.

### Actual Behaviour
The loop termination condition stops execution before reaching the final allowed attempt count.

### Starter Files
`retry_handler.py` - Executes transient operations with automated retry attempts.

### Task
Modify `execute_with_retry` in `retry_handler.py` so that operations are retried up to the full configured `max_retries`.

### Acceptance Criteria
1. Operation succeeding on attempt 3 returns `'OK'` when `max_retries=3`.
2. Operation succeeding on attempt 1 returns `'FAST'` without further retries.
3. Exhausted attempts that always fail return `None`.

### Constraints
- `max_retries` is a positive integer (`1 <= max_retries <= 10`).
- `operation` is a callable taking attempt index `attempt`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'retry_handler.py',
            'content': '''def execute_with_retry(operation, max_retries=3):
    attempt = 0
    while attempt < max_retries - 1:
        attempt += 1
        try:
            return operation(attempt)
        except Exception:
            continue
    return None'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Operation succeeds on final permitted attempt 3', 'input': 'execute_with_retry(lambda a: "OK" if a == 3 else (_ for _ in ()).throw(ValueError("transient error")), max_retries=3)', 'expected': 'OK', 'hidden': False},
            {'id': 2, 'name': 'Immediate success on attempt 1 terminates promptly', 'input': 'execute_with_retry(lambda a: "FAST", max_retries=3)', 'expected': 'FAST', 'hidden': False},
            {'id': 3, 'name': 'Complete failure across all attempts returns None', 'input': 'execute_with_retry(lambda a: (_ for _ in ()).throw(RuntimeError("down")), max_retries=3)', 'expected': 'None', 'hidden': True}
        ],
        'bug_signature': 'while attempt < max_retries - 1:',
        'suspected_component': 'retry_handler.py',
        'ai_suggestions': [
            'Trace the iteration count carefully from initial attempt to termination condition.',
            'Examine the comparison in the `while` loop condition relative to `max_retries`.',
            'Subtracting 1 from `max_retries` in `attempt < max_retries - 1` stops the loop after `N - 1` iterations instead of `N`.'
        ],
        'topics': ['Retries', 'Resilience', 'Loops'],
        'skills_tested': ['Python', 'Backend', 'Error Handling'],
        'prerequisites': ['While Loops', 'Exception Handling'],
        'status': 'published'
    })

    # 6. Multi-clinic patient records overwritten during deduplication
    challenges.append({
        'id': 6,
        'title': 'Multi-Clinic Patient Records Overwritten During Deduplication',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A regional healthcare network discovered missing patient records after merging intake data from separate clinic branches. Patients who happened to share the same local clinic ID were treated as duplicates, deleting legitimate medical files."

### Bug Report
The deduplication filter uses only local record IDs rather than clinic-scoped composite keys, causing distinct patients from different clinics to overwrite each other.

### Steps to Reproduce
1. Ingest records from Clinic 1 and Clinic 2 both using local ID `101`.
2. Run `deduplicate_records`.
3. Observe that the returned list contains only 1 record instead of 2.

### Expected Behaviour
Records from distinct clinics sharing the same local ID must both be retained; only records with identical `(clinic_id, id)` tuples should be deduplicated.

### Actual Behaviour
The deduplicator tracks uniqueness using solely `id`, dropping records from separate clinics.

### Starter Files
`deduplicator.py` - Filters duplicate medical intake records.

### Task
Update `deduplicate_records` in `deduplicator.py` to identify uniqueness using composite `(clinic_id, id)` pairs.

### Acceptance Criteria
1. `len(deduplicate_records([{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 2, "id": 101, "name": "Bob"}]))` returns `2`.
2. `len(deduplicate_records([{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 1, "id": 101, "name": "Alice"}]))` returns `1`.
3. `deduplicate_records([])` returns `[]`.

### Constraints
- Each record contains integer `clinic_id`, integer `id`, and metadata fields.
- Preserves original insertion ordering of first-seen records.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'deduplicator.py',
            'content': '''def deduplicate_records(records):
    seen = set()
    result = []
    for r in records:
        key = r.get("id")
        if key not in seen:
            seen.add(key)
            result.append(r)
    return result'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Preserves records sharing local ID across different clinics', 'input': 'len(deduplicate_records([{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 2, "id": 101, "name": "Bob"}]))', 'expected': '2', 'hidden': False},
            {'id': 2, 'name': 'Eliminates genuine duplicate from identical clinic', 'input': 'len(deduplicate_records([{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 1, "id": 101, "name": "Alice"}]))', 'expected': '1', 'hidden': False},
            {'id': 3, 'name': 'Empty records list returns empty collection', 'input': 'deduplicate_records([])', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'key = r.get("id")',
        'suspected_component': 'deduplicator.py',
        'ai_suggestions': [
            'In distributed or multi-tenant systems, primary keys generated by separate databases are not globally unique on their own.',
            'Look at what is stored in the `seen` set in `deduplicate_records`.',
            'Create a composite tuple combining `clinic_id` and `id` to ensure unique tracking across multiple branches.'
        ],
        'topics': ['Deduplication', 'Data Integrity', 'Multi-Tenancy'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Sets and Tuples'],
        'status': 'published'
    })

    # 7. Zero value configuration settings reset to default timeout
    challenges.append({
        'id': 7,
        'title': 'Zero Value Configuration Settings Reset to Default Timeout',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"DevOps engineers trying to disable request caching by setting `TIMEOUT_SECONDS=0` discovered that the microservice unexpectedly reverted to the 30-second default timeout."

### Bug Report
Configuration loading treats integer zero as falsy, incorrectly replacing explicitly configured zero values with fallback defaults.

### Steps to Reproduce
1. Set `TIMEOUT_SECONDS="0"` in the configuration environment dictionary.
2. Call `get_timeout_seconds({"TIMEOUT_SECONDS": "0"})`.
3. Observe that the function returns default `30` instead of integer `0`.

### Expected Behaviour
Explicit numerical string `"0"` must evaluate to integer `0`; the default `30` should only apply when the setting is missing or empty.

### Actual Behaviour
The return statement evaluates the integer truthiness of the parsed value, causing `0 or 30` to resolve to `30`.

### Starter Files
`config_loader.py` - Parses environment configuration settings with fallback defaults.

### Task
Fix `get_timeout_seconds` in `config_loader.py` so that explicit zero values are preserved.

### Acceptance Criteria
1. `get_timeout_seconds({"TIMEOUT_SECONDS": "0"})` returns `0`.
2. `get_timeout_seconds({})` returns `30`.
3. `get_timeout_seconds({"TIMEOUT_SECONDS": "120"})` returns `120`.

### Constraints
- `env_dict` is a dictionary with string keys and string/None values.
- Valid timeout values are non-negative integers (`>= 0`).
- Default timeout is integer `30`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'config_loader.py',
            'content': '''def get_timeout_seconds(env_dict=None):
    env = env_dict if env_dict is not None else {}
    val = env.get("TIMEOUT_SECONDS")
    if not val:
        return 30
    parsed = int(val)
    return parsed or 30'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Explicit zero string returns integer 0 without fallback', 'input': 'get_timeout_seconds({"TIMEOUT_SECONDS": "0"})', 'expected': '0', 'hidden': False},
            {'id': 2, 'name': 'Unset configuration uses default fallback 30', 'input': 'get_timeout_seconds({})', 'expected': '30', 'hidden': False},
            {'id': 3, 'name': 'Explicit positive integer is correctly preserved', 'input': 'get_timeout_seconds({"TIMEOUT_SECONDS": "120"})', 'expected': '120', 'hidden': True}
        ],
        'bug_signature': 'return parsed or 30',
        'suspected_component': 'config_loader.py',
        'ai_suggestions': [
            'In Python, the integer `0` evaluates to `False` in boolean conditions like `a or b`.',
            'Check where `return parsed or 30` handles the converted integer in `config_loader.py`.',
            'Distinguish between absence (`val is None` or empty string) and numeric zero: return `int(val)` directly once valid presence is confirmed.'
        ],
        'topics': ['Configuration', 'Environment Variables', 'Boolean Logic'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Python Basics'],
        'status': 'published'
    })

    # 8. Multi-tenant cache returns data across customer accounts
    challenges.append({
        'id': 8,
        'title': "Multi-Tenant Cache Returns Data Across Customer Accounts",
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Caching',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A security audit discovered that customer profiles from Store A were leaking into Store B because both stores were retrieving data using shared unnamespaced cache keys."

### Bug Report
Cache key generation omits the tenant store identifier, producing key collisions across distinct tenant accounts.

### Steps to Reproduce
1. Call `generate_cache_key("store_a", "42")`.
2. Compare against `generate_cache_key("store_b", "42")`.
3. Observe that both calls return identical cache keys without tenant isolation.

### Expected Behaviour
Cache keys must incorporate both store and user IDs in the format `store:{store_id}:user:{user_id}`.

### Actual Behaviour
The key generator creates keys solely using `user_id`, ignoring the store context.

### Starter Files
`cache_manager.py` - Formats partition keys for multi-tenant caching layers.

### Task
Update `generate_cache_key` in `cache_manager.py` to enforce strict tenant namespacing.

### Acceptance Criteria
1. `generate_cache_key("store_a", "42")` returns `'store:store_a:user:42'`.
2. `generate_cache_key("acme", "10")` returns `'store:acme:user:10'`.
3. `generate_cache_key("store_b", "42")` returns `'store:store_b:user:42'`.

### Constraints
- `store_id` and `user_id` are non-empty alphanumeric strings.
- Output key format strictly adheres to `store:<store_id>:user:<user_id>`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'cache_manager.py',
            'content': '''def generate_cache_key(store_id, user_id):
    return f"user_profile:{user_id}"'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Tenant-scoped key for store_a user 42', 'input': 'generate_cache_key("store_a", "42")', 'expected': 'store:store_a:user:42', 'hidden': False},
            {'id': 2, 'name': 'Tenant-scoped key for acme user 10', 'input': 'generate_cache_key("acme", "10")', 'expected': 'store:acme:user:10', 'hidden': False},
            {'id': 3, 'name': 'Tenant-scoped key for store_b user 42', 'input': 'generate_cache_key("store_b", "42")', 'expected': 'store:store_b:user:42', 'hidden': True}
        ],
        'bug_signature': 'return f"user_profile:{user_id}"',
        'suspected_component': 'cache_manager.py',
        'ai_suggestions': [
            'Multi-tenant caching strategies require strict tenant namespacing to prevent cross-account information leakage.',
            'Examine the format string returned by `generate_cache_key` in `cache_manager.py`.',
            'Incorporate both `store_id` and `user_id` into the cache key pattern to guarantee uniqueness per merchant.'
        ],
        'topics': ['Caching', 'Multi-Tenancy', 'Security'],
        'skills_tested': ['Python', 'Caching', 'Backend'],
        'prerequisites': ['String Formatting'],
        'status': 'published'
    })

    # 9. Inventory system rejects out of stock zero quantity updates
    challenges.append({
        'id': 9,
        'title': 'Inventory System Rejects Out of Stock Zero Quantity Updates',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Validation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Warehouse associates attempting to mark depleted items as out of stock reported that the inventory management portal rejected quantity updates of 0 with an error saying 'Quantity is required'."

### Bug Report
Input validation rejects numeric quantity `0` as missing data, preventing stock depletion updates.

### Steps to Reproduce
1. Call `validate_inventory_update("SKU-1", 0)`.
2. Inspect the validation result tuple.
3. Observe that updating stock to zero is rejected as invalid.

### Expected Behaviour
Zero quantity represents valid out-of-stock inventory and must return `(True, "Valid")`; only negative values or missing `None` should be rejected.

### Actual Behaviour
The validator evaluates `if not quantity:`, misinterpreting numeric `0` as an empty field.

### Starter Files
`validator.py` - Validates inventory quantity update requests.

### Task
Refactor `validate_inventory_update` in `validator.py` so that numeric zero is recognized as a valid inventory count.

### Acceptance Criteria
1. `validate_inventory_update("SKU-1", 0)` returns `(True, 'Valid')`.
2. `validate_inventory_update("SKU-1", 15)` returns `(True, 'Valid')`.
3. `validate_inventory_update("SKU-1", -5)` returns `(False, 'Quantity cannot be negative')`.

### Constraints
- `item_id` is a non-empty string.
- `quantity` is an integer or `None`.
- Returns tuple `(is_valid: bool, message: str)`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'validator.py',
            'content': '''def validate_inventory_update(item_id, quantity):
    if not item_id:
        return (False, "Item ID is required")
    if not quantity:
        return (False, "Quantity is required")
    if quantity < 0:
        return (False, "Quantity cannot be negative")
    return (True, "Valid")'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Zero stock quantity is accepted as valid', 'input': 'validate_inventory_update("SKU-1", 0)', 'expected': '(True, \'Valid\')', 'hidden': False},
            {'id': 2, 'name': 'Positive stock quantity is accepted as valid', 'input': 'validate_inventory_update("SKU-1", 15)', 'expected': '(True, \'Valid\')', 'hidden': False},
            {'id': 3, 'name': 'Negative stock quantity is rejected with descriptive error', 'input': 'validate_inventory_update("SKU-1", -5)', 'expected': '(False, \'Quantity cannot be negative\')', 'hidden': True},
            {'id': 4, 'name': 'None value is rejected with requirement error', 'input': 'validate_inventory_update("SKU-1", None)', 'expected': '(False, \'Quantity is required\')', 'hidden': True}
        ],
        'bug_signature': 'if not quantity:',
        'suspected_component': 'validator.py',
        'ai_suggestions': [
            'In Python, `not 0` evaluates to `True`, which causes falsy value checks to conflate numerical zero with `None`.',
            'Review the condition checking `quantity` in `validator.py`.',
            'Explicitly check `quantity is None` for missing inputs, allowing zero and positive integers to proceed.'
        ],
        'topics': ['Validation', 'Boolean Logic', 'APIs'],
        'skills_tested': ['Python', 'Validation', 'Backend'],
        'prerequisites': ['Python If Statements'],
        'status': 'published'
    })

    # 10. Customer address export breaks on embedded commas
    challenges.append({
        'id': 10,
        'title': 'Customer Address Export Breaks on Embedded Commas',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A marketing coordinator reported that customer mailing lists exported to CSV had shifted columns whenever an address included an apartment number like '123 Maple St, Suite 4'."

### Bug Report
The CSV parser splits lines strictly by commas without respecting quotation marks, breaking rows with embedded commas into mismatched columns.

### Steps to Reproduce
1. Pass `"John Doe","123 Maple St, Suite 4","Springfield"` into `parse_csv_row`.
2. Inspect the parsed list of columns.
3. Observe that the address field with an internal comma is erroneously split into separate fields.

### Expected Behaviour
Quoted fields containing internal commas must be preserved as single column values according to standard CSV rules.

### Actual Behaviour
The function uses naive string splitting on all commas regardless of quotation boundaries.

### Starter Files
`csv_parser.py` - Parses delimited CSV text rows into list columns.

### Task
Update `parse_csv_row` in `csv_parser.py` to use Python's standard `csv` module for compliant parsing.

### Acceptance Criteria
1. `parse_csv_row('"John Doe","123 Maple St, Suite 4","Springfield"')` returns `['John Doe', '123 Maple St, Suite 4', 'Springfield']`.
2. `parse_csv_row("Alice,25,Engineer")` returns `['Alice', '25', 'Engineer']`.
3. `parse_csv_row("")` returns `[]`.

### Constraints
- `row_str` is an RFC 4180 compliant CSV line string.
- Strips surrounding quotes while preserving internal comma content.
- Returns list of field strings.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'csv_parser.py',
            'content': '''def parse_csv_row(row_str):
    if not row_str:
        return []
    return [field.strip().strip('"') for field in row_str.split(",")]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Quoted field with internal comma is parsed as single column', 'input': 'parse_csv_row(\'"John Doe","123 Maple St, Suite 4","Springfield"\')', 'expected': '[\'John Doe\', \'123 Maple St, Suite 4\', \'Springfield\']', 'hidden': False},
            {'id': 2, 'name': 'Standard unquoted line parses across standard columns', 'input': 'parse_csv_row("Alice,25,Engineer")', 'expected': '[\'Alice\', \'25\', \'Engineer\']', 'hidden': False},
            {'id': 3, 'name': 'Empty string input returns empty list', 'input': 'parse_csv_row("")', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'return [field.strip().strip(\'"\') for field in row_str.split(",")]',
        'suspected_component': 'csv_parser.py',
        'ai_suggestions': [
            'Splitting strings by commas fails whenever data fields contain punctuation enclosed in quotes.',
            'Python includes a standard library `csv` module designed specifically for compliant delimited data parsing.',
            'Use `csv.reader` together with `io.StringIO` to tokenize the line according to standard CSV quoting rules.'
        ],
        'topics': ['CSV', 'Parsing', 'Standard Library'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Python CSV Module'],
        'status': 'published'
    })

    # 11. Build priority queue orders high severity below low severity
    challenges.append({
        'id': 11,
        'title': 'Build Priority Queue Orders High Severity Below Low Severity',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A CI/CD build manager reported that urgent hotfix jobs with priority level '100' were scheduled after minor jobs with priority '2' because the scheduler ordered priorities alphabetically."

### Bug Report
Priority levels stored as string numbers are sorted lexicographically rather than by numeric magnitude, prioritizing `'10'` and `'100'` before `'2'`.

### Steps to Reproduce
1. Call `sort_priority_levels(["10", "2", "1", "20", "100"])`.
2. Inspect the resulting ordering.
3. Observe that `'100'` appears before `'2'` due to alphabetical character sorting.

### Expected Behaviour
The priority list must be sorted in ascending order according to numerical value: `['1', '2', '10', '20', '100']`.

### Actual Behaviour
The sorting function compares items character by character as strings.

### Starter Files
`sorter.py` - Orders queue build tasks by priority rank.

### Task
Modify `sort_priority_levels` in `sorter.py` to sort numeric strings by integer magnitude.

### Acceptance Criteria
1. `sort_priority_levels(["10", "2", "1", "20", "100"])` returns `['1', '2', '10', '20', '100']`.
2. `sort_priority_levels(["5"])` returns `['5']`.
3. `sort_priority_levels([])` returns `[]`.

### Constraints
- `levels` is a list of positive integer numeric strings.
- Output maintains string representations ordered by integer value.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'sorter.py',
            'content': '''def sort_priority_levels(levels):
    return sorted(levels)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Orders numeric strings by numeric value [1, 2, 10, 20, 100]', 'input': 'sort_priority_levels(["10", "2", "1", "20", "100"])', 'expected': "['1', '2', '10', '20', '100']", 'hidden': False},
            {'id': 2, 'name': 'Single element list preserved accurately', 'input': 'sort_priority_levels(["5"])', 'expected': "['5']", 'hidden': False},
            {'id': 3, 'name': 'Empty input list returns empty collection', 'input': 'sort_priority_levels([])', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'return sorted(levels)',
        'suspected_component': 'sorter.py',
        'ai_suggestions': [
            'Alphabetical string comparisons compare characters one by one from left to right, meaning `\"10\"` is evaluated as smaller than `\"2\"`.',
            'Python\'s `sorted()` function takes a `key` parameter that dictates the comparison criterion.',
            'Pass `key=int` to `sorted()` so each string is compared based on its integer conversion.'
        ],
        'topics': ['Sorting', 'Data Types', 'Algorithms'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Python sorted'],
        'status': 'published'
    })

    # 12. Profile API serializer omits account creation timestamp
    challenges.append({
        'id': 12,
        'title': 'Profile API Serializer Omits Account Creation Timestamp',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Mobile app engineers reported that iOS and Android client applications crashed immediately after user login with a schema validation error when reading user profile JSON responses."

### Bug Report
The profile serialization function omits the required `created_at` timestamp field from the outbound user dictionary.

### Steps to Reproduce
1. Call `serialize_user_profile` with a complete user model dictionary.
2. Inspect the returned dictionary keys.
3. Observe that `created_at` is missing from the serialized output.

### Expected Behaviour
The serialized profile must include `id`, `username`, `email`, and `created_at`.

### Actual Behaviour
The dictionary mapping drops the `created_at` attribute during serialization.

### Starter Files
`serializer.py` - Transforms internal user models into outbound API responses.

### Task
Update `serialize_user_profile` in `serializer.py` to include `created_at` in the output dictionary.

### Acceptance Criteria
1. `serialize_user_profile({"id": 1, "username": "alice", "email": "a@test.com", "created_at": "2026-01-01T00:00:00Z"}).get("created_at")` returns `'2026-01-01T00:00:00Z'`.
2. `serialize_user_profile({"id": 2, "username": "bob", "email": "b@test.com", "created_at": "2026-02-15T12:00:00Z"}).get("username")` returns `'bob'`.
3. `serialize_user_profile(None)` returns `{}`.

### Constraints
- `user_model` is a dictionary or `None`.
- Output contains string keys `id`, `username`, `email`, `created_at`.
- Empty or `None` inputs return an empty dictionary `{}`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'serializer.py',
            'content': '''def serialize_user_profile(user_model):
    if not user_model:
        return {}
    return {
        "id": user_model.get("id"),
        "username": user_model.get("username"),
        "email": user_model.get("email")
    }'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Extracts account creation timestamp', 'input': 'serialize_user_profile({"id": 1, "username": "alice", "email": "a@test.com", "created_at": "2026-01-01T00:00:00Z"}).get("created_at")', 'expected': '2026-01-01T00:00:00Z', 'hidden': False},
            {'id': 2, 'name': 'Serializes standard username field', 'input': 'serialize_user_profile({"id": 2, "username": "bob", "email": "b@test.com", "created_at": "2026-02-15T12:00:00Z"}).get("username")', 'expected': 'bob', 'hidden': False},
            {'id': 3, 'name': 'None input returns empty dictionary', 'input': 'serialize_user_profile(None)', 'expected': '{}', 'hidden': True}
        ],
        'bug_signature': '"email": user_model.get("email")\n    }',
        'suspected_component': 'serializer.py',
        'ai_suggestions': [
            'Client contracts depend on strict schema conformance; every required field in the domain model must be mapped.',
            'Check the dictionary literal constructed in `serialize_user_profile` in `serializer.py`.',
            'Extract `created_at` using `.get(\"created_at\")` and include it as a key in the returned dictionary.'
        ],
        'topics': ['Serialization', 'APIs', 'JSON'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Python Dictionaries'],
        'status': 'published'
    })

    # 13. User session tokens expire seconds after generation
    challenges.append({
        'id': 13,
        'title': 'User Session Tokens Expire Seconds After Generation',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Every time I log into my account, I get kicked back to the login screen after just 3 or 4 seconds. I barely have time to click my profile before seeing 'Session expired. Please log in again.' This is happening on every device across our entire team."

### Bug Report
Newly issued authentication tokens intended to remain valid for 1 hour (3600 seconds) expire approximately 3 seconds after generation, forcing users into continuous re-authentication loops.

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
- `current_timestamp` is a valid Unix epoch timestamp in seconds (`0 <= current_timestamp <= 2_500_000_000`).
- `seconds_to_live` is a non-negative integer representing session validity duration in seconds (`0 <= seconds_to_live <= 604_800`).
- Return type: integer (`int`) timestamp representing `current_timestamp + seconds_to_live`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.
""",
        'files': [{
            'name': 'token_service.py',
            'content': '''def calculate_expiration(current_timestamp, seconds_to_live=3600):
    return current_timestamp + int(seconds_to_live / 1000)'''
        }],
        'test_cases': [
            {'id': 1, 'name': '1-hour session (3600s) extends expiration to 1700003600', 'input': 'calculate_expiration(1700000000, 3600)', 'expected': '1700003600', 'hidden': False},
            {'id': 2, 'name': '60-second session extends expiration to 160', 'input': 'calculate_expiration(100, 60)', 'expected': '160', 'hidden': False},
            {'id': 3, 'name': 'Zero-duration session expires immediately at current timestamp (500)', 'input': 'calculate_expiration(500, 0)', 'expected': '500', 'hidden': False},
            {'id': 4, 'name': '24-hour session (86400s) extends expiration to 1700086400', 'input': 'calculate_expiration(1700000000, 86400)', 'expected': '1700086400', 'hidden': True}
        ],
        'bug_signature': 'return current_timestamp + int(seconds_to_live / 1000)',
        'suspected_component': 'token_service.py',
        'ai_suggestions': [
            'Verify the units of measurement for timestamps and durations: both values here represent seconds.',
            'Examine how `seconds_to_live` is combined with `current_timestamp` in `token_service.py`.',
            'Both parameters are already measured in seconds; applying a scaling divisor mistakenly treats the input as milliseconds, reducing 3600 seconds down to only 3 seconds.'
        ],
        'topics': ['Authentication', 'Math & Units', 'Tokens'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Basic Arithmetic'],
        'status': 'published'
    })

    # 14. Background queue worker crashes when task buffer is empty
    challenges.append({
        'id': 14,
        'title': 'Background Queue Worker Crashes When Task Buffer Is Empty',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Error Handling',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"An on-call engineer was paged at 3:00 AM because background queue workers entered a crash-loop during low-traffic periods whenever the task buffer had no pending jobs."

### Bug Report
Calling `peek_next_job` on an empty list raises an unhandled IndexError, crashing the worker daemon.

### Steps to Reproduce
1. Call `peek_next_job([])` with an empty queue.
2. Inspect worker process execution.
3. Observe that an unhandled indexing exception causes the worker to crash.

### Expected Behaviour
The function must safely return `None` when the queue is empty, and the first job identifier when jobs are present.

### Actual Behaviour
The function attempts direct positional index access without verifying whether any elements exist.

### Starter Files
`queue_processor.py` - Inspects pending background tasks.

### Task
Modify `peek_next_job` in `queue_processor.py` to handle empty queues safely without raising exceptions.

### Acceptance Criteria
1. `peek_next_job(["job_1", "job_2"])` returns `'job_1'`.
2. `peek_next_job([])` returns `'None'`.
3. `peek_next_job(["only_job"])` returns `'only_job'`.

### Constraints
- `jobs` is a list of job identifier strings.
- Returns string job ID or `None` if empty.
- Does not mutate or pop elements from the queue.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'queue_processor.py',
            'content': '''def peek_next_job(jobs):
    return jobs[0]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Non-empty queue returns first pending job', 'input': 'peek_next_job(["job_1", "job_2"])', 'expected': 'job_1', 'hidden': False},
            {'id': 2, 'name': 'Empty queue safely returns None without exception', 'input': 'peek_next_job([])', 'expected': 'None', 'hidden': False},
            {'id': 3, 'name': 'Single item queue returns the single job', 'input': 'peek_next_job(["only_job"])', 'expected': 'only_job', 'hidden': True}
        ],
        'bug_signature': 'return jobs[0]',
        'suspected_component': 'queue_processor.py',
        'ai_suggestions': [
            'Accessing positional index 0 on an empty sequence raises an immediate error in Python.',
            'Check `jobs` for truthiness or length before attempting an index lookup.',
            'Add an initial check: `if not jobs: return None` before reading `jobs[0]`.'
        ],
        'topics': ['Defensive Programming', 'Lists', 'Queue'],
        'skills_tested': ['Python', 'Error Handling'],
        'prerequisites': ['Python Lists'],
        'status': 'published'
    })

    # 15. Invoice tax calculation shows discrepancy on summed line items
    challenges.append({
        'id': 15,
        'title': 'Invoice Tax Calculation Shows Discrepancy on Summed Line Items',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"A billing auditor found discrepancies between monthly customer invoices and bank deposit records. Invoices with multiple small line items showed a 1-cent mismatch compared to the total tax calculated on the order sum."

### Bug Report
The invoice tax function rounds taxes individually per item before summing, compounding fractional cent rounding errors across multi-item invoices.

### Steps to Reproduce
1. Calculate tax on three items of `$10.04` each at an `8.25%` tax rate using `calculate_total_tax([10.04, 10.04, 10.04], 0.0825)`.
2. Compare the returned tax total against cumulative tax on the `$30.12` subtotal.
3. Observe that premature per-item rounding produces a 1-cent discrepancy.

### Expected Behaviour
The function must compute tax on the total sum of all line items before rounding once to 2 decimal places (`round(sum(line_items) * tax_rate, 2)`).

### Actual Behaviour
Tax is calculated and rounded individually on each line item before being summed together.

### Starter Files
`invoice_calculator.py` - Computes sales tax on invoice line items.

### Task
Refactor `calculate_total_tax` in `invoice_calculator.py` to sum line items prior to rounding tax.

### Acceptance Criteria
1. `calculate_total_tax([10.04, 10.04, 10.04], 0.0825)` returns `2.48`.
2. `calculate_total_tax([100.00], 0.10)` returns `10.0`.
3. `calculate_total_tax([])` returns `0.0`.

### Constraints
- `line_items` is a list of non-negative float amounts (`item >= 0.0`).
- `tax_rate` is a float between `0.0` and `1.0`.
- Returns a float rounded to 2 decimal places.
- Empty line items return `0.0`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'invoice_calculator.py',
            'content': '''def calculate_total_tax(line_items, tax_rate=0.0825):
    if not line_items:
        return 0.0
    tax_sum = sum(round(item * tax_rate, 2) for item in line_items)
    return round(tax_sum, 2)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Computes cumulative tax on subtotal avoiding premature rounding error', 'input': 'calculate_total_tax([10.04, 10.04, 10.04], 0.0825)', 'expected': '2.48', 'hidden': False},
            {'id': 2, 'name': 'Single item invoice calculated and rounded accurately', 'input': 'calculate_total_tax([100.00], 0.10)', 'expected': '10.0', 'hidden': False},
            {'id': 3, 'name': 'Empty invoice returns 0.0 tax total', 'input': 'calculate_total_tax([])', 'expected': '0.0', 'hidden': True}
        ],
        'bug_signature': 'tax_sum = sum(round(item * tax_rate, 2) for item in line_items)',
        'suspected_component': 'invoice_calculator.py',
        'ai_suggestions': [
            'Intermediate rounding during financial calculations compounds precision errors across multiple transactions.',
            'Examine where the `round()` function is called inside the comprehension in `invoice_calculator.py`.',
            'Sum the line items first (`sum(line_items)`), multiply the cumulative subtotal by the tax rate, and round the final result once.'
        ],
        'topics': ['Finance', 'Rounding', 'Precision'],
        'skills_tested': ['Python', 'Backend', 'Data Processing'],
        'prerequisites': ['Floating Point Precision'],
        'status': 'published'
    })

    return challenges
