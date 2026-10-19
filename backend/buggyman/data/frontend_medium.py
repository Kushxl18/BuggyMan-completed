"""
Frontend Studio: Medium Challenges (96 to 110)
"""

def get_frontend_medium():
    challenges = []

    # 96. Rapid search requests overwrite newer results
    challenges.append({
        'id': 96,
        'title': '[FE-M01] Rapid Search Requests Overwrite Newer Results',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Asynchronous UI',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An enterprise documentation portal provides a live typeahead search across thousands of API endpoints.

### Bug Report
When typing quickly (e.g. searching for "users" by typing "u", "us", "use", "user", "users"), the query for "us" took 350ms while "users" took 80ms. The earlier slow response arrived last and overwrote the results, leaving stale results for "us" visible on the screen even though the input displays "users".

### Steps to Reproduce
1. Open `LiveSearch.jsx`.
2. Type query rapidly into the search field.
3. Observe race condition where network latency differences cause out-of-order state updates.

### Expected Behavior
The search component must ignore responses from stale queries or abort previous in-flight requests using an `active` flag or `AbortController`.

### Actual Behavior
Component unconditionally calls `setResults(data)` in the `.then()` callback regardless of whether the query is still the latest one.

### Impact
Users see irrelevant search results that do not match the text in the search input, causing confusion and incorrect navigation.

### Requirements
- Implement a request cancellation flag or controller to ignore responses from stale or superseded search requests.
- Only update state if the request is still current.
""",
        'files': [{
            'name': 'LiveSearch.jsx',
            'content': '''import React, { useState, useEffect } from 'react';

export default function LiveSearch({ fetchResults }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    fetchResults(query).then(data => {
      setResults(data);
    });
  }, [query, fetchResults]);

  return (
    <div className="search-container p-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documentation..."
        className="border p-2 rounded w-full"
      />
      <ul className="mt-2 divide-y">
        {results.map((item, idx) => (
          <li key={idx} className="p-2">{item.title}</li>
        ))}
      </ul>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Uses cancellation flag or AbortController to prevent race conditions', 'input': '', 'expected': 'active'}
        ],
        'bug_signature': 'fetchResults(query).then(data => {\n      setResults(data);',
        'suspected_component': 'LiveSearch.jsx',
        'ai_suggestions': [
            'Introduce a boolean flag `let active = true;` inside the `useEffect`.',
            'Check `if (active) setResults(data);` before updating state, and return a cleanup function `() => { active = false; };`.'
        ],
        'topics': ['React', 'Async', 'Race Conditions', 'useEffect'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Hooks', 'Asynchronous JavaScript'],
        'status': 'published'
    })

    # 97. React state updates lose changes during batched operations
    challenges.append({
        'id': 97,
        'title': '[FE-M02] React State Updates Lose Changes During Batched Operations',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'State Management',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An inventory ticketing application allows warehouse workers to quickly increment box counts by +3 using a shortcut button.

### Bug Report
Clicking "+3" only increments the box count by 1 instead of 3.

### Steps to Reproduce
1. In `CounterBatch.jsx`, click the "+3" button.
2. The button calls `incrementByThree()`, which invokes `setCount(count + 1)` three times in a row.
3. Box count changes from 0 to 1 instead of 0 to 3.

### Expected Behavior
Each sequential update must incorporate the latest queued state transition so the counter increments by the full expected amount.

### Actual Behavior
All three `setCount(count + 1)` calls read the same snapshot value of `count` from the current render closure.

### Impact
Warehouse staff submit incorrect inventory counts, leading to stock discrepancies.

### Requirements
- Use functional state updates to ensure all increments are applied correctly during batched state transitions.
""",
        'files': [{
            'name': 'CounterBatch.jsx',
            'content': '''import React, { useState } from 'react';

export default function CounterBatch() {
  const [count, setCount] = useState(0);

  const incrementByThree = () => {
    setCount(count + 1);
    setCount(count + 1);
    setCount(count + 1);
  };

  return (
    <div className="p-4">
      <p className="text-lg font-bold">Boxes: {count}</p>
      <button
        onClick={incrementByThree}
        className="bg-emerald-600 text-white px-3 py-1 rounded mt-2"
      >
        +3 Quick Add
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Uses functional state updater prev => prev + 1', 'input': '', 'expected': 'prev =>'}
        ],
        'bug_signature': 'setCount(count + 1);\n    setCount(count + 1);\n    setCount(count + 1);',
        'suspected_component': 'CounterBatch.jsx',
        'ai_suggestions': [
            'Use functional updates: `setCount(prev => prev + 1)` instead of reading `count` from closure.'
        ],
        'topics': ['React', 'State', 'Batching'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Management'],
        'status': 'published'
    })

    # 98. useEffect dependency causes stale values or repeated requests
    challenges.append({
        'id': 98,
        'title': '[FE-M03] useEffect Dependency Causes Stale Values or Missing Updates',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'React Hooks',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A customer support portal displays user details in a sidebar drawer. As support agents click different ticket owners, `userId` changes.

### Bug Report
When an agent clicks between User A and User B, the drawer continues to show User A's details because the effect dependency array is empty `[]`.

### Steps to Reproduce
1. Mount `UserProfileLoader.jsx` with `userId = "usr_101"`. Profile loads.
2. Parent changes prop to `userId = "usr_202"`.
3. Profile does not reload and keeps showing data for `usr_101`.

### Expected Behavior
Effect must re-run whenever `userId` changes by declaring `userId` in the dependency array: `[userId, fetchUser]`.

### Actual Behavior
Dependency array is `[]`, closing over initial `userId` and never refetching.

### Impact
Agents take actions on wrong customer accounts due to stale profile displays.

### Requirements
- Add `userId` (and `fetchUser`) to the `useEffect` dependency array.
""",
        'files': [{
            'name': 'UserProfileLoader.jsx',
            'content': '''import React, { useState, useEffect } from 'react';

export default function UserProfileLoader({ userId, fetchUser }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    fetchUser(userId).then(data => {
      if (isMounted) {
        setProfile(data);
        setLoading(false);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <p>Loading profile...</p>;
  return (
    <div className="profile-card p-4">
      <h2 className="text-xl font-bold">{profile?.name}</h2>
      <p>{profile?.email}</p>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Declares userId in dependency array', 'input': '', 'expected': '[userId'}
        ],
        'bug_signature': '}, []);',
        'suspected_component': 'UserProfileLoader.jsx',
        'ai_suggestions': [
            'Add `userId` to the `useEffect` dependency array: `[userId, fetchUser]` or `[userId]`.'
        ],
        'topics': ['React', 'Hooks', 'useEffect', 'Dependencies'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Hooks Rules'],
        'status': 'published'
    })

    # 99. Shopping cart calculates totals incorrectly after quantity updates
    challenges.append({
        'id': 99,
        'title': '[FE-M04] Shopping Cart Calculates Totals Incorrectly After Mutation',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'State Immutability',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An online grocery checkout component allows customers to update item quantities.

### Bug Report
Modifying item quantity directly mutates the state array object `items[index].qty = newQty`. React fails to trigger re-renders reliably because the array reference remains identical, and cart total calculation falls out of sync.

### Steps to Reproduce
1. In `ShoppingCart.jsx`, call `updateQuantity(itemId, 5)`.
2. The code mutates the existing item in place: `items[index].qty = newQty; setItems(items);`.
3. Component doesn't re-render or produces stale totals.

### Expected Behavior
State must be updated immutably using `.map()` to return a new array with newly created item objects.

### Actual Behavior
Mutates item in place and passes identical array reference to `setItems`.

### Impact
Shoppers see incorrect order totals and get charged mismatched amounts.

### Requirements
- Use immutable state update: `setItems(items.map(item => item.id === id ? { ...item, qty: newQty } : item));`.
""",
        'files': [{
            'name': 'ShoppingCart.jsx',
            'content': '''import React, { useState } from 'react';

export default function ShoppingCart({ initialItems = [] }) {
  const [items, setItems] = useState(initialItems);

  const updateQuantity = (id, newQty) => {
    const index = items.findIndex(item => item.id === id);
    if (index !== -1) {
      items[index].qty = newQty;
      setItems(items);
    }
  };

  const total = items.reduce((sum, item) => sum + item.price * (item.qty || 1), 0);

  return (
    <div className="cart p-4">
      {items.map(item => (
        <div key={item.id} className="flex justify-between py-2 border-b">
          <span>{item.name} (${item.price})</span>
          <input
            type="number"
            value={item.qty}
            onChange={(e) => updateQuantity(item.id, parseInt(e.target.value) || 0)}
            className="w-16 border rounded p-1"
          />
        </div>
      ))}
      <div className="font-bold mt-4">Total: ${total.toFixed(2)}</div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Immutably maps items using object spread', 'input': '', 'expected': 'items.map'}
        ],
        'bug_signature': 'items[index].qty = newQty;\n      setItems(items);',
        'suspected_component': 'ShoppingCart.jsx',
        'ai_suggestions': [
            'Avoid mutating `items[index]`.',
            'Use `setItems(items.map(item => item.id === id ? { ...item, qty: newQty } : item))`.'
        ],
        'topics': ['React', 'Immutability', 'State'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Object Spread', 'React Immutability'],
        'status': 'published'
    })

    # 100. Paginated list resets unexpectedly when filters change
    challenges.append({
        'id': 100,
        'title': '[FE-M05] Paginated List Does Not Reset Page When Filter Changes',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Pagination',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An admin product catalog provides category filtering and pagination.

### Bug Report
An admin navigates to Page 6 of "All Products". They then filter by "Furniture", which only has 2 pages of results. The view displays "No products found" because the table stayed on `page = 6`, which is out of range for the filtered results!

### Steps to Reproduce
1. In `FilterPagination.jsx`, navigate to page 5.
2. Select a different category from the dropdown.
3. The catalog displays an empty state because `page` remained 5 instead of resetting to 1.

### Expected Behavior
Changing `category` must reset `page` back to 1.

### Actual Behavior
`handleFilterChange` updates category without touching `page`.

### Impact
Users believe products are missing or deleted when changing search filters.

### Requirements
- Call `setPage(1)` whenever the filter changes.
""",
        'files': [{
            'name': 'FilterPagination.jsx',
            'content': '''import React, { useState } from 'react';

export default function FilterPagination({ products = [] }) {
  const [category, setCategory] = useState('All');
  const [page, setPage] = useState(1);
  const pageSize = 5;

  const handleFilterChange = (newCategory) => {
    setCategory(newCategory);
  };

  const filtered = category === 'All' 
    ? products 
    : products.filter(p => p.category === category);

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const paginated = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="catalog p-4">
      <select 
        value={category} 
        onChange={(e) => handleFilterChange(e.target.value)}
        className="border p-2 rounded mb-4"
      >
        <option value="All">All Categories</option>
        <option value="Electronics">Electronics</option>
        <option value="Furniture">Furniture</option>
      </select>

      {paginated.length === 0 ? (
        <p>No products found</p>
      ) : (
        <ul>
          {paginated.map(p => <li key={p.id}>{p.name}</li>)}
        </ul>
      )}

      <div className="flex gap-2 mt-4">
        <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
        <span>Page {page} of {totalPages}</span>
        <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Resets page to 1 on filter change', 'input': '', 'expected': 'setPage(1)'}
        ],
        'bug_signature': 'const handleFilterChange = (newCategory) => {\n    setCategory(newCategory);\n  };',
        'suspected_component': 'FilterPagination.jsx',
        'ai_suggestions': [
            'Inside `handleFilterChange`, add `setPage(1);` alongside `setCategory(newCategory);`.'
        ],
        'topics': ['React', 'Pagination', 'Filtering'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Handling'],
        'status': 'published'
    })

    # 101. Event listener registered repeatedly and not cleaned up
    challenges.append({
        'id': 101,
        'title': '[FE-M06] Event Listener Registered Repeatedly Without Cleanup',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Memory Leaks',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A charting widget listens for browser window resize events to recalculate SVG canvas dimensions.

### Bug Report
Every time the user navigates between dashboard tabs, browser memory consumption increases steadily. Profiling reveals that thousands of `resize` listeners remain attached to `window`, leading to sluggish responsiveness.

### Steps to Reproduce
1. Inspect `ResizeListener.jsx`.
2. Notice `window.addEventListener('resize', handleResize)` is registered in `useEffect`.
3. No cleanup function is returned.

### Expected Behavior
`useEffect` must return a cleanup function: `return () => window.removeEventListener('resize', handleResize);`.

### Actual Behavior
Omits cleanup, leaking event listeners on every unmount and re-mount.

### Impact
Severe memory leak causing browser tab crashes on long-lived sessions.

### Requirements
- Return `() => window.removeEventListener('resize', handleResize)` from `useEffect`.
""",
        'files': [{
            'name': 'ResizeListener.jsx',
            'content': '''import React, { useState, useEffect } from 'react';

export default function ResizeListener() {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
  }, []);

  return (
    <div className="p-4">
      <p className="font-semibold">Current width: {windowWidth}px</p>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Cleans up event listener with removeEventListener', 'input': '', 'expected': 'removeEventListener'}
        ],
        'bug_signature': 'window.addEventListener(\'resize\', handleResize);\n    // BUG: Missing cleanup function to removeEventListener\n  }, []);',
        'suspected_component': 'ResizeListener.jsx',
        'ai_suggestions': [
            'Return a cleanup callback from `useEffect`: `return () => window.removeEventListener("resize", handleResize);`.'
        ],
        'topics': ['React', 'useEffect', 'Cleanup', 'DOM Events'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['DOM Event Listeners', 'React Hooks'],
        'status': 'published'
    })

    # 102. Authentication refresh request creates redirect loops
    challenges.append({
        'id': 102,
        'title': '[FE-M07] Authentication Refresh Request Creates Redirect Loops',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Authentication',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A cloud dashboard implements route guarding to protect user settings and billing.

### Bug Report
When an authenticated user refreshes `/settings`, the page flickers and immediately redirects to `/login`. Upon arriving at `/login`, the auth provider finishes hydrating and redirects them back to `/settings`, causing an infinite redirect loop.

### Steps to Reproduce
1. In `ProtectedRoute.jsx`, observe the auth check.
2. When the app first boots, `isLoading` is `true` while the session token is validated, but `user` is initially `null`.
3. `ProtectedRoute` immediately executes `if (!user) return <Navigate to="/login" />` before checking `isLoading`.

### Expected Behavior
If `isLoading` is true, render a loading spinner `<LoadingSpinner />` and wait until authentication state resolves before redirecting.

### Actual Behavior
Treats unhydrated state (`user === null` while `isLoading === true`) as unauthenticated and redirects immediately.

### Impact
Authenticated users cannot reload or deep-link to protected pages without getting kicked out.

### Requirements
- Add `if (isLoading) return <LoadingSpinner />;` before checking `if (!user)`.
""",
        'files': [{
            'name': 'ProtectedRoute.jsx',
            'content': '''import React from 'react';

function LoadingSpinner() {
  return <div className="spinner p-4">Loading session...</div>;
}

function Navigate({ to }) {
  return <div>Redirecting to {to}...</div>;
}

export default function ProtectedRoute({ user, isLoading, children }) {
  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Checks isLoading before redirecting', 'input': '', 'expected': 'isLoading'}
        ],
        'bug_signature': 'export default function ProtectedRoute({ user, isLoading, children }) {\n  if (!user) {',
        'suspected_component': 'ProtectedRoute.jsx',
        'ai_suggestions': [
            'Add `if (isLoading) return <LoadingSpinner />;` at the beginning of `ProtectedRoute` before `if (!user)`.'
        ],
        'topics': ['React', 'Authentication', 'Routing', 'Loading States'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Routing and Auth Flow'],
        'status': 'published'
    })

    # 103. File-upload component mishandles progress and failed requests
    challenges.append({
        'id': 103,
        'title': '[FE-M08] File-Upload Component Mishandles Progress and Failed Requests',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Error Handling',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A customer portal allows users to upload PDF receipts for reimbursement.

### Bug Report
If an upload fails (e.g. 500 server error or dropped connection), the UI remains stuck showing "Uploading 65%..." and the upload button stays disabled forever. The user is unable to retry without refreshing the entire page.

### Steps to Reproduce
1. In `FileUploader.jsx`, simulate an upload failure.
2. The `try/catch` catches the error, but only calls `console.error`.
3. `isUploading` remains `true` and `error` state is never populated.

### Expected Behavior
Inside the `catch` block, set `setIsUploading(false)` and `setError(err.message || 'Upload failed')`.

### Actual Behavior
Leaves `isUploading: true` and does not set user-facing error message.

### Impact
Users assume their documents are still uploading and abandon their expense submissions.

### Requirements
- Update `catch` block to set `setIsUploading(false)` and set `setError(...)`.
""",
        'files': [{
            'name': 'FileUploader.jsx',
            'content': '''import React, { useState } from 'react';

export default function FileUploader({ uploadApi }) {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    setProgress(20);

    try {
      await uploadApi(file, (p) => setProgress(p));
      setIsUploading(false);
      setProgress(100);
    } catch (err) {
      console.error('Upload failed', err);
    }
  };

  return (
    <div className="uploader p-4 border rounded">
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {isUploading ? (
        <p>Uploading... {progress}%</p>
      ) : (
        <button 
          onClick={() => handleUpload({ name: 'receipt.pdf' })}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Upload Document
        </button>
      )}
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Resets isUploading and sets error state on failure', 'input': '', 'expected': 'setIsUploading(false)'}
        ],
        'bug_signature': '} catch (err) {\n      console.error(\'Upload failed\', err);\n    }',
        'suspected_component': 'FileUploader.jsx',
        'ai_suggestions': [
            'In the `catch` block, call `setIsUploading(false);` and `setError(err.message || "Upload failed");`.'
        ],
        'topics': ['React', 'Async', 'Error Handling'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Promises', 'Async/Await'],
        'status': 'published'
    })

    # 104. Multi-step form loses user-entered values when navigating backward
    challenges.append({
        'id': 104,
        'title': '[FE-M09] Multi-Step Form Loses User Values When Navigating Backward',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Form Architecture',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An insurance quote onboarding flow consists of Step 1 (Personal Info) and Step 2 (Vehicle Details).

### Bug Report
A user fills out Step 1, proceeds to Step 2, and then clicks "Back" to fix a typo in their name. When Step 1 re-mounts, all previously entered fields are blank!

### Steps to Reproduce
1. In `WizardForm.jsx`, notice that `Step1` maintains local `useState` for `fullName` and `email` instead of lifting state to parent.
2. Moving to Step 2 unmounts `Step1`, destroying its local state.
3. Returning to Step 1 re-mounts with empty initial strings.

### Expected Behavior
Form data must be lifted up to parent `WizardForm` and passed down as props (`formData` and `onChange`) to persist between step transitions.

### Actual Behavior
Child step component owns its own state, discarding it upon unmount.

### Impact
High checkout abandonment rates due to users having to re-type form inputs.

### Requirements
- Lift state to `WizardForm` and pass `formData.fullName` and `formData.email` into `Step1`.
""",
        'files': [{
            'name': 'WizardForm.jsx',
            'content': '''import React, { useState } from 'react';

export function Step1({ formData = {}, onChange }) {
  const [name, setName] = useState('');

  return (
    <div>
      <input
        type="text"
        value={name}
        onChange={(e) => {
          setName(e.target.value);
          onChange({ name: e.target.value });
        }}
        placeholder="Full Name"
        className="border p-2"
      />
    </div>
  );
}

export default function WizardForm() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ name: '' });

  return (
    <div className="p-4">
      {step === 1 && (
        <Step1 formData={formData} onChange={(d) => setFormData(prev => ({ ...prev, ...d }))} />
      )}
      {step === 2 && (
        <div>Step 2: Confirmation for {formData.name}</div>
      )}
      <div className="mt-4 flex gap-2">
        <button onClick={() => setStep(s => Math.max(1, s - 1))}>Back</button>
        <button onClick={() => setStep(s => s + 1)}>Next</button>
      </div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Step1 initializes with formData.name', 'input': '', 'expected': 'formData.name'}
        ],
        'bug_signature': 'export function Step1({ formData = {}, onChange }) {\n  const [name, setName] = useState(\'\');',
        'suspected_component': 'WizardForm.jsx',
        'ai_suggestions': [
            'Initialize `Step1` name state from `formData.name || ""` or use controlled inputs directly from `formData`.'
        ],
        'topics': ['React', 'Lifting State', 'Forms', 'Multi-step'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Lifting'],
        'status': 'published'
    })

    # 105. Dashboard renders inconsistent data after parallel API calls
    challenges.append({
        'id': 105,
        'title': '[FE-M10] Dashboard Renders Inconsistent Data After Parallel API Calls',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Asynchronous Data',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An executive analytics dashboard fetches Revenue Metrics and Server Health in parallel.

### Bug Report
If the Server Health endpoint encounters a minor 503 outage, `Promise.all` fails immediately, causing the entire dashboard to crash and display an error screen—even though the critical Revenue Metrics were returned successfully!

### Steps to Reproduce
1. In `MetricsDashboard.jsx`, observe `Promise.all([fetchRevenue(), fetchHealth()])`.
2. Rejecting `fetchHealth()` causes the entire try block to fail.
3. No revenue numbers are shown to the executive.

### Expected Behavior
Use `Promise.allSettled` or individual try/catch blocks so successful metrics are displayed with an isolated fallback banner for the degraded service.

### Actual Behavior
All-or-nothing `Promise.all` fails completely on single endpoint errors.

### Impact
Total service interruption on dashboard when non-critical endpoints fail.

### Requirements
- Use `Promise.allSettled` to independently evaluate each endpoint result.
""",
        'files': [{
            'name': 'MetricsDashboard.jsx',
            'content': '''import React, { useState, useEffect } from 'react';

export default function MetricsDashboard({ fetchRevenue, fetchHealth }) {
  const [revenue, setRevenue] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchRevenue(), fetchHealth()])
      .then(([revData, healthData]) => {
        setRevenue(revData);
        setHealth(healthData);
      })
      .catch((err) => {
        setError('Failed to load dashboard metrics');
      });
  }, [fetchRevenue, fetchHealth]);

  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="p-4 grid grid-cols-2 gap-4">
      <div className="card border p-4">
        <h3>Revenue: {revenue ? `$${revenue.total}` : 'Loading...'}</h3>
      </div>
      <div className="card border p-4">
        <h3>System Health: {health ? health.status : 'Unavailable'}</h3>
      </div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Uses Promise.allSettled for resilient data fetching', 'input': '', 'expected': 'Promise.allSettled'}
        ],
        'bug_signature': 'Promise.all([fetchRevenue(), fetchHealth()])',
        'suspected_component': 'MetricsDashboard.jsx',
        'ai_suggestions': [
            'Handle partial API failures gracefully by allowing independent endpoints to settle without aborting sibling data.'
        ],
        'topics': ['React', 'Async', 'Promise.allSettled', 'Resilience'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Promises'],
        'status': 'published'
    })

    # 106. Frontend cache displays outdated profile information
    challenges.append({
        'id': 106,
        'title': '[FE-M11] Frontend Cache Displays Outdated Profile Information',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Caching',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A social networking platform caches user profile payloads in an in-memory map to reduce redundant API roundtrips.

### Bug Report
When a user updates their profile name and clicks "Save", the update API returns 200 OK. However, navigating back to their profile view still displays their old name until the page is hard refreshed.

### Steps to Reproduce
1. In `ProfileCache.jsx`, save an updated name via `handleUpdateName`.
2. Notice the code calls `api.updateName(newName)`, but never invalidates or updates the `cache` entry for `userId`.
3. Subsequent reads from `cache.get(userId)` return the old profile object.

### Expected Behavior
After a successful update, the cache entry must be invalidated or updated with the new profile data.

### Actual Behavior
The cache is not mutated or cleared, leading to stale reads.

### Impact
Users repeatedly submit duplicate update requests thinking their changes were lost.

### Requirements
- Update `cache.set(userId, updated)` or delete `cache.delete(userId)` after saving.
""",
        'files': [{
            'name': 'ProfileCache.jsx',
            'content': '''import React, { useState } from 'react';

export default function ProfileCache({ userId, api, cache }) {
  const [profile, setProfile] = useState(() => cache.get(userId) || { name: 'Anonymous' });
  const [nameInput, setNameInput] = useState('');

  const handleUpdateName = async () => {
    const updated = await api.updateName(userId, nameInput);
    setProfile(updated);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl">User: {profile.name}</h2>
      <input
        type="text"
        value={nameInput}
        onChange={(e) => setNameInput(e.target.value)}
        placeholder="New name"
        className="border p-1 mr-2"
      />
      <button onClick={handleUpdateName} className="bg-blue-500 text-white px-3 py-1 rounded">
        Save
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Updates or deletes the cache entry on save', 'input': '', 'expected': 'cache.set(userId'}
        ],
        'bug_signature': '',
        'suspected_component': 'ProfileCache.jsx',
        'ai_suggestions': [
            'Add `cache.set(userId, updated);` after updating the profile state.'
        ],
        'topics': ['React', 'Caching', 'Cache Invalidation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Client-side Caching'],
        'status': 'published'
    })

    # 107. Component submits duplicate requests after repeated clicks
    challenges.append({
        'id': 107,
        'title': '[FE-M12] Component Submits Duplicate Requests After Repeated Clicks',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Form Submission',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A food delivery app features an "Order Now" checkout button.

### Bug Report
Impatient users double-click the "Place Order" button. The server receives two parallel order requests and charges the customer twice for the same meal!

### Steps to Reproduce
1. In `SubmitButton.jsx`, observe the `handleSubmit` click handler.
2. The button lacks a `disabled` attribute tied to `isSubmitting`, and `handleSubmit` does not check if a submission is already pending.

### Expected Behavior
The button must be disabled when `isSubmitting` is true (`disabled={isSubmitting}`), and `handleSubmit` must guard against re-entry.

### Actual Behavior
Button stays clickable during the async network request.

### Impact
Duplicate financial transactions and customer chargeback disputes.

### Requirements
- Set `disabled={isSubmitting}` on `<button>`.
- Check `if (isSubmitting) return;` at the start of `handleSubmit`.
""",
        'files': [{
            'name': 'SubmitButton.jsx',
            'content': '''import React, { useState } from 'react';

export default function SubmitButton({ onOrder }) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await onOrder();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
<button 
        onClick={handleSubmit}
        className="bg-green-600 text-white px-4 py-2 rounded"
      >
        {isSubmitting ? 'Processing...' : 'Place Order'}
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Disables button when isSubmitting is true', 'input': '', 'expected': 'disabled={isSubmitting}'}
        ],
        'bug_signature': '',
        'suspected_component': 'SubmitButton.jsx',
        'ai_suggestions': [
            'Inspect button attributes during pending states: prevent double submissions by disabling the action element.',
            'Add `if (isSubmitting) return;` at the start of `handleSubmit`.'
        ],
        'topics': ['React', 'Forms', 'Debounce', 'Double Submission'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Event Handling'],
        'status': 'published'
    })

    # 108. Date picker displays incorrect date due to timezone conversion
    challenges.append({
        'id': 108,
        'title': '[FE-M13] Date Picker Displays Incorrect Date Due to Timezone Offset',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Date & Time',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A hotel booking system displays selected check-in and check-out dates.

### Bug Report
Users in the Americas (e.g. UTC-5, UTC-8) select "October 15, 2026" on the calendar. After selecting, the confirmation text shows "October 14, 2026"—one day behind!

### Steps to Reproduce
1. In `DatePicker.jsx`, `new Date("2026-10-15")` parses the string at midnight UTC.
2. In America/New_York (UTC-4), midnight UTC corresponds to 8:00 PM on October 14.
3. Calling `date.getDate()` or `toISOString()` renders October 14 instead of October 15.

### Expected Behavior
Format dates using local components or parse without midnight UTC shifting (e.g. `dateString.split('-')` or `new Date(year, month - 1, day)`).

### Actual Behavior
Converts through `new Date(isoDateString).toISOString().split('T')[0]`, shifting timezone by negative UTC offset.

### Impact
Guests book rooms for the wrong night, causing booking errors and lost revenue.

### Requirements
- Parse date inputs using local calendar date parts to avoid unexpected timezone shifts.
""",
        'files': [{
            'name': 'DatePicker.jsx',
            'content': '''import React, { useState } from 'react';

export default function DatePicker({ onSelect }) {
  const [selectedDate, setSelectedDate] = useState('');

  const handleDateChange = (dateString) => {
    const d = new Date(dateString);
    const formatted = d.toISOString().split('T')[0];
    setSelectedDate(formatted);
    onSelect(formatted);
  };

  return (
    <div className="p-4">
      <input
        type="date"
        onChange={(e) => handleDateChange(e.target.value)}
        className="border p-2 rounded"
      />
      {selectedDate && <p className="mt-2">Selected: {selectedDate}</p>}
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Retains raw dateString without UTC shifting', 'input': '', 'expected': 'setSelectedDate(dateString)'}
        ],
        'bug_signature': 'const d = new Date(dateString);\n    const formatted = d.toISOString().split(\'T\')[0];\n    setSelectedDate(formatted);',
        'suspected_component': 'DatePicker.jsx',
        'ai_suggestions': [
            'Directly use `setSelectedDate(dateString); onSelect(dateString);` since `<input type="date">` already provides `YYYY-MM-DD`.'
        ],
        'topics': ['React', 'Dates', 'Timezones'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Date Handling'],
        'status': 'published'
    })

    # 109. Form does not preserve server validation errors
    challenges.append({
        'id': 109,
        'title': '[FE-M14] Form Does Not Preserve Field-Level Server Validation Errors',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Form Validation',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
A SaaS account creation form validates workspace subdomain and company tax ID on the backend.

### Bug Report
When submitting with a taken subdomain, the backend returns HTTP 422: `{ errors: { subdomain: "Subdomain already in use" } }`. The frontend replaces the entire form with a generic message `"An error occurred"` rather than highlighting the `subdomain` field with its specific server error message.

### Steps to Reproduce
1. In `ServerErrorForm.jsx`, simulate a 422 response with `err.response.data.errors`.
2. Notice `catch (err)` discards `err.response.data.errors` and sets a single string error.
3. No field-specific error messages are rendered next to the offending input.

### Expected Behavior
Catch block must inspect `err.response?.data?.errors` and store them in `fieldErrors` state (`setFieldErrors(err.response.data.errors)`).

### Actual Behavior
Wipes out detailed field-level error messages in favor of a vague banner.

### Impact
Users cannot tell which field was invalid or how to fix it, abandoning signup.

### Requirements
- Set `setFieldErrors(err.response?.data?.errors || {})` inside the catch handler.
""",
        'files': [{
            'name': 'ServerErrorForm.jsx',
            'content': '''import React, { useState } from 'react';

export default function ServerErrorForm({ onSubmit }) {
  const [subdomain, setSubdomain] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError('');
    setFieldErrors({});

    try {
      await onSubmit({ subdomain });
    } catch (err) {
      setGeneralError('Submission failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-2">
      {generalError && <p className="text-red-600">{generalError}</p>}
      <div>
        <label>Subdomain:</label>
        <input
          type="text"
          value={subdomain}
          onChange={(e) => setSubdomain(e.target.value)}
          className="border p-1 block w-full"
        />
        {fieldErrors.subdomain && (
          <span className="text-red-500 text-sm">{fieldErrors.subdomain}</span>
        )}
      </div>
      <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
        Submit
      </button>
    </form>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Populates fieldErrors from server error response', 'input': '', 'expected': 'setFieldErrors(err.response'}
        ],
        'bug_signature': '} catch (err) {\n      setGeneralError(\'Submission failed\');\n    }',
        'suspected_component': 'ServerErrorForm.jsx',
        'ai_suggestions': [
            'In the `catch` block, add `if (err.response?.data?.errors) setFieldErrors(err.response.data.errors);`.'
        ],
        'topics': ['React', 'Forms', 'Validation', 'Error Handling'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['HTTP Status Codes', 'React Form State'],
        'status': 'published'
    })

    # 110. Accessible dropdown fails to manage keyboard navigation correctly
    challenges.append({
        'id': 110,
        'title': '[FE-M15] Accessible Dropdown Fails to Close on Escape Key',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Accessibility',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Company Scenario
An enterprise banking application requires compliance with WCAG 2.1 AA accessibility guidelines.

### Bug Report
When a blind or motor-impaired user opens a custom dropdown menu using keyboard navigation, pressing the "Escape" key does not close the dropdown menu, trapping focus and violating accessibility standards.

### Steps to Reproduce
1. In `AccessibleDropdown.jsx`, open the dropdown.
2. Press the Escape key.
3. The dropdown remains open because `handleKeyDown` ignores `e.key === 'Escape'`.

### Expected Behavior
When `e.key === 'Escape'` is pressed, `setIsOpen(false)` must be called to dismiss the dropdown.

### Actual Behavior
`handleKeyDown` ignores the Escape key.

### Impact
Fails WCAG 2.1 AA audit, blocking users who rely on assistive technologies.

### Requirements
- Add `if (e.key === 'Escape') setIsOpen(false);` in `handleKeyDown`.
""",
        'files': [{
            'name': 'AccessibleDropdown.jsx',
            'content': '''import React, { useState } from 'react';

export default function AccessibleDropdown({ options = [], onSelect }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      setIsOpen(prev => !prev);
    }
  };

  return (
    <div className="relative inline-block" onKeyDown={handleKeyDown}>
      <button
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        className="border px-4 py-2 rounded"
      >
        {selected ? selected.label : 'Select an option'}
      </button>

      {isOpen && (
        <ul role="listbox" className="absolute border bg-white mt-1 w-full shadow-lg">
          {options.map((opt) => (
            <li
              key={opt.value}
              role="option"
              onClick={() => {
                setSelected(opt);
                setIsOpen(false);
                onSelect(opt);
              }}
              className="p-2 hover:bg-slate-100 cursor-pointer"
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Closes dropdown when Escape key is pressed', 'input': '', 'expected': "e.key === 'Escape'"}
        ],
        'bug_signature': 'const handleKeyDown = (e) => {\n    if (e.key === \'Enter\' || e.key === \' \') {',
        'suspected_component': 'AccessibleDropdown.jsx',
        'ai_suggestions': [
            'Add `if (e.key === "Escape") { setIsOpen(false); }` inside `handleKeyDown`.'
        ],
        'topics': ['React', 'Accessibility', 'WCAG', 'Keyboard Events'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Web Accessibility Basics'],
        'status': 'published'
    })

    return challenges
