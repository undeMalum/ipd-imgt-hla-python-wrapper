import pytest
import httpx
from fastapi import HTTPException

from ipd_imgt_hla_python_wrapper.services.allele_services import (
    fetch_all_alleles_from_query,
    fetch_single_allele,
    download_alleles,
    download_over_1000_alleles,
    retrieve_allele_accession_numbers,
)
from ipd_imgt_hla_python_wrapper.services.allele_settings import (
    AllelesNames,
    MetaData,
    SingleAllele,
)
from mocks import MockHTTPXResponse


@pytest.mark.asyncio
async def test_fetch_all_allele_from_query(monkeypatch, query):
    expected_allele_data = {
        "data": [
            {"accession": "HLA00220", "name": "B*27:01"},
            {"accession": "HLA00221", "name": "B*27:02:01:01"},
        ],
        "meta": {"next": None, "prev": None, "sort": None, "total": 2},
    }

    expected_data_as_pydantic = AllelesNames(
        data=[
            SingleAllele(accession="HLA00220", name="B*27:01"),
            SingleAllele(accession="HLA00221", name="B*27:02:01:01"),
        ],
        meta=MetaData(total=2),
    )

    async def mock_get(*args, **kwargs):
        return MockHTTPXResponse(200, expected_allele_data)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_all_alleles_from_query(client, query)

    assert result == expected_data_as_pydantic
    assert result.data == expected_data_as_pydantic.data
    assert result.meta == expected_data_as_pydantic.meta
