import urllib.request
import json
from typing import Dict, List, Any

async def url_json(url: str = "http://127.0.0.1:1024/api/data") -> Dict[str, Any]:

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            result = f"""Please confirm this JSON result: {data}"""
            return result
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}


PLUGIN_INFO = {
    "name": "url_json",
    "description": """Use this function to retrieve and format JSON from web pages""",
    "function": url_json,
    "schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "title": "URL",
                "description": "The URL to fetch JSON data from (defaults to http://127.0.0.1:1024/api/data)"
            }
        },
        "required": [],
        "title": "url_json"
    }
} 
