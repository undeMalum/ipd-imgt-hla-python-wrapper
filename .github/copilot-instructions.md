# Copilot Instructions for ipd-imgt-hla-python-wrapper

## Project Overview

This project is a Python package and FastAPI application for retrieving and serving data from the IPD-IMGT/HLA database. It provides REST endpoints to fetch allele metadata and sequence data, supporting both small and large result sets.

## Architecture & Major Components

- **API Layer**: [main.py](../main.py) (project root) defines FastAPI endpoints.
    - `/` — fetches allele metadata (names, accessions) for a query.
    - `/downloads` — fetches allele sequences for a query.
    - `/downloads/large` — fetches sequences for a large set of alleles (handles pagination and large result sets).
- **Service Layer**: [src/ipd_imgt_hla_python_wrapper/services/allele_services.py](../src/ipd_imgt_hla_python_wrapper/services/allele_services.py)
    - Handles all HTTP requests to the external IPD-IMGT/HLA API.
    - Implements async functions for paginated fetches, downloads, and large-batch sequence retrieval.
    - Uses Pydantic models for data structure consistency.
- **Data Models**: [src/ipd_imgt_hla_python_wrapper/services/allele_settings.py](../src/ipd_imgt_hla_python_wrapper/services/allele_settings.py)
    - Defines Pydantic models for allele metadata, sequences, and response schemas.
    - Enum `SequenceTypes` for specifying sequence type (protein, genomic, coding).
- **Configuration**: [src/ipd_imgt_hla_python_wrapper/urls.py](../src/ipd_imgt_hla_python_wrapper/urls.py)
    - Centralizes all external API URLs.

## Developer Workflows

- **Run the API server**:
    ```sh
    uvicorn main:app --reload
    ```
    (Runs FastAPI app defined in [main.py](../main.py).)
- **Build/install dependencies**:
    ```sh
    pip install -r requirements.txt
    # or, if using pyproject.toml:
    pip install .
    ```
- **Interactive experiments**: Use notebooks/scripts in [sundbox/](../sundbox/) for data exploration and prototyping (uses `marimo`, `polars`, etc.).

## Project-Specific Patterns & Conventions

- **Async HTTP**: All external API calls use `httpx.AsyncClient` for concurrency.
- **Pagination**: When fetching all alleles, the service layer handles `meta["next"]` for paginated API responses.
- **Data Transformation**: Sequence downloads parse FASTA-like text into structured JSON using string operations and Pydantic models.
- **Type Safety**: All API/service responses use Pydantic models for validation and serialization.
- **Query Convention**: Query strings for the IPD-IMGT/HLA API use the format `startsWith(name, "B*27")` etc.

## Integration Points & Dependencies

- **External API**: All data comes from `https://www.ebi.ac.uk/cgi-bin/ipd/api/allele`.
- **Key dependencies**: `fastapi`, `httpx`, `pydantic`, `polars`, `marimo` (for data exploration).
- **No explicit test suite**: (Add tests in `tests/` or similar if needed.)

## Example: Adding a New Endpoint

1. Define a new async function in [src/ipd_imgt_hla_python_wrapper/services/allele_services.py](../src/ipd_imgt_hla_python_wrapper/services/allele_services.py).
2. Add a corresponding route in [main.py](../main.py), calling the service function and returning the result.

## File/Directory Reference

- [main.py](../main.py) — FastAPI entrypoint and route definitions.
- [src/ipd_imgt_hla_python_wrapper/services/allele_services.py](../src/ipd_imgt_hla_python_wrapper/services/allele_services.py) — Service logic for all external API calls.
- [src/ipd_imgt_hla_python_wrapper/services/allele_settings.py](../src/ipd_imgt_hla_python_wrapper/services/allele_settings.py) — Data models and enums.
- [src/ipd_imgt_hla_python_wrapper/urls.py](../src/ipd_imgt_hla_python_wrapper/urls.py) — External API URLs.
- [sundbox/](../sundbox/) — Prototyping and data exploration scripts.

---