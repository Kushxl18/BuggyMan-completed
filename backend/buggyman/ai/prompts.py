"""
Prompt formatting templates for BuggyMan AI Service
"""

def build_hint_prompt(context: dict) -> str:
    title = context.get('title', 'Coding Challenge')
    description = context.get('description', '')
    technology = context.get('technology', 'Programming')
    category = context.get('category', 'General')
    starter_code = context.get('starter_code', '')
    user_code = context.get('user_code', '')
    test_results = context.get('test_results', [])
    previous_hints = context.get('previous_hints', [])

    hint_level = context.get('level', len(previous_hints) + 1)
    hint_level = min(3, max(1, hint_level))

    prompt = f"""You are BuggyMan AI, an expert debugging mentor.
Your task is to provide a helpful, encouraging progressive debugging hint to help the user solve a coding challenge WITHOUT giving away the exact code solution.

Challenge Details:
- Title: {title}
- Technology: {technology}
- Category: {category}
- Description: {description}

Starter / Buggy Code:
```
{starter_code}
```

User's Current Code:
```
{user_code}
```
"""
    if test_results:
        prompt += "\nFailed Test Outputs:\n"
        for tr in test_results:
            if not tr.get('passed'):
                prompt += f"- Test '{tr.get('name')}': Expected '{tr.get('expected')}', Got '{tr.get('actual')}'\n"

    if previous_hints:
        prompt += "\nPrevious Hints Received (DO NOT REPEAT THESE):\n"
        for i, h in enumerate(previous_hints, 1):
            prompt += f"Hint Level {i}: {h}\n"

    level_guidelines = {
        1: "Provide high-level CONCEPTUAL DIRECTION. Explain the fundamental programming concept or logic rule involved without mentioning specific code syntax, variable names, or line numbers.",
        2: "Provide MORE SPECIFIC GUIDANCE. Explain what specific function, clause, component, or state mechanism needs modification and why the current approach fails.",
        3: "Point toward the EXACT PROBLEMATIC AREA. Identify the precise line, statement, or variable reference causing the bug, but DO NOT provide copy-paste solution code."
    }

    prompt += f"""
Target Hint Level: Level {hint_level}
Level Goal: {level_guidelines[hint_level]}

Instructions:
- Tailor your response strictly to Level {hint_level} guidelines above.
- DO NOT reveal the complete solution or copy-paste code fix.
- Keep the hint concise (2-4 sentences).
- Do not repeat concepts already stated in previous hints.
"""
    return prompt

def build_feedback_prompt(context: dict) -> str:
    title = context.get('title', 'Coding Challenge')
    description = context.get('description', '')
    technology = context.get('technology', 'Programming')
    category = context.get('category', 'General')
    starter_code = context.get('starter_code', '')
    user_code = context.get('user_code', '')
    test_results = context.get('test_results', [])
    stdout = context.get('stdout', '')
    stderr = context.get('stderr', '')
    error = context.get('error', '')

    prompt = f"""You are BuggyMan AI, an expert automated code reviewer and debugging diagnostic engine.
Your task is to analyze the user's current code against execution outputs and test failures, providing structured diagnostic feedback.

Challenge Details:
- Title: {title}
- Technology: {technology}
- Category: {category}
- Description: {description}

Starter Code:
```
{starter_code}
```

User's Code:
```
{user_code}
```

Execution Outputs:
- Stdout: {stdout or 'None'}
- Stderr: {stderr or 'None'}
- Runtime Error: {error or 'None'}
"""
    if test_results:
        prompt += "\nTest Results:\n"
        for tr in test_results:
            status_str = "PASSED" if tr.get('passed') else "FAILED"
            prompt += f"- [{status_str}] {tr.get('name')}: Expected '{tr.get('expected')}', Got '{tr.get('actual')}'\n"

    prompt += """
Format your JSON response strictly with these keys:
{
  "whatIsWrong": "Clear explanation of what is failing or broken",
  "whyItIsWrong": "Explanation of why the logic or code fails execution/tests",
  "conceptToUnderstand": "The key programming or system concept the user should master",
  "suggestedDirection": "Guidance on how to fix the code without copy-paste solution"
}
"""
    return prompt

def build_explanation_prompt(context: dict) -> str:
    title = context.get('title', 'Coding Challenge')
    description = context.get('description', '')
    technology = context.get('technology', 'Programming')
    category = context.get('category', 'General')
    starter_code = context.get('starter_code', '')
    submitted_code = context.get('submitted_code', '')

    prompt = f"""You are BuggyMan AI, an expert programming instructor.
The user has successfully solved a coding challenge. Your task is to provide a clear, educational post-mortem solution explanation.

Challenge Details:
- Title: {title}
- Technology: {technology}
- Category: {category}
- Description: {description}

Original Buggy Code:
```
{starter_code}
```

User's Successful Solution Code:
```
{submitted_code}
```

Format your JSON response strictly with these keys:
{{
  "whatTheBugWas": "Concise summary of the original bug",
  "whyItHappened": "Explanation of why the original code caused errors/failures",
  "whyFixWorks": "Technical explanation of why the user's fix resolves the issue",
  "keyConcept": "Core engineering concept demonstrated by this challenge",
  "alternativeApproaches": "Alternative valid programming approaches or design patterns for this task"
}}
"""
    return prompt

def build_personalized_feedback_prompt(context: dict) -> str:
    username = context.get('username', 'Developer')
    total_submissions = context.get('total_submissions', 0)
    solved_count = context.get('solved_count', 0)
    accuracy_rate = context.get('accuracy_rate', 0)
    top_technologies = context.get('top_technologies', [])
    failed_categories = context.get('failed_categories', [])

    prompt = f"""You are BuggyMan AI, a personalized developer growth coach and learning analytics engine.
Analyze this user's debugging practice history and provide targeted learning insights and recommendations.

User Analytics Profile:
- Username: {username}
- Total Submissions: {total_submissions}
- Challenges Solved: {solved_count}
- Accuracy Rate: {accuracy_rate}%
- Top Technologies Attempted: {', '.join(top_technologies) if top_technologies else 'General'}
- Frequent Issue Categories: {', '.join(failed_categories) if failed_categories else 'None'}

Format your JSON response strictly with these keys:
{{
  "debuggingStrengths": ["Strength 1", "Strength 2"],
  "areasNeedingImprovement": ["Growth Area 1", "Growth Area 2"],
  "recommendedFocus": "Detailed recommendation on what topic or skill to practice next",
  "learningStyleInsight": "Insight into accuracy trends, attempt patterns, and problem-solving velocity",
  "recommendedChallengeIds": ["RE-E01", "SQL-E01"]
}}
"""
    return prompt
