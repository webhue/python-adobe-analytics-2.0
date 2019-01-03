from .client import Request
from .suite import ReportSuite


class Account(object):
    def __init__(self, client):
        self._client = client

    def list_reports_suites(self):
        request = Request(Request.Method.GET,
                          '/collections/suites?expansion=name')
        response = self._client.execute(request)

        content = response['content']
        reports_suites = [ReportSuite(
            rs['rsid'], rs['name'], self._client) for rs in content]

        return reports_suites
