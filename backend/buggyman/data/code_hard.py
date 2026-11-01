"""
Code Arena: Hard Challenges (36 to 50)
"""

def get_code_hard():
    challenges = []

    # 36. Rapid double-tap submissions cause duplicate checkout charges
    challenges.append({
        'id': 36,
        'title': 'Rapid Double-Tap Submissions Cause Duplicate Checkout Charges',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Customer support reported numerous complaints from mobile shoppers who were charged twice when double-tapping the checkout button on slow cellular connections."

### Bug Report
The payment gateway execution function executes transactions before acquiring an in-flight processing lock, allowing rapid successive clicks to trigger concurrent charge executions.

### Steps to Reproduce
1. Call `process_payment("ORD2", paid, locks, mock_charge)` where `locks` already contains `"ORD2"`.
2. Inspect the returned status dictionary.
3. Observe whether the second request is rejected or charged concurrently.

### Expected Behaviour
If `order_id` is currently in `processing_locks`, return `{"status": "LOCKED"}` immediately without executing `charge_fn`.

### Actual Behaviour
Charges are triggered before acquiring a processing lock, allowing simultaneous double-tap requests to charge the customer multiple times.

### Starter Files
`payment_gateway.py` - Manages payment execution and double-submission locking.

### Task
Acquire `processing_locks` prior to invoking `charge_fn`, releasing the lock after execution completes.

### Acceptance Criteria
1. `process_payment("ORD2", paid, {"ORD2"}, mock_charge)["status"]` returns `'LOCKED'`.
2. `process_payment("ORD1", set(), set(), mock_charge)["status"]` returns `'SUCCESS'`.

### Constraints
- `order_id` is a non-empty string.
- `paid_orders` and `processing_locks` are Python sets.
- Locks must be acquired before charging and released after completion (or on error).
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
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
            {'id': 1, 'name': 'Active lock prevents concurrent processing', 'input': '''paid = set(); locks = {"ORD2"}
charges = []
def mock_charge(oid): charges.append(oid); return "ch_1"
process_payment("ORD2", paid, locks, mock_charge)["status"]''', 'expected': 'LOCKED', 'hidden': False},
            {'id': 2, 'name': 'Acquires lock and executes successful charge', 'input': '''paid = set(); locks = set()
charges = []
def mock_charge(oid): charges.append(oid); return "ch_1"
process_payment("ORD1", paid, locks, mock_charge)["status"]''', 'expected': 'SUCCESS', 'hidden': False}
        ],
        'bug_signature': '# Charge happens before locking',
        'suspected_component': 'payment_gateway.py',
        'ai_suggestions': [
            'In multi-threaded checkout systems, check-then-act sequences must be protected by atomic locks to prevent race conditions.',
            'Inspect when `processing_locks` is checked and acquired relative to `charge_fn` in `payment_gateway.py`.',
            'Check both `paid_orders` and `processing_locks` upfront; acquire the lock before calling `charge_fn`, and release it once complete.'
        ],
        'topics': ['Concurrency', 'Distributed Locks', 'Fintech', 'Race Conditions'],
        'skills_tested': ['Python', 'Concurrency', 'Security'],
        'prerequisites': ['Atomic Operations', 'Race Conditions'],
        'status': 'published'
    })

    # 37. Long video transcoding jobs reassigned mid-execution
    challenges.append({
        'id': 37,
        'title': 'Long Video Transcoding Jobs Reassigned Mid-Execution',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Backend',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Rendering worker clusters produced duplicate and corrupted MP4 assets because long video transcoding jobs were being reassigned to secondary workers while the primary worker was still actively encoding."

### Bug Report
The job heartbeat renewal routine does not extend lease expiration timestamps, causing the scheduler to treat active, long-running transcoding jobs as abandoned.

### Steps to Reproduce
1. Assign a job with lease expiration `t=100`.
2. Call `renew_lease(leases, "J1", 90, extension=30)` while worker is active at `t=90`.
3. Check `should_reassign_job(105, "J1", leases)`.
4. Observe that the job is marked for reassignment because the lease expiration was never extended.

### Expected Behaviour
Calling `renew_lease` must extend `leases[job_id]["expires_at"]` to `current_time + extension`.

### Actual Behaviour
`renew_lease` is unimplemented, allowing active leases to expire and trigger duplicate task executions.

### Starter Files
`job_scheduler.py` - Evaluates job lease expirations and heartbeat renewals.

### Task
Implement lease extension logic in `renew_lease` in `job_scheduler.py`.

### Acceptance Criteria
1. `renew_lease(leases, "J1", 90, extension=30)` sets expiration to `120`.
2. `should_reassign_job(105, "J1", leases)` returns `False`.
3. `should_reassign_job(130, "J1", leases)` returns `True`.

### Constraints
- `leases` is a dictionary mapping job IDs to lease dictionaries.
- `current_time` and `extension` are non-negative numeric timestamps.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
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
            {'id': 1, 'name': 'Heartbeat extends lease expiration timestamp', 'input': '''leases = {"J1": {"expires_at": 100}}
renew_lease(leases, "J1", 90, extension=30)
leases["J1"]["expires_at"]''', 'expected': '120', 'hidden': False},
            {'id': 2, 'name': 'Active valid lease prevents job reassignment', 'input': '''leases = {"J1": {"expires_at": 120}}
should_reassign_job(105, "J1", leases)''', 'expected': 'False', 'hidden': False},
            {'id': 3, 'name': 'Expired lease triggers job reassignment', 'input': '''leases = {"J1": {"expires_at": 120}}
should_reassign_job(130, "J1", leases)''', 'expected': 'True', 'hidden': True}
        ],
        'bug_signature': '# Missing heartbeat renewal implementation\n    pass',
        'suspected_component': 'job_scheduler.py',
        'ai_suggestions': [
            'Distributed leasing algorithms require periodic heartbeats from healthy workers to prove liveness for long-running tasks.',
            'Look at the empty `pass` statement in `renew_lease` in `job_scheduler.py`.',
            'Update the lease dictionary for `job_id` so that `expires_at` is recalculated as `current_time + extension`.'
        ],
        'topics': ['Distributed Systems', 'Leases', 'Heartbeats'],
        'skills_tested': ['Python', 'Backend', 'Architecture'],
        'prerequisites': ['Distributed Leases'],
        'status': 'published'
    })

    # 38. Airline seat allocation confirms tickets beyond flight capacity
    challenges.append({
        'id': 38,
        'title': 'Airline Seat Allocation Confirms Tickets Beyond Flight Capacity',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Airport gate staff faced boarding emergencies when an airline flash sale confirmed 112 seat reservations on a regional flight configured with only 100 seats."

### Bug Report
The flight seat reservation routine decrements available seat inventory without verifying sufficient remaining capacity, resulting in oversold flights.

### Steps to Reproduce
1. Initialize flight inventory with 1 remaining seat.
2. Call `reserve_seats(inv, "FL100", 1)`.
3. Call `reserve_seats(inv, "FL100", 1)` a second time.
4. Inspect the returned boolean and inventory level.
5. Observe that the second booking is accepted and inventory becomes negative.

### Expected Behaviour
If `requested_seats > inventory[flight_id]`, reject the reservation by returning `False` without decrementing inventory.

### Actual Behaviour
The function deducts requested seats unconditionally, confirming bookings beyond capacity.

### Starter Files
`inventory_allocator.py` - Allocates available seats on commercial flights.

### Task
Add capacity checks to `reserve_seats` in `inventory_allocator.py` to prevent overselling.

### Acceptance Criteria
1. Requests within available seat count return `True` and decrement inventory.
2. Requests exceeding remaining seats return `False` and leave inventory intact.

### Constraints
- `inventory` is a dictionary mapping flight IDs to integer counts.
- `requested_seats` is a positive integer.
- Inventory must never drop below `0`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'inventory_allocator.py',
            'content': '''def reserve_seats(inventory, flight_id, requested_seats):
    current_seats = inventory.get(flight_id, 0)
    inventory[flight_id] = current_seats - requested_seats
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Valid seat reservation returns True', 'input': '''inv = {"FL100": 1}
reserve_seats(inv, "FL100", 1)''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Overbooking attempt returns False', 'input': '''inv = {"FL100": 0}
reserve_seats(inv, "FL100", 1)''', 'expected': 'False', 'hidden': False},
            {'id': 3, 'name': 'Exhausted flight stock decrements to exactly zero', 'input': '''inv = {"FL100": 1}
reserve_seats(inv, "FL100", 1)
reserve_seats(inv, "FL100", 1)
inv["FL100"]''', 'expected': '0', 'hidden': True}
        ],
        'bug_signature': 'current_seats = inventory.get(flight_id, 0)\n    inventory[flight_id] = current_seats - requested_seats',
        'suspected_component': 'inventory_allocator.py',
        'ai_suggestions': [
            'Concurrency bugs in reservation engines arise when reading state and writing state are separated in time.',
            'Examine `reserve_seats` in `inventory_allocator.py` to ensure the balance check is validated before mutation.',
            'Ensure the stock check `inventory.get(flight_id, 0) >= requested_seats` evaluates the live state immediately prior to deduction.'
        ],
        'topics': ['Concurrency', 'Inventory', 'Race Conditions'],
        'skills_tested': ['Python', 'Concurrency'],
        'prerequisites': ['Compare-and-Swap'],
        'status': 'published'
    })

    # 39. Cache-aside strategy restores stale bio after database update
    challenges.append({
        'id': 39,
        'title': 'Cache-Aside Strategy Restores Stale Bio After Database Update',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Caching',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Users editing their public profile bio noticed that after refreshing their browser, their old bio text reappeared and stayed cached for hours."

### Bug Report
The cache-aside update function invalidates the cache key before writing changes to the database, allowing concurrent reads to repopulate the cache with stale database state.

### Steps to Reproduce
1. Call `update_user_bio(db, cache, "u1", "New Bio")`.
2. Inspect the sequence of cache deletion and database write operations.
3. Observe that cache invalidation occurs prior to database persistence.

### Expected Behaviour
Write the updated value to the database first, then invalidate the cache key.

### Actual Behaviour
The cache is evicted before persisting changes, leaving a race window for stale repopulation.

### Starter Files
`cache_aside.py` - Updates user profile bios with cache invalidation.

### Task
Reorder operations in `update_user_bio` in `cache_aside.py` to ensure database persistence precedes cache invalidation.

### Acceptance Criteria
1. `update_user_bio` records `DB_WRITE` before `CACHE_DELETE`.
2. The updated bio is properly saved in the database.

### Constraints
- `user_id` and `new_bio` are strings.
- Operations must execute in strict sequence: database write then cache delete.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'cache_aside.py',
            'content': '''def update_user_bio(db, cache, user_id, new_bio):
    cache.delete(f"user:{user_id}")
    db[user_id] = new_bio
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'DB write precedes cache deletion', 'input': '''ops = []
class MockDB:
    def __setitem__(self, k, v): ops.append("DB_WRITE")
class MockCache:
    def delete(self, k): ops.append("CACHE_DELETE")
update_user_bio(MockDB(), MockCache(), "u1", "New Bio")
ops''', 'expected': "['DB_WRITE', 'CACHE_DELETE']", 'hidden': False},
            {'id': 2, 'name': 'User bio updated in database', 'input': '''db = {}; cache = type('Mock', (), {'delete': lambda self, k: None})()
update_user_bio(db, cache, "u2", "Updated")
db.get("u2")''', 'expected': 'Updated', 'hidden': False}
        ],
        'bug_signature': 'cache.delete(f"user:{user_id}")\n    db[user_id] = new_bio',
        'suspected_component': 'cache_aside.py',
        'ai_suggestions': [
            'In cache-aside architecture, deleting cache before database updates creates a window for readers to cache stale database rows.',
            'Inspect the execution order in `update_user_bio` in `cache_aside.py`.',
            'Swap the statements: write to `db[user_id] = new_bio` first, and call `cache.delete(...)` immediately following the write.'
        ],
        'topics': ['Cache-Aside', 'Concurrency', 'Data Consistency'],
        'skills_tested': ['Python', 'Caching'],
        'prerequisites': ['Cache-Aside Architecture'],
        'status': 'published'
    })

    # 40. Delayed worker task releases unrelated lock held by new owner
    challenges.append({
        'id': 40,
        'title': 'Delayed Worker Task Releases Unrelated Lock Held by New Owner',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A financial end-of-day reconciliation report was corrupted because a stalled worker task woke up after its lease expired and deleted the active lock owned by another worker."

### Bug Report
The distributed lock release helper purges lock keys unconditionally without verifying ownership tokens, releasing locks held by subsequent acquiring workers.

### Steps to Reproduce
1. Assign a lock key to `'owner_B'` in `lock_storage`.
2. Worker `'owner_A'` calls `release_lock(lock_storage, "report_lock", "owner_A")`.
3. Inspect `lock_storage`.
4. Observe that `'owner_B'`'s valid lock was deleted by `'owner_A'`.

### Expected Behaviour
A lock must only be deleted if `lock_storage[lock_key] == owner_token`, returning `True`; otherwise return `False` and preserve the lock.

### Actual Behaviour
The function deletes the lock key unconditionally without verifying ownership token match.

### Starter Files
`distributed_lock.py` - Manages distributed mutual exclusion locks with ownership tokens.

### Task
Add ownership token verification in `release_lock` in `distributed_lock.py`.

### Acceptance Criteria
1. Releasing a lock with a mismatched token returns `False` and does not delete the key.
2. Releasing a lock with the matching token deletes the key and returns `True`.

### Constraints
- `lock_storage` is a dictionary mapping lock keys to owner token strings.
- Token comparison must be exact string equality.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'distributed_lock.py',
            'content': '''def release_lock(lock_storage, lock_key, owner_token):
    if lock_key in lock_storage:
        del lock_storage[lock_key]
        return True
    return False'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Wrong owner token cannot release lock', 'input': '''release_lock({"report_lock": "owner_B"}, "report_lock", "owner_A")''', 'expected': 'False', 'hidden': False},
            {'id': 2, 'name': 'Valid owner releases held lock', 'input': '''release_lock({"report_lock": "owner_A"}, "report_lock", "owner_A")''', 'expected': 'True', 'hidden': False},
            {'id': 3, 'name': 'Unauthorized attempt preserves existing lock', 'input': '''locks = {"report_lock": "owner_B"}
release_lock(locks, "report_lock", "owner_A")
list(locks.keys())''', 'expected': "['report_lock']", 'hidden': True}
        ],
        'bug_signature': 'if lock_key in lock_storage:\n        del lock_storage[lock_key]',
        'suspected_component': 'distributed_lock.py',
        'ai_suggestions': [
            'Distributed locks require fencing tokens: a client must prove it is the current legitimate owner before releasing a lock.',
            'Check what condition is evaluated before `del lock_storage[lock_key]` in `distributed_lock.py`.',
            'Verify that `lock_storage.get(lock_key) == owner_token` before deleting the key and returning `True`.'
        ],
        'topics': ['Distributed Locks', 'Redis', 'Concurrency'],
        'skills_tested': ['Python', 'Concurrency', 'Security'],
        'prerequisites': ['Distributed Lock Semantics'],
        'status': 'published'
    })

    # 41. Synchronized retries trigger thundering herd request storm
    challenges.append({
        'id': 41,
        'title': 'Synchronized Retries Trigger Thundering Herd Request Storm',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'API & Web',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Our payment gateway crashed during an outage recovery because thousands of failed client requests retried in synchronized linear intervals, overwhelming server capacity."

### Bug Report
The retry delay calculator scales linearly with attempt count rather than using exponential growth, producing clustered retry bursts that overwhelm recovering services.

### Steps to Reproduce
1. Call `calculate_backoff(3, base_delay=2, max_delay=60, jitter=0)`.
2. Inspect the computed backoff duration.
3. Observe that delays grow linearly instead of exponentially.

### Expected Behaviour
Retry delay must scale exponentially according to `min(max_delay, base_delay * (2 ** attempt) + jitter)`.

### Actual Behaviour
Linear scaling produces insufficient spacing between successive retries.

### Starter Files
`backoff_client.py` - Computes retry backoff durations for distributed clients.

### Task
Implement exponential backoff in `calculate_backoff` in `backoff_client.py`.

### Acceptance Criteria
1. `calculate_backoff(3, base_delay=2, max_delay=60, jitter=0)` returns `16`.
2. `calculate_backoff(10, base_delay=2, max_delay=30, jitter=0)` caps at `30`.

### Constraints
- `attempt` is a positive integer.
- `base_delay` and `max_delay` are positive numeric values.
- Delay is capped at `max_delay`.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'backoff_client.py',
            'content': '''def calculate_backoff(attempt, base_delay=1, max_delay=32, jitter=0):
    return min(max_delay, base_delay * attempt + jitter)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Exponential growth at attempt 3', 'input': 'calculate_backoff(3, base_delay=2, max_delay=60, jitter=0)', 'expected': '16', 'hidden': False},
            {'id': 2, 'name': 'Capped at max_delay', 'input': 'calculate_backoff(10, base_delay=2, max_delay=30, jitter=0)', 'expected': '30', 'hidden': False}
        ],
        'bug_signature': 'return min(max_delay, base_delay * attempt + jitter)',
        'suspected_component': 'backoff_client.py',
        'ai_suggestions': [
            'Resilient distributed systems use exponential backoff rather than linear backoff to prevent thundering herd spikes.',
            'Examine the multiplier applied to `base_delay` in `calculate_backoff` in `backoff_client.py`.',
            'Replace the linear multiplication with power of two exponentiation: `base_delay * (2 ** attempt)`.'
        ],
        'topics': ['Resilience', 'Exponential Backoff', 'Jitter', 'Thundering Herd'],
        'skills_tested': ['Python', 'Backend', 'APIs'],
        'prerequisites': ['Exponential Backoff'],
        'status': 'published'
    })

    # 42. Simultaneous report generations produce interleaved CSV output
    challenges.append({
        'id': 42,
        'title': 'Simultaneous Report Generations Produce Interleaved CSV Output',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Finance auditors discovered monthly earnings spreadsheets with mangled and interleaved data rows whenever two automated export jobs ran concurrently."

### Bug Report
The report exporter writes directly to target files without atomic staging, causing concurrent file writers to overwrite and corrupt each other's output.

### Steps to Reproduce
1. Call `write_report_safely(fs, "report.csv", "DATA", 123)`.
2. Inspect the filesystem operations.
3. Observe whether content was staged through a process-specific temporary file before final commit.

### Expected Behaviour
Write content to temporary file `f"{dest_path}.tmp.{pid}"` first, then atomically move/commit it to `dest_path`.

### Actual Behaviour
Direct writes to destination paths risk race conditions and partial file corruption during concurrent operations.

### Starter Files
`report_writer.py` - Safely stages and writes business reports to storage.

### Task
Implement atomic file staging in `write_report_safely` in `report_writer.py`.

### Acceptance Criteria
1. Generates temporary file `f"{dest_path}.tmp.{pid}"` during the write process.
2. Successfully populates destination path with final content.

### Constraints
- `dest_path` is a file path string.
- `pid` is a process identifier.
- Staging file must include `.tmp.<pid>` pattern.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'report_writer.py',
            'content': '''def write_report_safely(file_system, dest_path, content, pid):
    file_system[dest_path] = content
    return dest_path'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Atomic staging file created during report write', 'input': '''class MockFS(dict):
    def __init__(self):
        super().__init__()
        self.temp_used = False
    def __setitem__(self, k, v):
        if ".tmp." in str(k):
            self.temp_used = True
        super().__setitem__(k, v)

fs = MockFS()
write_report_safely(fs, "report.csv", "DATA", 123)
fs.temp_used''', 'expected': 'True', 'hidden': False},
            {'id': 2, 'name': 'Final destination file contains report content', 'input': '''class MockFS(dict): pass
fs = MockFS()
write_report_safely(fs, "report.csv", "DATA_ROW", 456)
fs.get("report.csv")''', 'expected': 'DATA_ROW', 'hidden': False}
        ],
        'bug_signature': 'file_system[dest_path] = content\n    return dest_path',
        'suspected_component': 'report_writer.py',
        'ai_suggestions': [
            'Atomic file replacement prevents partial writes and corruption by writing to a hidden temporary file before renaming.',
            'Look at how `dest_path` is written directly into `file_system` in `report_writer.py`.',
            'Write first to `f"{dest_path}.tmp.{pid}"`, then assign `file_system[dest_path] = file_system.pop(temp_path)`.'
        ],
        'topics': ['File I/O', 'Atomicity', 'Concurrency'],
        'skills_tested': ['Python', 'Backend'],
        'prerequisites': ['Atomic File Writes'],
        'status': 'published'
    })

    # 43. Concurrent resource allocation leads to worker thread deadlock
    challenges.append({
        'id': 43,
        'title': 'Concurrent Resource Allocation Leads to Worker Thread Deadlock',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Worker background threads periodically froze and stopped processing jobs when concurrent tasks attempted to acquire GPU and NVMe storage locks in opposite orders."

### Bug Report
The resource allocation coordinator assigns lock acquisition orders based on arbitrary input sequences rather than a global deterministic order, causing circular wait deadlocks.

### Steps to Reproduce
1. Call `determine_lock_order(["NVMe", "GPU", "CPU"])`.
2. Inspect the returned acquisition sequence.
3. Observe that locks are returned in non-standardized arbitrary sequence.

### Expected Behaviour
Return all resource identifiers in lexicographically sorted order to establish a universal lock acquisition hierarchy.

### Actual Behaviour
The function returns the input collection unmodified, allowing competing processes to request resources in conflicting orders.

### Starter Files
`resource_manager.py` - Establishes lock acquisition order to prevent worker deadlocks.

### Task
Sort resource lock requests deterministically in `determine_lock_order` in `resource_manager.py`.

### Acceptance Criteria
1. `determine_lock_order(["NVMe", "GPU", "CPU"])` returns `['CPU', 'GPU', 'NVMe']`.
2. `determine_lock_order(["CPU", "NVMe", "GPU"])` returns `['CPU', 'GPU', 'NVMe']`.

### Constraints
- `resources` is a list of resource name strings.
- Returned list must be deterministically sorted.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'resource_manager.py',
            'content': '''def determine_lock_order(required_resources):
    return list(required_resources)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Sorts resources deterministically into alphabetical order', 'input': '''determine_lock_order(["NVMe", "GPU", "CPU"])''', 'expected': "['CPU', 'GPU', 'NVMe']", 'hidden': False},
            {'id': 2, 'name': 'Maintains consistent hierarchy regardless of input order', 'input': '''determine_lock_order(["CPU", "NVMe", "GPU"])''', 'expected': "['CPU', 'GPU', 'NVMe']", 'hidden': False},
            {'id': 3, 'name': 'Arbitrary key sets ordered deterministically', 'input': '''determine_lock_order(["Z", "A", "M"])''', 'expected': "['A', 'M', 'Z']", 'hidden': True}
        ],
        'bug_signature': 'return list(required_resources)',
        'suspected_component': 'resource_manager.py',
        'ai_suggestions': [
            'Coffman\'s condition for deadlock (circular wait) can be eliminated by enforcing a total ordering on all shared locks.',
            'Inspect what `determine_lock_order` returns in `resource_manager.py`.',
            'Sort the collection before returning: `return sorted(required_resources)`.'
        ],
        'topics': ['Deadlocks', 'Concurrency', 'Lock Ordering'],
        'skills_tested': ['Python', 'Concurrency'],
        'prerequisites': ['Deadlock Prevention'],
        'status': 'published'
    })

    # 44. Security guard runs after modifying user role assignment
    challenges.append({
        'id': 44,
        'title': 'Security Guard Runs After Modifying User Role Assignment',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Security',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A security audit revealed that an unauthorized guest account was granted administrator privileges because the role update was committed before the authorization check was executed."

### Bug Report
The privilege elevation handler updates the user's role in the database before invoking the authorization guard, leaving unauthorized privilege elevations intact if the guard fails.

### Steps to Reproduce
1. Initialize `users = {"guest_user": "guest"}`.
2. Call `elevate_user_role(users, "unauthorized_user", "guest_user", "admin", lambda a: False)`.
3. Inspect `users["guest_user"]`.
4. Observe that role elevation was committed before authorization was verified.

### Expected Behaviour
Validate `auth_guard(admin_user)` before making any modifications; raise `PermissionError` if unauthorized without mutating user roles.

### Actual Behaviour
Role assignment occurs prior to security validation, violating the principle of secure authorization.

### Starter Files
`access_controller.py` - Validates caller permissions before elevating user roles.

### Task
Reorder operations in `elevate_user_role` in `access_controller.py` so authorization verification precedes role modification.

### Acceptance Criteria
1. Unauthorized callers raise `PermissionError` and leave target user roles unchanged.
2. Authorized callers update target user role to `new_role`.

### Constraints
- `users` is a dictionary mapping usernames to role strings.
- `auth_guard` is a callable returning a boolean.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'access_controller.py',
            'content': '''def elevate_user_role(user_db, actor, target, new_role, auth_checker):
    user_db[target] = new_role
    if not auth_checker(actor):
        raise PermissionError("Actor not authorized to grant roles")
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Unauthorized role elevation leaves target role unchanged', 'input': '''users = {"guest_user": "guest"}
try:
    elevate_user_role(users, "guest_user", "guest_user", "admin", lambda a: False)
except PermissionError:
    pass
users["guest_user"]''', 'expected': 'guest', 'hidden': False},
            {'id': 2, 'name': 'Authorized actor updates target role to admin', 'input': '''users = {"target_user": "member"}
elevate_user_role(users, "admin_user", "target_user", "admin", lambda a: True)
users["target_user"]''', 'expected': 'admin', 'hidden': False}
        ],
        'bug_signature': 'user_db[target] = new_role\n    if not auth_checker(actor):',
        'suspected_component': 'access_controller.py',
        'ai_suggestions': [
            'Security gates must always validate permissions before executing privileged state mutations.',
            'Look at the order of operations in `elevate_user_role` in `access_controller.py`.',
            'Invoke `if not auth_checker(actor): raise PermissionError(...)` before executing `user_db[target] = new_role`.'
        ],
        'topics': ['Security', 'Authorization', 'Defensive Programming'],
        'skills_tested': ['Python', 'Security', 'Backend'],
        'prerequisites': ['Security Fundamentals'],
        'status': 'published'
    })

    # 45. Interrupted database migration leaves no resumption checkpoint
    challenges.append({
        'id': 45,
        'title': 'Interrupted Database Migration Leaves No Resumption Checkpoint',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Data & Processing',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A nightly migration of 10 million legacy customer records crashed at record 4,200,000, but had to be restarted from record 0 because no checkpoint was recorded."

### Bug Report
The batch migration worker migrates records to the destination store but fails to persist the last successfully processed record ID in the checkpoint store.

### Steps to Reproduce
1. Call `migrate_batch(db, cp, [{"id": 10}, {"id": 20}, {"id": 30}])`.
2. Inspect `cp.get("last_id")`.
3. Observe that no progress checkpoint was recorded.

### Expected Behaviour
Update `checkpoint_store["last_id"]` with the ID of the final successfully migrated record in the batch.

### Actual Behaviour
Records are inserted into the destination database without recording progress in the checkpoint store.

### Starter Files
`migration_runner.py` - Migrates batches of records with resumption checkpoint tracking.

### Task
Record the final batch record ID in `checkpoint_store` in `migration_runner.py`.

### Acceptance Criteria
1. `migrate_batch(db, cp, [{"id": 10}, {"id": 20}, {"id": 30}])` sets `cp["last_id"] = 30`.
2. `migrate_batch(db, cp, [{"id": 5}])` sets `cp["last_id"] = 5`.

### Constraints
- `batch` is a list of dictionaries with integer `'id'` fields.
- `checkpoint_store` is a dictionary tracking migration progress.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'migration_runner.py',
            'content': '''def migrate_batch(destination_db, checkpoint_store, batch):
    for record in batch:
        destination_db[record["id"]] = record
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Checkpoint updated with last migrated record ID', 'input': '''db = {}; cp = {}
migrate_batch(db, cp, [{"id": 10}, {"id": 20}, {"id": 30}])
cp.get("last_id")''', 'expected': '30', 'hidden': False},
            {'id': 2, 'name': 'Single record migration sets checkpoint', 'input': '''db = {}; cp = {}
migrate_batch(db, cp, [{"id": 5}])
cp.get("last_id")''', 'expected': '5', 'hidden': False}
        ],
        'bug_signature': 'for record in batch:\n        destination_db[record["id"]] = record\n    return True',
        'suspected_component': 'migration_runner.py',
        'ai_suggestions': [
            'Large-scale data pipelines require persistent checkpoints to enable crash recovery without duplicating work.',
            'Examine what `migrate_batch` writes to `checkpoint_store` in `migration_runner.py`.',
            'After writing records, update `checkpoint_store["last_id"] = batch[-1]["id"]` if the batch contains records.'
        ],
        'topics': ['Migrations', 'Checkpoints', 'Fault Tolerance'],
        'skills_tested': ['Python', 'Backend', 'Data Processing'],
        'prerequisites': ['Checkpoints in Data Processing'],
        'status': 'published'
    })

    # 46. Entity event stream reorders sequential account actions
    challenges.append({
        'id': 46,
        'title': 'Entity Event Stream Reorders Sequential Account Actions',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A banking ledger showed an account withdrawal processed before the initial deposit event because events for the same account were routed to different worker shards."

### Bug Report
The event stream partitioner uses random shard assignment rather than consistent entity hashing, causing sequential events for the same entity to process out of order.

### Steps to Reproduce
1. Submit two sequential events for entity `"ORD_99"` (`CREATE` and `CANCEL`).
2. Compute shard assignments via `assign_event_shard(event, 4)`.
3. Observe that events for the same entity are distributed to different partition shards.

### Expected Behaviour
All events sharing the same `entity_id` must deterministically map to the same shard: `hash(entity_id) % num_shards`.

### Actual Behaviour
Random shard allocation distributes related entity events arbitrarily across shards.

### Starter Files
`event_stream.py` - Partitions event streams across worker shards.

### Task
Implement consistent entity hashing in `assign_event_shard` in `event_stream.py`.

### Acceptance Criteria
1. Events with identical `entity_id` map to identical shard indices.
2. Shard indices fall within `0 <= shard < num_shards`.

### Constraints
- `event` contains a string `'entity_id'`.
- `num_shards` is a positive integer.
- Partitioning must be deterministic across calls.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'event_stream.py',
            'content': '''def assign_event_shard(event, num_shards):
    import random
    return random.randint(0, num_shards - 1)'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Sequential events for identical entity route to same shard', 'input': '''e1 = {"entity_id": "ORD_99", "type": "CREATE"}
e2 = {"entity_id": "ORD_99", "type": "CANCEL"}
assign_event_shard(e1, 4) - assign_event_shard(e2, 4)''', 'expected': '0', 'hidden': False},
            {'id': 2, 'name': 'Assigned shard is within valid shard bounds', 'input': '''0 <= assign_event_shard({"entity_id": "ORD_1"}, 4) < 4''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'return random.randint(0, num_shards - 1)',
        'suspected_component': 'event_stream.py',
        'ai_suggestions': [
            'Event streaming platforms preserve per-entity order by routing messages with matching partition keys to the same partition.',
            'Notice that `assign_event_shard` uses `random.randint` in `event_stream.py`.',
            'Use hash partitioning: derive the shard by computing `abs(hash(event["entity_id"])) % num_shards`.'
        ],
        'topics': ['Event Sourcing', 'Partitioning', 'Concurrency'],
        'skills_tested': ['Python', 'Concurrency', 'Architecture'],
        'prerequisites': ['Consistent Partitioning'],
        'status': 'published'
    })

    # 47. Travel booking saga leaves orphaned flight after rental failure
    challenges.append({
        'id': 47,
        'title': 'Travel Booking Saga Leaves Orphaned Flight After Rental Failure',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A travel booking package failed when the rental car step threw an error, but while the hotel was canceled, the customer was still charged for the non-refundable flight."

### Bug Report
The distributed saga coordinator rolls back only the single most recently completed step upon failure rather than compensating all previously completed steps in reverse order.

### Steps to Reproduce
1. Execute a saga with three steps: Flight, Hotel, and Car (where Car fails).
2. Catch the resulting exception.
3. Inspect the list of compensated steps.
4. Observe that only Hotel was rolled back, leaving Flight orphaned.

### Expected Behaviour
When a step in the saga fails, roll back all previously completed steps in reverse order of execution: `['Hotel', 'Flight']`.

### Actual Behaviour
The coordinator only invokes rollback on `completed[-1]`, leaving earlier completed transactions uncompensated.

### Starter Files
`saga_coordinator.py` - Executes distributed multi-step transaction sagas with rollback compensation.

### Task
Update error handling in `execute_saga` in `saga_coordinator.py` to reverse-iterate through all completed steps and execute compensation.

### Acceptance Criteria
1. Failure in step 3 compensates step 2 and step 1 in reverse order: `['Hotel', 'Flight']`.
2. Successful sagas return `True`.

### Constraints
- `steps` is a list of objects implementing `execute()` and `rollback()`.
- Rollbacks must execute in reverse order of completion.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
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
            {'id': 1, 'name': 'All completed saga steps rolled back in reverse order', 'input': '''rolled_back = []
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
rolled_back''', 'expected': "['Hotel', 'Flight']", 'hidden': False},
            {'id': 2, 'name': 'Successful saga completes cleanly', 'input': '''class MockStep:
    def __init__(self, name): self.name = name
    def execute(self): pass
    def rollback(self): pass
execute_saga([MockStep("Flight"), MockStep("Hotel")])''', 'expected': 'True', 'hidden': False}
        ],
        'bug_signature': 'if completed:\n                completed[-1].rollback()',
        'suspected_component': 'saga_coordinator.py',
        'ai_suggestions': [
            'The Saga pattern ensures eventual consistency by executing compensating transactions for every step completed prior to failure.',
            'Inspect what happens inside the `except Exception:` block in `saga_coordinator.py`.',
            'Iterate through all completed steps in reverse: `for s in reversed(completed): s.rollback()` before re-raising.'
        ],
        'topics': ['Saga Pattern', 'Distributed Transactions', 'Compensating Actions'],
        'skills_tested': ['Python', 'Architecture', 'Transactions'],
        'prerequisites': ['Saga Orchestration'],
        'status': 'published'
    })

    # 48. Multi-gigabyte stream parsing causes out-of-memory container crash
    challenges.append({
        'id': 48,
        'title': 'Multi-Gigabyte Stream Parsing Causes Out-of-Memory Container Crash',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Performance',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Log ingestion worker containers in Kubernetes were repeatedly terminated by the OOM killer when parsing multi-gigabyte server access log streams."

### Bug Report
The stream chunk parser accumulates all incoming data chunks in memory before parsing, causing unbounded memory growth proportional to stream size.

### Steps to Reproduce
1. Pass streaming chunks `["line1
li", "ne2
", "line3
"]` into `parse_stream_chunks`.
2. Inspect memory retention behavior.
3. Observe that all historical chunks are kept in memory instead of being yielded incrementally.

### Expected Behaviour
Use a sliding text buffer to yield complete lines as newlines are encountered, discarding emitted content to maintain memory efficiency.

### Actual Behaviour
The parser buffers the entire input stream in an expanding list, consuming gigabytes of memory.

### Starter Files
`stream_parser.py` - Parses streaming text chunks into lines with low memory footprint.

### Task
Refactor `parse_stream_chunks` in `stream_parser.py` into a memory-efficient generator that yields lines from a streaming buffer.

### Acceptance Criteria
1. `list(parse_stream_chunks(["line1
li", "ne2
", "line3
"]))` yields `['line1', 'line2', 'line3']`.
2. Complete lines are yielded progressively without retaining full historical chunks in memory.

### Constraints
- `chunks` is an iterable of string data.
- Generator yields individual stripped or newline-delimited lines.
- Retains only unparsed leftover text between chunks.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
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
            {'id': 1, 'name': 'Generator yields individual newline-delimited stream chunks', 'input': '''list(parse_stream_chunks(["line1" + chr(10) + "li", "ne2" + chr(10), "line3" + chr(10)]))''', 'expected': "['line1', 'line2', 'line3']", 'hidden': False},
            {'id': 2, 'name': 'Parses multiple complete lines', 'input': '''list(parse_stream_chunks(["hello" + chr(10) + "world" + chr(10)]))''', 'expected': "['hello', 'world']", 'hidden': False}
        ],
        'bug_signature': 'all_chunks = []\n    lines = []\n    for chunk in chunks:\n        all_chunks.append(chunk)',
        'suspected_component': 'stream_parser.py',
        'ai_suggestions': [
            'Streaming parsers should consume constant memory by yielding tokens as soon as delimiters are encountered.',
            'Avoid keeping an accumulating list of all previous chunks in `stream_parser.py`.',
            'Maintain a single `buffer` string; find `\\n`, yield lines, and slice `buffer = buffer[idx+1:]`.'
        ],
        'topics': ['Memory Management', 'Streaming', 'Generators'],
        'skills_tested': ['Python', 'Performance'],
        'prerequisites': ['Generators and Streams'],
        'status': 'published'
    })

    # 49. Account profile update leaves partially modified state on validation failure
    challenges.append({
        'id': 49,
        'title': 'Account Profile Update Leaves Partially Modified State on Validation Failure',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Customer service reported corrupt user records where accounts showed updated email addresses but old phone numbers after form submissions failed phone number validation."

### Bug Report
The account update routine applies email changes directly to the profile object before validating the phone number, leaving the profile in a corrupted partial state upon validation errors.

### Steps to Reproduce
1. Initialize profile `{"email": "old@test.com", "phone": "1111111111"}`.
2. Call `update_account(prof, "new@test.com", "bad_phone")`.
3. Catch the expected ValueError.
4. Inspect `prof["email"]`.
5. Observe that the email was updated despite phone validation failure.

### Expected Behaviour
Validate both email and phone number before mutating any fields; if validation fails, leave the original profile unchanged.

### Actual Behaviour
Premature mutation updates email before verifying phone validity.

### Starter Files
`account_service.py` - Validates and applies atomic profile updates.

### Task
Enforce atomic validation in `update_account` in `account_service.py` to validate all inputs before modifying state.

### Acceptance Criteria
1. Invalid phone numbers raise `ValueError` and leave original email intact.
2. Valid inputs update both email and phone successfully.

### Constraints
- `profile` is a dictionary containing `'email'` and `'phone'`.
- Phone numbers must be exactly 10 digits.
- Updates must be atomic (all fields update or none).
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
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
            {'id': 1, 'name': 'Invalid phone input aborts update leaving email unchanged', 'input': '''prof = {"email": "old@test.com", "phone": "1111111111"}
try:
    update_account(prof, "new@test.com", "bad_phone")
except ValueError:
    pass
prof["email"]''', 'expected': 'old@test.com', 'hidden': False},
            {'id': 2, 'name': 'Valid updates apply new email and phone', 'input': '''prof = {"email": "old@test.com", "phone": "1111111111"}
update_account(prof, "new@test.com", "9998887777")
prof["email"]''', 'expected': 'new@test.com', 'hidden': False}
        ],
        'bug_signature': 'if "@" in new_email:\n        profile["email"] = new_email\n    if not (new_phone',
        'suspected_component': 'account_service.py',
        'ai_suggestions': [
            'State updates should be atomic: perform all validation checks upfront before making any modifications.',
            'Notice that `profile["email"]` is updated before checking `new_phone` in `account_service.py`.',
            'Validate both `new_email` and `new_phone` first, and only mutate `profile` once both validations succeed.'
        ],
        'topics': ['Transactions', 'Validation', 'Atomicity'],
        'skills_tested': ['Python', 'Backend', 'Validation'],
        'prerequisites': ['Defensive Programming'],
        'status': 'published'
    })

    # 50. Ticket checkout displaces active unexpired seat reservations
    challenges.append({
        'id': 50,
        'title': 'Ticket Checkout Displaces Active Unexpired Seat Reservations',
        'difficulty': 'Hard',
        'technology': 'Python',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Concert attendees reported that while entering payment information for reserved seats, another buyer completed checkout for the exact same seats, bumping their active hold."

### Bug Report
The seat reservation routine overwrites existing holds unconditionally without checking expiration timestamps, displacing active unexpired reservations.

### Steps to Reproduce
1. User 1 reserves Seat `"A1"` at `t=100` with `ttl=300` (expires `t=400`).
2. User 2 requests Seat `"A1"` at `t=150`.
3. Inspect the returned status and reservation record.
4. Observe that User 2 displaced User 1's active reservation.

### Expected Behaviour
If an active unexpired reservation exists for the seat, reject the request by returning `False`; allow reservations only for unreserved or expired seats.

### Actual Behaviour
The function assigns the seat unconditionally, displacing active customer holds.

### Starter Files
`seat_reservation.py` - Manages time-limited seat reservations for ticket checkout.

### Task
Check existing reservation expiration before creating holds in `reserve_seat` in `seat_reservation.py`.

### Acceptance Criteria
1. Requests for actively reserved seats return `False`.
2. Requests for expired or unreserved seats return `True` and set reservation state.

### Constraints
- `reservations` is a dictionary mapping seat IDs to reservation details.
- `current_time` and `ttl` are positive numeric timestamps.
- Active reservations (`current_time < expires_at`) must be preserved.
- Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.""",
        'files': [{
            'name': 'seat_reservation.py',
            'content': '''def reserve_seat(reservations, seat_id, user_id, current_time, ttl=300):
    reservations[seat_id] = {"user": user_id, "expires_at": current_time + ttl}
    return True'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Active reservation blocks second reservation attempt', 'input': '''res = {}
reserve_seat(res, "A1", "Alice", 100, ttl=300)
reserve_seat(res, "A1", "Bob", 150, ttl=300)''', 'expected': 'False', 'hidden': False},
            {'id': 2, 'name': 'Expired reservation permits new reservation', 'input': '''res = {"A1": {"user": "Alice", "expires_at": 200}}
reserve_seat(res, "A1", "Bob", 250, ttl=300)''', 'expected': 'True', 'hidden': False},
            {'id': 3, 'name': 'Active reservation preserves original reserved user', 'input': '''res = {}
reserve_seat(res, "A1", "Alice", 100, ttl=300)
reserve_seat(res, "A1", "Bob", 150, ttl=300)
res["A1"]["user"]''', 'expected': 'Alice', 'hidden': True}
        ],
        'bug_signature': 'def reserve_seat(reservations, seat_id, user_id, current_time, ttl=300):\n    reservations[seat_id] =',
        'suspected_component': 'seat_reservation.py',
        'ai_suggestions': [
            'Time-based lease reservations must check whether an existing lease is active before allowing re-allocation.',
            'Look at whether existing reservation state is evaluated in `reserve_seat` in `seat_reservation.py`.',
            'Check `existing = reservations.get(seat_id)`. If `existing and current_time < existing["expires_at"]: return False`.'
        ],
        'topics': ['Concurrency', 'Reservations', 'Timeouts'],
        'skills_tested': ['Python', 'Concurrency', 'Backend'],
        'prerequisites': ['Expiring Leases'],
        'status': 'published'
    })

    return challenges
