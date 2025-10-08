from sqlalchemy import and_
from sqlalchemy.orm import Query


class SoftDeleteQuery(Query):
    """Default: exclude rows where deleted_at IS NOT NULL. Opt-in with `.with_deleted()`."""

    _with_deleted = False

    def with_deleted(self):
        q = self.clone()
        q._with_deleted = True
        return q

    def only_deleted(self):
        return self.with_deleted().filter(self._deleted_filter(only=True))

    def _deleted_filter(self, only: bool = False):
        filters = []
        for entity in self._entities:
            mapper = getattr(entity, "mapper", None)
            cls = mapper.class_
            column = getattr(cls, "deleted_at", None)
            if column is not None:
                filters.append(column.isnot(None) if only else column.is_(None))
        if not filters:
            return None
        return and_(*filters)

    def __iter__(self):
        if not getattr(self, "_with_deleted", False):
            deleted_filter = self._deleted_filter()
            if deleted_filter is not None:
                self = self.filter(deleted_filter)
        return super().__iter__()
