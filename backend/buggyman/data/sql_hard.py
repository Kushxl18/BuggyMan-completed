"""
SQL Lab: Hard Challenges (76 to 85)
Standardized into realistic production incident debugging tickets.
"""

def get_sql_hard():
    challenges = []

    # 76. Concurrent inventory reservations oversell stock
    challenges.append({
        'id': 76,
        'title': 'Warehouse Reservation Allows Negative Stock Count',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Concurrency',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A warehouse supervisor reported that high-demand game console inventory showed a stock level of -1, leading to physical stockouts during order fulfillment."

### Bug Report
The reservation update query decrements inventory unconditionally without verifying that remaining stock is strictly positive, causing inventory counts to become negative.

### Steps to Reproduce
1. Ingest an inventory item with `stock = 0`.
2. Execute `query.sql`.
3. Inspect the updated stock count.
4. Observe that stock was decremented below zero.

### Expected Behaviour
Update stock only when `stock >= 1`: `UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1;`.

### Actual Behaviour
The update executes without a guard on available quantity, allowing inventory to drop to negative values.

### Starter Files
`query.sql` - Reserves inventory items and selects the updated inventory state.
`schema.sql` - Warehouse inventory table and initial stock balances.

### Task
Add a guard condition to the `UPDATE` statement in `query.sql` to prevent decrements when stock is depleted.

### Acceptance Criteria
1. Modifies inventory only if current stock is at least 1.
2. Selects `id`, `name`, `stock` for the target inventory record.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Inventory stock must never become negative.
- Output columns: `id`, `name`, `stock`.""",
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
            {'id': 1, 'name': 'Guarded update only decrements when stock available', 'input': '', 'expected': """UPDATE inventory SET stock = stock - 1 WHERE id = 10 AND stock >= 1;
SELECT id, name, stock FROM inventory WHERE id = 10;"""}
        ],
        'bug_signature': 'UPDATE inventory SET stock = stock - 1 WHERE id = 10;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Consider optimistic concurrency control: an update should only succeed if the current state satisfies availability preconditions.',
            'Look at the WHERE clause of the UPDATE statement. Currently it only filters by record ID without checking whether remaining stock is positive.',
            'Append a condition checking that stock is at least 1 (e.g. `AND stock >= 1`) so that out-of-stock items are not decremented.'
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
        'title': 'Direct Transfer Drops Funds During Partial Write Failure',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A customer transferring funds between accounts reported their money vanished because the transaction deducted their balance without crediting the destination account."

### Bug Report
The transfer query executes balance updates across accounts without atomic safeguards, deducting funds from the sender even when the recipient account ID is invalid.

### Steps to Reproduce
1. Ingest sender account with balance $100 and recipient account with invalid ID 999.
2. Execute `query.sql`.
3. Inspect account balances.
4. Observe that sender balance was reduced while destination credit failed.

### Expected Behaviour
Deduct funds from the sender only if balance is sufficient, and credit the valid recipient account (ID 2).

### Actual Behaviour
The script deducts funds from the sender while attempting to credit a non-existent destination account.

### Starter Files
`query.sql` - Performs fund transfers between accounts and selects updated balances.
`schema.sql` - Account balances and owner identities.

### Task
Update `query.sql` to ensure sufficient sender balance and credit the valid recipient account (ID 2).

### Acceptance Criteria
1. Sender balance decrements only when `balance >= 50`.
2. Valid recipient (ID 2) balance increments by 50.
3. Selects `id`, `owner`, `balance` ordered by `id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Preserves total ledger balance integrity.
- Ordered by `id` ascending.""",
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
            {'id': 1, 'name': 'Balances reflect successful atomic transfer', 'input': '', 'expected': """UPDATE accounts SET balance = balance - 50 WHERE id = 1 AND balance >= 50;
UPDATE accounts SET balance = balance + 50 WHERE id = 2;
SELECT id, owner, balance FROM accounts ORDER BY id;"""}
        ],
        'bug_signature': 'WHERE id = 999;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Financial ledger operations must ensure both sides of the transfer match valid entity keys and balance constraints.',
            'Examine the recipient ID in the credit UPDATE statement and check whether the debit ensures sufficient funds exist.',
            'Update the debit query to verify `AND balance >= 50` on account 1, and direct the credit update to valid recipient `WHERE id = 2`.'
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
        'title': 'Customer Summary Query Multiplies Order and Ticket Totals',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A customer success manager found that customer profile summaries reported three times their actual lifetime order spend and double their real ticket count."

### Bug Report
Joining multiple independent one-to-many child tables (orders and tickets) produces a cartesian product of rows, inflating aggregate sums and counts.

### Steps to Reproduce
1. Ingest customer Alice with 2 orders and 3 support tickets.
2. Execute `query.sql`.
3. Compare reported `total_spent` and `total_tickets` against actual customer totals.
4. Observe that aggregates are multiplied by the row count of the other joined table.

### Expected Behaviour
Aggregate orders and support tickets independently in subqueries or CTEs before joining to the customer record.

### Actual Behaviour
Direct concurrent joins generate cross-product row duplication prior to grouping.

### Starter Files
`query.sql` - Generates customer overview metrics combining spend and support tickets.
`schema.sql` - Customers, orders, and customer support tickets.

### Task
Refactor `query.sql` to aggregate child tables independently before joining to customers.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `total_spent`, `total_tickets`.
2. Calculates exact order spend and ticket count without cross-product multiplication.
3. Unset metrics default safely to 0.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Avoids row explosion across multiple one-to-many relationships.
- Column aliases: `id`, `name`, `total_spent`, `total_tickets`.""",
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
            {'id': 1, 'name': 'Independent aggregation reports total_spent=150, tickets=3', 'input': '', 'expected': 'All registered users preserving unassigned plans as NULL'}
        ],
        'bug_signature': 'LEFT JOIN orders o ON c.id = o.customer_id\nLEFT JOIN tickets t',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Joining two separate one-to-many child tables to the same parent table creates a Cartesian product across the child rows.',
            'Compute aggregates for orders and tickets in separate queries or Common Table Expressions (CTEs) before joining them.',
            'Define `WITH o_summary AS (...)` and `WITH t_summary AS (...)` grouping by `customer_id`, then join both to `customers` with `COALESCE`.'
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
        'title': 'Settled Invoice Workflow Omits Audit Journal Entry',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"A financial compliance audit failed because invoice settlements showed as paid in the database without any corresponding entry in the immutable audit journal."

### Bug Report
The invoice settlement workflow updates the invoice status to paid but fails to insert a corresponding audit journal entry recording the payment action.

### Steps to Reproduce
1. Ingest invoice record with status `'pending'`.
2. Execute `query.sql`.
3. Inspect `audit_journal` entries for the invoice.
4. Observe that no audit record was generated for the payment.

### Expected Behaviour
Update invoice status to `'paid'` and insert an immutable audit journal record `(1, 1, 'INVOICE_PAID')`.

### Actual Behaviour
The query mutates status without generating an audit trail entry.

### Starter Files
`query.sql` - Marks invoices paid and queries payment status with journal counts.
`schema.sql` - Invoices and audit journal tables.

### Task
Add the missing journal insertion to `query.sql`.

### Acceptance Criteria
1. Updates invoice status to `'paid'`.
2. Inserts audit record `(1, 1, 'INVOICE_PAID')` into `audit_journal`.
3. Selects `i.status`, `journal_count`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Preserves audit compliance journal tracking.
- Output columns: `status`, `journal_count`.""",
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
            {'id': 1, 'name': 'Both invoice updated and audit journal written', 'input': '', 'expected': """UPDATE invoices SET status = 'paid' WHERE id = 1;
INSERT INTO audit_journal VALUES (1, 1, 'INVOICE_PAID');
SELECT i.status, COUNT(a.id) AS journal_count FROM invoices i LEFT JOIN audit_journal a ON i.id = a.invoice_id WHERE i.id = 1 GROUP BY i.status;"""}
        ],
        'bug_signature': "UPDATE invoices SET status = 'paid' WHERE id = 1;\nSELECT i.status",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Financial compliance operations require that every status transition is paired with an immutable journal entry.',
            'Look at the verification query: it expects `journal_count` to reflect an entry in `audit_journal` for invoice 1.',
            'Add `INSERT INTO audit_journal VALUES (1, 1, \'INVOICE_PAID\');` immediately following the invoice UPDATE statement.'
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
        'title': 'Settings Migration Fails on Unmigrated Missing Emails',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Schema',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"An automated email notification dispatch service crashed during overnight processing because legacy user settings records contained NULL notification email addresses."

