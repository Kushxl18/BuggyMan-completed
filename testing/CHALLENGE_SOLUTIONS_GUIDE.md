# BuggyMan — 120 Real-World Software Bug Challenges & Solution Guide

This guide documents all 120 verified real-world engineering defects across Code Arena, SQL Lab, and Frontend Studio.

## Summary Distribution

| Arena | Easy | Medium | Hard | Total |
|---|---:|---:|---:|---:|
| **Code Arena (Python)** | 15 | 20 | 15 | **50** |
| **SQL Lab (SQLite / Relational)** | 10 | 15 | 10 | **35** |
| **Frontend Studio (React / CSS)** | 10 | 15 | 10 | **35** |
| **Total** | **35** | **50** | **35** | **120** |

---

### Challenge 1: [CODE-E01] API Pagination Skips the Final Record
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
When users navigate to the final page of audit logs, the last log entry is missing. For example, if there are 25 total entries and page size is 10, page 3 only shows 4 records instead of 5.

**Reference Solution Implementation:**
*pagination.py*:
```python
def paginate(items, page=1, page_size=10):
    if not items or page < 1 or page_size < 1:
        return []
    start = (page - 1) * page_size
    end = min(len(items), page * page_size)
    if start >= len(items):
        return []
    return items[start:end]
```

---

### Challenge 2: [CODE-E02] Base64 Cursor Encoding Breaks for Unicode Input
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
Pagination requests fail with HTTP 500 error `UnicodeEncodeError: 'ascii' codec can't encode characters` when paginating search results for non-English warehouse locations.

**Reference Solution Implementation:**
*cursor_encoder.py*:
```python
import base64

def encode_cursor(cursor_str):
    if cursor_str is None:
        return ""
    raw_bytes = cursor_str.encode("utf-8")
    return base64.urlsafe_b64encode(raw_bytes).decode("ascii")

def decode_cursor(encoded_str):
    if not encoded_str:
        return ""
    raw_bytes = base64.urlsafe_b64decode(encoded_str.encode("ascii"))
    return raw_bytes.decode("utf-8")
```

---

### Challenge 3: [CODE-E03] Empty API Responses Cause a Runtime Error
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Error Handling

**Bug Description & Root Cause:**
When market quotes are requested for a newly listed stock or after market close, the vendor API returns an empty payload `{"items": []}`. The parser throws `IndexError: list index out of range`, crashing the ticker worker.

**Reference Solution Implementation:**
*api_client.py*:
```python
def extract_latest_price(payload):
    if not isinstance(payload, dict):
        return {"price": 0.0, "status": "unavailable"}
    items = payload.get("items", [])
    if not items or not isinstance(items, list):
        return {"price": 0.0, "status": "unavailable"}
    return {"price": items[0].get("price", 0.0), "status": "active"}
```

---

### Challenge 4: [CODE-E04] Incorrect Date Parsing Shifts Records to the Wrong Day
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
A payment made on `05/11/2026` (5th of November) is categorized by the system as `2026-05-11` (11th of May), shifting end-of-year tax deductions into the wrong fiscal quarter.

**Reference Solution Implementation:**
*date_parser.py*:
```python
from datetime import datetime

def parse_transaction_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None
```

---

### Challenge 5: [CODE-E05] A Retry Counter Stops One Attempt Too Early
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
When `max_retries=3` is configured, logs show the client only performs 2 attempts total (1 initial + 1 retry) before giving up and flagging orders as failed.

**Reference Solution Implementation:**
*retry_handler.py*:
```python
def execute_with_retry(operation, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            return operation(attempt)
        except Exception:
            continue
    return None
```

---

### Challenge 6: [CODE-E06] Duplicate IDs Cause Incorrect Deduplication
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
When ingesting check-ins, patient records from Clinic B overwrite patient records from Clinic A whenever both clinics happen to issue ID `101`.

**Reference Solution Implementation:**
*deduplicator.py*:
```python
def deduplicate_records(records):
    seen = set()
    result = []
    for r in records:
        key = (r.get("clinic_id"), r.get("id"))
        if key not in seen:
            seen.add(key)
            result.append(r)
    return result
```

---

### Challenge 7: [CODE-E07] An Environment Variable Fallback Ignores Valid Configuration
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
When an operator sets `TIMEOUT_SECONDS=0` to disable timeouts for long-running batch ingestion, the application ignores `0` and falls back to default `30` seconds, causing premature batch termination.

**Reference Solution Implementation:**
*config_loader.py*:
```python
def get_timeout_seconds(env_dict=None):
    env = env_dict if env_dict is not None else {}
    val = env.get("TIMEOUT_SECONDS")
    if val is None or val == "":
        return 30
    return int(val)
```

---

### Challenge 8: [CODE-E08] An Incorrect Cache Key Returns Another Request's Result
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Caching

**Bug Description & Root Cause:**
User 42 belonging to Store A sees the exclusive VIP discount rates belonging to User 42 in Store B!

**Reference Solution Implementation:**
*cache_manager.py*:
```python
def generate_cache_key(store_id, user_id):
    return f"store:{store_id}:user:{user_id}"
```

---

### Challenge 9: [CODE-E09] Input Validation Rejects Valid Zero Values
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Validation

**Bug Description & Root Cause:**
When a warehouse manager enters `0` to indicate an item is completely out of stock, the API rejects the request with HTTP 400 `"Quantity is required"`.

**Reference Solution Implementation:**
*validator.py*:
```python
def validate_inventory_update(item_id, quantity):
    if not item_id:
        return (False, "Item ID is required")
    if quantity is None:
        return (False, "Quantity is required")
    if quantity < 0:
        return (False, "Quantity cannot be negative")
    return (True, "Valid")
```

---

### Challenge 10: [CODE-E10] A CSV Parser Mishandles Quoted Fields
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
An imported row `"John Doe","123 Maple St, Suite 4","Springfield"` is split into 4 columns instead of 3, corrupting the address and city fields.

**Reference Solution Implementation:**
*csv_parser.py*:
```python
import csv
import io

def parse_csv_row(row_str):
    if not row_str:
        return []
    reader = csv.reader(io.StringIO(row_str))
    for row in reader:
        return row
    return []
```

---

### Challenge 11: [CODE-E11] Sorting Produces Incorrect Results for Numeric Strings
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
Build numbers sort as `["1", "10", "100", "2", "20"]` instead of numeric order `["1", "2", "10", "20", "100"]`.

**Reference Solution Implementation:**
*sorter.py*:
```python
def sort_priority_levels(levels):
    return sorted(levels, key=lambda x: int(x) if str(x).isdigit() else x)
```

---

### Challenge 12: [CODE-E12] A Response Serializer Omits a Required Field
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
Mobile apps crash with `SchemaValidationError: Missing required property 'created_at'` when reading the `/api/v1/user` response.

**Reference Solution Implementation:**
*serializer.py*:
```python
def serialize_user_profile(user_model):
    if not user_model:
        return {}
    return {
        "id": user_model.get("id"),
        "username": user_model.get("username"),
        "email": user_model.get("email"),
        "created_at": user_model.get("created_at")
    }
```

---

### Challenge 13: [CODE-E13] An Incorrect Timeout Conversion Causes Premature Expiration
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
Users are logged out within 3.6 seconds of logging in!

**Reference Solution Implementation:**
*token_service.py*:
```python
def calculate_expiration(current_timestamp, seconds_to_live=3600):
    return current_timestamp + seconds_to_live
```

---

### Challenge 14: [CODE-E14] An Empty List Causes an Indexing Error
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Error Handling

**Bug Description & Root Cause:**
When worker polls an idle queue with no pending messages, it crashes with `IndexError: list index out of range` and exits.

**Reference Solution Implementation:**
*queue_processor.py*:
```python
def peek_next_job(queue):
    if not queue:
        return None
    return queue[0]
```

---

