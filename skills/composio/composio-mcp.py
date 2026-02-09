#!/usr/bin/env python3
"""
Composio MCP Tool - Execute actions via MCP endpoint
Usage: 
  composio-mcp.py --list                    # List available meta-tools
  composio-mcp.py --search "query"          # Search for tools
  composio-mcp.py --exec TOOL_NAME [json]   # Execute a tool via multi-execute
  composio-mcp.py TOOL_NAME [json]          # Call meta-tool directly
"""

import sys
import json
import requests

MCP_URL = 'https://backend.composio.dev/tool_router/trs_r19DmEN65WU9/mcp'
API_KEY = 'REDACTED_COMPOSIO_MCP_KEY'

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream',
    'x-api-key': API_KEY
}

def parse_sse_response(response):
    """Parse SSE or JSON response"""
    if 'text/event-stream' in response.headers.get('content-type', ''):
        for line in response.text.split('\n'):
            if line.startswith('data:'):
                return json.loads(line[5:])
    return response.json()

def list_tools():
    """List available meta-tools from MCP endpoint"""
    response = requests.post(MCP_URL, headers=HEADERS, json={
        'jsonrpc': '2.0', 'method': 'tools/list', 'id': 1
    })
    result = parse_sse_response(response)
    if 'result' in result and 'tools' in result['result']:
        for tool in result['result']['tools']:
            desc = tool.get('description', '')[:70]
            print(f"- {tool['name']}: {desc}...")

def search_tools(query):
    """Search for tools by use case"""
    response = requests.post(MCP_URL, headers=HEADERS, json={
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': 'COMPOSIO_SEARCH_TOOLS',
            'arguments': {'queries': [{'use_case': query}]}
        },
        'id': 1
    })
    result = parse_sse_response(response)
    if 'result' in result:
        data = json.loads(result['result']['content'][0]['text'])
        if data.get('successful'):
            print("Found tools:")
            for r in data['data'].get('results', []):
                print(f"  Primary: {r.get('primary_tool_slugs', [])}")
                print(f"  Related: {r.get('related_tool_slugs', [])}")
            print("\nConnection status:")
            for c in data['data'].get('toolkit_connection_statuses', []):
                status = "CONNECTED" if c['has_active_connection'] else "NOT CONNECTED"
                print(f"  {c['toolkit']}: {status}")
        else:
            print(f"Error: {data.get('error')}")
    else:
        print(json.dumps(result, indent=2))

def execute_tool(tool_slug, params=None):
    """Execute a tool via COMPOSIO_MULTI_EXECUTE_TOOL"""
    response = requests.post(MCP_URL, headers=HEADERS, json={
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': 'COMPOSIO_MULTI_EXECUTE_TOOL',
            'arguments': {
                'tools': [{
                    'tool_slug': tool_slug,
                    'arguments': params or {}
                }]
            }
        },
        'id': 1
    })
    result = parse_sse_response(response)
    if 'result' in result:
        data = json.loads(result['result']['content'][0]['text'])
        print(json.dumps(data, indent=2, default=str))
    else:
        print(json.dumps(result, indent=2, default=str))

def call_meta_tool(tool_name, params=None):
    """Call a meta-tool directly"""
    response = requests.post(MCP_URL, headers=HEADERS, json={
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': params or {}},
        'id': 1
    })
    result = parse_sse_response(response)
    print(json.dumps(result, indent=2, default=str))

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  composio-mcp.py --list                  # List meta-tools")
        print("  composio-mcp.py --search \"query\"        # Search for tools")
        print("  composio-mcp.py --exec TOOL [json]      # Execute app tool")
        print("  composio-mcp.py METATOOL [json]         # Call meta-tool")
        print("\nExamples:")
        print("  composio-mcp.py --search \"post tweet\"")
        print("  composio-mcp.py --exec TWITTER_USER_LOOKUP_ME")
        print("  composio-mcp.py --exec TWITTER_CREATION_OF_A_POST '{\"text\": \"Hello!\"}'")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        list_tools()
    elif sys.argv[1] == '--search':
        search_tools(sys.argv[2] if len(sys.argv) > 2 else "")
    elif sys.argv[1] == '--exec':
        tool = sys.argv[2] if len(sys.argv) > 2 else ""
        params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        execute_tool(tool, params)
    else:
        tool_name = sys.argv[1]
        params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        call_meta_tool(tool_name, params)

if __name__ == '__main__':
    main()
