from django.core.management.base import BaseCommand
from buggyman.models import User, Challenge, Notification, Submission

class Command(BaseCommand):
    help = 'Seed database with initial challenges, users, and notifications'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Create Default User (Jane Doe)
        user, created = User.objects.get_or_create(
            username='janedoe',
            defaults={
                'email': 'jane.doe@college.edu',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'college': 'State Technical University',
                'bio': 'Aspiring Full Stack Engineer. Lover of logic puzzles and debugging challenge marathons.',
                'avatar': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
                'total_score': 780,
                'challenges_solved': 12,
                'streak': 5,
                'skills': {
                    'React': 80,
                    'Django': 60,
                    'NodeJS': 45,
                    'CSS': 70
                },
                'activities': [
                    { 'id': 1, 'text': 'Completed "Fix React State Updates"', 'time': '2 hours ago', 'xp': 100 },
                    { 'id': 2, 'text': 'Unlocked "Bug Squasher" Badge', 'time': '1 day ago', 'xp': 50 },
                    { 'id': 3, 'text': 'Solved "Express Middlewares" challenge', 'time': '3 days ago', 'xp': 200 }
                ],
                'badges': [
                    { 'name': 'First Bug Defeated', 'desc': 'Resolved your first bug', 'icon': '🐞', 'date': 'Jul 01, 2026' },
                    { 'name': 'Five Day Streak', 'desc': 'Debugged 5 days in a row', 'icon': '🔥', 'date': 'Jul 05, 2026' },
                    { 'name': 'AI Explorer', 'desc': 'Used AI hints 10 times', 'icon': '🤖', 'date': 'Jul 08, 2026' }
                ]
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write('Created user: janedoe (password: password123)')

        # 2. Create Leaderboard Competitors
        leaderboard_users = [
            {'username': 'alexrivera', 'email': 'alex@mit.edu', 'first_name': 'Alex', 'last_name': 'Rivera', 'score': 1450, 'solved': 22, 'streak': 12, 'college': 'MIT'},
            {'username': 'samchen', 'email': 'sam@stanford.edu', 'first_name': 'Sam', 'last_name': 'Chen', 'score': 1220, 'solved': 18, 'streak': 8, 'college': 'Stanford'},
            {'username': 'devonsmith', 'email': 'devon@gatech.edu', 'first_name': 'Devon', 'last_name': 'Smith', 'score': 650, 'solved': 9, 'streak': 3, 'college': 'Georgia Tech'},
            {'username': 'liwei', 'email': 'li@caltech.edu', 'first_name': 'Li', 'last_name': 'Wei', 'score': 580, 'solved': 7, 'streak': 2, 'college': 'Caltech'},
        ]

        for lu in leaderboard_users:
            u, c = User.objects.get_or_create(
                username=lu['username'],
                defaults={
                    'email': lu['email'],
                    'first_name': lu['first_name'],
                    'last_name': lu['last_name'],
                    'college': lu['college'],
                    'total_score': lu['score'],
                    'challenges_solved': lu['solved'],
                    'streak': lu['streak']
                }
            )
            if c:
                u.set_password('password123')
                u.save()

        # Clear old challenges
        Challenge.objects.all().delete()

        # 3. New 30 Challenges list
        challenges_data = [
            # 🟢 EASY (1-10)
            {
                'id': 1,
                'title': '1. Dark/Light Theme',
                'description': 'Add a Dark Mode and Light Mode toggle.\n\nRequirements:\n- Toggle should be available in the navbar.\n- Save the user\'s preference in localStorage.\n- Theme should persist after refresh.\n- Add smooth transition animations.\n- Do not break existing UI.',
                'difficulty': 'Easy',
                'technology': 'CSS',
                'category': 'CSS Grid & Responsive',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'ThemeToggle.css',
                        'content': (
                            "/* BUG: Missing standard CSS variable transition and theme selector fallback */\n"
                            ":root {\n"
                            "  --bg-primary: #ffffff;\n"
                            "  --text-primary: #0f172a;\n"
                            "}\n"
                            "[data-theme=\"dark\"] {\n"
                            "  --bg-primary: #090d16;\n"
                            "  --text-primary: #f8fafc;\n"
                            "}\n"
                            ".theme-container {\n"
                            "  background-color: var(--bg-primary);\n"
                            "  color: var(--text-primary);\n"
                            "  /* Buggy code below */\n"
                            "  transition: none;\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Uses transitions for smooth changes', 'input': '', 'expected': 'transition: background-color', 'passed': False }
                ],
                'bug_signature': 'transition: none;',
                'suspected_component': 'ThemeToggle.css',
                'ai_suggestions': [
                    'Change `transition: none;` to a smooth transition like `transition: background-color 0.3s ease, color 0.3s ease;`.'
                ]
            },
            {
                'id': 2,
                'title': '2. Search Bugs',
                'description': 'Add a search bar to filter bugs.\n\nRequirements:\n- Search by title.\n- Search updates in real time.\n- Case insensitive.\n- If nothing matches, show "No bugs found."',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'Search',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'BugSearch.jsx',
                        'content': (
                            "import React, { useState } from 'react';\n\n"
                            "export default function BugSearch({ bugs }) {\n"
                            "  const [query, setQuery] = useState('');\n\n"
                            "  // BUG: Case sensitive filter that crashes if bug has no title\n"
                            "  const filteredBugs = bugs.filter(bug => bug.title.includes(query));\n\n"
                            "  return (\n"
                            "    <div className=\"p-4\">\n"
                            "      <input \n"
                            "        type=\"text\" \n"
                            "        value={query} \n"
                            "        onChange={(e) => setQuery(e.target.value)}\n"
                            "        className=\"w-full p-2 border rounded-lg bg-slate-900 text-white\"\n"
                            "        placeholder=\"Search bugs...\"\n"
                            "      />\n"
                            "      {filteredBugs.length === 0 ? (\n"
                            "        <p className=\"text-slate-400 mt-4\">No bugs found.</p>\n"
                            "      ) : (\n"
                            "        <ul className=\"mt-4 space-y-2\">\n"
                            "          {filteredBugs.map(bug => <li key={bug.id} className=\"text-white\">{bug.title}</li>)}\n"
                            "        </ul>\n"
                            "      )}\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Case-insensitive filtering', 'input': '', 'expected': '.toLowerCase()', 'passed': False }
                ],
                'bug_signature': 'const filteredBugs = bugs.filter(bug => bug.title.includes(query));',
                'suspected_component': 'BugSearch.jsx',
                'ai_suggestions': [
                    'Use `.toLowerCase()` to make search case-insensitive and handle safe access: `const filteredBugs = bugs.filter(bug => (bug.title || "").toLowerCase().includes(query.toLowerCase()));`'
                ]
            },
            {
                'id': 3,
                'title': '3. Bug Priority Colors',
                'description': 'Improve the bug cards by showing appropriate priority badge colors: Low=Green, Medium=Orange, High=Red, Critical=Dark Red.',
                'difficulty': 'Easy',
                'technology': 'CSS',
                'category': 'Styling & CSS',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'PriorityBadge.css',
                        'content': (
                            "/* BUG: Bad colors, Critical and High priorities are using the same plain red background */\n"
                            ".badge-low {\n"
                            "  background-color: #10b981; /* Green */\n"
                            "}\n"
                            ".badge-medium {\n"
                            "  background-color: #f97316; /* Orange */\n"
                            "}\n"
                            ".badge-high {\n"
                            "  background-color: #ef4444; /* Red */\n"
                            "}\n"
                            ".badge-critical {\n"
                            "  background-color: #ef4444; /* BUG: Should be dark red */\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Critical badge uses dark red background', 'input': '', 'expected': 'background-color: #991b1b', 'passed': False }
                ],
                'bug_signature': '.badge-critical {\n  background-color: #ef4444;',
                'suspected_component': 'PriorityBadge.css',
                'ai_suggestions': [
                    'Change the background color of `.badge-critical` to a dark red hex code like `#991b1b` or `#7f1d1d`.'
                ]
            },
            {
                'id': 4,
                'title': '4. Toast Notifications',
                'description': 'Replace alert() with modern toast notifications.\n\nRequirements:\n- Success\n- Error\n- Warning\n- Auto disappear after 3 seconds.',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'User Experience',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'ToastContainer.jsx',
                        'content': (
                            "import React, { useEffect } from 'react';\n\n"
                            "export default function Toast({ message, type, onClose }) {\n"
                            "  useEffect(() => {\n"
                            "    // BUG: Standard alert blocks JS thread, and missing automatic 3 second timeout dismissal\n"
                            "    alert(`${type.toUpperCase()}: ${message}`);\n"
                            "    onClose();\n"
                            "  }, [message, type, onClose]);\n\n"
                            "  return (\n"
                            "    <div className={`p-4 rounded-lg text-white ${type === 'success' ? 'bg-emerald-600' : 'bg-rose-600'}`}>\n"
                            "      {message}\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Automatically dismisses after timeout', 'input': '', 'expected': 'setTimeout', 'passed': False }
                ],
                'bug_signature': 'alert(`${type.toUpperCase()}: ${message}`);\n    onClose();',
                'suspected_component': 'ToastContainer.jsx',
                'ai_suggestions': [
                    'Replace `alert(...)` with a timer: `const timer = setTimeout(onClose, 3000); return () => clearTimeout(timer);`.'
                ]
            },
            {
                'id': 5,
                'title': '5. Loading Spinner',
                'description': 'Whenever data is being fetched or submitted, show a loading spinner, then hide it after the request completes.',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'User Experience',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'FetchData.jsx',
                        'content': (
                            "import React, { useState, useEffect } from 'react';\n\n"
                            "export default function FetchData() {\n"
                            "  const [data, setData] = useState([]);\n"
                            "  const [loading, setLoading] = useState(false);\n\n"
                            "  useEffect(() => {\n"
                            "    setLoading(true);\n"
                            "    fetch('/api/challenges')\n"
                            "      .then(res => res.json())\n"
                            "      .then(data => setData(data));\n"
                            "      // BUG: Missing catch and finally block to set loading state back to false!\n"
                            "  }, []);\n\n"
                            "  if (loading) return <div className=\"spinner\">Loading...</div>;\n"
                            "  return <div>Loaded {data.length} items.</div>;\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Turns off loading indicator', 'input': '', 'expected': 'setLoading(false)', 'passed': False }
                ],
                'bug_signature': "fetch('/api/challenges')\n      .then(res => res.json())\n      .then(data => setData(data));",
                'suspected_component': 'FetchData.jsx',
                'ai_suggestions': [
                    'Add `.finally(() => setLoading(false))` or set `setLoading(false)` inside the `.then` block.'
                ]
            },
            {
                'id': 6,
                'title': '6. Empty State',
                'description': 'Improve the dashboard when there are no bugs. Show an illustration, "No Bugs Yet", and a button to create the first bug.',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'User Experience',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'EmptyState.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function EmptyState({ bugs, onCreateBug }) {\n"
                            "  if (bugs && bugs.length > 0) return null;\n\n"
                            "  // BUG: Empty return when there are no bugs, user sees a completely blank section!\n"
                            "  return null;\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Renders empty state message', 'input': '', 'expected': 'No Bugs Yet', 'passed': False }
                ],
                'bug_signature': '// BUG: Empty return when there are no bugs, user sees a completely blank section!\n  return null;',
                'suspected_component': 'EmptyState.jsx',
                'ai_suggestions': [
                    'Return a JSX fragment containing the text "No Bugs Yet" and a button to trigger `onCreateBug`.'
                ]
            },
            {
                'id': 7,
                'title': '7. Better Form Validation',
                'description': 'Improve bug creation validation.\n\nRequirements:\n- Required fields (title must be filled)\n- Description minimum length of 10 characters\n- Friendly error messages.',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'Data Validation',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'BugForm.jsx',
                        'content': (
                            "import React, { useState } from 'react';\n\n"
                            "export default function BugForm({ onSubmit }) {\n"
                            "  const [title, setTitle] = useState('');\n"
                            "  const [description, setDescription] = useState('');\n\n"
                            "  const handleSubmit = (e) => {\n"
                            "    e.preventDefault();\n"
                            "    // BUG: Missing validation entirely - permits empty submit!\n"
                            "    onSubmit({ title, description });\n"
                            "  };\n\n"
                            "  return (\n"
                            "    <form onSubmit={handleSubmit} className=\"space-y-4\">\n"
                            "      <input value={title} onChange={e => setTitle(e.target.value)} placeholder=\"Title\" />\n"
                            "      <textarea value={description} onChange={e => setDescription(e.target.value)} placeholder=\"Description\" />\n"
                            "      <button type=\"submit\">Submit</button>\n"
                            "    </form>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Restricts invalid submissions', 'input': '', 'expected': 'description.length < 10', 'passed': False }
                ],
                'bug_signature': '// BUG: Missing validation entirely - permits empty submit!\n    onSubmit({ title, description });',
                'suspected_component': 'BugForm.jsx',
                'ai_suggestions': [
                    'Check conditions like `if (!title.trim() || description.length < 10) { alert("Invalid input"); return; }` before calling `onSubmit`.'
                ]
            },
            {
                'id': 8,
                'title': '8. User Profile Page',
                'description': 'Create a simple profile page. Show Name, Email, Joined Date, and Number of bugs created. Make sure it uses the dynamic user object.',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'Components',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'UserProfile.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function UserProfile({ user }) {\n"
                            "  // BUG: Displaying hardcoded admin statistics instead of reading from the user prop!\n"
                            "  return (\n"
                            "    <div className=\"profile-card\">\n"
                            "      <h2>Developer Name: Administrator</h2>\n"
                            "      <p>Email: admin@company.com</p>\n"
                            "      <p>Member Since: 2020-01-01</p>\n"
                            "      <p>Bugs Opened: 99</p>\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Reads dynamically from user prop', 'input': '', 'expected': 'user.name', 'passed': False }
                ],
                'bug_signature': '<h2>Developer Name: Administrator</h2>\n      <p>Email: admin@company.com</p>\n      <p>Member Since: 2020-01-01</p>\n      <p>Bugs Opened: 99</p>',
                'suspected_component': 'UserProfile.jsx',
                'ai_suggestions': [
                    'Replace the hardcoded strings with dynamic props: `{user.name}`, `{user.email}`, `{user.joinedDate}`, `{user.bugsCount}`.'
                ]
            },
            {
                'id': 9,
                'title': '9. Copy Bug ID',
                'description': 'Add a copy button beside the Bug ID. Clicking it should copy the ID to clipboard and show a toast saying "Copied!"',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'User Experience',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'CopyButton.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function CopyButton({ bugId, onToast }) {\n"
                            "  const handleCopy = () => {\n"
                            "    // BUG: Using deprecated document.execCommand instead of modern navigator.clipboard API\n"
                            "    document.execCommand('copy');\n"
                            "    onToast('Copied!');\n"
                            "  };\n\n"
                            "  return (\n"
                            "    <button onClick={handleCopy} className=\"p-1 text-slate-400 hover:text-white\">\n"
                            "      Copy ID\n"
                            "    </button>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Writes to Clipboard API', 'input': '', 'expected': 'navigator.clipboard.writeText', 'passed': False }
                ],
                'bug_signature': "// BUG: Using deprecated document.execCommand instead of modern navigator.clipboard API\n    document.execCommand('copy');",
                'suspected_component': 'CopyButton.jsx',
                'ai_suggestions': [
                    'Use the modern clipboard API: `navigator.clipboard.writeText(bugId).then(() => onToast("Copied!"));`.'
                ]
            },
            {
                'id': 10,
                'title': '10. Pagination',
                'description': 'Add pagination to the bugs list. Show 10 bugs per page. Add working Previous and Next buttons.',
                'difficulty': 'Easy',
                'technology': 'React',
                'category': 'Optimization',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [
                    {
                        'name': 'Pagination.jsx',
                        'content': (
                            "import React, { useState } from 'react';\n\n"
                            "export default function PaginatedBugs({ bugs }) {\n"
                            "  const [currentPage, setCurrentPage] = useState(1);\n"
                            "  const itemsPerPage = 10;\n\n"
                            "  // BUG: Slice indices are hardcoded or incorrectly computed, ignoring currentPage!\n"
                            "  const displayedBugs = bugs.slice(0, bugs.length);\n\n"
                            "  return (\n"
                            "    <div>\n"
                            "      <ul>\n"
                            "        {displayedBugs.map(bug => <li key={bug.id}>{bug.title}</li>)}\n"
                            "      </ul>\n"
                            "      <div className=\"flex gap-2 mt-4\">\n"
                            "        <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))}>Previous</button>\n"
                            "        <button onClick={() => setCurrentPage(p => p + 1)}>Next</button>\n"
                            "      </div>\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Slices data based on currentPage', 'input': '', 'expected': '(currentPage - 1) * itemsPerPage', 'passed': False }
                ],
                'bug_signature': '// BUG: Slice indices are hardcoded or incorrectly computed, ignoring currentPage!\n  const displayedBugs = bugs.slice(0, bugs.length);',
                'suspected_component': 'Pagination.jsx',
                'ai_suggestions': [
                    'Compute correct page indexes: `const start = (currentPage - 1) * itemsPerPage; const displayedBugs = bugs.slice(start, start + itemsPerPage);`.'
                ]
            },

            # 🟡 MEDIUM (11-20)
            {
                'id': 11,
                'title': '11. Bug Status Timeline',
                'description': 'Create a timeline for each bug (Created -> Assigned -> In Progress -> Testing -> Completed). Highlight the current stage.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'Components',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'Timeline.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function Timeline({ currentStatus }) {\n"
                            "  const stages = ['Created', 'Assigned', 'In Progress', 'Testing', 'Completed'];\n\n"
                            "  return (\n"
                            "    <div className=\"flex justify-between items-center w-full\">\n"
                            "      {stages.map((stage, index) => {\n"
                            "        // BUG: Always checking if index === 0 instead of comparing with currentStatus index\n"
                            "        const isActive = index === 0;\n"
                            "        return (\n"
                            "          <div key={stage} className={`p-2 rounded-lg ${isActive ? 'bg-indigo-600 text-white font-bold' : 'bg-slate-800 text-slate-400'}`}>\n"
                            "            {stage}\n"
                            "          </div>\n"
                            "        );\n"
                            "      })}\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Evaluates active status index dynamically', 'input': '', 'expected': 'stages.indexOf(currentStatus)', 'passed': False }
                ],
                'bug_signature': '// BUG: Always checking if index === 0 instead of comparing with currentStatus index\n        const isActive = index === 0;',
                'suspected_component': 'Timeline.jsx',
                'ai_suggestions': [
                    'Compare the current loop index with the index of `currentStatus` in the stages array: `const isActive = index <= stages.indexOf(currentStatus);`.'
                ]
            },
            {
                'id': 12,
                'title': '12. Dashboard Statistics',
                'description': 'Create a dashboard with analytics displaying: Total, Open, Closed, High Priority, and Critical Bugs. Fix the statistics aggregation logic.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'Analytics',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'statsReducer.js',
                        'content': (
                            "// BUG: Incorrect statistics aggregation logic\n"
                            "export function calculateStats(bugs) {\n"
                            "  return bugs.reduce((acc, bug) => {\n"
                            "    acc.total += 1;\n"
                            "    // BUG: Adding all bugs to open instead of checking status!\n"
                            "    acc.open += 1;\n"
                            "    if (bug.priority === 'High') {\n"
                            "      acc.high += 1;\n"
                            "    }\n"
                            "    // BUG: Missing critical priority aggregation!\n"
                            "    return acc;\n"
                            "  }, { total: 0, open: 0, closed: 0, high: 0, critical: 0 });\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Separates stats by status and priority', 'input': '', 'expected': "bug.status === 'Open'", 'passed': False }
                ],
                'bug_signature': (
                    "// BUG: Adding all bugs to open instead of checking status!\n"
                    "    acc.open += 1;\n"
                    "    if (bug.priority === 'High') {\n"
                    "      acc.high += 1;\n"
                    "    }\n"
                    "    // BUG: Missing critical priority aggregation!"
                ),
                'suspected_component': 'statsReducer.js',
                'ai_suggestions': [
                    'Perform proper conditional checks on `bug.status` and check for both "High" and "Critical" priorities: `if (bug.status === "Open") acc.open += 1; else if (bug.status === "Closed") acc.closed += 1;`'
                ]
            },
            {
                'id': 13,
                'title': '13. Advanced Filters',
                'description': 'Add advanced filtering. Allow filtering by Priority and Status. Ensure multiple filters can work together.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'Filtering',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'FilterPanel.jsx',
                        'content': (
                            "import React, { useState } from 'react';\n\n"
                            "export default function FilterPanel({ bugs }) {\n"
                            "  const [priority, setPriority] = useState('All');\n"
                            "  const [status, setStatus] = useState('All');\n\n"
                            "  // BUG: Applying filters independently and replacing rather than combining criteria\n"
                            "  const filtered = bugs.filter(bug => {\n"
                            "    if (priority !== 'All') return bug.priority === priority;\n"
                            "    if (status !== 'All') return bug.status === status;\n"
                            "    return true;\n"
                            "  });\n\n"
                            "  return (\n"
                            "    <div>\n"
                            "      <select value={priority} onChange={e => setPriority(e.target.value)}>\n"
                            "        <option value=\"All\">All Priorities</option>\n"
                            "        <option value=\"High\">High</option>\n"
                            "      </select>\n"
                            "      <select value={status} onChange={e => setStatus(e.target.value)}>\n"
                            "        <option value=\"All\">All Statuses</option>\n"
                            "        <option value=\"Open\">Open</option>\n"
                            "      </select>\n"
                            "      <p>Filtered Count: {filtered.length}</p>\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Combined filters evaluation', 'input': '', 'expected': 'matchesPriority && matchesStatus', 'passed': False }
                ],
                'bug_signature': (
                    "  // BUG: Applying filters independently and replacing rather than combining criteria\n"
                    "  const filtered = bugs.filter(bug => {\n"
                    "    if (priority !== 'All') return bug.priority === priority;\n"
                    "    if (status !== 'All') return bug.status === status;\n"
                    "    return true;\n"
                    "  });"
                ),
                'suspected_component': 'FilterPanel.jsx',
                'ai_suggestions': [
                    'Combine filters logically using `&&`: `const matchesPriority = priority === "All" || bug.priority === priority; const matchesStatus = status === "All" || bug.status === status; return matchesPriority && matchesStatus;`.'
                ]
            },
            {
                'id': 14,
                'title': '14. Sort Bugs',
                'description': 'Allow sorting bugs by Latest, Oldest, or Highest Priority. Fix the sorting function so it doesn\'t mutate props directly.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'Sorting',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'SortBugs.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function SortBugs({ bugs, onSorted }) {\n"
                            "  const handleSort = (criteria) => {\n"
                            "    // BUG: Mutating original prop array directly instead of creating a copy!\n"
                            "    const sorted = bugs.sort((a, b) => {\n"
                            "      if (criteria === 'Latest') return b.id - a.id;\n"
                            "      return a.id - b.id;\n"
                            "    });\n"
                            "    onSorted(sorted);\n"
                            "  };\n\n"
                            "  return (\n"
                            "    <div className=\"flex gap-2\">\n"
                            "      <button onClick={() => handleSort('Latest')}>Sort Latest</button>\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Avoids array mutation', 'input': '', 'expected': '[...bugs]', 'passed': False }
                ],
                'bug_signature': (
                    "    // BUG: Mutating original prop array directly instead of creating a copy!\n"
                    "    const sorted = bugs.sort((a, b) => {"
                ),
                'suspected_component': 'SortBugs.jsx',
                'ai_suggestions': [
                    'Clone the bugs array before sorting it to prevent direct mutation of props: `const sorted = [...bugs].sort(...)`.'
                ]
            },
            {
                'id': 15,
                'title': '15. Comments System',
                'description': 'Implement comments list. The deletion logic deletes comments by index which shifts indices. Fix it to delete comments by unique ID.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'Comments',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'CommentsSection.jsx',
                        'content': (
                            "import React, { useState } from 'react';\n\n"
                            "export default function CommentsSection() {\n"
                            "  const [comments, setComments] = useState([\n"
                            "    { id: 1, text: 'First comment' },\n"
                            "    { id: 2, text: 'Second comment' }\n"
                            "  ]);\n\n"
                            "  const handleDelete = (index) => {\n"
                            "    // BUG: Deleting by index instead of unique comment ID!\n"
                            "    const newComments = comments.filter((_, idx) => idx !== index);\n"
                            "    setComments(newComments);\n"
                            "  };\n\n"
                            "  return (\n"
                            "    <div>\n"
                            "      {comments.map((comment, index) => (\n"
                            "        <div key={comment.id}>\n"
                            "          <span>{comment.text}</span>\n"
                            "          <button onClick={() => handleDelete(index)}>Delete</button>\n"
                            "        </div>\n"
                            "      ))}\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Deletes comment by ID', 'input': '', 'expected': 'comment.id !== id', 'passed': False }
                ],
                'bug_signature': (
                    "  const handleDelete = (index) => {\n"
                    "    // BUG: Deleting by index instead of unique comment ID!\n"
                    "    const newComments = comments.filter((_, idx) => idx !== index);\n"
                    "    setComments(newComments);\n"
                    "  };"
                ),
                'suspected_component': 'CommentsSection.jsx',
                'ai_suggestions': [
                    'Change `handleDelete` signature to accept `id` and filter based on comment ID: `comments.filter(comment => comment.id !== id)`.'
                ]
            },
            {
                'id': 16,
                'title': '16. File Attachments',
                'description': 'Allow users to upload screenshots. Add validation check for file size (maximum 5MB). The current limit validation is in bits/incorrect unit.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'Forms',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'Upload.jsx',
                        'content': (
                            "import React, { useState } from 'react';\n\n"
                            "export default function Upload({ onUpload }) {\n"
                            "  const [error, setError] = useState('');\n\n"
                            "  const handleFileChange = (e) => {\n"
                            "    const file = e.target.files[0];\n"
                            "    if (!file) return;\n\n"
                            "    // BUG: Incorrect size checking: 5MB is 5 * 1024 * 1024 bytes, but current code checks against bits or too small value!\n"
                            "    if (file.size > 5000) {\n"
                            "      setError('File too large. Max 5MB.');\n"
                            "      return;\n"
                            "    }\n\n"
                            "    onUpload(file);\n"
                            "  };\n\n"
                            "  return (\n"
                            "    <div>\n"
                            "      <input type=\"file\" onChange={handleFileChange} />\n"
                            "      {error && <span className=\"text-red-500\">{error}</span>}\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Validates 5MB limit in bytes', 'input': '', 'expected': '5 * 1024 * 1024', 'passed': False }
                ],
                'bug_signature': (
                    "    // BUG: Incorrect size checking: 5MB is 5 * 1024 * 1024 bytes, but current code checks against bits or too small value!\n"
                    "    if (file.size > 5000) {"
                ),
                'suspected_component': 'Upload.jsx',
                'ai_suggestions': [
                    'Specify 5MB in bytes: `5 * 1024 * 1024` which is `5242880` bytes.'
                ]
            },
            {
                'id': 17,
                'title': '17. Activity Log',
                'description': 'Track bug edits using Django signals. The signal callback contains a reference error causing it to fail.',
                'difficulty': 'Medium',
                'technology': 'Django',
                'category': 'Logging',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'signals.py',
                        'content': (
                            "from django.db.models.signals import post_save\n"
                            "from django.dispatch import receiver\n"
                            "from .models import Bug, ActivityLog\n\n"
                            "@receiver(post_save, sender=Bug)\n"
                            "def log_bug_activity(sender, instance, created, **kwargs):\n"
                            "    # BUG: Standing receiver function incorrectly references 'self'!\n"
                            "    action = \"Created\" if created else \"Updated\"\n"
                            "    self.stdout.write(f\"Logging activity: {action}\")\n"
                            "    ActivityLog.objects.create(bug=instance, action=action)"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Eliminates invalid self reference', 'input': '', 'expected': 'action =', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Standing receiver function incorrectly references 'self'!\n"
                    "    action = \"Created\" if created else \"Updated\"\n"
                    "    self.stdout.write(f\"Logging activity: {action}\")"
                ),
                'suspected_component': 'signals.py',
                'ai_suggestions': [
                    'Delete the `self.stdout.write(...)` line as receiver functions are module-level and do not have access to a `self` object.'
                ]
            },
            {
                'id': 18,
                'title': '18. Email Notifications',
                'description': 'Send email when a bug is completed. The function uses standard Django send_mail but specifies incorrect parameters.',
                'difficulty': 'Medium',
                'technology': 'Django',
                'category': 'Email',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'notifier.py',
                        'content': (
                            "from django.core.mail import send_mail\n\n"
                            "def send_bug_completed_email(bug):\n"
                            "    # BUG: send_mail called with positional list instead of keyword arguments or correct order\n"
                            "    send_mail(\n"
                            "        \"Bug Completed: \" + bug.title,\n"
                            "        \"The bug has been fixed.\",\n"
                            "        [\"dev@company.com\"],\n"
                            "        \"noreply@company.com\",\n"
                            "    )"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Correct parameters for send_mail', 'input': '', 'expected': '"noreply@company.com", ["dev@company.com"]', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: send_mail called with positional list instead of keyword arguments or correct order\n"
                    "    send_mail(\n"
                    "        \"Bug Completed: \" + bug.title,\n"
                    "        \"The bug has been fixed.\",\n"
                    "        [\"dev@company.com\"],\n"
                    "        \"noreply@company.com\",\n"
                    "    )"
                ),
                'suspected_component': 'notifier.py',
                'ai_suggestions': [
                    'The fourth parameter of send_mail should be the recipient list, and the third should be the sender: `send_mail(subject, message, sender, recipient_list)`.'
                ]
            },
            {
                'id': 19,
                'title': '19. Role Based Access',
                'description': 'Implement role-based permissions decorator. The role check crashes if request.user is not fully initialized.',
                'difficulty': 'Medium',
                'technology': 'Django',
                'category': 'Permissions',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'permissions.py',
                        'content': (
                            "from django.core.exceptions import PermissionDenied\n\n"
                            "def require_role(allowed_roles):\n"
                            "    def decorator(view_func):\n"
                            "        def _wrapped_view(request, *args, **kwargs):\n"
                            "            # BUG: Accessing non-existent 'request.user.role' before checking if user is authenticated\n"
                            "            if request.user.role not in allowed_roles:\n"
                            "                raise PermissionDenied\n"
                            "            return view_func(request, *args, **kwargs)\n"
                            "        return _wrapped_view\n"
                            "    return decorator"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Safe attribute validation', 'input': '', 'expected': 'getattr', 'passed': False }
                ],
                'bug_signature': (
                    "            # BUG: Accessing non-existent 'request.user.role' before checking if user is authenticated\n"
                    "            if request.user.role not in allowed_roles:\n"
                    "                raise PermissionDenied"
                ),
                'suspected_component': 'permissions.py',
                'ai_suggestions': [
                    'Safely access user roles: `if not request.user.is_authenticated or getattr(request.user, "role", None) not in allowed_roles:`'
                ]
            },
            {
                'id': 20,
                'title': '20. Kanban Board',
                'description': 'A Kanban board with draggable cards. The drag-over handler doesn\'t call preventDefault(), which blocks dropping.',
                'difficulty': 'Medium',
                'technology': 'React',
                'category': 'User Experience',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [
                    {
                        'name': 'Kanban.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function KanbanBoard({ onDropBug }) {\n"
                            "  const handleDragOver = (e) => {\n"
                            "    // BUG: Missing e.preventDefault() which blocks drop events in HTML5 drag and drop API\n"
                            "    console.log(\"Dragging over column...\");\n"
                            "  };\n\n"
                            "  const handleDrop = (e, status) => {\n"
                            "    const bugId = e.dataTransfer.getData(\"bugId\");\n"
                            "    onDropBug(bugId, status);\n"
                            "  };\n\n"
                            "  return (\n"
                            "    <div \n"
                            "      onDragOver={handleDragOver} \n"
                            "      onDrop={(e) => handleDrop(e, 'In Progress')}\n"
                            "      className=\"p-4 bg-slate-900 min-h-[300px]\"\n"
                            "    >\n"
                            "      In Progress Column (Drop here)\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Prevents default dragover event', 'input': '', 'expected': 'e.preventDefault()', 'passed': False }
                ],
                'bug_signature': (
                    "  const handleDragOver = (e) => {\n"
                    "    // BUG: Missing e.preventDefault() which blocks drop events in HTML5 drag and drop API\n"
                    "    console.log(\"Dragging over column...\");\n"
                    "  };"
                ),
                'suspected_component': 'Kanban.jsx',
                'ai_suggestions': [
                    'Add `e.preventDefault();` in the `handleDragOver` handler to allow elements to be dropped.'
                ]
            },

            # 🔴 HARD (21-30)
            {
                'id': 21,
                'title': '21. AI Bug Severity Prediction',
                'description': 'Integrate an AI model to predict severity from a description. Prompt construction has injection vulnerabilities.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'AI Integration',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'ai_predictor.py',
                        'content': (
                            "import json\n\n"
                            "def construct_ai_payload(description):\n"
                            "    # BUG: Concatenating description directly into JSON string template which breaks if user inputs quotes!\n"
                            "    payload_str = f'{{\"description\": \"{description}\", \"model\": \"severity-v1\"}}'\n"
                            "    return json.loads(payload_str)"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Safe JSON serialization', 'input': '', 'expected': 'json.dumps', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Concatenating description directly into JSON string template which breaks if user inputs quotes!\n"
                    "    payload_str = f'{{\"description\": \"{description}\", \"model\": \"severity-v1\"}}'"
                ),
                'suspected_component': 'ai_predictor.py',
                'ai_suggestions': [
                    'Construct the dictionary directly and use `json.dumps()` or return the dict: `payload = {"description": description, "model": "severity-v1"}`.'
                ]
            },
            {
                'id': 22,
                'title': '22. Duplicate Bug Detection',
                'description': 'Check for duplicate bugs based on title similarity. The loop returns immediately on the first comparison.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'Algorithms',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'detector.py',
                        'content': (
                            "def find_duplicate_bug(new_title, existing_bugs):\n"
                            "    for bug in existing_bugs:\n"
                            "        # BUG: Returns immediately in the first iteration instead of looking through all bugs!\n"
                            "        if bug.title.lower() == new_title.lower():\n"
                            "            return bug\n"
                            "        else:\n"
                            "            return None"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Inspects all items before returning', 'input': '', 'expected': 'return None', 'passed': False }
                ],
                'bug_signature': (
                    "        # BUG: Returns immediately in the first iteration instead of looking through all bugs!\n"
                    "        if bug.title.lower() == new_title.lower():\n"
                    "            return bug\n"
                    "        else:\n"
                    "            return None"
                ),
                'suspected_component': 'detector.py',
                'ai_suggestions': [
                    'Remove the `else` clause inside the loop so that the function only returns `None` after examining all existing bugs.'
                ]
            },
            {
                'id': 23,
                'title': '23. AI Bug Summary',
                'description': 'Generate an AI summary of a bug. The HTTP request is missing a timeout parameter, risking thread locks.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'AI Integration',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'ai_summary.py',
                        'content': (
                            "import urllib.request\n"
                            "import urllib.parse\n\n"
                            "def fetch_ai_summary(bug_details):\n"
                            "    data = urllib.parse.urlencode({'text': bug_details}).encode('utf-8')\n"
                            "    # BUG: Missing timeout parameter in urllib urlopen call, which can hang the server\n"
                            "    req = urllib.request.Request(\"http://ai-service/summarize\", data=data)\n"
                            "    response = urllib.request.urlopen(req)\n"
                            "    return response.read().decode('utf-8')"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Protects requests with timeouts', 'input': '', 'expected': 'timeout=', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Missing timeout parameter in urllib urlopen call, which can hang the server\n"
                    "    req = urllib.request.Request(\"http://ai-service/summarize\", data=data)\n"
                    "    response = urllib.request.urlopen(req)"
                ),
                'suspected_component': 'ai_summary.py',
                'ai_suggestions': [
                    'Specify a timeout (e.g. `timeout=5`) when calling `urllib.request.urlopen(req, timeout=5)`.'
                ]
            },
            {
                'id': 24,
                'title': '24. Smart Assignment',
                'description': 'Automatically assign bugs to the developer with the fewest open bugs. The sorting comparator returns wrong sorting order.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'Algorithms',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'assigner.py',
                        'content': (
                            "def find_best_developer(developers):\n"
                            "    # Developers is a list of dicts: [{'name': 'DevA', 'open_bugs': 5}, ...]\n"
                            "    # BUG: Sorting in reverse order (descending by open_bugs) assigns to the developer with the most bugs!\n"
                            "    sorted_devs = sorted(developers, key=lambda d: d['open_bugs'], reverse=True)\n"
                            "    return sorted_devs[0]"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Finds developer with minimum workload', 'input': '', 'expected': 'reverse=False', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Sorting in reverse order (descending by open_bugs) assigns to the developer with the most bugs!\n"
                    "    sorted_devs = sorted(developers, key=lambda d: d['open_bugs'], reverse=True)"
                ),
                'suspected_component': 'assigner.py',
                'ai_suggestions': [
                    'Change `reverse=True` to `reverse=False` (or remove it) to sort developers ascending by workload.'
                ]
            },
            {
                'id': 25,
                'title': '25. Real-Time Collaboration',
                'description': 'WebSocket consumer to broadcast status updates. The handler calls sync database queries inside an async context.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'WebSockets',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'consumers.py',
                        'content': (
                            "from channels.generic.websocket import AsyncWebsocketConsumer\n"
                            "from .models import Bug\n\n"
                            "class BugConsumer(AsyncWebsocketConsumer):\n"
                            "    async def receive(self, text_data):\n"
                            "        # BUG: Accessing Django ORM synchronously inside an async method without database_sync_to_async!\n"
                            "        bug = Bug.objects.get(id=1)\n"
                            "        await self.send(text_data=bug.title)"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Wrap sync DB operations safely', 'input': '', 'expected': 'database_sync_to_async', 'passed': False }
                ],
                'bug_signature': (
                    "        # BUG: Accessing Django ORM synchronously inside an async method without database_sync_to_async!\n"
                    "        bug = Bug.objects.get(id=1)"
                ),
                'suspected_component': 'consumers.py',
                'ai_suggestions': [
                    'Use `database_sync_to_async` decorator or wrapper to safely fetch database records in async views.'
                ]
            },
            {
                'id': 26,
                'title': '26. Version History',
                'description': 'Track version history. The history saver saves updates but contains a race condition.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'Database',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'history.py',
                        'content': (
                            "from django.db import transaction\n"
                            "from .models import Bug, BugHistory\n\n"
                            "def create_bug_version(bug_id, change_notes):\n"
                            "    with transaction.atomic():\n"
                            "        # BUG: Fetching row without select_for_update() allows race condition in concurrent updates!\n"
                            "        bug = Bug.objects.get(id=bug_id)\n"
                            "        latest_version = bug.version\n"
                            "        bug.version = latest_version + 1\n"
                            "        bug.save()\n"
                            "        BugHistory.objects.create(bug=bug, version=bug.version, notes=change_notes)"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Locks records for update', 'input': '', 'expected': 'select_for_update()', 'passed': False }
                ],
                'bug_signature': (
                    "        # BUG: Fetching row without select_for_update() allows race condition in concurrent updates!\n"
                    "        bug = Bug.objects.get(id=bug_id)"
                ),
                'suspected_component': 'history.py',
                'ai_suggestions': [
                    'Use `select_for_update()` to lock the row during version update: `Bug.objects.select_for_update().get(id=bug_id)`.'
                ]
            },
            {
                'id': 27,
                'title': '27. Project Analytics',
                'description': 'Render analytical charts. If the list of data points is empty, the chart component crashes with a Division by Zero.',
                'difficulty': 'Hard',
                'technology': 'React',
                'category': 'Analytics',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'AnalyticsChart.jsx',
                        'content': (
                            "import React from 'react';\n\n"
                            "export default function AnalyticsChart({ dataPoints }) {\n"
                            "  // BUG: Division by zero when calculating average if dataPoints is empty!\n"
                            "  const sum = dataPoints.reduce((acc, p) => acc + p.value, 0);\n"
                            "  const average = sum / dataPoints.length;\n\n"
                            "  return (\n"
                            "    <div className=\"analytics-card\">\n"
                            "      <h3>Average Resolution: {average} mins</h3>\n"
                            "    </div>\n"
                            "  );\n"
                            "}"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Handles empty data lists safely', 'input': '', 'expected': 'dataPoints.length === 0', 'passed': False }
                ],
                'bug_signature': (
                    "  // BUG: Division by zero when calculating average if dataPoints is empty!\n"
                    "  const sum = dataPoints.reduce((acc, p) => acc + p.value, 0);\n"
                    "  const average = sum / dataPoints.length;"
                ),
                'suspected_component': 'AnalyticsChart.jsx',
                'ai_suggestions': [
                    'Add a length check before dividing: `const average = dataPoints.length === 0 ? 0 : sum / dataPoints.length;`.'
                ]
            },
            {
                'id': 28,
                'title': '28. AI Bug Fix Suggestions',
                'description': 'Send context to AI to suggest a fix. The OpenAI API call uses a deprecated model name which is no longer supported.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'AI Integration',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'ai_fixer.py',
                        'content': (
                            "def get_ai_suggestions(bug_code):\n"
                            "    # BUG: Using deprecated model 'text-davinci-003' which is shut down\n"
                            "    payload = {\n"
                            "        \"model\": \"text-davinci-003\",\n"
                            "        \"prompt\": f\"Fix this code:\\n{bug_code}\",\n"
                            "        \"max_tokens\": 150\n"
                            "    }\n"
                            "    return payload"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Uses supported OpenAI model', 'input': '', 'expected': 'gpt-4', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Using deprecated model 'text-davinci-003' which is shut down\n"
                    "    payload = {\n"
                    "        \"model\": \"text-davinci-003\","
                ),
                'suspected_component': 'ai_fixer.py',
                'ai_suggestions': [
                    'Change the model name to a modern model such as `"gpt-4"`, `"gpt-3.5-turbo"` or `"gpt-4o"`.'
                ]
            },
            {
                'id': 29,
                'title': '29. Full Audit System',
                'description': 'Retrieve client IP address for the audit log. The code reads the wrong HTTP header or doesn\'t split proxies correctly.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'Security',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'audit.py',
                        'content': (
                            "def get_client_ip(request):\n"
                            "    # BUG: Reading HTTP_X_FORWARDED_FOR directly without fallback or splitting multiple proxies\n"
                            "    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')\n"
                            "    ip = x_forwarded_for\n"
                            "    return ip"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Reads client IP addresses correctly', 'input': '', 'expected': 'REMOTE_ADDR', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Reading HTTP_X_FORWARDED_FOR directly without fallback or splitting multiple proxies\n"
                    "    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')\n"
                    "    ip = x_forwarded_for\n"
                    "    return ip"
                ),
                'suspected_component': 'audit.py',
                'ai_suggestions': [
                    'Extract the first IP in the list from X-Forwarded-For if available, or fall back to REMOTE_ADDR: `ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.META.get("REMOTE_ADDR")`.'
                ]
            },
            {
                'id': 30,
                'title': '30. Production-Ready Improvements',
                'description': 'Prevent SQL injection in search parameters. The code uses raw raw SQL formatting instead of parameters.',
                'difficulty': 'Hard',
                'technology': 'Django',
                'category': 'Security',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [
                    {
                        'name': 'search.py',
                        'content': (
                            "from django.db import connection\n\n"
                            "def search_bug_reports(query):\n"
                            "    # BUG: Raw string formatting in query opens SQL injection vulnerability!\n"
                            "    raw_query = f\"SELECT * FROM buggyman_challenge WHERE title LIKE '%{query}%'\"\n"
                            "    with connection.cursor() as cursor:\n"
                            "        cursor.execute(raw_query)\n"
                            "        return cursor.fetchall()"
                        )
                    }
                ],
                'test_cases': [
                    { 'id': 1, 'name': 'Prevents raw SQL formatting vulnerabilities', 'input': '', 'expected': '%s', 'passed': False }
                ],
                'bug_signature': (
                    "    # BUG: Raw string formatting in query opens SQL injection vulnerability!\n"
                    "    raw_query = f\"SELECT * FROM buggyman_challenge WHERE title LIKE '%{query}%'\""
                ),
                'suspected_component': 'search.py',
                'ai_suggestions': [
                    'Pass values as parameters in the execute call to automatically escape inputs: `cursor.execute("SELECT * FROM buggyman_challenge WHERE title LIKE %s", [f"%{query}%"])`.'
                ]
            }
        ]

        SELECTED_CATALOG_IDS = {2, 4, 5, 12, 14, 17, 19, 22, 24, 30}
        for c_data in challenges_data:
            c_status = 'published' if c_data['id'] in SELECTED_CATALOG_IDS else 'archived'
            Challenge.objects.create(
                id=c_data['id'],
                title=c_data['title'],
                description=c_data['description'],
                status=c_status,
                difficulty=c_data['difficulty'],
                technology=c_data['technology'],
                category=c_data['category'],
                time_estimate=c_data['time_estimate'],
                points=c_data['points'],
                files=c_data['files'],
                test_cases=c_data['test_cases'],
                bug_signature=c_data['bug_signature'],
                suspected_component=c_data['suspected_component'],
                ai_suggestions=c_data['ai_suggestions']
            )

        # 4. Create Notifications for Jane Doe
        notifications_data = [
            { 'id': 1, 'title': 'Achievement Unlocked', 'message': 'You have earned the "Five Day Streak" badge! Keep it up.', 'type': 'achievement', 'read': False, 'time': '2 hours ago' },
            { 'id': 2, 'title': 'New Challenge Out', 'message': 'A new React custom hook challenge is now available: "Fix useFetch Hook".', 'type': 'challenge', 'read': False, 'time': '5 hours ago' },
            { 'id': 3, 'title': 'Weekly Leaderboard Updated', 'message': 'See your placement on the global weekly debugging ranks.', 'type': 'system', 'read': True, 'time': '1 day ago' }
        ]

        for n_data in notifications_data:
            Notification.objects.get_or_create(
                id=n_data['id'],
                user=user,
                defaults={
                    'title': n_data['title'],
                    'message': n_data['message'],
                    'type': n_data['type'],
                    'read': n_data['read'],
                    'time': n_data['time']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
