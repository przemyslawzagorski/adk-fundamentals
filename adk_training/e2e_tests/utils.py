"""
Shared utilities for E2E tests.
"""

import asyncio
import os
import importlib.util
import sys
from typing import Any, Callable, Optional
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables from root .env if exists
load_dotenv()


def import_agent_module(module_path: str):
    """
    Dynamically import agent module from specific path.

    Args:
        module_path: Path to the module directory (e.g., 'adk_training/module_02_custom_tool')

    Returns:
        Imported module object
    """
    agent_file = os.path.join(module_path, 'agent.py')

    if not os.path.exists(agent_file):
        raise FileNotFoundError(f"Agent file not found: {agent_file}")

    # Create unique module name to avoid conflicts
    module_name = f"agent_{os.path.basename(module_path)}"

    spec = importlib.util.spec_from_file_location(module_name, agent_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load spec from {agent_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


async def extract_response_text(agent, user_message: str, session_service, session) -> str:
    """
    Execute agent and extract response text from events using Runner.

    Args:
        agent: The agent to execute
        user_message: User query
        session_service: Session service to use
        session: Session object from the same session_service

    Returns:
        Concatenated response text
    """
    runner = Runner(
        agent=agent,
        app_name="test_app",
        session_service=session_service
    )

    # Create content from user message
    content = types.Content(role='user', parts=[types.Part(text=user_message)])

    response_text = ""

    # Use runner.run_async() with proper parameters
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text

    return response_text


async def extract_response_with_tool_calls(agent, user_message: str, session_service, session) -> tuple[str, list]:
    """
    Execute agent and extract both response text and tool calls using Runner.

    Args:
        agent: The agent to execute
        user_message: User query
        session_service: Session service to use
        session: Session object from the same session_service

    Returns:
        Tuple of (response_text, tool_calls_list)
    """
    runner = Runner(
        agent=agent,
        app_name="test_app",
        session_service=session_service
    )

    # Create content from user message
    content = types.Content(role='user', parts=[types.Part(text=user_message)])

    response_text = ""
    tool_calls = []

    # Use runner.run_async() with proper parameters
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content
    ):
        # Track tool calls
        if hasattr(event, 'function_calls') and event.function_calls:
            for fc in event.function_calls:
                if hasattr(fc, 'name'):
                    tool_calls.append(fc.name)

        # Extract text
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text

    return response_text, tool_calls


async def timeout_wrapper(coro: Callable, timeout_seconds: int = 30):
    """
    Wrap async coroutine with timeout.
    
    Args:
        coro: Async coroutine to execute
        timeout_seconds: Timeout in seconds
        
    Returns:
        Result of coroutine or raises TimeoutError
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")


def validate_response_not_empty(response_text: str, min_length: int = 10) -> tuple[bool, str]:
    """
    Validate that response is not empty and meets minimum length.
    
    Args:
        response_text: Response to validate
        min_length: Minimum acceptable length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not response_text:
        return False, "No response received"
    
    if len(response_text) < min_length:
        return False, f"Response too short ({len(response_text)} chars): {response_text}"
    
    return True, ""


def validate_response_contains(response_text: str, expected_keywords: list[str]) -> tuple[bool, str]:
    """
    Validate that response contains expected keywords.
    
    Args:
        response_text: Response to validate
        expected_keywords: List of keywords that should appear
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    response_lower = response_text.lower()
    
    for keyword in expected_keywords:
        if keyword.lower() not in response_lower:
            return False, f"Response doesn't contain expected keyword: '{keyword}'"
    
    return True, ""


def print_test_header(module_name: str, module_number: str):
    """Print formatted test header."""
    print("=" * 70)
    print(f"🧪 E2E Test: Module {module_number} - {module_name}")
    print("=" * 70)


def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print formatted test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {test_name}")
    if details:
        print(f"   {details}")


def print_test_summary(passed: int, total: int) -> int:
    """
    Print test summary and return exit code.
    
    Args:
        passed: Number of passed tests
        total: Total number of tests
        
    Returns:
        Exit code (0 if all passed, 1 otherwise)
    """
    print("\n" + "=" * 70)
    
    if passed == total:
        print(f"🎉 SUCCESS! All {total} tests passed!")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        return 1

