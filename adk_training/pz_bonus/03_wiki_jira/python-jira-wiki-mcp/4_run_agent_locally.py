"""
Run Jira Assistant Agent Locally

Test the agent programmatically without the web interface.
Make sure the MCP server is running before executing this script.
"""

import sys
import os

# Add agent_local_mcp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent_local_mcp'))

from agent import root_agent

def main():
    print("=" * 80)
    print("JIRA ASSISTANT AGENT - LOCAL TEST")
    print("=" * 80)
    print("\nMake sure the MCP server is running:")
    print("  ./2_run_mcp_server_locally.sh")
    print("\n" + "=" * 80)
    
    # Test queries
    test_queries = [
        "Show me my open tickets",
        "Search for tickets in project CLM6 that are open",
    ]
    
    print("\nRunning test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {query}")
        print("=" * 80)
        
        try:
            # Send query to agent
            response = root_agent.send_message(query)
            
            # Print response
            print(f"\n{response.text}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure:")
            print("  1. MCP server is running (./2_run_mcp_server_locally.sh)")
            print("  2. Environment variables are set correctly")
            break
    
    print("\n" + "=" * 80)
    print("Interactive mode - type your questions (or 'quit' to exit)")
    print("=" * 80)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            # Send message to agent
            response = root_agent.send_message(user_input)
            print(f"\nAgent: {response.text}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

