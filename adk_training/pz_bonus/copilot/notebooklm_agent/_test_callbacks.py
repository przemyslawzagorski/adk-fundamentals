"""Test callbacks with real ADK State object."""
import sys
sys.path.insert(0, r"c:\Users\NBPZAGORSKI\IdeaProjects\spectrum-project")

from google.adk.sessions.state import State
from notebooklm_agent.agent import _before_tool_cb, _after_tool_cb

class FakeTool:
    name = "click_at"

class FakeToolContext:
    def __init__(self):
        self.state = State(value={}, delta={})

# Test 1: before without safety_decision
ctx = FakeToolContext()
r = _before_tool_cb(tool=FakeTool(), args={"x": 1, "y": 2}, tool_context=ctx)
assert r is None
print("1. before (no safety): OK")

# Test 2: before with safety_decision
ctx = FakeToolContext()
args = {"x": 1, "safety_decision": "allowed"}
r = _before_tool_cb(tool=FakeTool(), args=args, tool_context=ctx)
assert r is None
assert "safety_decision" not in args, "safety_decision should be stripped from args"
assert ctx.state.get("_pending_safety") is True
print("2. before (with safety): OK")

# Test 3: after with ack needed
resp = {"image": "base64data"}
r = _after_tool_cb(tool=FakeTool(), args={}, tool_context=ctx, tool_response=resp)
assert r is not None
assert r.get("safety_acknowledgement") == "true"
print("3. after (ack needed): OK")

# Test 4: after without ack
ctx2 = FakeToolContext()
r = _after_tool_cb(tool=FakeTool(), args={}, tool_context=ctx2, tool_response={"img": "x"})
assert r is None
print("4. after (no ack): OK")

print("ALL CALLBACK TESTS PASSED")