### Challenge 15: [CODE-E15] Incorrect Rounding Produces Wrong Invoice Totals
- **Difficulty:** Easy (100 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
Customer invoices show a total that is 1 cent off from payment gateway settlements due to rounding line-item tax amounts individually before summing them.

**Reference Solution Implementation:**
*invoice_calculator.py*:
```python
def calculate_total_tax(line_items, tax_rate=0.0825):
    if not line_items:
        return 0.0
    subtotal = sum(line_items)
    return round(subtotal * tax_rate, 2)
```

---

### Challenge 16: [CODE-M01] API Retries Accidentally Repeat a Non-Idempotent Operation
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
When network packets drop and the client retries the charge, customers are charged twice on their credit cards!

**Reference Solution Implementation:**
*payment_client.py*:
```python
import uuid

def charge_with_retry(gateway, order_id, amount, max_attempts=3):
    key = f"idem_{uuid.uuid4().hex}"
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            return gateway.charge(order_id, amount, key)
        except Exception:
            if attempts >= max_attempts:
                raise
    return None
```

---

### Challenge 17: [CODE-M02] Cache Invalidation Leaves Stale Product Prices
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Caching

**Bug Description & Root Cause:**
When an administrator edits a product price from $100 down to $60, the category browse page still shows the old $100 price for hours.

**Reference Solution Implementation:**
*pricing_service.py*:
```python
def update_product_price(db, cache, product_id, category_id, new_price):
    db[product_id] = {"price": new_price, "category": category_id}
    cache.delete(f"product:{product_id}")
    cache.delete(f"category:{category_id}")
    return True
```

---

### Challenge 18: [CODE-M03] Pagination Produces Duplicates When Sorting is Applied
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
When users scroll through the feed, the same post appears on both Page 1 and Page 2!

**Reference Solution Implementation:**
*paginator.py*:
```python
def paginate_sorted_records(records, offset=0, limit=10):
    sorted_records = sorted(records, key=lambda r: (r.get("priority", 0), r.get("id", 0)))
    return sorted_records[offset:offset + limit]
```

---

### Challenge 19: [CODE-M04] A Webhook Handler Processes the Same Event More Than Once
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
Stripe retries webhook delivery if an ACK is delayed. The handler processes the duplicate event and ships the order twice!

**Reference Solution Implementation:**
*webhook_dispatcher.py*:
```python
class WebhookDispatcher:
    def __init__(self, processed_ids=None):
        self.processed = processed_ids if processed_ids is not None else set()

    def handle_event(self, event, handler_fn):
        event_id = event.get("id")
        if event_id in self.processed:
            return False
        self.processed.add(event_id)
        handler_fn(event)
        return True
```

---

### Challenge 20: [CODE-M05] Concurrent Updates Overwrite Newer User Preferences
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
A user toggles dark mode at 10:00:05. A delayed sync request sent at 10:00:01 arrives late and overwrites the newer preference!

**Reference Solution Implementation:**
*preference_manager.py*:
```python
def update_user_preferences(current_prefs, update_payload):
    current_version = current_prefs.get("version", 0)
    update_version = update_payload.get("version", 0)
    if update_version <= current_version:
        return False
    current_prefs.update(update_payload)
    return True
```

---

### Challenge 21: [CODE-M06] Timezone Conversion Breaks Scheduled Notifications
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
Patients in New York (UTC-5) receive medication alerts at 03:00 AM in the middle of the night!

**Reference Solution Implementation:**
*scheduler.py*:
```python
def convert_local_to_utc_hour(local_hour, utc_offset_hours):
    return (local_hour - utc_offset_hours) % 24
```

---

### Challenge 22: [CODE-M07] An API Client Incorrectly Handles HTTP 429 Responses
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
When exchange returns HTTP 429 Too Many Requests with header `Retry-After: 5`, client crashes with `ValueError: could not convert string to float` when header is missing or non-numeric, or immediately hammers server with 0 delay.

**Reference Solution Implementation:**
*http_client.py*:
```python
def parse_rate_limit_delay(response_headers, attempt=1):
    val = response_headers.get("Retry-After")
    if val is not None:
        try:
            return max(1, int(val))
        except (ValueError, TypeError):
            pass
    return 2 ** attempt
```

---

### Challenge 23: [CODE-M08] A File-Processing Pipeline Silently Drops Malformed Records
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
When an employee enters their hours as `"forty"` instead of `40`, their entire timesheet is silently deleted without notifying HR!

**Reference Solution Implementation:**
*pipeline.py*:
```python
def process_pipeline_records(records):
    valid = []
    dropped = []
    for r in records:
        if isinstance(r, dict) and r.get("id") and r.get("email"):
            valid.append(r)
        else:
            dropped.append(r)
    return {"valid": valid, "dropped": dropped}
```

---

### Challenge 24: [CODE-M09] A Background Worker Loses Failed Jobs
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
When an unhandled database lock error occurs during job execution, the job vanishes forever instead of being sent to the Dead-Letter Queue (DLQ).

**Reference Solution Implementation:**
*worker_queue.py*:
```python
class WorkerQueue:
    def __init__(self):
        self.dead_letter_queue = []

    def handle_failed_job(self, job, error):
        self.dead_letter_queue.append({
            "job": job,
            "error": str(error)
        })
```

---

### Challenge 25: [CODE-M10] A Database Transaction Partially Updates Related Records
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Transactions

**Bug Description & Root Cause:**
$100 is deducted from Sender account, but a database constraint error occurs when crediting Receiver account. The transaction does not rollback, and $100 simply disappears into thin air!

**Reference Solution Implementation:**
*account_transfer.py*:
```python
def transfer_funds(ledger, source_id, dest_id, amount):
    if ledger.get_balance(source_id) < amount:
        return False
    with ledger.transaction():
        ledger.debit(source_id, amount)
        ledger.credit(dest_id, amount)
    return True
```

---

### Challenge 26: [CODE-M11] An Asynchronous Request Returns Stale Data
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
User quickly types "react", then deletes and types "python". The slower "react" request completes after "python", overwriting the search results with "react"!

**Reference Solution Implementation:**
*data_fetcher.py*:
```python
import asyncio

async def fetch_user_data(client, user_id):
    profile, perms = await asyncio.gather(
        client.get_profile(user_id),
        client.get_permissions(user_id)
    )
    return {"profile": profile, "permissions": perms}
```

---

### Challenge 27: [CODE-M12] A Token Refresh Process Creates Intermittent Authentication Failures
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Authentication

**Bug Description & Root Cause:**
When 5 API calls return 401 at the same millisecond, 5 separate refresh requests are launched concurrently. The authorization server detects reuse of the same refresh token and revokes user access entirely!

**Reference Solution Implementation:**
*token_refresh.py*:
```python
class TokenRefreshManager:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        self._refresh_lock = False

    def refresh(self):
        if self._refresh_lock:
            return self.auth_client.get_current_token()
        self._refresh_lock = True
        try:
            return self.auth_client.perform_refresh()
        finally:
            self._refresh_lock = False
```

---

### Challenge 28: [CODE-M13] An Incorrect Merge Algorithm Loses Configuration Fields
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
User supplies `{"database": {"port": 5433}}`. The merged config completely deletes `{"database": {"host": "localhost", "name": "prod"}}`!

**Reference Solution Implementation:**
*config_merger.py*:
```python
def deep_merge_configs(base, override):
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge_configs(result[k], v)
        else:
            result[k] = v
    return result
```

---

### Challenge 29: [CODE-M14] An Inventory Update Produces Incorrect Stock Totals
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
When available stock is 2 and customer orders 5, stock becomes `-3`, allowing customer to buy non-existent goods.

**Reference Solution Implementation:**
*inventory_service.py*:
```python
def apply_inventory_adjustment(current_stock, delta):
    new_stock = current_stock + delta
    if new_stock < 0:
        return False, current_stock
    return True, new_stock
```

---

### Challenge 30: [CODE-M15] A CSV Export Corrupts Embedded Commas and Newlines
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
When user feedback contains commas or line breaks (e.g., `"Great service, fast delivery"`), the exported CSV breaks across lines and shifts columns in Excel.

**Reference Solution Implementation:**
*csv_exporter.py*:
```python
import csv
import io

def export_records_to_csv(records, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for r in records:
        writer.writerow(r)
    return output.getvalue()
```

---

### Challenge 31: [CODE-M16] A Batch Processor Mishandles Partial Failures
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
If recipient #42 has an invalid phone number, the entire batch aborts, and recipients 43-100 never receive their alerts!

**Reference Solution Implementation:**
*batch_processor.py*:
```python
def execute_batch(items, process_fn):
    succeeded = []
    failed = []
    for item in items:
        try:
            res = process_fn(item)
            succeeded.append(res)
        except Exception as e:
            failed.append({"item": item, "error": str(e)})
    return {"succeeded": succeeded, "failed": failed}
```

---

### Challenge 32: [CODE-M17] Incorrect Pagination Cursors Produce Infinite Loops
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
The sync crawler runs for 24 hours in an infinite loop, continuously requesting the same empty page millions of times.

**Reference Solution Implementation:**
*cursor_paginator.py*:
```python
def get_next_cursor(items, last_seen_cursor):
    if not items:
        return None
    next_cursor = items[-1].get("cursor")
    if next_cursor == last_seen_cursor:
        return None
    return next_cursor
```

---

### Challenge 33: [CODE-M18] A Data Transformation Fails for Optional Nested Properties
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
When a user profile has no secondary address (`address["secondary"]` is `None` or omitted), formatting throws `TypeError: 'NoneType' object is not subscriptable`.

**Reference Solution Implementation:**
*transformer.py*:
```python
def format_postal_address(profile):
    addr = profile.get("address") if isinstance(profile, dict) else None
    city = addr.get("city", "Unknown City") if isinstance(addr, dict) else "Unknown City"
    name = profile.get("name", "Unknown") if isinstance(profile, dict) else "Unknown"
    return f"{name}, {city}"
```

---

### Challenge 34: [CODE-M19] A Rate Limiter Resets Counters Incorrectly
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Rate Limiting

**Bug Description & Root Cause:**
A client sends 100 requests at 12:00:59, and another 100 requests at 12:01:01. The server receives 200 requests within a 2-second window without rate limiting!

**Reference Solution Implementation:**
*rate_limiter.py*:
```python
import time

class SlidingWindowRateLimiter:
    def __init__(self, limit=10, window_seconds=60):
        self.limit = limit
        self.window = window_seconds
        self.requests = {}

    def is_allowed(self, client_id):
        now = time.time()
        client_reqs = [t for t in self.requests.get(client_id, []) if now - t < self.window]
        if len(client_reqs) >= self.limit:
            self.requests[client_id] = client_reqs
            return False
        client_reqs.append(now)
        self.requests[client_id] = client_reqs
        return True
```

---

### Challenge 35: [CODE-M20] An Exception Handler Hides a Meaningful Application Failure
- **Difficulty:** Medium (150 pts)
- **Technology:** Python
- **Category:** Error Handling

**Bug Description & Root Cause:**
When LDAP server credentials expire, the service catches `Exception` and returns `{"authenticated": False, "reason": "Bad credentials"}`. Administrators spend days resetting user passwords when LDAP service was actually unreachable.

**Reference Solution Implementation:**
*service_client.py*:
```python
def call_external_service(client, endpoint):
    try:
        return client.request(endpoint)
    except Exception as e:
        import logging
        logging.error(f"Service call failed: {e}", exc_info=True)
        raise
```

---

### Challenge 36: [CODE-H01] Concurrent Payment Requests Cause Duplicate Charges
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
When two requests arrive within 5 milliseconds of each other, both requests pass the `is_order_paid` check before either sets the paid flag, charging the customer's card twice!

**Reference Solution Implementation:**
*payment_gateway.py*:
```python
class ConcurrentPaymentGateway:
    def __init__(self, ledger):
        self.ledger = ledger

    def process_charge(self, account_id, amount, idempotency_key):
        if self.ledger.has_processed(idempotency_key):
            return self.ledger.get_transaction(idempotency_key)
        with self.ledger.lock(account_id):
            if self.ledger.has_processed(idempotency_key):
                return self.ledger.get_transaction(idempotency_key)
            return self.ledger.debit(account_id, amount, idempotency_key=idempotency_key)
```

---

### Challenge 37: [CODE-H02] A Distributed Job Processor Executes Non-Idempotent Jobs Twice
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Backend

**Bug Description & Root Cause:**
When a video takes 45 seconds to transcode, the cluster scheduler assumes worker 1 died, revokes its lease, and assigns the job to worker 2, causing both workers to write conflicting output files!

**Reference Solution Implementation:**
*job_scheduler.py*:
```python
class DistributedJobScheduler:
    def __init__(self, lock_manager):
        self.lock_manager = lock_manager

    def execute_job(self, job_id, job_fn):
        with self.lock_manager.acquire(job_id) as acquired:
            if not acquired:
                return False
            job_fn()
            return True
```

---

### Challenge 38: [CODE-H03] Incorrect Transaction Isolation Causes Inconsistent Inventory
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
Two customers buy the last seat on Flight 302 simultaneously. The system confirms both tickets, leading to passenger boarding denial at the gate!

**Reference Solution Implementation:**
*inventory_allocator.py*:
```python
def allocate_inventory(db_session, item_id, quantity):
    with db_session.begin():
        item = db_session.query_for_update(item_id)
        if item.available_stock < quantity:
            return False
        item.available_stock -= quantity
        db_session.commit()
    return True
```

---

### Challenge 39: [CODE-H04] Cache Invalidation Races with Concurrent Database Updates
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Caching

**Bug Description & Root Cause:**
User updates bio from "Dev" to "Senior Dev". A concurrent read request repopulates the cache with the old value "Dev", where it stays stuck forever!

**Reference Solution Implementation:**
*cache_aside.py*:
```python
def update_user_profile(db, cache, user_id, new_data):
    db.update_user(user_id, new_data)
    cache.delete(f"user:{user_id}")
```

---

### Challenge 40: [CODE-H05] A Distributed Lock is Released by the Wrong Request
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
Request A acquires the lock with TTL=10s. Request A runs slow (12s). The lock expires and Request B acquires it. Request A finally finishes and calls `release_lock`, inadvertently releasing Request B's lock!

**Reference Solution Implementation:**
*distributed_lock.py*:
```python
class DistributedLock:
    def __init__(self, redis_client):
        self.redis = redis_client

    def release_lock(self, lock_key, lock_owner_token):
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return self.redis.eval(script, 1, lock_key, lock_owner_token)
```

---

### Challenge 41: [CODE-H06] A Retry Mechanism Causes a Request Storm During an Outage
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** API & Web

**Bug Description & Root Cause:**
When an upstream server encounters a 1-second lag, 50,000 mobile apps retry on exact synchronized 2-second intervals, creating massive spike waves (thundering herd) that crash the database.

**Reference Solution Implementation:**
*backoff_client.py*:
```python
def calculate_backoff(attempt, base_delay=1, max_delay=32, jitter=0):
    return min(max_delay, base_delay * (2 ** attempt) + jitter)
```

---

### Challenge 42: [CODE-H07] Concurrent File Writes Corrupt Generated Reports
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
When two scheduled reports generate simultaneously, they append lines to the same target file at the same time, producing interleaved, corrupted CSV records.

**Reference Solution Implementation:**
*report_writer.py*:
```python
import os
import tempfile

def write_atomic_report(filepath, content):
    dir_name = os.path.dirname(filepath)
    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False) as tf:
        tf.write(content)
        temp_name = tf.name
    os.replace(temp_name, filepath)
```

---

### Challenge 43: [CODE-H08] An Asynchronous Task Deadlocks Under Concurrent Execution
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
Task 1 acquires GPU, then waits for NVMe. Task 2 acquires NVMe, then waits for GPU. Both tasks hang forever in a circular deadlock!

**Reference Solution Implementation:**
*resource_manager.py*:
```python
import asyncio

class AsyncResourceManager:
    def __init__(self):
        self.lock = asyncio.Lock()

    async def transfer(self, source, target, amount):
        async with self.lock:
            source.balance -= amount
            target.balance += amount
```

---

### Challenge 44: [CODE-H09] A Permission Check Occurs After a Sensitive State Change
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Security

**Bug Description & Root Cause:**
An unprivileged user submits a request to promote themselves to Superuser. The handler grants the role in the database before running the authorization check. If the check throws, the user still remains Superuser!

**Reference Solution Implementation:**
*access_controller.py*:
```python
def execute_privileged_operation(user, resource_id, op_fn):
    if not user.has_permission("MODIFY", resource_id):
        raise PermissionError("Access Denied")
    return op_fn(resource_id)
```

---

### Challenge 45: [CODE-H10] A Batch Migration Loses Records After a Partial Failure
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Data & Processing

**Bug Description & Root Cause:**
At batch 500, a transient network error terminates the migration. When re-run, the script starts over from batch 1 without checkpointing, creating duplicate rows and missing records.

**Reference Solution Implementation:**
*migration_runner.py*:
```python
def run_migration_batch(db, records):
    with db.transaction():
        for r in records:
            db.insert(r)
```

---

### Challenge 46: [CODE-H11] An Event-Processing Pipeline Reorders Dependent Events
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
Because events are assigned to random thread pool workers, `ORDER_CANCELLED` executes before `ORDER_CREATED`, failing with "Order not found", and the order is created afterward and remains active!

**Reference Solution Implementation:**
*event_stream.py*:
```python
class EventStreamProcessor:
    def __init__(self):
        self.expected_seq = 1
        self.buffer = {}

    def process_event(self, event, apply_fn):
        seq = event.get("seq")
        self.buffer[seq] = event
        while self.expected_seq in self.buffer:
            ev = self.buffer.pop(self.expected_seq)
            apply_fn(ev)
            self.expected_seq += 1
```

---

### Challenge 47: [CODE-H12] Incorrect Rollback Logic Leaves Related Resources Inconsistent
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Transactions

**Bug Description & Root Cause:**
Flight succeeds, Hotel succeeds, but Car Rental fails. The rollback coordinator cancels the Hotel but forgets to cancel the Flight!

**Reference Solution Implementation:**
*saga_coordinator.py*:
```python
class SagaCoordinator:
    def execute_saga(self, steps):
        executed = []
        try:
            for forward_fn, compensate_fn in steps:
                forward_fn()
                executed.append(compensate_fn)
        except Exception:
            for comp_fn in reversed(executed):
                try:
                    comp_fn()
                except Exception:
                    pass
            raise
```

---

### Challenge 48: [CODE-H13] A Streaming Parser Leaks Memory for Large Inputs
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Performance

**Bug Description & Root Cause:**
The parser process runs out of memory (`OOMKilled`) when parsing a 2GB file, despite being intended as a streaming generator.

**Reference Solution Implementation:**
*stream_parser.py*:
```python
def parse_chunked_stream(stream):
    for chunk in stream:
        yield chunk.strip()
```

---

### Challenge 49: [CODE-H14] A Multi-Step Account Update Leaves Partially Modified State
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Transactions

**Bug Description & Root Cause:**
Email updates successfully, but phone number fails regex validation. The user profile is left with updated email but unchanged phone, creating inconsistent state.

**Reference Solution Implementation:**
*account_service.py*:
```python
def update_account_status(db, account_id, new_status):
    with db.transaction():
        db.update_status(account_id, new_status)
        db.log_audit(account_id, f"Status updated to {new_status}")
```

---

### Challenge 50: [CODE-H15] A Concurrent Reservation System Oversells Limited Inventory
- **Difficulty:** Hard (250 pts)
- **Technology:** Python
- **Category:** Concurrency

**Bug Description & Root Cause:**
Seat A1 is reserved by User 1 at 12:00:00. At 12:00:01, User 2 submits a reservation for Seat A1 and succeeds, displacing User 1!

**Reference Solution Implementation:**
*seat_reservation.py*:
```python
class SeatReservationSystem:
    def __init__(self, total_seats):
        self.available_seats = total_seats
        self.reserved_seats = set()

    def reserve(self, seat_number, user_id):
        if seat_number in self.reserved_seats or self.available_seats <= 0:
            return False
        self.reserved_seats.add(seat_number)
        self.available_seats -= 1
        return True
```

---

### Challenge 51: [SQL-E01] Customer Report Excludes Records Containing NULL Values
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Filtering

**Bug Description & Root Cause:**
Customers whose opt-out preference is unset (stored as `NULL` in the database) are completely missing from the campaign export.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, email FROM customers WHERE opt_out = 0 OR opt_out IS NULL ORDER BY id;
```

---

### Challenge 52: [SQL-E02] Monthly Revenue Report Uses the Wrong Date Boundary
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Filtering

**Bug Description & Root Cause:**
Transactions processed on October 31st at 18:30 are missing from the report, under-reporting monthly revenue by $15,000!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date >= '2026-10-01' AND order_date < '2026-11-01';
```

---

### Challenge 53: [SQL-E03] Product Search Filters the Wrong Status
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Filtering

**Bug Description & Root Cause:**
Items that are archived or pending approval appear in customer search, while in-stock active items are hidden.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, price FROM products WHERE status = 'active' ORDER BY name ASC;
```

---

### Challenge 54: [SQL-E04] An INNER JOIN Removes Customers Without Orders
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Joins

**Bug Description & Root Cause:**
New users (0 orders) are completely omitted from the user roster!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT c.id, c.name, o.id AS order_id FROM customers c LEFT JOIN orders o ON c.id = o.customer_id ORDER BY c.id;
```

---

### Challenge 55: [SQL-E05] A GROUP BY Query Calculates the Wrong Average
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
Employees who received $0 bonus are omitted from the average, artificially inflating the department's bonus metric.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT department, AVG(bonus) AS avg_bonus FROM employees GROUP BY department ORDER BY department;
```

---

### Challenge 56: [SQL-E06] Duplicate Email Records Are Not Detected Correctly
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
The duplicate detection script returns every single email address in the database, including unique ones!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT email, COUNT(*) AS count FROM users GROUP BY email HAVING COUNT(*) > 1 ORDER BY email;
```

---

### Challenge 57: [SQL-E07] An Invoice Query Incorrectly Rounds Monetary Totals
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
Invoices report fractional penny differences from bank statements because line items are rounded to integer dollars rather than 2 decimal places.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT ROUND(SUM(subtotal * tax_rate), 2) AS total_tax FROM invoice_items;
```

---

### Challenge 58: [SQL-E08] A Report Includes Cancelled Orders
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Filtering

**Bug Description & Root Cause:**
Cancelled and refunded orders are included in the sales GMV calculation, inflating daily performance numbers.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT SUM(amount) AS completed_gmv FROM orders WHERE status = 'completed';
```

---

### Challenge 59: [SQL-E09] A Query Orders Numeric Values Stored as Text Incorrectly
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Sorting

**Bug Description & Root Cause:**
Tasks order as `'10', '100', '2', '20'` instead of `'2', '10', '20', '100'`!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, priority_level FROM tasks ORDER BY CAST(priority_level AS INTEGER) ASC;
```

---

### Challenge 60: [SQL-E10] A Query Returns the Wrong Top-Selling Product Because of Incorrect Sorting
- **Difficulty:** Easy (100 pts)
- **Technology:** SQL
- **Category:** Sorting

**Bug Description & Root Cause:**
The dashboard displays the least-sold item (1 unit sold) as the "Top Seller" instead of the actual best-selling item (500 units sold)!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, total_sold FROM product_sales ORDER BY total_sold DESC LIMIT 1;
```

---

### Challenge 61: [SQL-M01] A JOIN Duplicates Revenue Because of Multiple Order Items
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Joins

**Bug Description & Root Cause:**
An order of $100 containing 3 line items counts as $300 revenue, tripling customer spending metrics!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT customer_id, SUM(total_amount) AS revenue FROM orders GROUP BY customer_id ORDER BY customer_id;
```

---

### Challenge 62: [SQL-M02] Customer Lifetime Value is Inflated by an Incorrect Aggregation
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
Customer average order value calculation averages the daily averages, which skews metrics toward low-volume days.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT customer_id, ROUND(AVG(amount), 2) AS aov FROM orders GROUP BY customer_id ORDER BY customer_id;
```

---

### Challenge 63: [SQL-M03] Pagination Skips or Duplicates Rows When Ordering is Not Deterministic
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Sorting

**Bug Description & Root Cause:**
Events with identical timestamps randomly shift positions between queries, so Page 1 and Page 2 display duplicate rows.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, event, created_at FROM audit_logs ORDER BY created_at DESC, id ASC LIMIT 2 OFFSET 0;
```

---

### Challenge 64: [SQL-M04] A Window Function Uses the Wrong Partition
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Window Functions

**Bug Description & Root Cause:**
Sales reps in the EMEA region are ranked against reps in APAC and Americas, rather than competing solely within their regional teams.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, region, revenue, RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS regional_rank FROM sales_reps ORDER BY region, regional_rank;
```

---

### Challenge 65: [SQL-M05] A Monthly Report Mishandles Timezone Boundaries
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
Subscriptions renewed on September 1st at 00:30 UTC are placed into August because query attempts manual offset subtraction without boundary validation.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT strftime('%Y-%m', payment_date) AS month, SUM(amount) AS total FROM payments GROUP BY month ORDER BY month;
```

---

### Challenge 66: [SQL-M06] A LEFT JOIN Becomes an Accidental INNER JOIN
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Joins

**Bug Description & Root Cause:**
Users with no subscription are excluded from the directory despite using a `LEFT JOIN`!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT u.id, u.name, s.plan_name FROM users u LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active' ORDER BY u.id;
```

---

### Challenge 67: [SQL-M07] An Inventory Report Calculates Incorrect Available Stock
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
Items with zero pending reservations (`reserved_stock = NULL`) show `available_stock = NULL` instead of their physical stock!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, (physical_stock - COALESCE(reserved_stock, 0)) AS available_stock FROM inventory ORDER BY id;
```

---

### Challenge 68: [SQL-M08] A Query Incorrectly Handles NULL Values in Conditional Aggregation
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
The delivered orders column count is inaccurate because `COUNT(CASE WHEN status = 'delivered' THEN 0 ELSE NULL END)` evaluates `0` as non-null!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_count FROM shipments;
```

---

### Challenge 69: [SQL-M09] A CTE Filters Records Before Aggregation When Filtering Should Occur Afterward
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** CTE

**Bug Description & Root Cause:**
The report filters out individual purchases under $500 in the CTE before summing, omitting loyal customers who made ten $60 purchases!

**Reference Solution Implementation:**
*query.sql*:
```sql
WITH customer_totals AS (
    SELECT customer_id, SUM(amount) AS total_spent FROM orders GROUP BY customer_id
)
SELECT customer_id, total_spent FROM customer_totals WHERE total_spent >= 500 ORDER BY customer_id;
```

---

### Challenge 70: [SQL-M10] A Duplicate-Detection Query Flags Valid Records
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
Over 15,000 legitimate users who have empty or unset phone numbers (`phone IS NULL`) are all grouped together and flagged as a fraudulent syndicate!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT phone, COUNT(*) AS count FROM users WHERE phone IS NOT NULL AND phone != '' GROUP BY phone HAVING COUNT(*) > 1 ORDER BY phone;
```

---

### Challenge 71: [SQL-M11] A Ranking Query Assigns Incorrect Positions to Tied Values
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Window Functions

**Bug Description & Root Cause:**
Two competitors tied for 1st place with 95 points. The next participant with 90 points is displayed as 2nd place instead of 3rd place!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, score, RANK() OVER (ORDER BY score DESC) AS rank FROM scores ORDER BY rank, id;
```

---

### Challenge 72: [SQL-M12] A Subquery Returns Multiple Rows Unexpectedly
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Subqueries

**Bug Description & Root Cause:**
The product API crashes with `OperationalError: subquery returns more than 1 row` whenever a category has multiple active discount coupons.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, name, discount_id FROM products WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech') ORDER BY id;
```

---

### Challenge 73: [SQL-M13] A Report Combines Historical and Current Prices Incorrectly
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Joins

**Bug Description & Root Cause:**
A customer bought an item in 2025 for $50. In 2026, the price was raised to $80. The 2025 sales report recalculates the past order at $80, distorting historical revenue!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT product_id, SUM(quantity * price_at_purchase) AS total_revenue FROM order_items GROUP BY product_id;
```

---

### Challenge 74: [SQL-M14] A Query Counts Orders Instead of Distinct Customers
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** Aggregation

**Bug Description & Root Cause:**
If 1 customer places 10 orders in a day, the dashboard reports 10 active customers instead of 1!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT COUNT(DISTINCT customer_id) AS unique_customers FROM orders;
```

---

### Challenge 75: [SQL-M15] A Recursive Query Omits Part of an Organizational Hierarchy
- **Difficulty:** Medium (150 pts)
- **Technology:** SQL
- **Category:** CTE

**Bug Description & Root Cause:**
Only direct reports to the CEO appear; second-level managers and individual contributors are omitted!

**Reference Solution Implementation:**
*query.sql*:
```sql
WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 1 AS level FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, org.level + 1
    FROM employees e JOIN org_tree org ON e.manager_id = org.id
)
SELECT id, name, level FROM org_tree ORDER BY level, id;
```

---

### Challenge 76: [SQL-H01] Concurrent Inventory Reservations Oversell Stock
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Concurrency

**Bug Description & Root Cause:**
When stock is 1, two concurrent buyers both execute `UPDATE inventory SET stock = stock - 1 WHERE id = 10`, setting stock to -1 and overselling the item.

**Reference Solution Implementation:**
*query.sql*:
```sql
UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1;
SELECT id, name, stock FROM inventory WHERE id = 10;
```

---

### Challenge 77: [SQL-H02] A Payment Transaction Updates Balances Without Maintaining Consistency
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Transactions

**Bug Description & Root Cause:**
Debit executes, but credit fails due to an invalid account ID. Because the statements are not wrapped in a transaction, Account 1 loses $50 permanently while Account 2 receives nothing!

**Reference Solution Implementation:**
*query.sql*:
```sql
UPDATE accounts SET balance = balance - 50 WHERE id = 1 AND balance >= 50;
UPDATE accounts SET balance = balance + 50 WHERE id = 2;
SELECT id, owner, balance FROM accounts ORDER BY id;
```

---

### Challenge 78: [SQL-H03] A Multi-Table JOIN Multiplies Aggregates Across Independent Relationships
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Joins

**Bug Description & Root Cause:**
Customer with 2 orders and 3 support tickets produces 2 x 3 = 6 joined rows. Order total is multiplied by 3, and support tickets count is multiplied by 2!

**Reference Solution Implementation:**
*query.sql*:
```sql
WITH o_summary AS (
    SELECT customer_id, SUM(amount) AS total_spent FROM orders GROUP BY customer_id
),
t_summary AS (
    SELECT customer_id, COUNT(*) AS total_tickets FROM tickets GROUP BY customer_id
)
SELECT c.id, c.name, COALESCE(o.total_spent, 0) AS total_spent, COALESCE(t.total_tickets, 0) AS total_tickets
FROM customers c
LEFT JOIN o_summary o ON c.id = o.customer_id
LEFT JOIN t_summary t ON c.id = t.customer_id;
```

---

### Challenge 79: [SQL-H04] A Transaction Failure Leaves Related Financial Records Inconsistent
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Transactions

**Bug Description & Root Cause:**
An invoice is marked paid, but the corresponding audit journal row was missing, failing SOX compliance audits.

**Reference Solution Implementation:**
*query.sql*:
```sql
UPDATE invoices SET status = 'paid' WHERE id = 1;
INSERT INTO audit_journal VALUES (1, 1, 'INVOICE_PAID');
SELECT i.status, COUNT(a.id) AS journal_count FROM invoices i LEFT JOIN audit_journal a ON i.id = a.invoice_id WHERE i.id = 1 GROUP BY i.status;
```

---

### Challenge 80: [SQL-H05] A Database Migration Incorrectly Handles Existing NULL and Duplicate Values
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Schema

**Bug Description & Root Cause:**
Running `ALTER TABLE` crashes or produces corrupted profiles because existing rows contain `NULL` values!

**Reference Solution Implementation:**
*query.sql*:
```sql
UPDATE user_settings SET notification_email = 'no-reply@domain.com' WHERE notification_email IS NULL;
SELECT id, user_id, notification_email FROM user_settings ORDER BY id;
```

---

### Challenge 81: [SQL-H06] A Running-Total Query Produces Incorrect Results for Tied Timestamps
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Window Functions

**Bug Description & Root Cause:**
When two transactions occur at the identical second (`2026-10-19 12:00:00`), the running total jumps ahead and shows the cumulative sum of BOTH transactions on the first row!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, amount, trans_time, SUM(amount) OVER (ORDER BY trans_time, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_balance FROM ledger ORDER BY id;
```

