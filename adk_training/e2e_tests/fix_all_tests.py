"""
Script to automatically fix all test files to use new API.
"""

import os
import re

# List of test files to fix
test_files = [
    'test_module_01.py',
    'test_module_04.py',
    'test_module_05.py',
    'test_module_07.py',
    'test_module_08.py',
    'test_module_11.py',
    'test_module_12.py',
]

def fix_imports(content, module_name):
    """Fix imports to use import_agent_module."""

    # Check if already using import_agent_module
    if 'import_agent_module' in content:
        return content

    # Pattern to find old import style
    old_import_pattern = r'# Add module to path\nmodule_path = os\.path\.join\(os\.path\.dirname\(__file__\), \'\.\.\',[^)]+\)\nsys\.path\.insert\(0, module_path\)\n\n# Add utils to path\nutils_path = os\.path\.dirname\(__file__\)\nsys\.path\.insert\(0, utils_path\)\n\nfrom agent import ([^\n]+)\nfrom google\.adk\.sessions import InMemorySessionService\nfrom utils import \('

    # Simpler approach - just replace the import section
    lines = content.split('\n')
    new_lines = []
    skip_until = -1

    for i, line in enumerate(lines):
        if i < skip_until:
            continue

        if '# Add module to path' in line:
            # Found start of old import section
            # Find where it ends (after "from utils import")
            end_idx = i
            for j in range(i, min(i+20, len(lines))):
                if 'from utils import' in lines[j]:
                    # Find closing parenthesis
                    for k in range(j, min(j+10, len(lines))):
                        if ')' in lines[k]:
                            end_idx = k
                            break
                    break

            # Extract module path and imports
            module_path_line = None
            agent_imports = []
            utils_imports = []

            for j in range(i, end_idx+1):
                if 'module_path = os.path.join' in lines[j]:
                    # Extract module name from path
                    match = re.search(r"'(module_\d+[^']+)'", lines[j])
                    if match:
                        module_path_line = match.group(1)

                if 'from agent import' in lines[j]:
                    match = re.search(r'from agent import (.+)', lines[j])
                    if match:
                        agent_imports = [x.strip() for x in match.group(1).split(',')]

                if 'from utils import' in lines[j]:
                    # Collect all imports (might span multiple lines)
                    import_text = lines[j]
                    paren_count = import_text.count('(') - import_text.count(')')
                    k = j + 1
                    while paren_count > 0 and k < len(lines):
                        import_text += '\n' + lines[k]
                        paren_count += lines[k].count('(') - lines[k].count(')')
                        k += 1

                    # Extract imports
                    match = re.search(r'from utils import \(([^)]+)\)', import_text, re.DOTALL)
                    if match:
                        utils_imports = [x.strip() for x in match.group(1).split(',')]

            # Generate new import section
            new_lines.append('# Add utils to path')
            new_lines.append('utils_path = os.path.dirname(__file__)')
            new_lines.append('sys.path.insert(0, utils_path)')
            new_lines.append('')

            # Add import_agent_module to utils imports if not present
            if 'import_agent_module' not in utils_imports:
                utils_imports.insert(0, 'import_agent_module')

            new_lines.append('from utils import (')
            for imp in utils_imports:
                new_lines.append(f'    {imp},')
            new_lines[-1] = new_lines[-1].rstrip(',')  # Remove trailing comma
            new_lines.append(')')
            new_lines.append('from google.adk.sessions import InMemorySessionService')
            new_lines.append('')
            new_lines.append('# Import agent module dynamically')
            new_lines.append(f"module_path = os.path.join(os.path.dirname(__file__), '..', '{module_path_line}')")
            new_lines.append('agent_module = import_agent_module(module_path)')

            # Add agent imports
            for imp in agent_imports:
                new_lines.append(f'{imp} = agent_module.{imp}')

            skip_until = end_idx + 1
            continue

        new_lines.append(line)

    return '\n'.join(new_lines)


def fix_function_calls(content):
    """Fix extract_response_text and extract_response_with_tool_calls calls."""

    # Pattern: extract_response_text(\n        root_agent,\n        "...",\n        session\n    )
    # Replace with: extract_response_text(\n        root_agent,\n        "...",\n        session_service,\n        session\n    )

    # Use a more flexible pattern
    pattern = r'(extract_response(?:_text|_with_tool_calls)\(\s+root_agent,\s+[^,]+,\s+)(session\s*\))'
    replacement = r'\1session_service,\n        \2'

    content = re.sub(pattern, replacement, content)

    return content


def fix_test_file(filepath):
    """Fix a single test file."""
    print(f"\n📝 Processing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Extract module name from filepath
    match = re.search(r'test_(module_\d+[^.]*)', filepath)
    module_name = match.group(1) if match else 'unknown'

    # Fix imports
    content = fix_imports(content, module_name)

    # Fix function calls
    content = fix_function_calls(content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {os.path.basename(filepath)}")
        return True
    else:
        print(f"⏭️  No changes needed: {os.path.basename(filepath)}")
        return False


# Fix all test files
script_dir = os.path.dirname(os.path.abspath(__file__))
fixed_count = 0

print("="*70)
print("🔧 Fixing all test files...")
print("="*70)

for test_file in test_files:
    filepath = os.path.join(script_dir, test_file)
    if os.path.exists(filepath):
        if fix_test_file(filepath):
            fixed_count += 1
    else:
        print(f"❌ Not found: {test_file}")

print("\n" + "="*70)
print(f"🎉 Fixed {fixed_count}/{len(test_files)} files")
print("="*70)

