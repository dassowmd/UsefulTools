#!/usr/bin/env python3
"""Example: batch-verify addresses from a CSV file.

This replaces the original ``Address Verification/verify.py`` script.
Set the ``LOB_API_KEY`` environment variable before running, or use a
test key for dummy responses.

Usage:
    export LOB_API_KEY="test_..."
    python batch_verify.py input.csv
"""

from __future__ import annotations

import sys

from address_verify import AddressVerifier, USAddress, process_csv


def single_example() -> None:
    """Verify a single address."""
    with AddressVerifier() as verifier:
        result = verifier.verify_us(
            USAddress(
                primary_line="210 King St",
                city="San Francisco",
                state="CA",
                zip_code="94107",
            )
        )
    print(f"Deliverability: {result.deliverability}")
    print(f"Corrected:      {result.primary_line}, {result.last_line}")
    if result.components:
        print(f"ZIP+4:          {result.components.zip_code}-{result.components.zip_code_plus_4}")


def csv_example(input_path: str) -> None:
    """Verify all addresses in a CSV file."""
    counts = process_csv(
        input_path=input_path,
        verified_path="verified.csv",
        errors_path="errors.csv",
        column_mapping={
            "primary_line": "address1",
            "secondary_line": "address2",
            "city": "city",
            "state": "state",
            "zip_code": "zip_code",
        },
    )
    print(
        f"\nResults: {counts['verified']} verified, "
        f"{counts['errors']} errors out of {counts['total']} total."
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_example(sys.argv[1])
    else:
        single_example()
