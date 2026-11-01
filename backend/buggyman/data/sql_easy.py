"""
SQL Lab: Easy Challenges (51 to 60)
"""

def get_sql_easy():
    challenges = []

    # 51. Marketing contact export omits customers with unset preferences
    challenges.append({
        'id': 51,
        'title': 'Marketing Contact Export Omits Customers With Unset Preferences',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Marketing operations reported that nearly half of their customer contact list vanished from automated email campaign exports after a database migration introduced optional preference fields."

### Bug Report
The contact export query fails to include customers whose marketing communication preferences have not been explicitly populated in the database.

### Steps to Reproduce
1. Inspect the contact table containing active customers with both explicit opt-out flags and unset preferences.
2. Execute `query.sql`.
3. Compare the number of exported contacts against eligible customer accounts.
4. Observe that customers with unset preferences are absent from the export results.

### Expected Behaviour
Return all customers who have not opted out (i.e. those where `opt_out` is `0` or unset/null), including `id`, `name`, and `email`, ordered by `id`.

### Actual Behaviour
Customers with unpopulated preference values are excluded from the exported query results.

### Starter Files
`query.sql` - Extracts eligible marketing contact records from the customer table.
`schema.sql` - Table definitions and seed data for customer communication preferences.

### Task
Modify `query.sql` to include customers who have not explicitly opted out.

### Acceptance Criteria
1. Returns `id`, `name`, and `email` for all customers whose opt-out status is not `1`.
2. Results are ordered by `id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Handles `NULL` attribute values according to standard SQL three-valued logic.
- Column projections must match: `id`, `name`, `email`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    opt_out INT
);

INSERT INTO customers VALUES
(1, 'Alice', 'alice@test.com', 0),
(2, 'Bob', 'bob@test.com', 1),
(3, 'Charlie', 'charlie@test.com', NULL),
(4, 'Diana', 'diana@test.com', 0);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, email FROM customers WHERE opt_out != 1;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Includes NULL and 0 opt-out records', 'input': '', 'expected': 'Customers including opt_out=0 and opt_out IS NULL'}
        ],
        'bug_signature': 'WHERE opt_out != 1',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In SQL three-valued logic, comparing NULL against any value using `=` or `!=` evaluates to UNKNOWN rather than TRUE.',
            'Examine the WHERE clause in `query.sql` and consider how unset database values behave under standard inequality.',
            'Use an explicit `IS NULL` check (e.g. `opt_out = 0 OR opt_out IS NULL`) or `COALESCE` to handle missing values.'
        ],
        'topics': ['SQL', 'NULL Handling', 'Three-Valued Logic'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE Clause', 'NULLs in SQL'],
        'status': 'published',
        'expected_query': 'SELECT id, name, email FROM customers WHERE opt_out = 0 OR opt_out IS NULL ORDER BY id;'
    })

    # 52. Monthly revenue report truncates final day orders
    challenges.append({
        'id': 52,
        'title': 'Monthly Revenue Report Truncates Final Day Orders',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Finance reported an accounting discrepancy where October revenue was under-reported by thousands of dollars compared to bank merchant statements."

### Bug Report
The monthly revenue calculation excludes transactions executed during the afternoon and evening hours of the month's final day.

### Steps to Reproduce
1. Ingest orders placed throughout the month of October, including afternoon transactions on October 31st.
2. Execute `query.sql`.
3. Compare the calculated revenue against total order amounts recorded for October.
4. Observe that late-day transactions on October 31st are omitted from the calculated sum.

### Expected Behaviour
Aggregate all order amounts falling between the start of October 1st and the start of November 1st: `SELECT SUM(amount) AS total_revenue ...`.

### Actual Behaviour
Date range filtering truncates transactions placed on the final calendar day of the reporting period.

### Starter Files
`query.sql` - Calculates monthly revenue totals from the orders table.
`schema.sql` - Schema definitions and seed transactions.

### Task
Update the date boundary filter in `query.sql` to capture all transactions through the entire month.

### Acceptance Criteria
1. Calculates total revenue across all October orders.
2. Output column is aliased as `total_revenue`.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Timestamps include ISO date and time components (`YYYY-MM-DD HH:MM:SS`).
- Output column alias must be `total_revenue`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    amount DECIMAL(10,2),
    order_date DATETIME
);

INSERT INTO orders VALUES
(1, 100.00, '2026-10-01 10:00:00'),
(2, 250.00, '2026-10-15 14:00:00'),
(3, 150.00, '2026-10-31 18:30:00'),
(4, 300.00, '2026-11-01 09:00:00');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date BETWEEN '2026-10-01' AND '2026-10-31';"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Total includes October 31st afternoon order', 'input': '', 'expected': 'Total revenue sum including October 31st afternoon transactions'}
        ],
        'bug_signature': "BETWEEN '2026-10-01' AND '2026-10-31'",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Using `BETWEEN` on datetime columns with date-only literals truncates the end date to midnight (00:00:00).',
            'Consider how half-open intervals (`>= start` and `< next_period_start`) cleanly capture full time spans.',
            'Filter with `order_date >= \'2026-10-01\' AND order_date < \'2026-11-01\'` to capture all timestamps throughout October 31st.'
        ],
        'topics': ['SQL', 'Dates', 'Half-Open Intervals'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Datetime'],
        'status': 'published',
        'expected_query': "SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date >= '2026-10-01' AND order_date < '2026-11-01';"
    })

    # 53. Public storefront search displays obsolete archived products
    challenges.append({
        'id': 53,
        'title': 'Public Storefront Search Displays Obsolete Archived Products',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Store managers reported that customers were purchasing discontinued items that had been archived years ago, while current catalog items were missing from storefront search."

### Bug Report
The catalog search query inverts inventory availability filters, returning obsolete and discontinued products instead of active store inventory.

### Steps to Reproduce
1. Inspect the product catalog containing active and archived items.
2. Execute `query.sql`.
3. Inspect the returned product records.
4. Observe that archived items are displayed while active items are missing.

### Expected Behaviour
Return `id`, `name`, and `price` for all products whose status is `'active'`, ordered by `name` ascending.

### Actual Behaviour
The query selects products with archived status, exposing discontinued catalog items.

### Starter Files
`query.sql` - Searches and filters active merchandise catalog products.
`schema.sql` - Product catalog schema and seed inventory items.

### Task
Update `query.sql` to return active inventory products.

### Acceptance Criteria
1. Only products with `status = 'active'` are returned.
2. Projected columns: `id`, `name`, `price`.
3. Rows are ordered alphabetically by `name` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Price values preserve decimal precision.
- Result ordering must be alphabetical by `name`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    price DECIMAL(10,2),
    status VARCHAR(20)
);

INSERT INTO products VALUES
(1, 'Laptop Pro', 1200.00, 'active'),
(2, 'Legacy Phone', 150.00, 'archived'),
(3, 'Wireless Mouse', 25.00, 'active');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, price FROM products WHERE status = 'archived' ORDER BY name ASC;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Returns active products ordered by name', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': "WHERE status = 'archived'",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Database status flags distinguish between obsolete records and active inventory.',
            'Examine the literal string checked in the WHERE clause of `query.sql`.',
            'Update the predicate to `WHERE status = \'active\'`.'
        ],
        'topics': ['SQL', 'Filtering'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE Clause'],
        'status': 'published',
        'expected_query': "SELECT id, name, price FROM products WHERE status = 'active' ORDER BY name ASC;"
    })

    # 54. User roster omits newly registered customers without orders
    challenges.append({
        'id': 54,
        'title': 'User Roster Omits Newly Registered Customers Without Orders',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"The customer onboarding team noticed that new users who registered but had not yet made a purchase were completely missing from onboarding follow-up lists."

### Bug Report
The customer roster query drops accounts that have no recorded order history, preventing customer success teams from reaching out to newly registered users.

### Steps to Reproduce
1. Ingest registered customers where some accounts have zero recorded purchase orders.
2. Execute `query.sql`.
3. Compare the returned customer list against the full user registration directory.
4. Observe that registered customers with no order history are omitted.

### Expected Behaviour
Return all registered customers alongside their associated order ID (or `NULL` if no orders exist), ordered by `id` ascending.

### Actual Behaviour
Registered customers without order transactions are excluded from the result set.

### Starter Files
`query.sql` - Generates customer onboarding rosters joined with purchase orders.
`schema.sql` - Customer accounts and order transaction tables.

### Task
Update table joins in `query.sql` to retain all registered customers regardless of order history.

### Acceptance Criteria
1. Projected columns: `c.id`, `c.name`, `order_id`.
2. Customers without orders display `NULL` for `order_id`.
3. Rows are ordered by `c.id` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output preserves all primary customer records.
- Column aliases: `c.id`, `c.name`, `order_id`.""",
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
                'content': """SELECT c.id, c.name, o.id AS order_id FROM customers c INNER JOIN orders o ON c.id = o.customer_id ORDER BY c.id;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'LEFT JOIN includes Charlie with NULL order_id', 'input': '', 'expected': 'All customers with order IDs or NULL if no orders'}
        ],
        'bug_signature': 'INNER JOIN orders o',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'An INNER JOIN requires matches on both sides of the join condition, omitting unmatched left-table rows.',
            'Consider which relational join type preserves all rows from the primary table even when no foreign key match exists.',
            'Change `INNER JOIN` to `LEFT JOIN` (or `LEFT OUTER JOIN`).'
        ],
        'topics': ['SQL', 'Joins', 'LEFT JOIN'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins'],
        'status': 'published',
        'expected_query': 'SELECT c.id, c.name, o.id AS order_id FROM customers c LEFT JOIN orders o ON c.id = o.customer_id ORDER BY c.id;'
    })

    # 55. Department bonus metrics overstate average by excluding zero bonus staff
    challenges.append({
        'id': 55,
        'title': 'Department Bonus Metrics Overstate Average by Excluding Zero Bonus Staff',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Executive HR leadership noticed departmental average bonus metrics were artificially inflated because employees receiving $0 bonuses were excluded from performance calculations."

### Bug Report
The departmental bonus calculation filters out employees with zero bonus before computing averages, skewing compensation metrics upwards.

### Steps to Reproduce
1. Populate an employee table with departmental bonus data, including staff with zero bonus awards.
2. Execute `query.sql`.
3. Compare the reported departmental average against the true per-capita bonus average.
4. Observe that departmental averages are overstated.

### Expected Behaviour
Calculate the true average bonus across all employees in each department, ordered by department name.

### Actual Behaviour
Pre-filtering non-bonus recipients removes zero-value rows prior to average aggregation, biasing metrics.

### Starter Files
`query.sql` - Computes departmental average compensation bonuses.
`schema.sql` - Employee compensation and department records.

### Task
Adjust aggregation in `query.sql` to include all departmental staff in the average bonus metric.

### Acceptance Criteria
1. Projected columns: `department`, `avg_bonus`.
2. All staff in the department contribute to the average divisor.
3. Results are ordered by `department` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- `avg_bonus` accurately computes arithmetic mean including zero values.
- Grouped by `department`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE employees (
    id INT PRIMARY KEY,
    department VARCHAR(50),
    bonus DECIMAL(5,2)
);

INSERT INTO employees VALUES
(1, 'Engineering', 10.0),
(2, 'Engineering', 0.0),
(3, 'Sales', 20.0),
(4, 'Sales', 10.0);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT department, AVG(bonus) AS avg_bonus FROM employees WHERE bonus > 0 GROUP BY department ORDER BY department;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Department average includes 0% bonus', 'input': '', 'expected': 'Average metric correctly computed per group'}
        ],
        'bug_signature': 'WHERE bonus > 0 GROUP BY',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Filtering rows in a WHERE clause removes them from consideration before aggregate functions like AVG are computed.',
            'Review whether employees receiving zero bonus should be counted in the department average denominator.',
            'Remove `WHERE bonus > 0` so that all department employees are included in `AVG(bonus)`.'
        ],
        'topics': ['SQL', 'Aggregation', 'AVG'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL GROUP BY'],
        'status': 'published',
        'expected_query': 'SELECT department, AVG(bonus) AS avg_bonus FROM employees GROUP BY department ORDER BY department;'
    })

    # 56. Registration cleanup report flags unique accounts as duplicates
    challenges.append({
        'id': 56,
        'title': 'Registration Cleanup Report Flags Unique Accounts as Duplicates',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Database administrators alerted that an automated cleanup script flagged every single user account in the system for duplicate account merging."

### Bug Report
The duplicate account detection query identifies single-occurrence email addresses as duplicates, misclassifying unique accounts as redundant.

### Steps to Reproduce
1. Ingest user records containing unique email addresses alongside duplicate entries.
2. Execute `query.sql`.
3. Inspect the returned duplicate list.
4. Observe that unique email addresses with count = 1 are present in the duplicate report.

### Expected Behaviour
Return only email addresses associated with more than one account record, along with their occurrence count, ordered by email.

### Actual Behaviour
Group filtering captures single-occurrence unique accounts alongside genuine duplicates.

### Starter Files
`query.sql` - Scans user records for duplicate email addresses.
`schema.sql` - User registration table and sample accounts.

### Task
Correct the aggregation threshold in `query.sql` to isolate accounts with multiple occurrences.

### Acceptance Criteria
1. Projected columns: `email`, `count`.
2. Only emails with `count > 1` are returned.
3. Rows are ordered by `email` ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Filter criteria evaluated post-aggregation.
- Results sorted by `email` ascending.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100)
);

