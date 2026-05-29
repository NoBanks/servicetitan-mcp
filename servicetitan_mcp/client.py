"""
ServiceTitan API client with OAuth 2.0 Client Credentials authentication.
"""
import os
import time
from typing import Any, Optional

import httpx


class ServiceTitanAPIError(Exception):
    """Raised when the ServiceTitan API returns an error."""
    pass


class ServiceTitanAuthError(Exception):
    """Raised when OAuth authentication fails."""
    pass


class ServiceTitanClient:
    """
    Async client for ServiceTitan V2 API with OAuth 2.0 Client Credentials.
    
    Automatically manages access token lifecycle with 60-second safety buffer.
    Requires environment variables:
    - SERVICETITAN_CLIENT_ID
    - SERVICETITAN_CLIENT_SECRET
    - SERVICETITAN_APP_KEY
    - SERVICETITAN_TENANT_ID
    """
    
    BASE_URL = "https://api.servicetitan.io"
    AUTH_URL = "https://auth.servicetitan.io/connect/token"
    TOKEN_SAFETY_BUFFER = 60  # seconds
    
    def __init__(self) -> None:
        self.client_id = os.environ.get("SERVICETITAN_CLIENT_ID")
        self.client_secret = os.environ.get("SERVICETITAN_CLIENT_SECRET")
        self.app_key = os.environ.get("SERVICETITAN_APP_KEY")
        self.tenant_id = os.environ.get("SERVICETITAN_TENANT_ID")
        
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._http_client = httpx.AsyncClient(timeout=30.0)
    
    def _validate_config(self) -> None:
        """Validate that all required environment variables are set."""
        missing = []
        if not self.client_id:
            missing.append("SERVICETITAN_CLIENT_ID")
        if not self.client_secret:
            missing.append("SERVICETITAN_CLIENT_SECRET")
        if not self.app_key:
            missing.append("SERVICETITAN_APP_KEY")
        if not self.tenant_id:
            missing.append("SERVICETITAN_TENANT_ID")
        
        if missing:
            raise ServiceTitanAuthError(
                "Missing required environment variables: " + ", ".join(missing)
            )
    
    async def _ensure_valid_token(self) -> str:
        """Ensure we have a valid access token, refreshing if necessary."""
        self._validate_config()
        
        current_time = time.time()
        buffer = self.TOKEN_SAFETY_BUFFER
        
        if not self._access_token or current_time >= (self._token_expires_at - buffer):
            await self._refresh_token()
        
        return self._access_token
    
    async def _refresh_token(self) -> None:
        """Refresh the OAuth access token via Client Credentials flow."""
        data = (
            "grant_type=client_credentials"
            + "&client_id=" + self.client_id
            + "&client_secret=" + self.client_secret
        )
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        response = await self._http_client.post(
            self.AUTH_URL,
            content=data,
            headers=headers,
        )
        
        if response.status_code != 200:
            raise ServiceTitanAuthError(
                "OAuth authentication failed: " + str(response.status_code) + " " + response.text
            )
        
        token_data = response.json()
        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 900)
        self._token_expires_at = time.time() + expires_in
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to the ServiceTitan API."""
        token = await self._ensure_valid_token()
        
        headers = {
            "Authorization": "Bearer " + token,
            "ST-App-Key": self.app_key,
        }
        
        url = self.BASE_URL + endpoint
        
        response = await self._http_client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
        )
        
        if response.status_code == 429:
            raise ServiceTitanAPIError(
                "rate limited, ServiceTitan caps at 60 req/sec per tenant, retry with backoff"
            )
        
        if response.status_code >= 400:
            raise ServiceTitanAPIError(
                "API error: " + str(response.status_code) + " " + response.text
            )
        
        return response.json()
    
    async def search_customers(
        self,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Search for customer records in ServiceTitan by name, phone, or email.
        
        Returns active customers with contact details.
        """
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        if phone:
            params["phone"] = phone
        if email:
            params["email"] = email
        
        endpoint = "/crm/v2/tenant/" + self.tenant_id + "/customers"
        return await self._request("GET", endpoint, params=params)
    
    async def get_available_slots(
        self,
        starts_on_or_after: str,
        ends_on_or_before: str,
        job_type_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Retrieve live open booking windows from ServiceTitan Scheduling Pro.
        
        Returns time slots available for booking.
        """
        params: dict[str, Any] = {
            "startsOnOrAfter": starts_on_or_after,
            "endsOnOrBefore": ends_on_or_before,
        }
        if job_type_id is not None:
            params["jobTypeId"] = job_type_id
        
        endpoint = "/scheduling-pro/v2/tenant/" + self.tenant_id + "/availability"
        return await self._request("GET", endpoint, params=params)
    
    async def create_booking_request(
        self,
        name: str,
        summary: str,
        phone: str,
        street: str,
        city: str,
        state: str,
        zip: str,
        source: str = "AI Assistant",
        is_first_time_client: bool = False,
    ) -> dict[str, Any]:
        """
        Create a pending booking request in the ServiceTitan dispatcher Calls inbox.
        
        Returns the booking ID and pending status.
        """
        body: dict[str, Any] = {
            "source": source,
            "summary": summary,
            "isFirstTimeClient": is_first_time_client,
            "name": name,
            "address": {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip,
            },
            "contacts": [
                {"type": "Phone", "value": phone},
            ],
        }
        
        endpoint = "/crm/v2/tenant/" + self.tenant_id + "/bookings"
        return await self._request("POST", endpoint, json_data=body)
    
    async def list_jobs(
        self,
        modified_on_or_after: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """
        Query and fetch paginated jobs by status or modified-since timestamp.
        
        Returns jobs with pagination info.
        """
        params: dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
        }
        if modified_on_or_after:
            params["modifiedOnOrAfter"] = modified_on_or_after
        if status:
            params["status"] = status
        
        endpoint = "/jpm/v2/tenant/" + self.tenant_id + "/jobs"
        return await self._request("GET", endpoint, params=params)
    
    async def get_job_details(self, job_id: int) -> dict[str, Any]:
        """
        Retrieve comprehensive details for a single job by ID.
        
        Returns job details including customer history notes.
        """
        endpoint = "/jpm/v2/tenant/" + self.tenant_id + "/jobs/" + str(job_id)
        return await self._request("GET", endpoint)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()
    
    async def __aenter__(self) -> "ServiceTitanClient":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
