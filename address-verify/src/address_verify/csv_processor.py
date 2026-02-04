"""Batch CSV address verification processor."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Callable, Dict, Optional

from .client import AddressVerifier
from .models import USAddress


# Default column mapping matching the original verify.py indices:
# address1=3, address2=4, city=6, country=7, postcode=8, state=9
DEFAULT_COLUMN_MAPPING: Dict[str, str] = {
    "primary_line": "address1",
    "secondary_line": "address2",
    "city": "city",
    "state": "state",
    "zip_code": "zip_code",
}


def process_csv(
    input_path: str | Path,
    verified_path: str | Path,
    errors_path: str | Path,
    column_mapping: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None,
    has_header: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> Dict[str, int]:
    """Read addresses from a CSV, verify each one, and write results.

    Args:
        input_path: Path to the input CSV file.
        verified_path: Path for the verified-addresses output CSV.
        errors_path: Path for the error-addresses output CSV.
        column_mapping: Maps USAddress field names to CSV column headers.
            Defaults to ``DEFAULT_COLUMN_MAPPING``.
        api_key: Lob API key (falls back to ``LOB_API_KEY`` env var).
        has_header: Whether the input CSV has a header row.
        progress_callback: Optional ``callback(current_row, total_rows)``
            called after each row is processed.

    Returns:
        Dict with counts: ``{"verified": N, "errors": N, "total": N}``.
    """
    input_path = Path(input_path)
    verified_path = Path(verified_path)
    errors_path = Path(errors_path)
    mapping = column_mapping or DEFAULT_COLUMN_MAPPING

    verifier = AddressVerifier(api_key=api_key)

    # First pass: count rows for progress reporting
    with open(input_path, newline="", encoding="utf-8") as f:
        total = sum(1 for _ in f)
    if has_header:
        total = max(total - 1, 0)

    verified_count = 0
    error_count = 0

    with (
        open(input_path, newline="", encoding="utf-8") as infile,
        open(verified_path, "w", newline="", encoding="utf-8") as vfile,
        open(errors_path, "w", newline="", encoding="utf-8") as efile,
    ):
        reader = csv.DictReader(infile) if has_header else csv.reader(infile)
        v_writer = csv.writer(vfile)
        e_writer = csv.writer(efile)

        if has_header:
            # Write header rows
            assert isinstance(reader, csv.DictReader)
            fieldnames = reader.fieldnames or []
            v_header = list(fieldnames) + [
                "deliverability",
                "verified_primary_line",
                "verified_secondary_line",
                "verified_last_line",
            ]
            e_header = list(fieldnames) + ["error"]
            v_writer.writerow(v_header)
            e_writer.writerow(e_header)

        for idx, row in enumerate(reader):
            if progress_callback:
                progress_callback(idx + 1, total)
            else:
                sys.stdout.write(".")
                sys.stdout.flush()

            try:
                if has_header:
                    assert isinstance(row, dict)
                    address = _row_dict_to_address(row, mapping)
                    row_values = list(row.values())
                else:
                    assert isinstance(row, list)
                    address = _row_list_to_address(row, mapping)
                    row_values = list(row)

                result = verifier.verify_us(address)
                v_writer.writerow(
                    row_values
                    + [
                        result.deliverability,
                        result.primary_line,
                        result.secondary_line,
                        result.last_line,
                    ]
                )
                verified_count += 1
            except Exception as e:
                if has_header:
                    assert isinstance(row, dict)
                    row_values = list(row.values())
                else:
                    assert isinstance(row, list)
                    row_values = list(row)
                e_writer.writerow(row_values + [str(e)])
                error_count += 1

    sys.stdout.write("\n")
    verifier.close()

    return {
        "verified": verified_count,
        "errors": error_count,
        "total": verified_count + error_count,
    }


def _row_dict_to_address(
    row: Dict[str, str], mapping: Dict[str, str]
) -> USAddress:
    """Build a USAddress from a csv.DictReader row using the column mapping."""
    return USAddress(
        primary_line=row.get(mapping.get("primary_line", ""), ""),
        secondary_line=row.get(mapping.get("secondary_line", "")) or None,
        city=row.get(mapping.get("city", "")) or None,
        state=row.get(mapping.get("state", "")) or None,
        zip_code=row.get(mapping.get("zip_code", "")) or None,
    )


def _row_list_to_address(
    row: list, mapping: Dict[str, int | str]
) -> USAddress:
    """Build a USAddress from a csv.reader list row using index mapping."""
    def _get(key: str) -> str:
        idx = mapping.get(key)
        if idx is None:
            return ""
        if isinstance(idx, int) and idx < len(row):
            return row[idx]
        return ""

    return USAddress(
        primary_line=_get("primary_line"),
        secondary_line=_get("secondary_line") or None,
        city=_get("city") or None,
        state=_get("state") or None,
        zip_code=_get("zip_code") or None,
    )
