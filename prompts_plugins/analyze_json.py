"""
JSON Analysis Prompt Plugin
Provides prompt templates for JSON data analysis
"""

def analyze_json_prompt(url: str, format_type: str) -> str:
    """Creates analysis prompt for given JSON data"""
    return f"""Please help me analyze the JSON data returned from this URL: {url}, format type: {format_type}

Please use the following tools to get detailed information:
1. url_json - Get JSON data returned from the URL
2. parse_json_structure - Analyze JSON structure and hierarchy
3. validate_json_format - Validate if JSON format complies with {format_type} standards
4. extract_json_keys - Extract all key fields and values
5. check_json_security - Check for security risks in the JSON
6. analyze_json_data_types - Analyze data types and formats
7. compare_json_schema - Compare with standard schema
8. generate_json_visualization - Generate visual representation of JSON data

Please provide a comprehensive analysis report based on the above information, focusing on:
1. Structure and completeness of JSON data
2. Validity of key fields and their values
3. Compliance of data format with expected standards
4. Potential data issues or anomalies
5. JSON data optimization suggestions, if needed"""

# Prompt plugin information
PROMPT_INFO = {
    'name': 'analyze_json',  # Prompt name
    'description': 'Generate detailed analysis prompt for JSON data',  # Prompt description
    'function': analyze_json_prompt  # Processing function
} 