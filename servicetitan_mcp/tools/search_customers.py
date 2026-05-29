"""Tool: search_customers - Search for customer records in ServiceTitan."""

from typing import Any

from servicetitan_mcp.schemas import SearchCustomersInput
from servicetitan_mcp.client import ServiceTitanClient


async def search_customers(client: ServiceTitanClient, input_data: SearchCustomersInput) -> dict[str, Any]:
    """Search for customer records in ServiceTitan by name, phone, or email.
    
    Args:
        client: ServiceTitanClient instance with auth and tenant context.
        input_data: SearchCustomersInput with optional name, phone, email.
    
    Returns:
        dict with 'data' list of customer records and 'hasMore' boolean.
    """
    params: dict[str, str] = {}
    
    if input_data.name:
        params["name"] = input_data.name
    if input_data.phone:
        params["phone"] = input_data.phone
    if input_data.email:
        params["email"] = input_data.email
    
    tenant_id = client.tenant_id
    url = f"https://api.servicetitan.io/crm/v2/tenant/{tenant_id}/customers"
    
    response = await client.get(url, params=params)
    
    return response


def get_search_customers_tool() -> dict[str, Any]:
    """Return the MCP tool definition for search_customers."""
    return {
        "name": "search_customers",
        "description": "Search for customer records in ServiceTitan by name, phone, or email. "
                      "Returns active customers with contact details. "
                      "Used by AI receptionists to identify an inbound caller.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "First and/or last name"
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number (digits only or formatted)"
                },
                "email": {
                    "type": "string",
                    "description": "Email address"
                }
            },
            "required": []
        }
    }
