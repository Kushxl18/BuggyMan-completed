import sys
import os
import django

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from buggyman.evaluator.engine import EvaluationEngine
from buggyman.data.code_challenges import get_code_challenges

engine = EvaluationEngine()
chs = {c['id']: c for c in get_code_challenges()}

solutions = {}

# 1. pagination.py
solutions[1] = [{
    'name': 'pagination.py',
    'content': '''def paginate(items, page=1, page_size=10):
    if not items or page < 1 or page_size < 1:
        return []
    start = (page - 1) * page_size
    end = min(len(items), page * page_size)
    if start >= len(items):
        return []
    return items[start:end]
'''
}]

# 2. cursor_encoder.py
solutions[2] = [{
    'name': 'cursor_encoder.py',
    'content': '''import base64

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
'''
}]

# 3. api_client.py
solutions[3] = [{
    'name': 'api_client.py',
    'content': '''def extract_latest_price(payload):
    if not isinstance(payload, dict):
        return {"price": 0.0, "status": "unavailable"}
    items = payload.get("items", [])
    if not items or not isinstance(items, list):
        return {"price": 0.0, "status": "unavailable"}
    return {"price": items[0].get("price", 0.0), "status": "active"}
'''
}]

# 4. date_parser.py
solutions[4] = [{
    'name': 'date_parser.py',
    'content': '''from datetime import datetime

def parse_transaction_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None
'''
}]

# 5. retry_handler.py
solutions[5] = [{
    'name': 'retry_handler.py',
    'content': '''def execute_with_retry(operation, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            return operation(attempt)
        except Exception:
            continue
    return None
'''
}]

# 6. deduplicator.py
solutions[6] = [{
    'name': 'deduplicator.py',
    'content': '''def deduplicate_records(records):
    seen = set()
    result = []
    for r in records:
        key = (r.get("clinic_id"), r.get("id"))
        if key not in seen:
            seen.add(key)
            result.append(r)
    return result
'''
}]

# 7. config_loader.py
solutions[7] = [{
    'name': 'config_loader.py',
    'content': '''def get_timeout_seconds(env_dict=None):
    env = env_dict if env_dict is not None else {}
    val = env.get("TIMEOUT_SECONDS")
    if val is None or val == "":
        return 30
    return int(val)
'''
}]

# 8. cache_manager.py
solutions[8] = [{
    'name': 'cache_manager.py',
    'content': '''def generate_cache_key(store_id, user_id):
    return f"store:{store_id}:user:{user_id}"
'''
}]

# 9. validator.py
solutions[9] = [{
    'name': 'validator.py',
    'content': '''def validate_inventory_update(item_id, quantity):
    if not item_id:
        return (False, "Item ID is required")
    if quantity is None:
        return (False, "Quantity is required")
    if quantity < 0:
        return (False, "Quantity cannot be negative")
    return (True, "Valid")
'''
}]

# 10. csv_parser.py
solutions[10] = [{
    'name': 'csv_parser.py',
    'content': '''import csv
import io

def parse_csv_row(row_str):
    if not row_str:
        return []
    reader = csv.reader(io.StringIO(row_str))
    for row in reader:
        return row
    return []
'''
}]

# 11. sorter.py
solutions[11] = [{
    'name': 'sorter.py',
    'content': '''def sort_priority_levels(levels):
    return sorted(levels, key=lambda x: int(x) if str(x).isdigit() else x)
'''
}]

# 12. serializer.py
solutions[12] = [{
    'name': 'serializer.py',
    'content': '''def serialize_user_profile(user_model):
    if not user_model:
        return {}
    return {
        "id": user_model.get("id"),
        "username": user_model.get("username"),
        "email": user_model.get("email"),
        "created_at": user_model.get("created_at")
    }
'''
}]

# 13. token_service.py
solutions[13] = [{
    'name': 'token_service.py',
    'content': '''def calculate_expiration(current_timestamp, seconds_to_live=3600):
    return current_timestamp + seconds_to_live
'''
}]

