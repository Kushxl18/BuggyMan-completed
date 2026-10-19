"""
SQL Lab: Medium Challenges (61 to 75)
"""

def get_sql_medium():
    challenges = []

    # 61. A JOIN duplicates revenue because of multiple order items
    challenges.append({
        'id': 61,
        'title': '[SQL-M01] A JOIN Duplicates Revenue Because of Multiple Order Items',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
An analytics query reports total customer spending by joining the `orders` table with the `order_items` table.

### Bug Report
An order of $100 containing 3 line items counts as $300 revenue, tripling customer spending metrics!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `orders` table has `total_amount = 100.00`.
3. Joining with `order_items` replicates the order row for every item.
4. `SUM(o.total_amount)` multiplies order totals.

### Expected Behavior
Sum `o.total_amount` directly from `orders` without joining `order_items`, OR sum `item_price * quantity` from `order_items`.

### Actual Behavior
Joins `order_items` and sums `orders.total_amount`.

### Impact
Revenue reports inflated by up to 400%, misleading financial stakeholders.

### Requirements
- Calculate true total revenue per customer from `orders` table directly, grouped by `customer_id`.
""",
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
            {'id': 1, 'name': 'Visible: Accurate customer revenue without join duplication', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'JOIN order_items i ON o.id = i.order_id GROUP BY o.customer_id',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Do not join `order_items` if `orders` already contains `total_amount`.',
            'Query `orders` directly: `SELECT customer_id, SUM(total_amount) AS revenue FROM orders GROUP BY customer_id ORDER BY customer_id;`.'
        ],
        'topics': ['SQL', 'Joins', 'Aggregation', 'Cartesian Product'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins and Grouping'],
        'status': 'published',
        'expected_query': 'SELECT customer_id, SUM(total_amount) AS revenue FROM orders GROUP BY customer_id ORDER BY customer_id;'
    })

    # 62. Customer lifetime value is inflated by an incorrect aggregation
    challenges.append({
        'id': 62,
        'title': '[SQL-M02] Customer Lifetime Value is Inflated by an Incorrect Aggregation',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A customer intelligence report calculates average order value (AOV) per customer across multiple stores.

### Bug Report
Customer average order value calculation averages the daily averages, which skews metrics toward low-volume days.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `AVG(order_amount)` over aggregated day totals rather than individual orders.

### Expected Behavior
Calculate true AOV as `SUM(amount) / COUNT(id)` directly across all individual orders.

### Actual Behavior
Averages the pre-aggregated daily sums.

### Impact
Inaccurate lifetime value projections in VIP customer retention tiers.

### Requirements
- Compute true average order value: `ROUND(AVG(amount), 2)` grouped by `customer_id`.
""",
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
            {'id': 1, 'name': 'Visible: True average order value per customer', 'input': '', 'expected': 'Average metric correctly computed per group'}
        ],
        'bug_signature': 'SELECT customer_id, SUM(amount) AS aov FROM orders',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Use `ROUND(AVG(amount), 2) AS aov` instead of `SUM(amount)`.'
        ],
        'topics': ['SQL', 'Aggregation', 'AVG'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Averages'],
        'status': 'published',
        'expected_query': 'SELECT customer_id, ROUND(AVG(amount), 2) AS aov FROM orders GROUP BY customer_id ORDER BY customer_id;'
    })

    # 63. Pagination skips or duplicates rows when ordering is not deterministic
    challenges.append({
        'id': 63,
        'title': '[SQL-M03] Pagination Skips or Duplicates Rows When Ordering is Not Deterministic',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
An audit log viewer paginates system events in chunks of 2 rows using `LIMIT 2 OFFSET n`.

### Bug Report
Events with identical timestamps randomly shift positions between queries, so Page 1 and Page 2 display duplicate rows.

### Steps to Reproduce
1. Query `LIMIT 2 OFFSET 0` ordered by `created_at DESC`.
2. Query `LIMIT 2 OFFSET 2` ordered by `created_at DESC`.
3. Records with identical `created_at` values appear on both pages.

### Expected Behavior
Add `id ASC` as a secondary deterministic sort column to guarantee stable row order: `ORDER BY created_at DESC, id ASC`.

### Actual Behavior
Sorts solely by `created_at DESC`.

### Impact
Compliance auditors miss critical security events due to unstable pagination windows.

### Requirements
- Add secondary unique sort key `id ASC` to the `ORDER BY` clause.
""",
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
            {'id': 1, 'name': 'Visible: Deterministic sort with id tie-breaker', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'ORDER BY created_at DESC LIMIT 2 OFFSET 0;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `, id ASC` to `ORDER BY created_at DESC`.'
        ],
        'topics': ['SQL', 'Pagination', 'Deterministic Ordering'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL LIMIT and OFFSET'],
        'status': 'published',
        'expected_query': 'SELECT id, event, created_at FROM audit_logs ORDER BY created_at DESC, id ASC LIMIT 2 OFFSET 0;'
    })

    # 64. A window function uses the wrong partition
    challenges.append({
        'id': 64,
        'title': '[SQL-M04] A Window Function Uses the Wrong Partition',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
An enterprise sales leaderboard ranks account executives by closed revenue within their respective global sales regions.

### Bug Report
Sales reps in the EMEA region are ranked against reps in APAC and Americas, rather than competing solely within their regional teams.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `RANK() OVER (ORDER BY revenue DESC)` lacks `PARTITION BY region`.
3. Rankings are global instead of regional.

### Expected Behavior
Rank sales executives partitioned by regional division: `RANK() OVER (PARTITION BY region ORDER BY revenue DESC)`.

### Actual Behavior
Omits `PARTITION BY region`.

### Impact
Regional sales quarterly performance bonuses distributed to the wrong employees.

### Requirements
- Add `PARTITION BY region` to the window ranking function.
""",
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
            {'id': 1, 'name': 'Visible: Regional partition ranks top rep in each region as #1', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'RANK() OVER (ORDER BY revenue DESC) AS regional_rank',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `PARTITION BY region` inside the `OVER (...)` clause.'
        ],
        'topics': ['SQL', 'Window Functions', 'RANK', 'PARTITION BY'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Window Functions'],
        'status': 'published',
        'expected_query': 'SELECT id, name, region, revenue, RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS regional_rank FROM sales_reps ORDER BY region, regional_rank;'
    })

    # 65. A monthly report mishandles timezone boundaries
    challenges.append({
        'id': 65,
        'title': '[SQL-M05] A Monthly Report Mishandles Timezone Boundaries',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A subscription billing portal groups recurring payments by calendar month using UTC timestamps.

### Bug Report
Subscriptions renewed on September 1st at 00:30 UTC are placed into August because query attempts manual offset subtraction without boundary validation.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice manual string slicing cuts off date without `strftime('%Y-%m', payment_date)`.

### Expected Behavior
Extract standard year-month group key: `strftime('%Y-%m', payment_date)`.

### Actual Behavior
Manual substring parsing shifts dates.

### Impact
Revenue numbers misattributed between fiscal months.

### Requirements
- Use `strftime('%Y-%m', payment_date) AS month` and group by month.
""",
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
            {'id': 1, 'name': 'Visible: Grouped by YYYY-MM formatted month', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'substr(payment_date, 6, 2) AS month',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Use `strftime(\'%Y-%m\', payment_date) AS month`.'
        ],
        'topics': ['SQL', 'Dates', 'strftime'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Datetime Functions'],
        'status': 'published',
        'expected_query': "SELECT strftime('%Y-%m', payment_date) AS month, SUM(amount) AS total FROM payments GROUP BY month ORDER BY month;"
    })

    # 66. A LEFT JOIN becomes an accidental INNER JOIN
    challenges.append({
        'id': 66,
        'title': '[SQL-M06] A LEFT JOIN Becomes an Accidental INNER JOIN',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A customer directory query displays user account profiles along with their most recent premium subscription plan. Users without premium plans must still be displayed.

### Bug Report
Users with no subscription are excluded from the directory despite using a `LEFT JOIN`!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `WHERE s.status = 'active'`.
3. Users with no subscription have `s.status = NULL`. The `WHERE` clause filters out `NULL`, converting the `LEFT JOIN` into an `INNER JOIN`!

### Expected Behavior
Move the condition `s.status = 'active'` into the `ON` clause of the `LEFT JOIN`: `LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'`.

### Actual Behavior
Filters `s.status = 'active'` in the `WHERE` clause.

### Impact
Free-tier users disappear from administrative moderation lists.

### Requirements
- Move filter into `ON` clause so unmatched users remain with NULL subscription details.
""",
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
            {'id': 1, 'name': 'Visible: Preserves Bob with NULL plan_name', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': "LEFT JOIN subscriptions s ON u.id = s.user_id WHERE s.status = 'active'",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Move `AND s.status = \'active\'` into the `ON` clause and remove the `WHERE` clause.'
        ],
        'topics': ['SQL', 'Joins', 'LEFT JOIN', 'WHERE vs ON'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins'],
        'status': 'published',
        'expected_query': "SELECT u.id, u.name, s.plan_name FROM users u LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active' ORDER BY u.id;"
    })

    # 67. An inventory report calculates incorrect available stock
    challenges.append({
        'id': 67,
        'title': '[SQL-M07] An Inventory Report Calculates Incorrect Available Stock',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A warehouse management system computes available stock as `physical_stock - reserved_stock`.

### Bug Report
Items with zero pending reservations (`reserved_stock = NULL`) show `available_stock = NULL` instead of their physical stock!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `physical_stock - reserved_stock`.
3. In SQL arithmetic, `10 - NULL` evaluates to `NULL`.

### Expected Behavior
Use `COALESCE(reserved_stock, 0)` so unreserved items subtract 0.

### Actual Behavior
Subtracts raw NULL, wiping out availability numbers.

### Impact
In-stock items show as unavailable in product catalog, halting sales.

### Requirements
- Compute available inventory by subtracting reserved stock from physical stock, handling unset reserved quantities as 0.
""",
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
            {'id': 1, 'name': 'Visible: Keyboard shows available_stock = 25', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': '(physical_stock - reserved_stock) AS available_stock',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Wrap `reserved_stock` in `COALESCE(reserved_stock, 0)`.'
        ],
        'topics': ['SQL', 'NULL Handling', 'COALESCE'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['COALESCE and Math'],
        'status': 'published',
        'expected_query': 'SELECT id, name, (physical_stock - COALESCE(reserved_stock, 0)) AS available_stock FROM inventory ORDER BY id;'
    })

    # 68. A query incorrectly handles NULL values in conditional aggregation
    challenges.append({
        'id': 68,
        'title': '[SQL-M08] A Query Incorrectly Handles NULL Values in Conditional Aggregation',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A customer engagement dashboard counts how many orders were successfully delivered vs returned.

### Bug Report
The delivered orders column count is inaccurate because `COUNT(CASE WHEN status = 'delivered' THEN 0 ELSE NULL END)` evaluates `0` as non-null!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`.
3. `COUNT()` counts non-null values, including `0`, so returned orders are counted as delivered!

### Expected Behavior
Use `SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)` OR `COUNT(CASE WHEN status = 'delivered' THEN 1 END)`.

### Actual Behavior
Uses `COUNT()` with `ELSE 0`, counting all rows.

### Impact
Executive dashboard shows a 100% delivery rate despite thousands of returned packages.

### Requirements
- Accurately calculate delivered order counts without miscounting non-delivered orders in the aggregate.
""",
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
            {'id': 1, 'name': 'Visible: True delivered count is 2', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': "COUNT(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In SQL, COUNT(0) counts 0 as a valid non-null row; consider using SUM with 1 and 0, or COUNT without an ELSE clause.'
        ],
        'topics': ['SQL', 'Conditional Aggregation', 'CASE WHEN'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['Conditional Aggregation'],
        'status': 'published',
        'expected_query': "SELECT SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_count FROM shipments;"
    })

    # 69. A CTE filters records before aggregation when filtering should occur afterward
    challenges.append({
        'id': 69,
        'title': '[SQL-M09] A CTE Filters Records Before Aggregation When Filtering Should Occur Afterward',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A customer loyalty tier report identifies high-value accounts whose total annual spending exceeds $500.

### Bug Report
The report filters out individual purchases under $500 in the CTE before summing, omitting loyal customers who made ten $60 purchases!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `WITH large_orders AS (SELECT * FROM orders WHERE amount >= 500)`.
3. Customers with multiple smaller orders totalling > $500 are omitted.

### Expected Behavior
Sum all orders first per customer in the CTE, then filter `WHERE total_spent >= 500`.

### Actual Behavior
Filters individual transaction amounts in the initial CTE.

### Impact
High-value repeat customers excluded from VIP perks and loyalty reward distributions.

### Requirements
- Aggregate total spending per customer across all orders first in the CTE, then filter for qualifying high-value clients in the outer query.
""",
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
            {'id': 1, 'name': 'Visible: Customers 101 and 102 both have total >= 500', 'input': '', 'expected': 'High-value customers whose total spend meets or exceeds 500'}
        ],
        'bug_signature': 'SELECT customer_id, amount FROM orders WHERE amount >= 500',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Sum in the CTE first: `SELECT customer_id, SUM(amount) AS total_spent FROM orders GROUP BY customer_id`.',
            'Filter in the outer query: `WHERE total_spent >= 500`.'
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

    # 70. A duplicate-detection query flags valid records
    challenges.append({
        'id': 70,
        'title': '[SQL-M10] A Duplicate-Detection Query Flags Valid Records',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A fraud-detection system flags accounts suspected of multi-accounting by matching identical telephone numbers.

### Bug Report
Over 15,000 legitimate users who have empty or unset phone numbers (`phone IS NULL`) are all grouped together and flagged as a fraudulent syndicate!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `GROUP BY phone HAVING COUNT(*) > 1`.
3. `NULL` phone values group together into a single cluster.

### Expected Behavior
Exclude `NULL` and empty phone strings from the duplicate scan: `WHERE phone IS NOT NULL AND phone != ''`.

### Actual Behavior
Groups all NULL records into a single false-positive duplicate cluster.

### Impact
Thousands of legitimate user accounts locked by automated security filters.

### Requirements
- Exclude missing, null, and empty phone values before evaluating duplicate phone counts.
""",
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
            {'id': 1, 'name': 'Visible: Only non-null duplicate phone 555-0100 returned', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'SELECT phone, COUNT(*) AS count FROM users GROUP BY phone',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `WHERE phone IS NOT NULL AND phone != \'\'` before the `GROUP BY phone` clause.'
        ],
        'topics': ['SQL', 'Duplicates', 'NULL Handling'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE and HAVING'],
        'status': 'published',
        'expected_query': "SELECT phone, COUNT(*) AS count FROM users WHERE phone IS NOT NULL AND phone != '' GROUP BY phone HAVING COUNT(*) > 1 ORDER BY phone;"
    })

    # 71. A ranking query assigns incorrect positions to tied values
    challenges.append({
        'id': 71,
        'title': '[SQL-M11] A Ranking Query Assigns Incorrect Positions to Tied Values',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A hackathon scoring platform displays leaderboard ranks based on judge scores.

### Bug Report
Two competitors tied for 1st place with 95 points. The next participant with 90 points is displayed as 2nd place instead of 3rd place!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `DENSE_RANK() OVER (ORDER BY score DESC)`.
3. Scores 95, 95, 90 receive ranks 1, 1, 2 (dense rank does not skip ranks).

### Expected Behavior
Standard competition ranking must skip ranks after ties: 1, 1, 3. Use `RANK()`.

### Actual Behavior
Uses `DENSE_RANK()`.

### Impact
Award ceremony medals and prize distributions given to wrong placement tiers.

### Requirements
- Review the difference between RANK() and DENSE_RANK(): RANK leaves gaps after tied positions, whereas DENSE_RANK does not.
""",
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
            {'id': 1, 'name': 'Visible: Competition rank assigns Charlie rank 3', 'input': '', 'expected': 'Ranked records with correct tie-breaker ordering'}
        ],
        'bug_signature': 'DENSE_RANK() OVER (ORDER BY score DESC) AS rank',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Review the difference between RANK() and DENSE_RANK(): RANK leaves gaps after tied positions, whereas DENSE_RANK does not.'
        ],
        'topics': ['SQL', 'Window Functions', 'RANK vs DENSE_RANK'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Window Functions'],
        'status': 'published',
        'expected_query': 'SELECT id, name, score, RANK() OVER (ORDER BY score DESC) AS rank FROM scores ORDER BY rank, id;'
    })

    # 72. A subquery returns multiple rows unexpectedly
    challenges.append({
        'id': 72,
        'title': '[SQL-M12] A Subquery Returns Multiple Rows Unexpectedly',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Subqueries',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
A product pricing query applies store discounts by matching eligible category promotions.

### Bug Report
The product API crashes with `OperationalError: subquery returns more than 1 row` whenever a category has multiple active discount coupons.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice scalar comparison `WHERE discount_id = (SELECT id FROM discounts WHERE category = 'tech')`.
3. When multiple discounts exist, scalar equality `=` throws a database error.

### Expected Behavior
Use `IN` instead of `=` for multi-row subqueries: `WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech')`.

### Actual Behavior
Uses scalar `=` operator against a multi-row subquery.

### Impact
Product catalog crashes across major retail categories.

### Requirements
- Use a set-membership operator rather than scalar equality to safely handle subqueries that return multiple matching discount records.
""",
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
            {'id': 1, 'name': 'Visible: IN operator matches all eligible products', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'WHERE discount_id = (SELECT id FROM discounts',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'When a subquery returns more than a single scalar value, use set-membership predicates such as IN instead of equality.'
        ],
        'topics': ['SQL', 'Subqueries', 'IN vs EQUALS'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Subqueries'],
        'status': 'published',
        'expected_query': "SELECT id, name, discount_id FROM products WHERE discount_id IN (SELECT id FROM discounts WHERE category = 'tech') ORDER BY id;"
    })

    # 73. A report combines historical and current prices incorrectly
    challenges.append({
        'id': 73,
        'title': '[SQL-M13] A Report Combines Historical and Current Prices Incorrectly',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
An order line item audit checks sales totals. Prices change over time, so past orders must multiply by historical unit price, not the current catalog price.

### Bug Report
A customer bought an item in 2025 for $50. In 2026, the price was raised to $80. The 2025 sales report recalculates the past order at $80, distorting historical revenue!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice query joins `products` table and uses `p.current_price` instead of historical `oi.price_at_purchase`.

### Expected Behavior
Use `oi.price_at_purchase * oi.quantity` recorded at the time of purchase.

### Actual Behavior
Multiplies by `p.current_price`.

### Impact
Audited historical balance sheets are altered every time modern catalog prices change.

### Requirements
- Multiply quantity by historical price: `SUM(oi.quantity * oi.price_at_purchase) AS total_revenue`.
""",
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
            {'id': 1, 'name': 'Visible: Total reflects historical purchase price (2 * 50 = 100)', 'input': '', 'expected': 'Aggregated revenue matching date/order criteria'}
        ],
        'bug_signature': 'SUM(oi.quantity * p.current_price) AS total_revenue',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Use `price_at_purchase`: `SELECT product_id, SUM(quantity * price_at_purchase) AS total_revenue FROM order_items GROUP BY product_id;`.'
        ],
        'topics': ['SQL', 'Historical Data', 'Data Integrity'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Aggregations'],
        'status': 'published',
        'expected_query': 'SELECT product_id, SUM(quantity * price_at_purchase) AS total_revenue FROM order_items GROUP BY product_id;'
    })

    # 74. A query counts orders instead of distinct customers
    challenges.append({
        'id': 74,
        'title': '[SQL-M14] A Query Counts Orders Instead of Distinct Customers',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
An executive KPI dashboard reports monthly active unique purchasing customers.

### Bug Report
If 1 customer places 10 orders in a day, the dashboard reports 10 active customers instead of 1!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `COUNT(customer_id)`.
3. Multiple orders by the same customer are counted repeatedly.

### Expected Behavior
Count distinct customers: `COUNT(DISTINCT customer_id) AS unique_customers`.

### Actual Behavior
Uses `COUNT(customer_id)` without `DISTINCT`.

### Impact
Customer base size inflated by 300% on investor quarterly reports.

### Requirements
- Use `COUNT(DISTINCT customer_id) AS unique_customers`.
""",
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
            {'id': 1, 'name': 'Visible: Distinct customers count is 2', 'input': '', 'expected': 'Deduplicated groups satisfying having condition'}
        ],
        'bug_signature': 'SELECT COUNT(customer_id) AS unique_customers FROM orders;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `DISTINCT`: `SELECT COUNT(DISTINCT customer_id) AS unique_customers FROM orders;`.'
        ],
        'topics': ['SQL', 'COUNT DISTINCT', 'Metrics'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Aggregation'],
        'status': 'published',
        'expected_query': 'SELECT COUNT(DISTINCT customer_id) AS unique_customers FROM orders;'
    })

    # 75. A recursive query omits part of an organizational hierarchy
    challenges.append({
        'id': 75,
        'title': '[SQL-M15] A Recursive Query Omits Part of an Organizational Hierarchy',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '15 mins',
        'points': 150,
        'description': """### Company Scenario
An HR organizational chart application displays all employees reporting under the CEO (including indirect reports).

### Bug Report
Only direct reports to the CEO appear; second-level managers and individual contributors are omitted!

### Steps to Reproduce
1. Execute recursive query in `query.sql`.
2. Notice recursive term joins `WHERE e.manager_id = org.manager_id` instead of `WHERE e.manager_id = org.id`.
3. Hierarchy stops descending after level 1.

### Expected Behavior
The recursive join must match employee `manager_id` with parent `org.id`.

### Actual Behavior
Joins on identical manager_id, failing to recurse down the tree.

### Impact
Department heads cannot view full staffing headcount across sub-teams.

### Requirements
- Correct the recursive join condition so employee manager relationships properly link to the ancestor node's primary key.
""",
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
            {'id': 1, 'name': 'Visible: Full 4-level tree generated', 'input': '', 'expected': 'Complete hierarchical reporting structure'}
        ],
        'bug_signature': 'ON e.manager_id = org.manager_id',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            "Check the recursive join condition: an employee's manager_id should match the ancestor's primary key id."
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
