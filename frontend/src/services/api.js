// Custom Fetch API Client with Mock Fallback for local testing when backend is not running
import { isValidEmail, getEmailValidationError } from '../utils/validators';

const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && envUrl !== '/api') {
    return envUrl.replace(/\/+$/, '');
  }
  // In production (Vercel, custom domain), always connect directly to live Render backend API
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const host = window.location.hostname.toLowerCase();
    if (host !== 'localhost' && host !== '127.0.0.1' && !host.startsWith('192.168.') && !host.startsWith('10.')) {
      return 'https://buggyman-completed.onrender.com/api';
    }
  }
  return '/api';
};

const BASE_URL = getApiBaseUrl();
const ENABLE_MOCK_FALLBACK = import.meta.env.VITE_ENABLE_MOCK_FALLBACK !== undefined
  ? import.meta.env.VITE_ENABLE_MOCK_FALLBACK === 'true'
  : false;

const DJANGO_MOCK_CHALLENGES = [
  {
    id: 'DJ-E01',
    title: 'Login API returns "Invalid Credentials" for valid users',
    description: 'A Django login endpoint rejects valid credentials because of incorrect authentication logic.',
    difficulty: 'Easy',
    technology: 'Django',
    category: 'Authentication',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      { name: 'views.py', content: 'Check login authentication flow for correct password verification and user lookup.' }
    ]
  },
  {
    id: 'DJ-E02',
    title: 'User registration doesn\'t save to database',
    description: 'The registration view accepts valid input but fails to persist the new user record.',
    difficulty: 'Easy',
    technology: 'Django',
    category: 'ORM',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      { name: 'views.py', content: 'Ensure newly created User instances are saved with `user.save()` or created via `create_user()`.' }
    ]
  },
  {
    id: 'DJ-E03',
    title: 'Missing CSRF token on form submission',
    description: 'A form POST fails because the CSRF token is not included in the template output.',
    difficulty: 'Easy',
    technology: 'Django',
    category: 'Security',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      { name: 'template.html', content: 'Add `{% csrf_token %}` inside all POST forms when CSRF middleware is enabled.' }
    ]
  },
  {
    id: 'DJ-E04',
    title: 'Static files (CSS/JS) not loading',
    description: 'Static assets are missing because Django static file settings or URL routing is incorrect.',
    difficulty: 'Easy',
    technology: 'Django',
    category: 'Configuration',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      { name: 'settings.py', content: 'Verify STATIC_URL, STATICFILES_DIRS, and static files handling in the project settings.' }
    ]
  },
  {
    id: 'DJ-M01',
    title: 'URL returns 404 due to incorrect routing',
    description: 'A valid view is unreachable because its URL pattern is misconfigured or omitted from urlpatterns.',
    difficulty: 'Medium',
    technology: 'Django',
    category: 'URL Routing',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      { name: 'urls.py', content: 'Ensure the view path is registered and included in the application URL configuration.' }
    ]
  },
  {
    id: 'DJ-M02',
    title: 'Password isn\'t hashed before saving',
    description: 'Passwords are stored as plain text because Django\'s `set_password` is not used.',
    difficulty: 'Medium',
    technology: 'Django',
    category: 'Authentication',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      { name: 'models.py', content: 'Use `user.set_password(password)` before saving users, rather than assigning the raw password string.' }
    ]
  },
  {
    id: 'DJ-M03',
    title: 'Serializer missing required fields',
    description: 'A DRF serializer omits required fields, causing otherwise valid POST payloads to fail validation.',
    difficulty: 'Medium',
    technology: 'Django REST Framework',
    category: 'Django REST Framework',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      { name: 'serializers.py', content: 'Verify the serializer includes all required model fields and that required=True is set where needed.' }
    ]
  },
  {
    id: 'DJ-H01',
    title: 'Permission class accidentally allows admin bypass',
    description: 'A custom permission check is flawed and lets unauthorized users bypass the intended admin-only restrictions.',
    difficulty: 'Hard',
    technology: 'Django',
    category: 'Permissions',
    timeEstimate: '25 mins',
    points: 250,
    files: [
      { name: 'permissions.py', content: 'Review the permission logic and ensure the negative branch does not grant access unexpectedly.' }
    ]
  },
  {
    id: 'DJ-H02',
    title: 'Transaction rollback leaves partial data behind',
    description: 'A bulk operation fails midway and leaves the database in a partially updated state because transactions are not handled correctly.',
    difficulty: 'Hard',
    technology: 'Django',
    category: 'Transactions',
    timeEstimate: '25 mins',
    points: 250,
    files: [
      { name: 'views.py', content: 'Wrap the mutation sequence in a transaction and ensure rollback occurs on failure.' }
    ]
  },
  {
    id: 'DJ-H03',
    title: 'Cache invalidation breaks after model update',
    description: 'A model change does not invalidate the cached response, so stale data continues to be served to the API.',
    difficulty: 'Hard',
    technology: 'Django',
    category: 'Caching',
    timeEstimate: '25 mins',
    points: 250,
    files: [
      { name: 'views.py', content: 'Clear or update the cache whenever the underlying model data changes.' }
    ]
  }
];

const SQL_MOCK_CHALLENGES = [
  {
    id: 'SQL-E01',
    title: 'Incorrect WHERE clause returns extra records',
    description: 'A SELECT query returns too many rows because the WHERE expression is missing parentheses or uses an incorrect operator.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Query',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'query.sql',
        content: `-- BUG: Missing required WHERE condition
SELECT * FROM orders;`
      }
    ],
    testCases: [
      { id: 1, name: 'Filters rows correctly', input: '', expected: 'WHERE clause present', passed: false }
    ],
    bugSignature: 'SELECT * FROM orders;',
    suspectedComponent: 'query.sql',
    aiSuggestions: ['Add a proper WHERE clause to restrict results to the intended rows.']
  },
  {
    id: 'SQL-E02',
    title: 'ORDER BY sorts incorrectly',
    description: 'Results are sorted in the wrong order because the ORDER BY uses the wrong field or missing direction.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Sorting',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'report.sql',
        content: `-- BUG: ORDER BY uses wrong column
SELECT name, price FROM products ORDER BY created_at;`
      }
    ],
    testCases: [
      { id: 1, name: 'Orders by correct column', input: '', expected: 'ORDER BY price', passed: false }
    ],
    bugSignature: 'ORDER BY created_at;',
    suspectedComponent: 'report.sql',
    aiSuggestions: ['Order by the intended field, such as price, for the correct sort order.']
  },
  {
    id: 'SQL-E03',
    title: 'Missing PRIMARY KEY',
    description: 'A table has no PRIMARY KEY constraint, causing duplicate rows and unreliable joins.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Schema',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'schema.sql',
        content: `-- BUG: users table defined without a primary key
CREATE TABLE users (
  username VARCHAR(50),
  email VARCHAR(100)
);`
      }
    ],
    testCases: [
      { id: 1, name: 'Defines a primary key', input: '', expected: 'PRIMARY KEY (username)', passed: false }
    ],
    bugSignature: 'CREATE TABLE users (',
    suspectedComponent: 'schema.sql',
    aiSuggestions: ['Add a PRIMARY KEY constraint to the table definition.']
  },
  {
    id: 'SQL-E04',
    title: 'Duplicate usernames allowed',
    description: 'The users table lacks a UNIQUE constraint on username, allowing duplicate accounts.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Constraints',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'schema.sql',
        content: `-- BUG: Missing UNIQUE constraint on username
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(50),
  email VARCHAR(100)
);`
      }
    ],
    testCases: [
      { id: 1, name: 'Username uniqueness enforced', input: '', expected: 'UNIQUE(username)', passed: false }
    ],
    bugSignature: 'CREATE TABLE users (',
    suspectedComponent: 'schema.sql',
    aiSuggestions: ['Add UNIQUE(username) to prevent duplicate username values.']
  },
  {
    id: 'SQL-M01',
    title: 'GROUP BY omits aggregate column',
    description: 'A report query fails because the SELECT list includes a non-aggregated column without a corresponding GROUP BY expression.',
    difficulty: 'Medium',
    technology: 'SQL',
    category: 'Aggregation',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      {
        name: 'sales_report.sql',
        content: `-- BUG: Missing GROUP BY column
SELECT region, SUM(amount) FROM sales GROUP BY region;`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses GROUP BY correctly', input: '', expected: 'SELECT region, SUM(amount)', passed: false }
    ],
    bugSignature: 'SELECT region, SUM(amount) FROM sales GROUP BY region;',
    suspectedComponent: 'sales_report.sql',
    aiSuggestions: ['Ensure every non-aggregated field in SELECT appears in GROUP BY.']
  },
  {
    id: 'SQL-M02',
    title: 'JOIN duplicates rows unexpectedly',
    description: 'A multi-table join returns duplicate records because the join condition is too broad or the join type is incorrect.',
    difficulty: 'Medium',
    technology: 'SQL',
    category: 'Joins',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      {
        name: 'nested_join.sql',
        content: `-- BUG: Join missing proper ON condition
SELECT o.id, c.name FROM orders o JOIN customers c;`
      }
    ],
    testCases: [
      { id: 1, name: 'Joins with explicit conditions', input: '', expected: 'JOIN customers c ON o.customer_id = c.id', passed: false }
    ],
    bugSignature: 'JOIN customers c;',
    suspectedComponent: 'nested_join.sql',
    aiSuggestions: ['Add the missing ON clause and ensure the join condition is specific.']
  },
  {
    id: 'SQL-M03',
    title: 'HAVING used instead of WHERE',
    description: 'A filter on aggregated results is applied in the wrong clause, so the final output is incorrect.',
    difficulty: 'Medium',
    technology: 'SQL',
    category: 'Filtering',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      {
        name: 'aggregate.sql',
        content: `-- BUG: HAVING should be used after aggregation, but the expression should reference grouped columns
SELECT product_id, SUM(quantity) FROM orders HAVING quantity > 10;`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses WHERE before aggregation', input: '', expected: 'WHERE quantity > 10', passed: false }
    ],
    bugSignature: 'HAVING quantity > 10;',
    suspectedComponent: 'aggregate.sql',
    aiSuggestions: ['Move the filter to WHERE when filtering rows before aggregation.']
  },
  {
    id: 'SQL-H01',
    title: 'Window function partitions incorrectly',
    description: 'A ranking query uses the wrong PARTITION BY clause, causing each row to be compared against the wrong group.',
    difficulty: 'Hard',
    technology: 'SQL',
    category: 'Window Functions',
    timeEstimate: '25 mins',
    points: 250,
    files: [
      {
        name: 'ranking.sql',
        content: `-- BUG: Window function partitions on the wrong field
SELECT *, RANK() OVER (PARTITION BY department ORDER BY salary DESC) FROM employee_metrics;`
      }
    ],
    testCases: [
      { id: 1, name: 'Partitions by correct field', input: '', expected: 'PARTITION BY department', passed: false }
    ],
    bugSignature: 'PARTITION BY department ORDER BY salary DESC',
    suspectedComponent: 'ranking.sql',
    aiSuggestions: ['Validate the partition key is correct for the ranking calculation.']
  },
  {
    id: 'SQL-H02',
    title: 'Recursive CTE repeats indefinitely',
    description: 'A recursive CTE does not include a termination condition, producing an endless recursion loop.',
    difficulty: 'Hard',
    technology: 'SQL',
    category: 'CTE',
    timeEstimate: '25 mins',
    points: 250,
    files: [
      {
        name: 'hierarchy.sql',
        content: `-- BUG: Recursive CTE missing termination condition
WITH RECURSIVE manager_path AS (
  SELECT id, manager_id FROM org_chart
  UNION ALL
  SELECT o.id, o.manager_id FROM org_chart o JOIN manager_path mp ON o.manager_id = mp.id
)
SELECT * FROM manager_path;`
      }
    ],
    testCases: [
      { id: 1, name: 'Adds termination condition', input: '', expected: 'WHERE manager_id IS NULL', passed: false }
    ],
    bugSignature: 'WITH RECURSIVE manager_path AS (',
    suspectedComponent: 'hierarchy.sql',
    aiSuggestions: ['Include a base case and termination filter in the recursive CTE.']
  },
  {
    id: 'SQL-H03',
    title: 'Index hint prevents plan reuse',
    description: 'A query uses the wrong index hint and performs a full table scan even though a better index exists.',
    difficulty: 'Hard',
    technology: 'SQL',
    category: 'Performance',
    timeEstimate: '25 mins',
    points: 250,
    files: [
      {
        name: 'query.sql',
        content: `-- BUG: Wrong index hint forces an inefficient scan
SELECT * FROM events FORCE INDEX (idx_old_date) WHERE event_date > CURRENT_DATE - INTERVAL 7 DAY;`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses correct index hint', input: '', expected: 'FORCE INDEX (idx_event_date)', passed: false }
    ],
    bugSignature: 'FORCE INDEX (idx_old_date)',
    suspectedComponent: 'query.sql',
    aiSuggestions: ['Use the more appropriate index for the queried column.']
  }
];

