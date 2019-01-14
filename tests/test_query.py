import unittest
from dateparser import parse
from query import Clause, Operator, Metric, MetricFilter, FilterType, Query, and_, or_


class TestQueryMethods(unittest.TestCase):
    def test_match_operator(self):
        expected_output = "MATCH 'home'"

        clause = Clause(Operator.match, "'home'")
        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_contains_operator(self):
        expected_output = "CONTAINS 'home'"

        clause = Clause(Operator.contains, "'home'")
        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_begins_with_operator(self):
        expected_output = "BEGINS-WITH 'home'"

        clause = Clause(Operator.begins_with, "'home'")
        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_ends_with_operator(self):
        expected_output = "ENDS-WITH 'home'"

        clause = Clause(Operator.ends_with, "'home'")
        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_simple_search_clause(self):
        expected_output = "CONTAINS 'home'"

        clause = Clause(Operator.contains, "'home'")
        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_and_composed_search_clause(self):
        expected_output = "CONTAINS 'red' AND CONTAINS 'green'"

        clause = and_(Clause(Operator.contains, "'red'"),
                      Clause(Operator.contains, "'green'"))

        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_and_nested_search_clause(self):
        expected_output = " AND ( CONTAINS ping AND CONTAINS pong )"

        clause = and_((
            Clause(Operator.contains, 'ping'),
            Clause(Operator.contains, 'pong'),))

        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_or_composed_search_clause(self):
        expected_output = "CONTAINS 'red' OR CONTAINS 'green'"

        clause = or_(Clause(Operator.contains, "'red'"),
                     Clause(Operator.contains, "'green'"))

        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_or_nested_search_clause(self):
        expected_output = " OR ( CONTAINS ping OR CONTAINS pong )"

        clause = or_((
            Clause(Operator.contains, 'ping'),
            Clause(Operator.contains, 'pong'),))

        output = clause.compile()

        self.assertEqual(expected_output, output)

    def test_and_or_search_clause(self):
        expected_output = "CONTAINS 'ball' OR ( BEGINS-WITH 'ping' AND BEGINS-WITH 'pong' )"

        and_clause = and_(
            Clause(Operator.begins_with, "'ping'"),
            Clause(Operator.begins_with, "'pong'"))

        mixed_clause = or_(Clause(Operator.contains, "'ball'"),
                           (and_clause, ))

        output = mixed_clause.compile()

        self.assertEqual(expected_output, output)

    def test_global_filter(self):
        expected_output = [
            {'dateRange': '2017-01-01T00:00:00/2018-12-31T23:59:59.999000', 'type': 'dateRange'}]

        metric = Metric('metrics/averagetimespentonsite', 0)

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999"))

        output = query.compile()

        self.assertEqual(expected_output, output['globalFilters'])

    def test_metric(self):
        expected_output = {'metrics': [
            {'columnId': '0', 'id': 'metrics/averagetimespentonsite', 'filters': []}]}

        metric = Metric('metrics/averagetimespentonsite', 0)

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999"))

        output = query.compile()

        self.assertEqual(expected_output, output['metricContainer'])

    def test_metric_filters(self):
        expected_metric_output = {'metrics': [
            {'columnId': '0', 'id': 'metrics/averagetimespentonsite', 'filters': ['c314676362ee1e8c']}]}

        expected_filter_output = [{'dateRange': '2017-01-01T00:00:00.000/2018-12-31T23:59:59.999',
                                   'id': 'c314676362ee1e8c',
                                   'type': 'dateRange'}]

        metric_filter = MetricFilter(FilterType.dateRange,
                                     "2017-01-01T00:00:00.000/2018-12-31T23:59:59.999",
                                     id="c314676362ee1e8c")

        metric = Metric('metrics/averagetimespentonsite',
                        0, filters=[metric_filter])

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999"))

        output = query.compile()

        self.assertEqual(expected_metric_output, output['metricContainer'])
        self.assertEqual(expected_filter_output, output['metricFilters'])

    def test_dimension_breakdown(self):
        expected_metric_output = {'metrics': [{'columnId': '0',
                                               'filters': [],
                                               'id': 'metrics/averagetimespentonsite'}]}

        expected_filter_output = [{'dimension': 'variables/daterangeday',
                                   'itemIds': ['364325780', '1181019'],
                                   'id': None,
                                   'type': 'breakdown'},
                                  {'dimension': 'variables/page',
                                   'itemIds': ['364325780', '1181019'],
                                   'id': None,
                                   'type': 'breakdown'}]

        brakedown_filters = Query.brakedown_filters(
            {'variables/daterangeday': ['364325780', '1181019'],
             'variables/page': ['364325780', '1181019']})

        for f in brakedown_filters:
            for fo in expected_filter_output:
                if f.value[0] == fo['dimension']:
                    fo.update({'id': f.id})
                    expected_metric_output['metrics'][0]['filters'].append(
                        f.id)

        metric = Metric('metrics/averagetimespentonsite',
                        0, filters=brakedown_filters)

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999"))

        output = query.compile()

        self.assertEqual(expected_metric_output, output['metricContainer'])
        self.assertEqual(expected_filter_output, output['metricFilters'])

    def test_segments(self):
        expected_output = [{'dateRange': '2017-01-01T00:00:00/2018-12-31T23:59:59.999000',
                            'type': 'dateRange'},
                           {'segmentId': '53adb46be4b0a2a175bf38c4',
                            'type': 'segment'},
                           {'segmentId': '76ceb46be4b0a2a175bf38de',
                            'type': 'segment'}]

        metric = Metric('metrics/averagetimespentonsite', 0)

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999")) \
            .with_segments(['53adb46be4b0a2a175bf38c4', '76ceb46be4b0a2a175bf38de'])

        output = query.compile()

        self.assertEqual(expected_output, output['globalFilters'])

    def test_pagination(self):
        expected_output = {'page': '1', 'dimensionSort': 'asc'}

        metric = Metric('metrics/averagetimespentonsite', 0)

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999"))

        query.compile()
        query.next()

        output = query.compile()

        self.assertEqual(expected_output, output['settings'])

    def test_limit(self):
        expected_output = {'page': '0', 'dimensionSort': 'asc', 'limit': '100'}

        metric = Metric('metrics/averagetimespentonsite', 0)

        query = Query("cogntestsuite").select("variables/geocity",
                                              [metric]) \
            .for_range(parse("2017-01-01T00:00:00.000"), parse("2018-12-31T23:59:59.999")) \
            .limit(100)

        output = query.compile()

        self.assertEqual(expected_output, output['settings'])
