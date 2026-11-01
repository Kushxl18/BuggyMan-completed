"""
Code Arena: Medium Challenges (16 to 35)
"""

def get_code_medium():
    challenges = []

    # 16. API retries accidentally repeat a non-idempotent operation
    challenges.append({
        'id': 16,
        'title': '[CODE-M01] API Retries Accidentally Repeat a Non-Idempotent Operation',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A customer reported being charged twice on their credit card statement after seeing a temporary network timeout alert during checkout for order ORD-1."

### Bug Report
When network retries occur during checkout payment requests, distinct transaction tokens are sent to the payment gateway across attempts, resulting in duplicate financial charges.

### Steps to Reproduce
1. Call `charge_with_retry(gateway, order_id="ORD-1", amount=50, max_attempts=3)`.
2. Simulate a transient network error on the initial attempt.
3. Inspect the idempotency keys submitted to the payment gateway across retries.
4. Observe that the retry attempts do not preserve the same idempotency key.

### Expected Behaviour
All retry attempts for the same logical payment transaction must reuse the same invariant idempotency key.

### Actual Behaviour
A new idempotency token is regenerated on each retry iteration, causing the gateway to treat each attempt as an independent transaction.

### Starter Files
`payment_client.py` - Manages payment gateway transactions and retry policies.

### Task
Refactor `charge_with_retry` in `payment_client.py` so the idempotency key is created once prior to entering the retry loop.

### Acceptance Criteria
1. `charge_with_retry(mock_gw, "ORD-1", 50)` produces exactly 1 unique idempotency key across failed and successful attempts.
2. `charge_with_retry(mock_gw, "ORD-2", 25)["status"]` returns `'paid'`.

### Constraints
- `order_id` is a non-empty string.
- `amount` is a positive number.
- `max_attempts` is an integer `>= 1`.
- Re-raises the last exception if all retry attempts fail.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'payment_client.py',
            'content': '''import uuid

def charge_with_retry(gateway, order_id, amount, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        idempotency_key = f"idem_{uuid.uuid4().hex[:8]}"
        try:
            return gateway.charge(order_id, amount, idempotency_key)
        except Exception:
            if attempts >= max_attempts:
                raise
    return None'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Retries reuse identical idempotency key', 'input': '''class MockGateway:
    def __init__(self): self.keys = []
    def charge(self, oid, amt, key):
        self.keys.append(key)
        if len(self.keys) < 2: raise ConnectionError("drop")
        return {"status": "paid", "keys": self.keys}
gw = MockGateway()
res = charge_with_retry(gw, "ORD-1", 50)
res["keys"][0] == res["keys"][1]''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Successful first attempt', 'input': '''class MockGateway:
    def charge(self, oid, amt, key): return {"status": "paid", "key": key}
charge_with_retry(MockGateway(), "ORD-2", 25)["status"]''', 'expected': 'paid', 'hidden': False}
        ],
        'bug_signature': 'attempts += 1\n        idempotency_key = f"idem_{uuid.uuid4().hex[:8]}"',
        'suspected_component': 'payment_client.py',
        'ai_suggestions': [
            'Notice that `idempotency_key` is created inside `while attempts < max_attempts:`.',
            'Move `idempotency_key = f"idem_{uuid.uuid4().hex[:8]}"` (or based on order_id) above the while loop so retries pass the same key.'
        ],
        'topics': ['Idempotency', 'Retries', 'Payments'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Network Retries', 'Idempotency Keys'],
        'status': 'published'
    })

    # 17. Cache invalidation leaves stale product prices
    challenges.append({
        'id': 17,
        'title': '[CODE-M02] Cache Invalidation Leaves Stale Product Prices',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Caching',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Our merchandising team marked down the summer apparel collection from $100 to $60. When clicking an individual product link the price shows $60, but when browsing the category grid, the old $100 price is still shown."

### Bug Report
When updating an item's price, the cache invalidation service fails to invalidate related category aggregate caches, resulting in stale catalog listings.

### Steps to Reproduce
1. Update a product price via `update_product_price(db, cache, "P10", "CAT2", 60)`.
2. Inspect the keys purged from the cache layer.
3. Observe that category collection cache entries remain untouched.

### Expected Behaviour
Price updates must invalidate both the individual product cache key (`product:{product_id}`) and the associated category listing cache key (`category:{category_id}`).

### Actual Behaviour
Only the single product cache entry is invalidated, leaving collection views serving stale prices.

### Starter Files
`pricing_service.py` - Handles price updates and cache invalidation.

### Task
Modify `update_product_price` in `pricing_service.py` to invalidate both the product key and its parent category key.

### Acceptance Criteria
1. `update_product_price({}, cache, "P10", "CAT2", 60)` invalidates both `'product:P10'` and `'category:CAT2'`.

### Constraints
- `product_id` and `category_id` are alphanumeric strings.
- `new_price` is a positive numeric value.
- Both cache entries must be purged in the cache layer.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'pricing_service.py',
            'content': '''def update_product_price(db, cache, product_id, category_id, new_price):
    # Update database
    db[product_id] = {"price": new_price, "category": category_id}
    # Invalidate individual item cache
    cache.delete(f"product:{product_id}")
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Invalidate both product and category keys', 'input': '''class MockCache:
    def __init__(self): self.deleted = []
    def delete(self, key): self.deleted.append(key)
c = MockCache()
update_product_price({}, c, "P10", "CAT2", 60)
"category:CAT2" in c.deleted and "product:P10" in c.deleted''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': '',
        'suspected_component': 'pricing_service.py',
        'ai_suggestions': [
            'Add `cache.delete(f"category:{category_id}")` alongside the product cache deletion.'
        ],
        'topics': ['Caching', 'Cache Invalidation', 'Data Consistency'],
        'skills_tested': ['Python', 'Caching'],
        'prerequisites': ['Cache Invalidation Patterns'],
        'status': 'published'
    })

    # 18. Pagination produces duplicates when sorting is applied
    challenges.append({
        'id': 18,
        'title': '[CODE-M03] Pagination Produces Duplicates When Sorting is Applied',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Users browsing the trending feed reported that certain posts appeared on page 1 and then appeared again at the top of page 2, while other posts were skipped entirely."

### Bug Report
When multiple posts share the same upvote count, pagination ordering is non-deterministic, causing posts to shift positions and duplicate across pagination windows.

### Steps to Reproduce
1. Query page 1 with `page_size=2` for a list of posts with tied upvote counts.
2. Query page 2 with `page_size=2`.
3. Compare the post IDs across both pages.
4. Observe that duplicate IDs appear across consecutive pages.

### Expected Behaviour
Posts must be deterministically sorted with highest upvotes first, using post `id` as an ascending tie-breaker for identical upvote counts.

### Actual Behaviour
Sorting relies solely on the upvotes metric without a unique secondary tie-breaker, resulting in unstable page windows.

### Starter Files
`paginator.py` - Sorts and chunks social feed items into paginated slices.

### Task
Update `sort_and_paginate_posts` in `paginator.py` to introduce post `id` as a secondary sorting criterion.

### Acceptance Criteria
1. `[p["id"] for p in sort_and_paginate_posts(posts, page=1, page_size=2)]` returns `[1, 4]`.
2. `[p["id"] for p in sort_and_paginate_posts(posts, page=2, page_size=2)]` returns `[2, 3]`.

### Constraints
- `posts` is a list of dictionaries with `'id'` (int) and `'upvotes'` (int).
- Primary sort is descending by `upvotes`; secondary sort is ascending by `id`.
- `page >= 1` and `page_size >= 1`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'paginator.py',
            'content': '''def sort_and_paginate_posts(posts, page=1, page_size=2):
    sorted_posts = sorted(posts, key=lambda p: p["upvotes"], reverse=True)
    start = (page - 1) * page_size
    return sorted_posts[start:start + page_size]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Deterministic sort with tie-breaker', 'input': '''posts = [
    {"id": 3, "upvotes": 5},
    {"id": 1, "upvotes": 5},
    {"id": 2, "upvotes": 5},
    {"id": 4, "upvotes": 10}
]
p1 = sort_and_paginate_posts(posts, page=1, page_size=2)
p2 = sort_and_paginate_posts(posts, page=2, page_size=2)
# Post 4 is first, then 1, then 2, 3
[p["id"] for p in p1] == [4, 1] and [p["id"] for p in p2] == [2, 3]''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'sorted_posts = sorted(posts, key=lambda p: p["upvotes"], reverse=True)',
        'suspected_component': 'paginator.py',
        'ai_suggestions': [
            'Use a tuple key for sorting: `key=lambda p: (-p["upvotes"], p["id"])`.'
        ],
        'topics': ['Sorting', 'Pagination', 'Determinism'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Python Sorting Tuples'],
        'status': 'published'
    })

    # 19. A webhook handler processes the same event more than once
    challenges.append({
        'id': 19,
        'title': '[CODE-M04] A Webhook Handler Processes the Same Event More Than Once',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Warehouse operators reported duplicate dispatch labels printed for identical orders whenever the payment provider resent webhook delivery events."

### Bug Report
The webhook handler processes events unconditionally without idempotency tracking, resulting in duplicate fulfillment actions when external providers retry webhook delivery.

### Steps to Reproduce
1. Call `handle_webhook_event({"id": "evt_1", "order_id": "101"}, processed, actions)`.
2. Call `handle_webhook_event` again with the identical event payload.
3. Inspect the `actions` log.
4. Observe duplicate fulfillment actions recorded for the same event ID.

### Expected Behaviour
When an event ID has already been recorded in `processed_events`, the handler must return `'ALREADY_PROCESSED'` and take no fulfillment actions.

### Actual Behaviour
Every incoming webhook event is processed and added to `order_actions` regardless of whether it was already processed.

### Starter Files
`webhook_dispatcher.py` - Ingests external webhook events and triggers downstream order fulfillment.

### Task
Add an idempotency check in `handle_webhook_event` using `processed_events` to ignore duplicate deliveries.

### Acceptance Criteria
1. Processing a new event returns `'PROCESSED'` and records the fulfillment action.
2. Processing a duplicate event returns `'ALREADY_PROCESSED'` and does not re-add to `order_actions`.

### Constraints
- `event` is a dictionary containing `'id'` and `'order_id'`.
- `processed_events` is a `set` of event ID strings.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'webhook_dispatcher.py',
            'content': '''def handle_webhook_event(event, processed_events, order_actions):
    event_id = event.get("id")
    order_actions.append(f"FULFILL_{event.get('order_id')}")
    return "PROCESSED"'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Duplicate event skipped', 'input': '''processed = set()
actions = []
r1 = handle_webhook_event({"id": "evt_1", "order_id": "101"}, processed, actions)
r2 = handle_webhook_event({"id": "evt_1", "order_id": "101"}, processed, actions)
(r1 == "PROCESSED" and r2 == "ALREADY_PROCESSED" and len(actions) == 1)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'order_actions.append(f"FULFILL_{event.get(\'order_id\')}")',
        'suspected_component': 'webhook_dispatcher.py',
        'ai_suggestions': [
            'Add `if event_id in processed_events: return "ALREADY_PROCESSED"`.',
            'Add `processed_events.add(event_id)` before fulfilling the order.'
        ],
        'topics': ['Webhooks', 'Idempotency', 'Deduplication'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Sets', 'Idempotent Handlers'],
        'status': 'published'
    })

    # 20. Concurrent updates overwrite newer user preferences
    challenges.append({
        'id': 20,
        'title': '[CODE-M05] Concurrent Updates Overwrite Newer User Preferences',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A user reported that changing their dark mode setting reverted their newly updated notification email address because an older browser tab saved right after."

### Bug Report
The preference service lacks optimistic concurrency control, allowing stale client updates with lower version numbers to overwrite more recent database changes.

### Steps to Reproduce
1. Initialize a record with `version: 5`.
2. Attempt an update with a payload carrying `version: 3`.
3. Inspect the result and the record's current state.
4. Observe that the stale payload overwrote the newer record.

### Expected Behaviour
Updates must only be applied if `incoming_update['version'] > current_record['version']`, returning `True`; otherwise return `False` and leave the record unmutated.

### Actual Behaviour
Incoming payloads overwrite the current record unconditionally, disregarding version numbers.

### Starter Files
`preference_manager.py` - Updates user account preferences with optimistic concurrency control.

### Task
Implement optimistic concurrency version checks in `update_user_preferences`.

### Acceptance Criteria
1. `update_user_preferences({"theme": "dark", "version": 5}, {"theme": "light", "version": 3})` returns `False`.
2. `update_user_preferences({"theme": "dark", "version": 5}, {"theme": "solarized", "version": 6})` returns `True`.

### Constraints
- `current_record` and `incoming_update` contain an integer `'version'` field.
- Updates must only apply when incoming version is strictly greater than current version.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'preference_manager.py',
            'content': '''def update_user_preferences(current_record, incoming_update):
    current_record.update(incoming_update)
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Stale version rejected', 'input': '''current = {"theme": "dark", "version": 5}
stale = {"theme": "light", "version": 3}
applied = update_user_preferences(current, stale)
(applied is False and current["theme"] == "dark")''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Newer version accepted', 'input': '''current = {"theme": "dark", "version": 5}
newer = {"theme": "solarized", "version": 6}
applied = update_user_preferences(current, newer)
(applied is True and current["theme"] == "solarized" and current["version"] == 6)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'current_record.update(incoming_update)\n    return True',
        'suspected_component': 'preference_manager.py',
        'ai_suggestions': [
            'Compare `incoming_update.get("version", 0)` with `current_record.get("version", 0)`.',
            'If incoming is less than or equal to current, return False.'
        ],
        'topics': ['Optimistic Locking', 'Concurrency', 'Versioning'],
        'skills_tested': ['Python', 'Concurrency', 'Backend'],
        'prerequisites': ['Optimistic Concurrency Control'],
        'status': 'published'
    })

    # 21. Timezone conversion breaks scheduled notifications
    challenges.append({
        'id': 21,
        'title': '[CODE-M06] Timezone Conversion Breaks Scheduled Notifications',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Automated database maintenance notifications scheduled for 8:00 AM New York time (UTC-5) were dispatched at 3:00 AM instead of 1:00 PM UTC."

### Bug Report
The timezone converter adds the local UTC offset to the target hour instead of subtracting it, shifting scheduled jobs in the reverse direction.

### Steps to Reproduce
1. Call `convert_local_to_utc_hour(8, -5)`.
2. Inspect the converted UTC hour.
3. Observe that the calculation produces an hour that moves earlier instead of later.

### Expected Behaviour
Converting local hour to UTC requires subtracting the UTC offset: `(local_hour - utc_offset_hours) % 24`.

### Actual Behaviour
The formula adds the offset, causing negative offsets (Western Hemisphere) to shift earlier instead of later.

### Starter Files
`scheduler.py` - Converts localized job schedules into standardized UTC hours.

### Task
Fix the hour conversion formula in `scheduler.py` to correctly calculate UTC hours.

### Acceptance Criteria
1. `convert_local_to_utc_hour(8, -5)` returns `13`.
2. `convert_local_to_utc_hour(8, 9)` returns `23`.
3. `convert_local_to_utc_hour(8, 0)` returns `8`.

### Constraints
- `local_hour` is an integer `0 <= local_hour <= 23`.
- `utc_offset_hours` is an integer between `-12` and `14`.
- Returned value is an integer `0 <= hour <= 23`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'scheduler.py',
            'content': '''def convert_local_to_utc_hour(local_hour, utc_offset_hours):
    # e.g. for UTC-5 (offset -5), it should add 5 to local hour to get UTC
    return (local_hour + utc_offset_hours) % 24'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: NYC (UTC-5) 8am local -> 1pm UTC', 'input': 'convert_local_to_utc_hour(8, -5)', 'expected': '13', 'hidden': False},
            {'id': 2, 'name': 'Visible: Tokyo (UTC+9) 8am local -> 11pm previous day (23)', 'input': 'convert_local_to_utc_hour(8, 9)', 'expected': '23', 'hidden': False},
            {'id': 3, 'name': 'Hidden: London (UTC+0) 8am -> 8am', 'input': 'convert_local_to_utc_hour(8, 0)', 'expected': '8', 'hidden': True}
        ],
        'bug_signature': 'return (local_hour + utc_offset_hours) % 24',
        'suspected_component': 'scheduler.py',
        'ai_suggestions': [
            'Remember: `UTC = Local - Offset`. For UTC-5, `8 - (-5) = 13`.',
            'Consider both the sign of the timezone offset and 24-hour wrap-around boundaries when converting local time to UTC.'
        ],
        'topics': ['Timezones', 'Datetime', 'Scheduling'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['UTC and Timezones'],
        'status': 'published'
    })

    # 22. An API client incorrectly handles HTTP 429 responses
    challenges.append({
        'id': 22,
        'title': '[CODE-M07] An API Client Incorrectly Handles HTTP 429 Responses',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"The market ingestion daemon crashed during peak trading hours when a partner API returned HTTP 429 without the optional Retry-After response header."

### Bug Report
The rate limit delay parser accesses headers via direct key indexing, crashing with a KeyError when upstream servers omit the Retry-After header.

### Steps to Reproduce
1. Call `parse_rate_limit_delay({}, attempt=1)` with empty headers.
2. Observe that an unhandled KeyError crashes the parser.

### Expected Behaviour
If `Retry-After` is missing or invalid, fall back to exponential backoff `min(2 ** attempt, 30)` seconds.

### Actual Behaviour
Direct dictionary lookup raises an unhandled KeyError when the header is absent.

### Starter Files
`http_client.py` - Handles upstream rate limit response headers and backoff calculations.

### Task
Update `parse_rate_limit_delay` in `http_client.py` to read `Retry-After` safely and apply exponential backoff fallback.

### Acceptance Criteria
1. `parse_rate_limit_delay({"Retry-After": "5"}, 1)` returns `5`.
2. `parse_rate_limit_delay({}, 1)` returns `2`.
3. `parse_rate_limit_delay({}, 5)` returns `30`.

### Constraints
- `response_headers` is a dictionary of string header pairs.
- `attempt` is a positive integer.
- Fallback delay is capped at `30` seconds.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'http_client.py',
            'content': '''def parse_rate_limit_delay(response_headers, attempt=1):
    raw_delay = response_headers["Retry-After"]
    return int(raw_delay)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Valid Retry-After header', 'input': 'parse_rate_limit_delay({"Retry-After": "5"}, 1)', 'expected': '5', 'hidden': False},
            {'id': 2, 'name': 'Visible: Missing header uses exponential backoff', 'input': 'parse_rate_limit_delay({}, 3)', 'expected': '8', 'hidden': False},
            {'id': 3, 'name': 'Hidden: Non-numeric header fallback', 'input': 'parse_rate_limit_delay({"Retry-After": "invalid"}, 2)', 'expected': '4', 'hidden': True}
        ],
        'bug_signature': 'raw_delay = response_headers["Retry-After"]',
        'suspected_component': 'http_client.py',
        'ai_suggestions': [
            'Use `raw = response_headers.get("Retry-After")`.',
            'If `raw` is a digit, return `int(raw)`. Otherwise return `min(60, 2 ** attempt)`.'
        ],
        'topics': ['HTTP', 'Rate Limiting', 'Resilience'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['HTTP Headers', 'Error Handling'],
        'status': 'published'
    })

    # 23. A file-processing pipeline silently drops malformed records
    challenges.append({
        'id': 23,
        'title': '[CODE-M08] A File-Processing Pipeline Silently Drops Malformed Records',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A payroll specialist discovered that 45 contractor timesheets vanished from the weekly payroll reconciliation report with zero error logs."

### Bug Report
The timesheet ingestion pipeline uses a bare exception catch block that discards malformed records silently without appending them to the quarantine buffer.

### Steps to Reproduce
1. Submit a batch containing valid records and one record with invalid hours (e.g. `{"emp_id": "E2", "hours": "forty"}`).
2. Call `process_timesheets(rows)`.
3. Inspect `res["quarantined"]`.
4. Observe that the quarantine collection is empty despite the malformed record.

### Expected Behaviour
Records with invalid numeric hours must be captured in `quarantined` with the original record and error message.

### Actual Behaviour
Malformed records are silently swallowed by an empty `except` block, losing data silently.

### Starter Files
`pipeline.py` - Ingests timesheet data, validating numeric hours and separating invalid records.

### Task
Modify `process_timesheets` in `pipeline.py` to route invalid records to `quarantined`.

### Acceptance Criteria
1. Batches with invalid hours route malformed entries to `quarantined`.
2. Valid entries have hours converted to float in `valid`.

### Constraints
- `rows` is a list of dictionaries with `'emp_id'` and `'hours'`.
- Quarantined items must contain `record` and `error` keys.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'pipeline.py',
            'content': '''def process_timesheets(rows):
    valid_records = []
    quarantined_records = []
    for r in rows:
        try:
            hours = float(r["hours"])
            valid_records.append({"emp_id": r["emp_id"], "hours": hours})
        except Exception:
            pass
    return {"valid": valid_records, "quarantined": quarantined_records}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Malformed row quarantined', 'input': '''res = process_timesheets([{"emp_id": "E1", "hours": "40"}, {"emp_id": "E2", "hours": "forty"}])
(len(res["valid"]) == 1 and len(res["quarantined"]) == 1 and res["quarantined"][0]["record"]["emp_id"] == "E2")''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'except Exception:\n            pass',
        'suspected_component': 'pipeline.py',
        'ai_suggestions': [
            'In the except block, record the failure: `quarantined_records.append({"record": r, "error": str(e)})`.'
        ],
        'topics': ['Data Pipelines', 'Error Handling', 'Auditability'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Exception Handling'],
        'status': 'published'
    })

    # 24. A background worker loses failed jobs
    challenges.append({
        'id': 24,
        'title': '[CODE-M09] A Background Worker Loses Failed Jobs',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Customer order notification emails were permanently lost during a database outage because background jobs were acknowledged from the queue before execution finished."

### Bug Report
The background worker acknowledges jobs immediately upon receipt before executing the job handler, preventing retries or dead-letter queue routing if execution fails.

### Steps to Reproduce
1. Call `execute_job(queue, {"id": "JOB-1"}, fail_fn)` with a function that raises an exception.
2. Inspect queue acknowledgments and dead-letter queue.
3. Observe that the failed job was acknowledged before execution and not routed to the DLQ.

### Expected Behaviour
Acknowledge the job only after successful execution; if an exception occurs, route the job to `send_to_dlq(job, error)`.

### Actual Behaviour
Pre-acknowledging jobs removes them from queue visibility prior to processing.

### Starter Files
`worker_queue.py` - Manages task execution lifecycle, acknowledgments, and dead-letter queues.

### Task
Refactor `execute_job` in `worker_queue.py` to acknowledge only upon success and forward failures to the dead-letter queue.

### Acceptance Criteria
1. Failed jobs are forwarded to `send_to_dlq`.
2. Succeeded jobs are acknowledged via `ack`.

### Constraints
- `queue` implements `ack(job_id)` and `send_to_dlq(job, error)`.
- Returns `True` on success, `False` on failure.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'worker_queue.py',
            'content': '''def execute_job(queue, job, job_fn):
    queue.ack(job["id"])
    job_fn(job)
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Failed job sent to DLQ', 'input': '''class MockQueue:
    def __init__(self): self.acked = []; self.dlq = []
    def ack(self, jid): self.acked.append(jid)
    def send_to_dlq(self, j, err): self.dlq.append((j["id"], err))

q = MockQueue()
def fail_fn(j): raise RuntimeError("Database down")
execute_job(q, {"id": "JOB-1"}, fail_fn)
(len(q.acked) == 0 and len(q.dlq) == 1 and q.dlq[0][0] == "JOB-1")''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'queue.ack(job["id"])\n    job_fn(job)',
        'suspected_component': 'worker_queue.py',
        'ai_suggestions': [
            'Wrap `job_fn(job)` in try/except.',
            'Call `queue.ack(job["id"])` on success, `queue.send_to_dlq(job, str(e))` on exception.'
        ],
        'topics': ['Queues', 'Resilience', 'Dead-Letter Queue'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Try/Except Blocks'],
        'status': 'published'
    })

    # 25. A database transaction partially updates related records
    challenges.append({
        'id': 25,
        'title': '[CODE-M10] A Database Transaction Partially Updates Related Records',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Transactions',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A user attempted to transfer $100 to a mistyped account number. Their balance was deducted immediately, but the funds vanished because the destination account did not exist."

### Bug Report
The fund transfer function mutates the sender account balance before verifying that the recipient account exists in the ledger, causing ledger imbalance.

### Steps to Reproduce
1. Initialize accounts `{"ACC_A": 500}`.
2. Call `transfer_funds(accounts, "ACC_A", "ACC_NONEXISTENT", 100)`.
3. Inspect `accounts["ACC_A"]`.
4. Observe that the sender account balance was decremented even though the destination was invalid.

### Expected Behaviour
Validate that both sender and recipient accounts exist and sender has sufficient balance before modifying any account balances.

### Actual Behaviour
Funds are deducted from the sender prior to recipient validation, corrupting ledger integrity on invalid targets.

### Starter Files
`account_transfer.py` - Processes atomic ledger fund transfers between accounts.

### Task
Modify `transfer_funds` in `account_transfer.py` to validate all conditions before mutating balances.

### Acceptance Criteria
1. Transferring to a non-existent recipient returns `False` and leaves sender balance unchanged.
2. Transferring more than available balance returns `False`.
3. Valid transfers update both accounts and return `True`.

### Constraints
- `accounts` is a dictionary mapping account IDs to numeric balances.
- All balance operations must be atomic (either both update or neither).
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'account_transfer.py',
            'content': '''def transfer_funds(balances, sender, receiver, amount):
    if balances.get(sender, 0) < amount:
        raise ValueError("Insufficient funds")
    # Step 1: Debit sender
    balances[sender] -= amount
    # Step 2: Credit receiver (may throw if receiver invalid)
    if receiver not in balances:
        raise KeyError(f"Receiver {receiver} not found")
    balances[receiver] += amount
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Sender balance restored on receiver failure', 'input': '''balances = {"Alice": 200}
try:
    transfer_funds(balances, "Alice", "NonExistent", 50)
except KeyError:
    pass
balances["Alice"] == 200''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Successful transfer', 'input': '''balances = {"Alice": 200, "Bob": 50}
transfer_funds(balances, "Alice", "Bob", 50)
(balances["Alice"] == 150 and balances["Bob"] == 100)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'if receiver not in balances:\n        return False',
        'suspected_component': 'account_transfer.py',
        'ai_suggestions': [
            'Before raising KeyError, rollback the sender: `balances[sender] += amount`.'
        ],
        'topics': ['Transactions', 'Atomicity', 'Rollback'],
        'skills_tested': ['Python', 'Backend', 'Transactions'],
        'prerequisites': ['Atomicity and Transactions'],
        'status': 'published'
    })

    # 26. An asynchronous request returns stale data
    challenges.append({
        'id': 26,
        'title': '[CODE-M11] An Asynchronous Request Returns Stale Data',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Users typing fast in the document search box noticed that query results frequently reverted back to older search terms after the user had already typed a new query."

### Bug Report
Out-of-order network responses overwrite newer query results with stale data due to missing sequence verification in the client response store.

### Steps to Reproduce
1. Call `apply_response(1, "stale_react")`.
2. Call `apply_response(2, "fresh_python")`.
3. Call delayed response `apply_response(1, "late_stale_react")`.
4. Inspect `current_result`.
5. Observe that the stale response overwrote the newer response.

### Expected Behaviour
Responses with sequence IDs strictly less than `self.latest_issued_seq` must be discarded without mutating `current_result`.

### Actual Behaviour
Every incoming response overwrites `current_result` in network arrival order.

### Starter Files
`data_fetcher.py` - Stores and resolves asynchronous search result payloads.

### Task
Implement sequence checks in `AsyncResultStore.apply_response` in `data_fetcher.py` to discard out-of-order responses.

### Acceptance Criteria
1. Responses with sequence IDs `>= latest_issued_seq` update `current_result` and advance the sequence.
2. Stale responses with older sequence IDs return `False` and do not alter `current_result`.

### Constraints
- `response_seq_id` is a monotonically increasing integer.
- Ignore responses where `response_seq_id < latest_issued_seq`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'data_fetcher.py',
            'content': '''class AsyncResultStore:
    def __init__(self):
        self.current_result = None
        self.latest_issued_seq = 0

    def apply_response(self, response_seq_id, data):
        self.current_result = data
        return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Stale response discarded', 'input': '''store = AsyncResultStore()
store.latest_issued_seq = 2
store.apply_response(1, "stale_react")
store.apply_response(2, "fresh_python")
store.apply_response(1, "late_stale_react")
store.current_result == "fresh_python"''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'def apply_response(self, response_seq_id, data):\n        self.current_result = data\n        return True',
        'suspected_component': 'data_fetcher.py',
        'ai_suggestions': [
            'Add `if response_seq_id < self.latest_issued_seq: return False` before updating `self.current_result`.'
        ],
        'topics': ['Race Conditions', 'Async', 'Sequence Ordering'],
        'skills_tested': ['Python', 'Concurrency'],
        'prerequisites': ['Race Conditions'],
        'status': 'published'
    })

    # 27. A token refresh process creates intermittent authentication failures
    challenges.append({
        'id': 27,
        'title': '[CODE-M12] A Token Refresh Process Creates Intermittent Authentication Failures',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Authentication',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Our identity provider rate-limited our production backend after 1,000 concurrent API requests simultaneously triggered 1,000 independent OAuth token refresh calls."

### Bug Report
The token manager requests a new authorization token from the auth provider on every request without caching valid tokens until expiration.

### Steps to Reproduce
1. Initialize `mgr = TokenManager(mock_refresh)`.
2. Call `mgr.get_token()` twice in immediate succession.
3. Check the invocation count of `mock_refresh`.
4. Observe that the refresh function was invoked on each call.

### Expected Behaviour
When a valid cached token exists and has not expired, return the cached token without invoking `refresh_fn`.

### Actual Behaviour
A new token is fetched unconditionally on every `get_token` call.

### Starter Files
`token_refresh.py` - Manages OAuth access tokens and token renewal caching.

### Task
Implement token caching with expiration tracking in `token_refresh.py`.

### Acceptance Criteria
1. Repeated calls to `get_token()` within token TTL reuse the cached token.
2. Refresh is invoked only when no token is cached or the token has expired.

### Constraints
- Cache TTL is 300 seconds.
- Return the cached token string.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'token_refresh.py',
            'content': '''class TokenManager:
    def __init__(self, refresh_fn):
        self.refresh_fn = refresh_fn
        self.access_token = None
        self.is_refreshing = False

    def get_token(self):
        self.access_token = self.refresh_fn()
        return self.access_token'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Reuses cached token when valid', 'input': '''refresh_count = 0
def mock_refresh():
    global refresh_count
    refresh_count += 1
    return f"token_{refresh_count}"

mgr = TokenManager(mock_refresh)
# If token exists, return it without calling refresh_fn again
t1 = mgr.get_token()
t2 = mgr.get_token()
(t1 == t2 and refresh_count == 1)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'self.access_token = self.refresh_fn()',
        'suspected_component': 'token_refresh.py',
        'ai_suggestions': [
            'Check `if self.access_token: return self.access_token` before calling `self.refresh_fn()`.'
        ],
        'topics': ['Authentication', 'Token Management', 'Concurrency'],
        'skills_tested': ['Python', 'Backend', 'Security'],
        'prerequisites': ['OAuth Tokens'],
        'status': 'published'
    })

    # 28. An incorrect merge algorithm loses configuration fields
    challenges.append({
        'id': 28,
        'title': '[CODE-M13] An Incorrect Merge Algorithm Loses Configuration Fields',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Deploying to staging caused service startup failures because staging environment overrides for `db.port` completely erased the default `db.host` setting."

### Bug Report
The configuration loader performs shallow dictionary merging, replacing entire nested configuration sections when overriding individual nested properties.

### Steps to Reproduce
1. Define base config `{"db": {"host": "localhost", "port": 5432}}`.
2. Override with `{"db": {"port": 5433}}`.
3. Call `deep_merge(base, override)`.
4. Inspect `res["db"]`.
5. Observe that `host` was erased and only `port` remains.

### Expected Behaviour
Nested dictionary keys must be recursively merged so sibling properties in nested objects are retained.

### Actual Behaviour
Shallow dictionary updates overwrite entire sub-dictionaries when keys collide.

### Starter Files
`config_merger.py` - Merges layered application configurations across environments.

### Task
Implement recursive dictionary merging in `deep_merge` in `config_merger.py`.

### Acceptance Criteria
1. `deep_merge(base, override)["db"]["port"]` returns `5433`.
2. `deep_merge(base, override)["db"]["host"]` returns `'localhost'`.

### Constraints
- `base` and `override` are dictionaries with arbitrary nesting.
- Non-conflicting keys must be preserved.
- Sibling nested dictionary values must not be lost.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'config_merger.py',
            'content': '''def deep_merge(base, override):
    result = base.copy()
    result.update(override)
    return result'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Sibling nested keys preserved', 'input': '''base = {"db": {"host": "localhost", "port": 5432}}
override = {"db": {"port": 5433}}
res = deep_merge(base, override)
(res["db"]["host"] == "localhost" and res["db"]["port"] == 5433)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'result.update(override)\n    return result',
        'suspected_component': 'config_merger.py',
        'ai_suggestions': [
            'Iterate through `override.items()`. If key is in `base` and both values are dictionaries, recursively merge them.',
            'Otherwise, assign `override[key]`.'
        ],
        'topics': ['Deep Merge', 'Recursion', 'Configuration'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Recursion', 'Dictionaries'],
        'status': 'published'
    })

    # 29. An inventory update produces incorrect stock totals
    challenges.append({
        'id': 29,
        'title': '[CODE-M14] An Inventory Update Produces Incorrect Stock Totals',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"During a Black Friday flash sale, our fulfillment team noticed an item had an inventory level of -14, resulting in 14 orders that could not be fulfilled."

### Bug Report
The inventory decrement routine performs unconditional subtraction without validating stock availability, allowing stock balances to drop below zero.

### Steps to Reproduce
1. Initialize stock `{"SKU1": 2}`.
2. Attempt to decrement 5 units via `decrement_stock(inv, "SKU1", 5)`.
3. Observe that stock goes negative instead of raising a ValueError.

### Expected Behaviour
If requested quantity exceeds available stock, raise a `ValueError("Insufficient stock")` and do not mutate stock.

### Actual Behaviour
The function subtracts the requested quantity unconditionally, creating negative stock balances.

### Starter Files
`inventory_service.py` - Decrements warehouse inventory on purchase orders.

### Task
Add inventory validation in `decrement_stock` to reject overdrawn orders.

### Acceptance Criteria
1. Decrementing within available quantity returns the updated stock level.
2. Decrementing more than available stock raises `ValueError`.

### Constraints
- `inventory` is a dictionary of string item IDs to integer stock counts.
- `qty` is a positive integer.
- Stock must never become negative.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'inventory_service.py',
            'content': '''def decrement_stock(inventory, item_id, qty):
    inventory[item_id] -= qty
    return inventory[item_id]'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Oversell raises ValueError', 'input': '''inv = {"SKU1": 2}
try:
    decrement_stock(inv, "SKU1", 5)
    raised = False
except ValueError:
    raised = True
(raised and inv["SKU1"] == 2)''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Valid decrement', 'input': '''inv = {"SKU1": 10}
decrement_stock(inv, "SKU1", 3) == 7''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'inventory[item_id] -= qty\n    return inventory[item_id]',
        'suspected_component': 'inventory_service.py',
        'ai_suggestions': [
            'Add check `if inventory.get(item_id, 0) < qty: raise ValueError("Insufficient stock")` before subtracting.'
        ],
        'topics': ['Inventory', 'Validation', 'Business Logic'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Defensive Programming'],
        'status': 'published'
    })

    # 30. A CSV export corrupts embedded commas and newlines
    challenges.append({
        'id': 30,
        'title': '[CODE-M15] A CSV Export Corrupts Embedded Commas and Newlines',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A financial analyst reported that customer reports failed to import into Excel because customer addresses containing commas shifted data into the wrong columns."

### Bug Report
The CSV export module concatenates strings with raw commas rather than using standard CSV quoting, corrupting rows containing commas or special characters.

### Steps to Reproduce
1. Call `export_to_csv_row(["Alice", "Hello, World", 100])`.
2. Inspect the resulting CSV row.
3. Observe that the string containing a comma is not enclosed in quotes, splitting it into two columns.

### Expected Behaviour
Fields containing commas or special characters must be properly escaped and quoted according to RFC 4180 standard.

### Actual Behaviour
Raw string concatenation produces unquoted delimiters, corrupting tabular data.

### Starter Files
`csv_exporter.py` - Exports data records into CSV formatted rows.

### Task
Use Python's `csv` module in `csv_exporter.py` to format CSV rows with standard escaping.

### Acceptance Criteria
1. Fields with embedded commas are properly quoted: `Alice,"Hello, World",100`.
2. Standard fields without commas are formatted cleanly.

### Constraints
- `fields` is a list of strings, integers, or floats.
- Returns a string ending with a newline `\n`.
- RFC 4180 compliant CSV formatting.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'csv_exporter.py',
            'content': '''def export_to_csv_row(fields):
    return ",".join(str(f) for f in fields) + "\\n"'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Escaped field with comma', 'input': '''res = export_to_csv_row(["Alice", "Hello, World", 100])
'"Hello, World"' in res''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'return ",".join(str(f) for f in fields) + "\\n"',
        'suspected_component': 'csv_exporter.py',
        'ai_suggestions': [
            'Import `csv` and `io`.',
            'Use `output = io.StringIO(); writer = csv.writer(output); writer.writerow(fields); return output.getvalue()`.'
        ],
        'topics': ['CSV', 'Export', 'RFC 4180'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Python CSV Module'],
        'status': 'published'
    })

    # 31. A batch processor mishandles partial failures
    challenges.append({
        'id': 31,
        'title': '[CODE-M16] A Batch Processor Mishandles Partial Failures',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A marketing blast to 500 customers stopped after only 12 emails were sent because one invalid email address caused the batch worker to crash."

### Bug Report
The batch notification processor lacks isolated error handling per item, causing the entire batch to abort when any single recipient fails.

### Steps to Reproduce
1. Provide a batch of 3 items where item 2 raises an exception in `send_fn`.
2. Call `process_batch(items, mock_send)`.
3. Observe that item 3 is never processed and the function crashes.

### Expected Behaviour
Individual item failures must be caught, logging the failed ID into `failed` and allowing the remaining items to process into `succeeded`.

### Actual Behaviour
An unhandled exception on an invalid item terminates batch execution prematurely.

### Starter Files
`batch_processor.py` - Processes batch notifications and isolates item-level failures.

### Task
Wrap per-item processing in `batch_processor.py` with exception handling to isolate errors.

### Acceptance Criteria
1. Valid items are recorded in `res["succeeded"]`.
2. Failed items are recorded in `res["failed"]` without aborting remaining items.

### Constraints
- `items` is a list of dictionaries with an `'id'` field.
- Returns `{"succeeded": [...], "failed": [...]}`.
- All items in the batch must be evaluated.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'batch_processor.py',
            'content': '''def process_batch(items, send_fn):
    succeeded = []
    failed = []
    for item in items:
        send_fn(item)
        succeeded.append(item["id"])
    return {"succeeded": succeeded, "failed": failed}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Sibling items processed despite middle failure', 'input': '''def mock_send(item):
    if item["id"] == 2: raise ValueError("Bad phone")
res = process_batch([{"id": 1}, {"id": 2}, {"id": 3}], mock_send)
(res["succeeded"] == [1, 3] and len(res["failed"]) == 1 and res["failed"][0]["id"] == 2)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'for item in items:\n        send_fn(item)',
        'suspected_component': 'batch_processor.py',
        'ai_suggestions': [
            'Wrap `send_fn(item)` in a try/except block inside the for loop.',
            'Append to `failed` list on error instead of terminating the loop.'
        ],
        'topics': ['Batch Processing', 'Resilience', 'Error Isolation'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Try/Except Blocks'],
        'status': 'published'
    })

    # 32. Incorrect pagination cursors produce infinite loops
    challenges.append({
        'id': 32,
        'title': '[CODE-M17] Incorrect Pagination Cursors Produce Infinite Loops',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"API monitoring alerted on an external partner making millions of consecutive pagination requests overnight because our API kept returning a next-page cursor after the last record."

### Bug Report
The pagination response builder generates a next-page cursor token even when the current page contains fewer records than the requested page size, trapping clients in an infinite loop.

### Steps to Reproduce
1. Call `build_page_response(records=[{"id": 1}], page_size=10, last_id=1)` with fewer records than `page_size`.
2. Inspect `res["next_cursor"]`.
3. Observe that a next-page cursor is returned instead of signaling dataset exhaustion with `None`.

### Expected Behaviour
When `len(records) < page_size`, the dataset is complete and `next_cursor` must be `None`.

### Actual Behaviour
An opaque next cursor is returned unconditionally regardless of whether the page is full.

### Starter Files
`cursor_paginator.py` - Formats paginated API responses and cursor tokens.

### Task
Update `build_page_response` in `cursor_paginator.py` to set `next_cursor = None` when records are exhausted.

### Acceptance Criteria
1. Slices with `len(records) < page_size` return `next_cursor: None`.
2. Full slices with `len(records) == page_size` return `next_cursor: "cur_<id>"`.

### Constraints
- `records` is a list of items.
- `page_size` is a positive integer.
- `last_id` is an integer or string identifier.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'cursor_paginator.py',
            'content': '''def build_page_response(records, page_size, last_id):
    next_cursor = f"cur_{last_id}"
    return {"records": records, "next_cursor": next_cursor}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Final page next_cursor is None', 'input': '''res = build_page_response([{"id": 1}], page_size=10, last_id=1)
res["next_cursor"] is None''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Full page generates next cursor', 'input': '''res = build_page_response(list(range(10)), page_size=10, last_id=10)
res["next_cursor"] == "cur_10"''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'def build_page_response(records, page_size, last_id):\n    next_cursor = f"cur_{last_id}"\n    return',
        'suspected_component': 'cursor_paginator.py',
        'ai_suggestions': [
            'Check: `next_cursor = f"cur_{last_id}" if len(records) == page_size else None`.'
        ],
        'topics': ['Pagination', 'Cursors', 'Infinite Loops'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Pagination Logic'],
        'status': 'published'
    })

    # 33. A data transformation fails for optional nested properties
    challenges.append({
        'id': 33,
        'title': '[CODE-M18] A Data Transformation Fails for Optional Nested Properties',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"New users were unable to view their profile dashboard because accounts created via social login without an address triggered a 500 error."

### Bug Report
The address formatting routine performs nested attribute lookups on optional address objects without null checks, raising unhandled TypeErrors.

### Steps to Reproduce
1. Call `format_postal_address({"name": "Alice", "address": None})`.
2. Observe that an unhandled TypeError crashes the formatter.

### Expected Behaviour
If `address` is missing or `None`, format the output with `'Unknown City'`: `f"{profile['name']}, Unknown City"`.

### Actual Behaviour
The function directly accesses `profile["address"]["city"]`, crashing when `address` is `None`.

### Starter Files
`transformer.py` - Enriches and formats user profile addresses.

### Task
Add defensive null checking for the `address` dictionary in `transformer.py`.

### Acceptance Criteria
1. Profiles with `address: None` return `'Alice, Unknown City'`.
2. Profiles with valid address dictionaries return `'Bob, Boston'`.

### Constraints
- `profile` is a dictionary containing `'name'` and optional `'address'`.
- Missing address or city defaults safely to `'Unknown City'`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'transformer.py',
            'content': '''def format_postal_address(profile):
    city = profile["address"]["city"]
    return f"{profile['name']}, {city}"'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Missing address safely handled', 'input': 'format_postal_address({"name": "Alice", "address": None})', 'expected': 'Alice, Unknown City', 'hidden': False},
            {'id': 2, 'name': 'Visible: Full address formatted', 'input': 'format_postal_address({"name": "Bob", "address": {"city": "Boston"}})', 'expected': 'Bob, Boston', 'hidden': False}
        ],
        'bug_signature': 'city = profile["address"]["city"]',
        'suspected_component': 'transformer.py',
        'ai_suggestions': [
            'Use safe navigation: `addr = profile.get("address") or {}`',
            'Then `city = addr.get("city", "Unknown City")`.'
        ],
        'topics': ['Data Transformation', 'Defensive Programming', 'Null Safety'],
        'skills_tested': ['Python', 'Data Processing'],
        'prerequisites': ['Safe Dictionary Access'],
        'status': 'published'
    })

    # 34. A rate limiter resets counters incorrectly
    challenges.append({
        'id': 34,
        'title': '[CODE-M19] A Rate Limiter Resets Counters Incorrectly',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Rate Limiting',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"API clients reported that their accounts were permanently locked out with HTTP 429 errors even after waiting hours between requests."

### Bug Report
The sliding window rate limiter counts all historical request timestamps without pruning expired timestamps outside the rolling window, permanently blocking clients once the limit is reached.

### Steps to Reproduce
1. Initialize `limiter = SlidingWindowLimiter(max_requests=2, window_size=60)`.
2. Submit requests at `t=10` and `t=20`.
3. Submit a request at `t=80` (where `t=10` is older than the 60-second window: 80 - 10 = 70 > 60).
4. Observe that the request at `t=80` is rejected because old timestamps were not evicted.

### Expected Behaviour
Requests older than `current_time - self.window_size` must be evicted from history before checking if current count is within limit.

### Actual Behaviour
The limiter accumulates timestamps indefinitely, locking out clients permanently.

### Starter Files
`rate_limiter.py` - Enforces rolling window request limits for API consumers.

### Task
Prune expired timestamps in `allow_request` in `rate_limiter.py`.

### Acceptance Criteria
1. Requests within a sliding window are limited to `max_requests`.
2. Expired timestamps are removed, allowing new requests once older requests age out.

### Constraints
- `max_requests` and `window_size` are positive integers.
- `current_time` is a monotonically non-decreasing timestamp.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'rate_limiter.py',
            'content': '''class SlidingWindowLimiter:
    def __init__(self, max_requests=100, window_size=60):
        self.max_requests = max_requests
        self.window_size = window_size
        self.history = []

    def allow_request(self, current_time):
        if len(self.history) >= self.max_requests:
            return False
        self.history.append(current_time)
        return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Expired timestamps pruned allowing new request', 'input': '''limiter = SlidingWindowLimiter(max_requests=2, window_size=60)
limiter.allow_request(10)
limiter.allow_request(20)
# At time 80, timestamp 10 is expired (80 - 10 = 70 > 60)
limiter.allow_request(80)''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Active window limit enforced', 'input': '''limiter = SlidingWindowLimiter(max_requests=2, window_size=60)
limiter.allow_request(10)
limiter.allow_request(20)
limiter.allow_request(30)''', 'expected': 'False', 'hidden': False}
        ],
        'bug_signature': 'if len(self.history) >= self.max_requests:\n            return False',
        'suspected_component': 'rate_limiter.py',
        'ai_suggestions': [
            'Before checking `len(self.history)`, prune old items: `self.history = [t for t in self.history if current_time - t < self.window_size]`.'
        ],
        'topics': ['Rate Limiting', 'Sliding Window', 'Algorithms'],
        'skills_tested': ['Python', 'Backend', 'Security'],
        'prerequisites': ['List Comprehensions', 'Timestamps'],
        'status': 'published'
    })

    # 35. An exception handler hides a meaningful application failure
    challenges.append({
        'id': 35,
        'title': '[CODE-M20] An Exception Handler Hides a Meaningful Application Failure',
        'difficulty': 'Medium',
        'technology': 'Python',
        'category': 'Error Handling',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Operations spent two days investigating an apparent user login failure storm, only to discover that our LDAP authentication server had been offline and errors were masked as bad passwords."

### Bug Report
The authentication wrapper catches generic exceptions indiscriminately, hiding critical network connection failures and misreporting infrastructure outages as invalid user credentials.

### Steps to Reproduce
1. Call `verify_credentials(mock_auth, "alice", "secret")` where `mock_auth` raises `ConnectionError("LDAP timeout")`.
2. Inspect the returned result.
3. Observe that the network failure was caught and concealed as `{"authenticated": False, "error": "Invalid credentials"}`.

### Expected Behaviour
Network failures such as `ConnectionError` must be allowed to propagate to trigger infrastructure alerts; only authentication validation failures should return unauthenticated status.

### Actual Behaviour
Catching generic `Exception` suppresses low-level connection errors and masks them as bad credentials.

### Starter Files
`service_client.py` - Wraps external authentication calls with error classification.

### Task
Refactor exception handling in `verify_credentials` in `service_client.py` to allow `ConnectionError` to re-raise.

### Acceptance Criteria
1. `ConnectionError` is raised out of the function during network failure.
2. Expected credential validation errors return `{"authenticated": False, "error": "Invalid credentials"}`.

### Constraints
- `auth_fn` is a callable accepting `(username, password)`.
- Infrastructure exceptions like `ConnectionError` must propagate unswallowed.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'service_client.py',
            'content': '''def verify_credentials(auth_fn, username, password):
    try:
        return auth_fn(username, password)
    except Exception:
        return {"authenticated": False, "error": "Invalid credentials"}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: ConnectionError re-raised', 'input': '''def mock_auth(u, p): raise ConnectionError("LDAP timeout")
try:
    verify_credentials(mock_auth, "alice", "secret")
    raised = False
except ConnectionError:
    raised = True
raised''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Bad credentials handled cleanly', 'input': '''def mock_auth(u, p): raise ValueError("Incorrect password")
verify_credentials(mock_auth, "alice", "wrong")["authenticated"]''', 'expected': 'False', 'hidden': False}
        ],
        'bug_signature': 'except Exception:\n        return False',
        'suspected_component': 'service_client.py',
        'ai_suggestions': [
            'Catch `ValueError` specifically for invalid credentials.',
            'Let `ConnectionError` or other exceptions propagate up.'
        ],
        'topics': ['Error Handling', 'Exceptions', 'Observability'],
        'skills_tested': ['Python', 'Error Handling', 'Backend'],
        'prerequisites': ['Exception Hierarchies'],
        'status': 'published'
    })

    return challenges