INSERT INTO users VALUES
(1, 'Alice', 'dup@test.com'),
(2, 'Bob', 'unique@test.com'),
(3, 'Charlie', 'dup@test.com');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT email, COUNT(*) AS count FROM users GROUP BY email HAVING COUNT(*) >= 1 ORDER BY email;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Only true duplicate emails returned', 'input': '', 'expected': 'Deduplicated groups satisfying having condition'}
        ],
        'bug_signature': 'HAVING COUNT(*) >= 1',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'A duplicate item in a relational table is defined by having a frequency count strictly greater than one.',
            'Inspect the comparison operator in the `HAVING` clause of `query.sql`.',
            'Change `COUNT(*) >= 1` to `COUNT(*) > 1`.'
        ],
        'topics': ['SQL', 'Duplicates', 'HAVING'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL HAVING Clause'],
        'status': 'published',
        'expected_query': 'SELECT email, COUNT(*) AS count FROM users GROUP BY email HAVING COUNT(*) > 1 ORDER BY email;'
    })

    # 57. Customer invoice tax sum truncates fractional pennies
    challenges.append({
        'id': 57,
        'title': 'Customer Invoice Tax Sum Truncates Fractional Pennies',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Billing accounting noted that customer sales tax invoices showed whole dollar integers instead of exact cents, failing automated sales tax compliance audits."

### Bug Report
The invoice sales tax calculation rounds the total tax to the nearest integer dollar, discarding fractional cents required for sales tax records.

### Steps to Reproduce
1. Ingest invoice items with standard decimal tax rates.
2. Execute `query.sql`.
3. Inspect the `total_tax` field value.
4. Observe that decimal cent values are rounded away to zero decimal places.

### Expected Behaviour
Aggregate line-item sales taxes rounded to two decimal places: `ROUND(SUM(subtotal * tax_rate), 2) AS total_tax`.

### Actual Behaviour
Tax calculations are rounded without decimal precision, truncating cent values.

### Starter Files
`query.sql` - Computes sales tax sums on customer invoice line items.
`schema.sql` - Invoice items and taxation rate data.

### Task
Modify `ROUND()` in `query.sql` to preserve two decimal places.

### Acceptance Criteria
1. Projected column: `total_tax`.
2. Tax total is rounded to exactly 2 decimal places.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output column alias: `total_tax`.
- Financial calculations must preserve 2 decimal places.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE invoice_items (
    id INT PRIMARY KEY,
    subtotal DECIMAL(10,2),
    tax_rate DECIMAL(4,4)
);

INSERT INTO invoice_items VALUES
(1, 10.50, 0.0825),
(2, 25.20, 0.0825);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT ROUND(SUM(subtotal * tax_rate)) AS total_tax FROM invoice_items;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Monetary total rounded to 2 decimal places', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'ROUND(SUM(subtotal * tax_rate))',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In standard SQL, `ROUND(value)` without a second parameter rounds to the nearest integer.',
            'Pass the desired scale as a second argument to `ROUND()` for monetary precision.',
            'Change to `ROUND(SUM(subtotal * tax_rate), 2)`.'
        ],
        'topics': ['SQL', 'Math', 'ROUND'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Math Functions'],
        'status': 'published',
        'expected_query': 'SELECT ROUND(SUM(subtotal * tax_rate), 2) AS total_tax FROM invoice_items;'
    })

    # 58. Executive sales metric dashboard includes cancelled transactions
    challenges.append({
        'id': 58,
        'title': 'Executive Sales Metric Dashboard Includes Cancelled Transactions',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"The CEO dashboard reported higher gross merchandise value (GMV) than actual settled revenue because orders canceled prior to fulfillment were included in total sales."

### Bug Report
The sales revenue query computes total order GMV without filtering by order fulfillment status, counting canceled transactions toward completed sales.

### Steps to Reproduce
1. Ingest orders with mixed status values (`completed`, `cancelled`).
2. Execute `query.sql`.
3. Compare the returned GMV against completed order totals.
4. Observe that canceled order amounts contribute to the total.

### Expected Behaviour
Calculate the total sum of `amount` as `completed_gmv` strictly for orders with status `'completed'`.

### Actual Behaviour
All order records contribute to the revenue sum regardless of status.

### Starter Files
`query.sql` - Calculates executive Gross Merchandise Value (GMV) metrics.
`schema.sql` - Order transaction tables and fulfillment statuses.

### Task
Add status filtering in `query.sql` to restrict GMV calculation to completed orders.

### Acceptance Criteria
1. Projected column: `completed_gmv`.
2. Canceled orders do not contribute to the sum.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Status filter is case-sensitive `'completed'`.
- Output column alias: `completed_gmv`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE orders (
    id INT PRIMARY KEY,
    amount DECIMAL(10,2),
    status VARCHAR(20)
);

INSERT INTO orders VALUES
(1, 100.00, 'completed'),
(2, 50.00, 'cancelled'),
(3, 200.00, 'completed');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT SUM(amount) AS completed_gmv FROM orders;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Total only includes completed orders', 'input': '', 'expected': 'Sum of GMV for completed orders only'}
        ],
        'bug_signature': 'SELECT SUM(amount) AS completed_gmv FROM orders;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Financial metrics must filter on status attributes to exclude cancelled, refunded, or fraudulent transactions.',
            'Notice that `query.sql` currently has no `WHERE` clause.',
            'Add `WHERE status = \'completed\'` to the query.'
        ],
        'topics': ['SQL', 'Filtering', 'Revenue'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE Clause'],
        'status': 'published',
        'expected_query': "SELECT SUM(amount) AS completed_gmv FROM orders WHERE status = 'completed';"
    })

    # 59. Emergency task dispatch ordering misplaces double-digit urgency levels
    challenges.append({
        'id': 59,
        'title': 'Emergency Task Dispatch Ordering Misplaces Double-Digit Urgency Levels',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Hospital dispatch operators reported that urgent priority level 10 tasks were pushed to the bottom of the dispatch queue below low-priority level 2 tasks."

### Bug Report
The task priority query sorts priority levels lexicographically as text strings, ordering priority 10 below priority 2 instead of by numerical urgency.

### Steps to Reproduce
1. Ingest tasks with priority levels stored as text (e.g. `'10'`, `'2'`, `'20'`, `'100'`).
2. Execute `query.sql`.
3. Inspect task ordering in the result set.
4. Observe that sorting follows alphabetical character sequence rather than numerical value.

### Expected Behaviour
Sort tasks by `priority_level` evaluated as integers in ascending order: `ORDER BY CAST(priority_level AS INTEGER) ASC`.

### Actual Behaviour
Text column sorting places `'10'` before `'2'` due to character code comparisons.

### Starter Files
`query.sql` - Dispatches operational tasks ordered by urgency priority.
`schema.sql` - Operational tasks and priority ratings.

### Task
Cast priority level to integer during sorting in `query.sql`.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `priority_level`.
2. Rows are ordered numerically by priority level ascending.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Numerical ordering must handle single and multi-digit levels correctly.
- Output columns: `id`, `name`, `priority_level`.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE tasks (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    priority_level VARCHAR(10)
);

INSERT INTO tasks VALUES
(1, 'Task A', '10'),
(2, 'Task B', '2'),
(3, 'Task C', '100'),
(4, 'Task D', '20');"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, priority_level FROM tasks ORDER BY priority_level ASC;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Tasks ordered by numerical priority level', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'ORDER BY priority_level ASC;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'String columns order alphabetically rather than numerically, placing \'10\' before \'2\'.',
            'SQL allows casting column data types inside the ORDER BY clause.',
            'Use `CAST(priority_level AS INTEGER)` in the `ORDER BY` clause.'
        ],
        'topics': ['SQL', 'Sorting', 'Type Casting'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL CAST and ORDER BY'],
        'status': 'published',
        'expected_query': 'SELECT id, name, priority_level FROM tasks ORDER BY CAST(priority_level AS INTEGER) ASC;'
    })

    # 60. Best-selling product card displays least-ordered inventory item
    challenges.append({
        'id': 60,
        'title': 'Best-Selling Product Card Displays Least-Ordered Inventory Item',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
"Marketing noticed that the home page 'Best Seller' banner featured a niche clearance item that had only sold 1 unit all month."

### Bug Report
The best-selling product query sorts sales volume in ascending order, featuring the lowest-selling item rather than the top-performing product.

### Steps to Reproduce
1. Ingest product sales records with varying `total_sold` volumes.
2. Execute `query.sql`.
3. Inspect the returned product record.
4. Observe that the product with the minimum sales count is returned.

### Expected Behaviour
Return the product record with the highest `total_sold` count using descending order and a limit of 1.

### Actual Behaviour
Ascending sort order returns the lowest-selling product.

### Starter Files
`query.sql` - Identifies the top-performing catalog product by sales volume.
`schema.sql` - Product catalog sales history.

### Task
Invert the sort direction in `query.sql` to return the highest-selling product.

### Acceptance Criteria
1. Projected columns: `id`, `name`, `total_sold`.
2. Returns the single top-selling product.

### Constraints
- Target Database: SQLite 3.35+ / ANSI SQL standard compliant.
- Output columns: `id`, `name`, `total_sold`.
- Row limit: 1.""",
        'files': [
            {
                'name': 'schema.sql',
                'content': """CREATE TABLE product_sales (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    total_sold INT
);

INSERT INTO product_sales VALUES
(1, 'Slow Mover', 1),
(2, 'Hot Item', 500),
(3, 'Average Seller', 50);"""
            },
            {
                'name': 'query.sql',
                'content': """SELECT id, name, total_sold FROM product_sales ORDER BY total_sold ASC LIMIT 1;"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Returns top selling item with highest count', 'input': '', 'expected': 'Accurate tabular result set satisfying problem criteria'}
        ],
        'bug_signature': 'ORDER BY total_sold ASC LIMIT 1;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Ascending order (`ASC`) orders from lowest to highest, while finding top performers requires ordering highest to lowest.',
            'Examine the sorting direction specified in `query.sql`.',
            'Change `ORDER BY total_sold ASC` to `ORDER BY total_sold DESC`.'
        ],
        'topics': ['SQL', 'Sorting', 'LIMIT'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL ORDER BY and LIMIT'],
        'status': 'published',
        'expected_query': 'SELECT id, name, total_sold FROM product_sales ORDER BY total_sold DESC LIMIT 1;'
    })

    return challenges