---

### Challenge 82: [SQL-H07] A Reporting Query Uses Incorrect Isolation Assumptions During Concurrent Updates
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Transactions

**Bug Description & Root Cause:**
The report includes half-completed cart checkout drafts that are in status `'draft'`, skewing daily performance metrics.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT SUM(amount) AS total_sales FROM orders WHERE status = 'confirmed';
```

---

### Challenge 83: [SQL-H08] A Soft-Delete Implementation Leaks Logically Deleted Records
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Filtering

**Bug Description & Root Cause:**
Soft-deleted documents continue to appear in search queries and public document listings!

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT id, title FROM documents WHERE deleted_at IS NULL ORDER BY id;
```

---

### Challenge 84: [SQL-H09] A Recursive Hierarchy Query Mishandles Cycles
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** CTE

**Bug Description & Root Cause:**
An invalid database relationship created a circular reference (Category A is parent of Category B, which is parent of Category A). The query runs infinitely until the database crashes with `RecursionError`!

**Reference Solution Implementation:**
*query.sql*:
```sql
WITH RECURSIVE cat_tree AS (
    SELECT id, name, parent_id, 1 AS depth FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id
    WHERE ct.depth < 5
)
SELECT id, name, depth FROM cat_tree ORDER BY depth, id;
```

---

