from sqlalchemy import and_
from sqlalchemy.orm import Query


class SoftDeleteQuery(Query):
    """Default: exclude rows where deleted_at IS NOT NULL. Opt-in with `.with_deleted()`."""

    _with_deleted = False

    def with_deleted(self):
        q = self.enable_assertions(False)
        q._with_deleted = True
        return q

    def only_deleted(self):
        return self.with_deleted().filter(self._deleted_filter(only=True))

    def _deleted_filter(self, only: bool = False):
        crits = []
        for ent in self._entities:
            mapper = getattr(ent, "mapper", None)
            if not mapper:
                continue
            cls = mapper.class_
            col = getattr(cls, "deleted_at", None)
            if col is not None:
                crits.append(col.isnot(None) if only else col.is_(None))
        if not crits:
            return None
        return and_(*crits)

    def __iter__(self):
        if not getattr(self, "_with_deleted", False):
            crit = self._deleted_filter()
            if crit is not None:
                self = self.filter(crit)
        return super().__iter__()
