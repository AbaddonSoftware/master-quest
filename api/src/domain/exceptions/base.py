from __future__ import annotations


class AppError(Exception):
    status_code: int = 400
    title: str = "Bad Request"
    detail: str = "Bad request."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail

    def to_problem(self, instance: str | None = None) -> dict:
        return {
            "type": f"https://httpstatuses.com/{self.status_code}",
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
            "instance": instance or "",
        }
