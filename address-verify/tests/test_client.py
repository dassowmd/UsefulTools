"""Tests for AddressVerifier client with mocked Lob API calls."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from address_verify.client import AddressVerifier
from address_verify.models import IntlAddress, USAddress


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_us_response():
    """Return a mock object mimicking a Lob UsVerification response."""
    components = SimpleNamespace(
        primary_number="210",
        street_predirection="",
        street_name="KING",
        street_suffix="ST",
        street_postdirection="",
        secondary_designator="",
        secondary_number="",
        city="SAN FRANCISCO",
        state="CA",
        zip_code="94107",
        zip_code_plus_4="1702",
        zip_code_type="STANDARD",
        address_type="commercial",
        record_type="street",
        county="SAN FRANCISCO",
        county_fips="06075",
        carrier_route="C001",
        carrier_route_type="city_delivery",
        default_building_address=True,
        po_box_only_flag="N",
    )
    components.to_dict = lambda: {
        "primary_number": "210",
        "street_predirection": "",
        "street_name": "KING",
        "street_suffix": "ST",
        "street_postdirection": "",
        "secondary_designator": "",
        "secondary_number": "",
        "city": "SAN FRANCISCO",
        "state": "CA",
        "zip_code": "94107",
        "zip_code_plus_4": "1702",
        "zip_code_type": "STANDARD",
        "address_type": "commercial",
        "record_type": "street",
        "county": "SAN FRANCISCO",
        "county_fips": "06075",
        "carrier_route": "C001",
        "carrier_route_type": "city_delivery",
    }

    resp = SimpleNamespace(
        id="us_ver_abc123",
        deliverability="deliverable",
        valid_address=True,
        primary_line="210 KING ST",
        secondary_line="",
        urbanization="",
        last_line="SAN FRANCISCO CA 94107-1702",
        components=components,
        deliverability_analysis=None,
        lob_confidence_score=None,
        object="us_verification",
    )
    resp.to_dict = lambda: {
        "id": "us_ver_abc123",
        "deliverability": "deliverable",
        "valid_address": True,
        "primary_line": "210 KING ST",
        "secondary_line": "",
        "urbanization": "",
        "last_line": "SAN FRANCISCO CA 94107-1702",
    }
    return resp


@pytest.fixture()
def mock_intl_response():
    """Return a mock object mimicking a Lob IntlVerification response."""
    components = SimpleNamespace()
    components.to_dict = lambda: {
        "primary_number": "370",
        "street_name": "WATER ST",
        "city": "SUMMERSIDE",
        "state": "PE",
        "postal_code": "C1N 1C4",
        "country": "CA",
    }

    resp = SimpleNamespace(
        id="intl_ver_xyz789",
        deliverability="deliverable",
        primary_line="370 WATER ST",
        secondary_line="",
        last_line="SUMMERSIDE PE C1N 1C4",
        country="CA",
        components=components,
    )
    resp.to_dict = lambda: {
        "id": "intl_ver_xyz789",
        "deliverability": "deliverable",
        "primary_line": "370 WATER ST",
        "secondary_line": "",
        "last_line": "SUMMERSIDE PE C1N 1C4",
        "country": "CA",
    }
    return resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAddressVerifierInit:
    def test_requires_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            # Remove LOB_API_KEY if present
            import os

            os.environ.pop("LOB_API_KEY", None)
            with pytest.raises(ValueError, match="Lob API key is required"):
                AddressVerifier()

    def test_accepts_explicit_key(self):
        verifier = AddressVerifier(api_key="test_key_123")
        assert verifier._config.username == "test_key_123"
        verifier.close()

    def test_reads_env_var(self):
        with patch.dict("os.environ", {"LOB_API_KEY": "env_key_456"}):
            verifier = AddressVerifier()
            assert verifier._config.username == "env_key_456"
            verifier.close()

    def test_context_manager(self):
        with AddressVerifier(api_key="test_key") as verifier:
            assert verifier is not None


class TestVerifyUS:
    @patch("address_verify.client.UsVerificationsApi")
    @patch("address_verify.client.lob_python.ApiClient")
    @patch("address_verify.client.lob_python.Configuration")
    def test_verify_single_address(
        self, mock_config_cls, mock_client_cls, mock_api_cls, mock_us_response
    ):
        mock_api_instance = MagicMock()
        mock_api_instance.verifySingle.return_value = mock_us_response
        mock_api_cls.return_value = mock_api_instance

        verifier = AddressVerifier(api_key="test_key")
        result = verifier.verify_us(
            USAddress(
                primary_line="210 King St",
                city="San Francisco",
                state="CA",
                zip_code="94107",
            )
        )

        assert result.deliverability == "deliverable"
        assert result.is_deliverable is True
        assert result.valid_address is True
        assert result.primary_line == "210 KING ST"
        assert result.last_line == "SAN FRANCISCO CA 94107-1702"
        assert result.components is not None
        assert result.components.city == "SAN FRANCISCO"
        assert result.components.state == "CA"
        assert result.components.zip_code == "94107"

        mock_api_instance.verifySingle.assert_called_once()
        verifier.close()

    @patch("address_verify.client.UsVerificationsApi")
    @patch("address_verify.client.lob_python.ApiClient")
    @patch("address_verify.client.lob_python.Configuration")
    def test_undeliverable_address(
        self, mock_config_cls, mock_client_cls, mock_api_cls
    ):
        undeliverable = SimpleNamespace(
            id="us_ver_bad",
            deliverability="undeliverable",
            valid_address=False,
            primary_line="999 FAKE ST",
            secondary_line="",
            urbanization="",
            last_line="NOWHERE CA 00000",
            components=None,
            deliverability_analysis=None,
        )
        undeliverable.to_dict = lambda: {"deliverability": "undeliverable"}

        mock_api_instance = MagicMock()
        mock_api_instance.verifySingle.return_value = undeliverable
        mock_api_cls.return_value = mock_api_instance

        verifier = AddressVerifier(api_key="test_key")
        result = verifier.verify_us(
            USAddress(primary_line="999 Fake St", city="Nowhere", state="CA")
        )

        assert result.deliverability == "undeliverable"
        assert result.is_deliverable is False
        assert result.components is None
        verifier.close()


class TestVerifyUSBulk:
    @patch("address_verify.client.UsVerificationsApi")
    @patch("address_verify.client.lob_python.ApiClient")
    @patch("address_verify.client.lob_python.Configuration")
    def test_bulk_verify(
        self, mock_config_cls, mock_client_cls, mock_api_cls, mock_us_response
    ):
        bulk_response = SimpleNamespace(addresses=[mock_us_response])
        mock_api_instance = MagicMock()
        mock_api_instance.verifyBulk.return_value = bulk_response
        mock_api_cls.return_value = mock_api_instance

        verifier = AddressVerifier(api_key="test_key")
        results = verifier.verify_us_bulk(
            [
                USAddress(
                    primary_line="210 King St",
                    city="San Francisco",
                    state="CA",
                    zip_code="94107",
                )
            ]
        )

        assert len(results) == 1
        assert results[0].deliverability == "deliverable"
        mock_api_instance.verifyBulk.assert_called_once()
        verifier.close()


class TestVerifyInternational:
    @patch("address_verify.client.CountryExtended")
    @patch("address_verify.client.IntlVerificationWritable")
    @patch("address_verify.client.IntlVerificationsApi")
    @patch("address_verify.client.UsVerificationsApi")
    @patch("address_verify.client.lob_python.ApiClient")
    @patch("address_verify.client.lob_python.Configuration")
    def test_verify_intl_address(
        self,
        mock_config_cls,
        mock_client_cls,
        mock_us_api_cls,
        mock_intl_api_cls,
        mock_intl_writable_cls,
        mock_country_cls,
        mock_intl_response,
    ):
        mock_intl_instance = MagicMock()
        mock_intl_instance.verifySingle.return_value = mock_intl_response
        mock_intl_api_cls.return_value = mock_intl_instance

        verifier = AddressVerifier(api_key="test_key")
        result = verifier.verify_international(
            IntlAddress(
                primary_line="370 Water St",
                city="Summerside",
                state="PE",
                postal_code="C1N 1C4",
                country="CA",
            )
        )

        assert result.deliverability == "deliverable"
        assert result.is_deliverable is True
        assert result.primary_line == "370 WATER ST"
        assert result.country == "CA"
        mock_intl_instance.verifySingle.assert_called_once()
        mock_country_cls.assert_called_once_with("CA")
        verifier.close()
