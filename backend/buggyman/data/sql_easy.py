"""
SQL Lab: Easy Challenges (51 to 60)
"""

def get_sql_easy():
    challenges = []

    # 51. Customer report excludes records containing NULL values
    challenges.append({
        'id': 51,
        'title': '[SQL-E01] Customer Report Excludes Records Containing NULL Values',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A customer success team generates a contact list of all registered clients who have not opted out of marketing updates (`opt_out = 0` or NULL).

### Bug Report
Customers whose opt-out preference is unset (stored as `NULL` in the database) are completely missing from the campaign export.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe only customers with explicit `opt_out = 0` are returned.
3. Customers with `opt_out IS NULL` are omitted.

### Expected Behavior
Include both `opt_out = 0` and `opt_out IS NULL`.

### Actual Behavior
The condition `WHERE opt_out != 1` evaluates to `UNKNOWN` (falsy) for `NULL` values in SQL three-valued logic.

### Impact
Over 40% of the customer base is omitted from critical service announcements.

### Requirements
- Update `query.sql` to select `id`, `name`, `email` where `opt_out = 0 OR opt_out IS NULL` (or `COALESCE(opt_out, 0) = 0`).
""",
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
(4, 'Diana', 'diana@test.com', 0);
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Evaluates to UNKNOWN for NULL values, excluding Charlie
SELECT id, name, email FROM customers WHERE opt_out != 1;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Includes NULL and 0 opt-out records', 'input': '', 'expected': 'SELECT id, name, email FROM customers WHERE opt_out = 0 OR opt_out IS NULL ORDER BY id;'}
        ],
        'bug_signature': 'WHERE opt_out != 1',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'In SQL, `NULL != 1` evaluates to UNKNOWN, not TRUE.',
            'Change to `WHERE opt_out = 0 OR opt_out IS NULL` or `WHERE COALESCE(opt_out, 0) != 1`.'
        ],
        'topics': ['SQL', 'NULL Handling', 'Three-Valued Logic'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE Clause', 'NULLs in SQL'],
        'status': 'published',
        'expected_query': 'SELECT id, name, email FROM customers WHERE opt_out = 0 OR opt_out IS NULL ORDER BY id;'
    })

    # 52. Monthly revenue report uses the wrong date boundary
    challenges.append({
        'id': 52,
        'title': '[SQL-E02] Monthly Revenue Report Uses the Wrong Date Boundary',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A finance team generates the October 2026 revenue statement.

### Bug Report
Transactions processed on October 31st at 18:30 are missing from the report, under-reporting monthly revenue by $15,000!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `WHERE order_date BETWEEN '2026-10-01' AND '2026-10-31'`.
3. Datetime values on October 31st (e.g. `'2026-10-31 18:30:00'`) are excluded because `'2026-10-31'` evaluates to `'2026-10-31 00:00:00'`.

### Expected Behavior
Include all transactions from October 1st up to strictly before November 1st: `order_date >= '2026-10-01' AND order_date < '2026-11-01'`.

### Actual Behavior
BETWEEN with date-only string cuts off the final day at midnight.

### Impact
Incorrect revenue reported to investors and fiscal regulators.

### Requirements
- Use half-open range: `order_date >= '2026-10-01' AND order_date < '2026-11-01'`.
""",
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
(4, 300.00, '2026-11-01 09:00:00');
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Excludes afternoon orders on October 31st
SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date BETWEEN '2026-10-01' AND '2026-10-31';
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Total includes October 31st afternoon order', 'input': '', 'expected': "SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date >= '2026-10-01' AND order_date < '2026-11-01';"}
        ],
        'bug_signature': "BETWEEN '2026-10-01' AND '2026-10-31'",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Avoid `BETWEEN` for datetimes.',
            'Use half-open interval: `WHERE order_date >= \'2026-10-01\' AND order_date < \'2026-11-01\'`.'
        ],
        'topics': ['SQL', 'Dates', 'Half-Open Intervals'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Datetime'],
        'status': 'published',
        'expected_query': "SELECT SUM(amount) AS total_revenue FROM orders WHERE order_date >= '2026-10-01' AND order_date < '2026-11-01';"
    })

    # 53. Product search filters the wrong status
    challenges.append({
        'id': 53,
        'title': '[SQL-E03] Product Search Filters the Wrong Status',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An online catalog displays currently available products to customers.

### Bug Report
Items that are archived or pending approval appear in customer search, while in-stock active items are hidden.

### Steps to Reproduce
1. Query in `query.sql` uses `WHERE status = 'archived'`.
2. Active products are excluded.

### Expected Behavior
Filter specifically for `status = 'active'`.

### Actual Behavior
Filters for `status = 'archived'`.

### Impact
Customers cannot purchase active inventory; archived obsolete items are erroneously ordered.

### Requirements
- Update filter to `WHERE status = 'active'` and sort by `name ASC`.
""",
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
(3, 'Wireless Mouse', 25.00, 'active');
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Selects archived products instead of active products
SELECT id, name, price FROM products WHERE status = 'archived' ORDER BY name ASC;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Returns active products ordered by name', 'input': '', 'expected': "SELECT id, name, price FROM products WHERE status = 'active' ORDER BY name ASC;"}
        ],
        'bug_signature': "WHERE status = 'archived'",
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Change `WHERE status = \'archived\'` to `WHERE status = \'active\'`.'
        ],
        'topics': ['SQL', 'Filtering'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE Clause'],
        'status': 'published',
        'expected_query': "SELECT id, name, price FROM products WHERE status = 'active' ORDER BY name ASC;"
    })

    # 54. An INNER JOIN removes customers without orders
    challenges.append({
        'id': 54,
        'title': '[SQL-E04] An INNER JOIN Removes Customers Without Orders',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A customer marketing team wants a complete user roster showing their order counts, including new users who haven't placed an order yet.

### Bug Report
New users (0 orders) are completely omitted from the user roster!

### Steps to Reproduce
1. Customer "Charlie" registered yesterday and has 0 orders.
2. Query in `query.sql` uses `INNER JOIN orders`.
3. Charlie is omitted from the result set.

### Expected Behavior
All customers must appear. Customers without orders should show `order_id = NULL` or `0` orders.

### Actual Behavior
`INNER JOIN` drops customers who have no matching rows in the `orders` table.

### Impact
Customer onboarding emails are not triggered for new signups who haven't bought yet.

### Requirements
- Change `INNER JOIN` to `LEFT JOIN` to preserve all customers.
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
INSERT INTO orders VALUES (101, 1, 50.00), (102, 2, 75.00);
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: INNER JOIN removes Charlie (who has 0 orders)
SELECT c.id, c.name, o.id AS order_id FROM customers c INNER JOIN orders o ON c.id = o.customer_id ORDER BY c.id;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: LEFT JOIN includes Charlie with NULL order_id', 'input': '', 'expected': 'SELECT c.id, c.name, o.id AS order_id FROM customers c LEFT JOIN orders o ON c.id = o.customer_id ORDER BY c.id;'}
        ],
        'bug_signature': 'INNER JOIN orders o',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Change `INNER JOIN` to `LEFT JOIN`.'
        ],
        'topics': ['SQL', 'Joins', 'LEFT JOIN'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Joins'],
        'status': 'published',
        'expected_query': 'SELECT c.id, c.name, o.id AS order_id FROM customers c LEFT JOIN orders o ON c.id = o.customer_id ORDER BY c.id;'
    })

    # 55. A GROUP BY query calculates the wrong average
    challenges.append({
        'id': 55,
        'title': '[SQL-E05] A GROUP BY Query Calculates the Wrong Average',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An HR performance dashboard calculates the average bonus percentage awarded across departments.

### Bug Report
Employees who received $0 bonus are omitted from the average, artificially inflating the department's bonus metric.

### Steps to Reproduce
1. Department has 2 employees: Alice received 10%, Bob received 0% (or NULL).
2. Query filters `WHERE bonus > 0` before running `AVG(bonus)`.
3. Average returns 10% instead of true average 5%.

### Expected Behavior
Average must include all department employees, counting zero/missing bonus as 0.

### Actual Behavior
Filters out 0 values before aggregation.

### Impact
HR leadership relies on inflated compensation metrics during budget planning.

### Requirements
- Calculate `AVG(COALESCE(bonus, 0))` grouped by `department` without excluding zero-bonus rows.
""",
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
(4, 'Sales', 10.0);
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: WHERE clause removes 0.0 bonus employees before AVG
SELECT department, AVG(bonus) AS avg_bonus FROM employees WHERE bonus > 0 GROUP BY department ORDER BY department;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Department average includes 0% bonus', 'input': '', 'expected': 'SELECT department, AVG(bonus) AS avg_bonus FROM employees GROUP BY department ORDER BY department;'}
        ],
        'bug_signature': 'WHERE bonus > 0 GROUP BY',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Remove `WHERE bonus > 0` so that employees with 0 bonus are included in the average.'
        ],
        'topics': ['SQL', 'Aggregation', 'AVG'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL GROUP BY'],
        'status': 'published',
        'expected_query': 'SELECT department, AVG(bonus) AS avg_bonus FROM employees GROUP BY department ORDER BY department;'
    })

    # 56. Duplicate email records are not detected correctly
    challenges.append({
        'id': 56,
        'title': '[SQL-E06] Duplicate Email Records Are Not Detected Correctly',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A data cleanup pipeline scans user registration databases to identify accounts sharing duplicate email addresses.

### Bug Report
The duplicate detection script returns every single email address in the database, including unique ones!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `HAVING COUNT(*) >= 1`.
3. Unique accounts with count = 1 are incorrectly returned.

### Expected Behavior
Only emails with `COUNT(*) > 1` (more than one occurrence) are duplicates.

### Actual Behavior
Uses `>= 1` which matches every single row.

### Impact
Unique accounts are incorrectly flagged for deletion or account merge.

### Requirements
- Change condition to `HAVING COUNT(*) > 1`.
""",
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
(3, 'Charlie', 'dup@test.com');
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Uses >= 1 instead of > 1, flagging unique emails
SELECT email, COUNT(*) AS count FROM users GROUP BY email HAVING COUNT(*) >= 1 ORDER BY email;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Only true duplicate emails returned', 'input': '', 'expected': 'SELECT email, COUNT(*) AS count FROM users GROUP BY email HAVING COUNT(*) > 1 ORDER BY email;'}
        ],
        'bug_signature': 'HAVING COUNT(*) >= 1',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Change `HAVING COUNT(*) >= 1` to `HAVING COUNT(*) > 1`.'
        ],
        'topics': ['SQL', 'Duplicates', 'HAVING'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL HAVING Clause'],
        'status': 'published',
        'expected_query': 'SELECT email, COUNT(*) AS count FROM users GROUP BY email HAVING COUNT(*) > 1 ORDER BY email;'
    })

    # 57. An invoice query incorrectly rounds monetary totals
    challenges.append({
        'id': 57,
        'title': '[SQL-E07] An Invoice Query Incorrectly Rounds Monetary Totals',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An invoicing database computes tax totals across order line items.

### Bug Report
Invoices report fractional penny differences from bank statements because line items are rounded to integer dollars rather than 2 decimal places.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `ROUND(SUM(subtotal * tax_rate))` without decimal argument.
3. Totals are truncated to whole dollars.

### Expected Behavior
Round currency to exactly 2 decimal places: `ROUND(..., 2)`.

### Actual Behavior
Rounds to 0 decimal places.

### Impact
Accounting ledger totals fail to reconcile with stripe merchant payouts.

### Requirements
- Update query to `ROUND(SUM(subtotal * tax_rate), 2) AS total_tax`.
""",
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
(2, 25.20, 0.0825);
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Rounds to integer dollar instead of 2 decimal places
SELECT ROUND(SUM(subtotal * tax_rate)) AS total_tax FROM invoice_items;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Monetary total rounded to 2 decimal places', 'input': '', 'expected': 'SELECT ROUND(SUM(subtotal * tax_rate), 2) AS total_tax FROM invoice_items;'}
        ],
        'bug_signature': 'ROUND(SUM(subtotal * tax_rate))',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `, 2` to the `ROUND()` function: `ROUND(SUM(subtotal * tax_rate), 2)`.'
        ],
        'topics': ['SQL', 'Math', 'ROUND'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL Math Functions'],
        'status': 'published',
        'expected_query': 'SELECT ROUND(SUM(subtotal * tax_rate), 2) AS total_tax FROM invoice_items;'
    })

    # 58. A report includes cancelled orders
    challenges.append({
        'id': 58,
        'title': '[SQL-E08] A Report Includes Cancelled Orders',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An executive sales metric dashboard calculates daily net gross merchandise value (GMV).

### Bug Report
Cancelled and refunded orders are included in the sales GMV calculation, inflating daily performance numbers.

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice cancelled orders with `status = 'cancelled'` are summed.

### Expected Behavior
Only orders with `status = 'completed'` (or `status != 'cancelled'`) should be summed.

### Actual Behavior
Sums all rows in `orders` regardless of status.

### Impact
Management bases hiring decisions on inflated gross sales numbers.

### Requirements
- Add `WHERE status = 'completed'` to the total revenue query.
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
(1, 100.00, 'completed'),
(2, 50.00, 'cancelled'),
(3, 200.00, 'completed');
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Includes cancelled orders in GMV
SELECT SUM(amount) AS completed_gmv FROM orders;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Total only includes completed orders', 'input': '', 'expected': "SELECT SUM(amount) AS completed_gmv FROM orders WHERE status = 'completed';"}
        ],
        'bug_signature': 'SELECT SUM(amount) AS completed_gmv FROM orders;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Add `WHERE status = \'completed\'` to the query.'
        ],
        'topics': ['SQL', 'Filtering', 'Revenue'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL WHERE Clause'],
        'status': 'published',
        'expected_query': "SELECT SUM(amount) AS completed_gmv FROM orders WHERE status = 'completed';"
    })

    # 59. A query orders numeric values stored as text incorrectly
    challenges.append({
        'id': 59,
        'title': '[SQL-E09] A Query Orders Numeric Values Stored as Text Incorrectly',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A priority dispatch queue sorts tasks by urgency score (`priority_level`), which is stored in a `VARCHAR` column in a legacy table.

### Bug Report
Tasks order as `'10', '100', '2', '20'` instead of `'2', '10', '20', '100'`!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Observe alphabetical string sorting of numbers.

### Expected Behavior
Order rows by numerical value: `ORDER BY CAST(priority_level AS INTEGER) ASC`.

### Actual Behavior
Orders by textual lexicographical ASCII value.

### Impact
Urgent priority 100 emergency repairs are placed after minor priority 2 maintenance requests.

### Requirements
- Cast `priority_level` to `INTEGER` in the `ORDER BY` clause.
""",
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
(4, 'Task D', '20');
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Sorts VARCHAR priority alphabetically
SELECT id, name, priority_level FROM tasks ORDER BY priority_level ASC;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Tasks ordered by numerical priority level', 'input': '', 'expected': 'SELECT id, name, priority_level FROM tasks ORDER BY CAST(priority_level AS INTEGER) ASC;'}
        ],
        'bug_signature': 'ORDER BY priority_level ASC;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Use `CAST(priority_level AS INTEGER)` in the `ORDER BY` clause.'
        ],
        'topics': ['SQL', 'Sorting', 'Type Casting'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL CAST and ORDER BY'],
        'status': 'published',
        'expected_query': 'SELECT id, name, priority_level FROM tasks ORDER BY CAST(priority_level AS INTEGER) ASC;'
    })

    # 60. A query returns the wrong top-selling product because of incorrect sorting
    challenges.append({
        'id': 60,
        'title': '[SQL-E10] A Query Returns the Wrong Top-Selling Product Because of Incorrect Sorting',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An inventory re-ordering dashboard highlights the #1 best-selling product of the week.

### Bug Report
The dashboard displays the least-sold item (1 unit sold) as the "Top Seller" instead of the actual best-selling item (500 units sold)!

### Steps to Reproduce
1. Execute query in `query.sql`.
2. Notice `ORDER BY total_sold ASC LIMIT 1`.
3. Lowest seller is returned.

### Expected Behavior
Order by `total_sold DESC LIMIT 1` to retrieve the highest seller.

### Actual Behavior
Sorts `ASC` (ascending).

### Impact
Factory re-orders large batches of unsold inventory while popular stock runs out.

### Requirements
- Update sort direction to `DESC` to return top seller.
""",
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
(3, 'Average Seller', 50);
"""
            },
            {
                'name': 'query.sql',
                'content': """-- BUG: Orders ASC instead of DESC
SELECT id, name, total_sold FROM product_sales ORDER BY total_sold ASC LIMIT 1;
"""
            }
        ],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Returns top selling item with highest count', 'input': '', 'expected': 'SELECT id, name, total_sold FROM product_sales ORDER BY total_sold DESC LIMIT 1;'}
        ],
        'bug_signature': 'ORDER BY total_sold ASC LIMIT 1;',
        'suspected_component': 'query.sql',
        'ai_suggestions': [
            'Change `ORDER BY total_sold ASC` to `ORDER BY total_sold DESC`.'
        ],
        'topics': ['SQL', 'Sorting', 'LIMIT'],
        'skills_tested': ['SQL', 'Database'],
        'prerequisites': ['SQL ORDER BY and LIMIT'],
        'status': 'published',
        'expected_query': 'SELECT id, name, total_sold FROM product_sales ORDER BY total_sold DESC LIMIT 1;'
    })

    return challenges
