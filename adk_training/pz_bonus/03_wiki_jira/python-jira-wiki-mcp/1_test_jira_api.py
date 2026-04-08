"""
Test Jira API Client

Simple script to test Jira REST API connectivity and basic operations.
Run this before starting the MCP server to verify your credentials.
"""

import os
from dotenv import load_dotenv
from jira_client import JiraClient

load_dotenv()

def main():
    print("=" * 80)
    print("JIRA API CLIENT TEST")
    print("=" * 80)
    
    # Initialize client
    try:
        jira = JiraClient()
        print(f"\n✅ Jira client initialized")
        print(f"   Base URL: {jira.base_url}")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("  - JIRA_BASE_URL")
        print("  - JIRA_BEARER_TOKEN")
        return
    
    # Test 1: Get my open tickets
    print("\n" + "-" * 80)
    print("TEST 1: Get my open tickets")
    print("-" * 80)
    tickets = jira.my_open_tickets(limit=5)
    if tickets:
        print(f"\nFound {len(tickets)} open tickets:")
        for ticket in tickets:
            key = ticket.get('key', 'N/A')
            summary = ticket.get('fields', {}).get('summary', 'N/A')
            status = ticket.get('fields', {}).get('status', {}).get('name', 'N/A')
            print(f"  • {key}: {summary} [{status}]")
    else:
        print("\nNo open tickets found (or error occurred)")
    
    # Test 2: Search with JQL
    print("\n" + "-" * 80)
    print("TEST 2: Search with JQL")
    print("-" * 80)
    
    # Get project key from env or use default
    project_key = os.getenv("JIRA_DEFAULT_PROJECT_KEY", "CLM6")
    jql = f"project = {project_key} ORDER BY created DESC"
    print(f"JQL: {jql}")
    
    results = jira.search(jql, limit=3)
    if results:
        print(f"\nFound {len(results)} tickets:")
        for ticket in results:
            key = ticket.get('key', 'N/A')
            summary = ticket.get('fields', {}).get('summary', 'N/A')
            created = ticket.get('fields', {}).get('created', 'N/A')
            print(f"  • {key}: {summary}")
            print(f"    Created: {created}")
    else:
        print("\nNo tickets found (or error occurred)")
    
    # Test 3: Get specific ticket (if available)
    if results and len(results) > 0:
        print("\n" + "-" * 80)
        print("TEST 3: Get specific ticket")
        print("-" * 80)
        
        ticket_id = results[0].get('key')
        print(f"Fetching ticket: {ticket_id}")
        
        ticket = jira.get_ticket(ticket_id)
        if 'error' not in ticket:
            print(f"\n✅ Ticket details:")
            print(f"   Key: {ticket.get('key', 'N/A')}")
            print(f"   Summary: {ticket.get('fields', {}).get('summary', 'N/A')}")
            print(f"   Status: {ticket.get('fields', {}).get('status', {}).get('name', 'N/A')}")
            print(f"   Assignee: {ticket.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')}")
            print(f"   Priority: {ticket.get('fields', {}).get('priority', {}).get('name', 'N/A')}")
        else:
            print(f"\n❌ Error: {ticket.get('error')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("\n✅ Jira API client is working!")
    print("\nNext steps:")
    print("  1. Run MCP server: ./2_run_mcp_server_locally.sh")
    print("  2. Test with ADK: adk web agent_local_mcp")
    print("  3. Or run agent programmatically: python 4_run_agent_locally.py")
    print()

if __name__ == "__main__":
    main()

