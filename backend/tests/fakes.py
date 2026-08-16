"""A lightweight fake Supabase client for unit-testing service functions
without a real database. It mimics the postgrest-py fluent query builder
(`.table(x).select(...).eq(...).execute()`) closely enough for our
services: any filter/select/order/limit call returns the same query
object, and `.execute()` pops the next queued canned result for that
table name.
"""


class FakeResult:
    def __init__(self, data=None, count=None):
        self.data = data if data is not None else []
        self.count = count


class _FakeQuery:
    def __init__(self, provider):
        self._provider = provider

    def __getattr__(self, _name):
        def method(*_args, **_kwargs):
            return self

        return method

    def execute(self):
        return self._provider()


class FakeSupabase:
    def __init__(self):
        self._queues: dict[str, list[FakeResult]] = {}
        self.calls: list[tuple[str, str]] = []

    def queue(self, table_name: str, result: FakeResult):
        self._queues.setdefault(table_name, []).append(result)
        return self

    def table(self, name: str):
        self.calls.append(("table", name))
        queue = self._queues.setdefault(name, [])

        def provider():
            if queue:
                return queue.pop(0)
            return FakeResult(data=[])

        return _FakeQuery(provider)
