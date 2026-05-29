"""Pydantic v2 schemas for ServiceTitan MCP server."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Input Schemas ---

class SearchCustomersInput(BaseModel):
    """Input schema for searching customers."""
    name: Optional[str] = Field(None, description="First and/or last name")
    phone: Optional[str] = Field(None, description="Phone number (digits only or formatted)")
    email: Optional[str] = Field(None, description="Email address")


class GetAvailableSlotsInput(BaseModel):
    """Input schema for getting available appointment slots."""
    startsOnOrAfter: datetime = Field(..., description="Start of search window, ISO 8601")
    endsOnOrBefore: datetime = Field(..., description="End of search window, ISO 8601")
    jobTypeId: Optional[int] = Field(None, description="Optional job type ID to check specific capacity")


class CreateBookingRequestInput(BaseModel):
    """Input schema for creating a booking request."""
    name: str = Field(..., description="Customer's name")
    summary: str = Field(..., description="Summary of the service request")
    phone: str = Field(..., description="Customer's phone number")
    street: str = Field(..., description="Service address street")
    city: str = Field(..., description="Service address city")
    state: str = Field(..., description="Two-letter state code")
    zip: str = Field(..., description="Postal code")
    source: str = Field(default="AI Assistant", description="Source tag for the booking")
    isFirstTimeClient: bool = Field(default=False)


class ListJobsInput(BaseModel):
    """Input schema for listing jobs."""
    modifiedOnOrAfter: Optional[datetime] = Field(None, description="List jobs modified on or after this ISO 8601 timestamp")
    status: Optional[str] = Field(None, description="Filter by job status")
    page: int = Field(default=1, ge=1, description="Page number")
    pageSize: int = Field(default=50, ge=1, le=5000, description="Number of results per page")


class GetJobDetailsInput(BaseModel):
    """Input schema for getting job details."""
    jobId: int = Field(..., description="The specific ServiceTitan Job ID")


# --- Response Schemas ---

class CustomerContact(BaseModel):
    """Customer contact information."""
    type: str
    value: str


class CustomerData(BaseModel):
    """Customer data from search results."""
    id: int
    name: str
    active: bool
    contacts: list[CustomerContact]


class SearchCustomersResponse(BaseModel):
    """Response schema for customer search."""
    data: list[CustomerData]
    hasMore: bool


class AvailabilitySlot(BaseModel):
    """Available appointment slot."""
    start: str
    end: str
    available: bool


class GetAvailableSlotsResponse(BaseModel):
    """Response schema for available slots."""
    slots: list[AvailabilitySlot]


class BookingAddress(BaseModel):
    """Address for booking request."""
    street: str
    city: str
    state: str
    zip: str


class BookingContact(BaseModel):
    """Contact for booking request."""
    type: str
    value: str


class CreateBookingRequestResponse(BaseModel):
    """Response schema for booking request creation."""
    id: str
    status: str
    source: str


class JobType(BaseModel):
    """Job type information."""
    id: int
    name: str


class JobData(BaseModel):
    """Job data from list results."""
    id: int
    customerId: int
    status: str
    jobType: JobType
    modifiedOn: str


class ListJobsResponse(BaseModel):
    """Response schema for job listing."""
    data: list[JobData]
    hasMore: bool


class JobNote(BaseModel):
    """Job note."""
    id: int
    text: str


class GetJobDetailsResponse(BaseModel):
    """Response schema for job details."""
    id: int
    customerId: int
    status: str
    jobType: JobType
    notes: list[JobNote]
