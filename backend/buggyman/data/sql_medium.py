"""
SQL Lab: Medium Challenges (61 to 75)
"""

def get_sql_medium():
    challenges = []

    # 61. Customer revenue report multiplied by order line items join
    challenges.append({
        'id': 61,
        'title': 'Customer Revenue Report Multiplied by Order Line Items Join',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A sales manager reported that top customer accounts showed inflated revenue totals that were multiples of actual customer invoice receipts."

### Bug Report
Joining the orders table with order line items duplicates order records for each item row, multiplying order revenue sums during aggregation.

### Steps to Reproduce
1. Populate orders where an order has multiple associated line items.
2. Execute `query.sql`.
3. Compare customer revenue against distinct order amounts.
4. Observe that orders with multiple line items are summed multiple times.

### Expected Behaviour
Calculate total customer revenue without multiplying order amounts: `SELECT o.customer_id, SUM(o.total_amount) AS revenue FROM orders o GROUP BY o.customer_id ORDER BY o.customer_id;`.

### Actual Behaviour
Unnecessary joins against line items duplicate parent order rows prior to summing.

### Starter Files
`query.sql` - Computes customer revenue summaries.
`schema.sql` - Order headers and line-item details.

### Task
Refactor `query.sql` to aggregate customer revenue accurately without row multiplication.

### Acceptance Criteria
1. Projected columns: `customer_id`, `revenue`.
2. Multi-item orders are counted exactly once per order.
3. Rows are ordered by `customer_id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Grouped by `customer_id`.
- Result ordering by `customer_id` ascending.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    total_amount DECIMAL(10,2)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(50)
);

INSERT INTO orders VALUES (1, 10, 100.00), (2, 20, 50.00);
INSERT INTO order_items VALUES (1, 1, 'Book A'), (2, 1, 'Book B'), (3, 2, 'Pen');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT o.customer_id, SUM(o.total_amount) AS revenue FROM orders o JOIN order_items i ON o.id = i.order_id GROUP BY o.customer_id ORDER BY o.customer_id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Accurate customer revenue without join duplication', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'JOIN order_items i ON o.id = i.order_id GROUP BY o.customer_id',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Joining a one-to-many relationship multiplies rows in the parent table before aggregation occurs.',
            'Examine whether `order_items` is actually needed if `orders` already contains `total_amount`.',
            'Query `orders` directly without joining `order_items`: `SELECT customer_id, SUM(total_amount) AS revenue FROM orders GROUP BY customer_id ORDER BY customer_id;`.'
        ],
        'topics': ['SQL', 'Joins', 'Aggregation', 'Cartesian Product'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins and Grouping'],
        'status': 'published',
        'expected_query': 'SELECT customer_id, SUM(total_amount) AS revenue FROM orders GROUP BY customer_id ORDER BY customer_id;'
    })

    # 62. Average order value metrics distorted by day-level aggregation
    challenges.append({
        'id': 62,
        'title': 'Average Order Value Metrics Distorted by Day-Level Aggregation',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Data analysts noticed that customer Average Order Value (AOV) metrics on the executive dashboard displayed astronomical figures that matched customer lifetime spend."

### Bug Report
The AOV query sums customer order amounts instead of calculating the arithmetic mean, misreporting total spend as average order value.

### Steps to Reproduce
1. Ingest customer order records with multiple transactions per customer.
2. Execute `query.sql`.
3. Compare the reported `aov` against actual average transaction size.
4. Observe that `aov` equals total spend rather than average per order.

### Expected Behaviour
Calculate average order value per customer: `SELECT customer_id, AVG(amount) AS aov FROM orders GROUP BY customer_id ORDER BY customer_id;`.

### Actual Behaviour
`SUM(amount)` is aliased as `aov`, conflating cumulative spend with average order size.

### Starter Files
`query.sql` - Computes Average Order Value (AOV) per customer.
`schema.sql` - Customer order transaction history.

### Task
Use the `AVG()` aggregate function in `query.sql` to compute average order values.

### Acceptance Criteria
1. Projected columns: `customer_id`, `aov`.
2. Accurately calculates mean transaction amount per customer.
3. Ordered by `customer_id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column alias: `aov`.
- Result sorted by `customer_id` ascending.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2)
);

