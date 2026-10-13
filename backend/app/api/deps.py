from fastapi import Query


class PageParams:
    def __init__(self, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
        self.offset, self.limit = offset, limit
