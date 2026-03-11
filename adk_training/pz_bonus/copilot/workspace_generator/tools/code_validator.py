"""
✅ Code Validator Tool
Narzędzie do walidacji składni kodu Java
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def validate_java_code(code: str, file_extension: str = ".java") -> str:
    """
    Validates code syntax (polyglot - Java/Python/React).

    Args:
        code: Source code to validate
        file_extension: File extension (.java, .py, .tsx) - determines validation type

    Returns:
        Validation result with errors (if any)
    """
    # BYPASS dla non-Java (Python i React mają własną walidację w SyntaxCritic)
    if file_extension in [".py", ".tsx", ".ts", ".jsx"]:
        logger.info(f"Skipping Java validation for {file_extension} file (handled by SyntaxCritic)")
        return f"✅ Validation skipped for {file_extension} (polyglot mode)"

    # Walidacja Java
    try:
        import javalang

        # Try to parse the code
        try:
            tree = javalang.parse.parse(code)
            return "✅ Java syntax is valid"
        except javalang.parser.JavaSyntaxError as e:
            return f"❌ Java syntax error: {e}"
        except Exception as e:
            return f"❌ Parse error: {e}"

    except ImportError:
        logger.warning("javalang not installed, using basic validation")
        return _basic_java_validation(code)


def _basic_java_validation(code: str) -> str:
    """Basic validation when javalang is not available"""
    
    errors = []
    
    # Check for basic Java syntax
    if "class " not in code and "interface " not in code:
        errors.append("No class or interface declaration found")
    
    # Check for balanced braces
    if code.count("{") != code.count("}"):
        errors.append(f"Unbalanced braces: {code.count('{')} opening, {code.count('}')} closing")
    
    # Check for balanced parentheses
    if code.count("(") != code.count(")"):
        errors.append(f"Unbalanced parentheses: {code.count('(')} opening, {code.count(')')} closing")
    
    # Check for package declaration
    if "package " not in code:
        errors.append("No package declaration (recommended)")
    
    if errors:
        return "⚠️ Basic validation issues:\n" + "\n".join(f"- {e}" for e in errors)
    else:
        return "✅ Basic validation passed (install 'javalang' for full syntax check)"


def count_todo_comments(code: str) -> str:
    """
    Counts TODO comments in code.
    
    Args:
        code: Source code
    
    Returns:
        Count and list of TODO comments
    """
    lines = code.split("\n")
    todos = []
    
    for i, line in enumerate(lines, 1):
        if "TODO" in line or "todo" in line:
            todos.append(f"Line {i}: {line.strip()}")
    
    if not todos:
        return "No TODO comments found"
    
    result = f"Found {len(todos)} TODO comment(s):\n\n"
    for todo in todos:
        result += f"- {todo}\n"
    
    return result


def check_code_quality(code: str) -> str:
    """
    Performs basic code quality checks.
    
    Args:
        code: Source code
    
    Returns:
        Quality assessment
    """
    issues = []
    recommendations = []
    
    # Check for javadoc
    if "/**" not in code:
        recommendations.append("Add Javadoc comments for classes and methods")
    
    # Check for TODO comments
    todo_count = code.count("TODO") + code.count("todo")
    if todo_count == 0:
        issues.append("No TODO comments found (expected for training code)")
    elif todo_count < 3:
        recommendations.append(f"Only {todo_count} TODO comments - consider adding more for training")
    
    # Check for proper naming
    if code.count("public class") > 1:
        issues.append("Multiple public classes in one file")
    
    # Build result
    result = "Code Quality Check:\n\n"
    
    if issues:
        result += "Issues:\n"
        for issue in issues:
            result += f"❌ {issue}\n"
        result += "\n"
    
    if recommendations:
        result += "Recommendations:\n"
        for rec in recommendations:
            result += f"💡 {rec}\n"
    
    if not issues and not recommendations:
        result += "✅ No issues found\n"
    
    return result