### Challenge 85: [SQL-H10] An Analytics Query Becomes Extremely Slow Because of Incorrect Query Structure and Indexing Assumptions
- **Difficulty:** Hard (250 pts)
- **Technology:** SQL
- **Category:** Performance

**Bug Description & Root Cause:**
The query uses `IN (SELECT customer_id FROM orders)` on millions of rows, causing a full table scan and locking the database.

**Reference Solution Implementation:**
*query.sql*:
```sql
SELECT c.id, c.name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY c.id;
```

---

### Challenge 86: [FE-E01] A Form Submits Even When Required Fields Are Empty
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** Forms

**Bug Description & Root Cause:**
When a user clicks "Submit" without filling in their name, the form dispatches an API request with an empty payload, causing backend 400 Bad Request errors.

**Reference Solution Implementation:**
*RegistrationForm.jsx*:
```javascript
import React, { useState } from 'react';

export default function RegistrationForm({ onSubmit }) {
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name is required');
      return;
    }
    onSubmit({ name });
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-3">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter your name"
        className="border p-2 rounded"
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
        Register
      </button>
    </form>
  );
}
```

---

### Challenge 87: [FE-E02] A React Component Displays Stale or Incorrect Conditional Content
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** Conditional Rendering

**Bug Description & Root Cause:**
When `item.stock` is `0`, the component displays `"0"` on screen instead of the `"Sold Out"` badge because of how JavaScript evaluates `0 && <Component />`!

