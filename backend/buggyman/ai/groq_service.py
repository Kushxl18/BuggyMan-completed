import os
import json
import urllib.request
import urllib.error
from buggyman.constants import get_groq_api_key, get_groq_model, get_groq_base_url, HINT_COSTS

class AIHintService:
    """
    Service layer abstracting Groq AI provider for BuggyMan progressive hints.
    Behaves as a 'Debugging Mentor' — helps users reason about bugs without giving away full copy-paste solutions.
    """

    @classmethod
    def generate_hint(cls, challenge, user_code, test_results, level):
        """
        Generates progressive debugging hint (Level 1, 2, or 3) via Groq API.
        """
        api_key = get_groq_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'AI assistance is temporarily unavailable (Groq API key not configured). Your BugBytes were not deducted.'
            }

        model = get_groq_model()
        base_url = get_groq_base_url()

        # 1. Normalize challenge details
        c_title = getattr(challenge, 'title', '')
        c_desc = getattr(challenge, 'description', '')
        c_tech = getattr(challenge, 'technology', '')
        c_cat = getattr(challenge, 'category', '')
        c_diff = getattr(challenge, 'difficulty', '')
        c_component = getattr(challenge, 'suspected_component', '')

        # Filter test results to send only non-sensitive summary
        sanitized_tests = []
        if test_results and isinstance(test_results, list):
            for t in test_results[:5]:
                sanitized_tests.append({
                    'name': t.get('name', 'Test'),
                    'passed': t.get('passed', False),
                    'actual': str(t.get('actual', ''))[:200],
                    'error': str(t.get('error', ''))[:200] if t.get('error') else None
                })

        # 2. Build level-specific instruction
        level_instructions = {
            1: (
                "LEVEL 1 CONCEPTUAL HINT:\n"
                "- Goal: Explain the underlying software engineering concept and common pitfalls.\n"
                "- DO NOT mention specific lines of code or exact variable names.\n"
                "- Help the user understand what theoretical concept applies to this bug."
            ),
            2: (
                "LEVEL 2 DIRECTIONAL HINT:\n"
                "- Goal: Direct the user's attention to the specific function, component, or query section.\n"
                "- Explain how the inputs or state flow through the failing component.\n"
                "- Do NOT provide the code solution."
            ),
            3: (
                "LEVEL 3 DETAILED HINT:\n"
                "- Goal: Explain the exact logic flaw and provide targeted pseudocode or structural guidance.\n"
                "- Point out the exact bug pattern, but FORCE the user to implement the final fixed code themselves.\n"
                "- NEVER write the complete final replacement code."
            )
        }

        inst = level_instructions.get(level, level_instructions[1])

        system_prompt = (
            "You are BuggyMan AI, an expert, encouraging Debugging Mentor for software developers.\n"
            "Your role is to guide users to debug their own code.\n"
            "RULES:\n"
            "1. NEVER give a full copy-paste final solution or complete replacement code.\n"
            "2. NEVER reveal hidden tests or backend secrets.\n"
            "3. Keep your response concise, clear, and formatted in Markdown.\n"
            f"{inst}"
        )

        user_prompt = (
            f"CHALLENGE: {c_title} ({c_tech} / {c_cat} - {c_diff})\n"
            f"SUSPECTED COMPONENT: {c_component}\n"
            f"DESCRIPTION: {c_desc[:400]}\n\n"
            f"USER CURRENT ATTEMPT CODE:\n```\n{user_code[:1500]}\n```\n\n"
            f"EVALUATION TEST RESULTS:\n{json.dumps(sanitized_tests, indent=2)}\n\n"
            f"Please generate the requested Level {level} Debugging Hint."
        )

        url = f"{base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 600
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BuggyMan/1.0"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                res_body = json.loads(resp.read().decode('utf-8'))
                choice_msg = res_body['choices'][0]['message']
                hint_text = (choice_msg.get('content') or choice_msg.get('reasoning') or '').strip()

                if not hint_text:
                    return {
                        'success': False,
                        'error': 'AI assistance returned an empty response. Your BugBytes were not deducted.'
                    }

                return {
                    'success': True,
                    'hint': hint_text
                }

        except urllib.error.HTTPError as he:
            return {
                'success': False,
                'error': 'AI assistance is temporarily unavailable. Your BugBytes were not deducted.'
            }
        except Exception as ex:
            return {
                'success': False,
                'error': 'AI assistance is temporarily unavailable. Your BugBytes were not deducted.'
            }
