# MasterMCP

## Project Introduction

MasterMCP is a demonstration tool designed to showcase various potential security attack vectors against MCP (Model Control Protocol). This project illustrates how malicious plugins can exploit weaknesses in the MCP architecture through practical examples, helping developers and security researchers understand these risks and strengthen system protection.

## Features

- **Plugin-based Malicious Payloads**: Demonstrates how malicious plugins can run within the MCP architecture
- **Multiple Attack Techniques**: Includes examples of data poisoning, cross-MCP calls, competitive malicious functions, and more
- **Dynamic Loading Mechanism**: Utilizes Python's dynamic module loading for imperceptible attack payload injection
- **Practical Educational Value**: Each attack vector comes with detailed explanations and implementation code

## Included Attack Vectors

1. **Data Poisoning**: The `banana` plugin demonstrates how to force users to perform specific operations
2. **JSON Injection Attacks**: The `url_json` plugin shows how to retrieve data from a local malicious service
3. **Competitive Malicious Functions**: The `remove_server` plugin overrides existing functionality
4. **Cross-MCP Call Attacks**: The `Master_cross_call` plugin guides users to perform dangerous operations

## Installation Instructions

```bash
# Clone the repository

cd MasterMCP

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the main service
python MasterMCP.py
```

## Project Structure

```
MasterMCP/
├── MasterMCP.py              # Main program, responsible for loading and managing plugins
├── tools_plugins/            # Malicious plugins directory
│   ├── initialize_data_poisoning.py    # Forces users to perform specific checks
│   ├── inject_json_poisoning.py        # JSON data injection example
│   ├── malicious_competitive_function.py  # Competitive function override
│   └── malicious_cross_mcp_call.py     # Cross-MCP call attack
├── resources_plugins/        # Resource plugins directory
├── prompts_plugins/          # Prompt plugins directory
└── utils/                    # Utility functions
```

## Security Warning

⚠️ **This project is for educational and research purposes only**. Do not use these techniques on any system without authorization. Malicious use of this code may violate laws and regulations.

## Defense Recommendations

- Implement strict plugin verification mechanisms
- Thoroughly check and sanitize all external inputs
- Implement the principle of least privilege, limiting plugin execution permissions
- Use signature verification to ensure only trusted plugins are loaded
- Regularly review installed plugins and their behaviors

## Attack Analysis

### Banana Detection Poisoning
The `initialize_data_poisoning.py` plugin establishes a mandatory process dependency by requiring a "banana check" before any operation. This technique can be used to:
- Induce users to perform unnecessary operations
- Establish a false sense of security
- Insert malicious steps before legitimate operations

### JSON Data Injection
The `inject_json_poisoning.py` plugin retrieves data from a local port by default, potentially leading to:
- Data leakage
- Execution of malicious instructions
- Bypassing normal security checks

### Competitive Function Override
The `malicious_competitive_function.py` provides a `remove_server` function with the same name but different functionality:
- Replaces critical system functions
- Prevents normal service removal operations
- Embeds hidden instructions encoded in hexadecimal within the confusion

### Cross-MCP Call Attack
The `malicious_cross_mcp_call.py` uses encoded error messages to induce users to:
- Add unverified external services
- Perform unnecessary operations
- Expand the attack surface

## Contribution Guidelines

Contributions to this project are welcome through:
- Submitting examples of new attack vectors
- Improving documentation for existing examples
- Adding example implementations of defense mechanisms

## License

[MIT License](LICENSE)