### Bug Report
The settings migration script queries user settings without backfilling missing notification emails with a valid system fallback address.

### Steps to Reproduce
1. Ingest user settings records containing unpopulated (`NULL`) notification emails.
2. Execute `query.sql`.
3. Inspect returned notification emails.
4. Observe that records with `NULL` email remain unpopulated.

### Expected Behaviour
Backfill unpopulated notification emails with `'no-reply@domain.com'` before selecting all records ordered by `id`.

### Actual Behaviour
Records with `NULL` email addresses remain unmodified, causing downstream mailer exceptions.

### Starter Files
`query.sql` - Migrates and selects user notification email preferences.
`schema.sql` - User settings table and notification preference records.

### Task
Add an `UPDATE` statement in `query.sql` to backfill `NULL` notification emails with `'no-reply@domain.com'`.

### Acceptance Criteria
1. Backfills `NULL` notification emails with `'no-reply@domain.com'`.
2. Selects `id`, `user_id`, `notification_email` ordered by `id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Backfill fallback value: `'no-reply@domain.com'`.
- Ordered by `id` ascending.""",
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
            {'id': 1, 'name': 'Backfills NULL notification emails', 'input': '', 'expected': """UPDATE user_settings SET notification_email = 'no-reply@domain.com' WHERE notification_email IS NULL;
SELECT id, user_id, notification_email FROM user_settings ORDER BY id;"""}
        ],
        'bug_signature': '',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Applying NOT NULL constraints to legacy tables requires backfilling default values for all existing NULL entries first.',
            'Identify which records have missing emails using `WHERE notification_email IS NULL`.',
            'Prepend an `UPDATE user_settings SET notification_email = \'no-reply@domain.com\' WHERE notification_email IS NULL;` before the SELECT.'
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
        'title': 'Ledger Running Balance Jumps on Tied Transaction Timestamps',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Accounting reconciliations showed erratic running balances where accounts with transactions occurring in the same second displayed identical jumped balances rather than sequential updates."