# 14. queue_processor.py
solutions[14] = [{
    'name': 'queue_processor.py',
    'content': '''def peek_next_job(queue):
    if not queue:
        return None
    return queue[0]
'''
}]

# 15. invoice_calculator.py
solutions[15] = [{
    'name': 'invoice_calculator.py',
    'content': '''def calculate_total_tax(line_items, tax_rate=0.0825):
    if not line_items:
        return 0.0
    subtotal = sum(line_items)
    return round(subtotal * tax_rate, 2)
'''
}]

# 16. payment_client.py
solutions[16] = [{
    'name': 'payment_client.py',
    'content': '''import uuid

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
'''
}]

# 17. pricing_service.py
solutions[17] = [{
    'name': 'pricing_service.py',
    'content': '''def update_product_price(db, cache, product_id, category_id, new_price):
    db[product_id] = {"price": new_price, "category": category_id}
    cache.delete(f"product:{product_id}")
    cache.delete(f"category:{category_id}")
    return True
'''
}]

# 18. paginator.py
solutions[18] = [{
    'name': 'paginator.py',
    'content': '''def paginate_sorted_records(records, offset=0, limit=10):
    sorted_records = sorted(records, key=lambda r: (r.get("priority", 0), r.get("id", 0)))
    return sorted_records[offset:offset + limit]
'''
}]

# 19. webhook_dispatcher.py
solutions[19] = [{
    'name': 'webhook_dispatcher.py',
    'content': '''class WebhookDispatcher:
    def __init__(self, processed_ids=None):
        self.processed = processed_ids if processed_ids is not None else set()

    def handle_event(self, event, handler_fn):
        event_id = event.get("id")
        if event_id in self.processed:
            return False
        self.processed.add(event_id)
        handler_fn(event)
        return True
'''
}]

# 20. preference_manager.py
solutions[20] = [{
    'name': 'preference_manager.py',
    'content': '''def update_user_preferences(current_prefs, update_payload):
    current_version = current_prefs.get("version", 0)
    update_version = update_payload.get("version", 0)
    if update_version <= current_version:
        return False
    current_prefs.update(update_payload)
    return True
'''
}]

# 21. scheduler.py
solutions[21] = [{
    'name': 'scheduler.py',
    'content': '''def convert_local_to_utc_hour(local_hour, utc_offset_hours):
    return (local_hour - utc_offset_hours) % 24
'''
}]

# 22. http_client.py
solutions[22] = [{
    'name': 'http_client.py',
    'content': '''def parse_rate_limit_delay(response_headers, attempt=1):
    val = response_headers.get("Retry-After")
    if val is not None:
        try:
            return max(1, int(val))
        except (ValueError, TypeError):
            pass
    return 2 ** attempt
'''
}]

# 23. pipeline.py
solutions[23] = [{
    'name': 'pipeline.py',
    'content': '''def process_pipeline_records(records):
    valid = []
    dropped = []
    for r in records:
        if isinstance(r, dict) and r.get("id") and r.get("email"):
            valid.append(r)
        else:
            dropped.append(r)
    return {"valid": valid, "dropped": dropped}
'''
}]

# 24. worker_queue.py
solutions[24] = [{
    'name': 'worker_queue.py',
    'content': '''class WorkerQueue:
    def __init__(self):
        self.dead_letter_queue = []

    def handle_failed_job(self, job, error):
        self.dead_letter_queue.append({
            "job": job,
            "error": str(error)
        })
'''
}]

# 25. account_transfer.py
solutions[25] = [{
    'name': 'account_transfer.py',
    'content': '''def transfer_funds(ledger, source_id, dest_id, amount):
    if ledger.get_balance(source_id) < amount:
        return False
    with ledger.transaction():
        ledger.debit(source_id, amount)
        ledger.credit(dest_id, amount)
    return True
'''
}]

