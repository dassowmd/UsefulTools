"""Tests for CSV batch processor with mocked Lob API calls."""

from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from address_verify.csv_processor import process_csv
from address_verify.models import VerificationResult


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    """Write a small sample CSV and return its path."""
    csv_path = tmp_path / "input.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["address1", "address2", "city", "state", "zip_code"])
        writer.writerow(["210 King St", "", "San Francisco", "CA", "94107"])
        writer.writerow(["185 Berry St", "Suite 100", "San Francisco", "CA", "94107"])
    return csv_path


@pytest.fixture()
def mock_verification_result():
    """A mock Lob UsVerification response."""
    components = SimpleNamespace()
    components.to_dict = lambda: {
        "primary_number": "210",
        "street_name": "KING",
        "street_suffix": "ST",
        "street_predirection": "",
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
    )
    resp.to_dict = lambda: {
        "id": "us_ver_abc123",
        "deliverability": "deliverable",
        "primary_line": "210 KING ST",
    }
    return resp


class TestProcessCSV:
    @patch("address_verify.csv_processor.AddressVerifier")
    def test_processes_all_rows(
        self, mock_verifier_cls, sample_csv, mock_verification_result, tmp_path
    ):
        verified_path = tmp_path / "verified.csv"
        errors_path = tmp_path / "errors.csv"

        mock_instance = MagicMock()
        mock_instance.verify_us.return_value = VerificationResult(
            id="us_ver_abc123",
            deliverability="deliverable",
            valid_address=True,
            primary_line="210 KING ST",
            secondary_line="",
            urbanization="",
            last_line="SAN FRANCISCO CA 94107-1702",
        )
        mock_verifier_cls.return_value = mock_instance

        counts = process_csv(
            input_path=sample_csv,
            verified_path=verified_path,
            errors_path=errors_path,
            column_mapping={
                "primary_line": "address1",
                "secondary_line": "address2",
                "city": "city",
                "state": "state",
                "zip_code": "zip_code",
            },
            api_key="test_key",
        )

        assert counts["total"] == 2
        assert counts["verified"] == 2
        assert counts["errors"] == 0
        assert mock_instance.verify_us.call_count == 2

        # Check that verified output has proper CSV format
        with open(verified_path) as f:
            reader = csv.reader(f)
            header = next(reader)
            assert "deliverability" in header
            assert "verified_primary_line" in header
            rows = list(reader)
            assert len(rows) == 2

    @patch("address_verify.csv_processor.AddressVerifier")
    def test_handles_api_errors(
        self, mock_verifier_cls, sample_csv, tmp_path
    ):
        verified_path = tmp_path / "verified.csv"
        errors_path = tmp_path / "errors.csv"

        mock_instance = MagicMock()
        mock_instance.verify_us.side_effect = Exception("API rate limit exceeded")
        mock_verifier_cls.return_value = mock_instance

        counts = process_csv(
            input_path=sample_csv,
            verified_path=verified_path,
            errors_path=errors_path,
            api_key="test_key",
        )

        assert counts["verified"] == 0
        assert counts["errors"] == 2

        with open(errors_path) as f:
            reader = csv.reader(f)
            header = next(reader)
            assert "error" in header
            rows = list(reader)
            assert len(rows) == 2
            assert "API rate limit exceeded" in rows[0][-1]

    @patch("address_verify.csv_processor.AddressVerifier")
    def test_progress_callback(
        self, mock_verifier_cls, sample_csv, tmp_path
    ):
        verified_path = tmp_path / "verified.csv"
        errors_path = tmp_path / "errors.csv"

        mock_instance = MagicMock()
        mock_instance.verify_us.return_value = VerificationResult(
            deliverability="deliverable",
            primary_line="TEST",
        )
        mock_verifier_cls.return_value = mock_instance

        progress_calls = []

        counts = process_csv(
            input_path=sample_csv,
            verified_path=verified_path,
            errors_path=errors_path,
            api_key="test_key",
            progress_callback=lambda current, total: progress_calls.append(
                (current, total)
            ),
        )

        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)

    @patch("address_verify.csv_processor.AddressVerifier")
    def test_output_uses_proper_csv_writer(
        self, mock_verifier_cls, tmp_path
    ):
        """Verify that commas in field values are properly escaped (fixes
        original verify.py bug where comma-separated string concat was used)."""
        csv_path = tmp_path / "input.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["address1", "address2", "city", "state", "zip_code"])
            writer.writerow(
                ["123 Main St, Bldg A", "Suite 100", "San Francisco", "CA", "94107"]
            )

        verified_path = tmp_path / "verified.csv"
        errors_path = tmp_path / "errors.csv"

        mock_instance = MagicMock()
        mock_instance.verify_us.return_value = VerificationResult(
            deliverability="deliverable",
            primary_line="123 MAIN ST BLDG A",
        )
        mock_verifier_cls.return_value = mock_instance

        process_csv(
            input_path=csv_path,
            verified_path=verified_path,
            errors_path=errors_path,
            api_key="test_key",
        )

        # Read back with csv.reader — the comma in the address should be
        # properly quoted, not splitting into extra columns.
        with open(verified_path) as f:
            reader = csv.reader(f)
            header = next(reader)
            row = next(reader)
            # Original 5 columns + 4 verification columns = 9
            assert len(row) == len(header)
            assert row[0] == "123 Main St, Bldg A"
