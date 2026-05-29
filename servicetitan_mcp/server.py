"""ServiceTitan MCP Server - Main entry point."""

import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from servicetitan_mcp.schemas import (
    SearchCustomersInput,
    GetAvailableSlotsInput,
    CreateBookingRequestInput,
    ListJobsInput,
    GetJobDetailsInput,
)
from servicetitan_mcp.client import ServiceTitanClient, ServiceTitanAPIError


APP_NAME = "servicetitan-mcp"
VERSION = "0.1.0"

server = Server(APP_NAME)


def get_client() -> ServiceTitanClient:
    """Get or create the ServiceTitan client instance."""
    return ServiceTitanClient()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="search_customers",
            description="Search for customer records in ServiceTitan by name, phone, or email. Returns active customers with contact details. Used by AI receptionists to identify an inbound caller.",
            inputSchema={
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
        ),
        Tool(
            name="get_available_slots",
            description="Retrieve live open booking windows from ServiceTitan Scheduling Pro based on dispatch availability. Returns time slots an AI receptionist can offer to a caller.",
            inputSchema={
                "type": "object",
                "properties": {
                    "startsOnOrAfter": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start of search window, ISO 8601"
                    },
                    "endsOnOrBefore": {
                        "type": "string",
                        "format": "date-time",
                        "description": "End of search window, ISO 8601"
                    },
                    "jobTypeId": {
                        "type": "integer",
                        "description": "Optional job type ID to check specific capacity"
                    }
                },
                "required": ["startsOnOrAfter", "endsOnOrBefore"]
            }
        ),
        Tool(
            name="create_booking_request",
            description="Create a pending booking request in the ServiceTitan dispatcher Calls inbox. This is the AI receptionist's primary write action. Returns the booking ID and pending status. A human dispatcher confirms and schedules the actual job.",
            inputSchema={
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
                        "default": "AI Assistant",
                        "description": "Source tag for the booking"
                    },
                    "isFirstTimeClient": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether this is a first-time client"
                    }
                },
                "required": ["name", "summary", "phone", "street", "city", "state", "zip"]
            }
        ),
        Tool(
            name="list_jobs",
            description="Query, filter, and fetch paginated jobs by status or modified-since timestamp. Used by AI dispatchers to monitor what is on the schedule.",
            inputSchema={
                "type": "object",
                "properties": {
                    "modifiedOnOrAfter": {
                        "type": "string",
                        "format": "date-time",
                        "description": "List jobs modified on or after this ISO 8601 timestamp"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["Unscheduled", "Scheduled", "Dispatched", "Arrived", "Complete", "Canceled"],
                        "description": "Filter by job status"
                    },
                    "page": {
                        "type": "integer",
                        "default": 1,
                        "minimum": 1,
                        "description": "Page number for pagination"
                    },
                    "pageSize": {
                        "type": "integer",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 5000,
                        "description": "Number of results per page"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_job_details",
            description="Retrieve comprehensive details for a single job by ID, including customer history notes. Used by AI assistants to read context before responding to a customer inquiry about their job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "jobId": {
                        "type": "integer",
                        "description": "The specific ServiceTitan Job ID"
                    }
                },
                "required": ["jobId"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
    client = get_client()
    
    try:
        if name == "search_customers":
            input_data = SearchCustomersInput(**arguments)
            result = await client.search_customers(
                name=input_data.name,
                phone=input_data.phone,
                email=input_data.email
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_available_slots":
            input_data = GetAvailableSlotsInput(**arguments)
            result = await client.get_available_slots(
                starts_on_or_after=input_data.startsOnOrAfter,
                ends_on_or_before=input_data.endsOnOrBefore,
                job_type_id=input_data.jobTypeId
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_booking_request":
            input_data = CreateBookingRequestInput(**arguments)
            result = await client.create_booking_request(
                name=input_data.name,
                summary=input_data.summary,
                phone=input_data.phone,
                street=input_data.street,
                city=input_data.city,
                state=input_data.state,
                zip=input_data.zip,
                source=input_data.source or "AI Assistant",
                is_first_time_client=input_data.isFirstTimeClient or False
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_jobs":
            input_data = ListJobsInput(**arguments)
            result = await client.list_jobs(
                modified_on_or_after=input_data.modifiedOnOrAfter,
                status=input_data.status,
                page=input_data.page or 1,
                page_size=input_data.pageSize or 50
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_job_details":
            input_data = GetJobDetailsInput(**arguments)
            result = await client.get_job_details(job_id=input_data.jobId)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]
    
    except ServiceTitanAPIError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Internal error: {str(e)}"}))]


async def main() -> None:
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main_sync() -> None:
    """Synchronous wrapper for the main entry point."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