### Bug Report
The running balance window function orders strictly by transaction timestamp without a unique tie-breaker, causing tied transactions to be aggregated into identical jumped totals.

### Steps to Reproduce
1. Ingest ledger transactions where multiple entries share the exact same `trans_time`.
2. Execute `query.sql`.
3. Inspect the computed `running_balance` for tied transactions.
4. Observe that tied entries report identical peer totals rather than sequential progressive balances.

### Expected Behaviour
Include `id` as a deterministic secondary tie-breaker in the window clause: `SUM(amount) OVER (ORDER BY trans_time, id) AS running_balance`.

### Actual Behaviour
Tied timestamps group row evaluations together in the window frame, skipping progressive updates.

### Starter Files
`query.sql` - Computes progressive running balances across ledger entries.
`schema.sql` - Financial ledger transactions and timestamps.

### Task
Add `id` to the `ORDER BY` specification inside the window function in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `amount`, `trans_time`, `running_balance`.
2. Progressive running balance advances sequentially on tied timestamps.
3. Output ordered by `id`.

### Constraints
- Target Database: SQLite 3.35+ with Window Function support.
- Output column alias: `running_balance`.
- Deterministic progressive window accumulation.""",
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
            {'id': 1, 'name': 'Strict row-by-row running balance (100.00 then 150.00)', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'SUM(amount) OVER (ORDER BY trans_time) AS running_balance',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In standard SQL, window ordering without a frame clause defaults to RANGE mode, which aggregates tied order values together.',
            'To calculate a true running total for every row, break ties deterministically and switch from RANGE to ROWS framing.',
            'Specify `ORDER BY trans_time, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` inside the `OVER(...)` clause.'
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
        'title': 'Revenue Summary Mistakenly Aggregates Uncommitted Draft Carts',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Transactions',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Executive revenue reports included abandoned shopping cart drafts as confirmed company sales, distorting financial forecasts."

### Bug Report
The sales summary query aggregates order amounts without filtering out unconfirmed draft orders, counting non-finalized shopping carts toward total sales.

### Steps to Reproduce
1. Ingest orders with statuses `confirmed` and `draft`.
2. Execute `query.sql`.
3. Compare the reported `total_sales` against finalized order receipts.
4. Observe that uncommitted draft orders contribute to the total sales volume.

### Expected Behaviour
Filter orders strictly by `status = 'confirmed'`: `SELECT SUM(amount) AS total_sales FROM orders WHERE status = 'confirmed';`.

### Actual Behaviour
Draft carts are included in the sales aggregation, inflating revenue metrics.

### Starter Files
`query.sql` - Computes total gross sales from customer orders.
`schema.sql` - Order records and order statuses.

### Task
Add a `WHERE status = 'confirmed'` filter to `query.sql`.

### Acceptance Criteria
1. Projected column: `total_sales`.
2. Draft orders are excluded from the calculated sum.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column alias: `total_sales`.
- Strict status qualification.""",
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
            {'id': 1, 'name': 'Only confirmed orders summed', 'input': '', 'expected': 'Total sales amount for confirmed orders only'}
        ],
        'bug_signature': 'SELECT SUM(amount) AS total_sales FROM orders;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Business financial reporting must always isolate committed transactional records from temporary workflow states.',
            'Review the columns of the `orders` table to identify which field tracks order lifecycle state.',
            'Add `WHERE status = \'confirmed\'` to the query to restrict the calculation to completed purchases.'
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
        'title': 'Archived Customer Documents Surface in Active Document Search',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"Legal counsel reported that superseded and soft-deleted contract drafts were appearing in active customer document searches."

