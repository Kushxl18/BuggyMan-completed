"""
Frontend Studio: Hard Challenges (111 to 120)
Standardized into realistic production incident debugging tickets.
"""

def get_frontend_hard():
    challenges = []

    # 111. Concurrent frontend requests create inconsistent checkout state
    challenges.append({
        'id': 111,
        'title': 'Concert Ticket Checkout Permits Overlapping Order Submissions',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Concurrency',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
During a high-demand concert ticket release, customer support and accounting were flooded with duplicate ticket purchases and split-billing disputes. Frustrated fans experiencing brief checkout latency clicked the "Confirm Checkout" button multiple times, causing two separate order creation requests to hit the payment gateway in parallel.

### Bug Report
In `CheckoutFlow.jsx`, `handleCheckout` initiates an order request without checking if an authorization request is already pending. Furthermore, the button's disabled condition only checks `status === 'completed'`, leaving the action fully clickable while `status === 'processing'`.

### Steps to Reproduce
1. In `CheckoutFlow.jsx`, trigger `handleCheckout`.
2. Before the asynchronous network call resolves, invoke `handleCheckout` a second time.
3. Observe that both requests dispatch concurrently to the order creation endpoint.

### Expected Behaviour
The checkout action must be protected by an execution lock (such as checking `if (status === 'processing') return;`) and disabling the submit button whenever `status === 'processing'`.

### Actual Behaviour
The component allows overlapping order submissions, leading to duplicate transactions and inventory over-allocation.

### Starter Files
- `CheckoutFlow.jsx`: Order authorization component lacking concurrency locks and pending state guards.

### Task
Update `CheckoutFlow.jsx` to guard against concurrent requests: check `if (status === 'processing') return;` at the beginning of `handleCheckout`, and disable the button while `status === 'processing'` or `status === 'completed'`.

### Acceptance Criteria
1. `handleCheckout` aborts immediately if `status === 'processing'`.
2. The `<button>` is disabled when `status === 'processing'`.
3. Overlapping checkout clicks dispatch exactly one authorization request.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'CheckoutFlow.jsx',
            'content': '''import React, { useState, useRef } from 'react';

export default function CheckoutFlow({ cart, api }) {
  const [status, setStatus] = useState('idle');
  const [orderId, setOrderId] = useState(null);

  const handleCheckout = async () => {
    setStatus('processing');
    try {
      const res = await api.createOrder(cart);
      setOrderId(res.id);
      setStatus('completed');
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div className="p-4">
      <h3>Cart Total: ${cart.total}</h3>
      <button
        onClick={handleCheckout}
        disabled={status === 'completed'}
        className="bg-blue-600 text-white px-4 py-2 rounded mt-2"
      >
        {status === 'processing' ? 'Authorizing...' : 'Confirm Checkout'}
      </button>
      {orderId && <p className="text-green-600 mt-2">Order Confirmed: {orderId}</p>}
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Guards against concurrent checkout with processing lock', 'input': '', 'expected': "status === 'processing'"}
        ],
        'bug_signature': 'const handleCheckout = async () => {\n    setStatus(\'processing\');',
        'suspected_component': 'CheckoutFlow.jsx',
        'ai_suggestions': [
            'Financial workflows must enforce an atomic mutex or lock preventing concurrent requests on user-facing controls.',
            'Inspect the entry point of `handleCheckout` and the button `disabled` condition.',
            'Add `if (status === "processing") return;` at the start of `handleCheckout` and disable the button when `status === "processing"`.'
        ],
        'topics': ['React', 'Concurrency', 'State Machine', 'E-commerce'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Management', 'Asynchronous Locks'],
        'status': 'published'
    })

    # 112. Memory leak develops after repeated mount/unmount cycles
    challenges.append({
        'id': 112,
        'title': 'Trading Dashboard Ticker Retains Zombie Listeners on Tab Switch',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Memory Management',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
Day traders using the cryptocurrency charting platform reported that after several hours of monitoring market movements and switching between different currency tabs, browser tabs became increasingly unresponsive and ultimately crashed with an "Out of Memory" error. Console logs showed continuous React warnings: `"Can't perform a React state update on an unmounted component"`.

### Bug Report
In `SubscriptionWidget.jsx`, `eventBus.subscribe(symbol, handleTick)` is called inside `useEffect`. When the user navigates away or switches tabs, the component unmounts without calling `unsubscribe`. The singleton event bus retains a reference to `handleTick`, keeping the entire unmounted component tree alive in memory.

### Steps to Reproduce
1. Mount `SubscriptionWidget.jsx` with a coin symbol.
2. Unmount the widget by switching tabs or un-rendering it.
3. Observe that the event bus still invokes `handleTick`, attempting state updates on the unmounted instance.

### Expected Behaviour
The `useEffect` hook must return a cleanup callback that invokes `eventBus.unsubscribe(symbol, handleTick)` when the component unmounts or when dependencies change.

### Actual Behaviour
The effect omits the cleanup callback, leaving zombie callbacks permanently registered.

### Starter Files
- `SubscriptionWidget.jsx`: Streaming price ticker component without event unsubscription logic.

### Task
Update `SubscriptionWidget.jsx` to unsubscribe from live market data streams when the component unmounts.

### Acceptance Criteria
1. The event listener subscription is cancelled upon component unmount.
2. Background ticker feeds stop delivering updates to detached components.
3. Memory overhead remains stable across component lifecycles.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'SubscriptionWidget.jsx',
            'content': '''import React, { useState, useEffect } from 'react';

export default function SubscriptionWidget({ symbol, eventBus }) {
  const [price, setPrice] = useState(null);

  useEffect(() => {
    const handleTick = (newPrice) => {
      setPrice(newPrice);
    };

    eventBus.subscribe(symbol, handleTick);
  }, [symbol, eventBus]);

  return (
    <div className="card p-4 border rounded">
      <h4>{symbol}</h4>
      <p className="text-2xl font-mono">{price ? `$${price}` : 'Connecting...'}</p>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Cleans up subscription on unmount', 'input': '', 'expected': 'eventBus.unsubscribe'}
        ],
        'bug_signature': 'eventBus.subscribe(symbol, handleTick);\n  }, [symbol, eventBus]);',
        'suspected_component': 'SubscriptionWidget.jsx',
        'ai_suggestions': [
            'Components subscribing to global publish/subscribe buses must unsubscribe when unmounting to prevent memory leaks.',
            'React effects can return a cleanup function that runs before re-running the effect and when the component unmounts.',
            'Return `() => { eventBus.unsubscribe(symbol, handleTick); };` from the `useEffect` body.'
        ],
        'topics': ['React', 'Memory Leaks', 'useEffect Cleanup', 'Event Bus'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Lifecycle', 'Memory Management'],
        'status': 'published'
    })

    # 113. Shared client-side cache exposes data between authenticated sessions
    challenges.append({
        'id': 113,
        'title': 'Shared Kiosk Client Cache Exposes Preceding Patient Records',
        'difficulty': 'Hard',
        'technology': 'JavaScript',
        'category': 'Security',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
A critical HIPAA data breach incident was reported at a shared hospital ward kiosk. A nurse logged out of the terminal after charting patient vitals. When a doctor subsequently signed into the terminal to examine an unrelated patient, the application pulled cached diagnostic records from memory, displaying the previous patient's confidential health data under the doctor's session.

### Bug Report
In `SessionCache.jsx`, the exported `sessionCache` map holds sensitive user-scoped records in memory. In `logoutUser`, the handler clears `localStorage` tokens and notifies the backend, but fails to purge `sessionCache`. Subsequent logins on the same client workstation read cached records left by the previous session.

### Steps to Reproduce
1. Populate `sessionCache` with patient records during user session 1.
2. Call `logoutUser(authApi, onLoggedOut)`.
3. Inspect `sessionCache.size`: observe that entries remain in memory.

### Expected Behaviour
`logoutUser` must invalidate and purge all entries from `sessionCache` via `sessionCache.clear()` prior to concluding the sign-out flow.

### Actual Behaviour
The in-memory cache persists across logout transitions, causing cross-tenant data leakage.

### Starter Files
- `SessionCache.jsx`: Client authentication and caching utility failing to clear in-memory cache on sign-out.

### Task
Update user sign-out in `SessionCache.jsx` to purge cached in-memory user data upon logging out.

### Acceptance Criteria
1. In-memory session caches are emptied when the user logs out.
2. Sensitive customer data is not retained across user sessions.
3. Subsequent logins begin with a fresh, unpolluted cache.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'SessionCache.jsx',
            'content': '''import React from 'react';

export const sessionCache = new Map();

export async function logoutUser(authApi, onLoggedOut) {
  try {
    await authApi.logout();
    localStorage.removeItem('authToken');
  } finally {
    if (onLoggedOut) onLoggedOut();
  }
}

export default function SessionCacheView({ currentUser, onLogout, authApi }) {
  return (
    <div className="p-4">
      <p>Signed in as: {currentUser?.username}</p>
      <button
        onClick={() => logoutUser(authApi, onLogout)}
        className="bg-red-600 text-white px-3 py-1 rounded"
      >
        Sign Out
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Clears sessionCache on logout', 'input': '', 'expected': 'sessionCache.clear()'}
        ],
        'bug_signature': 'localStorage.removeItem(\'authToken\');\n  } finally {',
        'suspected_component': 'SessionCache.jsx',
        'ai_suggestions': [
            'Client session caches storing personal or confidential data must be purged on user logout to prevent session crossover.',
            'Look at `logoutUser`: it removes auth tokens from localStorage but does not clear `sessionCache`.',
            'Add `sessionCache.clear();` inside `logoutUser` alongside `localStorage.removeItem(\'authToken\');`.'
        ],
        'topics': ['React', 'Security', 'Caching', 'Authentication'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Web Security', 'Session Management'],
        'status': 'published'
    })

    # 114. Optimistic UI update corrupts state after overlapping failed requests
    challenges.append({
        'id': 114,
        'title': 'Optimistic Feed Like Counter Decrements Below Zero on Network Drop',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Optimistic UI',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
Social feed users browsing in areas with intermittent connectivity noticed post like counters turning negative (`-1 Likes`). When users tapped like while walking through cellular dead zones, the network call failed, but the UI rollback logic subtracted from a mutated count, corrupting the feed statistics.

### Bug Report
In `OptimisticFeed.jsx`, `handleToggleLike` optimistically applies `setLikes(likes + 1)`. If the network request fails, the catch block blindly executes `setLikes(likes - 1)`. If the user tapped the button again or if `likes` changed in the interim, subtracting 1 from the stale or altered count drives the metric below zero.

### Steps to Reproduce
1. Render `OptimisticFeed.jsx` with `initialLikes = 0`.
2. Click the like button.
3. Simulate an API rejection in `api.likePost()`.
4. Observe that the rollback math calculates `0 - 1 = -1` or desynchronizes state.

### Expected Behaviour
Before applying an optimistic state mutation, capture exact snapshots of the current state (`previousLikes = likes`, `previousIsLiked = isLiked`), and revert strictly to those snapshots if the API fails.

### Actual Behaviour
The error handler relies on blind arithmetic rollback (`likes - 1`), causing desynchronized state.

### Starter Files
- `OptimisticFeed.jsx`: Like toggle component with brittle arithmetic rollback.

### Task
Update `handleToggleLike` in `OptimisticFeed.jsx` to capture snapshot variables (`previousLikes` and `previousIsLiked`) before the optimistic update, and restore those snapshot values in the `catch` block.

### Acceptance Criteria
1. Snapshots of `likes` and `isLiked` are stored before the state update.
2. On API error, `setLikes(previousLikes)` and `setIsLiked(previousIsLiked)` are invoked.
3. The counter never drops below the baseline state on failed requests.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.
""",
        'files': [{
            'name': 'OptimisticFeed.jsx',
            'content': '''import React, { useState } from 'react';

export default function OptimisticFeed({ initialLikes = 10, api }) {
  const [likes, setLikes] = useState(initialLikes);
  const [isLiked, setIsLiked] = useState(false);

  const handleToggleLike = async () => {
    setLikes(likes + 1);
    setIsLiked(true);

    try {
      await api.likePost();
    } catch (err) {
      // Reverting with stale value creates negative or out-of-sync counts
      setLikes(likes - 1);
      setIsLiked(false);
    }
  };

  return (
    <div className="p-4 border rounded">
      <button
        onClick={handleToggleLike}
        className={`px-4 py-2 rounded ${isLiked ? 'bg-pink-600 text-white' : 'bg-gray-200'}`}
      >
        ❤️ {likes} Likes
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Captures previousLikes snapshot and restores on error', 'input': '', 'expected': 'previousLikes'}
        ],
        'bug_signature': '// Reverting with stale value creates negative or out-of-sync counts\n      setLikes(likes - 1);',
        'suspected_component': 'OptimisticFeed.jsx',
        'ai_suggestions': [
            'Optimistic mutations should save an immutable snapshot of state before changing it, rather than computing inverse arithmetic.',
            'Store `const previousLikes = likes;` and `const previousIsLiked = isLiked;` prior to the optimistic update.',
            'In the `catch` block, revert with `setLikes(previousLikes); setIsLiked(previousIsLiked);`.'
        ],
        'topics': ['React', 'Optimistic UI', 'State Snapshots'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Asynchronous State', 'Optimistic Updates'],
        'status': 'published'
    })

    # 115. Complex dashboard produces inconsistent derived state
    challenges.append({
        'id': 115,
        'title': 'Executive KPI Summary Freezes on Outdated Monthly Revenue Filter',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Performance & Memoization',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
C-suite executives reviewing company revenue performance reported a discrepancies bug in their quarterly KPI portal. When switching tier filters from "Enterprise" to "Starter", the underlying transaction table updated, but the main Monthly Recurring Revenue (MRR) headline metrics remained frozen on the Enterprise numbers, leading to skewed financial analyses.

### Bug Report
In `AnalyticsHub.jsx`, the `metrics` calculation is wrapped in `useMemo`. However, its dependency array is declared as `[]` (empty). As a result, the memoized metrics are computed only once during initial mount and never recompute when `tierFilter` or `transactions` change.

### Steps to Reproduce
1. Render `AnalyticsHub.jsx` with transactions spanning multiple tiers.
2. Select a different tier from the dropdown (e.g. "Enterprise").
3. Observe that Total MRR and Transaction count remain unchanged from the initial view.

### Expected Behaviour
The `useMemo` hook must declare `[transactions, tierFilter]` in its dependencies, recalculating metrics whenever transactions or active filters change.

### Actual Behaviour
The empty dependency array prevents memoization recalculation, presenting stale metrics.

### Starter Files
- `AnalyticsHub.jsx`: Analytics summary component with missing memoization dependencies.

### Task
Update the memoized calculation in `AnalyticsHub.jsx` so that metrics recompute whenever transaction lists or filter criteria change.

### Acceptance Criteria
1. Analytics metrics recompute automatically when filter criteria change.
2. Updated transaction data triggers fresh metric aggregation.
3. Summary values accurately reflect the selected tier filter.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
""",
        'files': [{
            'name': 'AnalyticsHub.jsx',
            'content': '''import React, { useState, useMemo } from 'react';

export default function AnalyticsHub({ transactions = [] }) {
  const [tierFilter, setTierFilter] = useState('All');

  const metrics = useMemo(() => {
    const filtered = tierFilter === 'All'
      ? transactions
      : transactions.filter(t => t.tier === tierFilter);

    const totalMRR = filtered.reduce((acc, curr) => acc + curr.amount, 0);
    const avgMRR = filtered.length ? totalMRR / filtered.length : 0;
    return { totalMRR, avgMRR, count: filtered.length };
  }, []);

  return (
    <div className="p-4">
      <select value={tierFilter} onChange={(e) => setTierFilter(e.target.value)}>
        <option value="All">All</option>
        <option value="Starter">Starter</option>
        <option value="Enterprise">Enterprise</option>
      </select>
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="border p-4">Total MRR: ${metrics.totalMRR}</div>
        <div className="border p-4">Transactions: {metrics.count}</div>
      </div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Includes transactions and tierFilter in useMemo dependencies', 'input': '', 'expected': '[transactions, tierFilter]'}
        ],
        'bug_signature': 'return { totalMRR, avgMRR, count: filtered.length };\n  }, []);',
        'suspected_component': 'AnalyticsHub.jsx',
        'ai_suggestions': [
            'Values computed with `useMemo` must specify all outer variables referenced inside the calculation function in their dependency array.',
            'Inspect the dependencies of `useMemo`: the empty array `[]` tells React never to recompute the value after initial render.',
            'Change `useMemo(..., [])` to `useMemo(..., [transactions, tierFilter])`.'
        ],
        'topics': ['React', 'useMemo', 'Derived State', 'Performance'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Memoization'],
        'status': 'published'
    })

    # 116. Frontend authentication flow mishandles token expiration & concurrent refreshes
    challenges.append({
        'id': 116,
        'title': 'Concurrent Dashboard Requests Trigger Replay-Flagged Token Rotation',
        'difficulty': 'Hard',
        'technology': 'JavaScript',
        'category': 'Authentication Architecture',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
Users logging into the cloud dashboard were unexpectedly logged out within minutes. Security logs revealed that when access tokens expired, the client dashboard fired multiple simultaneous API requests (user profile, notifications, billing status). Each request received an HTTP 401 and independently initiated a refresh token exchange. Because the backend enforces refresh token rotation (one-time use), subsequent parallel requests sent invalidated refresh tokens, triggering security alarms and terminating the session.

### Bug Report
In `AuthManager.jsx`, `requestWithAuth` handles 401 errors by directly awaiting `refreshApi()`. It does not coordinate concurrent requests using a shared `refreshPromise`. When four requests fail simultaneously with 401, four separate token refreshes are executed in parallel.

### Steps to Reproduce
1. Execute multiple concurrent calls to `requestWithAuth` with an expired token.
2. Observe that each 401 handler calls `refreshApi()` independently.
3. The multiple refresh attempts trigger backend replay detection.

### Expected Behaviour
If a token refresh is already in progress, subsequent 401 requests must await the existing shared `refreshPromise` rather than creating new ones.

### Actual Behaviour
Every 401 response executes an uncoordinated token refresh call.

### Starter Files
- `AuthManager.jsx`: HTTP client interceptor lacking refresh request deduplication.

### Task
Refactor token refresh in `AuthManager.jsx` so that concurrent requests share a single in-flight refresh promise rather than initiating duplicate refresh calls.

### Acceptance Criteria
1. Concurrent 401 responses share a single in-flight `refreshPromise`.
2. When the refresh completes, all pending requests use the new access token.
3. `refreshPromise` is cleared upon completion.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'AuthManager.jsx',
            'content': '''let currentToken = 'old_token';
let refreshPromise = null;

export async function requestWithAuth(url, fetchApi, refreshApi) {
  try {
    return await fetchApi(url, currentToken);
  } catch (err) {
    if (err.status === 401) {
      const newTokens = await refreshApi();
      currentToken = newTokens.accessToken;
      return await fetchApi(url, currentToken);
    }
    throw err;
  }
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Shares single in-flight refreshPromise across calls', 'input': '', 'expected': 'refreshPromise'}
        ],
        'bug_signature': 'if (err.status === 401) {\n      const newTokens = await refreshApi();',
        'suspected_component': 'AuthManager.jsx',
        'ai_suggestions': [
            'Token refresh calls must be deduplicated across concurrent HTTP interceptors to support refresh token rotation.',
            'Check if a module-level `refreshPromise` already exists before starting a new refresh request.',
            'Assign `refreshPromise = refreshApi().finally(() => { refreshPromise = null; });` if null, then `await refreshPromise`.'
        ],
        'topics': ['JavaScript', 'Authentication', 'Token Refresh', 'Concurrency'],
        'skills_tested': ['JavaScript', 'Frontend Architecture'],
        'prerequisites': ['JWT Architecture', 'Promise Chaining'],
        'status': 'published'
    })

    # 117. Virtualized list renders incorrect items after filtering and reordering
    challenges.append({
        'id': 117,
        'title': 'Virtualized Log Viewer Reassigns Log Messages on Severity Filter',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Virtualization',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
DevOps engineers investigating a critical production incident were misled by the server log viewer. When filtering from "ALL" logs to "ERROR" logs, the virtualized list retained cached DOM nodes with old warning messages or assigned wrong log timestamps to error traces, wasting hours of debugging time.

### Bug Report
In `VirtualList.jsx`, the virtual slice maps visible items using `key={startIndex + index}`. Because keys represent the window offset index rather than the identity of the log entity, filtering or reordering logs causes React to reuse old DOM nodes and their internal state for entirely different log records.

### Steps to Reproduce
1. Render `VirtualList.jsx` with a list of log items containing unique `id` properties.
2. Filter the items list.
3. Observe that React's virtual DOM reconciliation reuses previous element nodes because keys correspond to array offsets rather than entity IDs.

### Expected Behaviour
Virtualized list items must use stable, unique entity identifiers (`key={item.id}`) to guarantee that elements are correctly mapped during filtering, sorting, and dynamic slicing.

### Actual Behaviour
The list uses computed window row indices as keys (`startIndex + index`), causing reconciliation mismatches.

### Starter Files
- `VirtualList.jsx`: Virtualized list component using index-based window keys.

### Task
Update the virtualization list in `VirtualList.jsx` to assign persistent unique item identifiers to rendered list rows rather than virtual index offsets.

### Acceptance Criteria
1. Virtualized list elements use stable item identifiers for element keys.
2. Scrolling and filtering operations maintain correct element-to-data mapping.
3. Visual jumpiness and mismatched row attributes are resolved.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'VirtualList.jsx',
            'content': '''import React, { useState } from 'react';

export default function VirtualList({ items = [], rowHeight = 35, viewportHeight = 350 }) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - 2);
  const visibleCount = Math.ceil(viewportHeight / rowHeight) + 4;
  const visibleItems = items.slice(startIndex, startIndex + visibleCount);

  return (
    <div
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
      style={{ height: viewportHeight, overflowY: 'auto', position: 'relative' }}
      className="border"
    >
      <div style={{ height: items.length * rowHeight, position: 'relative' }}>
        {visibleItems.map((item, index) => (
          <div
            key={startIndex + index}
            style={{
              position: 'absolute',
              top: (startIndex + index) * rowHeight,
              height: rowHeight,
              width: '100%'
            }}
            className="p-2 border-b truncate"
          >
            [{item.level}] {item.message}
          </div>
        ))}
      </div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Uses stable item.id for virtualized row key', 'input': '', 'expected': 'key={item.id}'}
        ],
        'bug_signature': 'key={startIndex + index}',
        'suspected_component': 'VirtualList.jsx',
        'ai_suggestions': [
            'In virtualized lists, using computed index offsets as keys leads to rendering glitches when the underlying data is filtered or sorted.',
            'React keys must identify the underlying entity, not its temporary position inside the viewport window.',
            'Replace `key={startIndex + index}` with `key={item.id}` on the rendered row container.'
        ],
        'topics': ['React', 'Virtualization', 'Keys', 'Reconciliation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['DOM Virtualization', 'React Keys'],
        'status': 'published'
    })

    # 118. Multi-step checkout loses consistency when requests fail partway through
    challenges.append({
        'id': 118,
        'title': 'Flight Reservation Abort Leaves Locked Seats Unreleased',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Compensating Transactions',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
An airline reservation platform experienced a surge in abandoned seats and customer complaints. Passengers whose credit cards were declined during checkout discovered that the system kept their selected seat locked for fifteen minutes, preventing them from immediately retrying with an alternate payment card and blocking other flyers from booking the seat.

### Bug Report
In `MultiStepCheckout.jsx`, the booking sequence first calls `api.reserveSeat(flightId, seatNumber)` and then `api.processPayment(...)`. If payment processing fails, the catch block sets the error message but never initiates a compensating transaction to release the seat reservation (`api.releaseSeat(reservation.id)`).

### Steps to Reproduce
1. In `MultiStepCheckout.jsx`, simulate a successful seat reservation followed by a rejected payment.
2. Observe that `api.releaseSeat` is never invoked in the error handler.
3. The reserved seat remains held on the backend inventory.

### Expected Behaviour
If payment fails after a reservation has been successfully acquired, the catch handler must invoke a compensating action: `await api.releaseSeat(reservation.id)` before presenting the error.

### Actual Behaviour
The seat remains held in pending state without cancellation.

### Starter Files
- `MultiStepCheckout.jsx`: Multi-phase transaction component lacking compensating rollback logic.

### Task
Update `handleBook` in `MultiStepCheckout.jsx` to verify if `reservation` exists inside the `catch` block and invoke `await api.releaseSeat(reservation.id)`.

### Acceptance Criteria
1. The catch handler checks `if (reservation)`.
2. When present, `await api.releaseSeat(reservation.id)` is executed.
3. The user is informed of the payment failure and the seat is released for re-selection.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'MultiStepCheckout.jsx',
            'content': '''import React, { useState } from 'react';

export default function MultiStepCheckout({ flightId, seatNumber, api }) {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const handleBook = async (paymentDetails) => {
    setStatus('booking');
    setError(null);
    let reservation = null;

    try {
      reservation = await api.reserveSeat(flightId, seatNumber);
      await api.processPayment(reservation.id, paymentDetails);
      setStatus('confirmed');
    } catch (err) {
      setError(err.message || 'Payment failed');
      setStatus('failed');
    }
  };

  return (
    <div className="p-4 border rounded">
      <h3>Seat: {seatNumber}</h3>
      {error && <p className="text-red-500">{error}</p>}
      <button
        onClick={() => handleBook({ card: '4111...' })}
        disabled={status === 'booking'}
        className="bg-indigo-600 text-white px-4 py-2 rounded mt-2"
      >
        {status === 'booking' ? 'Processing...' : 'Book & Pay'}
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Releases reserved seat on payment failure', 'input': '', 'expected': 'api.releaseSeat'}
        ],
        'bug_signature': '} catch (err) {\n      setError(err.message || \'Payment failed\');',
        'suspected_component': 'MultiStepCheckout.jsx',
        'ai_suggestions': [
            'Multi-step workflows that acquire distributed resources must execute compensating actions if downstream steps fail.',
            'Check whether `reservation` was successfully established prior to the payment exception.',
            'Inside `catch (err)`, add `if (reservation) { await api.releaseSeat(reservation.id); }` before setting error state.'
        ],
        'topics': ['React', 'Compensating Transactions', 'Error Recovery'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Distributed Consistency', 'Compensating Actions'],
        'status': 'published'
    })

    # 119. Real-time interface applies out-of-order events and displays stale state
    challenges.append({
        'id': 119,
        'title': 'Collaborative Document Buffer Reverts Recent Edits on Out-Of-Order Packets',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Real-Time State',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
Content editors working together in the real-time collaborative workspace reported erratic cursor jumps and disappearing paragraphs. When editing over cellular or high-jitter network connections, older text revisions frequently overwrote newer sentences, causing content loss and confusion among collaborating writers.

### Bug Report
In `RealtimeChat.jsx`, the WebSocket listener `handleIncomingMessage` updates document content with `setContent(event.text)` for every packet received. Because UDP/network jitter can deliver packets out of order, an older packet with sequence number 14 arriving after packet 15 overwrites the latest state.

### Steps to Reproduce
1. In `RealtimeChat.jsx`, dispatch event `{ seq: 15, text: 'Final Title' }`.
2. Dispatch a delayed event `{ seq: 14, text: 'Draft Title' }`.
3. Notice that the editor displays `'Draft Title'`, discarding the newer edit.

### Expected Behaviour
The component must track the highest sequence number processed (`lastSeq.current`). If an incoming event has `event.seq <= lastSeq.current`, it must be ignored.

### Actual Behaviour
Every incoming event is applied unconditionally without sequence validation.

### Starter Files
- `RealtimeChat.jsx`: Real-time text component applying events without monotonic sequence verification.

### Task
Update `handleIncomingMessage` in `RealtimeChat.jsx` to discard events if `event.seq <= lastSeq.current` before updating state and updating `lastSeq.current`.

### Acceptance Criteria
1. The message handler checks `if (event.seq <= lastSeq.current) return;`.
2. Out-of-order delayed packets are rejected.
3. The editor strictly maintains monotonically increasing sequence state.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.
""",
        'files': [{
            'name': 'RealtimeChat.jsx',
            'content': '''import React, { useState, useRef, useEffect } from 'react';

export default function RealtimeChat({ socket }) {
  const [content, setContent] = useState('');
  const lastSeq = useRef(0);

  useEffect(() => {
    const handleIncomingMessage = (event) => {
      setContent(event.text);
      lastSeq.current = event.seq;
    };

    socket.on('message', handleIncomingMessage);
    return () => socket.off('message', handleIncomingMessage);
  }, [socket]);

  return (
    <div className="p-4 border">
      <h3>Live Document</h3>
      <div className="p-2 bg-gray-100 rounded mt-2">{content}</div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Rejects out-of-order events using sequence comparison', 'input': '', 'expected': 'event.seq <'}
        ],
        'bug_signature': 'const handleIncomingMessage = (event) => {\n      setContent(event.text);',
        'suspected_component': 'RealtimeChat.jsx',
        'ai_suggestions': [
            'Real-time streaming event handlers must enforce sequence ordering to prevent late-arriving packets from overwriting newer state.',
            'Examine `handleIncomingMessage`: it immediately updates `content` without comparing `event.seq` against `lastSeq.current`.',
            'Add `if (event.seq <= lastSeq.current) return;` before calling `setContent(event.text)`.'
        ],
        'topics': ['React', 'WebSockets', 'Sequence Numbers', 'Event Ordering'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Real-time Systems', 'Network Jitter'],
        'status': 'published'
    })

    # 120. Frontend permission check hides a control but fails on unauthorized responses
    challenges.append({
        'id': 120,
        'title': 'Revoked Admin Session Triggers White-Screen Crash on Account Action',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Security & Error Handling',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Incident Report
An enterprise IT administrator logged into a management portal had their elevated privileges revoked by an organization owner in a different browser tab. When the administrator attempted to click "Delete Account", the backend responded with HTTP 403 Forbidden. Instead of displaying a polite "Access Denied" notice, the entire frontend crashed into a blank white screen due to an uncaught promise rejection.

### Bug Report
In `AdminPanel.jsx`, `handleDelete` calls `await api.deleteAccount(user.id)` without a `try/catch` wrapper. When the API returns a 403 error, the unhandled rejection bubbles to the root React error boundary, tearing down the UI.

### Steps to Reproduce
1. In `AdminPanel.jsx`, invoke `handleDelete` while mocking an HTTP 403 response.
2. Observe that the uncaught rejection causes a complete application crash.
3. No user-friendly error message is displayed.

### Expected Behaviour
The API call must be wrapped in `try/catch`. On an HTTP 403 error, set `setErrorMessage('Access Denied: You do not have permission to perform this action.')` while keeping the interface intact.

### Actual Behaviour
The API call runs unguarded, crashing the application on unauthorized access.

### Starter Files
- `AdminPanel.jsx`: Administration panel component lacking exception handling for unauthorized actions.

### Task
Wrap the `api.deleteAccount` call in `AdminPanel.jsx` in a `try/catch` block, setting `errorMessage` and resetting `isDeleting` gracefully.

### Acceptance Criteria
1. `api.deleteAccount` is enclosed in a `try/catch` statement.
2. In the catch block, an informative error message is stored in state.
3. `isDeleting` is reset to `false` and the UI remains responsive without crashing.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'AdminPanel.jsx',
            'content': '''import React, { useState } from 'react';

export default function AdminPanel({ user, api, onAccessDenied }) {
  const [errorMessage, setErrorMessage] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    setErrorMessage('');
    await api.deleteAccount(user.id);
    setIsDeleting(false);
  };

  return (
    <div className="p-4 border rounded border-red-300">
      <h3 className="text-red-700 font-bold">Danger Zone</h3>
      {errorMessage && <p className="text-red-500 mb-2">{errorMessage}</p>}
      <button
        onClick={handleDelete}
        disabled={isDeleting}
        className="bg-red-600 text-white px-3 py-1 rounded"
      >
        {isDeleting ? 'Deleting...' : 'Delete Account'}
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Handles 403 Forbidden with try/catch and error message', 'input': '', 'expected': 'try {'}
        ],
        'bug_signature': 'const handleDelete = async () => {\n    setIsDeleting(true);\n    setErrorMessage(\'\');\n    await api.deleteAccount(user.id);\n    setIsDeleting(false);\n  };',
        'suspected_component': 'AdminPanel.jsx',
        'ai_suggestions': [
            'Privileged UI actions must anticipate HTTP 403 authorization failures gracefully rather than letting unhandled rejections crash the view.',
            'Enclose the asynchronous `api.deleteAccount(user.id)` call within a `try/catch` structure.',
            'Inside `catch (err)`, update `setErrorMessage(err.message || "Access Denied")` and reset `setIsDeleting(false)`.'
        ],
        'topics': ['React', 'Security', 'Error Boundaries', 'HTTP 403'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['HTTP Error Codes', 'Error Resilience'],
        'status': 'published'
    })

    return challenges