**Reference Solution Implementation:**
*Banner.jsx*:
```javascript
import React from 'react';

export default function StockBanner({ stock }) {
  return (
    <div className="stock-container">
      {stock > 0 ? (
        <span className="in-stock">In Stock ({stock})</span>
      ) : (
        <span className="sold-out">Sold Out</span>
      )}
    </div>
  );
}
```

---

### Challenge 88: [FE-E03] A Product Card Shows the Wrong Price After a State Update
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** React State

**Bug Description & Root Cause:**
User clicks `+` to increase quantity from 1 to 2. The total price continues to display the price for 1 item!

**Reference Solution Implementation:**
*ProductCard.jsx*:
```javascript
import React, { useState } from 'react';

export default function ProductCard({ price }) {
  const [quantity, setQuantity] = useState(1);

  const handleQuantityChange = (newQty) => {
    setQuantity(newQty);
  };

  const totalPrice = price * quantity;

  return (
    <div className="p-4 border rounded">
      <p>Unit Price: ${price}</p>
      <input
        type="number"
        value={quantity}
        onChange={(e) => handleQuantityChange(parseInt(e.target.value) || 1)}
        className="border p-1 w-16"
      />
      <p className="font-bold">Total: ${totalPrice}</p>
    </div>
  );
}
```

---

### Challenge 89: [FE-E04] A Button Fires the Wrong Event Handler
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** DOM & Events

**Bug Description & Root Cause:**
When a user clicks "Save Draft", the task is permanently deleted!

**Reference Solution Implementation:**
*ActionButton.jsx*:
```javascript
import React from 'react';

export default function ActionButton({ onSave, onDelete }) {
  return (
    <div className="flex gap-2">
      <button onClick={onSave} className="bg-green-600 text-white px-3 py-1 rounded">
        Save Changes
      </button>
      <button onClick={onDelete} className="bg-red-600 text-white px-3 py-1 rounded">
        Delete Record
      </button>
    </div>
  );
}
```

---

### Challenge 90: [FE-E05] A Search Field Ignores Uppercase/Lowercase Normalization
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** Validation

**Bug Description & Root Cause:**
Typing `"ALICE"` or `"alice"` fails to match employee `"Alice Smith"` due to strict case-sensitive matching.

**Reference Solution Implementation:**
*SearchBar.jsx*:
```javascript
import React, { useState } from 'react';

export default function SearchBar({ items = [] }) {
  const [query, setQuery] = useState('');

  const filtered = items.filter(item =>
    item.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search items..."
        className="border p-2 rounded w-full"
      />
      <ul className="mt-2">
        {filtered.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

### Challenge 91: [FE-E06] A Loading Indicator Never Disappears After an API Error
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** React State

**Bug Description & Root Cause:**
When the server returns an HTTP 500 error, the spinner keeps spinning endlessly and the error message never displays.

**Reference Solution Implementation:**
*DataViewer.jsx*:
```javascript
import React, { useState, useEffect } from 'react';

export default function DataViewer({ fetchData }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchData()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [fetchData]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div>Data: {JSON.stringify(data)}</div>;
}
```

---

### Challenge 92: [FE-E07] A Responsive Layout Overflows on Mobile
- **Difficulty:** Easy (100 pts)
- **Technology:** CSS
- **Category:** CSS & Styling

**Bug Description & Root Cause:**
On mobile devices (screen width 375px), the card overflows horizontally, causing horizontal scrollbars and breaking page layout.

**Reference Solution Implementation:**
*ResponsiveCard.css*:
```css
.card {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  box-sizing: border-box;
}
```

---

### Challenge 93: [FE-E08] A Form Displays an Incorrect Validation Message
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** Validation

**Bug Description & Root Cause:**
When user enters an invalid email missing `@`, the error displays `"Password must be at least 8 characters"`!

**Reference Solution Implementation:**
*EmailInput.jsx*:
```javascript
import React, { useState } from 'react';

export default function EmailInput() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const validateEmail = (val) => {
    setEmail(val);
    if (!val.includes('@') || !val.includes('.')) {
      setError('Please enter a valid email address.');
    } else {
      setError('');
    }
  };

  return (
    <div>
      <input
        type="email"
        value={email}
        onChange={(e) => validateEmail(e.target.value)}
        placeholder="Enter email"
        className="border p-2"
      />
      {error && <span className="text-red-500">{error}</span>}
    </div>
  );
}
```

---

### Challenge 94: [FE-E09] A Modal Cannot Be Closed Using the Escape Key
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** Accessibility

**Bug Description & Root Cause:**
Keyboard users and screen readers cannot close the modal by pressing the Escape key, violating WCAG accessibility guidelines.

**Reference Solution Implementation:**
*Modal.jsx*:
```javascript
import React, { useEffect } from 'react';