### Bug Report
The document retrieval query selects document records without filtering on the soft-delete timestamp, displaying archived and deleted files to users.

### Steps to Reproduce
1. Ingest documents where active files have `deleted_at = NULL` and deleted files have timestamps.
2. Execute `query.sql`.
3. Inspect returned document titles.
4. Observe that soft-deleted documents appear in the active search results.

### Expected Behaviour
Filter documents to include only active records where `deleted_at IS NULL`, ordered by `id`.

### Actual Behaviour
Soft-deleted documents are returned alongside active documents.

### Starter Files
`query.sql` - Retrieves active customer documents from storage.
`schema.sql` - Document metadata and soft-delete timestamps.

### Task
Add a `WHERE deleted_at IS NULL` condition in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `title`.
2. Only records with `deleted_at IS NULL` are returned.
3. Ordered by `id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Excludes soft-deleted records.
- Ordered by `id` ascending.""",
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
            {'id': 1, 'name': 'Only non-deleted documents returned', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'SELECT id, title FROM documents ORDER BY id;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In soft-delete schemas, records are marked as removed using a timestamp column rather than being physically deleted.',
            'Check which column indicates deletion state and what value it holds for active records.',
            'Add `WHERE deleted_at IS NULL` before the `ORDER BY id` clause to filter out archived documents.'
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
        'title': 'Recursive Category Navigation Causes Unbounded CTE Loop',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"The category tree service caused runaway database query timeouts because an unconstrained recursive CTE traversed cyclical category links without a depth limit."

### Bug Report
The recursive category hierarchy query lacks a recursion depth guard, risking infinite recursive query execution on cyclical parent-child relationships.

### Steps to Reproduce
1. Ingest hierarchical category records with parent-child links.
2. Execute `query.sql`.
3. Inspect the recursive query structure.
4. Observe that recursive traversal lacks a termination depth guard.

### Expected Behaviour
Enforce a recursion depth boundary: `WHERE ct.depth < 10` in the recursive CTE member.

### Actual Behaviour
The recursive union lacks a depth guard, permitting runaway execution on circular links.

### Starter Files
`query.sql` - Recursively builds category hierarchy trees with depth metrics.
`schema.sql` - Category records and hierarchical parent links.

### Task
Add a `WHERE ct.depth < 10` recursion guard to the recursive query in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `depth`.
2. Enforces maximum recursion depth of 10.
3. Ordered by `depth, id`.

### Constraints
- Target Database: SQLite 3.35+ with Recursive CTE support.
- Maximum recursion depth: 10.
- Result ordering: `depth, id`.""",
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
            {'id': 1, 'name': 'Hierarchy traversed safely with depth limit', 'input': '', 'expected': 'Complete hierarchical reporting structure'}
        ],
        'bug_signature': 'FROM categories c JOIN cat_tree ct ON c.parent_id = ct.id\n)',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Recursive CTEs that traverse graph structures require a termination condition or max-depth guard to prevent infinite loops from circular references.',
            'Look at the recursive query term after `UNION ALL`: it increments `depth` by 1 at each iteration.',
            'Add `WHERE ct.depth < 5` to the recursive SELECT statement to enforce a safe upper depth limit.'
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
        'title': 'Customer Activity Query Scans Full Orders Table',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Performance',
        'time_estimate': '25 mins',
        'points': 250,
        'description': """### Incident Report
"The customer activity monitoring dashboard experienced severe query latency during peak hours because the subquery triggered a full table scan across millions of order records."

### Bug Report
The customer activity query uses an unindexed `IN (SELECT customer_id FROM orders)` pattern that materializes subquery results rather than using an efficient correlated `EXISTS` check.

### Steps to Reproduce
1. Ingest customer records and associated order transaction history.
2. Execute `query.sql`.
3. Analyze execution plan and subquery structure.
4. Observe that the subquery materializes all order customer IDs rather than performing early-exit existence verification.

### Expected Behaviour
Use correlated `EXISTS` for optimal short-circuiting: `SELECT c.id, c.name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY c.id;`.

### Actual Behaviour
The `IN` subquery scans and materializes the entire foreign key column.

### Starter Files
`query.sql` - Filters active purchasing customers using subquery evaluation.
`schema.sql` - Customer records and order activity.

### Task
Refactor the subquery in `query.sql` from `IN` to a correlated `EXISTS` clause.

### Acceptance Criteria
1. Projected columns: `c.id`, `c.name`.
2. Uses `WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)`.
3. Ordered by `c.id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Short-circuit existence verification via `EXISTS`.
- Ordered by `c.id` ascending.""",
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
            {'id': 1, 'name': 'Efficient EXISTS returns Alice and Bob', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'WHERE c.id IN (SELECT o.customer_id FROM orders o)',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Correlated existence checks allow the database engine to short-circuit upon finding the first matching record rather than collecting all values.',
            'Replace the `IN` subquery with an `EXISTS` predicate that links the inner and outer customer identifiers.',
            'Change the predicate to `WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` while maintaining the order by clause.'
        ],
        'topics': ['SQL', 'Query Optimization', 'EXISTS vs IN', 'Performance'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Optimization'],
        'status': 'published',
        'expected_query': 'SELECT c.id, c.name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY c.id;'
    })

    return challenges
