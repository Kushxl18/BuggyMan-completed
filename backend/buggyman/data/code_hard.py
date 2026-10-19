"""
Code Arena: Hard Challenges (36 to 50)
"""

def get_code_hard():
    challenges = []

    # 36. Concurrent payment requests cause duplicate charges
    challenges.append({
        'id': 36,
        'title': '[CODE-H01] Concurrent Payment Requests Cause Duplicate Charges',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'payment_gateway.py',
            'content': '''def process_payment(order_id, paid_orders, processing_locks, charge_fn):
    if order_id in paid_orders:
        return {"status": "ALREADY_PAID"}
    # Charge happens before locking
    res = charge_fn(order_id)
    paid_orders.add(order_id)
    return {"status": "SUCCESS", "charge_id": res}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Concurrent lock prevents duplicate charge', 'input': '''paid = set(); locks = set()
charges = []
def mock_charge(oid): charges.append(oid); return "ch_1"
# Process first request
r1 = process_payment("ORD1", paid, locks, mock_charge)
# Simulate second parallel request with order locked
locks.add("ORD2")
r2 = process_payment("ORD2", paid, locks, mock_charge)
(r1["status"] == "SUCCESS" and r2.get("status") in ["LOCKED", "DUPLICATE_IGNORED", "ALREADY_PROCESSING"])''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'if order_id in paid_orders:\n        return {"status": "ALREADY_PAID"}',
        'suspected_component': 'payment_gateway.py',
        'ai_suggestions': [
            'Check both `order_id in paid_orders` and `order_id in processing_locks`.',
            'If either is true, return `{"status": "DUPLICATE_IGNORED"}`.',
            'Acquire lock: `processing_locks.add(order_id)` before calling `charge_fn`, and release in finally block.'
        ],
        'topics': ['Concurrency', 'Distributed Locks', 'Fintech', 'Race Conditions'],
        'skills_tested': ['Python', 'Concurrency', 'Security'],
        'prerequisites': ['Atomic Operations', 'Race Conditions'],
        'status': 'published'
    })

    # 37. A distributed job processor executes non-idempotent jobs twice
    challenges.append({
        'id': 37,
        'title': '[CODE-H02] A Distributed Job Processor Executes Non-Idempotent Jobs Twice',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'job_scheduler.py',
            'content': '''def should_reassign_job(current_time, job_id, leases):
    lease_info = leases.get(job_id)
    if not lease_info:
        return True
    return current_time > lease_info["expires_at"]

def renew_lease(leases, job_id, current_time, extension=30):
    # Missing heartbeat renewal implementation
    pass'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Heartbeat renews lease preventing reassignment', 'input': '''leases = {"J1": {"expires_at": 100}}
renew_lease(leases, "J1", 90, extension=30)
(leases["J1"]["expires_at"] == 120 and should_reassign_job(105, "J1", leases) is False)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'def renew_lease(leases, job_id, current_time, extension=30):\n    pass',
        'suspected_component': 'job_scheduler.py',
        'ai_suggestions': [
            'In `renew_lease`, update `leases[job_id]["expires_at"] = current_time + extension`.'
        ],
        'topics': ['Distributed Systems', 'Leases', 'Heartbeats'],
        'skills_tested': ['Python', 'Backend', 'Architecture'],
        'prerequisites': ['Distributed Leases'],
        'status': 'published'
    })

    # 38. Incorrect transaction isolation causes inconsistent inventory
    challenges.append({
        'id': 38,
        'title': '[CODE-H03] Incorrect Transaction Isolation Causes Inconsistent Inventory',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'inventory_allocator.py',
            'content': '''def reserve_seats(inventory, flight_id, requested_seats):
    current_seats = inventory.get(flight_id, 0)
    if current_seats < requested_seats:
        return False
    inventory[flight_id] = current_seats - requested_seats
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Second allocation fails when stock exhausted', 'input': '''inv = {"FL100": 1}
r1 = reserve_seats(inv, "FL100", 1)
r2 = reserve_seats(inv, "FL100", 1)
(r1 is True and r2 is False and inv["FL100"] == 0)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'current_seats = inventory.get(flight_id, 0)\n    if current_seats < requested_seats:',
        'suspected_component': 'inventory_allocator.py',
        'ai_suggestions': [
            'Use an atomic conditional decrement pattern: verify `inventory.get(flight_id, 0) >= requested_seats` within a single synchronous critical section.'
        ],
        'topics': ['Concurrency', 'Inventory', 'Race Conditions'],
        'skills_tested': ['Python', 'Concurrency'],
        'prerequisites': ['Compare-and-Swap'],
        'status': 'published'
    })

    # 39. Cache invalidation races with concurrent database updates
    challenges.append({
        'id': 39,
        'title': '[CODE-H04] Cache Invalidation Races with Concurrent Database Updates',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Caching',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'cache_aside.py',
            'content': '''def update_user_bio(db, cache, user_id, new_bio):
    cache.delete(f"user:{user_id}")
    db[user_id] = new_bio
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: DB write precedes cache deletion', 'input': '''ops = []
class MockDB:
    def __setitem__(self, k, v): ops.append("DB_WRITE")
class MockCache:
    def delete(self, k): ops.append("CACHE_DELETE")
update_user_bio(MockDB(), MockCache(), "u1", "New Bio")
ops == ["DB_WRITE", "CACHE_DELETE"]''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'cache.delete(f"user:{user_id}")\n    db[user_id] = new_bio',
        'suspected_component': 'cache_aside.py',
        'ai_suggestions': [
            'Reverse the order: perform `db[user_id] = new_bio` first, then `cache.delete(f"user:{user_id}")`.'
        ],
        'topics': ['Cache-Aside', 'Concurrency', 'Data Consistency'],
        'skills_tested': ['Python', 'Caching'],
        'prerequisites': ['Cache-Aside Architecture'],
        'status': 'published'
    })

    # 40. A distributed lock is released by the wrong request
    challenges.append({
        'id': 40,
        'title': '[CODE-H05] A Distributed Lock is Released by the Wrong Request',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'distributed_lock.py',
            'content': '''def release_lock(lock_storage, lock_key, owner_token):
    if lock_key in lock_storage:
        del lock_storage[lock_key]
        return True
    return False'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Wrong token cannot release lock', 'input': '''locks = {"report_lock": "owner_B"}
released = release_lock(locks, "report_lock", "owner_A")
(released is False and "report_lock" in locks)''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Valid owner releases lock', 'input': '''locks = {"report_lock": "owner_A"}
released = release_lock(locks, "report_lock", "owner_A")
(released is True and "report_lock" not in locks)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'if lock_key in lock_storage:\n        del lock_storage[lock_key]',
        'suspected_component': 'distributed_lock.py',
        'ai_suggestions': [
            'Verify ownership: `if lock_storage.get(lock_key) == owner_token:` before deleting.'
        ],
        'topics': ['Distributed Locks', 'Redis', 'Concurrency'],
        'skills_tested': ['Python', 'Concurrency', 'Security'],
        'prerequisites': ['Distributed Lock Semantics'],
        'status': 'published'
    })

    # 41. A retry mechanism causes a request storm during an outage
    challenges.append({
        'id': 41,
        'title': '[CODE-H06] A Retry Mechanism Causes a Request Storm During an Outage',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'backoff_client.py',
            'content': '''def calculate_backoff(attempt, base_delay=1, max_delay=32, jitter=0):
    return min(max_delay, base_delay * attempt + jitter)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Exponential growth at attempt 3', 'input': 'calculate_backoff(3, base_delay=2, max_delay=60, jitter=0)', 'expected': '16', 'hidden': False},
            {'id': 2, 'name': 'Visible: Capped at max_delay', 'input': 'calculate_backoff(10, base_delay=2, max_delay=30, jitter=0)', 'expected': '30', 'hidden': False}
        ],
        'bug_signature': 'return min(max_delay, base_delay * attempt + jitter)',
        'suspected_component': 'backoff_client.py',
        'ai_suggestions': [
            'Use exponential factor `2 ** attempt`: `delay = min(max_delay, base_delay * (2 ** attempt)) + jitter`.'
        ],
        'topics': ['Resilience', 'Exponential Backoff', 'Jitter', 'Thundering Herd'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Exponential Backoff'],
        'status': 'published'
    })

    # 42. Concurrent file writes corrupt generated reports
    challenges.append({
        'id': 42,
        'title': '[CODE-H07] Concurrent File Writes Corrupt Generated Reports',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'report_writer.py',
            'content': '''def write_report_safely(file_system, dest_path, content, pid):
    file_system[dest_path] = content
    return dest_path'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Writes to temp file then renames', 'input': '''class MockFS(dict):
    def __init__(self):
        super().__init__()
        self.temp_used = False
    def __setitem__(self, k, v):
        if ".tmp." in str(k):
            self.temp_used = True
        super().__setitem__(k, v)

fs = MockFS()
write_report_safely(fs, "report.csv", "DATA", 123)
fs.temp_used and fs.get("report.csv") == "DATA"''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'file_system[dest_path] = content\n    return dest_path',
        'suspected_component': 'report_writer.py',
        'ai_suggestions': [
            'Write to `temp_path = f"{dest_path}.tmp.{pid}"` first.',
            'Then assign `file_system[dest_path] = file_system.pop(temp_path)`.'
        ],
        'topics': ['File I/O', 'Atomicity', 'Concurrency'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Atomic File Writes'],
        'status': 'published'
    })

    # 43. An asynchronous task deadlocks under concurrent execution
    challenges.append({
        'id': 43,
        'title': '[CODE-H08] An Asynchronous Task Deadlocks Under Concurrent Execution',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'resource_manager.py',
            'content': '''def determine_lock_order(required_resources):
    return list(required_resources)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Deterministic sorted lock order', 'input': '''r1 = determine_lock_order(["NVMe", "GPU", "CPU"])
r2 = determine_lock_order(["CPU", "NVMe", "GPU"])
r1 == ["CPU", "GPU", "NVMe"] and r2 == ["CPU", "GPU", "NVMe"]''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'return list(required_resources)',
        'suspected_component': 'resource_manager.py',
        'ai_suggestions': [
            'Enforce sorted ordering: `return sorted(required_resources)`.'
        ],
        'topics': ['Deadlocks', 'Concurrency', 'Lock Ordering'],
        'skills_tested': ['Python', 'Concurrency'],
        'prerequisites': ['Deadlock Prevention'],
        'status': 'published'
    })

    # 44. A permission check occurs after a sensitive state change
    challenges.append({
        'id': 44,
        'title': '[CODE-H09] A Permission Check Occurs After a Sensitive State Change',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Security',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'access_controller.py',
            'content': '''def elevate_user_role(user_db, actor, target, new_role, auth_checker):
    user_db[target] = new_role
    if not auth_checker(actor):
        raise PermissionError("Actor not authorized to grant roles")
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Unauthorized attempt leaves target role unchanged', 'input': '''users = {"guest_user": "guest"}
def mock_auth(actor): return False
try:
    elevate_user_role(users, "guest_user", "guest_user", "admin", mock_auth)
except PermissionError:
    pass
users["guest_user"] == "guest"''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'user_db[target] = new_role\n    if not auth_checker(actor):',
        'suspected_component': 'access_controller.py',
        'ai_suggestions': [
            'Move the authorization check to the top: `if not auth_checker(actor): raise PermissionError(...)` before modifying `user_db`.'
        ],
        'topics': ['Security', 'Authorization', 'Defensive Programming'],
        'skills_tested': ['Python', 'Security', 'Backend'],
        'prerequisites': ['Security Fundamentals'],
        'status': 'published'
    })

    # 45. A batch migration loses records after a partial failure
    challenges.append({
        'id': 45,
        'title': '[CODE-H10] A Batch Migration Loses Records After a Partial Failure',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'migration_runner.py',
            'content': '''def migrate_batch(destination_db, checkpoint_store, batch):
    for record in batch:
        destination_db[record["id"]] = record
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Checkpoint updated after batch', 'input': '''db = {}; cp = {}
batch = [{"id": 10}, {"id": 20}, {"id": 30}]
migrate_batch(db, cp, batch)
cp.get("last_id") == 30''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'for record in batch:\n            self.transform(record)\n        return True',
        'suspected_component': 'migration_runner.py',
        'ai_suggestions': [
            'Add `if batch: checkpoint_store["last_id"] = batch[-1]["id"]`.'
        ],
        'topics': ['Migrations', 'Checkpoints', 'Fault Tolerance'],
        'skills_tested': ['Python', 'Backend', 'Data Processing'],
        'prerequisites': ['Checkpoints in Data Processing'],
        'status': 'published'
    })

    # 46. An event-processing pipeline reorders dependent events
    challenges.append({
        'id': 46,
        'title': '[CODE-H11] An Event-Processing Pipeline Reorders Dependent Events',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'event_stream.py',
            'content': '''def assign_event_shard(event, num_shards):
    import random
    return random.randint(0, num_shards - 1)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Same entity ID always routes to identical shard', 'input': '''e1 = {"entity_id": "ORD_99", "type": "CREATE"}
e2 = {"entity_id": "ORD_99", "type": "CANCEL"}
assign_event_shard(e1, 4) == assign_event_shard(e2, 4)''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'return random.randint(0, num_shards - 1)',
        'suspected_component': 'event_stream.py',
        'ai_suggestions': [
            'Use hash partitioning: `return abs(hash(event["entity_id"])) % num_shards`.'
        ],
        'topics': ['Event Sourcing', 'Partitioning', 'Concurrency'],
        'skills_tested': ['Python', 'Concurrency', 'Architecture'],
        'prerequisites': ['Consistent Partitioning'],
        'status': 'published'
    })

    # 47. Incorrect rollback logic leaves related resources inconsistent
    challenges.append({
        'id': 47,
        'title': '[CODE-H12] Incorrect Rollback Logic Leaves Related Resources Inconsistent',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'saga_coordinator.py',
            'content': '''def execute_saga(steps):
    completed = []
    for step in steps:
        try:
            step.execute()
            completed.append(step)
        except Exception:
            if completed:
                completed[-1].rollback()
            raise
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: All completed steps rolled back in reverse', 'input': '''rolled_back = []
class MockStep:
    def __init__(self, name, fail=False): self.name = name; self.fail = fail
    def execute(self):
        if self.fail: raise RuntimeError(f"{self.name} failed")
    def rollback(self): rolled_back.append(self.name)

steps = [MockStep("Flight"), MockStep("Hotel"), MockStep("Car", fail=True)]
try:
    execute_saga(steps)
except RuntimeError:
    pass
rolled_back == ["Hotel", "Flight"]''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'if completed:\n                completed[-1].rollback()',
        'suspected_component': 'saga_coordinator.py',
        'ai_suggestions': [
            'Use a loop to rollback all completed steps: `for s in reversed(completed): s.rollback()`.'
        ],
        'topics': ['Saga Pattern', 'Distributed Transactions', 'Compensating Actions'],
        'skills_tested': ['Python', 'Architecture', 'Transactions'],
        'prerequisites': ['Saga Orchestration'],
        'status': 'published'
    })

    # 48. A streaming parser leaks memory for large inputs
    challenges.append({
        'id': 48,
        'title': '[CODE-H13] A Streaming Parser Leaks Memory for Large Inputs',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Performance',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'stream_parser.py',
            'content': '''def parse_stream_chunks(chunks):
    all_chunks = []
    lines = []
    for chunk in chunks:
        all_chunks.append(chunk)
        full_text = "".join(all_chunks)
        # Parse logic
    return lines'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Streaming generator yields lines without full accumulation', 'input': '''chunks = ["line1\\nli", "ne2\\n", "line3\\n"]
list(parse_stream_chunks(chunks)) == ["line1", "line2", "line3"]''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'all_chunks = []\n    lines = []\n    for chunk in chunks:\n        all_chunks.append(chunk)',
        'suspected_component': 'stream_parser.py',
        'ai_suggestions': [
            'Maintain a single `buffer = ""` string instead of an accumulating list.',
            'Split on `\\n` and discard yielded lines from `buffer`.'
        ],
        'topics': ['Memory Management', 'Streaming', 'Generators'],
        'skills_tested': ['Python', 'Performance'],
        'prerequisites': ['Generators and Streams'],
        'status': 'published'
    })

    # 49. A multi-step account update leaves partially modified state
    challenges.append({
        'id': 49,
        'title': '[CODE-H14] A Multi-Step Account Update Leaves Partially Modified State',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'account_service.py',
            'content': '''def update_account(profile, new_email, new_phone):
    if "@" in new_email:
        profile["email"] = new_email
    if not (new_phone and new_phone.isdigit() and len(new_phone) == 10):
        raise ValueError("Invalid phone number")
    profile["phone"] = new_phone
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Invalid phone leaves email untouched', 'input': '''prof = {"email": "old@test.com", "phone": "1111111111"}
try:
    update_account(prof, "new@test.com", "bad_phone")
except ValueError:
    pass
prof["email"] == "old@test.com"''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'if "@" in new_email:\n        profile["email"] = new_email\n    if not (new_phone',
        'suspected_component': 'account_service.py',
        'ai_suggestions': [
            'Validate both inputs upfront: validate email format and check `new_phone.isdigit() and len(new_phone) == 10`.',
            'Only update `profile["email"]` and `profile["phone"]` after all checks pass.'
        ],
        'topics': ['Transactions', 'Validation', 'Atomicity'],
        'skills_tested': ['Python', 'Backend', 'Validation'],
        'prerequisites': ['Defensive Programming'],
        'status': 'published'
    })

    # 50. A concurrent reservation system oversells limited inventory
    challenges.append({
        'id': 50,
        'title': '[CODE-H15] A Concurrent Reservation System Oversells Limited Inventory',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
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
""",
        'files': [{
            'name': 'seat_reservation.py',
            'content': '''def reserve_seat(reservations, seat_id, user_id, current_time, ttl=300):
    reservations[seat_id] = {"user": user_id, "expires_at": current_time + ttl}
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Active reservation blocks new buyer', 'input': '''res = {}
r1 = reserve_seat(res, "A1", "Alice", 100, ttl=300)
r2 = reserve_seat(res, "A1", "Bob", 150, ttl=300)
(r1 is True and r2 is False and res["A1"]["user"] == "Alice")''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Visible: Expired reservation allows new buyer', 'input': '''res = {"A1": {"user": "Alice", "expires_at": 200}}
r = reserve_seat(res, "A1", "Bob", 250, ttl=300)
(r is True and res["A1"]["user"] == "Bob")''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'reservations[seat_id] = {"user": user_id, "expires_at": current_time + ttl}\n    return True',
        'suspected_component': 'seat_reservation.py',
        'ai_suggestions': [
            'Check: `existing = reservations.get(seat_id)`. If `existing and current_time < existing["expires_at"]: return False`.'
        ],
        'topics': ['Concurrency', 'Reservations', 'Timeouts'],
        'skills_tested': ['Python', 'Concurrency', 'Backend'],
        'prerequisites': ['Expiring Leases'],
        'status': 'published'
    })

    return challenges
