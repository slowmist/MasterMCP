import os
import importlib.util
import inspect
from typing import Dict, List, Callable, Any, Optional, get_type_hints
from dataclasses import dataclass
import json
from inspect import Parameter, Signature
from functools import wraps
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.server.fastmcp.resources import FunctionResource
from multiprocessing import Process
# Import custom FastAPI module
from utils.fastapi_mod import run_fastapi_server

# Configure logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Create logger instance
log = logging.getLogger("MasterMCP")

# Initialize MCP server
mcp = FastMCP("Master MCP")

# For storing loaded plugin information
@dataclass
class PluginInfo:
    name: str
    description: str
    function: Callable
    schema: Dict[str, Any]

# Store loaded plugins
plugins: Dict[str, PluginInfo] = {}


def register_plugin(name: str, description: str, function: Callable, schema: Dict[str, Any]) -> None:
    """Register a plugin and create corresponding MCP tool"""
    # Store plugin information
    plugins[name] = PluginInfo(name, description, function, schema)
    
    # Create wrapper function with correct type annotations based on schema
    # First extract parameters and types from schema
    parameters = []
    annotations = {}
    
    # Process property definitions in schema
    if 'properties' in schema:
        properties = schema.get('properties', {})
        required_params = schema.get('required', [])
        
        for param_name, param_info in properties.items():
            # Determine if parameter is required or optional
            default = Parameter.empty if param_name in required_params else None
            
            # Determine Python type based on schema type
            param_type = Any  # Default to Any
            if param_info.get('type') == 'string':
                param_type = str
            elif param_info.get('type') == 'integer':
                param_type = int
            elif param_info.get('type') == 'number':
                param_type = float
            elif param_info.get('type') == 'boolean':
                param_type = bool
            elif param_info.get('type') == 'object':
                param_type = dict
            elif param_info.get('type') == 'array':
                param_type = list
                
            # Create parameter object
            parameters.append(
                Parameter(
                    name=param_name,
                    kind=Parameter.KEYWORD_ONLY,
                    default=default,
                    annotation=param_type
                )
            )
            
            # Add to type annotations dictionary
            annotations[param_name] = param_type
    
    # Create wrapper function
    @wraps(function)
    async def wrapper(**kwargs):
        """Dynamically created MCP tool function"""
        func = plugins[name].function
        # Check if function is a coroutine function (async)
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            # If synchronous function, call directly without await
            return func(**kwargs)
    
    # Add type annotations
    wrapper.__annotations__ = annotations
    
    # Update tool function name and documentation
    wrapper.__name__ = name
    wrapper.__doc__ = description
    
    # Create function with correct signature if needed
    if parameters:
        # Create function signature
        sig = Signature(parameters=parameters, return_annotation=Any)
        wrapper.__signature__ = sig
    
    # Register tool
    mcp.add_tool(wrapper, name=name, description=description)
    
    log.info(f"Plugin registered: {name}")

def load_plugins(plugins_dir: str = None) -> None:
    """Scan directory and load all valid plugin files"""
    # If plugin directory not specified, use plugins folder in script directory
    if plugins_dir is None:
        # Get absolute path of current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plugins_dir = os.path.join(script_dir, "tools_plugins")
    
    # Check if plugin directory exists
    if not os.path.exists(plugins_dir):
        log.error(f"Error: Plugin directory {plugins_dir} does not exist")
        return
        
    # Get current filename to avoid trying to load itself as a plugin
    current_file = os.path.basename(__file__)
    
    # Find all possible plugin files
    plugins_files = [f for f in os.listdir(plugins_dir) 
                    if f.endswith('.py') and not f.startswith('_') 
                    and f != current_file]
    
    if not plugins_files:
        log.warning(f"Warning: No plugin files found in directory {plugins_dir}")
        return
    
    plugins_count = 0
    errors_count = 0
    
    # Iterate through found plugin files
    for filename in plugins_files:
        try:
            # Get module path
            module_path = os.path.join(plugins_dir, filename)
            module_name = filename[:-3]  # Remove .py extension
            
            log.info(f"Attempting to load plugin: {module_name} (path: {module_path})")
            
            # Dynamically load module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if module has PLUGIN_INFO dictionary
                if hasattr(module, 'PLUGIN_INFO'):
                    info = module.PLUGIN_INFO
                    
                    # Validate plugin information is complete
                    if all(k in info for k in ['name', 'description', 'function', 'schema']):
                        # Register plugin
                        register_plugin(
                            info['name'],
                            info['description'],
                            info['function'],
                            info['schema']
                        )
                        plugins_count += 1
                    else:
                        log.warning(f"Warning: Plugin {module_name} is missing required PLUGIN_INFO fields")
                        errors_count += 1
                else:
                    log.warning(f"Warning: Plugin {module_name} does not define PLUGIN_INFO")
                    errors_count += 1
        except Exception as e:
            log.error(f"Error loading plugin {filename}: {str(e)}")
            errors_count += 1
    
    log.info(f"Loaded {plugins_count} plugins, {errors_count} failed")

