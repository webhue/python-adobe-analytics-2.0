import sys
from dateutil.parser import parse
from client import Client
from account import Account
from suite import ReportSuite
from query import Query, QueryError, MetricFilter, FilterType


TOKEN = 'eyJ4NXUiOiJpbXNfbmExLWtleS0xLmNlciIsImFsZyI6IlJTMjU2In0.eyJpZCI6IjE1NDUyMjI3NTUxNTRfNmRiY2QyMjQtM2E3NS00NWEyLTlmNmItYjI5OTJhOWViM2I4X3VlMSIsImNsaWVudF9pZCI6IjVhOGRjYzJjZmE3MTQ3MmNiZmE0ZmI1MzY3MWM0NWVkIiwidXNlcl9pZCI6IjFDQzUyRTg0NUMwRTAyMDIwQTQ5NUMyQUBBZG9iZUlEIiwic3RhdGUiOiIiLCJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiYXMiOiJpbXMtbmExIiwiZmciOiJUQTNWQllMRVhMUDM3SEdXMjROUUFBQUFIUT09PT09PSIsInNpZCI6IjE1NDUyMjI3NTQyOTBfNjJmNWE2ZmUtNDVhOS00MzM4LTkyODktM2JhNGM2YTQ3OWEyX3VlMSIsInJ0aWQiOiIxNTQ1MjIyNzU1MTU1XzFiZjJjMmMxLWVhOTctNDc3Ni04ZDVhLTBmMjFhN2EyMThiMV91ZTEiLCJvYyI6InJlbmdhKm5hMXIqMTY3YzY3NDBlNjQqTURTNjJQQVNaUzZBSDcwRjA3RzNXRkY2MjgiLCJydGVhIjoiMTU0NjQzMjM1NTE1NSIsIm1vaSI6IjgwMjI2NGE5IiwiYyI6Ikl0ZTNwNDhheEtyTFMxQnRzN1hzeFE9PSIsImV4cGlyZXNfaW4iOiI4NjQwMDAwMCIsInNjb3BlIjoib3BlbmlkLEFkb2JlSUQscmVhZF9vcmdhbml6YXRpb25zLGFkZGl0aW9uYWxfaW5mby5wcm9qZWN0ZWRQcm9kdWN0Q29udGV4dCxhZGRpdGlvbmFsX2luZm8uam9iX2Z1bmN0aW9uIiwiY3JlYXRlZF9hdCI6IjE1NDUyMjI3NTUxNTQifQ.j9gzqs_W18uw8btO2UuL1xE5S_7KN9X5mBsfAa0zix47VdDin_d38RjDe4XKGwRlhNa4XILWvu7h714kNuSrxFqxkjDopkQZJQOtsGVoRS1XLT5x9d_kCT6jkJeab61sk0kUxAdU8eY4yZzRQ-5MyUtP0S3RW_cDurUqBCszW-oppZbEmfZRuE2uoGbVXX4XkIpZgCqn0ZpMyYgObBUQCiJAi6_cAdnwS0tTL7rjCzpMIROD8ADQ2ClwosT0WRC8Oj2N-ENnoRE1pjzZ8-cDobrfvW3UMaqb9ltMYIDy9mGvk0Y3ZdDBA8KkDg1_FwguwrO8Tg9ZsRdYO5_EdahmNQ'
API_KEY = '5a8dcc2cfa71472cbfa4fb53671c45ed'
COMPANY_ID = 'exchanc7'


def list_reports_suites():
    client = Client(API_KEY, COMPANY_ID, TOKEN)
    account = Account(client)

    # import ipdb; ipdb.set_trace()

    result = account.list_reports_suites()

    print result


def fill_report_suite():
    client = Client(API_KEY, COMPANY_ID, TOKEN)
    suite = ReportSuite("cogntestsuite", "cogntestsuite", client)
    suite.fill()


def query_report_suite():
    query = Query("cogntestsuite").select("variables/daterangeday",
                                          ["metrics/averagetimespentonsite"]) \
        .filter(metrics_filter=[MetricFilter("metrics/averagetimespentonsite",
                                             FilterType.dateRange,
                                             "2017-01-01T00:00:00.000/2018-12-31T23:59:59.999")]) \
        .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999"))

    output = query.compile()

    client = Client(API_KEY, COMPANY_ID, TOKEN)
    suite = ReportSuite("cogntestsuite", "cogntestsuite", client)
    suite.fill()


fn_map = {'0': list_reports_suites,
          '1': fill_report_suite,
          '2': query_report_suite}

if __name__ == "__main__":
    args = sys.argv[1:]

    args = ['2']

    if len(args) == 0:
        raise ValueError("invocation argument expected")

    key = args[0]
    if not key in fn_map:
        raise KeyError("argument is not mapped to a function")

    fn_map[key]()
