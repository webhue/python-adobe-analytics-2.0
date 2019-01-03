from concurrent.futures import ThreadPoolExecutor, as_completed

from client import Request
from dynamic_object import DynamicObject, to_dynamic_object


class ReportSuite(object):
    """A ReportSuite represents a template for a concrete Report retrieved 
    from Adobe Analytics API.

    """

    def __init__(self, suite_id, name, client):
        self._suite_id = suite_id
        self._name = name
        self._client = client

        self._metrics = None
        self._dimensions = None
        self._segments = None

    @property
    def name(self):
        return self._name

    @property
    def suite_id(self):
        return self._suite_id

    @property
    def metrics(self):
        if not self._metrics:
            self._metrics = self._get_metrics()

        return self._metrics

    @property
    def dimensions(self):
        if not self._dimensions:
            self._dimensions = self._get_dimensions()

        return self._dimensions

    @property
    def segments(self):
        if not self._segments:
            self._segments = self._get_segments()

        return self._segments

    def fill(self):
        pool = ThreadPoolExecutor(max_workers=3)
        futures = [pool.submit(self._get_metrics), pool.submit(
            self._get_dimensions), pool.submit(self._get_segments)]
        results = [result for result in as_completed(futures)]

        import ipdb
        ipdb.set_trace()

        return results

    def validate(self, dimensions=None, segments=None, metrics=None):
        pass

    def _get_metrics(self):
        print "metrics got called"
        request = Request(Request.Method.GET,
                          '/metrics?rsid={}'.format(self._suite_id))
        response = self._client.execute(request)

        assert isinstance(response, list)
        metrics = [to_dynamic_object(metric) for metric in response]

        return metrics

    def _get_dimensions(self):
        print "dimensions got called"
        request = Request(Request.Method.GET,
                          '/dimensions?rsid={}'.format(self._suite_id))
        response = self._client.execute(request)

        assert isinstance(response, list)
        dimensions = [to_dynamic_object(
            dimension) for dimension in response]

        return dimensions

    def _get_segments(self):
        print "segments got called"
        request = Request(Request.Method.GET,
                          '/segments?rsid={}'.format(self._suite_id))
        response = self._client.execute(request)
        content = response['content']

        assert isinstance(content, list)
        segments = [to_dynamic_object(segment) for segment in content]

        return segments

    def __str__(self):
        return """
                \033[1m{:<10s}\033[0m{:>20s}
                \033[1m{:<10s}\033[0m{:>20s}
                \033[1m{:<10s}\033[0m{:>20s}
                \033[1m{:<10s}\033[0m{:>20s}
                """.format('Id:', self._suite_id, 'Name:', self._name, 'Metrics:', self._metrics,
                           'Dimensions:', self._dimensions)