# Load all plugins
load_plugins()

# For storing loaded resource plugin information
@dataclass
class ResourcePluginInfo:
    name: str
    description: str
    uri: str
    mime_type: str
    function: Callable

# For storing loaded resource template plugin information
@dataclass
class ResourceTemplatePluginInfo:
    name: str
    description: str
    uri_template: str
    mime_type: str
    function: Callable

# Store loaded resource plugins
resource_plugins: Dict[str, ResourcePluginInfo] = {}

# Store loaded resource template plugins
resource_template_plugins: Dict[str, ResourceTemplatePluginInfo] = {}

def register_resource_plugin(name: str, description: str, uri: str, mime_type: str, function: Callable) -> None:
    """Register a resource plugin and create corresponding MCP resource"""
    # Store resource plugin information
    resource_plugins[name] = ResourcePluginInfo(name, description, uri, mime_type, function)
    
    # Create resource object
    resource = FunctionResource(
        uri=uri,
        name=name,
        description=description,
        mime_type=mime_type,
        fn=function
    )
    
    # Add to server
    mcp.add_resource(resource)
    
    log.info(f"Resource plugin registered: {name}")

def register_resource_template_plugin(name: str, description: str, uri_template: str, mime_type: str, function: Callable) -> None:
    """Register a resource template plugin and create corresponding MCP resource template"""
    # Store resource template plugin information
    resource_template_plugins[name] = ResourceTemplatePluginInfo(name, description, uri_template, mime_type, function)
    
    # Add to server
    mcp._resource_manager.add_template(
        fn=function,
        uri_template=uri_template,
        name=name,
        description=description,
        mime_type=mime_type
    )
    
    log.info(f"Resource template plugin registered: {name}")

def load_resource_plugins(resources_plugins_dir: str = None) -> None:
    """Scan directory and load all valid resource plugin files"""
    # If resource plugin directory not specified, use resources_plugins folder in script directory
    if resources_plugins_dir is None:
        # Get absolute path of current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        resources_plugins_dir = os.path.join(script_dir, "resources_plugins")
    
    # Check if resource plugin directory exists
    if not os.path.exists(resources_plugins_dir):
        log.error(f"Error: Resource plugin directory {resources_plugins_dir} does not exist")
        return
        
    # Get current filename to avoid trying to load itself as a plugin
    current_file = os.path.basename(__file__)
    
    # Find all possible resource plugin files
    resources_plugins_files = [f for f in os.listdir(resources_plugins_dir) 
                              if f.endswith('.py') and not f.startswith('_') 
                              and f != current_file]
    
    if not resources_plugins_files:
        log.warning(f"Warning: No resource plugin files found in directory {resources_plugins_dir}")
        return
    
    resources_count = 0
    templates_count = 0
    errors_count = 0
    
    # Iterate through found resource plugin files
    for filename in resources_plugins_files:
        try:
            # Get module path
            module_path = os.path.join(resources_plugins_dir, filename)
            module_name = filename[:-3]  # Remove .py extension
            
            log.info(f"Attempting to load resource plugin: {module_name} (path: {module_path})")
            
            # Dynamically load module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if module has RESOURCE_INFO dictionary (regular resource)
                if hasattr(module, 'RESOURCE_INFO'):
                    info = module.RESOURCE_INFO
                    
                    # Validate resource plugin information is complete
                    if all(k in info for k in ['name', 'description', 'uri', 'mime_type', 'function']):
                        # Register resource plugin
                        register_resource_plugin(
                            info['name'],
                            info['description'],
                            info['uri'],
                            info['mime_type'],
                            info['function']
                        )
                        resources_count += 1
                    else:
                        log.warning(f"Warning: Resource plugin {module_name} is missing required RESOURCE_INFO fields")
                        errors_count += 1
                
                # Check if module has RESOURCE_TEMPLATE_INFO dictionary (resource template)
                if hasattr(module, 'RESOURCE_TEMPLATE_INFO'):
                    info = module.RESOURCE_TEMPLATE_INFO
                    
                    # Validate resource template plugin information is complete
                    if all(k in info for k in ['name', 'description', 'uri_template', 'mime_type', 'function']):
                        # Register resource template plugin
                        register_resource_template_plugin(
                            info['name'],
                            info['description'],
                            info['uri_template'],
                            info['mime_type'],
                            info['function']
                        )
                        templates_count += 1
                    else:
                        log.warning(f"Warning: Resource template plugin {module_name} is missing required RESOURCE_TEMPLATE_INFO fields")
                        errors_count += 1
                
                # If module has neither RESOURCE_INFO nor RESOURCE_TEMPLATE_INFO
                if not hasattr(module, 'RESOURCE_INFO') and not hasattr(module, 'RESOURCE_TEMPLATE_INFO'):
                    log.warning(f"Warning: Resource plugin {module_name} does not define RESOURCE_INFO or RESOURCE_TEMPLATE_INFO")
                    errors_count += 1
        except Exception as e:
            log.error(f"Error loading resource plugin {filename}: {str(e)}")
            errors_count += 1
    
    log.info(f"Loaded {resources_count} regular resource plugins, {templates_count} resource template plugins, {errors_count} failed")

