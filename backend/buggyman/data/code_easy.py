"""
Code Arena: Easy Challenges (1 to 15)
"""

def get_code_easy():
    challenges = []

    # 1. API pagination skips the final record
    challenges.append({
        'id': 1,
        'title': '[CODE-E01] API Pagination Skips the Final Record',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """A document portal API slices audit log records into paginated windows.
Due to an incorrect upper boundary calculation, the slicing expression terminates one element early, omitting the final record on each page and dropping the last item of the dataset.

For example, when requesting page 3 with 25 total records and a page size of 10, the endpoint returns only 4 records (`[20, 21, 22, 23]`) instead of 5 (`[20, 21, 22, 23, 24]`), dropping record index 24.

Correct `paginate(items, page, page_size)` in `pagination.py` so that full page ranges and partial final pages return all expected records, while handling empty datasets and out-of-bounds page requests safely.""",
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
            {'id': 1, 'name': 'Visible: Full Page Slice Includes Final Record', 'input': 'paginate(list(range(25)), page=3, page_size=10)', 'expected': '[20, 21, 22, 23, 24]', 'hidden': False},
            {'id': 2, 'name': 'Visible: First Page Exact Boundary', 'input': 'paginate(list(range(10)), page=1, page_size=5)', 'expected': '[0, 1, 2, 3, 4]', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Out of bounds page returns empty list', 'input': 'paginate(list(range(5)), page=4, page_size=5)', 'expected': '[]', 'hidden': True},
            {'id': 4, 'name': 'Hidden: Empty dataset handling', 'input': 'paginate([], page=1, page_size=10)', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'end = min(len(items), page * page_size) - 1',
        'suspected_component': 'pagination.py',
        'ai_suggestions': [
            'Notice that Python slice syntax `items[start:end]` is exclusive of `end`.',
            'Subtracting 1 from `(page * page_size)` drops the last record.',
            'Review Python slice upper bounds: slice ranges items[start:end] are exclusive of end, so subtracting 1 omits the boundary item.'
        ],
        'topics': ['Pagination', 'Slicing', 'APIs', 'Python'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Python Basics', 'List Slicing'],
        'status': 'published'
    })

    # 2. Base64 cursor encoding breaks for Unicode input
    challenges.append({
        'id': 2,
        'title': '[CODE-E02] Base64 Cursor Encoding Breaks for Unicode Input',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Japanese Kanji Location Cursor', 'input': 'decode_cursor(encode_cursor("東京_Warehouse_01"))', 'expected': '東京_Warehouse_01', 'hidden': False},
            {'id': 2, 'name': 'Visible: German Umlaut Cursor', 'input': 'decode_cursor(encode_cursor("München_Hub"))', 'expected': 'München_Hub', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Empty cursor handling', 'input': 'encode_cursor("")', 'expected': '', 'hidden': True},
            {'id': 4, 'name': 'Hidden: Plain ASCII backward compatibility', 'input': 'decode_cursor(encode_cursor("item_id_1092"))', 'expected': 'item_id_1092', 'hidden': True}
        ],
        'bug_signature': 'raw_bytes = cursor_str.encode("ascii")',
        'suspected_component': 'cursor_encoder.py',
        'ai_suggestions': [
            'Inspect the encoding argument passed to `.encode()`.',
            'Investigate standard character encodings: multibyte Unicode characters require UTF-8 encoding rather than ASCII.'
        ],
        'topics': ['Unicode', 'Base64', 'Encoding', 'Python'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['String Encoding'],
        'status': 'published'
    })

    # 3. Empty API responses cause a runtime error
    challenges.append({
        'id': 3,
        'title': '[CODE-E03] Empty API Responses Cause a Runtime Error',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Error Handling',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Normal active payload', 'input': 'extract_latest_price({"items": [{"price": 142.5}]})', 'expected': "{'price': 142.5, 'status': 'active'}", 'hidden': False},
            {'id': 2, 'name': 'Visible: Empty items list', 'input': 'extract_latest_price({"items": []})', 'expected': "{'price': 0.0, 'status': 'unavailable'}", 'hidden': False},
            {'id': 3, 'name': 'Hidden: Missing items key', 'input': 'extract_latest_price({})', 'expected': "{'price': 0.0, 'status': 'unavailable'}", 'hidden': True},
            {'id': 4, 'name': 'Hidden: Non-dict payload', 'input': 'extract_latest_price(None)', 'expected': "{'price': 0.0, 'status': 'unavailable'}", 'hidden': True}
        ],
        'bug_signature': 'first_item = items[0]',
        'suspected_component': 'api_client.py',
        'ai_suggestions': [
            'Check if `items` is empty: `if not items: return {"price": 0.0, "status": "unavailable"}` before indexing.',
            'Never access index 0 without verifying `len(items) > 0`.'
        ],
        'topics': ['Error Handling', 'Defensive Programming', 'APIs'],
        'skills_tested': ['Python', 'Error Handling', 'Backend'],
        'prerequisites': ['Python Dictionaries and Lists'],
        'status': 'published'
    })

    # 4. Incorrect date parsing shifts records to the wrong day
    challenges.append({
        'id': 4,
        'title': '[CODE-E04] Incorrect Date Parsing Shifts Records to the Wrong Day',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: 5th of November', 'input': 'parse_transaction_date("05/11/2026")', 'expected': '2026-11-05', 'hidden': False},
            {'id': 2, 'name': 'Visible: 24th of July', 'input': 'parse_transaction_date("24/07/2026")', 'expected': '2026-07-24', 'hidden': False},
            {'id': 3, 'name': 'Hidden: 1st of January', 'input': 'parse_transaction_date("01/01/2026")', 'expected': '2026-01-01', 'hidden': True},
            {'id': 4, 'name': 'Hidden: Invalid format returns None', 'input': 'parse_transaction_date("invalid")', 'expected': 'None', 'hidden': True}
        ],
        'bug_signature': 'dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")',
        'suspected_component': 'date_parser.py',
        'ai_suggestions': [
            'Look at the date format directives: `%m` is month, `%d` is day.',
            'Check the date format directive: European format places day before month (%d/%m/%Y).'
        ],
        'topics': ['Datetime', 'Parsing', 'Data Processing'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Python datetime'],
        'status': 'published'
    })

    # 5. A retry counter stops one attempt too early
    challenges.append({
        'id': 5,
        'title': '[CODE-E05] A Retry Counter Stops One Attempt Too Early',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Succeeds on attempt 3', 'input': 'execute_with_retry(lambda a: "OK" if a == 3 else (_ for _ in ()).throw(ValueError("transient error")), max_retries=3)', 'expected': 'OK', 'hidden': False},
            {'id': 2, 'name': 'Visible: Succeeds on attempt 1', 'input': 'execute_with_retry(lambda a: "FAST", max_retries=3)', 'expected': 'FAST', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Fails all 3 attempts returns None', 'input': 'execute_with_retry(lambda a: (_ for _ in ()).throw(RuntimeError("down")), max_retries=3)', 'expected': 'None', 'hidden': True}
        ],
        'bug_signature': 'while attempt < max_retries - 1:',
        'suspected_component': 'retry_handler.py',
        'ai_suggestions': [
            'Notice the condition `attempt < max_retries - 1`. If max_retries is 3, when attempt is 1, 1 < 2 is True (attempt 2). Next, 2 < 2 is False, so attempt 3 is never run.',
            'Trace the iteration count: a loop condition comparing against max_retries - 1 terminates one iteration early.'
        ],
        'topics': ['Retries', 'Resilience', 'Loops'],
        'skills_tested': ['Python', 'Backend', 'Error Handling'],
        'prerequisites': ['While Loops', 'Exception Handling'],
        'status': 'published'
    })

    # 6. Duplicate IDs cause incorrect deduplication
    challenges.append({
        'id': 6,
        'title': '[CODE-E06] Duplicate IDs Cause Incorrect Deduplication',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Different clinics with same local ID', 'input': 'len(deduplicate_records([{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 2, "id": 101, "name": "Bob"}]))', 'expected': '2', 'hidden': False},
            {'id': 2, 'name': 'Visible: Same clinic true duplicate removed', 'input': 'len(deduplicate_records([{"clinic_id": 1, "id": 101, "name": "Alice"}, {"clinic_id": 1, "id": 101, "name": "Alice"}]))', 'expected': '1', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Empty records list', 'input': 'deduplicate_records([])', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'key = r.get("id")',
        'suspected_component': 'deduplicator.py',
        'ai_suggestions': [
            'Clinic IDs are independent. Two different clinics can use the same `id`.',
            'Use composite tuple: `key = (r.get("clinic_id"), r.get("id"))`.'
        ],
        'topics': ['Deduplication', 'Data Integrity', 'Multi-Tenancy'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Sets and Tuples'],
        'status': 'published'
    })

    # 7. An environment variable fallback ignores valid configuration
    challenges.append({
        'id': 7,
        'title': '[CODE-E07] An Environment Variable Fallback Ignores Valid Configuration',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Valid zero timeout', 'input': 'get_timeout_seconds({"TIMEOUT_SECONDS": "0"})', 'expected': '0', 'hidden': False},
            {'id': 2, 'name': 'Visible: Unset timeout uses fallback', 'input': 'get_timeout_seconds({})', 'expected': '30', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Positive timeout preserved', 'input': 'get_timeout_seconds({"TIMEOUT_SECONDS": "120"})', 'expected': '120', 'hidden': True}
        ],
        'bug_signature': 'return parsed or 30',
        'suspected_component': 'config_loader.py',
        'ai_suggestions': [
            'Remember that in Python, integer 0 is falsy, so `0 or 30` evaluates to `30`.',
            'Explicitly check `if val is None or val == "": return 30` then `return int(val)`.'
        ],
        'topics': ['Configuration', 'Environment Variables', 'Boolean Logic'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Python Basics'],
        'status': 'published'
    })

    # 8. An incorrect cache key returns another request's result
    challenges.append({
        'id': 8,
        'title': "[CODE-E08] An Incorrect Cache Key Returns Another Request's Result",
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Caching',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'cache_manager.py',
            'content': '''def generate_cache_key(store_id, user_id):
    return f"user_profile:{user_id}"'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Different stores produce different keys', 'input': 'generate_cache_key("store_a", "42") != generate_cache_key("store_b", "42")', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Key includes both store and user', 'input': 'generate_cache_key("acme", "10")', 'expected': 'store:acme:user:10', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Sanitized string format check', 'input': '"acme" in generate_cache_key("acme", "99")', 'expected': 'True', 'hidden': True}
        ],
        'bug_signature': 'return f"user_profile:{user_id}"',
        'suspected_component': 'cache_manager.py',
        'ai_suggestions': [
            'Cache keys in multi-tenant systems must include the tenant identifier as a namespace prefix.',
            'Change to `return f"store:{store_id}:user:{user_id}"`.'
        ],
        'topics': ['Caching', 'Multi-Tenancy', 'Security'],
        'skills_tested': ['Python', 'Caching', 'Backend'],
        'prerequisites': ['String Formatting'],
        'status': 'published'
    })

    # 9. Input validation rejects valid zero values
    challenges.append({
        'id': 9,
        'title': '[CODE-E09] Input Validation Rejects Valid Zero Values',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Validation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Zero quantity accepted', 'input': 'validate_inventory_update("SKU-1", 0)', 'expected': '(True, \'Valid\')', 'hidden': False},
            {'id': 2, 'name': 'Visible: Positive quantity accepted', 'input': 'validate_inventory_update("SKU-1", 15)', 'expected': '(True, \'Valid\')', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Negative quantity rejected', 'input': 'validate_inventory_update("SKU-1", -5)', 'expected': '(False, \'Quantity cannot be negative\')', 'hidden': True},
            {'id': 4, 'name': 'Hidden: None quantity rejected', 'input': 'validate_inventory_update("SKU-1", None)', 'expected': '(False, \'Quantity is required\')', 'hidden': True}
        ],
        'bug_signature': 'if not quantity:',
        'suspected_component': 'validator.py',
        'ai_suggestions': [
            'In Python, `not 0` is `True`. To check for absence, check `quantity is None`.',
            'Remember that 0 evaluates to falsy in boolean contexts; check whether 0 is a valid value for this field.'
        ],
        'topics': ['Validation', 'Boolean Logic', 'APIs'],
        'skills_tested': ['Python', 'Validation', 'Backend'],
        'prerequisites': ['Python If Statements'],
        'status': 'published'
    })

    # 10. A CSV parser mishandles quoted fields
    challenges.append({
        'id': 10,
        'title': '[CODE-E10] A CSV Parser Mishandles Quoted Fields',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'csv_parser.py',
            'content': '''def parse_csv_row(row_str):
    if not row_str:
        return []
    return [field.strip().strip('"') for field in row_str.split(",")]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Quoted field with embedded comma', 'input': 'parse_csv_row(\'"John Doe","123 Maple St, Suite 4","Springfield"\')', 'expected': '[\'John Doe\', \'123 Maple St, Suite 4\', \'Springfield\']', 'hidden': False},
            {'id': 2, 'name': 'Visible: Simple CSV line without quotes', 'input': 'parse_csv_row("Alice,25,Engineer")', 'expected': '[\'Alice\', \'25\', \'Engineer\']', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Empty line handling', 'input': 'parse_csv_row("")', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'return [field.strip().strip(\'"\') for field in row_str.split(",")]',
        'suspected_component': 'csv_parser.py',
        'ai_suggestions': [
            'Do not use `.split(",")` for CSV parsing.',
            'Import `csv` and `import io`, then use `next(csv.reader(io.StringIO(row_str)))`.'
        ],
        'topics': ['CSV', 'Parsing', 'Standard Library'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Python CSV Module'],
        'status': 'published'
    })

    # 11. Sorting produces incorrect results for numeric strings
    challenges.append({
        'id': 11,
        'title': '[CODE-E11] Sorting Produces Incorrect Results for Numeric Strings',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'sorter.py',
            'content': '''def sort_priority_levels(levels):
    return sorted(levels)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Numeric magnitude order', 'input': 'sort_priority_levels(["10", "2", "1", "20", "100"])', 'expected': "['1', '2', '10', '20', '100']", 'hidden': False},
            {'id': 2, 'name': 'Visible: Single element list', 'input': 'sort_priority_levels(["5"])', 'expected': "['5']", 'hidden': False},
            {'id': 3, 'name': 'Hidden: Empty list handling', 'input': 'sort_priority_levels([])', 'expected': '[]', 'hidden': True}
        ],
        'bug_signature': 'return sorted(levels)',
        'suspected_component': 'sorter.py',
        'ai_suggestions': [
            'Python `sorted()` accepts a `key` parameter.',
            'Use `return sorted(levels, key=int)`.'
        ],
        'topics': ['Sorting', 'Data Types', 'Algorithms'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Python sorted'],
        'status': 'published'
    })

    # 12. A response serializer omits a required field
    challenges.append({
        'id': 12,
        'title': '[CODE-E12] A Response Serializer Omits a Required Field',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
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
            {'id': 1, 'name': 'Visible: Serializer output includes created_at', 'input': '"created_at" in serialize_user_profile({"id": 1, "username": "alice", "email": "a@test.com", "created_at": "2026-01-01T00:00:00Z"})', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Exact value serialized', 'input': 'serialize_user_profile({"id": 1, "username": "alice", "email": "a@test.com", "created_at": "2026-01-01T00:00:00Z"}).get("created_at")', 'expected': '2026-01-01T00:00:00Z', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Empty input handling', 'input': 'serialize_user_profile(None)', 'expected': '{}', 'hidden': True}
        ],
        'bug_signature': '"email": user_model.get("email")\n    }',
        'suspected_component': 'serializer.py',
        'ai_suggestions': [
            'Add `"created_at": user_model.get("created_at")` to the return dictionary.'
        ],
        'topics': ['Serialization', 'APIs', 'JSON'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Python Dictionaries'],
        'status': 'published'
    })

    # 13. An incorrect timeout conversion causes premature expiration
    challenges.append({
        'id': 13,
        'title': '[CODE-E13] An Incorrect Timeout Conversion Causes Premature Expiration',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'token_service.py',
            'content': '''def calculate_expiration(current_timestamp, seconds_to_live=3600):
    return current_timestamp + int(seconds_to_live / 1000)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: 1 hour token expiration', 'input': 'calculate_expiration(1700000000, 3600)', 'expected': '1700003600', 'hidden': False},
            {'id': 2, 'name': 'Visible: 60 second token', 'input': 'calculate_expiration(100, 60)', 'expected': '160', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Zero duration token', 'input': 'calculate_expiration(500, 0)', 'expected': '500', 'hidden': True}
        ],
        'bug_signature': 'return current_timestamp + int(seconds_to_live / 1000)',
        'suspected_component': 'token_service.py',
        'ai_suggestions': [
            'Look closely at the math: `seconds_to_live / 1000` turns 3600 into 3.6 seconds.',
            'Change to `return current_timestamp + seconds_to_live`.'
        ],
        'topics': ['Authentication', 'Math & Units', 'Tokens'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Basic Arithmetic'],
        'status': 'published'
    })

    # 14. An empty list causes an indexing error
    challenges.append({
        'id': 14,
        'title': '[CODE-E14] An Empty List Causes an Indexing Error',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Error Handling',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'queue_processor.py',
            'content': '''def peek_next_job(jobs):
    return jobs[0]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Non-empty queue returns first job', 'input': 'peek_next_job(["job_1", "job_2"])', 'expected': 'job_1', 'hidden': False},
            {'id': 2, 'name': 'Visible: Empty queue safely returns None', 'input': 'peek_next_job([])', 'expected': 'None', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Single item queue', 'input': 'peek_next_job(["only_job"])', 'expected': 'only_job', 'hidden': True}
        ],
        'bug_signature': 'return jobs[0]',
        'suspected_component': 'queue_processor.py',
        'ai_suggestions': [
            'Add a guard: `if not jobs: return None` before returning `jobs[0]`.'
        ],
        'topics': ['Defensive Programming', 'Lists', 'Queue'],
        'skills_tested': ['Python', 'Error Handling'],
        'prerequisites': ['Python Lists'],
        'status': 'published'
    })

    # 15. Incorrect rounding produces wrong invoice totals
    challenges.append({
        'id': 15,
        'title': '[CODE-E15] Incorrect Rounding Produces Wrong Invoice Totals',
        'difficulty': 'Easy',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'invoice_calculator.py',
            'content': '''def calculate_total_tax(line_items, tax_rate=0.0825):
    if not line_items:
        return 0.0
    tax_sum = sum(round(item * tax_rate, 2) for item in line_items)
    return round(tax_sum, 2)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Total tax calculation without intermediate rounding', 'input': 'calculate_total_tax([10.04, 10.04, 10.04], 0.0825)', 'expected': '2.48', 'hidden': False},
            {'id': 2, 'name': 'Visible: Single item invoice', 'input': 'calculate_total_tax([100.00], 0.10)', 'expected': '10.0', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Empty invoice handling', 'input': 'calculate_total_tax([])', 'expected': '0.0', 'hidden': True}
        ],
        'bug_signature': 'tax_sum = sum(round(item * tax_rate, 2) for item in line_items)',
        'suspected_component': 'invoice_calculator.py',
        'ai_suggestions': [
            'Do not round individual items. Sum the items first: `total_subtotal = sum(line_items)`.',
            'Then compute `return round(total_subtotal * tax_rate, 2)`.'
        ],
        'topics': ['Finance', 'Rounding', 'Precision'],
        'skills_tested': ['Python', 'Backend', 'Data Processing'],
        'prerequisites': ['Floating Point Precision'],
        'status': 'published'
    })

    return challenges