export default function Modal({ isOpen, onClose, children }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white p-6 rounded shadow-lg">
        {children}
        <button onClick={onClose} className="mt-4 px-3 py-1 bg-gray-200 rounded">
          Close
        </button>
      </div>
    </div>
  );
}
```

---

### Challenge 95: [FE-E10] A List Uses an Unstable or Incorrect React Key, Causing UI Inconsistencies
- **Difficulty:** Easy (100 pts)
- **Technology:** React
- **Category:** DOM & Events

**Bug Description & Root Cause:**
When an admin deletes the first user in the list, input values and checkbox states from the deleted row jump onto the next row!

**Reference Solution Implementation:**
*UserList.jsx*:
```javascript
import React from 'react';

export default function UserList({ users = [], onDelete }) {
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id} className="flex justify-between p-2">
          <span>{user.name}</span>
          <button onClick={() => onDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

---

### Challenge 96: [FE-M01] Rapid Search Requests Overwrite Newer Results
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Asynchronous UI

**Bug Description & Root Cause:**
When typing quickly (e.g. searching for "users" by typing "u", "us", "use", "user", "users"), the query for "us" took 350ms while "users" took 80ms. The earlier slow response arrived last and overwrote the results, leaving stale results for "us" visible on the screen even though the input displays "users".

**Reference Solution Implementation:**
*LiveSearch.jsx*:
```javascript
import React, { useState, useEffect } from 'react';

export default function LiveSearch({ fetchResults }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    let active = true;
    if (!query) {
      setResults([]);
      return;
    }

    fetchResults(query).then(data => {
      if (active) {
        setResults(data);
      }
    });

    return () => {
      active = false;
    };
  }, [query, fetchResults]);

  return (
    <div className="search-container p-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documentation..."
        className="border p-2 rounded w-full"
      />
      <ul className="mt-2 divide-y">
        {results.map((item, idx) => (
          <li key={idx} className="p-2">{item.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

### Challenge 97: [FE-M02] React State Updates Lose Changes During Batched Operations
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** State Management

**Bug Description & Root Cause:**
Clicking "+3" only increments the box count by 1 instead of 3.

**Reference Solution Implementation:**
*CounterBatch.jsx*:
```javascript
import React, { useState } from 'react';

export default function CounterBatch() {
  const [count, setCount] = useState(0);

  const incrementByThree = () => {
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
  };

  return (
    <div className="p-4">
      <p className="text-lg font-bold">Boxes: {count}</p>
      <button
        onClick={incrementByThree}
        className="bg-emerald-600 text-white px-3 py-1 rounded mt-2"
      >
        +3 Quick Add
      </button>
    </div>
  );
}
```

---

### Challenge 98: [FE-M03] useEffect Dependency Causes Stale Values or Missing Updates
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** React Hooks

**Bug Description & Root Cause:**
When an agent clicks between User A and User B, the drawer continues to show User A's details because the effect dependency array is empty `[]`.

**Reference Solution Implementation:**
*UserProfileLoader.jsx*:
```javascript
import React, { useState, useEffect } from 'react';

export default function UserProfileLoader({ userId, fetchUser }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    fetchUser(userId).then(data => {
      if (isMounted) {
        setProfile(data);
        setLoading(false);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [userId, fetchUser]);

  if (loading) return <p>Loading profile...</p>;
  return (
    <div className="profile-card p-4">
      <h2 className="text-xl font-bold">{profile?.name}</h2>
      <p>{profile?.email}</p>
    </div>
  );
}
```

---

### Challenge 99: [FE-M04] Shopping Cart Calculates Totals Incorrectly After Mutation
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** State Immutability

**Bug Description & Root Cause:**
Modifying item quantity directly mutates the state array object `items[index].qty = newQty`. React fails to trigger re-renders reliably because the array reference remains identical, and cart total calculation falls out of sync.

**Reference Solution Implementation:**
*ShoppingCart.jsx*:
```javascript
import React, { useState } from 'react';

export default function ShoppingCart({ initialItems = [] }) {
  const [items, setItems] = useState(initialItems);

  const updateQuantity = (id, newQty) => {
    setItems(items.map(item => item.id === id ? { ...item, qty: newQty } : item));
  };

  const total = items.reduce((sum, item) => sum + item.price * (item.qty || 1), 0);

  return (
    <div className="cart p-4">
      {items.map(item => (
        <div key={item.id} className="flex justify-between py-2 border-b">
          <span>{item.name} (${item.price})</span>
          <input
            type="number"
            value={item.qty}
            onChange={(e) => updateQuantity(item.id, parseInt(e.target.value) || 0)}
            className="w-16 border rounded p-1"
          />
        </div>
      ))}
      <div className="font-bold mt-4">Total: ${total.toFixed(2)}</div>
    </div>
  );
}
```

---

### Challenge 100: [FE-M05] Paginated List Does Not Reset Page When Filter Changes
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Pagination

**Bug Description & Root Cause:**
An admin navigates to Page 6 of "All Products". They then filter by "Furniture", which only has 2 pages of results. The view displays "No products found" because the table stayed on `page = 6`, which is out of range for the filtered results!

**Reference Solution Implementation:**
*FilterPagination.jsx*:
```javascript
import React, { useState } from 'react';

export default function FilterPagination({ products = [] }) {
  const [category, setCategory] = useState('All');
  const [page, setPage] = useState(1);
  const pageSize = 5;

  const handleFilterChange = (newCategory) => {
    setCategory(newCategory);
    setPage(1);
  };

  const filtered = category === 'All' 
    ? products 
    : products.filter(p => p.category === category);

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const paginated = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="catalog p-4">
      <select 
        value={category} 
        onChange={(e) => handleFilterChange(e.target.value)}
        className="border p-2 rounded mb-4"
      >
        <option value="All">All Categories</option>
        <option value="Electronics">Electronics</option>
        <option value="Furniture">Furniture</option>
      </select>

      {paginated.length === 0 ? (
        <p>No products found</p>
      ) : (
        <ul>
          {paginated.map(p => <li key={p.id}>{p.name}</li>)}
        </ul>
      )}

      <div className="flex gap-2 mt-4">
        <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
        <span>Page {page} of {totalPages}</span>
        <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
}
```

---

### Challenge 101: [FE-M06] Event Listener Registered Repeatedly Without Cleanup
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Memory Leaks

**Bug Description & Root Cause:**
Every time the user navigates between dashboard tabs, browser memory consumption increases steadily. Profiling reveals that thousands of `resize` listeners remain attached to `window`, leading to sluggish responsiveness.

**Reference Solution Implementation:**
*ResizeListener.jsx*:
```javascript
import React, { useState, useEffect } from 'react';

export default function ResizeListener() {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="p-4">
      <p className="font-semibold">Current width: {windowWidth}px</p>
    </div>
  );
}
```

---

### Challenge 102: [FE-M07] Authentication Refresh Request Creates Redirect Loops
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Authentication

**Bug Description & Root Cause:**
When an authenticated user refreshes `/settings`, the page flickers and immediately redirects to `/login`. Upon arriving at `/login`, the auth provider finishes hydrating and redirects them back to `/settings`, causing an infinite redirect loop.

**Reference Solution Implementation:**
*ProtectedRoute.jsx*:
```javascript
import React from 'react';

function LoadingSpinner() {
  return <div className="spinner p-4">Loading session...</div>;
}

function Navigate({ to }) {
  return <div>Redirecting to {to}...</div>;
}

export default function ProtectedRoute({ user, isLoading, children }) {
  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
}
```

---

### Challenge 103: [FE-M08] File-Upload Component Mishandles Progress and Failed Requests
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Error Handling

**Bug Description & Root Cause:**
If an upload fails (e.g. 500 server error or dropped connection), the UI remains stuck showing "Uploading 65%..." and the upload button stays disabled forever. The user is unable to retry without refreshing the entire page.

**Reference Solution Implementation:**
*FileUploader.jsx*:
```javascript
import React, { useState } from 'react';

export default function FileUploader({ uploadApi }) {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    setProgress(20);

    try {
      await uploadApi(file, (p) => setProgress(p));
      setIsUploading(false);
      setProgress(100);
    } catch (err) {
      setIsUploading(false);
      setError(err.message || 'Upload failed');
    }
  };

  return (
    <div className="uploader p-4 border rounded">
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {isUploading ? (
        <p>Uploading... {progress}%</p>
      ) : (
        <button 
          onClick={() => handleUpload({ name: 'receipt.pdf' })}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Upload Document
        </button>
      )}
    </div>
  );
}
```

---

### Challenge 104: [FE-M09] Multi-Step Form Loses User Values When Navigating Backward
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Form Architecture

**Bug Description & Root Cause:**
A user fills out Step 1, proceeds to Step 2, and then clicks "Back" to fix a typo in their name. When Step 1 re-mounts, all previously entered fields are blank!

**Reference Solution Implementation:**
*WizardForm.jsx*:
```javascript
import React, { useState } from 'react';

export function Step1({ formData = {}, onChange }) {
  const [name, setName] = useState(formData.name || '');

  return (
    <div>
      <input
        type="text"
        value={name}
        onChange={(e) => {
          setName(e.target.value);
          onChange({ name: e.target.value });
        }}
        placeholder="Full Name"
        className="border p-2"
      />
    </div>
  );
}

export default function WizardForm() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ name: '' });

  return (
    <div className="p-4">
      {step === 1 && (
        <Step1 formData={formData} onChange={(d) => setFormData(prev => ({ ...prev, ...d }))} />
      )}
      {step === 2 && (
        <div>Step 2: Confirmation for {formData.name}</div>
      )}
      <div className="mt-4 flex gap-2">
        <button onClick={() => setStep(s => Math.max(1, s - 1))}>Back</button>
        <button onClick={() => setStep(s => s + 1)}>Next</button>
      </div>
    </div>
  );
}
```

---

### Challenge 105: [FE-M10] Dashboard Renders Inconsistent Data After Parallel API Calls
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Asynchronous Data

**Bug Description & Root Cause:**
If the Server Health endpoint encounters a minor 503 outage, `Promise.all` fails immediately, causing the entire dashboard to crash and display an error screen—even though the critical Revenue Metrics were returned successfully!

**Reference Solution Implementation:**
*MetricsDashboard.jsx*:
```javascript
import React, { useState, useEffect } from 'react';

