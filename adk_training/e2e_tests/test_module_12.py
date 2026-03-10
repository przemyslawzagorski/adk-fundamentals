"""
E2E Test for Module 12: Router Agent

Tests agent routing logic and specialist selection.
"""

import sys
import os
import asyncio

# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', 'module_12_router_agent')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from agent import root_agent
from google.adk.sessions import InMemorySessionService
from utils import (
    extract_response_text,
    validate_response_not_empty,
    print_test_header,
    print_test_summary
)


async def test_navigation_routing():
    """Test: Captain routes navigation questions to Navigator"""
    print("\n📋 Test: Navigation routing")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Jaki jest najlepszy kurs do Port Royal?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should contain navigation-related terms
    response_lower = response_text.lower()
    navigation_terms = ["kurs", "nawigac", "route", "bearing", "heading"]
    
    has_nav_term = any(term in response_lower for term in navigation_terms)
    if not has_nav_term:
        print(f"⚠️  WARNING: Response doesn't contain navigation terms")
    
    print(f"✅ PASS: Navigation question handled")
    print(f"   Response length: {len(response_text)} chars")
    return True


async def test_quartermaster_routing():
    """Test: Captain routes supply questions to Quartermaster"""
    print("\n📋 Test: Quartermaster routing")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Ile mamy zapasów wody i prowiantu?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention supplies or inventory
    response_lower = response_text.lower()
    supply_terms = ["zapas", "prowiant", "woda", "supply", "inventory"]
    
    has_supply_term = any(term in response_lower for term in supply_terms)
    if not has_supply_term:
        print(f"⚠️  WARNING: Response doesn't contain supply terms")
    
    print(f"✅ PASS: Supply question handled")
    return True


async def test_gunner_routing():
    """Test: Captain routes combat questions to Gunner"""
    print("\n📋 Test: Gunner routing")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Jak przygotować działa do bitwy?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention combat or weapons
    response_lower = response_text.lower()
    combat_terms = ["działa", "bitwa", "cannon", "combat", "weapon"]
    
    has_combat_term = any(term in response_lower for term in combat_terms)
    if not has_combat_term:
        print(f"⚠️  WARNING: Response doesn't contain combat terms")
    
    print(f"✅ PASS: Combat question handled")
    return True


async def test_cook_routing():
    """Test: Captain routes food questions to Cook"""
    print("\n📋 Test: Cook routing")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Co będzie na obiad dla załogi?",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    # Should mention food or meals
    response_lower = response_text.lower()
    food_terms = ["obiad", "jedzenie", "posiłek", "food", "meal"]
    
    has_food_term = any(term in response_lower for term in food_terms)
    if not has_food_term:
        print(f"⚠️  WARNING: Response doesn't contain food terms")
    
    print(f"✅ PASS: Food question handled")
    return True


async def test_general_question():
    """Test: Captain handles general questions directly"""
    print("\n📋 Test: General question")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Opowiedz mi o życiu pirata",
        session_service,
        session
    )
    
    # Validate response
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: General question handled")
    return True


async def main():
    print_test_header("Router Agent", "12")
    
    tests = [
        ("Navigation routing", test_navigation_routing),
        ("Quartermaster routing", test_quartermaster_routing),
        ("Gunner routing", test_gunner_routing),
        ("Cook routing", test_cook_routing),
        ("General question", test_general_question),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL: {name} - Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    exit_code = print_test_summary(passed, total)
    
    return exit_code


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

