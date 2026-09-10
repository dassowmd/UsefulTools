"""Core AddressVerifier class wrapping the Lob Python SDK v5."""

from __future__ import annotations

import os
from typing import List, Optional

import lob_python
from lob_python.api.intl_verifications_api import IntlVerificationsApi
from lob_python.api.us_verifications_api import UsVerificationsApi
from lob_python.model.country_extended import CountryExtended
from lob_python.model.intl_verification_writable import IntlVerificationWritable
from lob_python.model.multiple_components import MultipleComponents
from lob_python.model.multiple_components_list import MultipleComponentsList
from lob_python.model.us_verifications_writable import UsVerificationsWritable

from .models import (
    AddressComponents,
    DeliverabilityAnalysis,
    IntlAddress,
    IntlVerificationResult,
    LobConfidenceScore,
    USAddress,
    VerificationResult,
)


class AddressVerifier:
    """Reusable address verification client wrapping the Lob API.

    Args:
        api_key: Lob API key. Falls back to the ``LOB_API_KEY`` environment
            variable when not provided.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        key = api_key or os.environ.get("LOB_API_KEY")
        if not key:
            raise ValueError(
                "A Lob API key is required. Pass api_key or set LOB_API_KEY."
            )
        self._config = lob_python.Configuration(username=key)
        self._api_client = lob_python.ApiClient(self._config)
        self._us_api = UsVerificationsApi(self._api_client)
        self._intl_api = IntlVerificationsApi(self._api_client)

    # ------------------------------------------------------------------
    # US verification
    # ------------------------------------------------------------------

    def verify_us(self, address: USAddress) -> VerificationResult:
        """Verify a single US address.

        Args:
            address: A ``USAddress`` instance with the address components.

        Returns:
            A ``VerificationResult`` with deliverability and corrected fields.
        """
        writable_kwargs = {
            "primary_line": address.primary_line,
        }
        if address.secondary_line is not None:
            writable_kwargs["secondary_line"] = address.secondary_line
        if address.city is not None:
            writable_kwargs["city"] = address.city
        if address.state is not None:
            writable_kwargs["state"] = address.state
        if address.zip_code is not None:
            writable_kwargs["zip_code"] = address.zip_code
        if address.urbanization is not None:
            writable_kwargs["urbanization"] = address.urbanization
        if address.recipient is not None:
            writable_kwargs["recipient"] = address.recipient

        writable = UsVerificationsWritable(**writable_kwargs)
        response = self._us_api.verifySingle(
            writable, _check_return_type=False
        )
        return self._parse_us_response(response)

    def verify_us_bulk(
        self, addresses: List[USAddress]
    ) -> List[VerificationResult]:
        """Verify multiple US addresses in a single API call.

        Args:
            addresses: List of ``USAddress`` instances.

        Returns:
            List of ``VerificationResult`` objects (one per input address).
        """
        components_list = []
        for addr in addresses:
            kwargs = {"primary_line": addr.primary_line}
            if addr.secondary_line is not None:
                kwargs["secondary_line"] = addr.secondary_line
            if addr.city is not None:
                kwargs["city"] = addr.city
            if addr.state is not None:
                kwargs["state"] = addr.state
            if addr.zip_code is not None:
                kwargs["zip_code"] = addr.zip_code
            if addr.urbanization is not None:
                kwargs["urbanization"] = addr.urbanization
            if addr.recipient is not None:
                kwargs["recipient"] = addr.recipient
            components_list.append(MultipleComponents(**kwargs))

        bulk_payload = MultipleComponentsList(addresses=components_list)
        response = self._us_api.verifyBulk(
            bulk_payload, _check_return_type=False
        )

        results: List[VerificationResult] = []
        addresses = (
            response.get("addresses", [])
            if isinstance(response, dict)
            else response.addresses
        )
        for item in addresses:
            if isinstance(item, dict):
                raw = item
                has_error = bool(item.get("error"))
            else:
                raw = item.to_dict() if hasattr(item, "to_dict") else {}
                has_error = hasattr(item, "error") and item.error
            if has_error:
                results.append(
                    VerificationResult(
                        deliverability="error",
                        raw=raw,
                    )
                )
            else:
                results.append(self._parse_us_response(item))
        return results

    # ------------------------------------------------------------------
    # International verification
    # ------------------------------------------------------------------

    def verify_international(
        self, address: IntlAddress
    ) -> IntlVerificationResult:
        """Verify a single international (non-US) address.

        Args:
            address: An ``IntlAddress`` instance.

        Returns:
            An ``IntlVerificationResult`` with deliverability and components.
        """
        writable_kwargs = {
            "primary_line": address.primary_line,
            "country": CountryExtended(address.country),
        }
        if address.secondary_line is not None:
            writable_kwargs["secondary_line"] = address.secondary_line
        if address.city is not None:
            writable_kwargs["city"] = address.city
        if address.state is not None:
            writable_kwargs["state"] = address.state
        if address.postal_code is not None:
            writable_kwargs["postal_code"] = address.postal_code
        if address.recipient is not None:
            writable_kwargs["recipient"] = address.recipient

        writable = IntlVerificationWritable(**writable_kwargs)
        response = self._intl_api.verifySingle(
            writable, _check_return_type=False
        )
        return self._parse_intl_response(response)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_us_response(response: object) -> VerificationResult:
        if isinstance(response, dict):
            raw = response
        else:
            raw = response.to_dict() if hasattr(response, "to_dict") else {}

        def _get(key: str, default: object = None) -> object:
            if isinstance(response, dict):
                return response.get(key, default)
            return getattr(response, key, default)

        components = None
        comp_raw = _get("components")
        if comp_raw is not None:
            comp_dict = (
                comp_raw
                if isinstance(comp_raw, dict)
                else comp_raw.to_dict()
                if hasattr(comp_raw, "to_dict")
                else {}
            )
            zip_type = comp_dict.get("zip_code_type", "")
            if isinstance(zip_type, dict):
                zip_type = zip_type.get("value", "")
            else:
                zip_type = str(zip_type or "")
            components = AddressComponents(
                primary_number=comp_dict.get("primary_number", "") or "",
                street_predirection=comp_dict.get("street_predirection", "") or "",
                street_name=comp_dict.get("street_name", "") or "",
                street_suffix=comp_dict.get("street_suffix", "") or "",
                street_postdirection=comp_dict.get("street_postdirection", "") or "",
                secondary_designator=comp_dict.get("secondary_designator", "") or "",
                secondary_number=comp_dict.get("secondary_number", "") or "",
                city=comp_dict.get("city", "") or "",
                state=comp_dict.get("state", "") or "",
                zip_code=comp_dict.get("zip_code", "") or "",
                zip_code_plus_4=comp_dict.get("zip_code_plus_4", "") or "",
                zip_code_type=zip_type,
                address_type=comp_dict.get("address_type", "") or "",
                record_type=comp_dict.get("record_type", "") or "",
                county=comp_dict.get("county", "") or "",
                county_fips=comp_dict.get("county_fips", "") or "",
                carrier_route=comp_dict.get("carrier_route", "") or "",
                carrier_route_type=comp_dict.get("carrier_route_type", "") or "",
                latitude=comp_dict.get("latitude"),
                longitude=comp_dict.get("longitude"),
            )

        da = None
        da_raw = _get("deliverability_analysis")
        if da_raw is not None:
            da_dict = da_raw if isinstance(da_raw, dict) else (
                da_raw.to_dict() if hasattr(da_raw, "to_dict") else {}
            )
            da = DeliverabilityAnalysis(
                dpv_confirmation=da_dict.get("dpv_confirmation", "") or "",
                dpv_cmra=da_dict.get("dpv_cmra", "") or "",
                dpv_vacant=da_dict.get("dpv_vacant", "") or "",
                dpv_active=da_dict.get("dpv_active", "") or "",
                dpv_inactive_reason=da_dict.get("dpv_inactive_reason", "") or "",
                dpv_throwback=da_dict.get("dpv_throwback", "") or "",
                dpv_non_delivery_day_flag=da_dict.get("dpv_non_delivery_day_flag", "") or "",
                dpv_non_delivery_day_values=da_dict.get("dpv_non_delivery_day_values", "") or "",
                dpv_no_secure_location=da_dict.get("dpv_no_secure_location", "") or "",
                dpv_door_not_accessible=da_dict.get("dpv_door_not_accessible", "") or "",
                dpv_footnotes=da_dict.get("dpv_footnotes") or [],
                ews_match=bool(da_dict.get("ews_match", False)),
                lacs_indicator=da_dict.get("lacs_indicator", "") or "",
                lacs_return_code=da_dict.get("lacs_return_code", "") or "",
                suite_return_code=da_dict.get("suite_return_code", "") or "",
            )

        lcs = None
        lcs_raw = _get("lob_confidence_score")
        if lcs_raw is not None:
            lcs_dict = lcs_raw if isinstance(lcs_raw, dict) else (
                lcs_raw.to_dict() if hasattr(lcs_raw, "to_dict") else {}
            )
            lcs = LobConfidenceScore(
                score=lcs_dict.get("score"),
                level=lcs_dict.get("level", "") or "",
            )

        return VerificationResult(
            id=_get("id"),
            deliverability=_get("deliverability", "unknown") or "unknown",
            valid_address=_get("valid_address"),
            primary_line=_get("primary_line", "") or "",
            secondary_line=_get("secondary_line", "") or "",
            urbanization=_get("urbanization", "") or "",
            last_line=_get("last_line", "") or "",
            components=components,
            deliverability_analysis=da,
            lob_confidence_score=lcs,
            raw=raw,
        )

    @staticmethod
    def _parse_intl_response(response: object) -> IntlVerificationResult:
        if isinstance(response, dict):
            raw = response
        else:
            raw = response.to_dict() if hasattr(response, "to_dict") else {}

        def _get(key: str, default: object = None) -> object:
            if isinstance(response, dict):
                return response.get(key, default)
            return getattr(response, key, default)

        comp_raw = _get("components")
        if comp_raw is not None:
            comp = (
                comp_raw
                if isinstance(comp_raw, dict)
                else comp_raw.to_dict()
                if hasattr(comp_raw, "to_dict")
                else {}
            )
        else:
            comp = {}

        return IntlVerificationResult(
            id=_get("id"),
            deliverability=_get("deliverability", "") or "",
            primary_line=_get("primary_line", "") or "",
            secondary_line=_get("secondary_line", "") or "",
            last_line=_get("last_line", "") or "",
            country=_get("country", "") or "",
            components=comp,
            raw=raw,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._api_client.close()

    def __enter__(self) -> "AddressVerifier":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
