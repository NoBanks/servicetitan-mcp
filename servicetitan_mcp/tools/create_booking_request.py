"""Tool: create_booking_request - Create a pending booking request in the dispatcher Calls inbox."""

from typing import Any

from servicetitan_mcp.schemas import CreateBookingRequestInput
from servicetitan_mcp.client import ServiceTitanClient


def get_tool_definition() -> dict[str, Any]:
    """Return the MCP tool definition for create_booking_request."""
    return {
        "name": "create_booking_request",
        "description": "Create a pending booking request in the ServiceTitan dispatcher Calls inbox. "
                      "This is the AI receptionist's primary write action. Returns the booking ID and "
                      "pending status. A human dispatcher confirms and schedules the actual job.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer's name"
                },
                "summary": {
                    "type": "string",
                    "description": "Summary of the service request"
                },
                "phone": {
                    "type": "string",
                    "description": "Customer's phone number"
                },
                "street": {
                    "type": "string",
                    "description": "Service address street"
                },
                "city": {
                    "type": "string",
                    "description": "Service address city"
                },
                "state": {
                    "type": "string",
                    "description": "Two-letter state code"
                },
                "zip": {
                    "type": "string",
                    "description": "Postal code"
                },
                "source": {
                    "type": "string",
                    "description": "Source tag for the booking",
                    "default": "AI Assistant"
                },
                "isFirstTimeClient": {
                    "type": "boolean",
                    "description": "Whether this is a first-time client",
                    "default": False
                }
            },
            "required": ["name", "summary", "phone", "street", "city", "state", "zip"]
        }
    }


async def execute(client: ServiceTitanClient, args: CreateBookingRequestInput) -> dict[str, Any]:
    """Execute the create_booking_request tool.
    
    Creates a pending booking request in the ServiceTitan dispatcher Calls inbox.
    
    Args:
        client: The ServiceTitan API client.
        args: The validated input arguments.
    
    Returns:
        A dict with id, status, and source fields.
    """
    url = "/crm/v2/tenant/" + client.tenant_id + "/bookings"
    
    payload = {
        "source": args.source,
        "summary": args.summary,
        "isFirstTimeClient": args.is_first_time_client,
        "name": args.name,
        "address": {
            "street": args.street,
            "city": args.city,
            "state": args.state,
            "zip": args.zip
        },
        "contacts": [
            {
                "type": "Phone",
                "value": args.phone
            }
        ]
    }
    
    response = await client.post(url, payload)
    
    return {
        "id": response.get("id", ""),
        "status": response.get("status", "Pending"),
        "source": response.get("source", args.source)
    }
