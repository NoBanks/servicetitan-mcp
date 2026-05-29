"""Tool: get_job_details - Retrieve comprehensive details for a single job by ID."""

from typing import Any

from pydantic import Field

from servicetitan_mcp.schemas import BaseToolInput
from servicetitan_mcp.client import ServiceTitanClient


class GetJobDetailsInput(BaseToolInput):
    """Input schema for get_job_details tool."""

    job_id: int = Field(
        description="The specific ServiceTitan Job ID",
        gt=0,
    )


TOOL_DEFINITION = {
    "name": "get_job_details",
    "description": "Retrieve comprehensive details for a single job by ID, including customer history notes. Used by AI assistants to read context before responding to a customer inquiry about their job.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "integer",
                "description": "The specific ServiceTitan Job ID",
            },
        },
        "required": ["job_id"],
    },
}


def get_job_details(client: ServiceTitanClient, job_id: int) -> dict[str, Any]:
    """Retrieve comprehensive details for a single job by ID.

    Args:
        client: ServiceTitanClient instance.
        job_id: The specific ServiceTitan Job ID.

    Returns:
        Job details including id, customerId, status, jobType, and notes.
    """
    tenant_id = client.tenant_id
    url = f"https://api.servicetitan.io/jpm/v2/tenant/{tenant_id}/jobs/{job_id}"

    response = client.get(url)

    result = {
        "id": response.get("id"),
        "customerId": response.get("customerId"),
        "status": response.get("status"),
        "jobType": response.get("jobType"),
        "notes": response.get("notes", []),
    }

    return result
