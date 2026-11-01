"""
Frontend Studio: Medium Challenges (96 to 110)
Standardized into realistic production incident debugging tickets.
"""

def get_frontend_medium():
    challenges = []

    # 96. Rapid search requests overwrite newer results
    challenges.append({
        'id': 96,
        'title': 'Documentation Typeahead Discards Newest Query Results on Latency Spikes',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Asynchronous UI',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Developers searching the enterprise documentation portal reported that live typeahead search was frequently displaying completely wrong search results. For example, after typing `"users"` quickly, the results list showed matches for `"us"` while the input field clearly showed `"users"`. The discrepancy caused developers to navigate into incorrect documentation sections.

### Bug Report
In `LiveSearch.jsx`, an asynchronous race condition occurs when subsequent keystrokes dispatch concurrent network requests. If an earlier request (e.g., for `"us"`) takes longer to resolve than a later request (e.g., for `"users"`), the older slow response resolves last and overwrites the newer search results unconditionally.

### Steps to Reproduce
1. Render `LiveSearch.jsx` with a mock search function that simulates variable network latency.
2. Type a multi-character search term quickly into the search input.
3. Observe that when the slower preliminary request resolves after the latest request, the preliminary results overwrite the current results list.

### Expected Behaviour
The search effect must track active request status or use an abort mechanism so that responses from outdated or superseded queries are ignored.

### Actual Behaviour
Every resolved promise unconditionally invokes `setResults(data)` regardless of whether the query that initiated it is still the latest user input.

### Starter Files
- `LiveSearch.jsx`: Search typeahead component vulnerable to asynchronous race conditions.

### Task
Refactor `LiveSearch.jsx` to prevent race conditions from out-of-order asynchronous responses overwriting newer search results.

### Acceptance Criteria
1. Fast-typing queries discard stale responses from previously initiated slower requests.
2. Only the results for the most recent search query are displayed.
3. In-flight requests are properly ignored when new queries are submitted.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Uses cancellation flag or AbortController to prevent race conditions', 'input': '', 'expected': 'active'}
        ],
        'bug_signature': 'fetchResults(query).then(data => {\n      setResults(data);',
        'suspected_component': 'LiveSearch.jsx',
        'ai_suggestions': [
            'Asynchronous network requests initiated inside `useEffect` must be guarded against out-of-order resolution race conditions.',
            'Maintain a boolean flag (such as `let active = true;`) scoped inside the effect that gets flipped to `false` in the effect cleanup return function.',
            'Verify `if (active)` before calling `setResults(data)`, and return `() => { active = false; };` from the effect.'
        ],
        'topics': ['React', 'Async', 'Race Conditions', 'useEffect'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Hooks', 'Asynchronous JavaScript'],
        'status': 'published'
    })

    # 97. React state updates lose changes during batched operations
    challenges.append({
        'id': 97,
        'title': 'Warehouse Quick-Add Action Discards Batched Inventory Increments',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'State Management',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Warehouse floor operators packing outgoing shipments noticed that clicking the "+3 Quick Add" shortcut button on inventory terminals only increased the item box count by 1 instead of 3. Operators were forced to repeatedly click the button, resulting in incorrect box counts and packaging delays.

### Bug Report
In `CounterBatch.jsx`, the `incrementByThree` handler calls `setCount(count + 1)` three times sequentially. Because each call closes over the same render's snapshot value of `count`, React batches all three updates and evaluates `setCount(0 + 1)` three times, resulting in a net increase of only 1.

### Steps to Reproduce
1. Render `CounterBatch.jsx` with an initial count of 0.
2. Click the "+3 Quick Add" button.
3. Observe that the displayed box count increments to 1 instead of 3.

### Expected Behaviour
Each sequential update in a batch must receive and operate on the previous queued state value, properly incrementing the count by 3.

### Actual Behaviour
All three state updates read the stale closure variable `count`, overwriting one another.

### Starter Files
- `CounterBatch.jsx`: Counter component using repeated direct state updates.

### Task
Refactor `incrementByThree` in `CounterBatch.jsx` so that consecutive queued state updates build upon the most recent state value.

### Acceptance Criteria
1. State updates use updater functions to avoid reading stale closure state.
2. Triggering the batch increment increases the counter by exactly 3.
3. The displayed count accurately reflects all queued modifications.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.
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
            {'id': 1, 'name': 'Uses functional state updater prev => prev + 1', 'input': '', 'expected': 'prev =>'}
        ],
        'bug_signature': 'setCount(count + 1);\n    setCount(count + 1);\n    setCount(count + 1);',
        'suspected_component': 'CounterBatch.jsx',
        'ai_suggestions': [
            'Multiple consecutive state updates within the same event execution read from the same render closure unless updater functions are used.',
            'React queues updater functions and passes the pending state as the first argument to each subsequent updater.',
            'Replace `setCount(count + 1)` with `setCount(prev => prev + 1)` across all three calls.'
        ],
        'topics': ['React', 'State', 'Batching'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Management'],
        'status': 'published'
    })

    # 98. useEffect dependency causes stale values or repeated requests
    challenges.append({
        'id': 98,
        'title': 'Customer Support Drawer Retains Prior User Profile Across Ticket Switches',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'React Hooks',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Customer support agents reported an urgent security and privacy issue: while triaging support tickets, clicking from Customer A's ticket to Customer B's ticket left Customer A's contact info, email address, and billing details displayed in the profile sidebar drawer. An agent inadvertently emailed Customer A regarding Customer B's ticket.

### Bug Report
In `UserProfileLoader.jsx`, the `useEffect` hook that fetches profile information specifies an empty dependency array `[]`. Because `userId` is omitted from dependencies, the effect runs only once when mounted and never refetches when the parent component passes a new `userId` prop.

### Steps to Reproduce
1. Render `UserProfileLoader.jsx` with `userId = "usr_101"`. Profile loads.
2. Change the incoming prop to `userId = "usr_202"`.
3. Observe that no network request is dispatched and the component continues to display data for `usr_101`.

### Expected Behaviour
The component must fetch and display the updated profile whenever the `userId` prop changes.

### Actual Behaviour
The effect ignores prop changes due to an empty dependency array, closing over stale profile data.

### Starter Files
- `UserProfileLoader.jsx`: Profile loader component with omitted hook dependencies.

### Task
Update `UserProfileLoader.jsx` so that changing the active user prop re-fetches and displays the selected user's profile.

### Acceptance Criteria
1. The dependency array includes `userId`.
2. Changing `userId` re-triggers loading and retrieves the correct profile.
3. Component cleanup remains intact to prevent state updates on unmounted instances.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Declares userId in dependency array', 'input': '', 'expected': '[userId'}
        ],
        'bug_signature': '}, []);',
        'suspected_component': 'UserProfileLoader.jsx',
        'ai_suggestions': [
            'All props and variables referenced inside a `useEffect` must be specified in its dependency array.',
            'Look at the empty dependency array `[]` at the bottom of the effect: it prevents the effect from executing when props change.',
            'Change the dependency array from `[]` to `[userId, fetchUser]` or `[userId]`.'
        ],
        'topics': ['React', 'Hooks', 'useEffect', 'Dependencies'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Hooks Rules'],
        'status': 'published'
    })

    # 99. Shopping cart calculates totals incorrectly after quantity updates
    challenges.append({
        'id': 99,
        'title': 'Checkout Cart Subtotal Freezes on In-Place Item Mutation',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'State Immutability',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Online shoppers complained that altering product quantities in the grocery checkout cart left the overall subtotal stuck on the initial balance. Only after navigating back and forth between different checkout steps did the price refresh, leading shoppers to believe discounts or items were missing.

### Bug Report
In `ShoppingCart.jsx`, `updateQuantity` mutates the existing state array in place via `items[index].qty = newQty` and then calls `setItems(items)`. Because the array reference has not changed, React's shallow comparison treats the state as unchanged, failing to trigger a re-render.

### Steps to Reproduce
1. Render `ShoppingCart.jsx` with sample line items.
2. Modify the quantity of an item using the number input.
3. Observe that the subtotal does not recalculate immediately because React skipped re-rendering the mutated array.

### Expected Behaviour
Updating an item's quantity must produce a new array containing a new item object, preserving state immutability and triggering immediate re-render.

### Actual Behaviour
The handler directly mutates `items[index].qty` and passes the existing reference back to `setItems`.

### Starter Files
- `ShoppingCart.jsx`: Cart component with direct in-place state mutation.

### Task
Refactor `updateQuantity` in `ShoppingCart.jsx` to treat state immutably when modifying item quantities.

### Acceptance Criteria
1. The update creates a new array reference without modifying the previous array.
2. The modified item is cloned with the updated `qty`.
3. The cart subtotal updates immediately upon quantity changes.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.
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
            {'id': 1, 'name': 'Immutably maps items using object spread', 'input': '', 'expected': 'items.map'}
        ],
        'bug_signature': 'items[index].qty = newQty;\n      setItems(items);',
        'suspected_component': 'ShoppingCart.jsx',
        'ai_suggestions': [
            'Direct mutation of React state structures prevents re-renders because React relies on reference equality.',
            'Do not assign properties directly onto objects inside state arrays like `items[index].qty = ...`.',
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
        'title': 'Catalog Pagination Leaves Filtered Views Trapped on Nonexistent Page',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Pagination',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Store managers managing product inventory reported that category filters were returning "No products found" even for categories with dozens of items. Investigation showed that if a manager was on page 5 of "All Categories" and then clicked "Furniture" (which only has 1 page of items), the view remained stuck on page 5, which had zero items.

### Bug Report
In `FilterPagination.jsx`, `handleFilterChange` updates `category` via `setCategory(newCategory)`. However, it neglects to reset `page` back to `1`. If the filtered category has fewer total pages than the current page index, the user is stranded on an out-of-range empty page.

### Steps to Reproduce
1. Navigate to page 3 or higher under "All Categories".
2. Select a category with few items (e.g. "Furniture").
3. Notice that the catalog displays "No products found" because `page` is still set to 3.

### Expected Behaviour
Whenever the user changes the filter category, `page` must reset to `1`.

### Actual Behaviour
The page index persists across filter changes, causing out-of-bounds pagination errors.

### Starter Files
- `FilterPagination.jsx`: Filterable paginated catalog component without page reset logic.

### Task
Update `handleFilterChange` in `FilterPagination.jsx` to call `setPage(1)` whenever `newCategory` is selected.

### Acceptance Criteria
1. Changing the category filter sets `page` to 1.
2. Filtered results render starting from the first page.
3. Pagination controls recalculate total pages accurately.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Resets page to 1 on filter change', 'input': '', 'expected': 'setPage(1)'}
        ],
        'bug_signature': 'const handleFilterChange = (newCategory) => {\n    setCategory(newCategory);\n  };',
        'suspected_component': 'FilterPagination.jsx',
        'ai_suggestions': [
            'When changing dataset filters, the current page number must be reset to prevent pointing past the end of the new result set.',
            'Examine `handleFilterChange`: it only updates the category state.',
            'Add `setPage(1);` inside `handleFilterChange` right after `setCategory(newCategory);`.'
        ],
        'topics': ['React', 'Pagination', 'Filtering'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Handling'],
        'status': 'published'
    })

    # 101. Event listener registered repeatedly and not cleaned up
    challenges.append({
        'id': 101,
        'title': 'SVG Dashboard Widget Accumulates Leaked Window Resize Listeners',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Memory Leaks',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Performance monitoring flagged client memory leaks in the operational analytics dashboard. Users who left the browser tab open throughout their work shift experienced severe browser tab lag and eventual tab crashes. Profiling showed tens of thousands of duplicate `resize` listeners accumulated on `window`.

### Bug Report
In `ResizeListener.jsx`, `window.addEventListener('resize', handleResize)` is registered in `useEffect`. However, the effect omits a cleanup function. Every time the component mounts or unmounts, a new listener is permanently attached to `window`.

### Steps to Reproduce
1. Mount and unmount `ResizeListener.jsx` repeatedly across tab switches.
2. Inspect the `window` event listeners using Chrome DevTools.
3. Observe that resize event listeners continuously accumulate without being removed.

### Expected Behaviour
The effect must return a cleanup callback that invokes `window.removeEventListener('resize', handleResize)` to detach the listener on unmount.

### Actual Behaviour
The effect has no cleanup return statement, causing memory leaks.

### Starter Files
- `ResizeListener.jsx`: Dimension tracking component omitting event listener cleanup.

### Task
Update `ResizeListener.jsx` to detach its window resize event listener when the component unmounts.

### Acceptance Criteria
1. A cleanup function removes the window resize listener when unmounting.
2. Event listener references match between registration and deregistration.
3. Memory leaks from lingering event listeners are eliminated.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.
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
            {'id': 1, 'name': 'Cleans up event listener with removeEventListener', 'input': '', 'expected': 'removeEventListener'}
        ],
        'bug_signature': 'window.addEventListener(\'resize\', handleResize);\n  }, []);',
        'suspected_component': 'ResizeListener.jsx',
        'ai_suggestions': [
            'Global event listeners attached to `window` or `document` inside effects must be cleaned up to avoid memory leaks.',
            'React `useEffect` supports returning a cleanup callback function that executes when the component unmounts.',
            'Return `() => window.removeEventListener("resize", handleResize);` from the effect function.'
        ],
        'topics': ['React', 'useEffect', 'Cleanup', 'DOM Events'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['DOM Event Listeners', 'React Hooks'],
        'status': 'published'
    })

    # 102. Authentication refresh request creates redirect loops
    challenges.append({
        'id': 102,
        'title': 'Settings Route Guard Triggers Infinite Login Redirect on Cold Refresh',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Authentication',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Logged-in users reloading their account settings page (`/settings`) reported being abruptly redirected to `/login`. Upon reaching `/login`, the session hydration completed and immediately redirected them back to `/settings`, triggering an infinite redirect loop that made the application unusable.

### Bug Report
In `ProtectedRoute.jsx`, the guard immediately evaluates `if (!user) return <Navigate to="/login" />`. On application launch or page reload, `user` is initially `null` while `isLoading` is `true`. The guard fails to verify `isLoading` first, mistakenly kicking valid sessions out before auth initialization completes.

### Steps to Reproduce
1. Render `ProtectedRoute.jsx` with `user = null` and `isLoading = true`.
2. Observe that the component renders `<Navigate to="/login" />` instead of waiting for loading to finish.
3. The premature redirection creates an authentication loop.

### Expected Behaviour
If `isLoading` is true, the route guard must display a loading spinner `<LoadingSpinner />` and defer redirect decisions until auth state resolves.

### Actual Behaviour
The guard assumes uninitialized auth state represents an unauthenticated visitor.

### Starter Files
- `ProtectedRoute.jsx`: Authentication wrapper component lacking initial loading check.

### Task
Update `ProtectedRoute.jsx` to check `if (isLoading) return <LoadingSpinner />;` before checking `if (!user)`.

### Acceptance Criteria
1. The component checks `isLoading` before checking `user`.
2. When `isLoading` is true, `<LoadingSpinner />` is returned.
3. Unauthenticated requests (`!user && !isLoading`) redirect to `/login`.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Checks isLoading before redirecting', 'input': '', 'expected': 'isLoading'}
        ],
        'bug_signature': 'export default function ProtectedRoute({ user, isLoading, children }) {\n  if (!user) {',
        'suspected_component': 'ProtectedRoute.jsx',
        'ai_suggestions': [
            'Asynchronous authentication systems take time to hydrate session tokens from storage or backend endpoints.',
            'A protected route should never redirect until session verification is finished.',
            'Add `if (isLoading) return <LoadingSpinner />;` prior to the `if (!user)` check.'
        ],
        'topics': ['React', 'Authentication', 'Routing', 'Loading States'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Routing and Auth Flow'],
        'status': 'published'
    })

    # 103. File-upload component mishandles progress and failed requests
    challenges.append({
        'id': 103,
        'title': 'Reimbursement Receipt Uploader Locks Up on Network Disruption',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Error Handling',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Employees filing travel expense reports reported that when an upload failed due to a spotty Wi-Fi connection, the file uploader widget stayed permanently frozen showing `"Uploading... 20%"`. The submit button remained disabled, and no error message appeared, preventing employees from retrying without reloading the entire page.

### Bug Report
In `FileUploader.jsx`, the `handleUpload` asynchronous function handles errors with `catch (err) { console.error('Upload failed', err); }`. It forgets to reset `setIsUploading(false)` or populate `setError(err.message || 'Upload failed')`. As a result, the component remains permanently locked in uploading mode.

### Steps to Reproduce
1. Render `FileUploader.jsx` with a mock `uploadApi` that throws an error.
2. Click the "Upload Document" button.
3. Observe that after the error occurs, the UI remains permanently stuck on "Uploading... 20%" with no error banner.

### Expected Behaviour
When an upload error occurs, `isUploading` must be reset to `false` and `error` must be set so the user is informed and can retry.

### Actual Behaviour
The `catch` block logs to console without clearing loading state or updating user-facing error state.

### Starter Files
- `FileUploader.jsx`: File upload component with incomplete error state handling.

### Task
Update the `catch` block in `FileUploader.jsx` to call `setIsUploading(false)` and set `setError(err.message || 'Upload failed')`.

### Acceptance Criteria
1. On failure, `setIsUploading(false)` is invoked.
2. `setError` is set with an informative error string.
3. The upload button becomes re-enabled so the user can attempt another upload.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Resets isUploading and sets error state on failure', 'input': '', 'expected': 'setIsUploading(false)'}
        ],
        'bug_signature': '} catch (err) {\n      console.error(\'Upload failed\', err);\n    }',
        'suspected_component': 'FileUploader.jsx',
        'ai_suggestions': [
            'Error handlers in async UI components must restore interactive state so users can retry failed actions.',
            'Inspect the `catch (err)` block in `handleUpload`.',
            'Add `setIsUploading(false);` and `setError(err.message || "Upload failed");` inside the catch handler.'
        ],
        'topics': ['React', 'Async', 'Error Handling'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Promises', 'Async/Await'],
        'status': 'published'
    })

    # 104. Multi-step form loses user-entered values when navigating backward
    challenges.append({
        'id': 104,
        'title': 'Multi-Step Onboarding Form Clears Inputs on Previous Step Navigation',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Form Architecture',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Prospective insurance policy buyers abandoned an onboarding questionnaire in high numbers. Users reported that after filling out Step 1 with their personal information and moving to Step 2, clicking "Back" to correct their address cleared all input fields in Step 1, forcing them to re-type everything.

### Bug Report
In `WizardForm.jsx`, child component `Step1` initializes local state `const [name, setName] = useState('')` without reading from the passed `formData` prop. When moving to Step 2, `Step1` unmounts and its local state is destroyed. When returning to Step 1, it re-mounts with an empty string.

### Steps to Reproduce
1. In `WizardForm.jsx`, type a name into Step 1.
2. Click "Next" to navigate to Step 2.
3. Click "Back" to return to Step 1.
4. Notice the name input field is blank.

### Expected Behaviour
Step 1 inputs must initialize with and display values from `formData.name` so that navigating backward preserves previously entered values.

### Actual Behaviour
Step 1 uses uninitialized local state, losing user data upon unmount.

### Starter Files
- `WizardForm.jsx`: Multi-step form component whose child steps do not initialize from parent state.

### Task
Update `Step1` in `WizardForm.jsx` so its state initializes from `formData.name || ''` (or reads controlled values directly from `formData.name`).

### Acceptance Criteria
1. `Step1` initializes its input state from `formData.name`.
2. Navigating back and forth between steps retains entered text.
3. Changes propagate cleanly to the parent `formData` container.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
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
            {'id': 1, 'name': 'Step1 initializes with formData.name', 'input': '', 'expected': 'formData.name'}
        ],
        'bug_signature': 'export function Step1({ formData = {}, onChange }) {\n  const [name, setName] = useState(\'\');',
        'suspected_component': 'WizardForm.jsx',
        'ai_suggestions': [
            'In multi-step wizards, child steps that unmount must receive their initial state from a lifted parent state object.',
            'Look at `Step1`: it receives `formData` as a prop but ignores it in its `useState` declaration.',
            'Initialize state with `useState(formData.name || "")`.'
        ],
        'topics': ['React', 'Lifting State', 'Forms', 'Multi-step'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Lifting'],
        'status': 'published'
    })

    # 105. Dashboard renders inconsistent data after parallel API calls
    challenges.append({
        'id': 105,
        'title': 'Executive Overview Dashboard Crashes Entirely on Minor Health Check Timeout',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Asynchronous Data',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
During a brief database maintenance blip, the server health check endpoint returned an HTTP 503 while critical revenue systems remained fully operational. However, executive users viewing the overview dashboard saw a full red error screen with zero metrics displayed, completely obscuring their revenue numbers.

### Bug Report
In `MetricsDashboard.jsx`, the data loader uses `Promise.all([fetchRevenue(), fetchHealth()])`. Because `Promise.all` follows fail-fast semantics, if the secondary `fetchHealth()` promise rejects, the entire promise chain rejects immediately, hiding the successfully fetched revenue data.

### Steps to Reproduce
1. Render `MetricsDashboard.jsx` with a working `fetchRevenue` and a failing `fetchHealth`.
2. Notice the `catch` handler runs and sets `error = "Failed to load dashboard metrics"`.
3. The dashboard renders an error banner rather than displaying the available revenue card.

### Expected Behaviour
The component should use `Promise.allSettled` to independently evaluate each endpoint, displaying revenue metrics even if health checks fail.

### Actual Behaviour
A single endpoint failure causes all dashboard widgets to collapse into an error state, hiding data from healthy services.

### Starter Files
- `MetricsDashboard.jsx`: Dashboard component using fail-fast `Promise.all` for parallel queries.

### Task
Refactor `MetricsDashboard.jsx` to retrieve dashboard metrics independently so that healthy widgets display their data even if sibling endpoints fail.

### Acceptance Criteria
1. Available metrics render successfully even when some endpoints fail.
2. Failing widgets display individual error notices without breaking the entire view.
3. Partial system degradations preserve visible operational metrics.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Uses Promise.allSettled for resilient data fetching', 'input': '', 'expected': 'Promise.allSettled'}
        ],
        'bug_signature': 'Promise.all([fetchRevenue(), fetchHealth()])',
        'suspected_component': 'MetricsDashboard.jsx',
        'ai_suggestions': [
            '`Promise.all` rejects immediately if any single promise fails, which is inappropriate for dashboards composed of independent widgets.',
            'Use `Promise.allSettled` to inspect the settlement status (`status === "fulfilled"`) of each call independently.',
            'Replace `Promise.all` with `Promise.allSettled` and extract `results[0].value` and `results[1].value` when fulfilled.'
        ],
        'topics': ['React', 'Async', 'Promise.allSettled', 'Resilience'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Promises'],
        'status': 'published'
    })

    # 106. Frontend cache displays outdated profile information
    challenges.append({
        'id': 106,
        'title': 'Profile Settings Card Displays Cached Name Following Successful Save',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Caching',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Users changing their display name in account preferences reported that after seeing a green "Saved successfully" toast notification, their old name continued to appear whenever they navigated back to their profile overview. The stale name persisted until they performed a hard browser cache refresh.

### Bug Report
In `ProfileCache.jsx`, the component maintains an in-memory client `cache` map to minimize redundant HTTP fetches. In `handleUpdateName`, the API call updates the backend and local state, but fails to update or invalidate the cached entry in `cache`. When the component re-mounts, it reads the stale name from `cache.get(userId)`.

### Steps to Reproduce
1. Render `ProfileCache.jsx` with a populated cache entry for `userId`.
2. Type a new name and click "Save".
3. Notice that `cache.get(userId)` still returns the previous name because the cache was not updated.

### Expected Behaviour
Following a successful update, the client cache must be synchronized with the new profile data via `cache.set(userId, updated)`.

### Actual Behaviour
The component updates its local React state but leaves the stale entry in the shared cache.

### Starter Files
- `ProfileCache.jsx`: Profile component utilizing a shared client-side cache without cache synchronization.

### Task
Update `handleUpdateName` in `ProfileCache.jsx` to update the cache entry using `cache.set(userId, updated)` following a successful API call.

### Acceptance Criteria
1. The cache is updated with `cache.set(userId, updated)`.
2. Subsequent cache reads return the newly saved profile data.
3. Display state and cache remain in sync.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Updates or deletes the cache entry on save', 'input': '', 'expected': 'cache.set(userId'}
        ],
        'bug_signature': '',
        'suspected_component': 'ProfileCache.jsx',
        'ai_suggestions': [
            'Client-side caches must be updated or invalidated whenever mutation requests succeed.',
            'Inspect `handleUpdateName`: it updates local state `setProfile(updated)` but forgets to update the shared `cache` instance.',
            'Add `cache.set(userId, updated);` immediately after obtaining the updated profile from the API.'
        ],
        'topics': ['React', 'Caching', 'Cache Invalidation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Client-side Caching'],
        'status': 'published'
    })

    # 107. Component submits duplicate requests after repeated clicks
    challenges.append({
        'id': 107,
        'title': 'Food Ordering Form Executes Duplicate Payments on Double Click',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Form Submission',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
A high-volume food delivery app received customer complaints regarding double billing. Impatient diners frequently double-clicked the "Place Order" button during checkout, causing two identical orders to be processed concurrently and billing the customer's credit card twice for the same meal.

### Bug Report
In `SubmitButton.jsx`, the button element lacks a `disabled={isSubmitting}` attribute. Furthermore, `handleSubmit` does not check whether an existing submission is already in flight. Multiple rapid clicks initiate parallel network requests.

### Steps to Reproduce
1. In `SubmitButton.jsx`, click "Place Order" twice in rapid succession.
2. Notice that the button remains clickable while `isSubmitting` is true.
3. Observe that `onOrder` is invoked twice.

### Expected Behaviour
While an order submission is in progress, the button must be disabled (`disabled={isSubmitting}`) and `handleSubmit` must prevent re-entrant execution.

### Actual Behaviour
The button remains active throughout the network call, permitting duplicate submissions.

### Starter Files
- `SubmitButton.jsx`: Order button component lacking disable attribute and submission guard.

### Task
Update `SubmitButton.jsx` to disable the button when `isSubmitting` is true (`disabled={isSubmitting}`) and add a guard `if (isSubmitting) return;` at the beginning of `handleSubmit`.

### Acceptance Criteria
1. The `<button>` element includes `disabled={isSubmitting}`.
2. `handleSubmit` guards against re-entry if `isSubmitting` is already true.
3. Double-clicking the button triggers only a single submission.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
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
            {'id': 1, 'name': 'Disables button when isSubmitting is true', 'input': '', 'expected': 'disabled={isSubmitting}'}
        ],
        'bug_signature': '',
        'suspected_component': 'SubmitButton.jsx',
        'ai_suggestions': [
            'Prevent duplicate form submissions by disabling buttons and checking pending state flags.',
            'Look at the `<button>` element props: it currently lacks a `disabled` attribute.',
            'Add `disabled={isSubmitting}` to `<button>` and prepend `if (isSubmitting) return;` inside `handleSubmit`.'
        ],
        'topics': ['React', 'Forms', 'Debounce', 'Double Submission'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Event Handling'],
        'status': 'published'
    })

    # 108. Date picker displays incorrect date due to timezone conversion
    challenges.append({
        'id': 108,
        'title': 'Hotel Reservation Calendar Shifts Selected Check-In Date Backwards',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Date & Time',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Hotel guests booking vacation rooms from North and South America reported arriving at hotels to find their reservations were booked for the wrong day. A guest who explicitly clicked "October 15, 2026" on the calendar widget discovered that their confirmed booking showed "October 14, 2026", resulting in denied check-ins and angry guests.

### Bug Report
In `DatePicker.jsx`, `handleDateChange` receives a string formatted as `"2026-10-15"`. It parses this string via `new Date(dateString)` and formats it using `d.toISOString().split('T')[0]`. In Western timezones (e.g. UTC-5), midnight local time parses as the previous day at 7:00 PM or 8:00 PM UTC, causing `toISOString()` to roll the calendar date backward by one full day.

### Steps to Reproduce
1. Render `DatePicker.jsx` in a browser configured with a negative UTC offset (e.g. US/Eastern).
2. Select `"2026-10-15"`.
3. Observe that `selectedDate` outputs `"2026-10-14"`.

### Expected Behaviour
The selected calendar date string (`"YYYY-MM-DD"`) provided by the HTML5 date input must be used directly without passing through timezone-shifting UTC conversions.

### Actual Behaviour
Constructing a `Date` object and converting back to ISO string shifts the date backward in negative timezones.

### Starter Files
- `DatePicker.jsx`: Date picker component with erroneous Date constructor UTC serialization.

### Task
Update `handleDateChange` in `DatePicker.jsx` to directly pass and store the raw `dateString` (`setSelectedDate(dateString); onSelect(dateString);`) without constructing a timezone-sensitive `Date` object.

### Acceptance Criteria
1. The raw `dateString` is stored and propagated directly.
2. No timezone date shifting occurs across different client timezones.
3. The selected date displays identically to the chosen calendar date.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
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
            {'id': 1, 'name': 'Retains raw dateString without UTC shifting', 'input': '', 'expected': 'setSelectedDate(dateString)'}
        ],
        'bug_signature': 'const d = new Date(dateString);\n    const formatted = d.toISOString().split(\'T\')[0];\n    setSelectedDate(formatted);',
        'suspected_component': 'DatePicker.jsx',
        'ai_suggestions': [
            'Native HTML date inputs (`<input type="date">`) already supply clean `"YYYY-MM-DD"` formatted date strings.',
            'Constructing `new Date("YYYY-MM-DD")` and converting to ISO string shifts dates backwards in timezones west of UTC.',
            'Directly use `setSelectedDate(dateString); onSelect(dateString);` without parsing into a `Date` object.'
        ],
        'topics': ['React', 'Dates', 'Timezones'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JavaScript Date Handling'],
        'status': 'published'
    })

    # 109. Form does not preserve server validation errors
    challenges.append({
        'id': 109,
        'title': 'Workspace Signup Form Conceals Field-Level Validation Errors',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Form Validation',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
Marketing and product teams identified a sharp drop in enterprise signup completions. When prospective clients attempted to create a workspace with an unavailable subdomain name, the backend responded with HTTP 422 and a detailed error message. However, the registration form wiped out all context and displayed only a vague "Submission failed" banner, leaving users unable to determine what went wrong.

### Bug Report
In `ServerErrorForm.jsx`, the catch handler catches the submission error but only executes `setGeneralError('Submission failed')`. It ignores the field-level errors provided in `err.response.data.errors`, preventing the input-specific error message (`fieldErrors.subdomain`) from rendering.

### Steps to Reproduce
1. Submit a taken subdomain in `ServerErrorForm.jsx` that rejects with `{ response: { data: { errors: { subdomain: 'Subdomain already in use' } } } }`.
2. Observe that only the generic error "Submission failed" appears.
3. The specific subdomain error text is never displayed beneath the input.

### Expected Behaviour
The catch handler must inspect `err.response?.data?.errors` and pass them to `setFieldErrors` so that specific validation messages appear next to invalid inputs.

### Actual Behaviour
Field-specific error structures are discarded in favor of a generic string message.

### Starter Files
- `ServerErrorForm.jsx`: Form component discarding field-level API error responses.

### Task
Update `handleSubmit` in `ServerErrorForm.jsx` to populate `setFieldErrors(err.response?.data?.errors || {})` inside the catch block.

### Acceptance Criteria
1. The catch block extracts `err.response?.data?.errors`.
2. `setFieldErrors` is populated with the field error map.
3. The specific error message is displayed beneath the subdomain input field.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
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
            {'id': 1, 'name': 'Populates fieldErrors from server error response', 'input': '', 'expected': 'setFieldErrors(err.response'}
        ],
        'bug_signature': '} catch (err) {\n      setGeneralError(\'Submission failed\');\n    }',
        'suspected_component': 'ServerErrorForm.jsx',
        'ai_suggestions': [
            'API validation errors (HTTP 422) provide structured per-field error maps that should be routed to their respective form inputs.',
            'Check `err.response?.data?.errors` inside the catch block.',
            'Add `if (err.response?.data?.errors) setFieldErrors(err.response.data.errors);`.'
        ],
        'topics': ['React', 'Forms', 'Validation', 'Error Handling'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['HTTP Status Codes', 'React Form State'],
        'status': 'published'
    })

    # 110. Accessible dropdown fails to manage keyboard navigation correctly
    challenges.append({
        'id': 110,
        'title': 'Accessible Selection Menu Traps Keyboard Focus by Ignoring Escape',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Accessibility',
        'time_estimate': '15 mins',
        'points': 200,
        'description': """### Incident Report
During a mandatory Section 508 and WCAG 2.1 compliance audit for a government contractor, the web application failed automated and manual accessibility testing. Keyboard-only users opening the custom dropdown menu were trapped inside the listbox because pressing the Escape key had no effect.

### Bug Report
In `AccessibleDropdown.jsx`, the keyboard listener `handleKeyDown` handles `'Enter'` and `' '` (Space) to toggle the menu, but completely omits a handler for `e.key === 'Escape'`. When the dropdown is open, pressing Escape does not close it.

### Steps to Reproduce
1. Render `AccessibleDropdown.jsx` and open the menu by pressing Space or clicking the button.
2. Press the Escape key.
3. Observe that the dropdown remains open and focus is trapped.

### Expected Behaviour
Pressing the Escape key while the dropdown is open must dismiss the menu by calling `setIsOpen(false)`.

### Actual Behaviour
The keydown handler ignores the Escape key, leaving the menu open.

### Starter Files
- `AccessibleDropdown.jsx`: Custom dropdown component lacking Escape key handler.

### Task
Update `handleKeyDown` in `AccessibleDropdown.jsx` to check if `e.key === 'Escape'` and dismiss the dropdown with `setIsOpen(false)`.

### Acceptance Criteria
1. `handleKeyDown` checks `if (e.key === 'Escape')`.
2. When Escape is pressed, `setIsOpen(false)` is invoked.
3. The menu closes cleanly without disturbing selection state.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.
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
            {'id': 1, 'name': 'Closes dropdown when Escape key is pressed', 'input': '', 'expected': "e.key === 'Escape'"}
        ],
        'bug_signature': 'const handleKeyDown = (e) => {\n    if (e.key === \'Enter\' || e.key === \' \') {',
        'suspected_component': 'AccessibleDropdown.jsx',
        'ai_suggestions': [
            'WCAG criteria require custom dropdowns and dialogs to be dismissable via the standard Escape key.',
            'Examine `handleKeyDown`: it currently only checks for Enter and Space.',
            'Add `if (e.key === "Escape") setIsOpen(false);` inside `handleKeyDown`.'
        ],
        'topics': ['React', 'Accessibility', 'WCAG', 'Keyboard Events'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Web Accessibility Basics'],
        'status': 'published'
    })

    return challenges
