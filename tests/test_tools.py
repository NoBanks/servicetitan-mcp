"""Tests for servicetitan-mcp tool input schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from servicetitan_mcp.schemas import (
    SearchCustomersInput,
    GetAvailableSlotsInput,
    CreateBookingRequestInput,
    ListJobsInput,
    GetJobDetailsInput,
)


class TestSearchCustomersInput:
    def test_all_fields_optional(self):
        inp = SearchCustomersInput()
        assert inp.name is None
        assert inp.phone is None
        assert inp.email is None

    def test_partial_fields(self):
        inp = SearchCustomersInput(phone="555-123-4567")
        assert inp.phone == "555-123-4567"
        assert inp.name is None


class TestGetAvailableSlotsInput:
    def test_requires_time_window(self):
        with pytest.raises(ValidationError):
            GetAvailableSlotsInput()

    def test_accepts_iso_datetimes(self):
        inp = GetAvailableSlotsInput(
            startsOnOrAfter=datetime(2026, 6, 1, 8, 0),
            endsOnOrBefore=datetime(2026, 6, 1, 18, 0),
        )
        assert inp.jobTypeId is None

    def test_optional_job_type(self):
        inp = GetAvailableSlotsInput(
            startsOnOrAfter=datetime(2026, 6, 1, 8, 0),
            endsOnOrBefore=datetime(2026, 6, 1, 18, 0),
            jobTypeId=3058,
        )
        assert inp.jobTypeId == 3058


class TestCreateBookingRequestInput:
    def test_requires_core_fields(self):
        with pytest.raises(ValidationError):
            CreateBookingRequestInput(name="Jane Doe")

    def test_complete_booking(self):
        inp = CreateBookingRequestInput(
            name="Jane Doe",
            summary="AC diagnostic",
            phone="555-123-4567",
            street="123 Main St",
            city="Glendale",
            state="CA",
            zip="91203",
        )
        assert inp.source == "AI Assistant"
        assert inp.isFirstTimeClient is False

    def test_source_override(self):
        inp = CreateBookingRequestInput(
            name="Jane Doe",
            summary="HVAC repair",
            phone="555-123-4567",
            street="123 Main St",
            city="Glendale",
            state="CA",
            zip="91203",
            source="AI Chatbot",
            isFirstTimeClient=True,
        )
        assert inp.source == "AI Chatbot"
        assert inp.isFirstTimeClient is True


class TestListJobsInput:
    def test_defaults(self):
        inp = ListJobsInput()
        assert inp.page == 1
        assert inp.pageSize == 50
        assert inp.status is None

    def test_page_size_bounds(self):
        with pytest.raises(ValidationError):
            ListJobsInput(pageSize=0)
        with pytest.raises(ValidationError):
            ListJobsInput(pageSize=5001)

    def test_status_filter(self):
        inp = ListJobsInput(status="Scheduled")
        assert inp.status == "Scheduled"


class TestGetJobDetailsInput:
    def test_requires_job_id(self):
        with pytest.raises(ValidationError):
            GetJobDetailsInput()

    def test_accepts_job_id(self):
        inp = GetJobDetailsInput(jobId=845118)
        assert inp.jobId == 845118
