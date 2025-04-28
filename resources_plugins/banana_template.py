"""
Banana Template Resource Plugin
Provides banana information based on type and quantity
"""

def get_banana(type: str, quantity: str):
    """Get information for specific type and quantity of bananas
    
    Args:
        type: Banana type, such as small banana, large banana, red banana, etc.
        quantity: Banana quantity
    """
    # Logic to retrieve banana information from suppliers can be implemented here
    # In actual applications, this should be replaced with real API calls
    
    return f"""
# {type} Banana Information - {quantity} units

## Banana Data
- Type: `{type}`
- Quantity: {quantity}
- Origin: [To be retrieved]
- Ripeness: [To be retrieved]
- Price: [To be retrieved]
- Shelf Life: [To be retrieved]
- Taste Rating: [To be retrieved]
- Nutritional Value: [To be retrieved]

## Consumption Suggestions
- Moderately ripe bananas taste best
- Can be used to make banana smoothies or banana bread
- Banana peels can be used as natural fertilizer
"""

# Resource template plugin information
RESOURCE_TEMPLATE_INFO = {
    'name': 'Banana Retrieval',
    'description': 'Provides banana information based on type and quantity',
    'uri_template': 'resource://fruit/banana/{type}/quantity/{quantity}',
    'mime_type': 'text/markdown',
    'function': get_banana
} 