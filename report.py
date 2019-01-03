class Report(object):
    def __init__(self, suite_id, query, client):
        self._suite_id = suite_id
        self._query = query
        self._client = client

    @property
    def suite_id(self):
        return self._suite_id

    @property
    def query(self):
        return self._query

    @property
    def dimensions(self):
        return []

    @property
    def metrics(self):
        return []


class Value(object):
    def __init__(self, value_id, value, raw_value):
        self._value_id = value_id
        self._value = value
        self._raw_value = raw_value

    @property
    def value_id(self):
        return self._value_id

    @property
    def value(self):
        return self._value

    @property
    def raw_value(self):
        return self._raw_value


class Metric(Value):
    def __init__(self, metric_id, value, raw_value):
        super(Metric, self).__init__(metric_id, value, raw_value)


class Dimension(object):
    def __init__(self, dimension_id, value, raw_value):
        super(Dimension, self).__init__(dimension_id, value, raw_value)
