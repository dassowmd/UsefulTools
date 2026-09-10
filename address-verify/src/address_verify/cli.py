"""CLI entrypoint for address-verify."""

from __future__ import annotations

import click

from .client import AddressVerifier
from .csv_processor import process_csv
from .models import USAddress


@click.group()
def cli() -> None:
    """Address verification powered by the Lob API."""


@cli.command()
@click.argument("input_csv", type=click.Path(exists=True))
@click.option(
    "--verified",
    "verified_path",
    default="verified.csv",
    show_default=True,
    help="Output path for verified addresses.",
)
@click.option(
    "--errors",
    "errors_path",
    default="errors.csv",
    show_default=True,
    help="Output path for addresses that failed verification.",
)
@click.option("--api-key", envvar="LOB_API_KEY", help="Lob API key.")
@click.option(
    "--no-header",
    is_flag=True,
    default=False,
    help="Input CSV has no header row.",
)
def verify(
    input_csv: str,
    verified_path: str,
    errors_path: str,
    api_key: str | None,
    no_header: bool,
) -> None:
    """Verify addresses from a CSV file.

    Reads INPUT_CSV, verifies each row via the Lob API, and writes results
    to --verified and --errors output files.
    """
    click.echo(f"Processing {input_csv} ...")
    counts = process_csv(
        input_path=input_csv,
        verified_path=verified_path,
        errors_path=errors_path,
        api_key=api_key,
        has_header=not no_header,
    )
    click.echo(
        f"Done. {counts['verified']} verified, "
        f"{counts['errors']} errors, {counts['total']} total."
    )


@cli.command("verify-single")
@click.argument("primary_line")
@click.option("--secondary", default=None, help="Secondary line (apt, suite, etc).")
@click.option("--city", default=None, help="City name.")
@click.option("--state", default=None, help="Two-letter state code.")
@click.option("--zip", "zip_code", default=None, help="5-digit ZIP code.")
@click.option("--api-key", envvar="LOB_API_KEY", help="Lob API key.")
def verify_single(
    primary_line: str,
    secondary: str | None,
    city: str | None,
    state: str | None,
    zip_code: str | None,
    api_key: str | None,
) -> None:
    """Verify a single US address.

    Example:

        address-verify verify-single "210 King St" --city "San Francisco" --state CA --zip 94107
    """
    address = USAddress(
        primary_line=primary_line,
        secondary_line=secondary,
        city=city,
        state=state,
        zip_code=zip_code,
    )

    with AddressVerifier(api_key=api_key) as verifier:
        result = verifier.verify_us(address)

    click.echo(f"Deliverability: {result.deliverability}")
    click.echo(f"Valid address:  {result.valid_address}")
    click.echo(f"Primary line:   {result.primary_line}")
    click.echo(f"Secondary line: {result.secondary_line}")
    click.echo(f"Last line:      {result.last_line}")
    if result.components:
        click.echo(f"City:           {result.components.city}")
        click.echo(f"State:          {result.components.state}")
        click.echo(f"ZIP:            {result.components.zip_code}")
        click.echo(f"ZIP+4:          {result.components.zip_code_plus_4}")
        if result.components.latitude is not None:
            click.echo(f"Latitude:       {result.components.latitude}")
            click.echo(f"Longitude:      {result.components.longitude}")
    if result.lob_confidence_score:
        click.echo(f"Confidence:     {result.lob_confidence_score.score} ({result.lob_confidence_score.level})")
    if result.deliverability_analysis:
        da = result.deliverability_analysis
        click.echo(f"DPV confirm:    {da.dpv_confirmation}")
        click.echo(f"DPV vacant:     {da.dpv_vacant}")
        click.echo(f"DPV active:     {da.dpv_active}")
        click.echo(f"CMRA:           {da.dpv_cmra}")
