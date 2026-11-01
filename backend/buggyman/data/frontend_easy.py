"""
Frontend Studio: Easy Challenges (86 to 95)
Standardized into realistic production incident debugging tickets.
"""

def get_frontend_easy():
    challenges = []

    # 86. A form submits even when required fields are empty
    challenges.append({
        'id': 86,
        'title': 'Registration Form Submits With Blank Account Fields',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Forms',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Customer support reported that newly signed-up user accounts were appearing in the administration console with blank names and corrupted profile records. Backend telemetry showed a surge of HTTP 400 Bad Request errors originating from the new registration page whenever prospective users clicked submit before entering their details.

### Bug Report
In `RegistrationForm.jsx`, the form submission handler invokes `onSubmit` immediately without validating whether the required name input contains non-whitespace characters. An empty string payload is dispatched to the backend service.

### Steps to Reproduce
1. Render `RegistrationForm.jsx` in the browser or test suite.
2. Leave the name input field completely empty (or whitespace only).
3. Click the "Register" submit button.
4. Observe that `onSubmit` fires with `{ name: '' }` and no validation error is displayed.

### Expected Behaviour
If the user attempts to submit without entering a name, submission must be halted, `onSubmit` must not be invoked, and the validation error message `"Name is required"` must be displayed.

### Actual Behaviour
The form dispatches empty values unconditionally without client-side verification.

### Starter Files
- `RegistrationForm.jsx`: Controlled React form component with unvalidated submission handler.

### Task
Refactor `handleSubmit` in `RegistrationForm.jsx` to validate input presence, blocking submissions that contain only whitespace and displaying 'Name is required'.

### Acceptance Criteria
1. Submissions containing empty or whitespace-only names are prevented.
2. An error message 'Name is required' is displayed when attempting to submit blank inputs.
3. Valid non-empty names invoke the submission callback.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
""",
        'files': [{
            'name': 'RegistrationForm.jsx',
            'content': '''import React, { useState } from 'react';

export default function RegistrationForm({ onSubmit }) {
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ name });
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-3">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter your name"
        className="border p-2 rounded"
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
        Register
      </button>
    </form>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Validates empty name before submission', 'input': '', 'expected': '!name.trim()'}
        ],
        'bug_signature': '',
        'suspected_component': 'RegistrationForm.jsx',
        'ai_suggestions': [
            'Client forms should validate required fields before dispatching API requests or parent callbacks.',
            'Inspect `handleSubmit`: check whether `name` contains non-whitespace characters before executing `onSubmit`.',
            'Add a condition `if (!name.trim()) { setError(\'Name is required\'); return; }` prior to calling `onSubmit`.'
        ],
        'topics': ['React', 'Forms', 'Validation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Form Handling'],
        'status': 'published'
    })

    # 87. A React component displays stale or incorrect conditional content
    challenges.append({
        'id': 87,
        'title': 'Stock Availability Banner Renders Raw Zero on Depleted Inventory',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Conditional Rendering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Shoppers browsing the online store alerted support that product catalog items with zero remaining stock were displaying a raw "0" character directly on the page instead of the styled "Sold Out" badge. The visual glitch distorted the product card layout and created confusion about product availability.

### Bug Report
In `Banner.jsx`, the component uses the logical AND operator `{stock && <span className="in-stock">...</span>}` for conditional rendering. In JavaScript, `0 && <Component />` evaluates to the falsy number `0`, which React renders as a literal text node rather than omitting it.

### Steps to Reproduce
1. Pass `stock = 0` as a prop to `StockBanner` in `Banner.jsx`.
2. Inspect the rendered DOM container.
3. Observe that the character `"0"` is displayed alongside or in place of the expected badge.

### Expected Behaviour
When `stock` is greater than 0, render `<span className="in-stock">In Stock ({stock})</span>`. When `stock` is 0 or less, render `<span className="sold-out">Sold Out</span>`.

### Actual Behaviour
The expression evaluates to numeric `0`, which React displays as raw text on screen.

### Starter Files
- `Banner.jsx`: Component using numeric short-circuit evaluation in JSX.

### Task
Refactor the conditional rendering in `Banner.jsx` using an explicit numeric comparison (such as a ternary `stock > 0 ? ... : ...`) so that numeric zero is never rendered as raw text.

### Acceptance Criteria
1. When `stock > 0`, the in-stock badge with item count is rendered.
2. When `stock <= 0`, the sold-out badge is rendered.
3. No raw number "0" is outputted to the DOM.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'Banner.jsx',
            'content': '''import React from 'react';

export default function StockBanner({ stock }) {
  return (
    <div className="stock-container">
      {stock && <span className="in-stock">In Stock ({stock})</span>}
      {!stock && <span className="sold-out">Sold Out</span>}
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Uses explicit numeric comparison stock > 0', 'input': '', 'expected': 'stock > 0'}
        ],
        'bug_signature': '{stock && <span className="in-stock">',
        'suspected_component': 'Banner.jsx',
        'ai_suggestions': [
            'In JavaScript JSX, numeric expressions like `0 && <Tag />` evaluate to the number `0`, which React renders as text.',
            'Avoid relying on short-circuit evaluation with numbers in JSX when the number can be zero.',
            'Use an explicit comparison or ternary: `{stock > 0 ? <span className="in-stock">...</span> : <span className="sold-out">...</span>}`.'
        ],
        'topics': ['React', 'Conditional Rendering', 'JSX'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JSX Expressions'],
        'status': 'published'
    })

    # 88. A product card shows the wrong price after a state update
    challenges.append({
        'id': 88,
        'title': 'Cart Item Card Total Price Fails to Refresh on Quantity Change',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'React State',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Shoppers reported an irritating lag when adjusting item quantities in their order summary. When clicking the `+` button to increment quantity from 1 to 2, the displayed total price remained at the 1-item price. Only on the subsequent click did it reflect the previous quantity, leaving the displayed total consistently one step out of sync.

### Bug Report
In `ProductCard.jsx`, the component maintains redundant state `totalPrice` alongside `quantity`. In the increment handler, `setTotalPrice(price * quantity)` reads `quantity` synchronously right after `setQuantity(...)`. Because React state updates are scheduled asynchronously, `quantity` holds its old value at calculation time.

### Steps to Reproduce
1. Render `ProductCard.jsx` with `price = 25`.
2. Click the `+` increment button once (quantity becomes 2).
3. Observe that Total still displays `$25` instead of `$50`.

### Expected Behaviour
The total price must update immediately in lockstep with the quantity, always displaying `price * quantity`.

### Actual Behaviour
The component reads stale state synchronously during the event handler, causing redundant state desynchronization.

### Starter Files
- `ProductCard.jsx`: Card component storing both `quantity` and redundant `totalPrice` in local state.

### Task
Refactor `ProductCard.jsx` to remove the redundant `totalPrice` state variable and derive total price directly during render (`price * quantity`).

### Acceptance Criteria
1. Total price computes directly from current price and quantity.
2. Modifying quantity immediately updates the displayed total amount.
3. State remains unified without out-of-sync intermediate values.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.
""",
        'files': [{
            'name': 'ProductCard.jsx',
            'content': '''import React, { useState } from 'react';

export default function ProductCard({ price = 25 }) {
  const [quantity, setQuantity] = useState(1);
  const [totalPrice, setTotalPrice] = useState(price);

  const handleIncrement = () => {
    setQuantity(quantity + 1);
    setTotalPrice(price * quantity);
  };

  return (
    <div className="card p-4 border rounded">
      <p>Unit Price: ${price}</p>
      <p>Quantity: {quantity}</p>
      <button onClick={handleIncrement} className="btn-add">+</button>
      <p className="total">Total: ${totalPrice}</p>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Total price derived cleanly from quantity', 'input': '', 'expected': 'price * quantity'}
        ],
        'bug_signature': 'setTotalPrice(price * quantity);',
        'suspected_component': 'ProductCard.jsx',
        'ai_suggestions': [
            'Avoid storing values in state that can be derived directly from existing props or state during render.',
            'React state setter calls do not update variables immediately within the same synchronous event cycle.',
            'Remove the `totalPrice` state and calculate `const totalPrice = price * quantity;` directly in the component body.'
        ],
        'topics': ['React', 'State', 'Derived State'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React useState'],
        'status': 'published'
    })

    # 89. A button fires the wrong event handler
    challenges.append({
        'id': 89,
        'title': 'Save Draft Toolbar Button Inadvertently Deletes Active Document',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'DOM & Events',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
A critical severity ticket was logged after several content creators lost hours of work. When users clicked the green "Save" button in the document toolbar to preserve their drafts, the document disappeared from their workspace and was permanently deleted from the database.

### Bug Report
In `ActionButton.jsx`, a copy-paste error caused the "Save" button to bind `onClick={onDelete}` instead of `onClick={onSave}`. As a result, clicking Save executes the document deletion callback.

### Steps to Reproduce
1. Render `ActionButton.jsx` with mock callbacks for `onSave` and `onDelete`.
2. Click the "Save" button.
3. Observe that `onDelete` is invoked instead of `onSave`.

### Expected Behaviour
Clicking the "Save" button must trigger the `onSave` handler. The "Delete" button should trigger `onDelete`.

### Actual Behaviour
The "Save" button is mistakenly wired to the destructive `onDelete` handler.

### Starter Files
- `ActionButton.jsx`: Toolbar component with inverted event handler binding.

### Task
Inspect `ActionButton.jsx` and rebind the Save button's click handler so that it executes `onSave`.

### Acceptance Criteria
1. The "Save" button has `onClick={onSave}`.
2. The "Delete" button maintains `onClick={onDelete}`.
3. Clicking Save executes only `onSave`.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.
""",
        'files': [{
            'name': 'ActionButton.jsx',
            'content': '''import React from 'react';

export default function ActionToolbar({ onSave, onDelete }) {
  return (
    <div className="flex gap-2">
<button onClick={onDelete} className="bg-emerald-600 text-white px-3 py-1 rounded">
        Save
      </button>
      <button onClick={onDelete} className="bg-rose-600 text-white px-3 py-1 rounded">
        Delete
      </button>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Save button triggers onSave', 'input': '', 'expected': 'onClick={onSave}'}
        ],
        'bug_signature': '<button onClick={onDelete} className="bg-emerald-600',
        'suspected_component': 'ActionButton.jsx',
        'ai_suggestions': [
            'Check event callback bindings to ensure user actions trigger their intended handlers.',
            'Review the `onClick` prop passed to the Save button.',
            'Change `onClick={onDelete}` on the Save button to `onClick={onSave}`.'
        ],
        'topics': ['React', 'Events', 'Event Handlers'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Event Binding in React'],
        'status': 'published'
    })

    # 90. A search field ignores uppercase/lowercase normalization
    challenges.append({
        'id': 90,
        'title': 'Employee Directory Filter Excludes Names on Mixed-Case Queries',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Validation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Employees looking up colleagues in the company staff directory complained that search was broken. Typing lowercase names like `"alice"` or uppercase abbreviations returned zero results, even when employee records such as `"Alice Smith"` were clearly listed on the page.

### Bug Report
In `SearchBar.jsx`, the filtering predicate uses standard JavaScript `item.name.includes(query)`. Because `.includes()` performs strict case-sensitive character comparisons, any difference in casing between query input and stored records produces false negatives.

### Steps to Reproduce
1. Render `SearchBar.jsx` with an employee list containing `"Alice"`.
2. Type `"alice"` into the search input.
3. Notice that the employee list renders empty.

### Expected Behaviour
Search matching must be case-insensitive, allowing users to find records regardless of whether they type in uppercase, lowercase, or mixed case.

### Actual Behaviour
The search filter requires exact casing match, discarding valid matches.

### Starter Files
- `SearchBar.jsx`: Search filter component performing case-sensitive substring matching.

### Task
Update search filtering in `SearchBar.jsx` so that matching operates in a case-insensitive manner.

### Acceptance Criteria
1. Searches match names regardless of upper or lowercase query input.
2. Submitting uppercase, lowercase, or mixed-case queries returns all matching records.
3. Filtered results update accurately in the component.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
""",
        'files': [{
            'name': 'SearchBar.jsx',
            'content': '''import React, { useState } from 'react';

export default function SearchBar({ items = [] }) {
  const [query, setQuery] = useState('');

  const filtered = items.filter(item => item.name.includes(query));

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search employees..."
      />
      <ul>
        {filtered.map(item => <li key={item.id}>{item.name}</li>)}
      </ul>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Case-insensitive search using toLowerCase', 'input': '', 'expected': 'toLowerCase()'}
        ],
        'bug_signature': 'item.name.includes(query)',
        'suspected_component': 'SearchBar.jsx',
        'ai_suggestions': [
            'User-facing text searches should be case-insensitive to ensure reliable discovery.',
            'Normalize both the source text and the search query before performing substring checks.',
            'Update the filter predicate to: `item.name.toLowerCase().includes(query.toLowerCase())`.'
        ],
        'topics': ['React', 'Search', 'Normalization'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['String Methods in JavaScript'],
        'status': 'published'
    })

    # 91. A loading indicator never disappears after an API error
    challenges.append({
        'id': 91,
        'title': 'Telemetry Viewer Leaves Loading Spinner Trapped on API Error',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'React State',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Monitoring team operators noted that when upstream telemetry APIs suffered transient 500 errors, the metric viewer dashboard remained stuck on an infinite spinning loading animation. Operators were unable to see the actual error notification or retry the action without manually reloading the entire browser tab.

### Bug Report
In `DataViewer.jsx`, the asynchronous fetch chain handles errors in `.catch()`, updating `setError(err.message)`. However, it neglects to call `setLoading(false)`. Because `loading` remains `true` and the render check prioritizes `if (loading) return <Spinner />`, the error message is never displayed.

### Steps to Reproduce
1. Render `DataViewer.jsx` with a `fetchFn` that rejects with an error.
2. Wait for the rejected Promise to complete.
3. Observe that the loading spinner remains visible indefinitely while the error message is hidden.

### Expected Behaviour
When an API error occurs, `loading` must be set to `false` and the error message must be presented to the user.

### Actual Behaviour
When a network or server error occurs, the loading indicator remains active indefinitely, preventing the error message from displaying.

### Starter Files
- `DataViewer.jsx`: Async data display component with incomplete error state handling.

### Task
Update error handling in `DataViewer.jsx` so that the loading indicator is dismissed when an error occurs.

### Acceptance Criteria
1. Network or server errors terminate the loading indicator.
2. The error message is rendered clearly when requests fail.
3. Successful requests continue to load data correctly.

### Constraints
- Framework: React 18 / Tailwind CSS.
- State transitions must be strictly immutable; array mutations and in-place object property assignments are prohibited.
- Rendered list items must use stable entity identifiers as keys rather than transient array indices.
- Dependent state values must remain synchronized without stale closures or intermediate rendering lag.
""",
        'files': [{
            'name': 'DataViewer.jsx',
            'content': '''import React, { useState, useEffect } from 'react';

export default function DataViewer({ fetchFn }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFn()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
      });
  }, [fetchFn]);

  if (loading) return <div className="spinner">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  return <div>Data Loaded: {JSON.stringify(data)}</div>;
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Loading set to false on catch', 'input': '', 'expected': 'setLoading(false)'}
        ],
        'bug_signature': 'setError(err.message);\n      });',
        'suspected_component': 'DataViewer.jsx',
        'ai_suggestions': [
            'Asynchronous operations must reset loading state in both success and error outcomes.',
            'Look at the `.catch(err => { ... })` block in the `useEffect` hook.',
            'Add `setLoading(false);` within the catch handler alongside `setError(err.message)`.'
        ],
        'topics': ['React', 'Async', 'Loading States'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Promises in React'],
        'status': 'published'
    })

    # 92. A responsive layout overflows on mobile
    challenges.append({
        'id': 92,
        'title': 'Product Detail Card Causes Horizontal Overflow on Mobile Screens',
        'difficulty': 'Easy',
        'technology': 'CSS',
        'category': 'CSS & Styling',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Mobile e-commerce shoppers reported that product detail pages were distorted on smartphones. The product card spilled outside the device viewport, triggering an annoying horizontal scroll bar, hiding right-hand buttons, and failing Google Mobile-Friendly usability checks.

### Bug Report
In `ResponsiveCard.css`, the `.product-card` class declares a fixed width `width: 600px;`. On screens narrower than 600px (such as standard 375px mobile displays), the fixed pixel width forces the container to overflow the viewport boundaries.

### Steps to Reproduce
1. View the component on a mobile viewport (e.g., width 375px).
2. Inspect the computed styles on `.product-card`.
3. Notice the card extends 225px beyond the screen edge, creating horizontal overflow.

### Expected Behaviour
The container should fluidly adapt to narrower screens while maintaining a maximum width of 600px on larger desktop viewports.

### Actual Behaviour
The card specifies a rigid `width: 600px;` regardless of screen dimensions.

### Starter Files
- `ResponsiveCard.css`: Stylesheet containing rigid fixed width styling.

### Task
Replace the fixed `width: 600px;` property in `ResponsiveCard.css` with responsive sizing using `max-width: 600px;` and `width: 100%;` (or fluid width constraints).

### Acceptance Criteria
1. The `.product-card` style uses `max-width: 600px;` instead of fixed `width: 600px;`.
2. The component fits cleanly inside narrow mobile viewports without horizontal scrolling.
3. Desktop layout maintains optimal reading width up to 600px.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Asynchronous responses arriving out of order must not overwrite fresher active search results.
- Partial API endpoint rejections must be handled gracefully without collapsing sibling operational widgets.
- Shared token refresh promises and user logout session caches must prevent cross-tenant credential leakage.
- Optimistic updates must restore the pre-action state snapshot accurately upon server rejection.
""",
        'files': [{
            'name': 'ResponsiveCard.css',
            'content': '''.product-card {
    width: 600px;
    padding: 24px;
    background: #ffffff;
    border-radius: 8px;
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Uses max-width for responsive scaling', 'input': '', 'expected': 'max-width'}
        ],
        'bug_signature': 'product-card {\n    width: 600px;',
        'suspected_component': 'ResponsiveCard.css',
        'ai_suggestions': [
            'Fixed pixel widths on container elements frequently cause horizontal overflow on mobile viewports.',
            'Use responsive constraints that allow containers to shrink to 100% of the available viewport width.',
            'Replace `width: 600px;` with `max-width: 600px; width: 100%;`.'
        ],
        'topics': ['CSS', 'Responsive Design', 'Mobile'],
        'skills_tested': ['CSS', 'Frontend'],
        'prerequisites': ['CSS Box Model'],
        'status': 'published'
    })

    # 93. A form displays an incorrect validation message
    challenges.append({
        'id': 93,
        'title': 'Newsletter Form Displays Password Error on Invalid Email',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Validation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Marketing noticed a high drop-off rate on the email newsletter subscription box. Users who mistyped their email address submitted feedback stating that the site complained their "password must be at least 8 characters", even though the newsletter widget has no password field whatsoever.

### Bug Report
In `EmailInput.jsx`, the validation function checks if `email.includes('@')`. When the check fails, `setError` is invoked with a copy-pasted string from a password component: `'Password must be at least 8 characters'`.

### Steps to Reproduce
1. Type `"johndoe"` (without `@`) into the input field in `EmailInput.jsx`.
2. Trigger the blur event by clicking outside the input.
3. Observe the confusing error message `'Password must be at least 8 characters'`.

### Expected Behaviour
When an invalid email address is entered, display a clear, contextually relevant error message: `'Please enter a valid email address.'`.

### Actual Behaviour
The component displays an irrelevant password length validation error.

### Starter Files
- `EmailInput.jsx`: Form input component with copy-paste validation message error.

### Task
Update `EmailInput.jsx` so that `setError` sets the message to `'Please enter a valid email address.'` when validation fails.

### Acceptance Criteria
1. The error message explicitly states `'Please enter a valid email address.'`.
2. Valid emails clear the error message.
3. The input properly notifies users of email syntax issues.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
""",
        'files': [{
            'name': 'EmailInput.jsx',
            'content': '''import React, { useState } from 'react';

export default function EmailInput() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const validate = () => {
    if (!email.includes('@')) {
      setError('Password must be at least 8 characters');
    } else {
      setError('');
    }
  };

  return (
    <div>
      <input value={email} onChange={e => setEmail(e.target.value)} onBlur={validate} />
      {error && <span className="error">{error}</span>}
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Displays valid email error message', 'input': '', 'expected': 'Please enter a valid email address.'}
        ],
        'bug_signature': "setError('Password must be at least 8 characters');",
        'suspected_component': 'EmailInput.jsx',
        'ai_suggestions': [
            'Form validation messages should accurately describe the field and the specific requirement that failed.',
            'Inspect the string passed to `setError(...)` inside the `validate` function.',
            'Replace the password error message with `setError(\'Please enter a valid email address.\');`.'
        ],
        'topics': ['React', 'Forms', 'Validation Messages'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Form Validation'],
        'status': 'published'
    })

    # 94. A modal cannot be closed using the Escape key
    challenges.append({
        'id': 94,
        'title': 'Confirmation Dialog Trap Ignores Escape Key Dismissal',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Accessibility',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
During a digital accessibility audit, the company was cited for non-compliance with WCAG 2.1 AA criteria. Power users and visually impaired individuals using keyboard-only navigation reported being trapped inside confirmation modals because pressing the standard Escape key failed to dismiss the dialog.

### Bug Report
In `Modal.jsx`, the modal attaches click handlers to its backdrop and close button, but registers no keyboard event listener for the Escape key on the window or document.

### Steps to Reproduce
1. Open the modal dialog by passing `isOpen = true`.
2. Press the Escape key on the physical keyboard.
3. Observe that the modal remains open and `onClose` is never invoked.

### Expected Behaviour
Pressing the Escape key (`e.key === 'Escape'`) while the modal is open must trigger `onClose()`.

### Actual Behaviour
The modal only closes via mouse clicks, ignoring keyboard dismissal.

### Starter Files
- `Modal.jsx`: Modal dialog component lacking keyboard event listeners.

### Task
Update `Modal.jsx` to support dismissing open modals when the user presses the Escape key, ensuring listeners are cleaned up when the modal closes.

### Acceptance Criteria
1. Pressing the Escape key triggers the modal close callback.
2. Event listeners are properly detached when the modal unmounts or closes.
3. Keyboard navigation operates consistently.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Global event listeners (`keydown`, `resize`, event bus subscriptions) must be detached in the `useEffect` cleanup return callback.
- Viewport layouts must scale responsively across mobile (`375px`) and desktop (`1440px`) breakpoints without horizontal overflow.
- Keyboard interactions (such as Escape key dismissal) must close open overlays reliably.
""",
        'files': [{
            'name': 'Modal.jsx',
            'content': '''import React, { useEffect } from 'react';

export default function Modal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} aria-label="Close">X</button>
        {children}
      </div>
    </div>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Attaches Escape key listener in useEffect', 'input': '', 'expected': 'Escape'}
        ],
        'bug_signature': '',
        'suspected_component': 'Modal.jsx',
        'ai_suggestions': [
            'Accessible modal dialogs must provide keyboard support for closing, specifically listening for the Escape key.',
            'Use a `useEffect` hook to attach a `keydown` listener to the global `window` object.',
            'Inside the listener, check `if (e.key === "Escape") onClose();` and return a cleanup function that calls `window.removeEventListener`.'
        ],
        'topics': ['React', 'Accessibility', 'Keyboard Events', 'WCAG'],
        'skills_tested': ['React', 'Frontend', 'Accessibility'],
        'prerequisites': ['Keyboard Listeners in React'],
        'status': 'published'
    })

    # 95. A list uses an unstable or incorrect React key, causing UI inconsistencies
    challenges.append({
        'id': 95,
        'title': 'Team Member List Reorders Input Focus and Checkbox State',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'DOM & Events',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Incident Report
Workspace administrators reported an alarming bug in the team management screen. When deleting an unwanted user from the top of the team list, checkbox selections, toggle states, and text input values from the deleted row jumped down onto the next team member, causing accidental permission changes.

### Bug Report
In `UserList.jsx`, the map iteration uses the array index as the React key: `<li key={index}>`. When an item is removed from the array, subsequent items shift indices, causing React's reconciliation engine to mistakenly preserve internal DOM state and form inputs across different entities.

### Steps to Reproduce
1. Render `UserList.jsx` with three team members.
2. Focus or modify an input associated with the first item (index 0).
3. Click "Delete" on the first item.
4. Observe that the second item inherits the DOM state of the deleted first item because index 0 was retained.

### Expected Behaviour
Each list item must use a permanent, unique entity identifier (`key={user.id}`) to guarantee accurate virtual DOM reconciliation during additions, removals, and reordering.

### Actual Behaviour
The component uses array positions as reconciliation keys, causing checkbox selections to shift to incorrect users when items are deleted.

### Starter Files
- `UserList.jsx`: List component mapping users with index-based keys.

### Task
Update `UserList.jsx` to use persistent unique item identifiers for list keys rather than array indices.

### Acceptance Criteria
1. List elements use unique stable entity identifiers for item keys.
2. Deleting an item preserves the checked state of remaining items.
3. Component identity remains stable across list reorder operations.

### Constraints
- Framework: React 18 / Tailwind CSS.
- Form submissions containing empty or whitespace-only inputs must be rejected with appropriate field errors.
- In-flight submissions must lock the submission trigger to prevent duplicate submissions.
- Inputs must maintain controlled component state across multi-step flows.
""",
        'files': [{
            'name': 'UserList.jsx',
            'content': '''import React from 'react';

export default function UserList({ users = [], onDelete }) {
  return (
    <ul>
{users.map((user, index) => (
        <li key={index} className="flex justify-between p-2">
          <span>{user.name}</span>
          <button onClick={() => onDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Uses stable user.id as key', 'input': '', 'expected': 'key={user.id}'}
        ],
        'bug_signature': '<li key={index}',
        'suspected_component': 'UserList.jsx',
        'ai_suggestions': [
            'Using array indices as React keys causes state bugs when items are reordered, filtered, or deleted.',
            'React keys must uniquely identify an item across renders so the diffing algorithm tracks the correct DOM node.',
            'Change `key={index}` to `key={user.id}` on the `<li>` element.'
        ],
        'topics': ['React', 'Keys', 'Reconciliation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Lists and Keys'],
        'status': 'published'
    })

    return challenges
