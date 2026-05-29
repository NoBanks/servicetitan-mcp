"""List jobs tool for ServiceTitan MCP server."""

from typing import Any

from mcp.types import Tool, TextContent

from servicetitan_mcp.schemas import ListJobsInput
from servicetitan_mcp.client import ServiceTitanClient


def get_list_jobs_tool() -> Tool:
    """Return the list_jobs tool definition."""
    return Tool(
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
    )


async def list_jobs(client: ServiceTitanClient, args: dict[str, Any]) -> TextContent:
    """Execute the list_jobs tool."""
    validated = ListJobsInput(**args)
    
    params: dict[str, Any] = {}
    
    if validated.modifiedOnOrAfter:
        params["modifiedOnOrAfter"] = validated.modifiedOnOrAfter.isoformat()
    
    if validated.status:
        params["status"] = validated.status
    
    params["page"] = validated.page
    params["pageSize"] = validated.pageSize
    
    response = await client.get(
        "/jpm/v2/tenant/{tenant_id}/jobs",
        params=params
    )
    
    return TextContent(
        type="text",
        text=response
    )
