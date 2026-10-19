"""
Frontend Studio: Hard Challenges (111 to 120)
"""

def get_frontend_hard():
    challenges = []

    # 111. Concurrent frontend requests create inconsistent checkout state
    challenges.append({
        'id': 111,
        'title': '[FE-H01] Concurrent Frontend Requests Create Inconsistent Checkout State',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Concurrency',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A high-volume ticket sales portal allows users to purchase concert tickets.

### Bug Report
During flash sales, customers click "Checkout" while background cart inventory verification is still in flight. Because there is no atomic state lock or mutex, two concurrent checkout requests are dispatched with the same cart items, creating duplicate bookings and split billing charges.

### Steps to Reproduce
1. In `CheckoutFlow.jsx`, click Checkout.
2. Trigger a second checkout action before the first returns.
3. Both proceed because state transition is not locked atomically.

### Expected Behavior
A checkout mutex/lock (`isProcessing` state or ref) must prevent any subsequent checkout attempt until the current one finishes or fails.

### Actual Behavior
Component allows overlapping checkout invocations, creating duplicate transactions.

### Impact
Overbooking of allocated seats and severe financial reconciliation overhead.

### Requirements
- Implement an execution guard or atomic lock to block concurrent overlapping checkout requests.
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
            {'id': 1, 'name': 'Visible: Guards against concurrent checkout with processing lock', 'input': '', 'expected': "status === 'processing'"}
        ],
        'bug_signature': 'const handleCheckout = async () => {\n    setStatus(\'processing\');',
        'suspected_component': 'CheckoutFlow.jsx',
        'ai_suggestions': [
            'Add `if (status === "processing") return;` or use a ref lock at the top of `handleCheckout` and disable the button while processing.'
        ],
        'topics': ['React', 'Concurrency', 'State Machine', 'E-commerce'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React State Management', 'Asynchronous Locks'],
        'status': 'published'
    })

    # 112. Memory leak develops after repeated mount/unmount cycles
    challenges.append({
        'id': 112,
        'title': '[FE-H02] Memory Leak Develops After Repeated Mount/Unmount Cycles',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Memory Management',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A financial trading platform streams real-time cryptocurrency price updates into dashboard widgets.

### Bug Report
When users switch between different coin tabs, browser memory continuously increases until the tab crashes with an "Out of Memory" error. The React DevTools console also outputs warnings: `"Can't perform a React state update on an unmounted component"`.

### Steps to Reproduce
1. In `SubscriptionWidget.jsx`, `eventBus.subscribe(symbol, handleTick)` is called in `useEffect`.
2. When the user navigates away, the component unmounts.
3. No unsubscribe callback is registered. The event bus keeps a reference to `handleTick`, retaining the unmounted component in memory indefinitely.

### Expected Behavior
The `useEffect` hook must return a cleanup function: `return () => eventBus.unsubscribe(symbol, handleTick);`.

### Actual Behavior
Omits the unsubscribe call, creating a permanent memory leak and zombie callback listeners.

### Impact
Browser tab crashes on prolonged usage; multiple zombie listeners fire simultaneously.

### Requirements
- Return a cleanup function from `useEffect` invoking `eventBus.unsubscribe(symbol, handleTick)`.
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
            {'id': 1, 'name': 'Visible: Cleans up subscription on unmount', 'input': '', 'expected': 'eventBus.unsubscribe'}
        ],
        'bug_signature': 'eventBus.subscribe(symbol, handleTick);\n  }, [symbol, eventBus]);',
        'suspected_component': 'SubscriptionWidget.jsx',
        'ai_suggestions': [
            'Return a cleanup function from `useEffect`: `return () => eventBus.unsubscribe(symbol, handleTick);`.'
        ],
        'topics': ['React', 'Memory Leaks', 'useEffect Cleanup', 'Event Bus'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Lifecycle', 'Memory Management'],
        'status': 'published'
    })

    # 113. Shared client-side cache exposes data between authenticated sessions
    challenges.append({
        'id': 113,
        'title': '[FE-H03] Shared Client-Side Cache Exposes Data Between Sessions',
        'difficulty': 'Hard',
        'technology': 'JavaScript',
        'category': 'Security',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A hospital kiosk workstation allows doctors and nurses to access confidential patient health records.

### Bug Report
Nurse Sarah logs into the kiosk, reviews Patient X's records, and clicks "Log Out". When Doctor Robert logs in next on the same workstation, the app reads from the client-side session cache before network validation completes, displaying Patient X's confidential records under Doctor Robert's session!

### Steps to Reproduce
1. In `SessionCache.jsx`, inspect the `logoutUser` implementation.
2. `logoutUser` calls `authApi.logout()` and clears local tokens, but fails to invoke `sessionCache.clear()`.
3. Subsequent logins reuse cached records belonging to the prior user.

### Expected Behavior
`logoutUser` must purge the client-side `sessionCache` completely (`sessionCache.clear()`) to prevent data leakage across sessions.

### Actual Behavior
Cached data remains in memory across different user sessions.

### Impact
Critical HIPAA / privacy violation exposing patient medical data across user boundaries.

### Requirements
- Call `sessionCache.clear()` inside `logoutUser`.
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
            {'id': 1, 'name': 'Visible: Clears sessionCache on logout', 'input': '', 'expected': 'sessionCache.clear()'}
        ],
        'bug_signature': 'localStorage.removeItem(\'authToken\');\n    // BUG: Leaves sensitive records in sessionCache across user logout',
        'suspected_component': 'SessionCache.jsx',
        'ai_suggestions': [
            'Add `sessionCache.clear();` inside `logoutUser`.'
        ],
        'topics': ['React', 'Security', 'Caching', 'Authentication'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Web Security', 'Session Management'],
        'status': 'published'
    })

    # 114. Optimistic UI update corrupts state after overlapping failed requests
    challenges.append({
        'id': 114,
        'title': '[FE-H04] Optimistic UI Update Corrupts State After Failed Requests',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Optimistic UI',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A social media platform uses optimistic UI updates to instantly toggle "Like" counts.

### Bug Report
A user clicks "Like" twice quickly under poor network conditions. The first request fails on the server. The rollback logic blindly subtracts 1 from the *current* count, but because the user had already clicked again, the like count drops below zero (`likes: -1`), permanently corrupting the counter.

### Steps to Reproduce
1. In `OptimisticFeed.jsx`, click like.
2. State is optimistically incremented: `setLikes(likes + 1)`.
3. Server returns an error. The catch block blindly calls `setLikes(likes - 1)` or decrements from stale closure, corrupting the counter.

### Expected Behavior
Capture a snapshot of the previous state before the optimistic mutation, and revert to that exact snapshot if the request fails.

### Actual Behavior
Reverts by subtracting from a stale or mutated counter value.

### Impact
Incorrect like counters and desynchronized like states across users.

### Requirements
- Snapshot previous state prior to optimistic updates and revert accurately to the snapshot if the network request fails.
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
            {'id': 1, 'name': 'Visible: Captures previousLikes snapshot and restores on error', 'input': '', 'expected': 'previousLikes'}
        ],
        'bug_signature': 'setLikes(likes + 1);\n    setIsLiked(true);\n\n    try {\n      await api.likePost();\n    } catch (err) {\n      setLikes(likes - 1);',
        'suspected_component': 'OptimisticFeed.jsx',
        'ai_suggestions': [
            'Store `const previousLikes = likes;` and `const previousIsLiked = isLiked;` before the async call.',
            'In the catch block, restore `setLikes(previousLikes); setIsLiked(previousIsLiked);`.'
        ],
        'topics': ['React', 'Optimistic UI', 'State Snapshots'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Asynchronous State', 'Optimistic Updates'],
        'status': 'published'
    })

    # 115. Complex dashboard produces inconsistent derived state
    challenges.append({
        'id': 115,
        'title': '[FE-H05] Complex Dashboard Produces Inconsistent Derived State',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Performance & Memoization',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
An executive KPI dashboard computes Monthly Recurring Revenue (MRR) and Average Revenue Per User (ARPU) based on transactions and active tier filter.

### Bug Report
When an executive switches the tier filter from "Enterprise" to "Starter", the transaction table updates, but the KPI Summary cards continue to display Enterprise MRR! Profiling shows `useMemo` closed over an empty dependency array `[]`.

### Steps to Reproduce
1. In `AnalyticsHub.jsx`, view the `mrr` computation.
2. `useMemo` is declared with `[]` instead of `[transactions, tierFilter]`.
3. Changing filters does not recalculate the summary metrics.

### Expected Behavior
`useMemo` must include `[transactions, tierFilter]` in its dependencies so derived metrics update when data or filters change.

### Actual Behavior
Derived metrics stay frozen on initial calculation due to missing dependencies.

### Impact
Executives make strategic pricing decisions based on incorrect and outdated metrics.

### Requirements
- Add `[transactions, tierFilter]` to the `useMemo` dependency array.
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
            {'id': 1, 'name': 'Visible: Includes transactions and tierFilter in useMemo dependencies', 'input': '', 'expected': '[transactions, tierFilter]'}
        ],
        'bug_signature': 'return { totalMRR, avgMRR, count: filtered.length };\n  }, []);',
        'suspected_component': 'AnalyticsHub.jsx',
        'ai_suggestions': [
            'Update the dependency array of `useMemo` from `[]` to `[transactions, tierFilter]`.'
        ],
        'topics': ['React', 'useMemo', 'Derived State', 'Performance'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Memoization'],
        'status': 'published'
    })

    # 116. Frontend authentication flow mishandles token expiration & concurrent refreshes
    challenges.append({
        'id': 116,
        'title': '[FE-H06] Concurrent API Calls Trigger Multiple Token Refreshes',
        'difficulty': 'Hard',
        'technology': 'JavaScript',
        'category': 'Authentication Architecture',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A Single Page Application initiates multiple parallel API calls when loading the dashboard (user profile, notifications, metrics, and alerts).

### Bug Report
When the user's access token expires, all 4 concurrent requests return 401 Unauthorized simultaneously. Each response interceptor independently calls `refreshTokenApi()`. The backend implements refresh token rotation (one-time use per refresh token). The first refresh succeeds, but the subsequent 3 requests arrive with the now-invalidated old refresh token, causing the backend to flag a replay attack and terminate the user's session!

### Steps to Reproduce
1. In `AuthManager.jsx`, four concurrent requests fail with 401.
2. `refreshToken()` is executed 4 separate times instead of reusing a single in-flight refresh promise.
3. User gets abruptly logged out.

### Expected Behavior
Implement refresh token deduplication: if a refresh is already in flight, all subsequent 401 interceptors must await the same shared promise (`refreshPromise`).

### Actual Behavior
Fires uncoordinated parallel refresh requests.

### Impact
Users get randomly logged out whenever tokens expire during dashboard navigation.

### Requirements
- Share an in-flight token refresh promise across concurrent requests to avoid duplicate refresh calls.
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
            {'id': 1, 'name': 'Visible: Shares single in-flight refreshPromise across calls', 'input': '', 'expected': 'refreshPromise'}
        ],
        'bug_signature': 'if (err.status === 401) {\n      const newTokens = await refreshApi();',
        'suspected_component': 'AuthManager.jsx',
        'ai_suggestions': [
            'Check `if (!refreshPromise) { refreshPromise = refreshApi().finally(() => { refreshPromise = null; }); }` and `await refreshPromise;`.'
        ],
        'topics': ['JavaScript', 'Authentication', 'Token Refresh', 'Concurrency'],
        'skills_tested': ['JavaScript', 'Frontend Architecture'],
        'prerequisites': ['JWT Architecture', 'Promise Chaining'],
        'status': 'published'
    })

    # 117. Virtualized list renders incorrect items after filtering and reordering
    challenges.append({
        'id': 117,
        'title': '[FE-H07] Virtualized List Renders Incorrect Items After Filtering',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Virtualization',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A server log monitoring tool uses a virtualized list to render 50,000 log lines with high performance.

### Bug Report
When filtering logs from "ALL" to "ERROR", log messages from other levels stay visible in the viewport or jump to wrong rows. Inspecting the DOM reveals the virtual list mapped array index `index` as the React `key`, confusing React's reconciliation engine.

### Steps to Reproduce
1. In `VirtualList.jsx`, inspect the rendered rows.
2. The virtual slice maps items using `key={startIndex + index}` instead of unique entity id `item.id`.
3. Filter or reorder items; DOM node recycling displays incorrect contents.

### Expected Behavior
Rows must be keyed by stable unique entity identifier: `key={item.id}`.

### Actual Behavior
Uses calculated row index as key.

### Impact
Engineers read wrong error timestamps and corrupted stack traces during production outages.

### Requirements
- Ensure virtualized list items use unique stable entity keys rather than computed window offsets.
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
            {'id': 1, 'name': 'Visible: Uses stable item.id for virtualized row key', 'input': '', 'expected': 'key={item.id}'}
        ],
        'bug_signature': 'key={startIndex + index}',
        'suspected_component': 'VirtualList.jsx',
        'ai_suggestions': [
            'Ensure virtualized list items use unique stable entity keys rather than computed window offsets.'
        ],
        'topics': ['React', 'Virtualization', 'Keys', 'Reconciliation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['DOM Virtualization', 'React Keys'],
        'status': 'published'
    })

    # 118. Multi-step checkout loses consistency when requests fail partway through
    challenges.append({
        'id': 118,
        'title': '[FE-H08] Multi-Step Checkout Loses Consistency on Partial Failure',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Compensating Transactions',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
An airline ticket booking engine executes two sequential transactions:
1. `reserveSeat(flightId, seatNumber)` - holds seat for 10 minutes.
2. `processPayment(paymentDetails)` - charges credit card.

### Bug Report
If the credit card fails (e.g. insufficient funds), the checkout displays an error, but never releases the held seat (`releaseSeat(reservationId)`). The seat remains locked for 10 minutes, preventing the passenger from retrying with another card and blocking other customers from booking that seat.

### Steps to Reproduce
1. In `MultiStepCheckout.jsx`, simulate payment failure after seat reservation succeeds.
2. In the catch block, error message is set, but no compensating rollback request is sent to release the reserved seat.

### Expected Behavior
If step 2 fails, invoke compensating rollback `await api.releaseSeat(reservation.id)` before showing the error.

### Actual Behavior
Leaves reserved inventory orphaned and locked in the backend.

### Impact
Lost flight bookings and stranded seat reservations.

### Requirements
- Call `await api.releaseSeat(reservation.id)` in the catch block if `reservation` exists.
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
            {'id': 1, 'name': 'Visible: Releases reserved seat on payment failure', 'input': '', 'expected': 'api.releaseSeat'}
        ],
        'bug_signature': '} catch (err) {\n      setError(err.message || \'Payment failed\');',
        'suspected_component': 'MultiStepCheckout.jsx',
        'ai_suggestions': [
            'Inside `catch (err)`, check `if (reservation) { await api.releaseSeat(reservation.id); }` before setting error.'
        ],
        'topics': ['React', 'Compensating Transactions', 'Error Recovery'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Distributed Consistency', 'Compensating Actions'],
        'status': 'published'
    })

    # 119. Real-time interface applies out-of-order events and displays stale state
    challenges.append({
        'id': 119,
        'title': '[FE-H09] Real-Time Interface Applies Out-Of-Order Events',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Real-Time State',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A collaborative live document editor receives character edit events over WebSockets from multiple peers.

### Bug Report
Under spotty cellular network connections, packets arrive out of sequence. An older event packet with `seq: 14` arrives after a newer packet with `seq: 15`. The editor blindly sets document content from the arriving payload, reverting recent changes and causing text to jump backwards.

### Steps to Reproduce
1. In `RealtimeChat.jsx`, notice `handleIncomingMessage(event)`.
2. Component receives `event = { seq: 15, text: "Hello World" }`, then later receives delayed `event = { seq: 14, text: "Hello" }`.
3. The editor renders "Hello", overwriting newer text.

### Expected Behavior
Maintain a sequence tracker (`lastSeqRef.current`). Ignore any incoming event where `event.seq <= lastSeqRef.current`.

### Actual Behavior
Applies all incoming events regardless of sequence numbers.

### Impact
Content loss and confusing cursor jumping during collaborative editing sessions.

### Requirements
- Track `lastSeqRef` and discard packets if `event.seq <= lastSeqRef.current`.
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
            {'id': 1, 'name': 'Visible: Rejects out-of-order events using sequence comparison', 'input': '', 'expected': 'event.seq <'}
        ],
        'bug_signature': 'const handleIncomingMessage = (event) => {\n      setContent(event.text);',
        'suspected_component': 'RealtimeChat.jsx',
        'ai_suggestions': [
            'Add check `if (event.seq <= lastSeq.current) return;` before updating content.'
        ],
        'topics': ['React', 'WebSockets', 'Sequence Numbers', 'Event Ordering'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Real-time Systems', 'Network Jitter'],
        'status': 'published'
    })

    # 120. Frontend permission check hides a control but fails on unauthorized responses
    challenges.append({
        'id': 120,
        'title': '[FE-H10] Frontend Fails to Gracefully Handle 403 Forbidden Responses',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Security & Error Handling',
        'time_estimate': '20 mins',
        'points': 300,
        'description': """### Company Scenario
A multi-tenant enterprise administration dashboard manages user permissions.

### Bug Report
If an organization's billing plan expires or an admin's session permissions are revoked in another tab, clicking "Delete Account" returns HTTP 403 Forbidden. Because `handleDelete` lacks a catch handler for 403, an uncaught rejection bubbles up, triggering React's unhandled rejection boundary and crashing the entire application into a blank white screen!

### Steps to Reproduce
1. In `AdminPanel.jsx`, trigger `handleDelete`.
2. Mock an HTTP 403 response (`{ status: 403, message: "Forbidden" }`).
3. Application crashes with unhandled promise error instead of showing an access-denied toast.

### Expected Behavior
Catch the error, check `err.status === 403`, and set `setErrorMessage("Access Denied: You do not have permission to perform this action.")` while keeping the interface intact.

### Actual Behavior
Unhandled error crashes the page.

### Impact
Total UI crash forcing users to perform a hard refresh and lose unsaved workspace data.

### Requirements
- Wrap `api.deleteAccount()` in `try/catch` and gracefully handle 403 status with appropriate user feedback.
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
            {'id': 1, 'name': 'Visible: Handles 403 Forbidden with try/catch and error message', 'input': '', 'expected': 'try {'}
        ],
        'bug_signature': 'const handleDelete = async () => {\n    setIsDeleting(true);\n    setErrorMessage(\'\');\n    await api.deleteAccount(user.id);\n    setIsDeleting(false);\n  };',
        'suspected_component': 'AdminPanel.jsx',
        'ai_suggestions': [
            'Wrap `await api.deleteAccount(user.id)` in a `try...catch` block.',
            'In the `catch (err)`, check `if (err.status === 403) setErrorMessage("Access Denied");`.'
        ],
        'topics': ['React', 'Security', 'Error Boundaries', 'HTTP 403'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['HTTP Error Codes', 'Error Resilience'],
        'status': 'published'
    })

    return challenges
