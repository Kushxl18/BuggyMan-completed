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
    'content': '''def sort_and_paginate_posts(posts, page=1, page_size=2):
    sorted_posts = sorted(posts, key=lambda p: (-p['upvotes'], p['id']))
    start = (page - 1) * page_size
    return sorted_posts[start:start + page_size]
'''
}]

# 19. webhook_dispatcher.py
solutions[19] = [{
    'name': 'webhook_dispatcher.py',
    'content': '''def handle_webhook_event(event, processed_events, order_actions):
    event_id = event.get('id')
    if event_id in processed_events:
        return 'ALREADY_PROCESSED'
    processed_events.add(event_id)
    action = f"FULFILL_{event['order_id']}"
    order_actions.append(action)
    return 'PROCESSED'
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
    'content': '''def process_timesheets(rows):
    valid_records = []
    quarantined_records = []
    for r in rows:
        try:
            hours = float(r['hours'])
            valid_records.append({'emp_id': r['emp_id'], 'hours': hours})
        except Exception as err:
            quarantined_records.append({'record': r, 'error': str(err)})
    return {'valid': valid_records, 'quarantined': quarantined_records}
'''
}]

# 24. worker_queue.py
solutions[24] = [{
    'name': 'worker_queue.py',
    'content': '''def execute_job(queue, job, job_fn):
    try:
        job_fn(job)
        queue.ack(job['id'])
        return True
    except Exception as err:
        queue.send_to_dlq(job, str(err))
        return False
'''
}]

# 25. account_transfer.py
solutions[25] = [{
    'name': 'account_transfer.py',
    'content': '''def transfer_funds(balances, sender, receiver, amount):
    if balances.get(sender, 0) < amount:
        raise ValueError('Insufficient funds')
    if receiver not in balances:
        raise KeyError(f'Receiver {receiver} not found')
    balances[sender] -= amount
    balances[receiver] += amount
    return True
'''
}]

# 26. data_fetcher.py
solutions[26] = [{
    'name': 'data_fetcher.py',
    'content': '''class AsyncResultStore:
    def __init__(self):
        self.current_result = None
        self.latest_issued_seq = 0
        self.last_applied_seq = 0
    def apply_response(self, response_seq_id, data):
        if response_seq_id < self.latest_issued_seq:
            return False
        self.current_result = data
        self.last_applied_seq = response_seq_id
        return True
'''
}]

# 27. token_refresh.py
solutions[27] = [{
    'name': 'token_refresh.py',
    'content': '''class TokenManager:
    def __init__(self, refresh_fn):
        self.refresh_fn = refresh_fn
        self.access_token = None
        self.is_refreshing = False
    def get_token(self):
        if self.access_token is not None:
            return self.access_token
        fresh_token = self.refresh_fn()
        self.access_token = fresh_token
        return self.access_token
'''
}]

# 28. config_merger.py
solutions[28] = [{
    'name': 'config_merger.py',
    'content': '''def deep_merge(base, override):
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result
'''
}]

# 29. inventory_service.py
solutions[29] = [{
    'name': 'inventory_service.py',
    'content': '''def decrement_stock(inventory, item_id, qty):
    if inventory.get(item_id, 0) < qty:
        raise ValueError('Insufficient stock')
    inventory[item_id] = inventory[item_id] - qty
    return inventory[item_id]
'''
}]

# 30. csv_exporter.py
solutions[30] = [{
    'name': 'csv_exporter.py',
    'content': '''import csv, io
def export_to_csv_row(fields):
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\\n')
    writer.writerow(fields)
    return output.getvalue()
'''
}]

# 31. batch_processor.py
solutions[31] = [{
    'name': 'batch_processor.py',
    'content': '''def process_batch(items, send_fn):
    succeeded = []
    failed = []
    for item in items:
        try:
            send_fn(item)
            succeeded.append(item['id'])
        except Exception as err:
            failed.append({'id': item['id'], 'error': str(err)})
    return {'succeeded': succeeded, 'failed': failed}
'''
}]

# 32. cursor_paginator.py
solutions[32] = [{
    'name': 'cursor_paginator.py',
    'content': '''def build_page_response(records, page_size, last_id):
    if not records or len(records) < page_size:
        next_cursor = None
    else:
        next_cursor = f'cur_{last_id}'
    return {'records': records, 'next_cursor': next_cursor}
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
    'content': '''class SlidingWindowLimiter:
    def __init__(self, max_requests=100, window_size=60):
        self.max_requests = max_requests
        self.window_size = window_size
        self.history = []
    def allow_request(self, current_time):
        cutoff = current_time - self.window_size
        self.history = [t for t in self.history if t > cutoff]
        if not (len(self.history) < self.max_requests):
            return False
        self.history.append(current_time)
        return True
'''
}]

# 35. service_client.py
solutions[35] = [{
    'name': 'service_client.py',
    'content': '''def verify_credentials(auth_fn, username, password):
    try:
        return auth_fn(username, password)
    except ConnectionError:
        raise
    except Exception:
        return {'authenticated': False, 'error': 'Invalid credentials'}
'''
}]

