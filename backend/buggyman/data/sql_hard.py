"""
SQL Lab: Hard Challenges (76 to 85)
"""

def get_sql_hard():
    challenges = []

    # 76. Concurrent inventory reservations oversell stock
    challenges.append({
        'id': 76,
        'title': '[SQL-H01] Concurrent Inventory Reservations Oversell Stock',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A flash-sale ticketing engine executes warehouse deductions when checkout begins.

### Bug Report
When stock is 1, two concurrent buyers both execute `UPDATE inventory SET stock = stock - 1 WHERE id = 10`, setting stock to -1 and overselling the item.

### Steps to Reproduce
1. Stock = 1.
2. Two updates execute without condition `stock >= requested_qty`.
3. Stock becomes negative.

### Expected Behavior
Guarded update: only decrement if `stock >= 1`: `UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1`.

### Actual Behavior
Blind decrement without checking availability in WHERE clause.

### Impact
Over-allocated physical inventory and canceled customer orders.

### Requirements
- Add guard condition `AND stock >= 1` (or `stock > 0`) to the UPDATE query.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE inventory (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    stock INT
);

INSERT INTO inventory VALUES (10, 'PlayStation 5', 0);"""
            },
            {
                'name': 'query.sql',
                'content': """UPDATE inventory SET stock = stock - 1 WHERE id = 10;
SELECT id, name, stock FROM inventory WHERE id = 10;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Guarded update only decrements when stock available', 'input': '', 'expected': """UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1;
SELECT id, name, stock FROM inventory WHERE id = 10;"""}
        ],
        'bug_signature': 'UPDATE inventory SET stock = stock - 1 WHERE id = 10;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `AND stock >= 1` to the `WHERE` clause.'
        ],
        'topics': ['SQL', 'Concurrency', 'Conditional UPDATE'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL UPDATE and Concurrency'],
        'status': 'published',
        'expected_query': """UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1;
SELECT id, name, stock FROM inventory WHERE id = 10;"""
    })

    # 77. A payment transaction updates balances without maintaining consistency
    challenges.append({
        'id': 77,
        'title': '[SQL-H02] A Payment Transaction Updates Balances Without Maintaining Consistency',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A banking ledger transfers $50 from Account 1 to Account 2.

### Bug Report
Debit executes, but credit fails due to an invalid account ID. Because the statements are not wrapped in a transaction, Account 1 loses $50 permanently while Account 2 receives nothing!

### Steps to Reproduce
1. Execute debit without BEGIN TRANSACTION / ROLLBACK.
2. Receiver update fails.
3. Total bank ledger is out of balance.

### Expected Behavior
Wrap statements in a database transaction with consistency checks.

### Actual Behavior
Unmanaged auto-commit executes partial state modifications.

### Impact
Financial ledger audit failure and lost customer money.

### Requirements
- Execute atomic update using conditional verification to ensure ledger balance.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE accounts (
    id INT PRIMARY KEY,
    owner VARCHAR(50),
    balance DECIMAL(10,2)
);

INSERT INTO accounts VALUES (1, 'Alice', 100.00), (2, 'Bob', 50.00);"""
            },
            {
                'name': 'query.sql',
                'content': """UPDATE accounts SET balance = balance - 50 WHERE id = 1;
UPDATE accounts SET balance = balance + 50 WHERE id = 999;
SELECT id, owner, balance FROM accounts ORDER BY id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Balances reflect successful atomic transfer', 'input': '', 'expected': """UPDATE accounts SET balance = balance - 50 WHERE id = 1 AND balance >= 50;
UPDATE accounts SET balance = balance + 50 WHERE id = 2;
SELECT id, owner, balance FROM accounts ORDER BY id;"""}
        ],
        'bug_signature': 'WHERE id = 999;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Ensure both balance updates execute with matching debit and credit amounts.'
        ],
        'topics': ['SQL', 'Transactions', 'Ledger Consistency'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Transactions'],
        'status': 'published',
        'expected_query': """UPDATE accounts SET balance = balance - 50 WHERE id = 1 AND balance >= 50;
UPDATE accounts SET balance = balance + 50 WHERE id = 2;
SELECT id, owner, balance FROM accounts ORDER BY id;"""
    })

    # 78. A multi-table JOIN multiplies aggregates across independent relationships
    challenges.append({
        'id': 78,
        'title': '[SQL-H03] A Multi-Table JOIN Multiplies Aggregates Across Independent Relationships',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A customer summary report calculates both total order spending AND total support tickets opened for each customer.

### Bug Report
Customer with 2 orders and 3 support tickets produces 2 x 3 = 6 joined rows. Order total is multiplied by 3, and support tickets count is multiplied by 2!

### Steps to Reproduce
1. Customer has orders totaling $150 (2 orders) and 3 tickets.
2. Query joins `customers` to `orders` AND to `tickets`.
3. Output reports revenue = $450 and tickets = 6.

### Expected Behavior
Aggregate `orders` and `tickets` independently in separate subqueries/CTEs before joining to `customers`.

### Actual Behavior
Joins multiple independent 1-to-many child tables in a single query.

### Impact
Customer lifetime value and support costs wildly inflated.

### Requirements
- Pre-aggregate `orders` by `customer_id` and `tickets` by `customer_id` in CTEs, then join to `customers`.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2)
);

CREATE TABLE tickets (
    id INT PRIMARY KEY,
    customer_id INT,
    subject VARCHAR(50)
);

INSERT INTO customers VALUES (1, 'Alice');
INSERT INTO orders VALUES (101, 1, 50.00), (102, 1, 100.00);
INSERT INTO tickets VALUES (201, 1, 'Login Help'), (202, 1, 'Billing Question'), (203, 1, 'Feedback');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT c.id, c.name, SUM(o.amount) AS total_spent, COUNT(t.id) AS total_tickets
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN tickets t ON c.id = t.customer_id
GROUP BY c.id, c.name;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Independent aggregation reports total_spent=150, tickets=3', 'input': '', 'expected': 'All registered users preserving unassigned plans as NULL'}
        ],
        'bug_signature': 'LEFT JOIN orders o ON c.id = o.customer_id\nLEFT JOIN tickets t',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Do not join two independent 1-to-many tables in one query.',
            'Aggregate each child table separately in CTEs first.'
        ],
        'topics': ['SQL', 'Cartesian Product', 'Multi-Table Joins', 'CTEs'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins and CTEs'],
        'status': 'published',
        'expected_query': """WITH o_summary AS (
    SELECT customer_id, SUM(amount) AS total_spent FROM orders GROUP BY customer_id
),
t_summary AS (
    SELECT customer_id, COUNT(*) AS total_tickets FROM tickets GROUP BY customer_id
)
SELECT c.id, c.name, COALESCE(o.total_spent, 0) AS total_spent, COALESCE(t.total_tickets, 0) AS total_tickets
FROM customers c
LEFT JOIN o_summary o ON c.id = o.customer_id
LEFT JOIN t_summary t ON c.id = t.customer_id;"""
    })

    # 79. A transaction failure leaves related financial records inconsistent
    challenges.append({
        'id': 79,
        'title': '[SQL-H04] A Transaction Failure Leaves Related Financial Records Inconsistent',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
An invoice closing script marks invoices as `'paid'` and creates matching audit records.

### Bug Report
An invoice is marked paid, but the corresponding audit journal row was missing, failing SOX compliance audits.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice audit logging statement is omitted or failing.

### Expected Behavior
Insert matching entry in `audit_journal` verifying invoice payment.

### Actual Behavior
Invoice status updated without journal ledger entry.

### Impact
SOX compliance violation leading to audit fines.

### Requirements
- Update invoice to `'paid'` and insert corresponding row into `audit_journal`.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE invoices (
    id INT PRIMARY KEY,
    amount DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE audit_journal (
    id INT PRIMARY KEY,
    invoice_id INT,
    action VARCHAR(50)
);

INSERT INTO invoices VALUES (1, 500.00, 'pending');"""
            },
            {
                'name': 'query.sql',
                'content': """UPDATE invoices SET status = 'paid' WHERE id = 1;
SELECT i.status, COUNT(a.id) AS journal_count FROM invoices i LEFT JOIN audit_journal a ON i.id = a.invoice_id WHERE i.id = 1 GROUP BY i.status;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Both invoice updated and audit journal written', 'input': '', 'expected': """UPDATE invoices SET status = 'paid' WHERE id = 1;
INSERT INTO audit_journal VALUES (1, 1, 'INVOICE_PAID');
SELECT i.status, COUNT(a.id) AS journal_count FROM invoices i LEFT JOIN audit_journal a ON i.id = a.invoice_id WHERE i.id = 1 GROUP BY i.status;"""}
        ],
        'bug_signature': "UPDATE invoices SET status = 'paid' WHERE id = 1;\nSELECT i.status",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `INSERT INTO audit_journal VALUES (1, 1, \'INVOICE_PAID\');`.'
        ],
        'topics': ['SQL', 'Audit Trail', 'Transactions'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL DML'],
        'status': 'published',
        'expected_query': """UPDATE invoices SET status = 'paid' WHERE id = 1;
INSERT INTO audit_journal VALUES (1, 1, 'INVOICE_PAID');
SELECT i.status, COUNT(a.id) AS journal_count FROM invoices i LEFT JOIN audit_journal a ON i.id = a.invoice_id WHERE i.id = 1 GROUP BY i.status;"""
    })

    # 80. A database migration incorrectly handles existing NULL and duplicate values
    challenges.append({
        'id': 80,
        'title': '[SQL-H05] A Database Migration Incorrectly Handles Existing NULL and Duplicate Values',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Schema',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A schema migration prepares to add a `NOT NULL` constraint and default value to a `user_settings.notification_email` column.

### Bug Report
Running `ALTER TABLE` crashes or produces corrupted profiles because existing rows contain `NULL` values!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe NULL values must be backfilled before adding constraints.

### Expected Behavior
Backfill existing `NULL` emails with `'no-reply@domain.com'` (or account fallback email).

### Actual Behavior
Leaves NULL values unmigrated.

### Impact
Failed database migrations during deployment causing production downtime.

### Requirements
- Update existing records with missing notification emails to a default fallback address prior to applying constraints.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE user_settings (
    id INT PRIMARY KEY,
    user_id INT,
    notification_email VARCHAR(100)
);

INSERT INTO user_settings VALUES
(1, 101, 'user1@test.com'),
(2, 102, NULL),
(3, 103, NULL);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, user_id, notification_email FROM user_settings ORDER BY id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Backfills NULL notification emails', 'input': '', 'expected': """UPDATE user_settings SET notification_email = 'no-reply@domain.com' WHERE notification_email IS NULL;
SELECT id, user_id, notification_email FROM user_settings ORDER BY id;"""}
        ],
        'bug_signature': 'UPDATE profiles SET country = (SELECT country FROM users WHERE id = profiles.user_id);',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `UPDATE user_settings SET notification_email = \'no-reply@domain.com\' WHERE notification_email IS NULL;` before SELECT.'
        ],
        'topics': ['SQL', 'Migrations', 'NULL Backfill'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Database Migrations'],
        'status': 'published',
        'expected_query': """UPDATE user_settings SET notification_email = 'no-reply@domain.com' WHERE notification_email IS NULL;
SELECT id, user_id, notification_email FROM user_settings ORDER BY id;"""
    })

    # 81. A running-total query produces incorrect results for tied timestamps
    challenges.append({
        'id': 81,
        'title': '[SQL-H06] A Running-Total Query Produces Incorrect Results for Tied Timestamps',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A financial ledger calculates account running balance after each transaction.

### Bug Report
When two transactions occur at the identical second (`2026-10-19 12:00:00`), the running total jumps ahead and shows the cumulative sum of BOTH transactions on the first row!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `SUM(amount) OVER (ORDER BY trans_time)`.
3. Default window frame for tied values groups peers together (`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`).

### Expected Behavior
Include `id` in `ORDER BY` OR specify `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` to process transactions strictly row by row.

### Actual Behavior
Tied timestamps cause peer grouping jump.

### Impact
Ledger audit mismatch during concurrent transactions.

### Requirements
- Use `ORDER BY trans_time, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE ledger (
    id INT PRIMARY KEY,
    amount DECIMAL(10,2),
    trans_time VARCHAR(20)
);

INSERT INTO ledger VALUES
(1, 100.00, '2026-10-19 12:00:00'),
(2, 50.00, '2026-10-19 12:00:00'),
(3, 25.00, '2026-10-19 13:00:00');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, amount, trans_time, SUM(amount) OVER (ORDER BY trans_time) AS running_balance FROM ledger ORDER BY id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Strict row-by-row running balance (100.00 then 150.00)', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'SUM(amount) OVER (ORDER BY trans_time) AS running_balance',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` to the `OVER()` clause.'
        ],
        'topics': ['SQL', 'Window Functions', 'Running Total', 'ROWS vs RANGE'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Window Frames'],
        'status': 'published',
        'expected_query': 'SELECT id, amount, trans_time, SUM(amount) OVER (ORDER BY trans_time, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_balance FROM ledger ORDER BY id;'
    })

    # 82. A reporting query uses incorrect isolation assumptions during concurrent updates
    challenges.append({
        'id': 82,
        'title': '[SQL-H07] A Reporting Query Uses Incorrect Isolation Assumptions During Concurrent Updates',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
An analytics query reports confirmed orders.

### Bug Report
The report includes half-completed cart checkout drafts that are in status `'draft'`, skewing daily performance metrics.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice missing status filter allows non-committed drafts into reporting tables.

### Expected Behavior
Filter strictly for confirmed, committed orders: `WHERE status = 'confirmed'`.

### Actual Behavior
Reads unconfirmed cart rows.

### Impact
Reports include abandoned carts as confirmed sales.

### Requirements
- Filter sales revenue calculations to reflect only confirmed orders.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    amount DECIMAL(10,2),
    status VARCHAR(20)
);

INSERT INTO orders VALUES
(1, 100.00, 'confirmed'),
(2, 50.00, 'draft'),
(3, 200.00, 'confirmed');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT SUM(amount) AS total_sales FROM orders;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Only confirmed orders summed', 'input': '', 'expected': 'Total sales amount for confirmed orders only'}
        ],
        'bug_signature': 'SELECT SUM(amount) AS total_sales FROM orders;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `WHERE status = \'confirmed\'`.'
        ],
        'topics': ['SQL', 'Isolation', 'Data Integrity'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Filtering'],
        'status': 'published',
        'expected_query': "SELECT SUM(amount) AS total_sales FROM orders WHERE status = 'confirmed';"
    })

    # 83. A soft-delete implementation leaks logically deleted records
    challenges.append({
        'id': 83,
        'title': '[SQL-H08] A Soft-Delete Implementation Leaks Logically Deleted Records',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A customer portal allows users to soft-delete archived documents (`deleted_at IS NOT NULL`).

### Bug Report
Soft-deleted documents continue to appear in search queries and public document listings!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice query omits `WHERE deleted_at IS NULL`.
3. Deleted records are returned.

### Expected Behavior
Filter strictly for active, non-deleted records: `WHERE deleted_at IS NULL`.

### Actual Behavior
Omits soft-delete check.

### Impact
Privacy violation: users see documents that were deleted by other administrators.

### Requirements
- Exclude logically deleted records from active customer listings and order by id.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE documents (
    id INT PRIMARY KEY,
    title VARCHAR(50),
    deleted_at VARCHAR(20)
);

INSERT INTO documents VALUES
(1, 'Public Specs', NULL),
(2, 'Deprecated Draft', '2026-10-15 10:00:00'),
(3, 'Security Policy', NULL);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, title FROM documents ORDER BY id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Only non-deleted documents returned', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'SELECT id, title FROM documents ORDER BY id;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `WHERE deleted_at IS NULL`.'
        ],
        'topics': ['SQL', 'Soft Deletes', 'Security'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Soft Delete Pattern'],
        'status': 'published',
        'expected_query': 'SELECT id, title FROM documents WHERE deleted_at IS NULL ORDER BY id;'
    })

    # 84. A recursive hierarchy query mishandles cycles
    challenges.append({
        'id': 84,
        'title': '[SQL-H09] A Recursive Hierarchy Query Mishandles Cycles',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A category hierarchy explorer queries nested product taxonomy trees.

### Bug Report
An invalid database relationship created a circular reference (Category A is parent of Category B, which is parent of Category A). The query runs infinitely until the database crashes with `RecursionError`!

### Steps to Reproduce
1. Execute recursive query on table with circular reference.
2. Query runs infinitely without depth bound.

### Expected Behavior
Add a depth boundary `WHERE depth < 5` to safeguard against infinite loops in recursive CTEs.

### Actual Behavior
No depth limiter.

### Impact
Database hangs and connection pool exhaustion.

### Requirements
- Add `AND depth < 5` (or `level < 5`) in the recursive step.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE categories (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    parent_id INT
);

INSERT INTO categories VALUES
(1, 'Tech', NULL),
(2, 'Computers', 1),
(3, 'Laptops', 2);"""
            },
            {
                'name': 'query.sql',
                'content': """WITH RECURSIVE cat_tree AS (
    SELECT id, name, parent_id, 1 AS depth FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id
)
SELECT id, name, depth FROM cat_tree ORDER BY depth, id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Hierarchy traversed safely with depth limit', 'input': '', 'expected': 'Complete hierarchical reporting structure'}
        ],
        'bug_signature': 'FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id\n)',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Ensure `WHERE ct.depth < 5` guards the recursive query step.'
        ],
        'topics': ['SQL', 'Recursive CTE', 'Cycles', 'Safety'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Recursive CTE Limits'],
        'status': 'published',
        'expected_query': """WITH RECURSIVE cat_tree AS (
    SELECT id, name, parent_id, 1 AS depth FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id
    WHERE ct.depth < 5
)
SELECT id, name, depth FROM cat_tree ORDER BY depth, id;"""
    })

    # 85. An analytics query becomes extremely slow because of incorrect query structure and indexing assumptions
    challenges.append({
        'id': 85,
        'title': '[SQL-H10] An Analytics Query Becomes Extremely Slow Because of Incorrect Query Structure and Indexing Assumptions',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Performance',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Company Scenario
A customer metrics query finds all customers who have placed an order in the last 30 days.

### Bug Report
The query uses `IN (SELECT customer_id FROM orders)` on millions of rows, causing a full table scan and locking the database.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice un-indexed `IN (SELECT ...)` subquery.

### Expected Behavior
Use `EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` or an indexed `INNER JOIN`.

### Actual Behavior
Slow correlated `IN` subquery.

### Impact
Query timeouts across executive reporting portals.

### Requirements
- Optimize the query using a semi-join or existence check rather than an unindexed full table join.
""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2)
);

INSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie');
INSERT INTO orders VALUES (101, 1, 50.00), (102, 2, 75.00);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT c.id, c.name FROM customers c WHERE c.id IN (SELECT o.customer_id FROM orders o) ORDER BY c.id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Efficient EXISTS returns Alice and Bob', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'WHERE c.id IN (SELECT o.customer_id FROM orders o)',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Ensure `EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` is used.'
        ],
        'topics': ['SQL', 'Query Optimization', 'EXISTS vs IN', 'Performance'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Optimization'],
        'status': 'published',
        'expected_query': 'SELECT c.id, c.name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY c.id;'
    })

    return challenges
