from typing import List, Dict


def build_system_prompt(tools: List[Dict] = None) -> str:
    """
    Builds the system prompt for the QA agent, including available tools.
    """
    tool_info = ""
    if tools:
        tool_info = "\nAvailable tools:\n"
        for t in tools:
            tool_info += f"- {t['name']}: {t.get('description', '')}\n"

    prompt = f"""
You are an AI QA Engineer. Your goal is to perform automated QA testing
on websites, forms, and flows using the tools provided. Use the tools when needed
and respond clearly with instructions or results.

{tool_info}
Follow best practices: capture screenshots, report issues, collect tool outputs.
"""
    return prompt


def build_user_prompt(target_url: str) -> str:
    """
    Builds the user prompt that tells the agent what to QA.
    """
    return f"Please QA the following website and report any issues: {target_url}"