INSERT INTO orders VALUES
(1, 1, 100.00),
(2, 1, 20.00),
(3, 1, 30.00),
(4, 2, 50.00);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT customer_id, SUM(amount) AS aov FROM orders GROUP BY customer_id ORDER BY customer_id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'True average order value per customer', 'input': '', 'expected': 'Average metric correctly computed per group'}
        ],
        'bug_signature': 'SELECT customer_id, SUM(amount) AS aov FROM orders',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Average Order Value measures the mean transaction size per customer rather than cumulative total spend.',
            'Check the aggregate function used in the SELECT clause of `query.sql`.',
            'Replace `SUM(amount)` with `ROUND(AVG(amount), 2) AS aov`.'
        ],
        'topics': ['SQL', 'Aggregation', 'AVG'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Averages'],
        'status': 'published',
        'expected_query': 'SELECT customer_id, ROUND(AVG(amount), 2) AS aov FROM orders GROUP BY customer_id ORDER BY customer_id;'
    })

    # 63. Audit log pagination displays duplicate events across pages
    challenges.append({
        'id': 63,
        'title': 'Audit Log Pagination Displays Duplicate Events Across Pages',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Compliance security officers inspecting audit trails reported that events displayed on page 1 were repeated on page 2 when events shared identical timestamps."

### Bug Report
The audit log pagination query lacks a deterministic secondary tie-breaker, causing events with identical timestamps to shift unpredictably between paginated windows.

### Steps to Reproduce
1. Ingest audit log events sharing identical timestamp values.
2. Execute `query.sql` for page 1 (`LIMIT 2 OFFSET 0`).
3. Inspect record ordering.
4. Observe that ordering is non-deterministic for identical timestamps.

### Expected Behaviour
Order audit logs deterministically by `created_at ASC, id ASC LIMIT 2 OFFSET 0`.

### Actual Behaviour
Single-column sorting allows arbitrary order resolution among tied timestamps.

### Starter Files
`query.sql` - Paginates system security audit logs.
`schema.sql` - System security audit trail events.

### Task
Add `id ASC` as a secondary sorting tie-breaker in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `event`, `created_at`.
2. Deterministically ordered by `created_at ASC, id ASC`.
3. Returns first 2 paginated records.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Pagination parameters: `LIMIT 2 OFFSET 0`.
- Deterministic tie-breaking by primary key.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE audit_logs (
    id INT PRIMARY KEY,
    event VARCHAR(50),
    created_at VARCHAR(20)
);

INSERT INTO audit_logs VALUES
(4, 'Login', '2026-10-19 10:00:00'),
(2, 'Logout', '2026-10-19 10:00:00'),
(1, 'Password Reset', '2026-10-19 10:00:00'),
(3, 'Login', '2026-10-19 10:00:00');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, event, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 2 OFFSET 0;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Deterministic sort with id tie-breaker', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'ORDER BY created_at DESC LIMIT 2 OFFSET 0;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Relational databases do not guarantee deterministic order for duplicate sort keys unless a unique column is included in the ORDER BY.',
            'Examine the ORDER BY clause in `query.sql`.',
            'Append `, id ASC` to `ORDER BY created_at DESC` to guarantee stable pagination.'
        ],
        'topics': ['SQL', 'Pagination', 'Deterministic Ordering'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL LIMIT and OFFSET'],
        'status': 'published',
        'expected_query': 'SELECT id, event, created_at FROM audit_logs ORDER BY created_at DESC, id ASC LIMIT 2 OFFSET 0;'
    })

    # 64. Regional sales leaderboard ranks executives across mixed regions
    challenges.append({
        'id': 64,
        'title': 'Regional Sales Leaderboard Ranks Executives Across Mixed Regions',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"European sales reps complained that their regional leaderboard ranked APAC executives above them instead of ranking representatives within each respective sales region."

### Bug Report
The sales representative ranking query calculates global sales ranks across all regions combined rather than partitioning rankings per sales territory.

### Steps to Reproduce
1. Ingest sales reps across multiple regions (`EMEA`, `APAC`).
2. Execute `query.sql`.
3. Inspect regional rank numbers for each territory.
4. Observe that rankings span across regions rather than restarting within each territory.

### Expected Behaviour
Calculate sales ranks partitioned by territory: `RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS regional_rank`.

### Actual Behaviour
The window function omits regional partitioning, producing a global leaderboard.

### Starter Files
`query.sql` - Ranks sales performance partitioned by region.
`schema.sql` - Sales representatives and regional revenue.

### Task
Partition the window function in `query.sql` by `region`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `region`, `revenue`, `regional_rank`.
2. Ranks reset to 1 within each distinct region.
3. Ordered by `region`, `regional_rank`.

### Constraints
- Target Database: SQLite 3.35+ with Window Function support.
- Partitioned by `region` and ordered by `revenue DESC`.
- Output ordering: `region, regional_rank`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE sales_reps (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    region VARCHAR(20),
    revenue DECIMAL(10,2)
);

INSERT INTO sales_reps VALUES
(1, 'Alice', 'EMEA', 50000.00),
(2, 'Bob', 'EMEA', 70000.00),
(3, 'Charlie', 'APAC', 60000.00),
(4, 'Diana', 'APAC', 90000.00);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, region, revenue, RANK() OVER (ORDER BY revenue DESC) AS regional_rank FROM sales_reps ORDER BY region, regional_rank;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Regional partition ranks top rep in each region as #1', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'RANK() OVER (ORDER BY revenue DESC) AS regional_rank',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Window functions require a PARTITION BY clause to break down calculations into distinct subset groupings.',
            'Look inside the `OVER (...)` clause in `query.sql`.',
            'Insert `PARTITION BY region` before `ORDER BY revenue DESC`.'
        ],
        'topics': ['SQL', 'Window Functions', 'RANK', 'PARTITION BY'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Window Functions'],
        'status': 'published',
        'expected_query': 'SELECT id, name, region, revenue, RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS regional_rank FROM sales_reps ORDER BY region, regional_rank;'
    })

    # 65. Monthly payment grouping misattributes midnight UTC renewals
    challenges.append({
        'id': 65,
        'title': 'Monthly Payment Grouping Misattributes Midnight UTC Renewals',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"A financial auditor noted that payments processed across different years were merged into identical monthly totals because aggregation extracted only calendar month digits."

### Bug Report
The recurring revenue grouping extracts two-digit month strings (`MM`) without year context (`YYYY-MM`), conflating revenue across multiple calendar years into single buckets.

### Steps to Reproduce
1. Ingest payment records spanning multiple calendar months.
2. Execute `query.sql`.
3. Inspect the `month` column output.
4. Observe that month identifiers lack full year-month formatting.

### Expected Behaviour
Group payments by standardized year-month strings (`YYYY-MM`): `strftime('%Y-%m', payment_date) AS month`.

### Actual Behaviour
Substring extraction isolates month digits without year qualification.

### Starter Files
`query.sql` - Aggregates recurring payments by calendar month.
`schema.sql` - Payment transactions and timestamps.

### Task
Update grouping in `query.sql` to aggregate by year and month (`YYYY-MM`).

### Acceptance Criteria
1. Projected columns: `month`, `total`.
2. Formatted as `YYYY-MM`.
3. Grouped and ordered by `month`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Month format: `YYYY-MM`.
- Output column aliases: `month`, `total`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE payments (
    id INT PRIMARY KEY,
    amount DECIMAL(10,2),
    payment_date VARCHAR(25)
);

INSERT INTO payments VALUES
(1, 100.00, '2026-09-01 00:30:00'),
(2, 200.00, '2026-09-15 12:00:00'),
(3, 150.00, '2026-10-01 10:00:00');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT substr(payment_date, 6, 2) AS month, SUM(amount) AS total FROM payments GROUP BY month ORDER BY month;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Grouped by YYYY-MM formatted month', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'substr(payment_date, 6, 2) AS month',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Deriving date buckets via manual string substrings breaks across year boundaries.',
            'SQL includes built-in datetime formatting functions like `strftime` for extracting date components.',
            'Use `strftime(\'%Y-%m\', payment_date) AS month` and group by month.'
        ],
        'topics': ['SQL', 'Dates', 'strftime'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Datetime Functions'],
        'status': 'published',
        'expected_query': "SELECT strftime('%Y-%m', payment_date) AS month, SUM(amount) AS total FROM payments GROUP BY month ORDER BY month;"
    })

    # 66. Free tier accounts filtered out of customer directory by WHERE clause
    challenges.append({
        'id': 66,
        'title': 'Free Tier Accounts Filtered Out of Customer Directory by WHERE Clause',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Customer success managers noticed that free-tier users without active subscriptions were completely missing from the user account directory."

### Bug Report
Filtering subscriptions in the `WHERE` clause converts an outer join into an inner join, eliminating users who do not have an active subscription.

### Steps to Reproduce
1. Populate users where some users hold active subscriptions and others hold no subscriptions.
2. Execute `query.sql`.
3. Inspect the returned user list.
4. Observe that users without subscriptions are omitted from the results.

### Expected Behaviour
Retain all users, displaying their active subscription plan or `NULL` if not subscribed: `LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'`.

### Actual Behaviour
Post-join `WHERE s.status = 'active'` drops users whose left-join subscription columns are null.

### Starter Files
`query.sql` - Generates user roster joined with active subscription details.
`schema.sql` - User accounts and subscription plans.

### Task
Move subscription status filtering from the `WHERE` clause into the `LEFT JOIN` condition in `query.sql`.

### Acceptance Criteria
1. Projected columns: `u.id`, `u.name`, `s.plan_name`.
2. Users without active plans show `NULL` for `plan_name`.
3. Ordered by `u.id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Preserves all registered users.
- Ordered by `u.id`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE subscriptions (
    id INT PRIMARY KEY,
    user_id INT,
    plan_name VARCHAR(50),
    status VARCHAR(20)
);

INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO subscriptions VALUES (101, 1, 'Pro Plan', 'active');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT u.id, u.name, s.plan_name FROM users u LEFT JOIN subscriptions s ON u.id = s.user_id WHERE s.status = 'active' ORDER BY u.id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Preserves Bob with NULL plan_name', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': "LEFT JOIN subscriptions s ON u.id = s.user_id WHERE s.status = 'active'",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Placing a filter on the right table in a WHERE clause filters out NULL rows produced by a LEFT JOIN, turning it into an INNER JOIN.',
            'Conditions placed in the ON clause dictate what rows are joined, whereas WHERE filters the entire combined result set.',
            'Move `AND s.status = \'active\'` into the `ON` clause and remove the `WHERE` clause.'
        ],
        'topics': ['SQL', 'Joins', 'LEFT JOIN', 'WHERE vs ON'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins'],
        'status': 'published',
        'expected_query': "SELECT u.id, u.name, s.plan_name FROM users u LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active' ORDER BY u.id;"
    })

    # 67. Unreserved warehouse inventory displays NULL availability
    challenges.append({
        'id': 67,
        'title': 'Unreserved Warehouse Inventory Displays NULL Availability',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Warehouse pickers reported that stock availability screens displayed blank empty values for items that had zero active customer reservations."

### Bug Report
Subtracting `NULL` reserved stock directly from physical inventory produces `NULL` availability rather than treating unset reservations as zero.

### Steps to Reproduce
1. Inspect inventory items where `reserved_stock` is unpopulated (`NULL`).
2. Execute `query.sql`.
3. Inspect the computed `available_stock` column.
4. Observe that availability displays as `NULL` instead of available physical inventory.

### Expected Behaviour
Coalesce unset reservations to zero during availability calculations: `(physical_stock - COALESCE(reserved_stock, 0)) AS available_stock`.

### Actual Behaviour
Direct arithmetic with `NULL` propagates null values to the calculated balance.

### Starter Files
`query.sql` - Calculates net available warehouse stock.
`schema.sql` - Warehouse inventory and reserved quantities.

### Task
Add null coalescing to `reserved_stock` in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `available_stock`.
2. Items with `NULL` reservations correctly report full physical stock.
3. Ordered by `id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column alias: `available_stock`.
- Result sorted by `id` ascending.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE inventory (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    physical_stock INT,
    reserved_stock INT
);

INSERT INTO inventory VALUES
(1, 'Laptop', 10, 2),
(2, 'Keyboard', 25, NULL),
(3, 'Monitor', 5, 5);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, (physical_stock - reserved_stock) AS available_stock FROM inventory ORDER BY id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Keyboard shows available_stock = 25', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': '(physical_stock - reserved_stock) AS available_stock',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In SQL arithmetic expressions, any number operated on with NULL results in NULL (e.g. `25 - NULL = NULL`).',
            'Use a null-coalescing function to substitute a default numerical value of zero.',
            'Wrap `reserved_stock` in `COALESCE(reserved_stock, 0)`.'
        ],
        'topics': ['SQL', 'NULL Handling', 'COALESCE'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['COALESCE and Math'],
        'status': 'published',
        'expected_query': 'SELECT id, name, (physical_stock - COALESCE(reserved_stock, 0)) AS available_stock FROM inventory ORDER BY id;'
    })

    # 68. Delivery success rate metric inflated by counting non-delivered rows
    challenges.append({
        'id': 68,
        'title': 'Delivery Success Rate Metric Inflated by Counting Non-Delivered Rows',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Operations dashboards reported a 100% on-time delivery rate even when returned and failed delivery shipments occurred."

### Bug Report
The delivery metric uses `COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`, which counts rows where the condition evaluates to `0` because `0` is non-NULL in SQL.

### Steps to Reproduce
1. Ingest shipments containing delivered and returned packages.
2. Execute `query.sql`.
3. Compare the reported `delivered_count` against actual delivered shipments.
4. Observe that returned shipments are counted toward the delivery metric.

### Expected Behaviour
Count only delivered shipments: `COUNT(CASE WHEN status = 'delivered' THEN 1 END) AS delivered_count`.

### Actual Behaviour
Returning `0` in the `ELSE` branch causes `COUNT()` to count all rows regardless of status.

### Starter Files
`query.sql` - Tracks completed package deliveries.
`schema.sql` - Package shipments and delivery statuses.

### Task
Modify `CASE` in `query.sql` so non-delivered statuses return `NULL` (or omit `ELSE`).

### Acceptance Criteria
1. Projected column: `delivered_count`.
2. Only shipments with `status = 'delivered'` are counted.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column alias: `delivered_count`.
- Correct aggregate counting of conditional subsets.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE shipments (
    id INT PRIMARY KEY,
    status VARCHAR(20)
);

INSERT INTO shipments VALUES
(1, 'delivered'),
(2, 'returned'),
(3, 'delivered');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_count FROM shipments;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'True delivered count is 2', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': "COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In SQL, `COUNT(x)` counts every non-null value; numerical 0 is not null and is therefore counted.',
            'Consider whether `SUM()` with 1 and 0, or `COUNT()` with NULL as the fallback, is the appropriate aggregation function.',
            'Change `COUNT(...)` to `SUM(CASE WHEN status = \'delivered\' THEN 1 ELSE 0 END)`.'
        ],
        'topics': ['SQL', 'Conditional Aggregation', 'CASE WHEN'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Conditional Aggregation'],
        'status': 'published',
        'expected_query': "SELECT SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_count FROM shipments;"
    })

    # 69. High-value customer loyalty tier excludes frequent repeat buyers
    challenges.append({
        'id': 69,
        'title': 'High-Value Customer Loyalty Tier Excludes Frequent Repeat Buyers',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Marketing noticed loyal customers who placed multiple $300 orders were excluded from the $500 VIP loyalty program, while single-order customers were admitted."

### Bug Report
The loyalty qualification query filters individual transaction amounts before aggregation rather than filtering on cumulative customer spend.

### Steps to Reproduce
1. Ingest customer orders where a customer has multiple transactions totaling over $500.
2. Execute `query.sql`.
3. Inspect the returned high-value customer list.
4. Observe that repeat buyers whose individual orders are under $500 are excluded.

### Expected Behaviour
Aggregate customer orders first, then filter customers whose total spend meets or exceeds 500: `HAVING SUM(amount) >= 500`.

### Actual Behaviour
Transaction filtering prior to aggregation eliminates customers with frequent moderate orders.

### Starter Files
`query.sql` - Identifies high-value customers qualifying for loyalty tiers.
`schema.sql` - Customer order transaction history.

### Task
Replace pre-aggregation filtering with a `HAVING` clause in `query.sql`.

### Acceptance Criteria
1. Projected columns: `customer_id`, `total_spent`.
2. Customers with cumulative spend >= 500 are included.
3. Ordered by `customer_id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Column aliases: `customer_id`, `total_spent`.
- Evaluation of cumulative thresholds via `HAVING`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2)
);

INSERT INTO orders VALUES
(1, 101, 300.00),
(2, 101, 300.00),
(3, 102, 600.00),
(4, 103, 100.00);"""
            },
            {
                'name': 'query.sql',
                'content': """WITH large_orders AS (
    SELECT customer_id, amount FROM orders WHERE amount >= 500
)
SELECT customer_id, SUM(amount) AS total_spent FROM large_orders GROUP BY customer_id ORDER BY customer_id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Customers 101 and 102 both have total >= 500', 'input': '', 'expected': 'High-value customers whose total spend meets or exceeds 500'}
        ],
        'bug_signature': 'SELECT customer_id, amount FROM orders WHERE amount >= 500',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Filtering row values before aggregation prevents calculating the total sum across multiple smaller events.',
            'Compute `SUM(amount) AS total_spent` grouped by `customer_id` inside the CTE first.',
            'Filter `WHERE total_spent >= 500` in the outer query.'
        ],
        'topics': ['SQL', 'CTE', 'HAVING vs WHERE'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Common Table Expressions'],
        'status': 'published',
        'expected_query': """WITH customer_totals AS (
    SELECT customer_id, SUM(amount) AS total_spent FROM orders GROUP BY customer_id
)
SELECT customer_id, total_spent FROM customer_totals WHERE total_spent >= 500 ORDER BY customer_id;"""
    })

    # 70. Multi-account fraud filter groups legitimate users with missing phones
    challenges.append({
        'id': 70,
        'title': 'Multi-Account Fraud Filter Groups Legitimate Users With Missing Phones',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Security monitors locked thousands of genuine user accounts because an automated fraud detection query flagged all users with missing phone numbers as a shared phone ring."

### Bug Report
The duplicate phone detection query groups by phone without filtering out `NULL` values, clustering all users with missing phone numbers into a single fraudulent group.

### Steps to Reproduce
1. Ingest user records where multiple accounts have unrecorded (`NULL`) phone numbers.
2. Execute `query.sql`.
3. Inspect the duplicate phone numbers report.
4. Observe that `NULL` appears as a duplicate phone group with a high account count.

### Expected Behaviour
Exclude `NULL` phone numbers prior to grouping: `WHERE phone IS NOT NULL GROUP BY phone HAVING COUNT(*) > 1`.

### Actual Behaviour
Grouping collects `NULL` entries into a single aggregate group, misinterpreting unset fields as duplicates.

### Starter Files
`query.sql` - Detects shared phone numbers indicative of multi-account abuse.
`schema.sql` - User accounts and phone records.

### Task
Filter out null phone records before grouping in `query.sql`.

### Acceptance Criteria
1. Projected columns: `phone`, `count`.
2. Only non-null duplicate phone numbers are reported.
3. Ordered by `phone` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `phone IS NOT NULL` must be enforced before grouping.
- Ordered by `phone` ascending.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    phone VARCHAR(20)
);

INSERT INTO users VALUES
(1, 'Alice', NULL),
(2, 'Bob', NULL),
(3, 'Charlie', '555-0100'),
(4, 'Diana', '555-0100');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT phone, COUNT(*) AS count FROM users GROUP BY phone HAVING COUNT(*) > 1 ORDER BY phone;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Only non-null duplicate phone 555-0100 returned', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'SELECT phone, COUNT(*) AS count FROM users GROUP BY phone',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In SQL GROUP BY operations, NULL values are treated as matching each other and form a single combined group.',
            'Filter out missing records before grouping to avoid false duplicate matches.',
            'Add `WHERE phone IS NOT NULL AND phone != \'\'` before the `GROUP BY phone` clause.'
        ],
        'topics': ['SQL', 'Duplicates', 'NULL Handling'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE and HAVING'],
        'status': 'published',
        'expected_query': "SELECT phone, COUNT(*) AS count FROM users WHERE phone IS NOT NULL AND phone != '' GROUP BY phone HAVING COUNT(*) > 1 ORDER BY phone;"
    })

    # 71. Competition leaderboard skips placing positions after tied scores
    challenges.append({
        'id': 71,
        'title': 'Competition Leaderboard Skips Placing Positions After Tied Scores',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Hackathon judges reported leaderboard placement anomalies where a participant who scored lower than two tied 1st-place finishers was displayed as 2nd place instead of 3rd place."

### Bug Report
The leaderboard ranking function assigns dense ranks without rank gaps for ties, contradicting competition ranking rules that require standard competitive ranking.

### Steps to Reproduce
1. Ingest scores where two participants tie for 1st place (score 95) and a third participant scores 90.
2. Execute `query.sql`.
3. Inspect the rank assigned to the third participant.
4. Observe that rank 2 is assigned instead of rank 3.

### Expected Behaviour
Use competitive ranking where ties produce subsequent rank gaps: `RANK() OVER (ORDER BY score DESC) AS rank`.

### Actual Behaviour
Dense ranking increments consecutively after ties without leaving ranking gaps.

### Starter Files
`query.sql` - Produces competitive participant score leaderboards.
`schema.sql` - Contest participants and scored submissions.

### Task
Replace `DENSE_RANK()` with `RANK()` in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `score`, `rank`.
2. Subsequent ranks skip positions proportional to tied competitors.
3. Ordered by `rank, id`.

### Constraints
- Target Database: SQLite 3.35+ with Window Function support.
- Standard competition ranking rules apply.
- Result ordering: `rank, id`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE scores (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    score INT
);

INSERT INTO scores VALUES
(1, 'Alice', 95),
(2, 'Bob', 95),
(3, 'Charlie', 90);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, score, DENSE_RANK() OVER (ORDER BY score DESC) AS rank FROM scores ORDER BY rank, id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Competition rank assigns Charlie rank 3', 'input': '', 'expected': 'Ranked records with correct tie-breaker ordering'}
        ],
        'bug_signature': 'DENSE_RANK() OVER (ORDER BY score DESC) AS rank',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'DENSE_RANK leaves no gaps after ties, whereas standard competition ranking (RANK) skips ranks corresponding to tied entries.',
            'Examine the window function name used in `query.sql`.',
            'Replace `DENSE_RANK()` with `RANK()`.'
        ],
        'topics': ['SQL', 'Window Functions', 'RANK vs DENSE_RANK'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Window Functions'],
        'status': 'published',
        'expected_query': 'SELECT id, name, score, RANK() OVER (ORDER BY score DESC) AS rank FROM scores ORDER BY rank, id;'
    })

    # 72. Product catalog crashes when category discounts return multiple rows
    challenges.append({
        'id': 72,
        'title': 'Product Catalog Crashes When Category Discounts Return Multiple Rows',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Subqueries',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Storefront API monitors raised 500 errors on catalog pages whenever merchandising configured more than one promotional discount for a product category."

### Bug Report
The product discount subquery uses scalar equality comparison against a subquery that returns multiple rows, causing subquery evaluation crashes.

### Steps to Reproduce
1. Configure multiple active discount records for category `'tech'`.
2. Execute `query.sql`.
3. Observe that the database engine raises a subquery scalar evaluation error.

### Expected Behaviour
Support set membership matching using `IN`: `WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech')`.

### Actual Behaviour
The `=` operator expects a single scalar value and fails when the subquery yields multiple rows.

### Starter Files
`query.sql` - Matches category promotional discounts against merchandise items.
`schema.sql` - Product categories and promotion discount schedules.

### Task
Update scalar comparison to set-based `IN` comparison in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `discount_id`.
2. Products matching any active category discount are returned.
3. Ordered by `id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Set-based subquery evaluation via `IN`.
- Ordered by `id` ascending.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE discounts (
    id INT PRIMARY KEY,
    category VARCHAR(20),
    amount DECIMAL(5,2)
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    discount_id INT
);

INSERT INTO discounts VALUES (1, 'tech', 10.00), (2, 'tech', 20.00);
INSERT INTO products VALUES (101, 'Mouse', 1), (102, 'Keyboard', 2), (103, 'Shirt', NULL);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, discount_id FROM products WHERE discount_id = (SELECT id FROM discounts WHERE category = 'tech') ORDER BY id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'IN operator matches all eligible products', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'WHERE discount_id = (SELECT id FROM discounts',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Comparing a scalar column to a subquery using `=` fails whenever the subquery returns more than one row.',
            'Consider which SQL operator evaluates membership within a set of values returned by a subquery.',
            'Change `=` to `IN`: `WHERE discount_id IN (SELECT id FROM discounts WHERE category = \'tech\')`.'
        ],
        'topics': ['SQL', 'Subqueries', 'IN vs EQUALS'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Subqueries'],
        'status': 'published',
        'expected_query': "SELECT id, name, discount_id FROM products WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech') ORDER BY id;"
    })

    # 73. Historical revenue audit distorted by modern catalog price updates
    challenges.append({
        'id': 73,
        'title': 'Historical Revenue Audit Distorted by Modern Catalog Price Updates',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"Financial auditors discovered that audited fiscal revenue from previous years shifted whenever current catalog product prices were updated in the merchandising system."

### Bug Report
The historical revenue audit joins against current product prices rather than multiplying order quantities by the historical unit price recorded at time of purchase.

### Steps to Reproduce
1. Ingest an order item purchased in 2025 at $50.00 where modern catalog price was updated to $80.00.
2. Execute `query.sql`.
3. Compare computed revenue against the purchase transaction receipt.
4. Observe that historical revenue is recalculated using current catalog rates.

### Expected Behaviour
Calculate revenue using transaction purchase prices: `SUM(oi.quantity * oi.price_at_purchase) AS total_revenue`.

### Actual Behaviour
Multiplying by current catalog price overwrites historical accounting data.

### Starter Files
`query.sql` - Audits historical order revenue per product.
`schema.sql` - Historical orders and modern catalog items.

### Task
Reference `price_at_purchase` from `order_items` in `query.sql`.

### Acceptance Criteria
1. Projected columns: `oi.product_id`, `total_revenue`.
2. Revenue reflects historical price at purchase.
3. Grouped by `oi.product_id`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column aliases: `product_id`, `total_revenue`.
- Historical integrity preservation.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    current_price DECIMAL(10,2)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    product_id INT,
    quantity INT,
    price_at_purchase DECIMAL(10,2)
);

INSERT INTO products VALUES (1, 'Widget', 80.00);
INSERT INTO order_items VALUES (101, 1, 2, 50.00);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT oi.product_id, SUM(oi.quantity * p.current_price) AS total_revenue FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY oi.product_id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Total reflects historical purchase price (2 * 50 = 100)', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'SUM(oi.quantity * p.current_price) AS total_revenue',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Historical financial metrics must rely on immutable snapshot values captured at transaction time rather than mutable master records.',
            'Check which price column is referenced in the arithmetic multiplication in `query.sql`.',
            'Compute `SUM(quantity * price_at_purchase) AS total_revenue` from `order_items` directly.'
        ],
        'topics': ['SQL', 'Historical Data', 'Data Integrity'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Aggregations'],
        'status': 'published',
        'expected_query': 'SELECT product_id, SUM(quantity * price_at_purchase) AS total_revenue FROM order_items GROUP BY product_id;'
    })

    # 74. Unique active customer metric multiplies repeat order buyers
    challenges.append({
        'id': 74,
        'title': 'Unique Active Customer Metric Multiplies Repeat Order Buyers',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"An investor metrics report showed 10,000 active monthly purchasers, but analytics found only 3,000 unique individuals because repeat buyers were counted on every purchase."

### Bug Report
The unique active customer aggregation counts total order records without deduplicating customer IDs, overstating active customer reach.

### Steps to Reproduce
1. Ingest multiple orders placed by the same repeat customer.
2. Execute `query.sql`.
3. Inspect the returned `unique_customers` count.
4. Observe that repeat customer orders are counted multiple times.

### Expected Behaviour
Deduplicate customer IDs during aggregation: `SELECT COUNT(DISTINCT customer_id) AS unique_customers FROM orders;`.

### Actual Behaviour
`COUNT(customer_id)` counts all order rows without distinct qualification.

### Starter Files
`query.sql` - Calculates unique purchasing customer reach metrics.
`schema.sql` - Order transaction records and customer identifiers.

### Task
Add `DISTINCT` to `COUNT()` in `query.sql` to calculate unique purchasers.

### Acceptance Criteria
1. Projected column: `unique_customers`.
2. Each purchaser is counted exactly once regardless of order volume.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column alias: `unique_customers`.
- Deduplicated count metric.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    order_date VARCHAR(20)
);

INSERT INTO orders VALUES
(1, 10, '2026-10-19'),
(2, 10, '2026-10-19'),
(3, 20, '2026-10-19');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT COUNT(customer_id) AS unique_customers FROM orders;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Distinct customers count is 2', 'input': '', 'expected': 'Deduplicated groups satisfying having condition'}
        ],
        'bug_signature': 'SELECT COUNT(customer_id) AS unique_customers FROM orders;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            '`COUNT(column)` tallies the total number of non-null rows, whereas measuring user populations requires counting distinct IDs.',
            'Examine the aggregation function in `query.sql`.',
            'Insert the `DISTINCT` keyword inside the count function: `COUNT(DISTINCT customer_id) AS unique_customers`.'
        ],
        'topics': ['SQL', 'COUNT DISTINCT', 'Metrics'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Aggregation'],
        'status': 'published',
        'expected_query': 'SELECT COUNT(DISTINCT customer_id) AS unique_customers FROM orders;'
    })

    # 75. Organizational hierarchy chart cuts off sub-team employee reports
    challenges.append({
        'id': 75,
        'title': 'Organizational Hierarchy Chart Cuts Off Sub-Team Employee Reports',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Incident Report
"HR reported that company org charts cut off after direct reports to the CEO, completely omitting sub-team managers and individual contributors."

### Bug Report
The recursive common table expression joins subsequent employee rows against parent manager IDs rather than parent employee IDs, terminating recursive traversal prematurely.

### Steps to Reproduce
1. Ingest a multi-tier reporting chain (CEO -> VP -> Lead -> Junior).
2. Execute `query.sql`.
3. Inspect the returned organizational hierarchy.
4. Observe that reports below level 2 are missing from the chart.

### Expected Behaviour
Join child employee `manager_id` with parent CTE `id`: `FROM employees e JOIN org_tree org ON e.manager_id = org.id`.

### Actual Behaviour
Joining on `org.manager_id` prevents downward recursive traversal past initial direct reports.

### Starter Files
`query.sql` - Builds corporate reporting hierarchy via recursive CTE.
`schema.sql` - Employee organizational reporting tree.

### Task
Correct the recursive join condition in `org_tree` in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `level`.
2. Traverses all reporting tiers from top executive to individual contributors.
3. Ordered by `level, id`.

### Constraints
- Target Database: SQLite 3.35+ with Recursive CTE support.
- Traverses full parent-child hierarchy.
- Result ordering: `level, id`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    manager_id INT
);

INSERT INTO employees VALUES
(1, 'CEO', NULL),
(2, 'VP Eng', 1),
(3, 'Lead Dev', 2),
(4, 'Junior Dev', 3);"""
            },
            {
                'name': 'query.sql',
                'content': """WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 1 AS level FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, org.level + 1
    FROM employees e JOIN org_tree org ON e.manager_id = org.manager_id
)
SELECT id, name, level FROM org_tree ORDER BY level, id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Full 4-level tree generated', 'input': '', 'expected': 'Complete hierarchical reporting structure'}
        ],
        'bug_signature': 'ON e.manager_id = org.manager_id',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In a recursive tree CTE, the recursive step must link child foreign keys to the parent primary key produced by the previous iteration.',
            'Check the join condition linking `employees e` with `org_tree org` in `query.sql`.',
            'Change `ON e.manager_id = org.manager_id` to `ON e.manager_id = org.id`.'
        ],
        'topics': ['SQL', 'Recursive CTE', 'Hierarchies'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Recursive CTEs'],
        'status': 'published',
        'expected_query': """WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 1 AS level FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, org.level + 1
    FROM employees e JOIN org_tree org ON e.manager_id = org.id
)
SELECT id, name, level FROM org_tree ORDER BY level, id;"""
    })

    return challenges
