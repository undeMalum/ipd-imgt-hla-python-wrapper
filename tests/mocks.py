import httpx


class MockHTTPXResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code == 502:
            raise httpx.RequestError()
        elif self.status_code == 504:
            raise httpx.TimeoutException()
        elif self.status_code >= 400:
            raise httpx.HTTPStatusError()
