# address-verify

Address verification package powered by the [Lob API](https://www.lob.com/). Replaces the legacy Python 2 `verify.py` script with a modern, reusable Python 3 package.

## Features

- **US address verification** (single and bulk) via `lob-python` v5 SDK
- **International address verification** for non-US addresses
- **Geolocation** — latitude/longitude coordinates for verified addresses
- **Deliverability analysis** — DPV confirmation, vacancy, CMRA, and more
- **Confidence scoring** — Lob's confidence score and level
- **CSV batch processing** with configurable column mapping and proper CSV output
- **CLI tool** for quick verification from the terminal
- **Importable package** — use `AddressVerifier` in your own code

## Installation

```bash
cd address-verify
pip install -e .
```

For development (adds pytest, black, mypy):

```bash
pip install -e ".[dev]"
```

## Getting a Lob API Key

1. **Create an account** at [lob.com](https://www.lob.com/) (no credit card required)
2. **Verify your email** — live keys will not work until this is done
3. **Add a payment method** at [Dashboard > Settings > Billing](https://dashboard.lob.com/settings/billing) — required for live key access, even on the free tier
4. **Copy your API key** from [Dashboard > Settings > API Keys](https://dashboard.lob.com/settings/api-keys)

### Test vs Live keys

| Key type | Prefix | Behavior |
|----------|--------|----------|
| **Test** | `test_` | Returns dummy data, no charges, good for development |
| **Live** | `live_` | Real verification against USPS data, counts toward quota |

The free Developer plan includes **300 US verifications/month** at no cost. See [Lob's pricing](https://www.lob.com/pricing/address-verification) for details.

### Test environment

With a test key, the API requires specific magic values to simulate responses. Set `primary_line` to one of: `deliverable`, `deliverable_unnecessary_unit`, `deliverable_incorrect_unit`, `deliverable_missing_unit`, or `undeliverable`, and `zip_code` to `11111`. See [Lob's test environment docs](https://docs.lob.com/#tag/US-Verifications/Testing) for the full list.

## Configuration

Set your API key as an environment variable:

```bash
export LOB_API_KEY="your_lob_api_key"
```

Or pass it directly via `--api-key` on the CLI, or as a parameter when creating a client.

## Usage

### Python API

```python
from address_verify import AddressVerifier, USAddress

with AddressVerifier() as verifier:
    result = verifier.verify_us(
        USAddress(
            primary_line="210 King St",
            city="San Francisco",
            state="CA",
            zip_code="94107",
        )
    )

print(result.deliverability)   # "deliverable"
print(result.primary_line)     # "210 KING ST"
print(result.last_line)        # "SAN FRANCISCO CA 94107-1702"
print(result.is_deliverable)   # True

# Geolocation
print(result.components.latitude)    # 37.7749
print(result.components.longitude)   # -122.3943

# Deliverability analysis
print(result.deliverability_analysis.dpv_confirmation)  # "Y"
print(result.deliverability_analysis.dpv_vacant)        # "N"
print(result.deliverability_analysis.dpv_cmra)          # "N"

# Lob confidence score
print(result.lob_confidence_score.score)  # 100.0
print(result.lob_confidence_score.level)  # "high"
```

### Bulk verification

```python
results = verifier.verify_us_bulk([
    USAddress(primary_line="210 King St", city="San Francisco", state="CA", zip_code="94107"),
    USAddress(primary_line="185 Berry St", city="San Francisco", state="CA", zip_code="94107"),
])
for r in results:
    print(r.deliverability, r.primary_line)
```

### International verification

```python
from address_verify import IntlAddress

result = verifier.verify_international(
    IntlAddress(
        primary_line="370 Water St",
        city="Summerside",
        state="PE",
        postal_code="C1N 1C4",
        country="CA",
    )
)
```

### CSV batch processing

```python
from address_verify import process_csv

counts = process_csv(
    input_path="addresses.csv",
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
print(f"{counts['verified']} verified, {counts['errors']} errors")
```

### CLI

Verify a single address:

```bash
address-verify verify-single "210 King St" --city "San Francisco" --state CA --zip 94107
```

Batch verify a CSV file:

```bash
address-verify verify input.csv --verified verified.csv --errors errors.csv
```

## Response fields

### `VerificationResult`

| Field | Type | Description |
|-------|------|-------------|
| `deliverability` | `str` | `deliverable`, `deliverable_unnecessary_unit`, `deliverable_incorrect_unit`, `deliverable_missing_unit`, or `undeliverable` |
| `is_deliverable` | `bool` | `True` if deliverability starts with `deliverable` |
| `valid_address` | `bool` | Whether the address exists as a real location |
| `primary_line` | `str` | Corrected street address |
| `secondary_line` | `str` | Corrected secondary line |
| `last_line` | `str` | City, state, and ZIP combined |
| `components` | `AddressComponents` | Parsed address components (see below) |
| `deliverability_analysis` | `DeliverabilityAnalysis` | USPS DPV analysis (see below) |
| `lob_confidence_score` | `LobConfidenceScore` | Confidence score and level |
| `raw` | `dict` | Full raw API response |

### `AddressComponents`

| Field | Description |
|-------|-------------|
| `primary_number` | House/building number |
| `street_name` | Street name |
| `street_suffix` | `ST`, `AVE`, `BLVD`, etc. |
| `street_predirection` / `street_postdirection` | `N`, `S`, `E`, `W`, etc. |
| `secondary_designator` / `secondary_number` | `APT`, `STE`, etc. and unit number |
| `city`, `state`, `zip_code`, `zip_code_plus_4` | Standard components |
| `county`, `county_fips` | County name and FIPS code |
| `latitude`, `longitude` | Geolocation coordinates |
| `address_type` | `residential`, `commercial`, or empty |
| `record_type` | USPS record type |
| `carrier_route`, `carrier_route_type` | Mail carrier route info |

### `DeliverabilityAnalysis`

| Field | Description |
|-------|-------------|
| `dpv_confirmation` | DPV match level: `Y` (confirmed), `S` (secondary missing), `D` (primary missing), `N` (not confirmed) |
| `dpv_cmra` | `Y` if Commercial Mail Receiving Agency (e.g. UPS Store) |
| `dpv_vacant` | `Y` if address is vacant |
| `dpv_active` | `Y` if address is active |
| `dpv_inactive_reason` | Reason code if inactive |
| `dpv_footnotes` | List of DPV footnote codes |
| `ews_match` | Early Warning System match |
| `lacs_indicator` / `lacs_return_code` | LACS conversion data |
| `suite_return_code` | SuiteLink return code |

### `LobConfidenceScore`

| Field | Description |
|-------|-------------|
| `score` | Numeric confidence score (0-100) |
| `level` | `high`, `medium`, or `low` |

## Changes from the original `verify.py`

| Original (Python 2)                    | This package (Python 3)                           |
|-----------------------------------------|---------------------------------------------------|
| `lob` v4 (`lob.Verification.create`)   | `lob-python` v5 (`UsVerificationsApi.verifySingle`) |
| Hardcoded API key in source             | Env var `LOB_API_KEY` or constructor param         |
| Hardcoded CSV column indices            | Configurable column mapping dict                   |
| `print` statements (no parens)          | Python 3 `print()`                                |
| `except Exception, e:`                  | `except Exception as e:`                           |
| String concat CSV output                | Proper `csv.writer` (handles commas in values)     |
| Interactive `input()` for output paths  | CLI args or function params                        |
| Single script                           | Importable package with `AddressVerifier` class    |

## Testing

```bash
pip install -e ".[dev]"
pytest
```

Tests use mocked Lob API responses, so no API key is needed to run them.
