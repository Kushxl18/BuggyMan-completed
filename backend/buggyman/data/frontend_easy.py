"""
Frontend Studio: Easy Challenges (86 to 95)
"""

def get_frontend_easy():
    challenges = []

    # 86. A form submits even when required fields are empty
    challenges.append({
        'id': 86,
        'title': '[FE-E01] A Form Submits Even When Required Fields Are Empty',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Forms',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A SaaS onboarding registration form collects user name and organization.

### Bug Report
When a user clicks "Submit" without filling in their name, the form dispatches an API request with an empty payload, causing backend 400 Bad Request errors.

### Steps to Reproduce
1. Load `RegistrationForm.jsx`.
2. Leave `name` empty and click Submit.
3. Form dispatches `onSubmit` event without validating.

### Expected Behavior
`handleSubmit` must verify `name.trim().length > 0`. If empty, prevent submission and set `error = "Name is required"`.

### Actual Behavior
Submits unconditionally without validation.

### Impact
Server logs flooded with 400 bad request errors from incomplete registrations.

### Requirements
- Check `if (!name.trim()) { setError("Name is required"); return; }` before dispatching `onSubmit`.
""",
        'files': [{
            'name': 'RegistrationForm.jsx',
            'content': '''import React, { useState } from 'react';

export default function RegistrationForm({ onSubmit }) {
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // BUG: Missing check for empty name before calling onSubmit
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
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Validates empty name before submission', 'input': '', 'expected': '!name.trim()'}
        ],
        'bug_signature': '// BUG: Missing check for empty name before calling onSubmit\n    onSubmit({ name });',
        'suspected_component': 'RegistrationForm.jsx',
        'ai_suggestions': [
            'Add validation inside `handleSubmit`: `if (!name.trim()) { setError("Name is required"); return; }`.'
        ],
        'topics': ['React', 'Forms', 'Validation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Form Handling'],
        'status': 'published'
    })

    # 87. A React component displays stale or incorrect conditional content
    challenges.append({
        'id': 87,
        'title': '[FE-E02] A React Component Displays Stale or Incorrect Conditional Content',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Conditional Rendering',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An e-commerce banner component notifies users when an item is in stock vs sold out.

### Bug Report
When `item.stock` is `0`, the component displays `"0"` on screen instead of the `"Sold Out"` badge because of how JavaScript evaluates `0 && <Component />`!

### Steps to Reproduce
1. Pass `stock = 0` to `Banner.jsx`.
2. Notice React renders raw text number `0` on screen.

### Expected Behavior
Render `<span className="badge-soldout">Sold Out</span>` when stock is 0, or boolean ternary `stock > 0 ? ... : ...`.

### Actual Behavior
`stock && <span>In Stock</span>` evaluates to `0` and renders literal "0".

### Impact
Broken visual layout with raw digits rendered in place of status badges.

### Requirements
- Use explicit boolean condition `stock > 0 ? ... : ...` or `Boolean(stock) && ...`.
""",
        'files': [{
            'name': 'Banner.jsx',
            'content': '''import React from 'react';

export default function StockBanner({ stock }) {
  // BUG: Falsy 0 renders raw "0" in JSX instead of conditional content
  return (
    <div className="stock-container">
      {stock && <span className="in-stock">In Stock ({stock})</span>}
      {!stock && <span className="sold-out">Sold Out</span>}
    </div>
  );
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Uses explicit numeric comparison stock > 0', 'input': '', 'expected': 'stock > 0'}
        ],
        'bug_signature': '{stock && <span className="in-stock">',
        'suspected_component': 'Banner.jsx',
        'ai_suggestions': [
            'In React, `{0 && <span />}` renders the number 0.',
            'Change `{stock && ...}` to `{stock > 0 ? <span className="in-stock">In Stock ({stock})</span> : <span className="sold-out">Sold Out</span>}`.'
        ],
        'topics': ['React', 'Conditional Rendering', 'JSX'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['JSX Expressions'],
        'status': 'published'
    })

    # 88. A product card shows the wrong price after a state update
    challenges.append({
        'id': 88,
        'title': '[FE-E03] A Product Card Shows the Wrong Price After a State Update',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'React State',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A product card displays unit price and calculates total price when the quantity selector increments.

### Bug Report
User clicks `+` to increase quantity from 1 to 2. The total price continues to display the price for 1 item!

### Steps to Reproduce
1. Load `ProductCard.jsx`.
2. Click "+" button.
3. Total price lags by 1 step because state is read synchronously right after `setQuantity`.

### Expected Behavior
Derive `totalPrice = price * quantity` during render rather than storing redundant stale derived state.

### Actual Behavior
Maintains duplicate state variable `totalPrice` that reads previous `quantity` value.

### Impact
Customers see outdated price totals during cart selection.

### Requirements
- Compute `const totalPrice = price * quantity;` directly during render.
""",
        'files': [{
            'name': 'ProductCard.jsx',
            'content': '''import React, { useState } from 'react';

export default function ProductCard({ price = 25 }) {
  const [quantity, setQuantity] = useState(1);
  const [totalPrice, setTotalPrice] = useState(price);

  const handleIncrement = () => {
    setQuantity(quantity + 1);
    // BUG: Reads stale quantity immediately after setQuantity
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
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Total price derived cleanly from quantity', 'input': '', 'expected': 'price * quantity'}
        ],
        'bug_signature': 'setTotalPrice(price * quantity);',
        'suspected_component': 'ProductCard.jsx',
        'ai_suggestions': [
            'Do not store redundant state for calculated values.',
            'Remove `totalPrice` state and calculate `const total = price * quantity;` directly in the component body.'
        ],
        'topics': ['React', 'State', 'Derived State'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React useState'],
        'status': 'published'
    })

    # 89. A button fires the wrong event handler
    challenges.append({
        'id': 89,
        'title': '[FE-E04] A Button Fires the Wrong Event Handler',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'DOM & Events',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A task management toolbar contains "Save" and "Delete" buttons.

### Bug Report
When a user clicks "Save Draft", the task is permanently deleted!

### Steps to Reproduce
1. Click the "Save" button in `ActionButton.jsx`.
2. Notice `onClick={onDelete}` is bound to the save button instead of `onClick={onSave}`.

### Expected Behavior
Save button triggers `onSave`; Delete button triggers `onDelete`.

### Actual Behavior
Save button is wired to `onDelete`.

### Impact
Catastrophic accidental data loss when users intend to save their work.

### Requirements
- Connect `onClick={onSave}` to the Save button.
""",
        'files': [{
            'name': 'ActionButton.jsx',
            'content': '''import React from 'react';

export default function ActionToolbar({ onSave, onDelete }) {
  return (
    <div className="flex gap-2">
      {/* BUG: Save button calls onDelete handler */}
      <button onClick={onDelete} className="bg-emerald-600 text-white px-3 py-1 rounded">
        Save
      </button>
      <button onClick={onDelete} className="bg-rose-600 text-white px-3 py-1 rounded">
        Delete
      </button>
    </div>
  );
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Save button triggers onSave', 'input': '', 'expected': 'onClick={onSave}'}
        ],
        'bug_signature': '<button onClick={onDelete} className="bg-emerald-600',
        'suspected_component': 'ActionButton.jsx',
        'ai_suggestions': [
            'Change the Save button handler from `onClick={onDelete}` to `onClick={onSave}`.'
        ],
        'topics': ['React', 'Events', 'Event Handlers'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Event Binding in React'],
        'status': 'published'
    })

    # 90. A search field ignores uppercase/lowercase normalization
    challenges.append({
        'id': 90,
        'title': '[FE-E05] A Search Field Ignores Uppercase/Lowercase Normalization',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Validation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An internal employee directory provides live text filtering by employee name.

### Bug Report
Typing `"ALICE"` or `"alice"` fails to match employee `"Alice Smith"` due to strict case-sensitive matching.

### Steps to Reproduce
1. Type `"alice"` in search bar.
2. Filter uses `item.name.includes(query)`.
3. Zero results returned.

### Expected Behavior
Search should be case-insensitive: compare `.toLowerCase()`.

### Actual Behavior
Case-sensitive substring check.

### Impact
Users fail to find valid contacts in company directory.

### Requirements
- Apply `.toLowerCase()` to both `item.name` and `query`.
""",
        'files': [{
            'name': 'SearchBar.jsx',
            'content': '''import React, { useState } from 'react';

export default function SearchBar({ items = [] }) {
  const [query, setQuery] = useState('');

  // BUG: Case-sensitive search ignores uppercase / lowercase normalization
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
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Case-insensitive search using toLowerCase', 'input': '', 'expected': 'toLowerCase()'}
        ],
        'bug_signature': 'item.name.includes(query)',
        'suspected_component': 'SearchBar.jsx',
        'ai_suggestions': [
            'Normalize strings: `item.name.toLowerCase().includes(query.toLowerCase())`.'
        ],
        'topics': ['React', 'Search', 'Normalization'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['String Methods in JavaScript'],
        'status': 'published'
    })

    # 91. A loading indicator never disappears after an API error
    challenges.append({
        'id': 91,
        'title': '[FE-E06] A Loading Indicator Never Disappears After an API Error',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'React State',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A metrics dashboard fetches telemetry data on mount.

### Bug Report
When the server returns an HTTP 500 error, the spinner keeps spinning endlessly and the error message never displays.

### Steps to Reproduce
1. Fetch API fails.
2. Catch block sets `setError(err.message)`, but forgets `setLoading(false)`.
3. Spinner remains visible forever.

### Expected Behavior
`setLoading(false)` must be executed in both success and error cases (or in `finally`).

### Actual Behavior
`loading` remains `true` on error.

### Impact
Users stare at an endless loading screen and assume their connection is frozen.

### Requirements
- Add `setLoading(false)` to the error catch block or use `try/finally`.
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
        // BUG: Fails to set loading to false on error
        setError(err.message);
      });
  }, [fetchFn]);

  if (loading) return <div className="spinner">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  return <div>Data Loaded: {JSON.stringify(data)}</div>;
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Loading set to false on catch', 'input': '', 'expected': 'setLoading(false)'}
        ],
        'bug_signature': 'setError(err.message);\n      });',
        'suspected_component': 'DataViewer.jsx',
        'ai_suggestions': [
            'Add `setLoading(false);` inside the `.catch()` block.'
        ],
        'topics': ['React', 'Async', 'Loading States'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Promises in React'],
        'status': 'published'
    })

    # 92. A responsive layout overflows on mobile
    challenges.append({
        'id': 92,
        'title': '[FE-E07] A Responsive Layout Overflows on Mobile',
        'difficulty': 'Easy',
        'technology': 'CSS',
        'category': 'CSS & Styling',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A product detail card contains title, description, and pricing for mobile and desktop screens.

### Bug Report
On mobile devices (screen width 375px), the card overflows horizontally, causing horizontal scrollbars and breaking page layout.

### Steps to Reproduce
1. Open layout on 375px screen width.
2. Observe `width: 600px;` forces horizontal overflow.

### Expected Behavior
Use fluid responsive sizing: `max-width: 600px; width: 100%; box-sizing: border-box;`.

### Actual Behavior
Hardcoded fixed `width: 600px;`.

### Impact
Broken mobile responsiveness and poor Google mobile search ranking.

### Requirements
- Replace `width: 600px;` with `max-width: 600px; width: 100%;`.
""",
        'files': [{
            'name': 'ResponsiveCard.css',
            'content': '''.product-card {
    /* BUG: Hardcoded fixed width overflows on small screens */
    width: 600px;
    padding: 24px;
    background: #ffffff;
    border-radius: 8px;
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Uses max-width for responsive scaling', 'input': '', 'expected': 'max-width'}
        ],
        'bug_signature': '/* BUG: Hardcoded fixed width overflows on small screens */\n    width: 600px;',
        'suspected_component': 'ResponsiveCard.css',
        'ai_suggestions': [
            'Change `width: 600px;` to `max-width: 600px; width: 100%;`.'
        ],
        'topics': ['CSS', 'Responsive Design', 'Mobile'],
        'skills_tested': ['CSS', 'Frontend'],
        'prerequisites': ['CSS Box Model'],
        'status': 'published'
    })

    # 93. A form displays an incorrect validation message
    challenges.append({
        'id': 93,
        'title': '[FE-E08] A Form Displays an Incorrect Validation Message',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Validation',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A customer newsletter subscription widget validates email syntax.

### Bug Report
When user enters an invalid email missing `@`, the error displays `"Password must be at least 8 characters"`!

### Steps to Reproduce
1. Type `"invalidemail"` into newsletter input.
2. Observe copy-paste error in validation message.

### Expected Behavior
Display `"Please enter a valid email address."`.

### Actual Behavior
Displays copy-paste password error message.

### Impact
Confused users cannot figure out why their email is being rejected.

### Requirements
- Update error text to `"Please enter a valid email address."`.
""",
        'files': [{
            'name': 'EmailInput.jsx',
            'content': '''import React, { useState } from 'react';

export default function EmailInput() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const validate = () => {
    if (!email.includes('@')) {
      // BUG: Copy-paste error displays password error message
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
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Displays valid email error message', 'input': '', 'expected': 'Please enter a valid email address.'}
        ],
        'bug_signature': "setError('Password must be at least 8 characters');",
        'suspected_component': 'EmailInput.jsx',
        'ai_suggestions': [
            'Change message to `setError("Please enter a valid email address.");`.'
        ],
        'topics': ['React', 'Forms', 'Validation Messages'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['Form Validation'],
        'status': 'published'
    })

    # 94. A modal cannot be closed using the Escape key
    challenges.append({
        'id': 94,
        'title': '[FE-E09] A Modal Cannot Be Closed Using the Escape Key',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Accessibility',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
An accessible modal dialog component displays order confirmations.

### Bug Report
Keyboard users and screen readers cannot close the modal by pressing the Escape key, violating WCAG accessibility guidelines.

### Steps to Reproduce
1. Open modal dialog.
2. Press "Escape" key.
3. Modal remains open because keydown listener is missing or checks wrong key.

### Expected Behavior
Pressing Escape (`e.key === "Escape"`) invokes `onClose()`.

### Actual Behavior
No Escape key listener attached to document.

### Impact
Accessibility compliance violation (WCAG 2.1 Level AA) for keyboard-only navigation.

### Requirements
- Add `useEffect` listening for `keydown` where `e.key === 'Escape'` triggers `onClose()`.
""",
        'files': [{
            'name': 'Modal.jsx',
            'content': '''import React, { useEffect } from 'react';

export default function Modal({ isOpen, onClose, children }) {
  // BUG: Missing Escape key accessibility listener
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} aria-label="Close">X</button>
        {children}
      </div>
    </div>
  );
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Attaches Escape key listener in useEffect', 'input': '', 'expected': 'Escape'}
        ],
        'bug_signature': '// BUG: Missing Escape key accessibility listener',
        'suspected_component': 'Modal.jsx',
        'ai_suggestions': [
            'Add a `useEffect` that listens for `keydown` on window: `if (e.key === "Escape") onClose();`.'
        ],
        'topics': ['React', 'Accessibility', 'Keyboard Events', 'WCAG'],
        'skills_tested': ['React', 'Frontend', 'Accessibility'],
        'prerequisites': ['Keyboard Listeners in React'],
        'status': 'published'
    })

    # 95. A list uses an unstable or incorrect React key, causing UI inconsistencies
    challenges.append({
        'id': 95,
        'title': '[FE-E10] A List Uses an Unstable or Incorrect React Key, Causing UI Inconsistencies',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'DOM & Events',
        'time_estimate': '10 mins',
        'points': 100,
        'description': """### Company Scenario
A user list allows administrators to reorder and delete team members.

### Bug Report
When an admin deletes the first user in the list, input values and checkbox states from the deleted row jump onto the next row!

### Steps to Reproduce
1. Check checkbox on item 0.
2. Delete item 0.
3. Item 1 now has its checkbox checked because array index `index` was used as key!

### Expected Behavior
Use stable unique entity ID `key={user.id}`.

### Actual Behavior
Uses array index: `key={index}`.

### Impact
State corruption in form inputs and reordered lists.

### Requirements
- Change `key={index}` to `key={user.id}`.
""",
        'files': [{
            'name': 'UserList.jsx',
            'content': '''import React from 'react';

export default function UserList({ users = [], onDelete }) {
  return (
    <ul>
      {/* BUG: Uses array index as key causing state corruption on deletion */}
      {users.map((user, index) => (
        <li key={index} className="flex justify-between p-2">
          <span>{user.name}</span>
          <button onClick={() => onDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
'''
        }],
        'test_cases': [
            {'id': 1, 'name': 'Visible: Uses stable user.id as key', 'input': '', 'expected': 'key={user.id}'}
        ],
        'bug_signature': '<li key={index}',
        'suspected_component': 'UserList.jsx',
        'ai_suggestions': [
            'Change `<li key={index}` to `<li key={user.id}`.'
        ],
        'topics': ['React', 'Keys', 'Reconciliation'],
        'skills_tested': ['React', 'Frontend'],
        'prerequisites': ['React Lists and Keys'],
        'status': 'published'
    })

    return challenges
