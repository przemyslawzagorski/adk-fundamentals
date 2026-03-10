"""Quick script to fix remaining test files."""
import re
import os

tests_to_fix = [
    ('test_module_05.py', 'module_05_human_in_loop', ['root_agent', 'SHIP_TREASURY']),
    ('test_module_07.py', 'module_07_parallel_agent', ['root_agent']),
    ('test_module_08.py', 'module_08_loop_critique', ['root_agent']),
    ('test_module_11.py', 'module_11_memory_bank', ['root_agent', '_memory_store']),
    ('test_module_12.py', 'module_12_router_agent', ['root_agent']),
]

for test_file, module_name, imports in tests_to_fix:
    filepath = os.path.join(os.path.dirname(__file__), test_file)
    
    if not os.path.exists(filepath):
        print(f"❌ Not found: {test_file}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix imports
    old_import = f"""# Add module to path
module_path = os.path.join(os.path.dirname(__file__), '..', '{module_name}')
sys.path.insert(0, module_path)

# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from agent import {', '.join(imports)}
from google.adk.sessions import InMemorySessionService
from utils import ("""
    
    new_import = f"""# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import (
    import_agent_module,"""
    
    if old_import in content:
        # Find the end of utils import
        start_idx = content.find(old_import)
        end_idx = content.find(')', start_idx) + 1
        old_section = content[start_idx:end_idx]
        
        # Extract utils imports
        utils_match = re.search(r'from utils import \(([^)]+)\)', old_section, re.DOTALL)
        if utils_match:
            utils_imports = [x.strip() for x in utils_match.group(1).split(',')]
            
            new_section = f"""# Add utils to path
utils_path = os.path.dirname(__file__)
sys.path.insert(0, utils_path)

from utils import (
    import_agent_module,
{chr(10).join('    ' + imp + ',' for imp in utils_imports)}
)
from google.adk.sessions import InMemorySessionService

# Import agent module dynamically
module_path = os.path.join(os.path.dirname(__file__), '..', '{module_name}')
agent_module = import_agent_module(module_path)
{chr(10).join(f'{imp} = agent_module.{imp}' for imp in imports)}"""
            
            content = content[:start_idx] + new_section + content[end_idx:]
    
    # Fix function calls
    content = re.sub(
        r'(extract_response(?:_text|_with_tool_calls)\(\s+root_agent,\s+[^,]+,\s+)(session\s*\))',
        r'\1session_service,\n        \2',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {test_file}")

print("\n🎉 All tests fixed!")