const FRONTEND_MOCK_CHALLENGES = [
  {
    id: 'RE-E01',
    title: 'Counter state doesn\'t update',
    description: 'A React counter component fails to re-render because state is mutated directly rather than updated immutably.',
    difficulty: 'Easy',
    technology: 'React',
    category: 'State',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'Counter.jsx',
        content: `import React, { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  const increment = () => {
    count = count + 1; // BUG: Mutating state directly
    setCount(count);
  };

  return <button onClick={increment}>{count}</button>;
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses state setter correctly', input: '', expected: 'setCount(count + 1)', passed: false }
    ],
    bugSignature: 'count = count + 1;',
    suspectedComponent: 'Counter.jsx',
    aiSuggestions: ['Do not mutate state directly; use `setCount(prev => prev + 1)` instead.']
  },
  {
    id: 'RE-E02',
    title: 'Form validation never displays errors',
    description: 'A form validation handler computes errors correctly but the UI never renders them.',
    difficulty: 'Easy',
    technology: 'React',
    category: 'Forms',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'SignupForm.jsx',
        content: `import React, { useState } from 'react';

export default function SignupForm() {
  const [errors] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    // BUG: validation errors are never stored or displayed
  };

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">Submit</button>
    </form>
  );
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Renders validation messages', input: '', expected: 'errors.email', passed: false }
    ],
    bugSignature: 'const [errors] = useState({});',
    suspectedComponent: 'SignupForm.jsx',
    aiSuggestions: ['Use state setter to update errors and display them below the form fields.']
  },
  {
    id: 'RE-E03',
    title: 'Navbar links don\'t navigate',
    description: 'React Router links appear in the navigation bar but clicks do not change routes due to a missing Link component or wrong path.',
    difficulty: 'Easy',
    technology: 'React Router',
    category: 'React Router',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'Navbar.jsx',
        content: `import React from 'react';

export default function Navbar() {
  return (
    <nav>
      <a href="/dashboard">Dashboard</a>
      <a href="/profile">Profile</a>
    </nav>
  );
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses React Router Link', input: '', expected: '<Link', passed: false }
    ],
    bugSignature: '<a href="/dashboard">',
    suspectedComponent: 'Navbar.jsx',
    aiSuggestions: ['Replace anchor tags with React Router `<Link to="...">` components for client-side routing.']
  },
  {
    id: 'RE-E04',
    title: 'Button click handler not working',
    description: 'A button render is fine but the onClick callback never fires due to incorrect binding or missing handler reference.',
    difficulty: 'Easy',
    technology: 'React',
    category: 'Events',
    timeEstimate: '10 mins',
    points: 100,
    files: [
      {
        name: 'ActionButton.jsx',
        content: `import React from 'react';

export default function ActionButton() {
  function handleClick() {
    console.log('clicked');
  }

  return <button onClick={handleclck}>Click me</button>; // BUG: typo in handler
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses correct handler reference', input: '', expected: 'onClick={handleClick}', passed: false }
    ],
    bugSignature: 'onClick={handleclck}',
    suspectedComponent: 'ActionButton.jsx',
    aiSuggestions: ['Fix the typo so the button references the correct handler function.']
  },
  {
    id: 'RE-M01',
    title: 'Image fails to load',
    description: 'An image asset is referenced incorrectly, causing a broken image placeholder in the UI.',
    difficulty: 'Medium',
    technology: 'Web',
    category: 'Assets',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      {
        name: 'Avatar.jsx',
        content: `import React from 'react';

export default function Avatar() {
  return <img src="/avatars/profile.png" alt="Profile" />; // BUG: wrong public asset path
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Loads correct image asset', input: '', expected: 'src="/assets/avatars/profile.png"', passed: false }
    ],
    bugSignature: 'src="/avatars/profile.png"',
    suspectedComponent: 'Avatar.jsx',
    aiSuggestions: ['Update the image path to the correct public asset location.']
  },
  {
    id: 'RE-M02',
    title: 'Input field doesn\'t update value',
    description: 'A controlled input does not reflect user typing because its value prop is not linked to state correctly.',
    difficulty: 'Medium',
    technology: 'React',
    category: 'Controlled Components',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      {
        name: 'SearchInput.jsx',
        content: `import React, { useState } from 'react';

export default function SearchInput() {
  const [search, setSearch] = useState('');

  return (
    <input value="" onChange={(e) => setSearch(e.target.value)} placeholder="Search" /> // BUG: value hardcoded to empty string
  );
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses state for input value', input: '', expected: 'value={search}', passed: false }
    ],
    bugSignature: 'value=""',
    suspectedComponent: 'SearchInput.jsx',
    aiSuggestions: ['Bind the input value to the component state variable instead of a fixed empty string.']
  },
  {
    id: 'RE-M03',
    title: 'Dark mode toggle resets on refresh',
    description: 'The theme toggle works, but the selection is not persisted, so the UI resets after page reload.',
    difficulty: 'Medium',
    technology: 'React',
    category: 'Local Storage',
    timeEstimate: '15 mins',
    points: 150,
    files: [
      {
        name: 'ThemeToggle.jsx',
        content: `import React, { useState } from 'react';

export default function ThemeToggle() {
  const [darkMode, setDarkMode] = useState(false);

  const toggle = () => {
    setDarkMode(!darkMode);
  };

  return <button onClick={toggle}>{darkMode ? 'Dark' : 'Light'}</button>;
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Persists theme selection', input: '', expected: 'localStorage.setItem', passed: false }
    ],
    bugSignature: 'const [darkMode, setDarkMode] = useState(false);',
    suspectedComponent: 'ThemeToggle.jsx',
    aiSuggestions: ['Save theme selection to localStorage and initialize the state from persisted preference.']
  },
  {
    id: 'RE-H01',
    title: 'Modal closes unexpectedly on backdrop click',
    description: 'A modal dialog closes as soon as the overlay is clicked, breaking the expected interaction flow.',
    difficulty: 'Hard',
    technology: 'React',
    category: 'Accessibility',
    timeEstimate: '20 mins',
    points: 250,
    files: [
      {
        name: 'Modal.jsx',
        content: `import React from 'react';

export default function Modal({ onClose }) {
  return (
    <div className="backdrop" onClick={onClose}> // BUG: closes when clicking inside modal content too
      <div className="modal-content">Modal body</div>
    </div>
  );
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Only backdrop clicks close modal', input: '', expected: 'event.stopPropagation', passed: false }
    ],
    bugSignature: 'onClick={onClose}',
    suspectedComponent: 'Modal.jsx',
    aiSuggestions: ['Stop propagation on modal content clicks so only the backdrop closes the dialog.']
  },
  {
    id: 'RE-H02',
    title: 'Dashboard list shows stale data after refresh',
    description: 'A list component keeps rendering old data because the data-fetch effect is not invalidating correctly.',
    difficulty: 'Hard',
    technology: 'React',
    category: 'Data Fetching',
    timeEstimate: '20 mins',
    points: 250,
    files: [
      {
        name: 'DataList.jsx',
        content: `import React, { useState, useEffect } from 'react';

export default function DataList() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const response = await fetch('/api/items');
    const data = await response.json();
    setItems(data);
  };

  return <ul>{items.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Refreshes data on demand', input: '', expected: 'useEffect(() => { fetchData(); }, [/* deps */])', passed: false }
    ],
    bugSignature: 'useEffect(() => {',
    suspectedComponent: 'DataList.jsx',
    aiSuggestions: ['Ensure the effect dependencies are set correctly or provide a refresh mechanism.']
  },
  {
    id: 'RE-H03',
    title: 'Responsive grid collapses on mobile',
    description: 'A card layout breaks on smaller screens because the flexbox and grid breakpoint rules are not applied correctly.',
    difficulty: 'Hard',
    technology: 'CSS',
    category: 'Responsive Layout',
    timeEstimate: '20 mins',
    points: 250,
    files: [
      {
        name: 'grid.css',
        content: `/* BUG: Missing mobile breakpoint styles */
.cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .cards {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}`
      }
    ],
    testCases: [
      { id: 1, name: 'Uses responsive columns for mobile', input: '', expected: 'grid-template-columns: repeat(1, minmax(0, 1fr))', passed: false }
    ],
    bugSignature: 'grid-template-columns: repeat(4, minmax(0, 1fr));',
    suspectedComponent: 'grid.css',
    aiSuggestions: ['Change the mobile breakpoint to use a single column layout for narrow screens.']
  }
];

// Initial Mock Database stored in LocalStorage for persistence during mock testing
const INITIAL_MOCK_DATA = {
  challenges: [
    {
      id: '1',
      title: '1. Dark/Light Theme',
      description: 'Add a Dark Mode and Light Mode toggle.\n\nRequirements:\n- Toggle should be available in the navbar.\n- Save the user\'s preference in localStorage.\n- Theme should persist after refresh.\n- Add smooth transition animations.\n- Do not break existing UI.',
      difficulty: 'Easy',
      technology: 'CSS',
      category: 'CSS Grid & Responsive',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'ThemeToggle.css',
          content: `/* BUG: Missing standard CSS variable transition and theme selector fallback */\n:root {\n  --bg-primary: #ffffff;\n  --text-primary: #0f172a;\n}\n[data-theme="dark"] {\n  --bg-primary: #090d16;\n  --text-primary: #f8fafc;\n}\n.theme-container {\n  background-color: var(--bg-primary);\n  color: var(--text-primary);\n  /* Buggy code below */\n  transition: none;\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Uses transitions for smooth changes', input: '', expected: 'transition: background-color', passed: false }
      ],
      bugSignature: 'transition: none;',
      suspectedComponent: 'ThemeToggle.css',
      aiSuggestions: [
        'Change `transition: none;` to a smooth transition like `transition: background-color 0.3s ease, color 0.3s ease;`.'
      ]
    },
    {
      id: '2',
      title: '2. Search Bugs',
      description: 'Add a search bar to filter bugs.\n\nRequirements:\n- Search by title.\n- Search updates in real time.\n- Case insensitive.\n- If nothing matches, show "No bugs found."',
      difficulty: 'Easy',
      technology: 'React',
      category: 'Search',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'BugSearch.jsx',
          content: `import React, { useState } from 'react';\n\nexport default function BugSearch({ bugs }) {\n  const [query, setQuery] = useState('');\n\n  // BUG: Case sensitive filter that crashes if bug has no title\n  const filteredBugs = bugs.filter(bug => bug.title.includes(query));\n\n  return (\n    <div className="p-4">\n      <input \n        type="text" \n        value={query} \n        onChange={(e) => setQuery(e.target.value)}\n        className="w-full p-2 border rounded-lg bg-slate-900 text-white"\n        placeholder="Search bugs..."\n      />\n      {filteredBugs.length === 0 ? (\n        <p className="text-slate-400 mt-4">No bugs found.</p>\n      ) : (\n        <ul className="mt-4 space-y-2">\n          {filteredBugs.map(bug => <li key={bug.id} className="text-white">{bug.title}</li>)}\n        </ul>\n      )}\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Case-insensitive filtering', input: '', expected: '.toLowerCase()', passed: false }
      ],
      bugSignature: 'const filteredBugs = bugs.filter(bug => bug.title.includes(query));',
      suspectedComponent: 'BugSearch.jsx',
      aiSuggestions: [
        'Use `.toLowerCase()` to make search case-insensitive and handle safe access: `const filteredBugs = bugs.filter(bug => (bug.title || "").toLowerCase().includes(query.toLowerCase()));`'
      ]
    },
    {
      id: '3',
      title: '3. Bug Priority Colors',
      description: 'Improve the bug cards by showing appropriate priority badge colors: Low=Green, Medium=Orange, High=Red, Critical=Dark Red.',
      difficulty: 'Easy',
      technology: 'CSS',
      category: 'Styling & CSS',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'PriorityBadge.css',
          content: `/* BUG: Bad colors, Critical and High priorities are using the same plain red background */\n.badge-low {\n  background-color: #10b981; /* Green */\n}\n.badge-medium {\n  background-color: #f97316; /* Orange */\n}\n.badge-high {\n  background-color: #ef4444; /* Red */\n}\n.badge-critical {\n  background-color: #ef4444; /* BUG: Should be dark red */\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Critical badge uses dark red background', input: '', expected: 'background-color: #991b1b', passed: false }
      ],
      bugSignature: '.badge-critical {\n  background-color: #ef4444;',
      suspectedComponent: 'PriorityBadge.css',
      aiSuggestions: [
        'Change the background color of `.badge-critical` to a dark red hex code like `#991b1b` or `#7f1d1d`.'
      ]
    },
    {
      id: '4',
      title: '4. Toast Notifications',
      description: 'Replace alert() with modern toast notifications.\n\nRequirements:\n- Success\n- Error\n- Warning\n- Auto disappear after 3 seconds.',
      difficulty: 'Easy',
      technology: 'React',
      category: 'User Experience',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'ToastContainer.jsx',
          content: `import React, { useEffect } from 'react';\n\nexport default function Toast({ message, type, onClose }) {\n  useEffect(() => {\n    // BUG: Standard alert blocks JS thread, and missing automatic 3 second timeout dismissal\n    alert(\`\${type.toUpperCase()}: \${message}\`);\n    onClose();\n  }, [message, type, onClose]);\n\n  return (\n    <div className={\`p-4 rounded-lg text-white \${type === 'success' ? 'bg-emerald-600' : 'bg-rose-600'}\`}>\n      {message}\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Automatically dismisses after timeout', input: '', expected: 'setTimeout', passed: false }
      ],
      bugSignature: 'alert(`${type.toUpperCase()}: ${message}`);\n    onClose();',
      suspectedComponent: 'ToastContainer.jsx',
      aiSuggestions: [
        'Replace `alert(...)` with a timer: `const timer = setTimeout(onClose, 3000); return () => clearTimeout(timer);`.'
      ]
    },
    {
      id: '5',
      title: '5. Loading Spinner',
      description: 'Whenever data is being fetched or submitted, show a loading spinner, then hide it after the request completes.',
      difficulty: 'Easy',
      technology: 'React',
      category: 'User Experience',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'FetchData.jsx',
          content: `import React, { useState, useEffect } from 'react';\n\nexport default function FetchData() {\n  const [data, setData] = useState([]);\n  const [loading, setLoading] = useState(false);\n\n  useEffect(() => {\n    setLoading(true);\n    fetch('/api/challenges')\n      .then(res => res.json())\n      .then(data => setData(data));\n      // BUG: Missing catch and finally block to set loading state back to false!\n  }, []);\n\n  if (loading) return <div className="spinner">Loading...</div>;\n  return <div>Loaded {data.length} items.</div>;\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Turns off loading indicator', input: '', expected: 'setLoading(false)', passed: false }
      ],
      bugSignature: "fetch('/api/challenges')\n      .then(res => res.json())\n      .then(data => setData(data));",
      suspectedComponent: 'FetchData.jsx',
      aiSuggestions: [
        'Add `.finally(() => setLoading(false))` or set `setLoading(false)` inside the `.then` block.'
      ]
    },
    {
      id: '6',
      title: '6. Empty State',
      description: 'Improve the dashboard when there are no bugs. Show an illustration, "No Bugs Yet", and a button to create the first bug.',
      difficulty: 'Easy',
      technology: 'React',
      category: 'User Experience',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'EmptyState.jsx',
          content: `import React from 'react';\n\nexport default function EmptyState({ bugs, onCreateBug }) {\n  if (bugs && bugs.length > 0) return null;\n\n  // BUG: Empty return when there are no bugs, user sees a completely blank section!\n  return null;\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Renders empty state message', input: '', expected: 'No Bugs Yet', passed: false }
      ],
      bugSignature: '// BUG: Empty return when there are no bugs, user sees a completely blank section!\n  return null;',
      suspectedComponent: 'EmptyState.jsx',
      aiSuggestions: [
        'Return a JSX fragment containing the text "No Bugs Yet" and a button to trigger `onCreateBug`.'
      ]
    },
    {
      id: '7',
      title: '7. Better Form Validation',
      description: 'Improve bug creation validation.\n\nRequirements:\n- Required fields (title must be filled)\n- Description minimum length of 10 characters\n- Friendly error messages.',
      difficulty: 'Easy',
      technology: 'React',
      category: 'Data Validation',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'BugForm.jsx',
          content: `import React, { useState } from 'react';\n\nexport default function BugForm({ onSubmit }) {\n  const [title, setTitle] = useState('');\n  const [description, setDescription] = useState('');\n\n  const handleSubmit = (e) => {\n    e.preventDefault();\n    // BUG: Missing validation entirely - permits empty submit!\n    onSubmit({ title, description });\n  };\n\n  return (\n    <form onSubmit={handleSubmit} className="space-y-4">\n      <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Title" />\n      <textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Description" />\n      <button type="submit">Submit</button>\n    </form>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Restricts invalid submissions', input: '', expected: 'description.length < 10', passed: false }
      ],
      bugSignature: '// BUG: Missing validation entirely - permits empty submit!\n    onSubmit({ title, description });',
      suspectedComponent: 'BugForm.jsx',
      aiSuggestions: [
        'Check conditions like `if (!title.trim() || description.length < 10) { alert("Invalid input"); return; }` before calling `onSubmit`.'
      ]
    },
    {
      id: '8',
      title: '8. User Profile Page',
      description: 'Create a simple profile page. Show Name, Email, Joined Date, and Number of bugs created. Make sure it uses the dynamic user object.',
      difficulty: 'Easy',
      technology: 'React',
      category: 'Components',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'UserProfile.jsx',
          content: `import React from 'react';\n\nexport default function UserProfile({ user }) {\n  // BUG: Displaying hardcoded admin statistics instead of reading from the user prop!\n  return (\n    <div className="profile-card">\n      <h2>Developer Name: Administrator</h2>\n      <p>Email: admin@company.com</p>\n      <p>Member Since: 2020-01-01</p>\n      <p>Bugs Opened: 99</p>\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Reads dynamically from user prop', input: '', expected: 'user.name', passed: false }
      ],
      bugSignature: '<h2>Developer Name: Administrator</h2>\n      <p>Email: admin@company.com</p>\n      <p>Member Since: 2020-01-01</p>\n      <p>Bugs Opened: 99</p>',
      suspectedComponent: 'UserProfile.jsx',
      aiSuggestions: [
        'Replace the hardcoded strings with dynamic props: `{user.name}`, `{user.email}`, `{user.joinedDate}`, `{user.bugsCount}`.'
      ]
    },
    {
      id: '9',
      title: '9. Copy Bug ID',
      description: 'Add a copy button beside the Bug ID. Clicking it should copy the ID to clipboard and show a toast saying "Copied!"',
      difficulty: 'Easy',
      technology: 'React',
      category: 'User Experience',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'CopyButton.jsx',
          content: `import React from 'react';\n\nexport default function CopyButton({ bugId, onToast }) {\n  const handleCopy = () => {\n    // BUG: Using deprecated document.execCommand instead of modern navigator.clipboard API\n    document.execCommand('copy');\n    onToast('Copied!');\n  };\n\n  return (\n    <button onClick={handleCopy} className="p-1 text-slate-400 hover:text-white">\n      Copy ID\n    </button>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Writes to Clipboard API', input: '', expected: 'navigator.clipboard.writeText', passed: false }
      ],
      bugSignature: "// BUG: Using deprecated document.execCommand instead of modern navigator.clipboard API\n    document.execCommand('copy');",
      suspectedComponent: 'CopyButton.jsx',
      aiSuggestions: [
        'Use the modern clipboard API: `navigator.clipboard.writeText(bugId).then(() => onToast("Copied!"));`.'
      ]
    },
    {
      id: '10',
      title: '10. Pagination',
      description: 'Add pagination to the bugs list. Show 10 bugs per page. Add working Previous and Next buttons.',
      difficulty: 'Easy',
      technology: 'React',
      category: 'Optimization',
      timeEstimate: '10 mins',
      points: 100,
      files: [
        {
          name: 'Pagination.jsx',
          content: `import React, { useState } from 'react';\n\nexport default function PaginatedBugs({ bugs }) {\n  const [currentPage, setCurrentPage] = useState(1);\n  const itemsPerPage = 10;\n\n  // BUG: Slice indices are hardcoded or incorrectly computed, ignoring currentPage!\n  const displayedBugs = bugs.slice(0, bugs.length);\n\n  return (\n    <div>\n      <ul>\n        {displayedBugs.map(bug => <li key={bug.id}>{bug.title}</li>)}\n      </ul>\n      <div className="flex gap-2 mt-4\">\n        <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))}>Previous</button>\n        <button onClick={() => setCurrentPage(p => p + 1)}>Next</button>\n      </div>\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Slices data based on currentPage', input: '', expected: '(currentPage - 1) * itemsPerPage', passed: false }
      ],
      bugSignature: '// BUG: Slice indices are hardcoded or incorrectly computed, ignoring currentPage!\n  const displayedBugs = bugs.slice(0, bugs.length);',
      suspectedComponent: 'Pagination.jsx',
      aiSuggestions: [
        'Compute correct page indexes: `const start = (currentPage - 1) * itemsPerPage; const displayedBugs = bugs.slice(start, start + itemsPerPage);`.'
      ]
    },
    {
      id: '11',
      title: '11. Bug Status Timeline',
      description: 'Create a timeline for each bug (Created -> Assigned -> In Progress -> Testing -> Completed). Highlight the current stage.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'Components',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'Timeline.jsx',
          content: `import React from 'react';\n\nexport default function Timeline({ currentStatus }) {\n  const stages = ['Created', 'Assigned', 'In Progress', 'Testing', 'Completed'];\n\n  return (\n    <div className="flex justify-between items-center w-full">\n      {stages.map((stage, index) => {\n        // BUG: Always checking if index === 0 instead of comparing with currentStatus index\n        const isActive = index === 0;\n        return (\n          <div key={stage} className={\`p-2 rounded-lg \${isActive ? 'bg-indigo-600 text-white font-bold' : 'bg-slate-800 text-slate-400'}\`}>\n            {stage}\n          </div>\n        );\n      })}\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Evaluates active status index dynamically', input: '', expected: 'stages.indexOf(currentStatus)', passed: false }
      ],
      bugSignature: '// BUG: Always checking if index === 0 instead of comparing with currentStatus index\n        const isActive = index === 0;',
      suspectedComponent: 'Timeline.jsx',
      aiSuggestions: [
        'Compare the current loop index with the index of `currentStatus` in the stages array: `const isActive = index <= stages.indexOf(currentStatus);`.'
      ]
    },
    {
      id: '12',
      title: '12. Dashboard Statistics',
      description: 'Create a dashboard with analytics displaying: Total, Open, Closed, High Priority, and Critical Bugs. Fix the statistics aggregation logic.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'Analytics',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'statsReducer.js',
          content: `// BUG: Incorrect statistics aggregation logic\nexport function calculateStats(bugs) {\n  return bugs.reduce((acc, bug) => {\n    acc.total += 1;\n    // BUG: Adding all bugs to open instead of checking status!\n    acc.open += 1;\n    if (bug.priority === 'High') {\n      acc.high += 1;\n    }\n    // BUG: Missing critical priority aggregation!\n    return acc;\n  }, { total: 0, open: 0, closed: 0, high: 0, critical: 0 });\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Separates stats by status and priority', input: '', expected: "bug.status === 'Open'", passed: false }
      ],
      bugSignature: '// BUG: Adding all bugs to open instead of checking status!\n    acc.open += 1;\n    if (bug.priority === \'High\') {\n      acc.high += 1;\n    }\n    // BUG: Missing critical priority aggregation!',
      suspectedComponent: 'statsReducer.js',
      aiSuggestions: [
        'Perform proper conditional checks on `bug.status` and check for both "High" and "Critical" priorities: `if (bug.status === "Open") acc.open += 1; else if (bug.status === "Closed") acc.closed += 1;`'
      ]
    },
    {
      id: '13',
      title: '13. Advanced Filters',
      description: 'Add advanced filtering. Allow filtering by Priority and Status. Ensure multiple filters can work together.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'Filtering',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'FilterPanel.jsx',
          content: `import React, { useState } from 'react';\n\nexport default function FilterPanel({ bugs }) {\n  const [priority, setPriority] = useState('All');\n  const [status, setStatus] = useState('All');\n\n  // BUG: Applying filters independently and replacing rather than combining criteria\n  const filtered = bugs.filter(bug => {\n    if (priority !== 'All') return bug.priority === priority;\n    if (status !== 'All') return bug.status === status;\n    return true;\n  });\n\n  return (\n    <div>\n      <select value={priority} onChange={e => setPriority(e.target.value)}>\n        <option value=\"All\">All Priorities</option>\n        <option value=\"High\">High</option>\n      </select>\n      <select value={status} onChange={e => setStatus(e.target.value)}>\n        <option value=\"All\">All Statuses</option>\n        <option value=\"Open\">Open</option>\n      </select>\n      <p>Filtered Count: {filtered.length}</p>\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Combined filters evaluation', input: '', expected: 'matchesPriority && matchesStatus', passed: false }
      ],
      bugSignature: '  // BUG: Applying filters independently and replacing rather than combining criteria\n  const filtered = bugs.filter(bug => {\n    if (priority !== \'All\') return bug.priority === priority;\n    if (status !== \'All\') return bug.status === status;\n    return true;\n  });',
      suspectedComponent: 'FilterPanel.jsx',
      aiSuggestions: [
        'Combine filters logically using `&&`: `const matchesPriority = priority === "All" || bug.priority === priority; const matchesStatus = status === "All" || bug.status === status; return matchesPriority && matchesStatus;`.'
      ]
    },
    {
      id: '14',
      title: '14. Sort Bugs',
      description: 'Allow sorting bugs by Latest, Oldest, or Highest Priority. Fix the sorting function so it doesn\'t mutate props directly.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'Sorting',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'SortBugs.jsx',
          content: `import React from 'react';\n\nexport default function SortBugs({ bugs, onSorted }) {\n  const handleSort = (criteria) => {\n    // BUG: Mutating original prop array directly instead of creating a copy!\n    const sorted = bugs.sort((a, b) => {\n      if (criteria === 'Latest') return b.id - a.id;\n      return a.id - b.id;\n    });\n    onSorted(sorted);\n  };\n\n  return (\n    <div className="flex gap-2">\n      <button onClick={() => handleSort('Latest')}>Sort Latest</button>\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Avoids array mutation', input: '', expected: '[...bugs]', passed: false }
      ],
      bugSignature: '    // BUG: Mutating original prop array directly instead of creating a copy!\n    const sorted = bugs.sort((a, b) => {',
      suspectedComponent: 'SortBugs.jsx',
      aiSuggestions: [
        'Clone the bugs array before sorting it to prevent direct mutation of props: `const sorted = [...bugs].sort(...)`.'
      ]
    },
    {
      id: '15',
      title: '15. Comments System',
      description: 'Implement comments list. The deletion logic deletes comments by index which shifts indices. Fix it to delete comments by unique ID.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'Comments',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'CommentsSection.jsx',
          content: `import React, { useState } from 'react';\n\nexport default function CommentsSection() {\n  const [comments, setComments] = useState([\n    { id: 1, text: 'First comment' },\n    { id: 2, text: 'Second comment' }\n  ]);\n\n  const handleDelete = (index) => {\n    // BUG: Deleting by index instead of unique comment ID!\n    const newComments = comments.filter((_, idx) => idx !== index);\n    setComments(newComments);\n  };\n\n  return (\n    <div>\n      {comments.map((comment, index) => (\n        <div key={comment.id}>\n          <span>{comment.text}</span>\n          <button onClick={() => handleDelete(index)}>Delete</button>\n        </div>\n      ))}\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Deletes comment by ID', input: '', expected: 'comment.id !== id', passed: false }
      ],
      bugSignature: '  const handleDelete = (index) => {\n    // BUG: Deleting by index instead of unique comment ID!\n    const newComments = comments.filter((_, idx) => idx !== index);\n    setComments(newComments);\n  };',
      suspectedComponent: 'CommentsSection.jsx',
      aiSuggestions: [
        'Change `handleDelete` signature to accept `id` and filter based on comment ID: `comments.filter(comment => comment.id !== id)`.'
      ]
    },
    {
      id: '16',
      title: '16. File Attachments',
      description: 'Allow users to upload screenshots. Add validation check for file size (maximum 5MB). The current limit validation is in bits/incorrect unit.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'Forms',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'Upload.jsx',
          content: `import React, { useState } from 'react';\n\nexport default function Upload({ onUpload }) {\n  const [error, setError] = useState('');\n\n  const handleFileChange = (e) => {\n    const file = e.target.files[0];\n    if (!file) return;\n\n    // BUG: Incorrect size checking: 5MB is 5 * 1024 * 1024 bytes, but current code checks against bits or too small value!\n    if (file.size > 5000) {\n      setError('File too large. Max 5MB.');\n      return;\n    }\n\n    onUpload(file);\n  };\n\n  return (\n    <div>\n      <input type="file" onChange={handleFileChange} />\n      {error && <span className="text-red-500">{error}</span>}\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Validates 5MB limit in bytes', input: '', expected: '5 * 1024 * 1024', passed: false }
      ],
      bugSignature: '    // BUG: Incorrect size checking: 5MB is 5 * 1024 * 1024 bytes, but current code checks against bits or too small value!\n    if (file.size > 5000) {',
      suspectedComponent: 'Upload.jsx',
      aiSuggestions: [
        'Specify 5MB in bytes: `5 * 1024 * 1024` which is `5242880` bytes.'
      ]
    },
    {
      id: '17',
      title: '17. Activity Log',
      description: 'Track bug edits using Django signals. The signal callback contains a reference error causing it to fail.',
      difficulty: 'Medium',
      technology: 'Django',
      category: 'Logging',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'signals.py',
          content: `from django.db.models.signals import post_save\nfrom django.dispatch import receiver\nfrom .models import Bug, ActivityLog\n\n@receiver(post_save, sender=Bug)\ndef log_bug_activity(sender, instance, created, **kwargs):\n    # BUG: Standing receiver function incorrectly references 'self'!\n    action = "Created" if created else "Updated"\n    self.stdout.write(f"Logging activity: {action}")\n    ActivityLog.objects.create(bug=instance, action=action)`
        }
      ],
      testCases: [
        { id: 1, name: 'Eliminates invalid self reference', input: '', expected: 'action =', passed: false }
      ],
      bugSignature: '    # BUG: Standing receiver function incorrectly references \'self\'!\n    action = "Created" if created else "Updated"\n    self.stdout.write(f"Logging activity: {action}")',
      suspectedComponent: 'signals.py',
      aiSuggestions: [
        'Delete the `self.stdout.write(...)` line as receiver functions are module-level and do not have access to a `self` object.'
      ]
    },
    {
      id: '18',
      title: '18. Email Notifications',
      description: 'Send email when a bug is completed. The function uses standard Django send_mail but specifies incorrect parameters.',
      difficulty: 'Medium',
      technology: 'Django',
      category: 'Email',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'notifier.py',
          content: `from django.core.mail import send_mail\n\ndef send_bug_completed_email(bug):\n    # BUG: send_mail called with positional list instead of keyword arguments or correct order\n    send_mail(\n        "Bug Completed: " + bug.title,\n        "The bug has been fixed.",\n        ["dev@company.com"],\n        "noreply@company.com",\n    )`
        }
      ],
      testCases: [
        { id: 1, name: 'Correct parameters for send_mail', input: '', expected: '"noreply@company.com", ["dev@company.com"]', passed: false }
      ],
      bugSignature: '    # BUG: send_mail called with positional list instead of keyword arguments or correct order\n    send_mail(\n        "Bug Completed: " + bug.title,\n        "The bug has been fixed.",\n        ["dev@company.com"],\n        "noreply@company.com",\n    )',
      suspectedComponent: 'notifier.py',
      aiSuggestions: [
        'The fourth parameter of send_mail should be the recipient list, and the third should be the sender: `send_mail(subject, message, sender, recipient_list)`.'
      ]
    },
    {
      id: '19',
      title: '19. Role Based Access',
      description: 'Implement role-based permissions decorator. The role check crashes if request.user is not fully initialized.',
      difficulty: 'Medium',
      technology: 'Django',
      category: 'Permissions',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'permissions.py',
          content: `from django.core.exceptions import PermissionDenied\n\ndef require_role(allowed_roles):\n    def decorator(view_func):\n        def _wrapped_view(request, *args, **kwargs):\n            # BUG: Accessing non-existent 'request.user.role' before checking if user is authenticated\n            if request.user.role not in allowed_roles:\n                raise PermissionDenied\n            return view_func(request, *args, **kwargs)\n        return _wrapped_view\n    return decorator`
        }
      ],
      testCases: [
        { id: 1, name: 'Safe attribute validation', input: '', expected: 'getattr', passed: false }
      ],
      bugSignature: '            # BUG: Accessing non-existent \'request.user.role\' before checking if user is authenticated\n            if request.user.role not in allowed_roles:\n                raise PermissionDenied',
      suspectedComponent: 'permissions.py',
      aiSuggestions: [
        'Safely access user roles: `if not request.user.is_authenticated or getattr(request.user, "role", None) not in allowed_roles:`'
      ]
    },
    {
      id: '20',
      title: '20. Kanban Board',
      description: 'A Kanban board with draggable cards. The drag-over handler doesn\'t call preventDefault(), which blocks dropping.',
      difficulty: 'Medium',
      technology: 'React',
      category: 'User Experience',
      timeEstimate: '15 mins',
      points: 150,
      files: [
        {
          name: 'Kanban.jsx',
          content: `import React from 'react';\n\nexport default function KanbanBoard({ onDropBug }) {\n  const handleDragOver = (e) => {\n    // BUG: Missing e.preventDefault() which blocks drop events in HTML5 drag and drop API\n    console.log("Dragging over column...");\n  };\n\n  const handleDrop = (e, status) => {\n    const bugId = e.dataTransfer.getData("bugId");\n    onDropBug(bugId, status);\n  };\n\n  return (\n    <div \n      onDragOver={handleDragOver} \n      onDrop={(e) => handleDrop(e, 'In Progress')}\n      className="p-4 bg-slate-900 min-h-[300px]"\n    >\n      In Progress Column (Drop here)\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Prevents default dragover event', input: '', expected: 'e.preventDefault()', passed: false }
      ],
      bugSignature: '  const handleDragOver = (e) => {\n    // BUG: Missing e.preventDefault() which blocks drop events in HTML5 drag and drop API\n    console.log("Dragging over column...");\n  };',
      suspectedComponent: 'Kanban.jsx',
      aiSuggestions: [
        'Add `e.preventDefault();` in the `handleDragOver` handler to allow elements to be dropped.'
      ]
    },
    {
      id: '21',
      title: '21. AI Bug Severity Prediction',
      description: 'Integrate an AI model to predict severity from a description. Prompt construction has injection vulnerabilities.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'AI Integration',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'ai_predictor.py',
          content: `import json\n\ndef construct_ai_payload(description):\n    # BUG: Concatenating description directly into JSON string template which breaks if user inputs quotes!\n    payload_str = f'{{"description": "{description}", "model": "severity-v1"}}'\n    return json.loads(payload_str)`
        }
      ],
      testCases: [
        { id: 1, name: 'Safe JSON serialization', input: '', expected: 'json.dumps', passed: false }
      ],
      bugSignature: '    # BUG: Concatenating description directly into JSON string template which breaks if user inputs quotes!\n    payload_str = f\'{{"description": "{description}", "model": "severity-v1"}}\'',
      suspectedComponent: 'ai_predictor.py',
      aiSuggestions: [
        'Construct the dictionary directly and use `json.dumps()` or return the dict: `payload = {"description": description, "model": "severity-v1"}`.'
      ]
    },
    {
      id: '22',
      title: '22. Duplicate Bug Detection',
      description: 'Check for duplicate bugs based on title similarity. The loop returns immediately on the first comparison.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'Algorithms',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'detector.py',
          content: `def find_duplicate_bug(new_title, existing_bugs):\n    for bug in existing_bugs:\n        // BUG: Returns immediately in the first iteration instead of looking through all bugs!\n        if bug.title.lower() == new_title.lower():\n            return bug\n        else:\n            return None`
        }
      ],
      testCases: [
        { id: 1, name: 'Inspects all items before returning', input: '', expected: 'return None', passed: false }
      ],
      bugSignature: '        # BUG: Returns immediately in the first iteration instead of looking through all bugs!\n        if bug.title.lower() == new_title.lower():\n            return bug\n        else:\n            return None',
      suspectedComponent: 'detector.py',
      aiSuggestions: [
        'Remove the `else` clause inside the loop so that the function only returns `None` after examining all existing bugs.'
      ]
    },
    {
      id: '23',
      title: '23. AI Bug Summary',
      description: 'Generate an AI summary of a bug. The HTTP request is missing a timeout parameter, risking thread locks.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'AI Integration',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'ai_summary.py',
          content: `import urllib.request\nimport urllib.parse\n\ndef fetch_ai_summary(bug_details):\n    data = urllib.parse.urlencode({'text': bug_details}).encode('utf-8')\n    # BUG: Missing timeout parameter in urllib urlopen call, which can hang the server\n    req = urllib.request.Request("http://ai-service/summarize", data=data)\n    response = urllib.request.urlopen(req)\n    return response.read().decode('utf-8')`
        }
      ],
      testCases: [
        { id: 1, name: 'Protects requests with timeouts', input: '', expected: 'timeout=', passed: false }
      ],
      bugSignature: '    # BUG: Missing timeout parameter in urllib urlopen call, which can hang the server\n    req = urllib.request.Request("http://ai-service/summarize", data=data)\n    response = urllib.request.urlopen(req)',
      suspectedComponent: 'ai_summary.py',
      aiSuggestions: [
        'Specify a timeout (e.g. `timeout=5`) when calling `urllib.request.urlopen(req, timeout=5)`.'
      ]
    },
    {
      id: '24',
      title: '24. Smart Assignment',
      description: 'Automatically assign bugs to the developer with the fewest open bugs. The sorting comparator returns wrong sorting order.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'Algorithms',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'assigner.py',
          content: `def find_best_developer(developers):\n    # Developers is a list of dicts: [{'name': 'DevA', 'open_bugs': 5}, ...]\n    # BUG: Sorting in reverse order (descending by open_bugs) assigns to the developer with the most bugs!\n    sorted_devs = sorted(developers, key=lambda d: d['open_bugs'], reverse=True)\n    return sorted_devs[0]`
        }
      ],
      testCases: [
        { id: 1, name: 'Finds developer with minimum workload', input: '', expected: 'reverse=False', passed: false }
      ],
      bugSignature: "    # BUG: Sorting in reverse order (descending by open_bugs) assigns to the developer with the most bugs!\n    sorted_devs = sorted(developers, key=lambda d: d['open_bugs'], reverse=True)",
      suspectedComponent: 'assigner.py',
      aiSuggestions: [
        'Change `reverse=True` to `reverse=False` (or remove it) to sort developers ascending by workload.'
      ]
    },
    {
      id: '25',
      title: '25. Real-Time Collaboration',
      description: 'WebSocket consumer to broadcast status updates. The handler calls sync database queries inside an async context.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'WebSockets',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'consumers.py',
          content: `from channels.generic.websocket import AsyncWebsocketConsumer\nfrom .models import Bug\n\nclass BugConsumer(AsyncWebsocketConsumer):\n    async def receive(self, text_data):\n        # BUG: Accessing Django ORM synchronously inside an async method without database_sync_to_async!\n        bug = Bug.objects.get(id=1)\n        await self.send(text_data=bug.title)`
        }
      ],
      testCases: [
        { id: 1, name: 'Wrap sync DB operations safely', input: '', expected: 'database_sync_to_async', passed: false }
      ],
      bugSignature: '        # BUG: Accessing Django ORM synchronously inside an async method without database_sync_to_async!\n        bug = Bug.objects.get(id=1)',
      suspectedComponent: 'consumers.py',
      aiSuggestions: [
        'Use `database_sync_to_async` decorator or wrapper to safely fetch database records in async views.'
      ]
    },
    {
      id: '26',
      title: '26. Version History',
      description: 'Track version history. The history saver saves updates but contains a race condition.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'Database',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'history.py',
          content: `from django.db import transaction\nfrom .models import Bug, BugHistory\n\ndef create_bug_version(bug_id, change_notes):\n    with transaction.atomic():\n        # BUG: Fetching row without select_for_update() allows race condition in concurrent updates!\n        bug = Bug.objects.get(id=bug_id)\n        latest_version = bug.version\n        bug.version = latest_version + 1\n        bug.save()\n        BugHistory.objects.create(bug=bug, version=bug.version, notes=change_notes)`
        }
      ],
      testCases: [
        { id: 1, name: 'Locks records for update', input: '', expected: 'select_for_update()', passed: false }
      ],
      bugSignature: '        # BUG: Fetching row without select_for_update() allows race condition in concurrent updates!\n        bug = Bug.objects.get(id=bug_id)',
      suspectedComponent: 'history.py',
      aiSuggestions: [
        'Use `select_for_update()` to lock the row during version update: `Bug.objects.select_for_update().get(id=bug_id)`.'
      ]
    },
    {
      id: '27',
      title: '27. Project Analytics',
      description: 'Render analytical charts. If the list of data points is empty, the chart component crashes with a Division by Zero.',
      difficulty: 'Hard',
      technology: 'React',
      category: 'Analytics',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'AnalyticsChart.jsx',
          content: `import React from 'react';\n\nexport default function AnalyticsChart({ dataPoints }) {\n  // BUG: Division by zero when calculating average if dataPoints is empty!\n  const sum = dataPoints.reduce((acc, p) => acc + p.value, 0);\n  const average = sum / dataPoints.length;\n\n  return (\n    <div className="analytics-card">\n      <h3>Average Resolution: {average} mins</h3>\n    </div>\n  );\n}`
        }
      ],
      testCases: [
        { id: 1, name: 'Handles empty data lists safely', input: '', expected: 'dataPoints.length === 0', passed: false }
      ],
      bugSignature: '  // BUG: Division by zero when calculating average if dataPoints is empty!\n  const sum = dataPoints.reduce((acc, p) => acc + p.value, 0);\n  const average = sum / dataPoints.length;',
      suspectedComponent: 'AnalyticsChart.jsx',
      aiSuggestions: [
        'Add a length check before dividing: `const average = dataPoints.length === 0 ? 0 : sum / dataPoints.length;`.'
      ]
    },
    {
      id: '28',
      title: '28. AI Bug Fix Suggestions',
      description: 'Send context to AI to suggest a fix. The OpenAI API call uses a deprecated model name which is no longer supported.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'AI Integration',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'ai_fixer.py',
          content: `def get_ai_suggestions(bug_code):\n    # BUG: Using deprecated model 'text-davinci-003' which is shut down\n    payload = {\n        "model": "text-davinci-003",\n        "prompt": f"Fix this code:\\n{bug_code}",\n        "max_tokens": 150\n    }\n    return payload`
        }
      ],
      testCases: [
        { id: 1, name: 'Uses supported OpenAI model', input: '', expected: 'gpt-4', passed: false }
      ],
      bugSignature: '    # BUG: Using deprecated model \'text-davinci-003\' which is shut down\n    payload = {\n        "model": "text-davinci-003",',
      suspectedComponent: 'ai_fixer.py',
      aiSuggestions: [
        'Change the model name to a modern model such as `"gpt-4"`, `"gpt-3.5-turbo"` or `"gpt-4o"`.'
      ]
    },
    {
      id: '29',
      title: '29. Full Audit System',
      description: 'Retrieve client IP address for the audit log. The code reads the wrong HTTP header or doesn\'t split proxies correctly.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'Security',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'audit.py',
          content: `def get_client_ip(request):\n    # BUG: Reading HTTP_X_FORWARDED_FOR directly without fallback or splitting multiple proxies\n    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')\n    ip = x_forwarded_for\n    return ip`
        }
      ],
      testCases: [
        { id: 1, name: 'Reads client IP addresses correctly', input: '', expected: 'REMOTE_ADDR', passed: false }
      ],
      bugSignature: '    # BUG: Reading HTTP_X_FORWARDED_FOR directly without fallback or splitting multiple proxies\n    x_forwarded_for = request.META.get(\'HTTP_X_FORWARDED_FOR\')\n    ip = x_forwarded_for\n    return ip',
      suspectedComponent: 'audit.py',
      aiSuggestions: [
        'Extract the first IP in the list from X-Forwarded-For if available, or fall back to REMOTE_ADDR: `ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.META.get("REMOTE_ADDR")`.'
      ]
    },
    {
      id: '30',
      title: '30. Production-Ready Improvements',
      description: 'Prevent SQL injection in search parameters. The code uses raw raw SQL formatting instead of parameters.',
      difficulty: 'Hard',
      technology: 'Django',
      category: 'Security',
      timeEstimate: '25 mins',
      points: 300,
      files: [
        {
          name: 'search.py',
          content: `from django.db import connection\n\ndef search_bug_reports(query):\n    # BUG: Raw string formatting in query opens SQL injection vulnerability!\n    raw_query = f"SELECT * FROM buggyman_challenge WHERE title LIKE '%{query}%'"\n    with connection.cursor() as cursor:\n        cursor.execute(raw_query)\n        return cursor.fetchall()`
        }
      ],
      testCases: [
        { id: 1, name: 'Prevents raw SQL formatting vulnerabilities', input: '', expected: '%s', passed: false }
      ],
      bugSignature: '    # BUG: Raw string formatting in query opens SQL injection vulnerability!\n    raw_query = f"SELECT * FROM buggyman_challenge WHERE title LIKE \'%{query}%\'"',
      suspectedComponent: 'search.py',
      aiSuggestions: [
        'Pass values as parameters in the execute call to automatically escape inputs: `cursor.execute("SELECT * FROM buggyman_challenge WHERE title LIKE %s", [f"%{query}%"])`.'
      ]
    }
  ],

  user: {
    name: 'New Developer',
    username: 'developer',
    email: 'developer@gmail.com',
    college: '',
    bio: '',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
    totalScore: 0,
    total_score: 0,
    challengesSolved: 0,
    challenges_solved: 0,
    streak: 0,
    streakDays: 0,
    streak_days: 0,
    bestStreak: 0,
    skills: {},
    activities: [
      { id: 1, text: 'Joined BuggyMan community', time: 'Just now', xp: 0 }
    ],
    badges: [],
    bugbytes_balance: 50,
    bugbytesBalance: 50,
    onboardingCompleted: false,
    onboarding_completed: false,
    isNewUser: true
  },
  users: [],
  leaderboard: [
    { rank: 1, name: 'Alex Rivera', score: 1450, streak: 12, solved: 22, college: 'MIT' },
    { rank: 2, name: 'Sam Chen', score: 1220, streak: 8, solved: 18, college: 'Stanford' },
    { rank: 3, name: 'Devon Smith', score: 650, streak: 3, solved: 9, college: 'Georgia Tech' },
    { rank: 4, name: 'Li Wei', score: 580, streak: 2, solved: 7, college: 'Caltech' }
  ],
  notifications: [
    { id: 1, title: 'Welcome to BuggyMan!', message: 'Welcome aboard! Solve your first debugging challenge to earn badges and XP.', type: 'system', read: false, time: 'Just now' }
  ],
  analytics: {
    totalSolved: 0,
    accuracy: 0,
    timeTrend: [
      { name: 'Mon', mins: 0, solved: 0 },
      { name: 'Tue', mins: 0, solved: 0 },
      { name: 'Wed', mins: 0, solved: 0 },
      { name: 'Thu', mins: 0, solved: 0 },
      { name: 'Fri', mins: 0, solved: 0 },
      { name: 'Sat', mins: 0, solved: 0 },
      { name: 'Sun', mins: 0, solved: 0 }
    ],
    bugStats: [],
    difficultyProgression: [
      { name: 'Easy', completed: 0 },
      { name: 'Medium', completed: 0 },
      { name: 'Hard', completed: 0 }
    ]
  },
  adminStats: {
    totalUsers: 154,
    totalChallenges: 18,
    activeUsers: 42,
    aiUsageCount: 289
  }
};

