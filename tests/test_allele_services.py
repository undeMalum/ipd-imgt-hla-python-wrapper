from asyncio import Semaphore

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


@pytest.fixture
def allele_data_pydantic():
    return AllelesNames(
        data=[
            SingleAllele(accession="HLA00220", name="B*27:01"),
            SingleAllele(accession="HLA00221", name="B*27:02"),
        ],
        meta=MetaData(total=2),
    )


@pytest.fixture
def semaphore():
    return Semaphore(1)


@pytest.mark.allele_services
@pytest.mark.asyncio
async def test_fetch_all_allele_from_query(monkeypatch, query, allele_data_pydantic):
    expected_allele_data = {
        "data": [
            {"accession": "HLA00220", "name": "B*27:01"},
            {"accession": "HLA00221", "name": "B*27:02"},
        ],
        "meta": {"next": None, "prev": None, "sort": None, "total": 2},
    }

    async def mock_get(*args, **kwargs):
        return MockHTTPXResponse(200, expected_allele_data)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_all_alleles_from_query(client, query)

    assert result == allele_data_pydantic
    assert result.data == allele_data_pydantic.data
    assert result.meta.total == 2


@pytest.mark.allele_services
@pytest.mark.asyncio
async def test_fetch_all_alleles_pagination(monkeypatch, query, allele_data_pydantic):
    page1_response = {
        "data": [{"accession": "HLA00220", "name": "B*27:01"}],
        "meta": {"next": "?page=2", "prev": None, "sort": None, "total": 2},
    }

    page2_response = {
        "data": [{"accession": "HLA00221", "name": "B*27:02"}],
        "meta": {"next": None, "prev": "?page=1", "sort": None, "total": 2},
    }

    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MockHTTPXResponse(200, page1_response)
        else:
            return MockHTTPXResponse(200, page2_response)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_all_alleles_from_query(client, query)

    assert result.data == allele_data_pydantic.data
    assert len(result.data) == 2
    assert call_count == 2


@pytest.mark.allele_services
@pytest.mark.asyncio
async def test_fetch_single_allele_success(monkeypatch, semaphore):
    mock_single_allele_response = {
        "accession": "HLA00220",
        "name": "B*27:01",
        "status": "Public",
        "sequence": {
            "genomic": "ATCGATCGATCGAATTCCGGTTAACCGGTTAACCGGTT",
            "protein": "MGSHSMRYFFTSVSRPGRGEPR",
            "coding": "ATGGGCTCCCACAGCATGCGG",
        },
    }

    async def mock_get(*args, **kwargs):
        return MockHTTPXResponse(200, mock_single_allele_response)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_single_allele(client, semaphore, "HLA00220")

    assert result is not None
    assert result["accession"] == "HLA00220"
    assert result["name"] == "B*27:01"
    assert result["status"] == "Public"


@pytest.mark.allele_services_errors
@pytest.mark.asyncio
async def test_fetch_single_allele_failure_502(monkeypatch, semaphore):
    async def mock_get(*args, **kwargs):
        return MockHTTPXResponse(502, {})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_single_allele(client, semaphore, "HLA00220")

    assert result is None


@pytest.mark.allele_services_errors
@pytest.mark.asyncio
async def test_fetch_single_allele_failure_504(monkeypatch, semaphore):
    async def mock_get(*args, **kwargs):
        return MockHTTPXResponse(504, {})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_single_allele(client, semaphore, "HLA00220")

    assert result is None


@pytest.mark.allele_services_errors
@pytest.mark.asyncio
async def test_fetch_single_allele_failure_http_status(monkeypatch, semaphore):
    async def mock_get(*args, **kwargs):
        return MockHTTPXResponse(400, {})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with httpx.AsyncClient() as client:
        result = await fetch_single_allele(client, semaphore, "HLA00220")

    assert result is None


@pytest.mark.allele_services
def test_retrieve_accession_numbers(allele_data_pydantic):
    result = retrieve_allele_accession_numbers(allele_data_pydantic)
    
    assert result == ["HLA00220", "HLA00221"]
    assert len(result) == 2
    

@pytest.mark.allele_services
@pytest.mark.asyncio
async def test_download_over_1000_allele(monkeypatch):
    mock_single_allele_responses = [
        {
            "name": "B*27:01",
            "status": "Public",
            "sequence": {"genomic": "ATCGATCG"}
        },
        {
            "name": "B*27:02", 
            "status": "Public",
            "sequence": {"genomic": "GCTAGCTA"}
        },
        None  # Failed request should be handled
    ]
    
    call_count = 0
    
    async def mock_get(*args, **kwargs):
        nonlocal call_count
        if call_count < len(mock_single_allele_responses) - 1:
            response_data = mock_single_allele_responses[call_count]
            call_count += 1
            return MockHTTPXResponse(200, response_data)
        else:
            call_count += 1
            raise MockHTTPXResponse(502, {})
    
    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    
    async with httpx.AsyncClient() as client:
        result = await download_over_1000_alleles(
            client,
            ["HLA00220", "HLA00221", "HLA00222"],
            max_concurrent_requests=2
        )
    
    assert len(result.sequences) == 2
    assert result.sequences[0].allele_name == "B*27:01"
    assert result.sequences[1].allele_name == "B*27:02"
