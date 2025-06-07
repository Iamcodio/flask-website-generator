"""
Upstash Redis MCP integration helper
Note: This is a helper module for development. In production with Claude,
the MCP tools would be called directly.
"""
import os
import requests
import json
from typing import Any, List, Optional

# Upstash connection details from environment or defaults
UPSTASH_REST_URL = os.environ.get('UPSTASH_REDIS_REST_URL', 'https://fleet-snail-15245.upstash.io')
UPSTASH_REST_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN', 'ATuNAAIjcDEyNTIzMjhjMTQxNTQ0NDRjODg5MmM1ODZiNTk5MmM1OHAxMA')

def upstash_run_command(command: List[str]) -> Any:
    """
    Run a Redis command via Upstash REST API
    In production with Claude, this would use: mcp__upstash__redis_database_run_single_redis_command
    """
    try:
        # Convert command to Upstash REST format
        # Special handling for commands with spaces or special characters
        if len(command) > 1:
            # Use POST for complex commands
            url = UPSTASH_REST_URL
            headers = {
                'Authorization': f'Bearer {UPSTASH_REST_TOKEN}',
                'Content-Type': 'application/json'
            }
            return requests.post(url, headers=headers, json=command).json().get('result')
        else:
            url = f"{UPSTASH_REST_URL}/{command[0]}"
            headers = {
                'Authorization': f'Bearer {UPSTASH_REST_TOKEN}'
            }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json().get('result')
            # Handle numeric responses
            if isinstance(result, str) and result.isdigit():
                return int(result)
            return result
        else:
            print(f"❌ Upstash command failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upstash command error: {e}")
        return None

def upstash_run_multiple_commands(commands: List[List[str]]) -> List[Any]:
    """
    Run multiple Redis commands via Upstash REST API
    In production with Claude, this would use: mcp__upstash__redis_database_run_multiple_redis_commands
    """
    try:
        # Use pipeline endpoint
        url = f"{UPSTASH_REST_URL}/pipeline"
        headers = {
            'Authorization': f'Bearer {UPSTASH_REST_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Format commands for pipeline
        pipeline_commands = []
        for cmd in commands:
            pipeline_commands.append(cmd)
        
        response = requests.post(url, headers=headers, json=pipeline_commands)
        
        if response.status_code == 200:
            results = response.json()
            return [r.get('result') for r in results]
        else:
            print(f"❌ Upstash pipeline failed: {response.status_code} - {response.text}")
            return [None] * len(commands)
    except Exception as e:
        print(f"❌ Upstash pipeline error: {e}")
        return [None] * len(commands)