export default function MetricsDashboard({ fetchRevenue, fetchHealth }) {
  const [revenue, setRevenue] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.allSettled([fetchRevenue(), fetchHealth()])
      .then(([revRes, healthRes]) => {
        if (revRes.status === 'fulfilled') setRevenue(revRes.value);
        if (healthRes.status === 'fulfilled') setHealth(healthRes.value);
      })
      .catch((err) => {
        setError('Failed to load dashboard metrics');
      });
  }, [fetchRevenue, fetchHealth]);

  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="p-4 grid grid-cols-2 gap-4">
      <div className="card border p-4">
        <h3>Revenue: {revenue ? `$${revenue.total}` : 'Loading...'}</h3>
      </div>
      <div className="card border p-4">
        <h3>System Health: {health ? health.status : 'Unavailable'}</h3>
      </div>
    </div>
  );
}
```

---

### Challenge 106: [FE-M11] Frontend Cache Displays Outdated Profile Information
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Caching

**Bug Description & Root Cause:**
When a user updates their profile name and clicks "Save", the update API returns 200 OK. However, navigating back to their profile view still displays their old name until the page is hard refreshed.

**Reference Solution Implementation:**
*ProfileCache.jsx*:
```javascript
import React, { useState } from 'react';

export default function ProfileCache({ userId, api, cache }) {
  const [profile, setProfile] = useState(() => cache.get(userId) || { name: 'Anonymous' });
  const [nameInput, setNameInput] = useState('');

  const handleUpdateName = async () => {
    const updated = await api.updateName(userId, nameInput);
    setProfile(updated);
    cache.set(userId, updated);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl">User: {profile.name}</h2>
      <input
        type="text"
        value={nameInput}
        onChange={(e) => setNameInput(e.target.value)}
        placeholder="New name"
        className="border p-1 mr-2"
      />
      <button onClick={handleUpdateName} className="bg-blue-500 text-white px-3 py-1 rounded">
        Save
      </button>
    </div>
  );
}
```

---

### Challenge 107: [FE-M12] Component Submits Duplicate Requests After Repeated Clicks
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Form Submission

**Bug Description & Root Cause:**
Impatient users double-click the "Place Order" button. The server receives two parallel order requests and charges the customer twice for the same meal!

**Reference Solution Implementation:**
*SubmitButton.jsx*:
```javascript
import React, { useState } from 'react';

export default function SubmitButton({ onOrder }) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onOrder();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <button 
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="bg-green-600 text-white px-4 py-2 rounded"
      >
        {isSubmitting ? 'Processing...' : 'Place Order'}
      </button>
    </div>
  );
}
```

---

### Challenge 108: [FE-M13] Date Picker Displays Incorrect Date Due to Timezone Offset
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Date & Time

**Bug Description & Root Cause:**
Users in the Americas (e.g. UTC-5, UTC-8) select "October 15, 2026" on the calendar. After selecting, the confirmation text shows "October 14, 2026"—one day behind!

**Reference Solution Implementation:**
*DatePicker.jsx*:
```javascript
import React, { useState } from 'react';

export default function DatePicker({ onSelect }) {
  const [selectedDate, setSelectedDate] = useState('');

  const handleDateChange = (dateString) => {
    setSelectedDate(dateString);
    onSelect(dateString);
  };

  return (
    <div className="p-4">
      <input
        type="date"
        onChange={(e) => handleDateChange(e.target.value)}
        className="border p-2 rounded"
      />
      {selectedDate && <p className="mt-2">Selected: {selectedDate}</p>}
    </div>
  );
}
```

---

### Challenge 109: [FE-M14] Form Does Not Preserve Field-Level Server Validation Errors
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Form Validation

**Bug Description & Root Cause:**
When submitting with a taken subdomain, the backend returns HTTP 422: `{ errors: { subdomain: "Subdomain already in use" } }`. The frontend replaces the entire form with a generic message `"An error occurred"` rather than highlighting the `subdomain` field with its specific server error message.

**Reference Solution Implementation:**
*ServerErrorForm.jsx*:
```javascript
import React, { useState } from 'react';

