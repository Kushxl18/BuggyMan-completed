from django.core.management.base import BaseCommand
from buggyman.models import FeatureChallenge

class Command(BaseCommand):
    help = 'Seeds initial Feature Implementation Arena challenges'

    def handle(self, *args, **options):
        challenges_data = [
            {
                'title': 'API Sliding-Window Rate Limiting Middleware',
                'slug': 'api-sliding-window-rate-limiter',
                'category': 'Backend',
                'difficulty': 'Medium',
                'technology': 'Python / FastAPI',
                'time_estimate': '30 mins',
                'points': 175,
                'bugbytes_reward': 40,
                'description': 'Implement an in-memory sliding-window rate limiter middleware for a high-throughput API gateway service. The middleware must track request bursts accurately without fixed-window boundary spikes, append diagnostic headers, support IP whitelisting, and prune expired memory timestamps.',
                'feature_request': """### Feature Request: Sliding-Window Rate Limiter

Our API gateway currently lacks protection against abusive traffic spikes and brute-force attacks. We need an in-memory sliding-window rate limiter middleware implemented in `app/middleware/rate_limiter.py`.

#### Requirements:
1. **Sliding Window Tracking**: For each incoming client IP, record request timestamps within a sliding window of `window_seconds`.
2. **Limit Enforcement**: Reject requests that exceed `max_requests` in the window with HTTP status code `429` and body `{"error": "Too Many Requests"}`.
3. **Response Headers**:
   - `X-RateLimit-Limit`: Maximum requests permitted per window.
   - `X-RateLimit-Remaining`: Count of remaining requests allowed within current window.
   - `X-RateLimit-Reset`: Seconds remaining until oldest request in window slides out.
4. **IP Whitelisting**: If client IP is listed in `WHITELIST_IPS`, bypass rate checks completely.
5. **Memory Pruning**: Automatically purge timestamps older than `window_seconds` during evaluation to prevent unbounded memory growth.
""",
                'requirements': [
                    {'id': 'req-1', 'title': 'Sliding Window Algorithm', 'description': 'Track timestamps per IP in a deque/list and count requests within window_seconds.'},
                    {'id': 'req-2', 'title': 'HTTP 429 Rejection', 'description': 'Return status 429 when max_requests threshold is breached.'},
                    {'id': 'req-3', 'title': 'Rate Limit Headers', 'description': 'Include X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers on all responses.'},
                    {'id': 'req-4', 'title': 'IP Whitelist', 'description': 'Bypass rate limits for addresses in WHITELIST_IPS (e.g. 127.0.0.1, internal-service).'},
                    {'id': 'req-5', 'title': 'Memory Pruning', 'description': 'Remove timestamps older than now - window_seconds on each evaluation.'}
                ],
                'acceptance_criteria': [
                    'Requests within max_requests return HTTP 200 with X-RateLimit-Remaining decreasing.',
                    'The (max_requests + 1)-th request within window_seconds returns status 429.',
                    'Whitelisted IPs never receive status 429 even under high volume.',
                    'Expired timestamps are discarded when new requests arrive.',
                    'X-RateLimit-Reset accurately reflects seconds until window clears.'
                ],
                'initial_files': [
                    {
                        'name': 'app/middleware/rate_limiter.py',
                        'readonly': False,
                        'is_entrypoint': True,
                        'content': '''import time
from collections import defaultdict

class SlidingWindowRateLimiter:
    """
    In-memory Sliding Window Rate Limiter.
    Tracks client request timestamps and enforces rate limits.
    """
    def __init__(self, max_requests=5, window_seconds=60, whitelist=None):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.whitelist = set(whitelist or [])
        # Map: ip_address -> list of timestamps
        self.records = defaultdict(list)

    def is_allowed(self, ip_address: str, current_time: float = None):
        """
        Evaluates whether a request from ip_address is permitted.
        
        Returns:
            tuple: (is_allowed: bool, headers: dict)
        """
        now = current_time if current_time is not None else time.time()
        
        # TODO: Check if IP is in whitelist
        if ip_address in self.whitelist:
            return True, {
                'X-RateLimit-Limit': str(self.max_requests),
                'X-RateLimit-Remaining': str(self.max_requests),
                'X-RateLimit-Reset': '0'
            }

        # TODO: Prune timestamps older than (now - self.window_seconds)
        timestamps = self.records[ip_address]
        cutoff = now - self.window_seconds
        valid_timestamps = [t for t in timestamps if t > cutoff]
        self.records[ip_address] = valid_timestamps

        # TODO: Check if request limit reached
        if len(valid_timestamps) >= self.max_requests:
            oldest = valid_timestamps[0]
            reset_time = max(0, int(self.window_seconds - (now - oldest)))
            return False, {
                'X-RateLimit-Limit': str(self.max_requests),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(reset_time)
            }

        # TODO: Record new timestamp and return remaining count
        valid_timestamps.append(now)
        remaining = self.max_requests - len(valid_timestamps)
        reset_time = int(self.window_seconds)
        if valid_timestamps:
            reset_time = max(0, int(self.window_seconds - (now - valid_timestamps[0])))

        return True, {
            'X-RateLimit-Limit': str(self.max_requests),
            'X-RateLimit-Remaining': str(remaining),
            'X-RateLimit-Reset': str(reset_time)
        }

    def reset(self, ip_address: str = None):
        """Clears records for a given IP or all IPs."""
        if ip_address:
            self.records.pop(ip_address, None)
        else:
            self.records.clear()
'''
                    },
                    {
                        'name': 'app/config.py',
                        'readonly': True,
                        'is_entrypoint': False,
                        'content': '''# Application Rate Limit Configuration
DEFAULT_MAX_REQUESTS = 5
DEFAULT_WINDOW_SECONDS = 60
WHITELIST_IPS = ["127.0.0.1", "localhost", "internal-cron"]
'''
                    },
                    {
                        'name': 'app/main.py',
                        'readonly': True,
                        'is_entrypoint': False,
                        'content': '''from app.middleware.rate_limiter import SlidingWindowRateLimiter
from app.config import DEFAULT_MAX_REQUESTS, DEFAULT_WINDOW_SECONDS, WHITELIST_IPS

limiter = SlidingWindowRateLimiter(
    max_requests=DEFAULT_MAX_REQUESTS,
    window_seconds=DEFAULT_WINDOW_SECONDS,
    whitelist=WHITELIST_IPS
)

def dispatch_request(client_ip, current_time=None):
    allowed, headers = limiter.is_allowed(client_ip, current_time)
    if not allowed:
        return 429, {"error": "Too Many Requests"}, headers
    return 200, {"status": "ok"}, headers
'''
                    }
                ],
                'test_cases': [
                    {
                        'id': 1,
                        'name': 'Requests under limit are permitted',
                        'type': 'feature',
                        'test_code': '''from app.middleware.rate_limiter import SlidingWindowRateLimiter
limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
allowed, h1 = limiter.is_allowed("192.168.1.1", current_time=100.0)
assert allowed is True, "First request must be allowed"
assert h1.get("X-RateLimit-Remaining") == "2", "Remaining requests should be 2"

allowed, h2 = limiter.is_allowed("192.168.1.1", current_time=101.0)
assert allowed is True, "Second request must be allowed"
assert h2.get("X-RateLimit-Remaining") == "1", "Remaining requests should be 1"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 2,
                        'name': 'Enforces 429 when max_requests exceeded',
                        'type': 'feature',
                        'test_code': '''from app.middleware.rate_limiter import SlidingWindowRateLimiter
limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10)
limiter.is_allowed("10.0.0.5", current_time=100.0)
limiter.is_allowed("10.0.0.5", current_time=101.0)
allowed, h = limiter.is_allowed("10.0.0.5", current_time=102.0)
assert allowed is False, "Third request must be blocked"
assert h.get("X-RateLimit-Remaining") == "0", "Remaining should be 0 when blocked"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 3,
                        'name': 'IP Whitelist bypass verification',
                        'type': 'regression',
                        'test_code': '''from app.middleware.rate_limiter import SlidingWindowRateLimiter
limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=10, whitelist=["127.0.0.1"])
for i in range(10):
    allowed, _ = limiter.is_allowed("127.0.0.1", current_time=100.0 + i)
    assert allowed is True, f"Whitelisted IP must never be blocked (call {i+1})"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 4,
                        'name': 'Sliding window timestamp expiration',
                        'type': 'hidden',
                        'test_code': '''from app.middleware.rate_limiter import SlidingWindowRateLimiter
limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10)
limiter.is_allowed("172.16.0.1", current_time=10.0)
limiter.is_allowed("172.16.0.1", current_time=12.0)
# Next immediate call is blocked
allowed_block, _ = limiter.is_allowed("172.16.0.1", current_time=15.0)
assert allowed_block is False, "Should be blocked within the 10s window"

# Move past window (10.0 + 10s = 20.0s)
allowed_after, h = limiter.is_allowed("172.16.0.1", current_time=21.0)
assert allowed_after is True, "Oldest timestamp must have slid out, permitting new request"
''',
                        'is_hidden': True
                    },
                    {
                        'id': 5,
                        'name': 'Client IP Isolation & Memory Cleanup',
                        'type': 'security',
                        'test_code': '''from app.middleware.rate_limiter import SlidingWindowRateLimiter
limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=5)
limiter.is_allowed("ip-alpha", current_time=1.0)
# ip-alpha is blocked
assert limiter.is_allowed("ip-alpha", current_time=2.0)[0] is False
# ip-beta must NOT be blocked by ip-alpha's usage
assert limiter.is_allowed("ip-beta", current_time=2.0)[0] is True
''',
                        'is_hidden': False
                    }
                ],
                'scoring_config': {
                    'feature_weight': 40,
                    'hidden_weight': 25,
                    'regression_weight': 15,
                    'quality_weight': 10,
                    'security_weight': 10
                },
                'ai_hints': [
                    {'level': 1, 'cost': 5, 'title': 'Timestamp Pruning Nudge', 'content': 'Calculate cutoff = current_time - window_seconds and filter your list to keep only t > cutoff.'},
                    {'level': 2, 'cost': 10, 'title': 'X-RateLimit-Reset Calculation', 'content': 'Reset time is window_seconds minus the elapsed time since the oldest valid timestamp in the list.'},
                    {'level': 3, 'cost': 15, 'title': 'Whitelist Handling', 'content': 'Check if ip_address is in self.whitelist at the very beginning of is_allowed before touching timestamps.'}
                ],
                'ai_context': 'The rate limiter operates as an in-memory sliding window algorithm. It lives in app/middleware/rate_limiter.py and is configured via app/config.py. It tracks lists of floats in a dictionary.'
            },
            {
                'title': 'JWT Refresh Token Rotation & Revocation Service',
                'slug': 'jwt-refresh-token-rotation',
                'category': 'Backend',
                'difficulty': 'Hard',
                'technology': 'Python / FastAPI',
                'time_estimate': '40 mins',
                'points': 225,
                'bugbytes_reward': 50,
                'description': 'Architect a secure token rotation service that detects refresh token theft. When a token is refreshed, issue a new pair and invalidate the old token. If an already-used refresh token is presented, revoke the entire token family.',
                'feature_request': """### Feature Request: Refresh Token Rotation & Family Revocation

To prevent stolen refresh token replay attacks, implement token family tracking in `services/token_manager.py`.

#### Requirements:
1. **Token Issuance**: `create_token_family(user_id)` generates a `family_id` and initial `refresh_token`.
2. **Rotation**: `rotate_refresh_token(old_token)` issues a new `refresh_token` and marks `old_token` as used.
3. **Theft Detection**: If an already-used `refresh_token` is submitted, invalidate the entire token family and raise `SecurityBreachError`.
4. **Validation**: `verify_token(token)` checks validity and expiration.
""",
                'requirements': [
                    {'id': 'req-1', 'title': 'Token Rotation', 'description': 'Invalidate old refresh token and return newly issued token.'},
                    {'id': 'req-2', 'title': 'Family Revocation', 'description': 'Revoke all tokens in family if an already-used token is re-submitted.'},
                    {'id': 'req-3', 'title': 'Expiration Enforcement', 'description': 'Reject tokens past their TTL.'}
                ],
                'acceptance_criteria': [
                    'Valid refresh token returns a new token pair and marks previous as used.',
                    'Submitting a previously used token raises SecurityBreachError and revokes the family.',
                    'Subsequent calls with any token from that revoked family return False.'
                ],
                'initial_files': [
                    {
                        'name': 'services/token_manager.py',
                        'readonly': False,
                        'is_entrypoint': True,
                        'content': '''import time
import uuid

class SecurityBreachError(Exception):
    """Raised when an already-used refresh token is re-submitted."""
    pass

class TokenManager:
    def __init__(self, token_ttl_seconds=3600):
        self.token_ttl = token_ttl_seconds
        # family_id -> { "revoked": bool, "user_id": str }
        self.families = {}
        # token -> { "family_id": str, "used": bool, "expires_at": float }
        self.tokens = {}

    def create_token_family(self, user_id: str, current_time: float = None):
        now = current_time if current_time is not None else time.time()
        family_id = str(uuid.uuid4())
        initial_token = f"rt_{uuid.uuid4().hex}"

        self.families[family_id] = {"revoked": False, "user_id": user_id}
        self.tokens[initial_token] = {
            "family_id": family_id,
            "used": False,
            "expires_at": now + self.token_ttl
        }
        return {"family_id": family_id, "refresh_token": initial_token}

    def rotate_refresh_token(self, old_token: str, current_time: float = None):
        now = current_time if current_time is not None else time.time()
        
        token_data = self.tokens.get(old_token)
        if not token_data:
            return None, "Invalid token"

        family_id = token_data["family_id"]
        family = self.families.get(family_id)

        # Check if family is revoked
        if not family or family["revoked"]:
            return None, "Token family revoked"

        # Check expiration
        if now > token_data["expires_at"]:
            return None, "Token expired"

        # Check for token reuse / theft
        if token_data["used"]:
            # SECURITY BREACH: Token reuse detected! Revoke whole family
            family["revoked"] = True
            raise SecurityBreachError(f"Token reuse detected for family {family_id}")

        # Mark old token as used
        token_data["used"] = True

        # Issue new token in same family
        new_token = f"rt_{uuid.uuid4().hex}"
        self.tokens[new_token] = {
            "family_id": family_id,
            "used": False,
            "expires_at": now + self.token_ttl
        }
        return {"refresh_token": new_token, "family_id": family_id}, None

    def is_token_valid(self, token: str, current_time: float = None):
        now = current_time if current_time is not None else time.time()
        token_data = self.tokens.get(token)
        if not token_data or token_data["used"]:
            return False
        if now > token_data["expires_at"]:
            return False
        family = self.families.get(token_data["family_id"])
        return bool(family and not family["revoked"])
'''
                    }
                ],
                'test_cases': [
                    {
                        'id': 1,
                        'name': 'Initial Token Creation & Validity',
                        'type': 'feature',
                        'test_code': '''from services.token_manager import TokenManager
mgr = TokenManager()
res = mgr.create_token_family("user-1", current_time=100.0)
token = res["refresh_token"]
assert mgr.is_token_valid(token, current_time=100.0) is True, "New token must be valid"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 2,
                        'name': 'Token Rotation Returns Fresh Token',
                        'type': 'feature',
                        'test_code': '''from services.token_manager import TokenManager
mgr = TokenManager()
t1 = mgr.create_token_family("user-1", current_time=100.0)["refresh_token"]
rot_res, err = mgr.rotate_refresh_token(t1, current_time=105.0)
assert err is None, "Rotation must succeed"
t2 = rot_res["refresh_token"]
assert t1 != t2, "New token must differ from old token"
assert mgr.is_token_valid(t1, current_time=106.0) is False, "Old token must no longer be valid"
assert mgr.is_token_valid(t2, current_time=106.0) is True, "New token must be valid"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 3,
                        'name': 'Theft Detection Triggers Family Revocation',
                        'type': 'security',
                        'test_code': '''from services.token_manager import TokenManager, SecurityBreachError
mgr = TokenManager()
t1 = mgr.create_token_family("user-1", current_time=100.0)["refresh_token"]
rot, _ = mgr.rotate_refresh_token(t1, current_time=101.0)
t2 = rot["refresh_token"]

# Attacker attempts to replay already-used t1
breach_caught = False
try:
    mgr.rotate_refresh_token(t1, current_time=102.0)
except SecurityBreachError:
    breach_caught = True

assert breach_caught is True, "Replaying used token must raise SecurityBreachError"
# After breach, legitimate t2 must also be invalid
assert mgr.is_token_valid(t2, current_time=103.0) is False, "Entire family must be revoked on breach"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 4,
                        'name': 'Expired Token Rejection',
                        'type': 'regression',
                        'test_code': '''from services.token_manager import TokenManager
mgr = TokenManager(token_ttl_seconds=60)
t = mgr.create_token_family("user-1", current_time=100.0)["refresh_token"]
assert mgr.is_token_valid(t, current_time=170.0) is False, "Expired token must be rejected"
''',
                        'is_hidden': False
                    },
                    {
                        'id': 5,
                        'name': 'Multi-Family Isolation Check',
                        'type': 'hidden',
                        'test_code': '''from services.token_manager import TokenManager, SecurityBreachError
mgr = TokenManager()
user_a_token = mgr.create_token_family("user-a")["refresh_token"]
user_b_token = mgr.create_token_family("user-b")["refresh_token"]

# Rotate user A
rot_a, _ = mgr.rotate_refresh_token(user_a_token)
# Trigger breach on user A
try:
    mgr.rotate_refresh_token(user_a_token)
except SecurityBreachError:
    pass

# User B must NOT be affected by User A breach
assert mgr.is_token_valid(user_b_token) is True, "User B token family must remain valid"
''',
                        'is_hidden': True
                    }
                ],
                'scoring_config': {
                    'feature_weight': 40,
                    'hidden_weight': 25,
                    'regression_weight': 15,
                    'quality_weight': 10,
                    'security_weight': 10
                },
                'ai_hints': [
                    {'level': 1, 'cost': 5, 'title': 'Tracking Used Status', 'content': 'Ensure each token record stores a boolean used flag that flips to True on rotation.'},
                    {'level': 2, 'cost': 10, 'title': 'Family Revocation Flag', 'content': 'Store a revoked boolean flag on each family object so you can invalidate all tokens at once.'},
                    {'level': 3, 'cost': 15, 'title': 'SecurityBreachError Logic', 'content': 'If token_data["used"] is True, set family["revoked"] = True and immediately raise SecurityBreachError.'}
                ],
                'ai_context': 'TokenManager tracks token families and tokens. It defends against refresh token theft by revoking the whole family when an old token is reused.'
            },
            {
                'title': 'Cart State Machine with Undo / Redo & Local Storage Sync',
                'slug': 'cart-state-machine-undo-redo',
                'category': 'Frontend',
                'difficulty': 'Medium',
                'technology': 'React / JavaScript',
                'time_estimate': '35 mins',
                'points': 160,
                'bugbytes_reward': 35,
                'description': 'Construct an immutable cart state reducer supporting dynamic item additions, updates, deletions, and an undo/redo time-travel history stack with 20-step limits.',
                'feature_request': """### Feature Request: Undo/Redo Shopping Cart State Machine

Implement the core cart state logic in `src/cartReducer.js` to enable optimistic UI updates with full Undo and Redo capability.

#### Requirements:
1. **Actions**:
   - `ADD_ITEM`: adds new item or increments quantity if item with same `id` exists.
   - `REMOVE_ITEM`: removes item by `id`.
   - `UPDATE_QTY`: sets exact quantity for an item (if qty <= 0, remove).
   - `UNDO`: restores previous state from past history.
   - `REDO`: reapplies undone state from future history.
   - `CLEAR`: empties cart and clears future stack.
2. **History Boundary**: Max history depth is 20 past states.
""",
                'requirements': [
                    {'id': 'req-1', 'title': 'Immutable Cart Operations', 'description': 'Support ADD, REMOVE, UPDATE_QTY without mutating state.'},
                    {'id': 'req-2', 'title': 'Undo/Redo Time Travel', 'description': 'Push states to past stack on change and pop on UNDO/REDO.'},
                    {'id': 'req-3', 'title': 'Quantity Calculations', 'description': 'Compute totalItems and subtotal correctly.'}
                ],
                'acceptance_criteria': [
                    'Adding item updates items array and records past state.',
                    'Dispatching UNDO restores previous cart items.',
                    'Dispatching REDO restores the state undone.',
                    'Past history does not exceed 20 entries.'
                ],
                'initial_files': [
                    {
                        'name': 'src/cartReducer.js',
                        'readonly': False,
                        'is_entrypoint': True,
                        'content': '''// Cart State Machine with Undo/Redo Support
export const initialCartState = {
  items: [], // [{ id, name, price, quantity }]
  past: [],  // array of past items snapshots (max 20)
  future: [] // array of future items snapshots
};

export function cartReducer(state = initialCartState, action) {
  switch (action.type) {
    case 'ADD_ITEM': {
      const { item } = action.payload;
      const existing = state.items.find(i => i.id === item.id);
      let newItems;
      if (existing) {
        newItems = state.items.map(i =>
          i.id === item.id ? { ...i, quantity: i.quantity + (item.quantity || 1) } : i
        );
      } else {
        newItems = [...state.items, { ...item, quantity: item.quantity || 1 }];
      }
      const newPast = [...state.past, state.items].slice(-20);
      return {
        items: newItems,
        past: newPast,
        future: []
      };
    }
    case 'REMOVE_ITEM': {
      const { id } = action.payload;
      const newItems = state.items.filter(i => i.id !== id);
      const newPast = [...state.past, state.items].slice(-20);
      return {
        items: newItems,
        past: newPast,
        future: []
      };
    }
    case 'UPDATE_QTY': {
      const { id, quantity } = action.payload;
      if (quantity <= 0) {
        return cartReducer(state, { type: 'REMOVE_ITEM', payload: { id } });
      }
      const newItems = state.items.map(i => i.id === id ? { ...i, quantity } : i);
      const newPast = [...state.past, state.items].slice(-20);
      return {
        items: newItems,
        past: newPast,
        future: []
      };
    }
    case 'UNDO': {
      if (state.past.length === 0) return state;
      const previous = state.past[state.past.length - 1];
      const newPast = state.past.slice(0, state.past.length - 1);
      return {
        items: previous,
        past: newPast,
        future: [state.items, ...state.future]
      };
    }
    case 'REDO': {
      if (state.future.length === 0) return state;
      const next = state.future[0];
      const newFuture = state.future.slice(1);
      return {
        items: next,
        past: [...state.past, state.items],
        future: newFuture
      };
    }
    case 'CLEAR': {
      return {
        items: [],
        past: [...state.past, state.items].slice(-20),
        future: []
      };
    }
    default:
      return state;
  }
}

export function computeCartTotals(items = []) {
  const totalItems = items.reduce((sum, item) => sum + (item.quantity || 0), 0);
  const subtotal = items.reduce((sum, item) => sum + ((item.price || 0) * (item.quantity || 0)), 0);
  return { totalItems, subtotal: Math.round(subtotal * 100) / 100 };
}
'''
                    }
                ],
                'test_cases': [
                    {
                        'id': 1,
                        'name': 'ADD_ITEM and Totals Calculation',
                        'type': 'feature',
                        'code': '''
const { cartReducer, computeCartTotals, initialCartState } = require('./src/cartReducer.js');
let s = cartReducer(initialCartState, { type: 'ADD_ITEM', payload: { item: { id: 1, name: 'Widget', price: 10 } } });
if (s.items.length !== 1) throw new Error('Expected 1 item in cart');
const totals = computeCartTotals(s.items);
if (totals.totalItems !== 1 || totals.subtotal !== 10) throw new Error('Incorrect totals');
''',
                        'is_hidden': False
                    },
                    {
                        'id': 2,
                        'name': 'UNDO and REDO Operations',
                        'type': 'feature',
                        'code': '''
const { cartReducer, initialCartState } = require('./src/cartReducer.js');
let s1 = cartReducer(initialCartState, { type: 'ADD_ITEM', payload: { item: { id: 1, name: 'A', price: 5 } } });
let s2 = cartReducer(s1, { type: 'ADD_ITEM', payload: { item: { id: 2, name: 'B', price: 15 } } });
if (s2.items.length !== 2) throw new Error('Expected 2 items');

// UNDO
let sUndo = cartReducer(s2, { type: 'UNDO' });
if (sUndo.items.length !== 1 || sUndo.items[0].id !== 1) throw new Error('Undo failed to revert to 1 item');

// REDO
let sRedo = cartReducer(sUndo, { type: 'REDO' });
if (sRedo.items.length !== 2) throw new Error('Redo failed to restore 2 items');
''',
                        'is_hidden': False
                    },
                    {
                        'id': 3,
                        'name': 'UPDATE_QTY with 0 Removes Item',
                        'type': 'regression',
                        'code': '''
const { cartReducer, initialCartState } = require('./src/cartReducer.js');
let s = cartReducer(initialCartState, { type: 'ADD_ITEM', payload: { item: { id: 1, name: 'A', price: 5 } } });
let sUpdated = cartReducer(s, { type: 'UPDATE_QTY', payload: { id: 1, quantity: 0 } });
if (sUpdated.items.length !== 0) throw new Error('Setting quantity to 0 must remove item');
''',
                        'is_hidden': False
                    },
                    {
                        'id': 4,
                        'name': 'History Stack Cap at 20',
                        'type': 'hidden',
                        'code': '''
const { cartReducer, initialCartState } = require('./src/cartReducer.js');
let s = initialCartState;
for (let i = 0; i < 30; i++) {
  s = cartReducer(s, { type: 'ADD_ITEM', payload: { item: { id: i, name: 'Item', price: 1 } } });
}
if (s.past.length > 20) throw new Error('Past history must not exceed 20 entries');
''',
                        'is_hidden': True
                    }
                ],
                'scoring_config': {
                    'feature_weight': 40,
                    'hidden_weight': 25,
                    'regression_weight': 15,
                    'quality_weight': 10,
                    'security_weight': 10
                },
                'ai_hints': [
                    {'level': 1, 'cost': 5, 'title': 'Array Slicing', 'content': 'Keep history capped using array.slice(-20).'},
                    {'level': 2, 'cost': 10, 'title': 'Undo Popping', 'content': 'When undoing, take the last element of past as current items, and prepend previous items to future.'},
                    {'level': 3, 'cost': 15, 'title': 'Redo Pushing', 'content': 'When redoing, take the first element of future and push current items into past.'}
                ],
                'ai_context': 'Redux-style cartReducer managing shopping cart states with an undo/redo time-travel history.'
            }
        ]

        count = 0
        for data in challenges_data:
            slug = data['slug']
            obj, created = FeatureChallenge.objects.update_or_create(
                slug=slug,
                defaults=data
            )
            count += 1
            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f"{action} FeatureChallenge: {obj.title} (ID: {obj.id})"))

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} Feature Challenges!"))