const MOCK_DEMO_USER = {
  id: 101,
  name: 'Jane Doe',
  username: 'janedoe',
  email: 'jane.doe@college.edu',
  college: 'State Technical University',
  bio: 'Aspiring Full Stack Engineer. Lover of logic puzzles and debugging challenge marathons.',
  avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
  totalScore: 780,
  total_score: 780,
  challengesSolved: 12,
  challenges_solved: 12,
  streak: 5,
  streakDays: 5,
  streak_days: 5,
  bestStreak: 5,
  skills: {
    React: 80,
    Django: 60,
    NodeJS: 45,
    CSS: 70
  },
  activities: [
    { id: 1, text: 'Completed "Fix React State Updates"', time: '2 hours ago', xp: 100 },
    { id: 2, text: 'Unlocked "Bug Squasher" Badge', time: '1 day ago', xp: 50 },
    { id: 3, text: 'Solved "Express Middlewares" challenge', time: '3 days ago', xp: 200 }
  ],
  badges: [
    { name: 'First Bug Defeated', desc: 'Resolved your first bug', icon: '🐞', date: 'Jul 01, 2026' },
    { name: 'Five Day Streak', desc: 'Debugged 5 days in a row', icon: '🔥', date: 'Jul 05, 2026' },
    { name: 'AI Explorer', desc: 'Used AI hints 10 times', icon: '🤖', date: 'Jul 08, 2026' }
  ],
  bugbytes_balance: 50,
  bugbytesBalance: 50,
  onboardingCompleted: true,
  onboarding_completed: true,
  isNewUser: false
};