export default function ServerErrorForm({ onSubmit }) {
  const [subdomain, setSubdomain] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError('');
    setFieldErrors({});

    try {
      await onSubmit({ subdomain });
    } catch (err) {
      if (err.response?.data?.errors) {
        setFieldErrors(err.response.data.errors);
      } else {
        setGeneralError('Submission failed');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-2">
      {generalError && <p className="text-red-600">{generalError}</p>}
      <div>
        <label>Subdomain:</label>
        <input
          type="text"
          value={subdomain}
          onChange={(e) => setSubdomain(e.target.value)}
          className="border p-1 block w-full"
        />
        {fieldErrors.subdomain && (
          <span className="text-red-500 text-sm">{fieldErrors.subdomain}</span>
        )}
      </div>
      <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
        Submit
      </button>
    </form>
  );
}
```

---

### Challenge 110: [FE-M15] Accessible Dropdown Fails to Close on Escape Key
- **Difficulty:** Medium (200 pts)
- **Technology:** React
- **Category:** Accessibility

**Bug Description & Root Cause:**
When a blind or motor-impaired user opens a custom dropdown menu using keyboard navigation, pressing the "Escape" key does not close the dropdown menu, trapping focus and violating accessibility standards.

**Reference Solution Implementation:**
*AccessibleDropdown.jsx*:
```javascript
import React, { useState } from 'react';

export default function AccessibleDropdown({ options = [], onSelect }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      return;
    }
    if (e.key === 'Enter' || e.key === ' ') {
      setIsOpen(prev => !prev);
    }
  };

  return (
    <div className="relative inline-block" onKeyDown={handleKeyDown}>
      <button
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        className="border px-4 py-2 rounded"
      >
        {selected ? selected.label : 'Select an option'}
      </button>

      {isOpen && (
        <ul role="listbox" className="absolute border bg-white mt-1 w-full shadow-lg">
          {options.map((opt) => (
            <li
              key={opt.value}
              role="option"
              onClick={() => {
                setSelected(opt);
                setIsOpen(false);
                onSelect(opt);
              }}
              className="p-2 hover:bg-slate-100 cursor-pointer"
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

### Challenge 111: [FE-H01] Concurrent Frontend Requests Create Inconsistent Checkout State
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Concurrency

**Bug Description & Root Cause:**
During flash sales, customers click "Checkout" while background cart inventory verification is still in flight. Because there is no atomic state lock or mutex, two concurrent checkout requests are dispatched with the same cart items, creating duplicate bookings and split billing charges.

**Reference Solution Implementation:**
*CheckoutFlow.jsx*:
```javascript
import React, { useState } from 'react';

export default function CheckoutFlow({ cart, api }) {
  const [status, setStatus] = useState('idle');
  const [orderId, setOrderId] = useState(null);

  const handleCheckout = async () => {
    if (status === 'processing') return;
    setStatus('processing');
    try {
      const res = await api.createOrder(cart);
      setOrderId(res.id);
      setStatus('completed');
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div className="p-4">
      <h3>Cart Total: ${cart.total}</h3>
      <button
        onClick={handleCheckout}
        disabled={status === 'completed' || status === 'processing'}
        className="bg-blue-600 text-white px-4 py-2 rounded mt-2"
      >
        {status === 'processing' ? 'Authorizing...' : 'Confirm Checkout'}
      </button>
      {orderId && <p className="text-green-600 mt-2">Order Confirmed: {orderId}</p>}
    </div>
  );
}
```

---

### Challenge 112: [FE-H02] Memory Leak Develops After Repeated Mount/Unmount Cycles
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Memory Management

**Bug Description & Root Cause:**
When users switch between different coin tabs, browser memory continuously increases until the tab crashes with an "Out of Memory" error. The React DevTools console also outputs warnings: `"Can't perform a React state update on an unmounted component"`.

**Reference Solution Implementation:**
*SubscriptionWidget.jsx*:
```javascript
import React, { useState, useEffect } from 'react';

export default function SubscriptionWidget({ symbol, eventBus }) {
  const [price, setPrice] = useState(null);

  useEffect(() => {
    const handleTick = (newPrice) => {
      setPrice(newPrice);
    };

    eventBus.subscribe(symbol, handleTick);
    return () => {
      eventBus.unsubscribe(symbol, handleTick);
    };
  }, [symbol, eventBus]);

  return (
    <div className="card p-4 border rounded">
      <h4>{symbol}</h4>
      <p className="text-2xl font-mono">{price ? `$${price}` : 'Connecting...'}</p>
    </div>
  );
}
```

---

### Challenge 113: [FE-H03] Shared Client-Side Cache Exposes Data Between Sessions
- **Difficulty:** Hard (300 pts)
- **Technology:** JavaScript
- **Category:** Security

**Bug Description & Root Cause:**
Nurse Sarah logs into the kiosk, reviews Patient X's records, and clicks "Log Out". When Doctor Robert logs in next on the same workstation, the app reads from the client-side session cache before network validation completes, displaying Patient X's confidential records under Doctor Robert's session!

**Reference Solution Implementation:**
*SessionCache.jsx*:
```javascript
import React from 'react';

export const sessionCache = new Map();

export async function logoutUser(authApi, onLoggedOut) {
  try {
    await authApi.logout();
    localStorage.removeItem('authToken');
    sessionCache.clear();
  } finally {
    if (onLoggedOut) onLoggedOut();
  }
}

export default function SessionCacheView({ currentUser, onLogout, authApi }) {
  return (
    <div className="p-4">
      <p>Signed in as: {currentUser?.username}</p>
      <button
        onClick={() => logoutUser(authApi, onLogout)}
        className="bg-red-600 text-white px-3 py-1 rounded"
      >
        Sign Out
      </button>
    </div>
  );
}
```

---

### Challenge 114: [FE-H04] Optimistic UI Update Corrupts State After Failed Requests
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Optimistic UI

**Bug Description & Root Cause:**
A user clicks "Like" twice quickly under poor network conditions. The first request fails on the server. The rollback logic blindly subtracts 1 from the *current* count, but because the user had already clicked again, the like count drops below zero (`likes: -1`), permanently corrupting the counter.

**Reference Solution Implementation:**
*OptimisticFeed.jsx*:
```javascript
import React, { useState } from 'react';

export default function OptimisticFeed({ initialLikes = 10, api }) {
  const [likes, setLikes] = useState(initialLikes);
  const [isLiked, setIsLiked] = useState(false);

  const handleToggleLike = async () => {
    const previousLikes = likes;
    const previousIsLiked = isLiked;
    setLikes(likes + 1);
    setIsLiked(true);

    try {
      await api.likePost();
    } catch (err) {
      setLikes(previousLikes);
      setIsLiked(previousIsLiked);
    }
  };

  return (
    <div className="p-4 border rounded">
      <button
        onClick={handleToggleLike}
        className={`px-4 py-2 rounded ${isLiked ? 'bg-pink-600 text-white' : 'bg-gray-200'}`}
      >
        ❤️ {likes} Likes
      </button>
    </div>
  );
}
```

---

### Challenge 115: [FE-H05] Complex Dashboard Produces Inconsistent Derived State
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Performance & Memoization

**Bug Description & Root Cause:**
When an executive switches the tier filter from "Enterprise" to "Starter", the transaction table updates, but the KPI Summary cards continue to display Enterprise MRR! Profiling shows `useMemo` closed over an empty dependency array `[]`.

**Reference Solution Implementation:**
*AnalyticsHub.jsx*:
```javascript
import React, { useState, useMemo } from 'react';

export default function AnalyticsHub({ transactions = [] }) {
  const [tierFilter, setTierFilter] = useState('All');

  const metrics = useMemo(() => {
    const filtered = tierFilter === 'All'
      ? transactions
      : transactions.filter(t => t.tier === tierFilter);

    const totalMRR = filtered.reduce((acc, curr) => acc + curr.amount, 0);
    const avgMRR = filtered.length ? totalMRR / filtered.length : 0;
    return { totalMRR, avgMRR, count: filtered.length };
  }, [transactions, tierFilter]);

  return (
    <div className="p-4">
      <select value={tierFilter} onChange={(e) => setTierFilter(e.target.value)}>
        <option value="All">All</option>
        <option value="Starter">Starter</option>
        <option value="Enterprise">Enterprise</option>
      </select>
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="border p-4">Total MRR: ${metrics.totalMRR}</div>
        <div className="border p-4">Transactions: {metrics.count}</div>
      </div>
    </div>
  );
}
```

---

### Challenge 116: [FE-H06] Concurrent API Calls Trigger Multiple Token Refreshes
- **Difficulty:** Hard (300 pts)
- **Technology:** JavaScript
- **Category:** Authentication Architecture

**Bug Description & Root Cause:**
When the user's access token expires, all 4 concurrent requests return 401 Unauthorized simultaneously. Each response interceptor independently calls `refreshTokenApi()`. The backend implements refresh token rotation (one-time use per refresh token). The first refresh succeeds, but the subsequent 3 requests arrive with the now-invalidated old refresh token, causing the backend to flag a replay attack and terminate the user's session!

**Reference Solution Implementation:**
*AuthManager.jsx*:
```javascript
let currentToken = 'old_token';
let refreshPromise = null;

export async function requestWithAuth(url, fetchApi, refreshApi) {
  try {
    return await fetchApi(url, currentToken);
  } catch (err) {
    if (err.status === 401) {
      if (!refreshPromise) {
        refreshPromise = refreshApi().finally(() => {
          refreshPromise = null;
        });
      }
      const newTokens = await refreshPromise;
      currentToken = newTokens.accessToken;
      return await fetchApi(url, currentToken);
    }
    throw err;
  }
}
```

---

### Challenge 117: [FE-H07] Virtualized List Renders Incorrect Items After Filtering
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Virtualization

**Bug Description & Root Cause:**
When filtering logs from "ALL" to "ERROR", log messages from other levels stay visible in the viewport or jump to wrong rows. Inspecting the DOM reveals the virtual list mapped array index `index` as the React `key`, confusing React's reconciliation engine.

**Reference Solution Implementation:**
*VirtualList.jsx*:
```javascript
import React, { useState } from 'react';

export default function VirtualList({ items = [], rowHeight = 35, viewportHeight = 350 }) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - 2);
  const visibleCount = Math.ceil(viewportHeight / rowHeight) + 4;
  const visibleItems = items.slice(startIndex, startIndex + visibleCount);

  return (
    <div
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
      style={{ height: viewportHeight, overflowY: 'auto', position: 'relative' }}
      className="border"
    >
      <div style={{ height: items.length * rowHeight, position: 'relative' }}>
        {visibleItems.map((item) => (
          <div
            key={item.id}
            style={{
              position: 'absolute',
              top: items.indexOf(item) * rowHeight,
              height: rowHeight,
              width: '100%'
            }}
            className="p-2 border-b truncate"
          >
            [{item.level}] {item.message}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### Challenge 118: [FE-H08] Multi-Step Checkout Loses Consistency on Partial Failure
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Compensating Transactions

**Bug Description & Root Cause:**
If the credit card fails (e.g. insufficient funds), the checkout displays an error, but never releases the held seat (`releaseSeat(reservationId)`). The seat remains locked for 10 minutes, preventing the passenger from retrying with another card and blocking other customers from booking that seat.

**Reference Solution Implementation:**
*MultiStepCheckout.jsx*:
```javascript
import React, { useState } from 'react';

export default function MultiStepCheckout({ flightId, seatNumber, api }) {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const handleBook = async (paymentDetails) => {
    setStatus('booking');
    setError(null);
    let reservation = null;

    try {
      reservation = await api.reserveSeat(flightId, seatNumber);
      await api.processPayment(reservation.id, paymentDetails);
      setStatus('confirmed');
    } catch (err) {
      if (reservation) {
        await api.releaseSeat(reservation.id);
      }
      setError(err.message || 'Payment failed');
      setStatus('failed');
    }
  };

  return (
    <div className="p-4 border rounded">
      <h3>Seat: {seatNumber}</h3>
      {error && <p className="text-red-500">{error}</p>}
      <button
        onClick={() => handleBook({ card: '4111...' })}
        disabled={status === 'booking'}
        className="bg-indigo-600 text-white px-4 py-2 rounded mt-2"
      >
        {status === 'booking' ? 'Processing...' : 'Book & Pay'}
      </button>
    </div>
  );
}
```

---

### Challenge 119: [FE-H09] Real-Time Interface Applies Out-Of-Order Events
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Real-Time State

**Bug Description & Root Cause:**
Under spotty cellular network connections, packets arrive out of sequence. An older event packet with `seq: 14` arrives after a newer packet with `seq: 15`. The editor blindly sets document content from the arriving payload, reverting recent changes and causing text to jump backwards.

**Reference Solution Implementation:**
*RealtimeChat.jsx*:
```javascript
import React, { useState, useRef, useEffect } from 'react';

export default function RealtimeChat({ socket }) {
  const [content, setContent] = useState('');
  const lastSeq = useRef(0);

  useEffect(() => {
    const handleIncomingMessage = (event) => {
      if (event.seq <= lastSeq.current) return;
      setContent(event.text);
      lastSeq.current = event.seq;
    };

    socket.on('message', handleIncomingMessage);
    return () => socket.off('message', handleIncomingMessage);
  }, [socket]);

  return (
    <div className="p-4 border">
      <h3>Live Document</h3>
      <div className="p-2 bg-gray-100 rounded mt-2">{content}</div>
    </div>
  );
}
```

---

### Challenge 120: [FE-H10] Frontend Fails to Gracefully Handle 403 Forbidden Responses
- **Difficulty:** Hard (300 pts)
- **Technology:** React
- **Category:** Security & Error Handling

**Bug Description & Root Cause:**
If an organization's billing plan expires or an admin's session permissions are revoked in another tab, clicking "Delete Account" returns HTTP 403 Forbidden. Because `handleDelete` lacks a catch handler for 403, an uncaught rejection bubbles up, triggering React's unhandled rejection boundary and crashing the entire application into a blank white screen!

**Reference Solution Implementation:**
*AdminPanel.jsx*:
```javascript
import React, { useState } from 'react';

export default function AdminPanel({ user, api, onAccessDenied }) {
  const [errorMessage, setErrorMessage] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    setErrorMessage('');
    try {
      await api.deleteAccount(user.id);
    } catch (err) {
      if (err.status === 403) {
        setErrorMessage('Access Denied');
        if (onAccessDenied) onAccessDenied();
      } else {
        setErrorMessage('Failed to delete account');
      }
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="p-4 border rounded border-red-300">
      <h3 className="text-red-700 font-bold">Danger Zone</h3>
      {errorMessage && <p className="text-red-500 mb-2">{errorMessage}</p>}
      <button
        onClick={handleDelete}
        disabled={isDeleting}
        className="bg-red-600 text-white px-3 py-1 rounded"
      >
        {isDeleting ? 'Deleting...' : 'Delete Account'}
      </button>
    </div>
  );
}
```

---
