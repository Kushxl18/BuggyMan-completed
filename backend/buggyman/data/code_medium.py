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
        'description': """### Company Scenario
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
""",
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
        'bug_signature': 'idempotency_key = f"idem_{uuid.uuid4().hex[:8]}"',
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'bug_signature': 'self.current_result = data\n        return True',
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
An admin panel exports user support feedback comments to CSV for analytical reporting in Excel.

### Bug Report
When user feedback contains commas or line breaks (e.g., `"Great service,\nfast delivery"`), the exported CSV breaks across lines and shifts columns in Excel.

### Steps to Reproduce
1. Export row with comment `"Great service,\nfast delivery"`.
2. Raw string join produces broken unquoted text.

### Expected Behavior
Fields with commas, quotes, or newlines must be enclosed in quotes according to RFC 4180.

### Actual Behavior
Naive string join `",".join(row)`.

### Impact
Corrupted spreadsheets in corporate accounting and analytics teams.

### Requirements
- Use Python standard library `csv.writer` and `io.StringIO` to format CSV rows properly.
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'bug_signature': 'next_cursor = f"cur_{last_id}"\n    return',
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
        'description': """### Company Scenario
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
""",
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
