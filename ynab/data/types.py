from pydantic import BaseModel


class YnabException(Exception):
    pass


class Response(BaseModel):
    status_code: int
    data: dict
    source: str

    @classmethod
    def from_requests_response(cls, response):
        return cls(
            status_code=response.status_code, data=response.json(), source="ynab"
        )

    @property
    def is_success(self):
        return 200 <= self.status_code < 300
