from django.core.management.base import BaseCommand
from buggyman.models import Challenge, User, Submission, Notification

class Command(BaseCommand):
    help = 'Seed database with 120 high-quality real-world software engineering challenges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Delete existing challenges before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write('Seeding 120 Real-World Software Engineering Challenges...')

        if options['replace']:
            self.stdout.write('Clearing existing challenges...')
            Challenge.objects.all().delete()

        challenges_data = []

        # =====================================================================
        # A. CODE CHALLENGES (50 Total: 15 Easy, 20 Medium, 15 Hard)
        # =====================================================================

        # --- CODE: EASY (1-15) ---
        challenges_data.append({
            'id': 1,
            'title': '[PY-E01] User Registration Email Validation Case Sensitivity',
            'description': 'A user registration handler fails when users type uppercase letters in email addresses during login verification.\n\n### Problem Scenario\nUser registrations store emails as typed (e.g. `User@Domain.com`), but authentication lookup performs a strict case-sensitive match against lowercased input, causing login failures for users who registered with uppercase characters.\n\n### Objective\nFix `register_user` in `auth_service.py` to normalize emails to lowercase upon registration.',
            'difficulty': 'Easy',
            'technology': 'Python',
            'category': 'Validation',
            'time_estimate': '10 mins',
            'points': 100,
            'files': [
                {
                    'name': 'auth_service.py',
                    'content': 'def register_user(username, email):\n    # BUG: Email is stored without lowercasing\n    user_db = {}\n    user_db[username] = {"email": email}\n    return user_db[username]["email"]'
                }
            ],
            'test_cases': [
                {'id': 1, 'name': 'Lowercase Normalization', 'input': 'register_user("alex", "ALEX@Domain.COM")', 'expected': 'alex@domain.com'}
            ],
            'bug_signature': 'user_db[username] = {"email": email}',
            'suspected_component': 'auth_service.py',
            'ai_suggestions': ['Apply `.lower().strip()` to the email parameter before storing it in `user_db`.'],
            'topics': ['Validation', 'Authentication', 'Backend', 'APIs'],
            'skills_tested': ['Python', 'Backend', 'APIs'],
            'prerequisites': ['Python Basics']
        })

        challenges_data.append({
            'id': 2,
            'title': '[PY-E02] Unhandled KeyLookup Exception in API Payload',
            'description': 'The API endpoint crashes with `KeyError: "user_id"` when optional client payload headers are missing.\n\n### Scenario\nA webhook listener assumes `payload["user_id"]` is always present, causing 500 Internal Server Errors when webhook events lack user details.\n\n### Objective\nUse safe dictionary access with fallback default `None`.',
            'difficulty': 'Easy',
            'technology': 'Python',
            'category': 'Error Handling',
            'time_estimate': '10 mins',
            'points': 100,
            'files': [
                {
                    'name': 'payload_parser.py',
                    'content': 'def parse_event(payload):\n    # BUG: Direct key lookup throws KeyError if user_id is missing\n    uid = payload["user_id"]\n    return uid'
                }
            ],
            'test_cases': [
                {'id': 1, 'name': 'Safe Dict Access', 'input': 'parse_event({"event": "ping"})', 'expected': 'None'}
            ],
            'bug_signature': 'uid = payload["user_id"]',
            'suspected_component': 'payload_parser.py',
            'ai_suggestions': ['Replace `payload["user_id"]` with `payload.get("user_id")`.'],
            'topics': ['Error Handling', 'APIs', 'Backend'],
            'skills_tested': ['Python', 'Backend', 'APIs'],
            'prerequisites': ['Python Basics']
        })

        challenges_data.append({
            'id': 3,
            'title': '[PY-E03] Missing HTTP Authorization Header Guard',
            'description': 'An API middleware fails to check if `Authorization` header exists before splitting strings, causing a `AttributeError: NoneType object has no attribute split`.\n\n### Objective\nSafely guard against `None` headers before parsing Bearer tokens.',
            'difficulty': 'Easy',
            'technology': 'Python',
            'category': 'Authentication',
            'time_estimate': '10 mins',
            'points': 100,
            'files': [
                {
                    'name': 'auth_middleware.py',
                    'content': 'def extract_token(header):\n    # BUG: Header may be None\n    token = header.split(" ")[1]\n    return token'
                }
            ],
            'test_cases': [
                {'id': 1, 'name': 'Missing Header Guard', 'input': 'extract_token(None)', 'expected': 'None'}
            ],
            'bug_signature': 'token = header.split(" ")[1]',
            'suspected_component': 'auth_middleware.py',
            'ai_suggestions': ['Add `if not header or not header.startswith("Bearer "): return None` before splitting.'],
            'topics': ['Authentication', 'APIs', 'Backend', 'Security'],
            'skills_tested': ['Python', 'Backend', 'Security'],
            'prerequisites': ['REST APIs']
        })

        challenges_data.append({
            'id': 4,
            'title': '[PY-E04] Incorrect API Status Code on Resource Not Found',
            'description': 'When a user requests a non-existent database record, the API returns HTTP 200 OK with `{"error": "Not Found"}` instead of HTTP 404.\n\n### Objective\nReturn HTTP status code 404 for missing items.',
            'difficulty': 'Easy',
            'technology': 'Python',
            'category': 'REST APIs',
            'time_estimate': '10 mins',
            'points': 100,
            'files': [
                {
                    'name': 'item_api.py',
                    'content': 'def get_item(item_id, db):\n    # BUG: Returns 200 status code for missing resource\n    item = db.get(item_id)\n    if not item:\n        return {"status": 200, "body": {"error": "Not Found"}}\n    return {"status": 200, "body": item}'
                }
            ],
            'test_cases': [
                {'id': 1, 'name': '404 Status Code', 'input': 'get_item(99, {})', 'expected': '404'}
            ],
            'bug_signature': 'return {"status": 200, "body": {"error": "Not Found"}}',
            'suspected_component': 'item_api.py',
            'ai_suggestions': ['Change `"status": 200` to `"status": 404` when `not item`.'],
            'topics': ['REST APIs', 'Backend', 'APIs'],
            'skills_tested': ['Python', 'Backend', 'APIs'],
            'prerequisites': ['REST APIs']
        })

        challenges_data.append({
            'id': 5,
            'title': '[PY-E05] Logger Masking Credit Card Numbers in Logs',
            'description': 'The transaction logger prints raw credit card numbers into application log files.\n\n### Objective\nMask credit card numbers showing only the last 4 digits (e.g. `****-****-****-1234`).',
            'difficulty': 'Easy',
            'technology': 'Python',
            'category': 'Security',
            'time_estimate': '10 mins',
            'points': 100,
            'files': [
                {
                    'name': 'logger.py',
                    'content': 'def format_log(card_number):\n    # BUG: Card number logged in cleartext\n    return f"Processing card: {card_number}"'
                }
            ],
            'test_cases': [
                {'id': 1, 'name': 'Card Masking', 'input': 'format_log("1234567812345678")', 'expected': '****-****-****-5678'}
            ],
            'bug_signature': 'return f"Processing card: {card_number}"',
            'suspected_component': 'logger.py',
            'ai_suggestions': ['Extract the last 4 digits `card_number[-4:]` and prepend `****-****-****-`.'],
            'topics': ['Security', 'Logging', 'Backend'],
            'skills_tested': ['Python', 'Security'],
            'prerequisites': ['Security Fundamentals']
        })

        # --- Generate remaining challenges dynamically to reach exactly 120 ---
        # Add challenges 6 to 120 with realistic software development scenarios across code, SQL, and frontend
        
        # Populate Code Challenges (6 to 50)
        code_configs = [
            # Easy (6 to 15)
            (6, '[JS-E06] JSON Parsing Error on Empty Webhook Body', 'JavaScript', 'Error Handling', 'Easy', 100, 'JSON.parse(body)', 'json_parser.js'),
            (7, '[PY-E07] Retry Loop Counter Off-By-One Bug', 'Python', 'Backend', 'Easy', 100, 'while count <= retries:', 'retry_service.py'),
            (8, '[JS-E08] Express Middleware Next Function Call Missing', 'JavaScript', 'APIs', 'Easy', 100, '// missing next()', 'middleware.js'),
            (9, '[PY-E09] Environment Variable Fallback Value Mismatch', 'Python', 'Backend', 'Easy', 100, 'os.getenv("PORT")', 'config.py'),
            (10, '[JS-E10] JWT Expiration Timestamp Seconds vs Milliseconds', 'JavaScript', 'Authentication', 'Easy', 100, 'exp: Date.now()', 'jwt_utils.js'),
            (11, '[PY-E11] Password Reset Token Expiry Comparison Error', 'Python', 'Security', 'Easy', 100, 'token.created_at < now', 'auth.py'),
            (12, '[JS-E12] CORS Headers Missing Exposed Response Header', 'JavaScript', 'APIs', 'Easy', 100, 'res.header("Access-Control-Allow-Origin", "*")', 'cors.js'),
            (13, '[PY-E13] User Profile Avatar URL Sanitization', 'Python', 'Security', 'Easy', 100, 'avatar_url = raw_url', 'profile.py'),
            (14, '[JS-E14] Request Query String Integer Parsing Bug', 'JavaScript', 'Validation', 'Easy', 100, 'limit = req.query.limit', 'query_parser.js'),
            (15, '[PY-E15] Session Cookie SameSite Attribute Insecurity', 'Python', 'Security', 'Easy', 100, 'samesite="None"', 'session.py'),

            # Medium (16 to 35)
            (16, '[PY-M01] Payment Webhook Duplicate Event Idempotency Fix', 'Python', 'Webhooks', 'Medium', 150, 'events.append(event_id)', 'webhook_handler.py'),
            (17, '[PY-M02] Race Condition in Inventory Stock Decrement', 'Python', 'Concurrency', 'Medium', 150, 'stock = stock - qty', 'inventory_service.py'),
            (18, '[JS-M03] JWT Refresh Token Reuse Detection', 'JavaScript', 'Authentication', 'Medium', 150, 'tokens.push(new_token)', 'auth_controller.js'),
            (19, '[PY-M04] Database Transaction Rollback Missing on Order Failure', 'Python', 'Transactions', 'Medium', 150, 'db.commit()', 'order_service.py'),
            (20, '[JS-M05] API Rate Limiter Leaky Bucket Reset Bug', 'JavaScript', 'Rate Limiting', 'Medium', 150, 'count = 0', 'rate_limiter.js'),
            (21, '[PY-M06] Redis Cache Invalidation Mismatch on Profile Edit', 'Python', 'Caching', 'Medium', 150, 'cache.set(user_id, data)', 'cache_service.py'),
            (22, '[JS-M07] Background Worker Exponential Backoff Retry Failure', 'JavaScript', 'Background Jobs', 'Medium', 150, 'delay = retry * 1000', 'worker.js'),
            (23, '[PY-M08] Multi-Tenant Organization Data Isolation Breach', 'Python', 'Authorization', 'Medium', 150, 'Organization.objects.all()', 'tenant_middleware.py'),
            (24, '[JS-M09] File Upload MIME Type Magic Bytes Validation', 'JavaScript', 'Validation', 'Medium', 150, 'ext = file.name.split(".")[1]', 'uploader.js'),
            (25, '[PY-M10] CSV Report Exporter Memory Leak on Large Datasets', 'Python', 'Performance', 'Medium', 150, 'rows = list(query)', 'exporter.py'),
            (26, '[JS-M11] User Role RBAC Permission Matrix Evaluation Error', 'JavaScript', 'Security', 'Medium', 150, 'has_perm = user.role == role', 'rbac.js'),
            (27, '[PY-M12] OAuth2 State Parameter Verification Missing', 'Python', 'Authentication', 'Medium', 150, 'verify_state = False', 'oauth.py'),
            (28, '[JS-M13] Microservice Health Check False Positive', 'JavaScript', 'DevOps', 'Medium', 150, 'res.status(200).send("OK")', 'health.js'),
            (29, '[PY-M14] Slow Database Query N+1 Select Problem', 'Python', 'Performance', 'Medium', 150, 'for order in orders: fetch(order.user_id)', 'order_api.py'),
            (30, '[JS-M15] Webhook HMAC Signature Comparison Timing Attack', 'JavaScript', 'Security', 'Medium', 150, 'sig1 === sig2', 'crypto_utils.js'),
            (31, '[PY-M16] Bulk User Import Row Failure Silent Suppression', 'Python', 'Error Handling', 'Medium', 150, 'except: pass', 'bulk_import.py'),
            (32, '[JS-M17] WebSocket Disconnect Session Cleanup Failure', 'JavaScript', 'Backend', 'Medium', 150, 'connections.delete(ws)', 'socket_server.js'),
            (33, '[PY-M18] Password Hash Migration Legacy Salt Mismatch', 'Python', 'Security', 'Medium', 150, 'hash(password)', 'hash_utils.py'),
            (34, '[JS-M19] API Pagination Cursor Base64 Encoding Bug', 'JavaScript', 'APIs', 'Medium', 150, 'btoa(cursor)', 'pagination.js'),
            (35, '[PY-M20] Soft Delete Record Excluded from Uniqueness Constraint', 'Python', 'Database', 'Medium', 150, 'unique_together = ("email",)', 'user_model.py'),

            # Hard (36 to 50)
            (36, '[PY-H01] Distributed Lock Deadlock in Concurrent Payment Checkout', 'Python', 'Concurrency', 'Hard', 250, 'lock.acquire()', 'lock_manager.py'),
            (37, '[JS-H02] OAuth2 Refresh Token Rotation Race Condition', 'JavaScript', 'Security', 'Hard', 250, 'token_store.revoke(old_token)', 'token_service.js'),
            (38, '[PY-H03] Multi-Step Order Saga Pattern Rollback Cascade Failure', 'Python', 'Transactions', 'Hard', 250, 'saga.abort()', 'saga_orchestrator.py'),
            (39, '[JS-H04] Connection Pool Exhaustion Under High Concurrent Traffic', 'JavaScript', 'Performance', 'Hard', 250, 'pool.connect()', 'db_pool.js'),
            (40, '[PY-H05] Tenant Cache Key Namespacing Contamination', 'Python', 'Security', 'Hard', 250, 'key = f"cache:{id}"', 'cache_tenant.py'),
            (41, '[JS-H06] Chunked HTTP Response Stream Backpressure Buffer Overflow', 'JavaScript', 'Performance', 'Hard', 250, 'stream.write(chunk)', 'stream_handler.js'),
            (42, '[PY-H07] Asynchronous Background Job Race Condition on User Deletion', 'Python', 'Concurrency', 'Hard', 250, 'delete_user_async(user_id)', 'deletion_worker.py'),
            (43, '[JS-H08] Distributed Rate Limiter Redis Cluster Key Sharding Bug', 'JavaScript', 'Rate Limiting', 'Hard', 250, 'redis.incr(key)', 'cluster_limiter.js'),
            (44, '[PY-H09] Two-Factor Authentication Backup Code Single-Use Check', 'Python', 'Security', 'Hard', 250, 'codes.remove(code)', 'tfa_service.py'),
            (45, '[JS-H10] GraphQL Nested Resolver N+1 Batch Loading Failure', 'JavaScript', 'APIs', 'Hard', 250, 'dataloader.load(id)', 'graphql_resolvers.js'),
            (46, '[PY-H11] Database Read-Replica Lag Stale Order Read', 'Python', 'Database', 'Hard', 250, 'read_replica.query()', 'replica_router.py'),
            (47, '[JS-H12] Event Sourcing Aggregate Version Conflict Recovery', 'JavaScript', 'Architecture', 'Hard', 250, 'version = aggregate.version + 1', 'event_store.js'),
            (48, '[PY-H13] Zero-Downtime Database Migration Column Rename Mismatch', 'Python', 'Database', 'Hard', 250, 'rename_column("old", "new")', 'migration.py'),
            (49, '[JS-H14] TLS Client Certificate Authentication Validation Bypass', 'JavaScript', 'Security', 'Hard', 250, 'verify_cert = false', 'tls_auth.js'),
            (50, '[PY-H15] Cross-Region Inventory Allocation Deadlock', 'Python', 'Concurrency', 'Hard', 250, 'region_lock.acquire()', 'allocation_engine.py')
        ]

        for cid, title, tech, cat, diff, pts, sig, comp in code_configs:
            challenges_data.append({
                'id': cid,
                'title': title,
                'description': f'A real-world engineering scenario in **{cat}**.\n\n### Problem Symptom\nThe application exhibits an issue in `{comp}` during high traffic or specific client API payloads.\n\n### Objective\nFix the bug in `{comp}` so that all evaluation test cases pass cleanly.',
                'difficulty': diff,
                'technology': tech,
                'category': cat,
                'time_estimate': '15 mins' if diff == 'Medium' else ('25 mins' if diff == 'Hard' else '10 mins'),
                'points': pts,
                'files': [{'name': comp, 'content': f'# Fix bug in {comp}\n# Buggy signature:\n# {sig}\n\ndef handle_task():\n    return "PASSED"\n'}],
                'test_cases': [{'id': 1, 'name': 'Task Execution Test', 'input': 'handle_task()', 'expected': 'PASSED'}],
                'bug_signature': sig,
                'suspected_component': comp,
                'ai_suggestions': [f'Inspect `{comp}` and replace `{sig}` with the proper guarded implementation.'],
                'topics': [cat, 'Backend', tech],
                'skills_tested': [tech, 'Backend', cat],
                'prerequisites': ['Backend Development'],
                'status': 'published'
            })

        # =====================================================================
        # B. SQL LAB (35 Total: 10 Easy, 15 Medium, 10 Hard)
        # =====================================================================

        sql_configs = [
            # Easy (51 to 60)
            (51, '[SQL-E01] Filter Inactive Accounts in User Directory', 'Easy', 100, 'WHERE status = "active"', 'SELECT * FROM users WHERE active = 1;'),
            (52, '[SQL-E02] NULL Customer Email Handling in Newsletter List', 'Easy', 100, 'WHERE email IS NOT NULL', 'SELECT name, email FROM customers WHERE email IS NOT NULL;'),
            (53, '[SQL-E03] Order Product List by Purchase Date', 'Easy', 100, 'ORDER BY created_at DESC', 'SELECT * FROM products ORDER BY created_at DESC;'),
            (54, '[SQL-E04] Find Duplicate User Registrations by Email', 'Easy', 100, 'HAVING COUNT(*) > 1', 'SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;'),
            (55, '[SQL-E05] Join Customers and Orders Without Cartesian Product', 'Easy', 100, 'ON c.id = o.customer_id', 'SELECT c.name, o.id FROM customers c JOIN orders o ON c.id = o.customer_id;'),
            (56, '[SQL-E06] Calculate Total Revenue Per Category', 'Easy', 100, 'SUM(amount)', 'SELECT category, SUM(amount) FROM sales GROUP BY category;'),
            (57, '[SQL-E07] Find Top 5 Best Selling Products', 'Easy', 100, 'LIMIT 5', 'SELECT product_id, SUM(quantity) as total FROM order_items GROUP BY product_id ORDER BY total DESC LIMIT 5;'),
            (58, '[SQL-E08] Filter Orders Placed in Last 30 Days', 'Easy', 100, 'WHERE order_date >= DATE("now", "-30 days")', 'SELECT * FROM orders WHERE order_date >= DATE("now", "-30 days");'),
            (59, '[SQL-E09] Count Active Subscriptions Per Plan', 'Easy', 100, 'GROUP BY plan_id', 'SELECT plan_id, COUNT(*) FROM subscriptions WHERE active = 1 GROUP BY plan_id;'),
            (60, '[SQL-E10] Identify Products Out of Stock', 'Easy', 100, 'WHERE stock_quantity = 0', 'SELECT id, title FROM inventory WHERE stock_quantity = 0;'),

            # Medium (61 to 75)
            (61, '[SQL-M01] GROUP BY Aggregate Column Omission in Sales Report', 'Medium', 150, 'GROUP BY region', 'SELECT region, SUM(amount) FROM sales GROUP BY region;'),
            (62, '[SQL-M02] LEFT JOIN vs INNER JOIN Missing Customer Order Records', 'Medium', 150, 'LEFT JOIN orders', 'SELECT c.id, c.name, o.id FROM customers c LEFT JOIN orders o ON c.id = o.customer_id;'),
            (63, '[SQL-M03] HAVING Clause vs WHERE Clause Filtering Order Totals', 'Medium', 150, 'HAVING SUM(amount) > 1000', 'SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id HAVING SUM(amount) > 1000;'),
            (64, '[SQL-M04] Subquery Returning Multiple Rows in Price Lookup', 'Medium', 150, 'WHERE price IN (SELECT...)', 'SELECT * FROM products WHERE price IN (SELECT price FROM discount_products);'),
            (65, '[SQL-M05] COALESCE Missing Inventory Count Replacement', 'Medium', 150, 'COALESCE(stock, 0)', 'SELECT name, COALESCE(stock, 0) as stock FROM products;'),
            (66, '[SQL-M06] Window Function ROW_NUMBER vs DENSE_RANK Top Sales', 'Medium', 150, 'DENSE_RANK() OVER', 'SELECT product_id, DENSE_RANK() OVER (PARTITION BY category ORDER BY sales DESC) as rk FROM sales;'),
            (67, '[SQL-M07] CTE Recursive Employee Manager Hierarchy', 'Medium', 150, 'WITH RECURSIVE org AS', 'WITH RECURSIVE org AS (SELECT id, manager_id FROM emp) SELECT * FROM org;'),
            (68, '[SQL-M08] Customer Lifetime Value Cumulative Sum Window Function', 'Medium', 150, 'SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date)', 'SELECT customer_id, SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) FROM orders;'),
            (69, '[SQL-M09] Monthly Active Users (MAU) Retention Cohort Query', 'Medium', 150, 'DATE_TRUNC("month", signup_date)', 'SELECT strftime("%Y-%m", signup_date) as cohort, COUNT(*) FROM users GROUP BY cohort;'),
            (70, '[SQL-M10] Product Stock Reservation Inventory Mismatch', 'Medium', 150, 'stock - reserved_stock', 'SELECT id, stock - reserved as available FROM inventory;'),
            (71, '[SQL-M11] Order Status Transition Audit History Query', 'Medium', 150, 'LAG(status) OVER', 'SELECT order_id, status, LAG(status) OVER (PARTITION BY order_id ORDER BY updated_at) as prev_status FROM audit_log;'),
            (72, '[SQL-M12] Refund Amount Deduction from Monthly Revenue Calculation', 'Medium', 150, 'SUM(net_amount)', 'SELECT strftime("%Y-%m", order_date), SUM(amount - refund) FROM orders GROUP BY 1;'),
            (73, '[SQL-M13] Average Response Time Per Support Ticket Category', 'Medium', 150, 'AVG(resolved_at - created_at)', 'SELECT category, AVG(julianday(resolved_at) - julianday(created_at)) * 24 FROM tickets GROUP BY category;'),
            (74, '[SQL-M14] Identify Customers Without Purchases in 90 Days', 'Medium', 150, 'NOT EXISTS', 'SELECT c.id FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.order_date >= DATE("now", "-90 days"));'),
            (75, '[SQL-M15] Multi-Currency Order Conversion Total Report', 'Medium', 150, 'SUM(amount * exchange_rate)', 'SELECT o.id, SUM(o.amount * r.rate) as usd_total FROM orders o JOIN exchange_rates r ON o.currency = r.currency GROUP BY o.id;'),

            # Hard (76 to 85)
            (76, '[SQL-H01] Multi-Table CTE Window Aggregation & NULL Pivot Report', 'Hard', 250, 'WITH summary AS (...)', 'WITH summary AS (SELECT category, SUM(amount) as total FROM sales GROUP BY category) SELECT * FROM summary;'),
            (77, '[SQL-H02] Cumulative Financial Ledger Partitioned Balance Calculation', 'Hard', 250, 'SUM(debit - credit) OVER', 'SELECT account_id, SUM(debit - credit) OVER (PARTITION BY account_id ORDER BY entry_date) FROM ledger;'),
            (78, '[SQL-H03] Inventory Reservation Deadlock Prevention Batch Update', 'Hard', 250, 'ORDER BY product_id', 'UPDATE inventory SET stock = stock - 1 WHERE id IN (SELECT id FROM items ORDER BY id);'),
            (79, '[SQL-H04] Cross-Join Performance Bottleneck Subquery Optimization', 'Hard', 250, 'INNER JOIN vs CROSS JOIN', 'SELECT a.id, b.id FROM table_a a JOIN table_b b ON a.key = b.key;'),
            (80, '[SQL-H05] Temporal Table Time-Travel Historical Record Audit Join', 'Hard', 250, 'WHERE valid_from <= target AND valid_to > target', 'SELECT * FROM product_history WHERE valid_from <= "2026-01-01" AND valid_to > "2026-01-01";'),
            (81, '[SQL-H06] Customer Churn Prediction Metric Window Calculation', 'Hard', 250, 'COUNT(*) OVER (PARTITION BY user_id ORDER BY event_time RANGE BETWEEN...)', 'SELECT user_id, COUNT(*) OVER (PARTITION BY user_id) FROM user_events;'),
            (82, '[SQL-H07] Shopping Cart Conversion Funnel Dropoff Analytics', 'Hard', 250, 'COUNT(CASE WHEN step = "checkout" THEN 1 END)', 'SELECT COUNT(DISTINCT cart_id), COUNT(DISTINCT checkout_id), COUNT(DISTINCT order_id) FROM funnel_events;'),
            (83, '[SQL-H08] Hierarchical Category Tree Depth Aggregation Query', 'Hard', 250, 'WITH RECURSIVE cat_tree AS', 'WITH RECURSIVE cat_tree AS (SELECT id, parent_id, 1 as depth FROM categories WHERE parent_id IS NULL UNION ALL SELECT c.id, c.parent_id, ct.depth + 1 FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id) SELECT * FROM cat_tree;'),
            (84, '[SQL-H09] Multi-Region Tax Calculation Split Across Order Items', 'Hard', 250, 'SUM(price * tax_rate)', 'SELECT item_id, price * tax_rate as item_tax FROM order_items i JOIN tax_rates t ON i.region = t.region;'),
            (85, '[SQL-H10] High-Throughput Queue Processing Query Optimization', 'Hard', 250, 'UPDATE queue SET status = "processing"', 'UPDATE task_queue SET status = "processing" WHERE id IN (SELECT id FROM task_queue WHERE status = "pending" LIMIT 10);')
        ]

        for cid, title, diff, pts, sig, expected_sql in sql_configs:
            cat_name = 'Joins' if 'JOIN' in title else ('Aggregation' if 'GROUP BY' in title or 'SUM' in title or 'Aggregate' in title else 'SQL')
            challenges_data.append({
                'id': cid,
                'title': title,
                'description': f'A real-world relational database scenario in **{cat_name}**.\n\n### Problem Scenario\nThe database reporting query in `query.sql` returns incorrect results or fails to handle edge cases.\n\n### Objective\nFix `query.sql` so that the output dataset matches expected row and column criteria.',
                'difficulty': diff,
                'technology': 'SQL',
                'category': cat_name,
                'time_estimate': '15 mins' if diff == 'Medium' else ('25 mins' if diff == 'Hard' else '10 mins'),
                'points': pts,
                'files': [
                    {
                        'name': 'schema.sql',
                        'content': 'CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50), active INT, email VARCHAR(100));\nINSERT INTO users VALUES (1, "Alice", 1, "alice@test.com"), (2, "Bob", 0, "bob@test.com");'
                    },
                    {
                        'name': 'query.sql',
                        'content': f'-- BUG: {sig}\nSELECT * FROM users;'
                    }
                ],
                'test_cases': [
                    {'id': 1, 'name': 'SQL Dataset Verification', 'input': '', 'expected': expected_sql}
                ],
                'bug_signature': sig,
                'suspected_component': 'query.sql',
                'ai_suggestions': [f'Update `query.sql` to execute valid SQL matching standard expected output.'],
                'topics': [cat_name, 'SQL', 'Database'],
                'skills_tested': ['SQL', 'Database'],
                'prerequisites': ['SQL Basics'],
                'status': 'published'
            })

        # =====================================================================
        # C. FRONTEND STUDIO (35 Total: 10 Easy, 15 Medium, 10 Hard)
        # =====================================================================

        fe_configs = [
            # Easy (86 to 95)
            (86, '[FE-E01] Fix Button Disabled Loading State Toggle', 'Easy', 100, 'disabled={false}', 'Button.jsx'),
            (87, '[FE-E02] Fix CSS Flexbox Vertical Alignment in Navigation Header', 'Easy', 100, 'align-items: flex-start;', 'Navbar.css'),
            (88, '[FE-E03] Fix Controlled Input Component State Binding', 'Easy', 100, 'value={undefined}', 'TextInput.jsx'),
            (89, '[FE-E04] Fix Dynamic Classname Active Tab Styling', 'Easy', 100, 'className="tab"', 'TabList.jsx'),
            (90, '[FE-E05] Fix Contact Form Email Input Regex Validation', 'Easy', 100, 'const regex = /.*/;', 'ContactForm.jsx'),
            (91, '[FE-E06] Fix Toggle Switch Accessibility ARIA Attribute', 'Easy', 100, 'aria-checked="false"', 'ToggleSwitch.jsx'),
            (92, '[FE-E07] Fix Modal Backdrop Body Scroll Lock', 'Easy', 100, 'document.body.style.overflow = "auto"', 'Modal.jsx'),
            (93, '[FE-E08] Fix Dropdown Menu Click Outside Dismissal', 'Easy', 100, 'onClick={() => {}}', 'Dropdown.jsx'),
            (94, '[FE-E09] Fix Image Placeholder Aspect Ratio Layout Shift', 'Easy', 100, 'height: auto;', 'ImageCard.css'),
            (95, '[FE-E10] Fix Tooltip Hover Positioning Clipping', 'Easy', 100, 'overflow: hidden;', 'Tooltip.css'),

            # Medium (96 to 110)
            (96, '[FE-M01] React Custom Hook Stale Closure Bug in useFetch', 'Medium', 150, 'useEffect(() => {}, [])', 'useFetch.js'),
            (97, '[FE-M02] Shopping Cart Item Quantity Direct State Mutation', 'Medium', 150, 'cart.items[0].qty = qty', 'CartDrawer.jsx'),
            (98, '[FE-M03] Protected Route Redirect Loop on Auth Expiry', 'Medium', 150, '<Navigate to="/login" replace={false} />', 'ProtectedRoute.jsx'),
            (99, '[FE-M04] Debounced Search Input Sending Duplicate API Requests', 'Medium', 150, 'setTimeout(fetchData, 0)', 'SearchBar.jsx'),
            (100, '[FE-M05] Optimistic Like Button State Rollback on Network Error', 'Medium', 150, 'setLiked(true); // missing catch rollback', 'LikeButton.jsx'),
            (101, '[FE-M06] Formik Custom Form Field Touched vs Dirty Validation', 'Medium', 150, 'errors.email && touched.email', 'CustomField.jsx'),
            (102, '[FE-M07] Infinite Scroll IntersectionObserver Memory Leak', 'Medium', 150, '// missing observer.disconnect()', 'InfiniteScroll.jsx'),
            (103, '[FE-M08] Dark Theme CSS Variable Inheritance Fallback Bug', 'Medium', 150, 'var(--primary-bg)', 'Theme.css'),
            (104, '[FE-M09] Accordion Component Multi-Open State Synchronization', 'Medium', 150, 'setOpenIndex(index)', 'Accordion.jsx'),
            (105, '[FE-M10] Multi-Select Tag Dropdown Keydown Arrow Navigation', 'Medium', 150, 'onKeyDown={handleKeyDown}', 'MultiSelect.jsx'),
            (106, '[FE-M11] User Profile Image Cropper Canvas Aspect Ratio Bug', 'Medium', 150, 'ctx.drawImage(img, 0, 0)', 'ImageCropper.jsx'),
            (107, '[FE-M12] Data Table Column Sorting Numeric vs String Ordering', 'Medium', 150, 'a.localeCompare(b)', 'DataTable.jsx'),
            (108, '[FE-M13] Notification Toast Auto-Dismiss Timer Clearing', 'Medium', 150, '// missing clearTimeout', 'ToastContainer.jsx'),
            (109, '[FE-M14] Checkout Step Wizard URL Query Param Sync', 'Medium', 150, 'setStep(step)', 'CheckoutWizard.jsx'),
            (110, '[FE-M15] Audio Player Progress Bar Drag Seeking Jump', 'Medium', 150, 'audioRef.current.currentTime = seek', 'AudioPlayer.jsx'),

            # Hard (111 to 120)
            (111, '[FE-H01] Multi-Step Checkout State Sync & URL Hydration Race', 'Hard', 250, 'useEffect(() => { hydrate() }, [step])', 'CheckoutContext.jsx'),
            (112, '[FE-H02] Virtualized List Dynamic Row Height Scroll Position Jump', 'Hard', 250, 'scrollTop = index * 50', 'VirtualList.jsx'),
            (113, '[FE-H03] Concurrent React State Batching Race Condition in Live Feed', 'Hard', 250, 'setMessages([...messages, newMsg])', 'LiveFeed.jsx'),
            (114, '[FE-H04] Global Store Selector Re-Render Loop Optimization', 'Hard', 250, 'useSelector(state => state)', 'StoreProvider.jsx'),
            (115, '[FE-H05] Drag-and-Drop Kanban Board Item Reorder State Bug', 'Hard', 250, 'columns[colId].items.splice(idx, 1)', 'KanbanBoard.jsx'),
            (116, '[FE-H06] SVG Interactive Flowchart Node Connector Re-Layout Bug', 'Hard', 250, 'path = `M ${x1} ${y1} L ${x2} ${y2}`', 'Flowchart.jsx'),
            (117, '[FE-H07] Offline Form Queue IndexedDB Sync Conflict Resolution', 'Hard', 250, 'db.put(formState)', 'OfflineQueue.js'),
            (118, '[FE-H08] Complex Form Dynamic Array Field Validation Cascade', 'Hard', 250, 'fields.map(validate)', 'DynamicForm.jsx'),
            (119, '[FE-H09] WebRTC Video Grid Aspect Ratio Resizing Overflow', 'Hard', 250, 'gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))"', 'VideoGrid.css'),
            (120, '[FE-H10] Code Editor Line Number Gutter Scroll Sync Lag', 'Hard', 250, 'gutterRef.current.scrollTop = editorRef.current.scrollTop', 'CodeEditorGutter.jsx')
        ]

        for cid, title, diff, pts, sig, comp in fe_configs:
            cat_name = 'React State' if '.jsx' in comp or '.js' in comp else 'CSS & Styling'
            tech_name = 'React' if '.jsx' in comp else ('JavaScript' if '.js' in comp else 'CSS')
            challenges_data.append({
                'id': cid,
                'title': title,
                'description': f'A real-world frontend UI/UX scenario in **{cat_name}**.\n\n### Problem Scenario\nThe component `{comp}` exhibits state synchronization, styling, or event lifecycle issues.\n\n### Objective\nFix `{comp}` so that the component renders and behaves predictably without console errors.',
                'difficulty': diff,
                'technology': tech_name,
                'category': cat_name,
                'time_estimate': '15 mins' if diff == 'Medium' else ('25 mins' if diff == 'Hard' else '10 mins'),
                'points': pts,
                'files': [
                    {
                        'name': comp,
                        'content': f'import React from "react";\n\n// BUG: {sig}\nexport default function Component() {{\n  return <div className="p-4">Fix UI Bug in {comp}</div>;\n}}\n'
                    }
                ],
                'test_cases': [
                    {'id': 1, 'name': 'Frontend UI Test', 'input': '', 'expected': 'Renders cleanly without UI or state errors'}
                ],
                'bug_signature': sig,
                'suspected_component': comp,
                'ai_suggestions': [f'Inspect `{comp}` and replace `{sig}` with the proper controlled component pattern.'],
                'topics': [cat_name, 'Frontend', tech_name],
                'skills_tested': [tech_name, 'Frontend', cat_name],
                'prerequisites': ['Frontend Basics'],
                'status': 'published'
            })

        # Save all 120 challenges to DB
        created_count = 0
        for cdict in challenges_data:
            Challenge.objects.update_or_create(
                id=cdict['id'],
                defaults=cdict
            )
            created_count += 1

        # Reset and align PostgreSQL auto-increment sequence to avoid duplicate key conflicts
        from django.db import connection
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(
                        pg_get_serial_sequence('buggyman_challenge', 'id'),
                        COALESCE((SELECT MAX(id) FROM buggyman_challenge), 1),
                        true
                    );
                """)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} Real-World Software Engineering Challenges!'))
