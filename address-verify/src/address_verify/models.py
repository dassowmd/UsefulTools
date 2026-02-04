"""Pydantic models for address verification input/output."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class USAddress(BaseModel):
    """Input model for US address verification."""

    primary_line: str = Field(..., description="Street address (e.g. '210 King St')")
    secondary_line: Optional[str] = Field(
        default=None, description="Apartment, suite, etc."
    )
    city: Optional[str] = Field(
        default=None,
        description="City name. Required with state if zip_code is not provided.",
    )
    state: Optional[str] = Field(
        default=None,
        description="Two-letter state code. Required with city if zip_code is not provided.",
    )
    zip_code: Optional[str] = Field(
        default=None,
        description="5-digit ZIP code. Required if city/state not provided.",
    )
    urbanization: Optional[str] = Field(
        default=None, description="Puerto Rico urbanization name."
    )
    recipient: Optional[str] = Field(
        default=None, description="Intended recipient at the address."
    )


class IntlAddress(BaseModel):
    """Input model for international address verification."""

    primary_line: str = Field(..., description="Street address")
    secondary_line: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    postal_code: Optional[str] = Field(default=None)
    country: str = Field(..., description="Two-letter ISO country code (e.g. 'CA')")
    recipient: Optional[str] = Field(default=None)


class AddressComponents(BaseModel):
    """Parsed address components from a US verification response."""

    primary_number: str = ""
    street_predirection: str = ""
    street_name: str = ""
    street_suffix: str = ""
    street_postdirection: str = ""
    secondary_designator: str = ""
    secondary_number: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    zip_code_plus_4: str = ""
    zip_code_type: str = ""
    address_type: str = ""
    record_type: str = ""
    county: str = ""
    county_fips: str = ""
    carrier_route: str = ""
    carrier_route_type: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DeliverabilityAnalysis(BaseModel):
    """USPS Delivery Point Validation analysis."""

    dpv_confirmation: str = ""
    dpv_cmra: str = ""
    dpv_vacant: str = ""
    dpv_active: str = ""
    dpv_inactive_reason: str = ""
    dpv_throwback: str = ""
    dpv_non_delivery_day_flag: str = ""
    dpv_non_delivery_day_values: str = ""
    dpv_no_secure_location: str = ""
    dpv_door_not_accessible: str = ""
    dpv_footnotes: List[str] = Field(default_factory=list)
    ews_match: bool = False
    lacs_indicator: str = ""
    lacs_return_code: str = ""
    suite_return_code: str = ""


class LobConfidenceScore(BaseModel):
    """Lob's confidence score for the address."""

    score: Optional[float] = None
    level: str = ""


class VerificationResult(BaseModel):
    """Output model for an address verification response."""

    id: Optional[str] = None
    deliverability: str = Field(
        ...,
        description=(
            "One of: deliverable, deliverable_unnecessary_unit, "
            "deliverable_incorrect_unit, deliverable_missing_unit, undeliverable"
        ),
    )
    valid_address: Optional[bool] = None
    primary_line: str = ""
    secondary_line: str = ""
    urbanization: str = ""
    last_line: str = ""
    components: Optional[AddressComponents] = None
    deliverability_analysis: Optional[DeliverabilityAnalysis] = None
    lob_confidence_score: Optional[LobConfidenceScore] = None
    raw: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full raw response from the Lob API.",
    )

    @property
    def is_deliverable(self) -> bool:
        """Return True if the address is deliverable."""
        return self.deliverability.startswith("deliverable")


class IntlVerificationResult(BaseModel):
    """Output model for an international address verification response."""

    id: Optional[str] = None
    deliverability: str = ""
    primary_line: str = ""
    secondary_line: str = ""
    last_line: str = ""
    country: str = ""
    components: Dict[str, Any] = Field(default_factory=dict)
    raw: Dict[str, Any] = Field(default_factory=dict)

    @property
    def is_deliverable(self) -> bool:
        return self.deliverability.startswith("deliverable")
