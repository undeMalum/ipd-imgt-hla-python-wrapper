import httpx


class MockHTTPXResponse:
    def __init__(self, status_code: int, json_data: dict, text_data: str = ""):
        self.status_code = status_code
        self.json_data = json_data
        self.text = text_data

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code == 502:
            raise httpx.RequestError("Network error")
        elif self.status_code == 504:
            raise httpx.TimeoutException("Timeout")
        elif self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP error: {self.status_code}",
                request=httpx.Request,
                response=httpx.Response,
            )
            
            
if __name__ == "__main__":
    mock = MockHTTPXResponse(200, {}, "Test text")
    print(mock.text)
    