# 26. data_fetcher.py
solutions[26] = [{
    'name': 'data_fetcher.py',
    'content': '''import asyncio

async def fetch_user_data(client, user_id):
    profile, perms = await asyncio.gather(
        client.get_profile(user_id),
        client.get_permissions(user_id)
    )
    return {"profile": profile, "permissions": perms}
'''
}]

# 27. token_refresh.py
solutions[27] = [{
    'name': 'token_refresh.py',
    'content': '''class TokenRefreshManager:
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
'''
}]

# 28. config_merger.py
solutions[28] = [{
    'name': 'config_merger.py',
    'content': '''def deep_merge_configs(base, override):
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge_configs(result[k], v)
        else:
            result[k] = v
    return result
'''
}]

# 29. inventory_service.py
solutions[29] = [{
    'name': 'inventory_service.py',
    'content': '''def apply_inventory_adjustment(current_stock, delta):
    new_stock = current_stock + delta
    if new_stock < 0:
        return False, current_stock
    return True, new_stock
'''
}]

# 30. csv_exporter.py
solutions[30] = [{
    'name': 'csv_exporter.py',
    'content': '''import csv
import io

def export_records_to_csv(records, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\\n')
    writer.writeheader()
    for r in records:
        writer.writerow(r)
    return output.getvalue()
'''
}]

# 31. batch_processor.py
solutions[31] = [{
    'name': 'batch_processor.py',
    'content': '''def execute_batch(items, process_fn):
    succeeded = []
    failed = []
    for item in items:
        try:
            res = process_fn(item)
            succeeded.append(res)
        except Exception as e:
            failed.append({"item": item, "error": str(e)})
    return {"succeeded": succeeded, "failed": failed}
'''
}]

# 32. cursor_paginator.py
solutions[32] = [{
    'name': 'cursor_paginator.py',
    'content': '''def get_next_cursor(items, last_seen_cursor):
    if not items:
        return None
    next_cursor = items[-1].get("cursor")
    if next_cursor == last_seen_cursor:
        return None
    return next_cursor
'''
}]

# 33. transformer.py
solutions[33] = [{
    'name': 'transformer.py',
    'content': '''def format_postal_address(profile):
    addr = profile.get("address") if isinstance(profile, dict) else None
    city = addr.get("city", "Unknown City") if isinstance(addr, dict) else "Unknown City"
    name = profile.get("name", "Unknown") if isinstance(profile, dict) else "Unknown"
    return f"{name}, {city}"
'''
}]

# 34. rate_limiter.py
solutions[34] = [{
    'name': 'rate_limiter.py',
    'content': '''import time

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
'''
}]

# 35. service_client.py
solutions[35] = [{
    'name': 'service_client.py',
    'content': '''def call_external_service(client, endpoint):
    try:
        return client.request(endpoint)
    except Exception as e:
        import logging
        logging.error(f"Service call failed: {e}", exc_info=True)
        raise
'''
}]

# 36. payment_gateway.py
solutions[36] = [{
    'name': 'payment_gateway.py',
    'content': '''class ConcurrentPaymentGateway:
    def __init__(self, ledger):
        self.ledger = ledger

    def process_charge(self, account_id, amount, idempotency_key):
        if self.ledger.has_processed(idempotency_key):
            return self.ledger.get_transaction(idempotency_key)
        with self.ledger.lock(account_id):
            if self.ledger.has_processed(idempotency_key):
                return self.ledger.get_transaction(idempotency_key)
            return self.ledger.debit(account_id, amount, idempotency_key=idempotency_key)
'''
}]

# 37. job_scheduler.py
solutions[37] = [{
    'name': 'job_scheduler.py',
    'content': '''class DistributedJobScheduler:
    def __init__(self, lock_manager):
        self.lock_manager = lock_manager

    def execute_job(self, job_id, job_fn):
        with self.lock_manager.acquire(job_id) as acquired:
            if not acquired:
                return False
            job_fn()
            return True
'''
}]

# 38. inventory_allocator.py
solutions[38] = [{
    'name': 'inventory_allocator.py',
    'content': '''def allocate_inventory(db_session, item_id, quantity):
    with db_session.begin():
        item = db_session.query_for_update(item_id)
        if item.available_stock < quantity:
            return False
        item.available_stock -= quantity
        db_session.commit()
    return True
'''
}]

