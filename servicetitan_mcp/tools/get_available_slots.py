"""Tool to retrieve live open booking windows from ServiceTitan Scheduling Pro."""

from typing import Any, Optional

from servicetitan_mcp.client import ServiceTitanClient
from servicetitan_mcp.schemas import GetAvailableSlotsInput


async def get_available_slots(
    client: ServiceTitanClient,
    input_data: GetAvailableSlotsInput,
) -> dict[str, Any]:
    """
    Retrieve live open booking windows from ServiceTitan Scheduling Pro.

    Args:
        client: ServiceTitanClient instance.
        input_data: Input schema with startsOnOrAfter, endsOnOrBefore, jobTypeId.

    Returns:
        Dict with 'slots' list containing start, end, available fields.
    """
    params: dict[str, Any] = {
        "startsOnOrAfter": input_data.startsOnOrAfter,
        "endsOnOrBefore": input_data.endsOnOrBefore,
    }

    if input_data.jobTypeId is not None:
        params["jobTypeId"] = str(input_data.jobTypeId)

    response = await client.get(
        "/scheduling-pro/v2/tenant/{tenant_id}/availability",
        params=params,
    )

    return response