# 36. payment_gateway.py
solutions[36] = [{
    'name': 'payment_gateway.py',
    'content': '''def process_payment(order_id, paid_orders, processing_locks, charge_fn):
    if order_id in paid_orders:
        return {'status': 'ALREADY_PAID'}
    if order_id in processing_locks:
        return {'status': 'LOCKED'}
    processing_locks.add(order_id)
    try:
        res = charge_fn(order_id)
        paid_orders.add(order_id)
        return {'status': 'SUCCESS', 'charge_id': res}
    finally:
        processing_locks.discard(order_id)
'''
}]

# 37. job_scheduler.py
solutions[37] = [{
    'name': 'job_scheduler.py',
    'content': '''def should_reassign_job(current_time, job_id, leases):
    lease_info = leases.get(job_id)
    if not lease_info:
        return True
    return current_time > lease_info['expires_at']
def renew_lease(leases, job_id, current_time, extension=30):
    if job_id in leases:
        leases[job_id]['expires_at'] = current_time + extension
        return True
    return False
'''
}]

# 38. inventory_allocator.py
solutions[38] = [{
    'name': 'inventory_allocator.py',
    'content': '''def reserve_seats(inventory, flight_id, requested_seats):
    available = inventory.get(flight_id, 0)
    if available < requested_seats:
        return False
    inventory[flight_id] = available - requested_seats
    return True
'''
}]

# 39. cache_aside.py
solutions[39] = [{
    'name': 'cache_aside.py',
    'content': '''def update_user_bio(db, cache, user_id, new_bio):
    db[user_id] = new_bio
    cache.delete(f'user:{user_id}')
    return True
'''
}]

# 40. distributed_lock.py
solutions[40] = [{
    'name': 'distributed_lock.py',
    'content': '''def release_lock(lock_storage, lock_key, owner_token):
    if lock_storage.get(lock_key) == owner_token:
        del lock_storage[lock_key]
        return True
    return False
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
    'content': '''def write_report_safely(file_system, dest_path, content, pid):
    temp_path = f'{dest_path}.tmp.{pid}'
    file_system[temp_path] = content
    file_system[dest_path] = file_system.pop(temp_path)
    return dest_path
'''
}]

# 43. resource_manager.py
solutions[43] = [{
    'name': 'resource_manager.py',
    'content': '''def determine_lock_order(required_resources):
    return sorted(list(required_resources))
'''
}]

# 44. access_controller.py
solutions[44] = [{
    'name': 'access_controller.py',
    'content': '''def elevate_user_role(user_db, actor, target, new_role, auth_checker):
    if not auth_checker(actor):
        raise PermissionError('Actor not authorized to grant roles')
    user_db[target] = new_role
    return True
'''
}]

# 45. migration_runner.py
solutions[45] = [{
    'name': 'migration_runner.py',
    'content': '''def migrate_batch(destination_db, checkpoint_store, batch):
    for record in batch:
        destination_db[record['id']] = record
    if batch:
        checkpoint_store['last_id'] = batch[-1]['id']
    return True
'''
}]

# 46. event_stream.py
solutions[46] = [{
    'name': 'event_stream.py',
    'content': '''def assign_event_shard(event, num_shards):
    entity_id = str(event.get('entity_id', ''))
    return hash(entity_id) % num_shards
'''
}]

# 47. saga_coordinator.py
solutions[47] = [{
    'name': 'saga_coordinator.py',
    'content': '''def execute_saga(steps):
    completed = []
    for step in steps:
        try:
            step.execute()
            completed.append(step)
        except Exception:
            for s in reversed(completed):
                s.rollback()
            raise
    return True
'''
}]

# 48. stream_parser.py
solutions[48] = [{
    'name': 'stream_parser.py',
    'content': '''def parse_stream_chunks(chunks):
    buffer = ''
    for c in chunks:
        buffer += c
        while '\\n' in buffer:
            line, buffer = buffer.split('\\n', 1)
            yield line
    if buffer:
        yield buffer
'''
}]

# 49. account_service.py
solutions[49] = [{
    'name': 'account_service.py',
    'content': '''def update_account(profile, new_email, new_phone):
    if '@' not in new_email:
        raise ValueError('Invalid email')
    if not (new_phone and new_phone.isdigit() and len(new_phone) == 10):
        raise ValueError('Invalid phone number')
    profile['email'] = new_email
    profile['phone'] = new_phone
    return True
'''
}]

# 50. seat_reservation.py
solutions[50] = [{
    'name': 'seat_reservation.py',
    'content': '''def reserve_seat(reservations, seat_id, user_id, current_time, ttl=300):
    existing = reservations.get(seat_id)
    if existing and existing.get('expires_at', 0) > current_time:
        return False
    reservations[seat_id] = {'user': user_id, 'expires_at': current_time + ttl}
    return True
'''
}]

def get_code_solutions():
    return solutions