// Initialize localStorage with clean databases, clearing legacy polluted mock data
const getMockDb = () => {
  const legacyDb = localStorage.getItem('buggyman_mock_db');
  if (legacyDb) {
    try {
      const parsed = JSON.parse(legacyDb);
      // Auto-purge stale legacy database that gave new users 5-day streak and Jane Doe's stats
      if ((parsed?.user?.streak === 5 && parsed?.user?.challengesSolved === 12) || !parsed?.schemaVersion || parsed.schemaVersion < 3) {
        localStorage.removeItem('buggyman_mock_db');
      }
    } catch (e) {
      localStorage.removeItem('buggyman_mock_db');
    }
  }

  const db = localStorage.getItem('buggyman_mock_db');
  if (!db) {
    const fresh = JSON.parse(JSON.stringify(INITIAL_MOCK_DATA));
    fresh.schemaVersion = 3;
    localStorage.setItem('buggyman_mock_db', JSON.stringify(fresh));
    return fresh;
  }
  return JSON.parse(db);
};

const updateMockDb = (data) => {
  localStorage.setItem('buggyman_mock_db', JSON.stringify(data));
};

export async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const fetchOptions = {
    ...options,
    headers
  };

  let res;
  try {
    res = await fetch(`${BASE_URL}${endpoint}`, fetchOptions);
  } catch (error) {
    if (ENABLE_MOCK_FALLBACK) {
      console.warn(`Real API connection failed for ${endpoint}. Falling back to simulated mock DB.`, error);
      return simulateMockApi(endpoint, options);
    }
    console.error(`Network error connecting to ${BASE_URL}${endpoint}:`, error);
    throw new Error(`Unable to connect to server. Please check your network connection or verify the backend service is running.`);
  }

  const contentType = res.headers.get('Content-Type') || '';
  let data = {};
  try {
    data = contentType.includes('application/json') ? await res.json() : await res.text();
  } catch (parseError) {
    data = {};
  }

  if (!res.ok) {
    if (res.status === 404 && endpoint.startsWith('/pvp') && ENABLE_MOCK_FALLBACK) {
      console.warn(`Backend 404 for ${endpoint}. Falling back to simulated mock DB.`);
      return simulateMockApi(endpoint, options);
    }
    const isHtml = typeof data === 'string' && data.trim().startsWith('<');
    const message = data?.error || data?.message || (!isHtml && typeof data === 'string' ? data : `Server error (${res.status}: ${res.statusText || 'Request failed'})`);
    throw new Error(message);
  }

  return data;
}

