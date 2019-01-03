from sqlalchemy import and_
from datetime import datetime
from enum import Enum


class QueryError(Exception):
    def __init__(self, message):
        super(QueryError, self).__init__(message)


class Query(object):
    Sort = Enum('Sort', 'asc desc')
    _sort_map = {Sort.asc: 'asc', Sort.desc: 'desc'}

    def __init__(self, suite_id):
        if not isinstance(suite_id, basestring):
            raise QueryError("suite_id type should be string")

        self._suite_id = suite_id

        self._dimension_id = None
        self._metrics_ids = None
        self._suite_id = None
        self._start_date = None
        self._end_date = None
        self._metrics_filter = None
        self._dimension_filter = None
        self._sort_mode = None
        self._limit = None

    def select(self, dimension_id, metrics):
        if not isinstance(dimension_id, basestring):
            raise QueryError("dimension_id type should be string")

        if not isinstance(metrics, list):
            raise QueryError("metrics type should be list")

        if not len(metrics):
            raise QueryError(
                "metrics_ids is expected to have atleast one element")

        self._dimension_id = dimension_id
        self._metrics = metrics

        return self

    def for_range(self, start_date, end_date):
        """Composes report dates range.

        Args:
            start_date (datetime)
            end_date (datetime)
        """

        if not isinstance(start_date, datetime):
            raise QueryError("start_date type should be datetime")

        if not isinstance(end_date, datetime):
            raise QueryError("end_date type should be datetime")

        if start_date > end_date:
            raise QueryError("start_date can't be greater than end_date")

        self._start_date = start_date
        self._end_date = end_date

        return self

    def filter(self, metrics_filter=None, dimension_filter=None):
        """Composes report quering conditions.

        Args:
            metrics_filter (:obj:`list`, optional)
            filters (:obj:`list`, optional)
        """

        if metrics_filter and not isinstance(metrics_filter, list):
            raise QueryError("metrics_filter type should be list")

        self._metrics_filter = metrics_filter

        self._dimension_filter = dimension_filter

        return self

    def sort(self, sort_mode):
        if not isinstance(sort_mode, Query.Sort):
            raise QueryError("sort_mode type should be Sort")

        self._sort_mode = sort_mode

        return self

    def limit(self, size):
        if not isinstance(size, int):
            raise QueryError("limit size type should be int")

        if size < 0:
            raise QueryError("limit size can't have a negative value")

        self._limit = size

        return self

    def next(self):
        """Handles report pagination"""
        pass

    def brakedown(self, dimensions):
        """Breaks down the report based on the specified dimensions"""
        pass

    def compile(self):
        if not self._dimension_id:
            raise QueryError("dimension_id must be specified")

        if not self._metrics_ids:
            raise QueryError("metrics_ids must be specified")

        # TODO: Make sure that MetricFIlter allows you to relate it to multiple metrics IDs at once.

        transaltion = {'rsid': self._suite_id,
                       'globalFilters': [{'type': 'dateRange',
                                          'dateRange': self._compose_date_range()}],
                       'metricContainer': {'metrics': self._compose_metric_container()},
                       'metricFilters': self._compose_metrics_filters(),
                       'dimension': self._dimension_id,
                       'settings': self._compose_settings()}

        return transaltion

    def _compose_date_range(self):
        return "{}/{}".format(self._start_date.isoformat(), self._end_date.isoformat())

    def _compose_metrics_filters(self):
        index = 0
        filters = []

        # This has to be refactored as metrics_ids is a l;ist
        for filter in self._metrics_filter:
            output = filter.compile()
            output.update({'id': str(index)})
            filters.append(output)
            index += 1

        return filters

    def _compose_metric_container(self):
        index = 0
        metrics = []

        for metric in self._metrics:
            metrics.append({'columnId': str(index),
                            'id': metric.id,
                            'filters': [f.id for f in metric.filters]})
            index += 1

        return metrics

    def _compose_settings(self):
        settings = {}

        if self._limit:
            settings.update({'limit': str(self._limit)})

        if self._sort_mode:
            settings.update(
                {'dimensionSort': Query._sort_map[self._sort_mode]})

        return settings


class Metric(object):
    def __init__(self, id, column_id, filters=None):
        self._id = id
        self._column_id = column_id

        if filters and not isinstance(filters, list):
            raise QueryError("filters type should be list")

        self._filters = filters

    @property
    def id(self):
        return self._id

    @property
    def column_id(self):
        return self._column_id

    @property
    def filters(self):
        return self._filters

    def compile(self):
        pass


FilterType = Enum('FilterType', 'dateRange segment')


class MetricFilter(object):
    _type_map = {FilterType.dateRange: 'dateRange',
                 FilterType.segment: 'segmentId'}

    def __init__(self, id, filter_type, value):
        self._id = id
        self._filter_type = filter_type
        self._value = value

    @property
    def id(self):
        return self._id

    @property
    def filter_type(self):
        return self._filter_type

    @property
    def value(self):
        return self._value

    def _compose_type(self):
        return MetricFilter._type_map[self._filter_type]

    def _compose_type_key(self):
        return MetricFilter._type_map[self._filter_type]

    def compile(self):
        return {'id': None,
                'type': self._compose_type(),
                self._compose_type_key(): self._value}


class DimensionFilter(object):
    def __init__(self, items_ids=None, exclude_items_ids=None, clause=None):
        self._include_search_total = True
        self._items_ids = items_ids
        self._excluded_items_ids = exclude_items_ids
        self._clause = clause

    @property
    def items_ids(self):
        return self._items_ids

    @property
    def exluce_items_ids(self):
        return self._excluded_items_ids

    @property
    def include_search_total(self):
        return self._include_search_total

    def compile(self):
        dimension_filter_map = {
            'includeSearchTotal': self._include_search_total}

        if self._items_ids:
            if len(self._items_ids) == 1:
                dimension_filter_map['itemId'] = self._items_ids[0]
            else:
                dimension_filter_map['itemIds'] = self._items_ids

        if self._excluded_items_ids:
            dimension_filter_map['excludeItemIds'] = self._excluded_items_ids

        if self._clause:
            dimension_filter_map['clause'] = self._clause.compile()

        return dimension_filter_map


Operator = Enum('Operator', 'match contains begins_with ends_with')

# According to documentation search clauses apply only to dimensions.


class Clause(object):
    Conjunction = Enum('Conjunction', 'and_ or_ not_')
    _operator_map = {Operator.match: 'MATCH',
                     Operator.contains: 'CONTAINS',
                     Operator.begins_with: 'BEGINGS-WIH',
                     Operator.ends_with: 'ENDS-WITH'}

    _conjunction_map = {Conjunction.and_: 'AND',
                        Conjunction.or_: 'OR',
                        Conjunction.not_: 'NOT'}

    def __init__(self, operator, operand):
        self._operator = operator
        self._operand = operand
        self._conjunction = None
        self._clauses = []

    def and_(self, clause):
        clause._conjunction = Clause.Conjunction.and_
        self._clauses.append(clause)

        return self

    def or_(self, clause):
        clause._conjunction = Clause.Conjunction.or_
        self._clauses.append(clause)

        return self

    def not_(self, clause):
        clause._conjunction = Clause.Conjunction.not_
        self._clauses.append(clause)

        return self

    def compile(self):
        if not self._clauses:
            return "{} {}".format(Clause._operator_map[self._operator], self._operand)

        translation = []
        for clause in self._clauses:
            output = "({} {})".format(clause._conjunction, clause.compile())
            translation.append(output)

        return ''.join(translation)