# 39. cache_aside.py
solutions[39] = [{
    'name': 'cache_aside.py',
    'content': '''def update_user_profile(db, cache, user_id, new_data):
    db.update_user(user_id, new_data)
    cache.delete(f"user:{user_id}")
'''
}]

# 40. distributed_lock.py
solutions[40] = [{
    'name': 'distributed_lock.py',
    'content': '''class DistributedLock:
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
'''
}]

# 41. backoff_client.py
solutions[41] = [{
    'name': 'backoff_client.py',
    'content': '''def calculate_backoff(attempt, base_delay=1, max_delay=32, jitter=0):
    return min(max_delay, base_delay * (2 ** attempt) + jitter)
'''
}]

# 42. report_writer.py
solutions[42] = [{
    'name': 'report_writer.py',
    'content': '''import os
import tempfile

def write_atomic_report(filepath, content):
    dir_name = os.path.dirname(filepath)
    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False) as tf:
        tf.write(content)
        temp_name = tf.name
    os.replace(temp_name, filepath)
'''
}]

# 43. resource_manager.py
solutions[43] = [{
    'name': 'resource_manager.py',
    'content': '''import asyncio

class AsyncResourceManager:
    def __init__(self):
        self.lock = asyncio.Lock()

    async def transfer(self, source, target, amount):
        async with self.lock:
            source.balance -= amount
            target.balance += amount
'''
}]

# 44. access_controller.py
solutions[44] = [{
    'name': 'access_controller.py',
    'content': '''def execute_privileged_operation(user, resource_id, op_fn):
    if not user.has_permission("MODIFY", resource_id):
        raise PermissionError("Access Denied")
    return op_fn(resource_id)
'''
}]

# 45. migration_runner.py
solutions[45] = [{
    'name': 'migration_runner.py',
    'content': '''def run_migration_batch(db, records):
    with db.transaction():
        for r in records:
            db.insert(r)
'''
}]

# 46. event_stream.py
solutions[46] = [{
    'name': 'event_stream.py',
    'content': '''class EventStreamProcessor:
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
'''
}]

# 47. saga_coordinator.py
solutions[47] = [{
    'name': 'saga_coordinator.py',
    'content': '''class SagaCoordinator:
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
'''
}]

# 48. stream_parser.py
solutions[48] = [{
    'name': 'stream_parser.py',
    'content': '''def parse_chunked_stream(stream):
    for chunk in stream:
        yield chunk.strip()
'''
}]

# 49. account_service.py
solutions[49] = [{
    'name': 'account_service.py',
    'content': '''def update_account_status(db, account_id, new_status):
    with db.transaction():
        db.update_status(account_id, new_status)
        db.log_audit(account_id, f"Status updated to {new_status}")
'''
}]

# 50. seat_reservation.py
solutions[50] = [{
    'name': 'seat_reservation.py',
    'content': '''class SeatReservationSystem:
    def __init__(self, total_seats):
        self.available_seats = total_seats
        self.reserved_seats = set()

    def reserve(self, seat_number, user_id):
        if seat_number in self.reserved_seats or self.available_seats <= 0:
            return False
        self.reserved_seats.add(seat_number)
        self.available_seats -= 1
        return True
'''
}]

def get_code_solutions():
    return solutions

if __name__ == '__main__':
    print("Validating all 50 solutions against EvaluationEngine...")
    passed_count = 0
    for cid in range(1, 51):
        c = chs[cid]
        sol = solutions[cid]
        res = engine.evaluate(c, files=sol)
        if res['success']:
            passed_count += 1
        else:
            print(f"FAILED: ID {cid} {c['title']}")
            print("  Error:", res.get('error'))
            print("  AI Summary:", res.get('ai_summary'))
            print("  Test Results:", res.get('test_results'))

    print(f"\nFinal Result: {passed_count}/50 passed")