# Load all resource plugins
load_resource_plugins()

# For storing loaded prompt plugin information
@dataclass
class PromptPluginInfo:
    name: str
    description: str
    function: Callable

# Store loaded prompt plugins
prompts_plugins: Dict[str, PromptPluginInfo] = {}

def register_prompt_plugin(name: str, description: str, function: Callable) -> None:
    """Register a prompt plugin and create corresponding MCP prompt template"""
    # Store prompt plugin information
    prompts_plugins[name] = PromptPluginInfo(name, description, function)
    
    # Add to server
    from mcp.server.fastmcp.prompts import Prompt
    prompt = Prompt.from_function(function, name=name, description=description)
    mcp.add_prompt(prompt)
    
    log.info(f"Prompt plugin registered: {name}")

def load_prompts_plugins(prompts_plugins_dir: str = None) -> None:
    """Scan directory and load all valid prompt plugin files"""
    # If prompt plugin directory not specified, use prompts_plugins folder in script directory
    if prompts_plugins_dir is None:
        # Get absolute path of current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompts_plugins_dir = os.path.join(script_dir, "prompts_plugins")
    
    # Check if prompt plugin directory exists
    if not os.path.exists(prompts_plugins_dir):
        log.error(f"Error: Prompt plugin directory {prompts_plugins_dir} does not exist")
        return
        
    # Get current filename to avoid trying to load itself as a plugin
    current_file = os.path.basename(__file__)
    
    # Find all possible prompt plugin files
    prompts_plugins_files = [f for f in os.listdir(prompts_plugins_dir) 
                          if f.endswith('.py') and not f.startswith('_') 
                          and f != current_file]
    
    if not prompts_plugins_files:
        log.warning(f"Warning: No prompt plugin files found in directory {prompts_plugins_dir}")
        return
    
    prompts_count = 0
    errors_count = 0
    
    # Iterate through found prompt plugin files
    for filename in prompts_plugins_files:
        try:
            # Get module path
            module_path = os.path.join(prompts_plugins_dir, filename)
            module_name = filename[:-3]  # Remove .py extension
            
            log.info(f"Attempting to load prompt plugin: {module_name} (path: {module_path})")
            
            # Dynamically load module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if module has PROMPT_INFO dictionary
                if hasattr(module, 'PROMPT_INFO'):
                    info = module.PROMPT_INFO
                    
                    # Validate prompt plugin information is complete
                    if all(k in info for k in ['name', 'description', 'function']):
                        # Register prompt plugin
                        register_prompt_plugin(
                            info['name'],
                            info['description'],
                            info['function']
                        )
                        prompts_count += 1
                    else:
                        log.warning(f"Warning: Prompt plugin {module_name} is missing required PROMPT_INFO fields")
                        errors_count += 1
                else:
                    log.warning(f"Warning: Prompt plugin {module_name} does not define PROMPT_INFO")
                    errors_count += 1
        except Exception as e:
            log.error(f"Error loading prompt plugin {filename}: {str(e)}")
            errors_count += 1
    
    log.info(f"Loaded {prompts_count} prompt plugins, {errors_count} failed")

# Load all prompt plugins
load_prompts_plugins()

if __name__ == "__main__":
    log.info(f"Starting MCP service, registered {len(plugins) + len(resource_plugins) + len(resource_template_plugins) + len(prompts_plugins) + 3} tools, resources and prompt templates")
    
    # Start FastAPI subprocess
    fastapi_process = Process(target=run_fastapi_server)
    fastapi_process.daemon = True  # Set as daemon process, automatically terminates when main process ends
    fastapi_process.start()
    log.info("FastAPI service started in subprocess")
    
    # Start MCP server
    mcp.run()