// Fallback logic simulating the backend endpoints
function simulateMockApi(endpoint, options) {
  const db = getMockDb();
  const method = options.method || 'GET';
  const body = options.body ? JSON.parse(options.body) : null;

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 1. Auth Mock APIs
      if (endpoint === '/login' && method === 'POST') {
        const { email, password } = body || {};
        if (!email || !password) {
          reject(new Error('Email and password required'));
          return;
        }

        const trimmed = email.trim();
        if (trimmed.includes('@')) {
          const emailErr = getEmailValidationError(trimmed);
          if (emailErr) {
            reject(new Error(emailErr));
            return;
          }
        }

        localStorage.setItem('token', 'mock_jwt_token_key');

        // Check registered mock users
        const existing = (db.users || []).find(u => u.email.toLowerCase() === trimmed.toLowerCase() || u.username.toLowerCase() === trimmed.toLowerCase());
        if (existing) {
          db.user = existing;
          updateMockDb(db);
          resolve({ token: 'mock_jwt_token_key', user: existing, isNewUser: Boolean(!existing.onboardingCompleted) });
          return;
        }

        // If active mock user matches
        if (db.user && (db.user.email.toLowerCase() === trimmed.toLowerCase() || db.user.username.toLowerCase() === trimmed.toLowerCase())) {
          resolve({ token: 'mock_jwt_token_key', user: db.user, isNewUser: Boolean(!db.user.onboardingCompleted) });
          return;
        }

        resolve({ token: 'mock_jwt_token_key', user: db.user, isNewUser: Boolean(!db.user.onboardingCompleted) });
        return;
      }

      if (endpoint === '/register' && method === 'POST') {
        const { displayName, fullName, email, password } = body || {};
        const name = displayName || fullName || '';
        if (!email || !password) {
          reject(new Error('Email and password are required'));
          return;
        }

        const emailErr = getEmailValidationError(email);
        if (emailErr) {
          reject(new Error(emailErr));
          return;
        }

        const trimmedEmail = email.trim().toLowerCase();
        const username = (body.username || trimmedEmail.split('@')[0]).toLowerCase();

        if ((db.users || []).some(u => u.email.toLowerCase() === trimmedEmail || u.username.toLowerCase() === username)) {
          reject(new Error('Email or username is already registered'));
          return;
        }

        if (body.otp) {
          const storedOtp = sessionStorage.getItem(`mock_reg_otp_${trimmedEmail}`);
          if (storedOtp && String(body.otp).trim() !== storedOtp) {
            reject(new Error('Invalid or expired 6-digit verification code.'));
            return;
          }
          sessionStorage.removeItem(`mock_reg_otp_${trimmedEmail}`);
        }

        const newUser = {
          id: Date.now(),
          name: name || username,
          display_name: name || username,
          username: username,
          email: trimmedEmail,
          college: body.college || '',
          bio: body.bio || '',
          avatar: body.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
          totalScore: 0,
          total_score: 0,
          challengesSolved: 0,
          challenges_solved: 0,
          streak: 0,
          streakDays: 0,
          streak_days: 0,
          bestStreak: 0,
          skills: {},
          activities: [
            { id: Date.now(), text: 'Joined BuggyMan community', time: 'Just now', xp: 0 }
          ],
          badges: [],
          strengths: body.strengths || [],
          weaknesses: body.weaknesses || [],
          interests: body.interests || [],
          theme: body.theme || 'dark',
          accent_color: body.accentColor || 'blue',
          bugbytes_balance: 50,
          bugbytesBalance: 50,
          onboardingCompleted: false,
          onboarding_completed: false,
          isNewUser: true,
          role: 'user',
          isAdmin: false
        };

        db.user = newUser;
        if (!db.users) db.users = [];
        db.users.push(newUser);
        db.notifications = [
          { id: Date.now(), title: 'Welcome to BuggyMan!', message: 'Welcome aboard! Solve your first debugging challenge to earn badges and XP.', type: 'system', read: false, time: 'Just now' }
        ];
        db.analytics = {
          totalSolved: 0,
          accuracy: 0,
          timeTrend: [
            { name: 'Mon', mins: 0, solved: 0 },
            { name: 'Tue', mins: 0, solved: 0 },
            { name: 'Wed', mins: 0, solved: 0 },
            { name: 'Thu', mins: 0, solved: 0 },
            { name: 'Fri', mins: 0, solved: 0 },
            { name: 'Sat', mins: 0, solved: 0 },
            { name: 'Sun', mins: 0, solved: 0 }
          ],
          bugStats: [],
          difficultyProgression: [
            { name: 'Easy', completed: 0 },
            { name: 'Medium', completed: 0 },
            { name: 'Hard', completed: 0 }
          ]
        };

        localStorage.setItem('token', 'mock_jwt_token_key');
        updateMockDb(db);
        resolve({ token: 'mock_jwt_token_key', user: newUser, isNewUser: true });
        return;
      }

      if (endpoint === '/check-availability' && method === 'POST') {
        const { username, email } = body || {};
        if (email) {
          const emailErr = getEmailValidationError(email);
          if (emailErr) {
            reject(new Error(emailErr));
            return;
          }
          if ((db.users || []).some(u => u.email.toLowerCase() === email.trim().toLowerCase())) {
            reject(new Error('Email is already registered'));
            return;
          }
        }
        if (username) {
          if ((db.users || []).some(u => u.username.toLowerCase() === username.trim().toLowerCase())) {
            reject(new Error('Username is already taken'));
            return;
          }
        }
        resolve({ available: true });
        return;
      }

      if (endpoint === '/auth/otp/send' && method === 'POST') {
        const { identifier, email, phone } = body || {};
        const target = (identifier || email || phone || '').trim().toLowerCase();
        if (!target) {
          reject(new Error('Email address or phone number is required.'));
          return;
        }
        if (target.includes('@')) {
          const emailErr = getEmailValidationError(target);
          if (emailErr) {
            reject(new Error(emailErr));
            return;
          }
        }
        const mockOtp = String(Math.floor(100000 + Math.random() * 900000));
        sessionStorage.setItem(`mock_reg_otp_${target}`, mockOtp);
        resolve({
          success: true,
          message: `Verification code sent to ${target}.`,
          identifier: target,
          isEmail: target.includes('@'),
          otpCode: mockOtp
        });
        return;
      }

      if (endpoint === '/auth/otp/verify-login' && method === 'POST') {
        const { identifier, otp } = body || {};
        const target = (identifier || '').trim().toLowerCase();
        const storedOtp = sessionStorage.getItem(`mock_reg_otp_${target}`);
        if (!otp || (storedOtp && String(otp).trim() !== storedOtp)) {
          reject(new Error('Invalid verification code.'));
          return;
        }
        localStorage.setItem('token', 'mock_jwt_token_key');
        const user = db.user || MOCK_DEMO_USER;
        resolve({ token: 'mock_jwt_token_key', user, message: 'Successfully authenticated with OTP.' });
        return;
      }

      if (endpoint === '/auth/oauth/config' && method === 'GET') {
        resolve({
          providers: {
            google: { id: 'google', name: 'Google', enabled: true },
            github: { id: 'github', name: 'GitHub', enabled: true }
          }
        });
        return;
      }

      if (endpoint === '/auth/oauth' && method === 'POST') {
        const { provider, email, name, displayName, avatar } = body;
        if (!email) {
          reject(new Error('Email is required for SSO authentication'));
          return;
        }
        localStorage.setItem('token', `mock_oauth_jwt_${provider}`);
        const userObj = {
          ...db.user,
          name: name || displayName || email.split('@')[0],
          display_name: name || displayName || email.split('@')[0],
          email: email,
          avatar: avatar || db.user.avatar,
          authProvider: provider,
          auth_provider: provider
        };
        db.user = userObj;
        updateMockDb(db);
        resolve({
          token: `mock_oauth_jwt_${provider}`,
          user: userObj,
          isNewUser: false,
          provider: provider
        });
        return;
      }

      if (endpoint === '/auth/oauth/callback' && method === 'POST') {
        const { provider = 'google', code } = body;
        const mockEmail = `${provider}_user@buggyman.dev`;
        localStorage.setItem('token', `mock_oauth_jwt_${provider}`);
        const userObj = {
          ...db.user,
          name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} Developer`,
          display_name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} Developer`,
          email: mockEmail,
          authProvider: provider,
          auth_provider: provider
        };
        db.user = userObj;
        updateMockDb(db);
        resolve({
          token: `mock_oauth_jwt_${provider}`,
          user: userObj,
          isNewUser: false,
          provider: provider,
          message: `Authenticated with ${provider}`
        });
        return;
      }

      if (endpoint === '/auth/oauth/disconnect' && method === 'POST') {
        db.user.authProvider = 'local';
        db.user.auth_provider = 'local';
        updateMockDb(db);
        resolve({ success: true, user: db.user });
        return;
      }

      // 2. Profile API
      if (endpoint === '/profile' && method === 'GET') {
        resolve(db.user);
        return;
      }
      if (endpoint === '/profile' && method === 'PUT') {
        if (body?.display_name) {
          db.user.name = body.display_name;
        }
        if (body?.name) {
          db.user.name = body.name;
        }
        db.user = { ...db.user, ...body };
        updateMockDb(db);
        resolve(db.user);
        return;
      }

      // 2.1 Career Insights API
      if (endpoint.startsWith('/career-insights') && method === 'GET') {
        const u = db.user || {};
        const strengths = u.strengths || ['Backend', 'SQL'];
        const weaknesses = u.weaknesses || ['Frontend'];
        const interests = u.interests || ['Backend Systems & Microservices'];

        const mockRoles = [
          {
            id: 'backend-developer',
            title: 'Backend Developer',
            matchScore: strengths.includes('Backend') ? 88 : 70,
            opportunityScore: 89,
            matchLabel: 'Strong Match',
            explanation: `Matches your declared profile strength in ${strengths.join(', ')} and target career interest. Focus on database optimization to maximize your career readiness.`,
            marketDemand: 'High',
            demandScore: 88,
            marketTrend: 'Growing',
            lastUpdated: '2026-09-01',
            source: 'Global Software Engineering Hiring Index 2026',
            demonstratedStrengths: strengths,
            skillGaps: [{ skill: 'Database Optimization', proficiency: 45, isDeclaredWeakness: false }],
            recommendedArena: 'code',
            arenaName: 'Code Challenges',
            isInterestMatch: interests.some(i => i.toLowerCase().includes('backend')),
            matchedInterests: interests.filter(i => i.toLowerCase().includes('backend')),
            profileStrengths: strengths.filter(s => ['Backend', 'SQL', 'APIs'].includes(s)),
            profileWeaknesses: weaknesses.filter(w => ['Backend', 'SQL', 'APIs'].includes(w)),
            recommendedChallenges: [
              { id: '1', title: 'Fix Django Session Authentication', difficulty: 'Easy', technology: 'Django', category: 'Backend', reason: 'Improves Backend proficiency.' }
            ]
          },
          {
            id: 'frontend-developer',
            title: 'Frontend Developer',
            matchScore: strengths.includes('Frontend') ? 85 : weaknesses.includes('Frontend') ? 45 : 62,
            opportunityScore: 68,
            matchLabel: strengths.includes('Frontend') ? 'Strong Match' : 'Developing Match',
            explanation: weaknesses.includes('Frontend')
              ? "Marked as an area to improve in your profile. Solving frontend challenges will help bridge this gap."
              : "Aligns with web and client-side engineering fundamentals.",
            marketDemand: 'High',
            demandScore: 82,
            marketTrend: 'Stable',
            lastUpdated: '2026-09-01',
            source: 'Global Software Engineering Hiring Index 2026',
            demonstratedStrengths: strengths.filter(s => ['Frontend', 'React', 'CSS'].includes(s)),
            skillGaps: [{ skill: 'Frontend', proficiency: weaknesses.includes('Frontend') ? 35 : 60, isDeclaredWeakness: weaknesses.includes('Frontend') }],
            recommendedArena: 'frontend',
            arenaName: 'Frontend Studio',
            isInterestMatch: interests.some(i => i.toLowerCase().includes('frontend')),
            matchedInterests: interests.filter(i => i.toLowerCase().includes('frontend')),
            profileStrengths: strengths.filter(s => ['Frontend', 'React', 'CSS'].includes(s)),
            profileWeaknesses: weaknesses.filter(w => ['Frontend', 'React', 'CSS'].includes(w)),
            recommendedChallenges: [
              { id: 'FE-E01', title: 'Responsive Navbar Flexbox Bug', difficulty: 'Easy', technology: 'React', category: 'Frontend', reason: 'Strengthens Frontend skills.' }
            ]
          },
          {
            id: 'fullstack-developer',
            title: 'Full-Stack Developer',
            matchScore: 80,
            opportunityScore: 86,
            matchLabel: 'Strong Match',
            explanation: `Combines your strengths in ${strengths[0] || 'core engineering'} with full lifecycle application delivery.`,
            marketDemand: 'Very High',
            demandScore: 94,
            marketTrend: 'Growing',
            lastUpdated: '2026-09-01',
            source: 'Global Software Engineering Hiring Index 2026',
            demonstratedStrengths: strengths,
            skillGaps: [{ skill: weaknesses[0] || 'Testing', proficiency: 40, isDeclaredWeakness: true }],
            recommendedArena: 'code',
            arenaName: 'Code Challenges',
            isInterestMatch: interests.some(i => i.toLowerCase().includes('full stack')),
            matchedInterests: interests.filter(i => i.toLowerCase().includes('full stack')),
            profileStrengths: strengths,
            profileWeaknesses: weaknesses,
            recommendedChallenges: [
              { id: '2', title: 'Full-Stack JWT Token Refresh Bug', difficulty: 'Medium', technology: 'Node.js', category: 'Full Stack', reason: 'Deepens Full-Stack integration.' }
            ]
          }
        ];

        mockRoles.sort((a, b) => (b.isInterestMatch ? 1 : 0) - (a.isInterestMatch ? 1 : 0) || b.matchScore - a.matchScore);

        resolve({
          isInsufficientData: false,
          dataMessage: `Personalized for ${u.name || 'Developer'} based on declared profile preferences and performance.`,
          userProfile: {
            name: u.name || 'Developer',
            username: u.username || 'developer',
            avatar: u.avatar || '',
            college: u.college || 'State Technical University',
            bio: u.bio || '',
            strengths: strengths,
            weaknesses: weaknesses,
            interests: interests,
            challengesSolved: u.challenges_solved || u.challengesSolved || 0,
            totalScore: u.total_score || u.totalScore || 0,
            streak: u.streak || 0
          },
          topMatch: mockRoles[0],
          roles: mockRoles,
          disclaimer: 'Market insights reflect current software engineering hiring benchmarks and update periodically.'
        });
        return;
      }

      // 3. Challenges APIs
      if ((endpoint === '/challenges' || endpoint.startsWith('/challenges?')) && method === 'GET') {
        const queryStr = endpoint.includes('?') ? endpoint.split('?')[1] : '';
        const params = new URLSearchParams(queryStr);
        const arena = params.get('arena') || 'code';
        const u = db.user || {};
        const strengths = (u.strengths || []).map(s => s.toLowerCase());
        const weaknesses = (u.weaknesses || []).map(w => w.toLowerCase());

        let list = DJANGO_MOCK_CHALLENGES;
        if (arena === 'sql') {
          list = SQL_MOCK_CHALLENGES || DJANGO_MOCK_CHALLENGES;
        } else if (arena === 'frontend') {
          list = FRONTEND_MOCK_CHALLENGES || DJANGO_MOCK_CHALLENGES;
        }

        const personalizedList = list.map(c => {
          const cat = (c.category || '').toLowerCase();
          const tech = (c.technology || '').toLowerCase();
          const isWeakness = weaknesses.some(w => cat.includes(w) || tech.includes(w));
          const isStrength = strengths.some(s => cat.includes(s) || tech.includes(s));
          let score = 65;
          let reason = `Recommended practice in ${c.category || c.technology}.`;

          if (isWeakness) {
            score = 85;
            reason = `Recommended for your ${c.category || c.technology} skill gap (35% mastery).`;
          } else if (isStrength) {
            score = 75;
            reason = `Recommended based on your strength in ${c.technology} to build advanced mastery.`;
          }

          return {
            ...c,
            recommendationScore: score,
            reason: reason,
            recommendationReason: reason,
            isPersonalized: true,
            isSolved: false
          };
        });

        personalizedList.sort((a, b) => b.recommendationScore - a.recommendationScore);
        resolve(personalizedList);
        return;
      }

      if (endpoint.startsWith('/challenges/') && method === 'GET') {
        const id = endpoint.split('/').pop();
        const challenge = db.challenges.find(c => c.id === id)
          || DJANGO_MOCK_CHALLENGES.find(c => c.id === id)
          || SQL_MOCK_CHALLENGES.find(c => c.id === id)
          || FRONTEND_MOCK_CHALLENGES.find(c => c.id === id);
        if (challenge) {
          resolve(challenge);
        } else {
          reject(new Error('Challenge not found'));
        }
        return;
      }

      if (endpoint.startsWith('/challenges/') && endpoint.endsWith('/submit') && method === 'POST') {
        // Evaluate code submission
        const id = endpoint.split('/')[2];
        const challenge = db.challenges.find(c => c.id === id)
          || DJANGO_MOCK_CHALLENGES.find(c => c.id === id)
          || SQL_MOCK_CHALLENGES.find(c => c.id === id)
          || FRONTEND_MOCK_CHALLENGES.find(c => c.id === id);
        if (!challenge) {
          reject(new Error('Challenge not found'));
          return;
        }
        
        // Simulating checking if user fixed the code:
        // We will simple compare editor contents with challenge's bug signature
        const { code } = body;
        const bugFixed = !code.includes(challenge.bugSignature);

        if (bugFixed) {
          // Increment completed challenges in database
          db.user.challengesSolved += 1;
          db.user.totalScore += challenge.points;
          db.user.activities.unshift({
            id: Date.now(),
            text: `Completed "${challenge.title}"`,
            time: 'Just now',
            xp: challenge.points
          });
          // Update analytics
          db.analytics.totalSolved = db.user.challengesSolved;
          updateMockDb(db);
          resolve({
            success: true,
            score: challenge.points,
            timeTaken: '4m 32s',
            bugsFixed: 1,
            remainingIssues: 0,
            testCases: challenge.testCases.map(tc => ({ ...tc, passed: true })),
            aiSummary: 'Excellent code correction! You replaced direct state mutation with immutable copies, enabling correct React virtual DOM comparisons.'
          });
        } else {
          resolve({
            success: false,
            score: 0,
            timeTaken: '4m 32s',
            bugsFixed: 0,
            remainingIssues: 1,
            testCases: challenge.testCases.map((tc, idx) => ({ ...tc, passed: idx === 0 })),
            aiSummary: 'We still detect state mutation or invalid validation logic. Make sure you fix the buggy segments and do not directly assign properties of the existing state.'
          });
        }
        return;
      }

      // 4. Analytics
      if (endpoint === '/analytics' && method === 'GET') {
        resolve(db.analytics);
        return;
      }

      // 5. Leaderboard
      if (endpoint === '/leaderboard' && method === 'GET') {
        resolve(db.leaderboard);
        return;
      }

      // 6. Notifications
      if (endpoint === '/notifications' && method === 'GET') {
        resolve(db.notifications);
        return;
      }
      if (endpoint.startsWith('/notifications/') && endpoint.endsWith('/read') && method === 'POST') {
        const id = parseInt(endpoint.split('/')[2]);
        db.notifications = db.notifications.map(n => n.id === id ? { ...n, read: true } : n);
        updateMockDb(db);
        resolve({ success: true });
        return;
      }

      // 7. Admin Endpoint
      if (endpoint === '/admin/stats' && method === 'GET') {
        resolve({
          ...db.adminStats,
          challenges: db.challenges,
          users: [
            { id: 1, name: 'Alex Rivera', email: 'alex@mit.edu', solved: 22 },
            { id: 2, name: 'Sam Chen', email: 'sam@stanford.edu', solved: 18 },
            { id: 3, name: 'Jane Doe', email: 'jane.doe@college.edu', solved: db.user.challengesSolved }
          ]
        });
        return;
      }

      if (endpoint === '/challenges/generate' && method === 'POST') {
        const difficulty = body?.difficulty || 'Easy';
        const technology = body?.technology || 'React';
        const newChallenge = {
          id: String(Date.now()),
          title: `Fix ${technology} ${difficulty} Bug #${Math.floor(Math.random() * 900 + 100)}`,
          description: `Dynamically generated ${difficulty} debugging task focusing on ${technology} runtime state and memory integrity.`,
          difficulty,
          technology,
          category: 'AI Generated',
          timeEstimate: '15 mins',
          points: difficulty === 'Easy' ? 100 : difficulty === 'Medium' ? 150 : 300,
          files: [
            {
              name: technology === 'React' ? 'App.jsx' : 'views.py',
              content: technology === 'React' 
                ? "import React, { useState } from 'react';\n\nexport default function App() {\n  const [val, setVal] = useState(0);\n  const handleClick = () => {\n    // BUG: Direct mutation\n    val = val + 1;\n    setVal(val);\n  };\n  return <button onClick={handleClick}>{val}</button>;\n}"
                : "from rest_framework.decorators import api_view\nfrom rest_framework.response import Response\n\n@api_view(['POST'])\ndef create_item(request):\n    # BUG: Missing validation\n    data = request.data\n    return Response(data, status=200)"
            }
          ],
          testCases: [{ id: 1, name: 'Passes execution check', input: '', expected: 'Success', passed: false }],
          bugSignature: technology === 'React' ? 'val = val + 1;' : '# BUG: Missing validation',
          suspectedComponent: technology === 'React' ? 'handleClick in App.jsx' : 'create_item in views.py',
          aiSuggestions: ['Review state mutation rules and validation checks.']
        };
        db.challenges.unshift(newChallenge);
        updateMockDb(db);
        resolve(newChallenge);
        return;
      }

      if (endpoint === '/admin/challenges' && method === 'POST') {

        const newChallenge = {
          id: String(db.challenges.length + 1),
          title: body.title,
          description: body.description,
          difficulty: body.difficulty,
          technology: body.technology,
          category: body.category,
          timeEstimate: body.timeEstimate,
          points: parseInt(body.points || 100),
          files: body.files || [{ name: 'index.js', content: '// Bug here' }],
          testCases: body.testCases || [{ id: 1, name: 'Runs without crash', input: '', expected: '', passed: false }],
          bugSignature: body.bugSignature || '',
          suspectedComponent: body.suspectedComponent || '',
          aiSuggestions: body.aiSuggestions || ['Check variable declarations']
        };
        db.challenges.push(newChallenge);
        db.adminStats.totalChallenges += 1;
        updateMockDb(db);
        resolve(newChallenge);
        return;
      }

      // 8. PvP Mock APIs
      if (endpoint === '/pvp/history' && method === 'GET') {
        const storedHistory = JSON.parse(localStorage.getItem('buggyman_pvp_history') || 'null');
        if (storedHistory) {
          resolve(storedHistory);
          return;
        }
        const defaultHistory = [
          {
            id: 'pvp-hist-1',
            battleId: 'b-9021',
            opponentName: 'CodeViper',
            opponentAvatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150',
            opponentRating: 1480,
            challengeTitle: 'Counter state doesn\'t update',
            technology: 'React',
            difficulty: 'Easy',
            result: 'Won',
            solveTime: '2m 14s',
            testsPassed: '3/3',
            opponentTestsPassed: '2/3',
            xpEarned: 150,
            date: '2 hours ago'
          },
          {
            id: 'pvp-hist-2',
            battleId: 'b-8742',
            opponentName: 'Sarah Jenkins',
            opponentAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
            opponentRating: 1620,
            challengeTitle: 'Missing CSRF token on form submission',
            technology: 'Django',
            difficulty: 'Medium',
            result: 'Lost',
            solveTime: '4m 32s',
            testsPassed: '2/4',
            opponentTestsPassed: '4/4',
            xpEarned: 40,
            date: 'Yesterday'
          },
          {
            id: 'pvp-hist-3',
            battleId: 'b-7619',
            opponentName: 'NullPointer',
            opponentAvatar: 'https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=150',
            opponentRating: 1390,
            challengeTitle: 'Dark/Light Theme',
            technology: 'CSS',
            difficulty: 'Easy',
            result: 'Won',
            solveTime: '1m 45s',
            testsPassed: '3/3',
            opponentTestsPassed: '1/3',
            xpEarned: 120,
            date: '3 days ago'
          },
          {
            id: 'pvp-hist-4',
            battleId: 'b-6531',
            opponentName: 'CyberSamurai',
            opponentAvatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
            opponentRating: 1540,
            challengeTitle: 'Search Bugs',
            technology: 'React',
            difficulty: 'Easy',
            result: 'Draw',
            solveTime: '10m 00s',
            testsPassed: '2/3',
            opponentTestsPassed: '2/3',
            xpEarned: 60,
            date: '5 days ago'
          }
        ];
        localStorage.setItem('buggyman_pvp_history', JSON.stringify(defaultHistory));
        resolve(defaultHistory);
        return;
      }

      const getPvPStore = () => JSON.parse(sessionStorage.getItem('buggyman_pvp_battles') || '{}');
      const savePvPStore = (store) => sessionStorage.setItem('buggyman_pvp_battles', JSON.stringify(store));

      const opponentsPool = [
        { name: 'CyberSamurai', avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150', rating: 1420 },
        { name: 'HexHacker', avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150', rating: 1380 },
        { name: 'BugBuster_X', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150', rating: 1490 },
        { name: 'NullPointer', avatar: 'https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=150', rating: 1350 },
        { name: 'CodeNinja_99', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150', rating: 1510 }
      ];

      const getRandomOpponent = () => opponentsPool[Math.floor(Math.random() * opponentsPool.length)];

      const selectChallengeForPvP = (diff) => {
        const pool = (db.challenges || []).concat(FRONTEND_MOCK_CHALLENGES);
        const filtered = pool.filter(c => !diff || diff === 'All' || c.difficulty === diff);
        const picked = filtered.length > 0 ? filtered[Math.floor(Math.random() * filtered.length)] : pool[0];
        return JSON.parse(JSON.stringify(picked));
      };

      if (endpoint === '/pvp/quick-match' && method === 'POST') {
        const difficulty = body?.difficulty || 'All';
        const challenge = selectChallengeForPvP(difficulty);
        const totalTests = challenge.testCases?.length || 3;
        const opp = getRandomOpponent();
        const battleId = 'battle_' + Math.random().toString(36).substring(2, 9);
        const roomCode = 'ROOM-' + Math.floor(1000 + Math.random() * 9000);

        const battle = {
          battleId,
          roomCode,
          status: 'MATCHED',
          difficulty: challenge.difficulty || 'Easy',
          timeLimit: body?.timeLimit || 600,
          timeRemaining: body?.timeLimit || 600,
          startedAt: null,
          challenge,
          player1: {
            id: db.user?.id || 'usr-current',
            name: db.user?.name || 'You',
            avatar: db.user?.avatar || '',
            rating: 1450,
            testsPassed: 0,
            totalTests,
            hasSubmitted: false
          },
          player2: {
            id: 'opp_' + Math.random().toString(36).substring(2, 6),
            name: opp.name,
            avatar: opp.avatar,
            rating: opp.rating,
            testsPassed: 0,
            totalTests,
            hasSubmitted: false
          },
          winner: null
        };

        const store = getPvPStore();
        store[battleId] = battle;
        store[roomCode] = battle;
        savePvPStore(store);

        resolve(battle);
        return;
      }

      if (endpoint === '/pvp/create' && method === 'POST') {
        const difficulty = body?.difficulty || 'All';
        const timeLimit = body?.timeLimit || 600;
        const challenge = selectChallengeForPvP(difficulty);
        const totalTests = challenge.testCases?.length || 3;
        const battleId = 'battle_' + Math.random().toString(36).substring(2, 9);
        const roomCode = 'ROOM-' + Math.floor(1000 + Math.random() * 9000);

        const battle = {
          battleId,
          roomCode,
          status: 'WAITING',
          difficulty: challenge.difficulty || 'Easy',
          timeLimit,
          timeRemaining: timeLimit,
          startedAt: null,
          createdAt: Date.now(),
          challenge,
          player1: {
            id: db.user?.id || 'usr-current',
            name: db.user?.name || 'You',
            avatar: db.user?.avatar || '',
            rating: 1450,
            testsPassed: 0,
            totalTests,
            hasSubmitted: false
          },
          player2: null,
          winner: null
        };

        const store = getPvPStore();
        store[battleId] = battle;
        store[roomCode] = battle;
        savePvPStore(store);

        resolve(battle);
        return;
      }

      if (endpoint === '/pvp/join' && method === 'POST') {
        const roomCode = (body?.roomCode || '').trim().toUpperCase();
        const store = getPvPStore();
        let battle = store[roomCode];

        if (!battle) {
          // If room doesn't exist yet, auto-create a match for convenience
          const challenge = selectChallengeForPvP('Easy');
          const totalTests = challenge.testCases?.length || 3;
          const opp = getRandomOpponent();
          const battleId = 'battle_' + Math.random().toString(36).substring(2, 9);
          battle = {
            battleId,
            roomCode,
            status: 'MATCHED',
            difficulty: challenge.difficulty || 'Easy',
            timeLimit: 600,
            timeRemaining: 600,
            startedAt: null,
            challenge,
            player1: {
              id: 'host_' + Math.random().toString(36).substring(2, 6),
              name: opp.name,
              avatar: opp.avatar,
              rating: opp.rating,
              testsPassed: 0,
              totalTests,
              hasSubmitted: false
            },
            player2: {
              id: db.user?.id || 'usr-current',
              name: db.user?.name || 'You',
              avatar: db.user?.avatar || '',
              rating: 1450,
              testsPassed: 0,
              totalTests,
              hasSubmitted: false
            },
            winner: null
          };
          store[battleId] = battle;
          store[roomCode] = battle;
          savePvPStore(store);
          resolve(battle);
          return;
        }

        if (battle.status === 'WAITING') {
          const opp = getRandomOpponent();
          battle.player2 = {
            id: db.user?.id || 'usr-current',
            name: db.user?.name || 'You',
            avatar: db.user?.avatar || '',
            rating: 1450,
            testsPassed: 0,
            totalTests: battle.player1.totalTests,
            hasSubmitted: false
          };
          battle.status = 'MATCHED';
          store[battle.battleId] = battle;
          store[roomCode] = battle;
          savePvPStore(store);
        }

        resolve(battle);
        return;
      }

      if (endpoint.startsWith('/pvp/') && endpoint.endsWith('/status') && method === 'GET') {
        const battleId = endpoint.split('/')[2];
        const store = getPvPStore();
        let battle = store[battleId];

        if (!battle) {
          // Provide default ongoing mock battle
          const challenge = selectChallengeForPvP('Easy');
          const opp = getRandomOpponent();
          battle = {
            battleId,
            roomCode: 'BUG-4892',
            status: 'IN_PROGRESS',
            difficulty: 'Easy',
            timeLimit: 600,
            timeRemaining: 550,
            startedAt: Date.now() - 50000,
            challenge,
            player1: {
              id: db.user?.id || 'usr-current',
              name: db.user?.name || 'You',
              avatar: db.user?.avatar || '',
              rating: 1450,
              testsPassed: 1,
              totalTests: challenge.testCases?.length || 3,
              hasSubmitted: false
            },
            player2: {
              id: 'opp-1',
              name: opp.name,
              avatar: opp.avatar,
              rating: opp.rating,
              testsPassed: 1,
              totalTests: challenge.testCases?.length || 3,
              hasSubmitted: false
            },
            winner: null
          };
          store[battleId] = battle;
          savePvPStore(store);
        }

        // If waiting for over 4 seconds, auto-match with simulated opponent
        if (battle.status === 'WAITING' && battle.createdAt && Date.now() - battle.createdAt > 4000) {
          const opp = getRandomOpponent();
          battle.player2 = {
            id: 'opp_' + Math.random().toString(36).substring(2, 6),
            name: opp.name,
            avatar: opp.avatar,
            rating: opp.rating,
            testsPassed: 0,
            totalTests: battle.player1.totalTests,
            hasSubmitted: false
          };
          battle.status = 'MATCHED';
          store[battleId] = battle;
          savePvPStore(store);
        }

        // Simulate opponent test progression during IN_PROGRESS
        if (battle.status === 'IN_PROGRESS' && battle.player2 && !battle.player2.hasSubmitted) {
          const total = battle.player2.totalTests || 3;
          const elapsed = battle.startedAt ? Math.floor((Date.now() - battle.startedAt) / 1000) : 0;
          // Progress opponent every 20-30 seconds
          const simulatedPassed = Math.min(total - 1, Math.floor(elapsed / 25));
          if (simulatedPassed > (battle.player2.testsPassed || 0)) {
            battle.player2.testsPassed = simulatedPassed;
            store[battleId] = battle;
            savePvPStore(store);
          }
        }

        resolve(battle);
        return;
      }

      if (endpoint.startsWith('/pvp/') && endpoint.endsWith('/start') && method === 'POST') {
        const battleId = endpoint.split('/')[2];
        const store = getPvPStore();
        let battle = store[battleId];
        if (battle) {
          battle.status = 'IN_PROGRESS';
          if (!battle.startedAt) battle.startedAt = Date.now();
          store[battleId] = battle;
          savePvPStore(store);
          resolve(battle);
        } else {
          resolve({ success: true, status: 'IN_PROGRESS', startedAt: Date.now() });
        }
        return;
      }

      if (endpoint.startsWith('/pvp/') && endpoint.endsWith('/progress') && method === 'POST') {
        const battleId = endpoint.split('/')[2];
        const store = getPvPStore();
        let battle = store[battleId];
        if (battle && battle.player1) {
          battle.player1.testsPassed = body.testsPassed ?? battle.player1.testsPassed;
          store[battleId] = battle;
          savePvPStore(store);
          resolve({ success: true, player1: battle.player1, player2: battle.player2 });
        } else {
          resolve({ success: true });
        }
        return;
      }

      if (endpoint.startsWith('/pvp/') && endpoint.endsWith('/submit') && method === 'POST') {
        const battleId = endpoint.split('/')[2];
        const store = getPvPStore();
        let battle = store[battleId] || {};
        
        const totalTests = battle.challenge?.testCases?.length || 3;
        const testsPassed = totalTests; // Successful submission
        const solveTimeSeconds = battle.startedAt ? Math.floor((Date.now() - battle.startedAt) / 1000) : 124;
        const minutes = Math.floor(solveTimeSeconds / 60);
        const seconds = solveTimeSeconds % 60;
        const formattedTime = `${minutes}m ${seconds < 10 ? '0' : ''}${seconds}s`;

        battle.status = 'COMPLETED';
        battle.winner = battle.player1?.id || 'usr-current';
        if (battle.player1) {
          battle.player1.testsPassed = testsPassed;
          battle.player1.hasSubmitted = true;
        }

        store[battleId] = battle;
        savePvPStore(store);

        // Record in history
        const history = JSON.parse(localStorage.getItem('buggyman_pvp_history') || '[]');
        const historyEntry = {
          id: 'pvp-hist-' + Date.now(),
          battleId,
          opponentName: battle.player2?.name || 'CyberSamurai',
          opponentAvatar: battle.player2?.avatar || '',
          opponentRating: battle.player2?.rating || 1400,
          challengeTitle: battle.challenge?.title || 'PvP Challenge',
          technology: battle.challenge?.technology || 'React',
          difficulty: battle.challenge?.difficulty || 'Easy',
          result: 'Won',
          solveTime: formattedTime,
          testsPassed: `${testsPassed}/${totalTests}`,
          opponentTestsPassed: `${battle.player2?.testsPassed || 1}/${totalTests}`,
          xpEarned: 150,
          date: 'Just now'
        };
        history.unshift(historyEntry);
        localStorage.setItem('buggyman_pvp_history', JSON.stringify(history.slice(0, 20)));

        resolve({
          success: true,
          status: 'COMPLETED',
          winner: battle.player1?.id || 'usr-current',
          isWinner: true,
          solveTime: solveTimeSeconds,
          formattedTime,
          testsPassed,
          totalTests,
          xpEarned: 150,
          player1: battle.player1,
          player2: battle.player2,
          message: 'Victory! You squashed the bug before your opponent.'
        });
        return;
      }

      if (endpoint.startsWith('/pvp/') && endpoint.endsWith('/cancel') && method === 'POST') {
        const battleId = endpoint.split('/')[2];
        const store = getPvPStore();
        if (store[battleId]) {
          store[battleId].status = 'CANCELLED';
          savePvPStore(store);
        }
        resolve({ success: true, message: 'Battle cancelled.' });
        return;
      }

      // 9. BugBytes Store & Payment Simulation Mock APIs
      if (endpoint === '/store/packages' && method === 'GET') {
        const defaultPackages = [
          { id: 1, name: 'Starter Pack', bugbytes: 50, price_inr: 49, is_popular: false, tag: 'Beginner', mission_days: 7, challenges_required: 2 },
          { id: 2, name: 'Pro Debugger', bugbytes: 150, price_inr: 129, is_popular: true, tag: 'Most Popular', mission_days: 10, challenges_required: 4 },
          { id: 3, name: 'Master Hacker', bugbytes: 400, price_inr: 299, is_popular: false, tag: 'Best Value', mission_days: 14, challenges_required: 8 }
        ];
        resolve({ packages: defaultPackages, userBalance: db.user.bugbytes_balance || db.user.bugbytesBalance || 0 });
        return;
      }

      if (endpoint === '/store/checkout' && method === 'POST') {
        const pkgId = body?.packageId;
        const defaultPackages = [
          { id: 1, name: 'Starter Pack', bugbytes: 50, price_inr: 49 },
          { id: 2, name: 'Pro Debugger', bugbytes: 150, price_inr: 129 },
          { id: 3, name: 'Master Hacker', bugbytes: 400, price_inr: 299 }
        ];
        const pkg = defaultPackages.find(p => p.id === pkgId) || defaultPackages[0];
        const mockPurchase = {
          id: Date.now(),
          transactionReference: 'BB-ORD-' + Math.floor(100000 + Math.random() * 900000),
          packageName: pkg.name,
          packageId: pkg.id,
          bugbytesAmount: pkg.bugbytes,
          priceInr: pkg.price_inr,
          status: 'PENDING',
          canRefund: false,
          createdAt: new Date().toISOString()
        };
        const purchases = JSON.parse(localStorage.getItem('buggyman_purchases') || '[]');
        purchases.unshift(mockPurchase);
        localStorage.setItem('buggyman_purchases', JSON.stringify(purchases));
        resolve({ purchase: mockPurchase });
        return;
      }

      if (endpoint === '/store/confirm-payment' && method === 'POST') {
        const { transactionReference, simulateOutcome = 'SUCCESS' } = body || {};
        const purchases = JSON.parse(localStorage.getItem('buggyman_purchases') || '[]');
        const idx = purchases.findIndex(p => p.transactionReference === transactionReference);
        const purchase = idx >= 0 ? purchases[idx] : {
          id: Date.now(),
          transactionReference: transactionReference || 'BB-ORD-999',
          packageName: 'Pro Debugger',
          bugbytesAmount: 150,
          priceInr: 129,
          status: 'PENDING',
          createdAt: new Date().toISOString()
        };

        if (simulateOutcome === 'SUCCESS') {
          purchase.status = 'COMPLETED';
          purchase.canRefund = true;
          const currentBal = db.user.bugbytes_balance || db.user.bugbytesBalance || 0;
          const newBal = currentBal + purchase.bugbytesAmount;
          db.user.bugbytes_balance = newBal;
          db.user.bugbytesBalance = newBal;
          updateMockDb(db);
          if (idx >= 0) purchases[idx] = purchase;
          else purchases.unshift(purchase);
          localStorage.setItem('buggyman_purchases', JSON.stringify(purchases));

          resolve({
            success: true,
            message: `Simulated payment successful! +${purchase.bugbytesAmount} BugBytes credited.`,
            purchase,
            newBalance: newBal
          });
        } else {
          purchase.status = 'FAILED';
          purchase.canRefund = false;
          if (idx >= 0) purchases[idx] = purchase;
          else purchases.unshift(purchase);
          localStorage.setItem('buggyman_purchases', JSON.stringify(purchases));

          resolve({
            success: false,
            message: 'Simulated payment failed. No BugBytes were credited.',
            purchase,
            failureReason: body?.failureReason || 'Simulated card/UPI decline test.'
          });
        }
        return;
      }

      if (endpoint === '/store/purchases' && method === 'GET') {
        const purchases = JSON.parse(localStorage.getItem('buggyman_purchases') || '[]');
        resolve({ purchases, totalCount: purchases.length });
        return;
      }

      if (endpoint.startsWith('/store/purchases/') && endpoint.endsWith('/refund') && method === 'POST') {
        const purchaseId = parseInt(endpoint.split('/')[3]);
        const purchases = JSON.parse(localStorage.getItem('buggyman_purchases') || '[]');
        const idx = purchases.findIndex(p => p.id === purchaseId);
        if (idx < 0) {
          reject(new Error('Purchase record not found.'));
          return;
        }
        const purchase = purchases[idx];
        if (purchase.status !== 'COMPLETED' || purchase.refundedAt) {
          reject(new Error('Only completed, unrefunded purchases can be refunded.'));
          return;
        }

        purchase.status = 'REFUNDED';
        purchase.refundAmountInr = purchase.priceInr;
        purchase.refundReason = body?.reason || '100% Money-Back Guarantee: Completed required challenges on time';
        purchase.refundedAt = new Date().toISOString();
        purchase.canRefund = false;
        purchases[idx] = purchase;
        localStorage.setItem('buggyman_purchases', JSON.stringify(purchases));

        // Note: BugBytes are NOT deducted! User keeps all their BugBytes as their learning reward.
        const userBalance = db.user.bugbytes_balance || db.user.bugbytesBalance || 0;

        resolve({
          success: true,
          message: `Successfully refunded ₹${purchase.priceInr}! You keep all your BugBytes for completing the challenges on time.`,
          purchase,
          newBalance: userBalance
        });
        return;
      }

      if (endpoint === '/store/missions' && method === 'GET') {
        resolve({ missions: [], activeMissions: [], completedMissions: [], claimedMissions: [], expiredMissions: [] });
        return;
      }

      if (endpoint === '/store/rewards' && method === 'GET') {
        resolve({ totalPurchasedInr: 0, totalRewardedInr: 0, netSimulatedCostInr: 0, rewards: [] });
        return;
      }

      // Fallback fallback:
      resolve({ status: 'success', data: {} });
    }, 400); // simulate network latency
  });
}
