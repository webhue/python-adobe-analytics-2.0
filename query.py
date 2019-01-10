
from datetime import datetime
from enum import Enum
from os import urandom


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
        self._metrics = None
        self._start_date = None
        self._end_date = None
        self._metrics_filter = None
        self._dimension_filter = None
        self._sort_mode = None
        self._limit = None
        self._page = 0
        self._translation = None

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
        self._page += 1
        self._translation['settings'].update({'page': str(self._page)})

    def brakedown(self, dimensions):
        """Breaks down the report based on the specified dimensions"""
        pass

    def compile(self):
        if not self._dimension_id:
            raise QueryError("dimension_id must be specified")

        self._translation = {'rsid': self._suite_id,
                             'globalFilters': [{'type': 'dateRange',
                                                'dateRange': self._compose_date_range()}],
                             'metricContainer': {'metrics': self._compose_metric_container()},
                             'metricFilters': self._compose_metrics_filters(),
                             'dimension': self._dimension_id,
                             'settings': self._compose_settings()}

        if self._dimension_filter:
            self._translation.update(
                {'search': self._dimension_filter.compile()})

        return self._translation

    def _compose_date_range(self):
        return "{}/{}".format(self._start_date.isoformat(), self._end_date.isoformat())

    def _compose_metrics_filters(self):
        filters = []

        for filter in self._metrics_filter:
            output = filter.compile()
            filters.append(output)
        return filters

    def _compose_metric_container(self):
        if not self._metrics:
            raise QueryError("metrics must be specified")

        index = 0
        metrics = []

        for metric in self._metrics:
            metrics.append({'columnId': str(index) if not metric.column_id else str(metric.column_id),
                            'id': metric.id,
                            'filters': [f.id for f in metric.filters]})
            index += 1

        return metrics

    def _compose_settings(self):
        settings = {}

        if self._limit:
            settings.update({'limit': str(self._limit)})

        settings.update({'page': str(self._page)})

        if not self._sort_mode:
            self._sort_mode = Query.Sort.asc

        settings.update(
            {'dimensionSort': Query._sort_map[self._sort_mode]})

        return settings


class Metric(object):
    def __init__(self, id, column_id=None, filters=None):
        self._id = id
        # If column_id is not specified it is going to be generated.
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

    def __init__(self, filter_type, value):
        self._id = urandom(8).encode('hex')
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
        return {'id': self._id,
                'type': self._compose_type(),
                self._compose_type_key(): self._value}


class DimensionFilter(object):
    def __init__(self, *args, **kwargs):
        self._include_search_total = True
        self._items_ids = kwargs.get('items_ids')
        self._excluded_items_ids = kwargs.get('exclude_items_ids')
        self._criteria = args  # criteria

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

        if self._criteria:
            dimension_filter_map['clause'] = self._compile_search()

        return dimension_filter_map

    def _compile_search(self):
        if len(self._criteria) == 1 and isinstance(self._criteria[0], Clause):
            return self._criteria[0].compile()

        translation = []
        for criterion in self._criteria:
            if isinstance(criterion, Conjunction):
                translation.append(criterion.compile())

            if isinstance(criterion, tuple):
                output = [" ( "]
                for item in criterion:
                    output.append(item.compile())
                output.append(" )")
                translation.append(''.join(output))

        return ''.join(translation)


Operator = Enum('Operator', 'match contains begins_with ends_with')


class Conjunction(object):
    def __init__(self, conjunction, *clauses):
        self._conjunction = conjunction
        self._clauses = []

        for item in clauses:
            self._clauses.append(Clause._to_clause(item, conjunction))

    def compile(self):
        translation = []
        fmt = " {} {}"

        for index, clause in enumerate(self._clauses):
            if isinstance(clause, tuple):
                output = []
                for index, item in enumerate(clause):
                    if not index:
                        output.append(
                            " {} ( {}".format(Clause._conjunction_map[item._conjunction], item.compile()))
                        continue

                    output.append(fmt.format(
                        Clause._conjunction_map[item._conjunction], item.compile()))
                output.append(" )")
                translation.append(''.join(output))
                continue

            if not index:
                translation.append("{}".format(clause.compile()))
                continue

            output = fmt.format(
                Clause._conjunction_map[clause._conjunction], clause.compile())

            translation.append(output)

        return ''.join(translation)


class and_(Conjunction):
    def __init__(self, *clauses):
        super(and_, self).__init__(Clause.Conjunction.and_, *clauses)


class or_(Conjunction):
    def __init__(self, *clauses):
        super(or_, self).__init__(Clause.Conjunction.or_, *clauses)


class Clause(object):
    Conjunction = Enum('Conjunction', 'and_ or_ not_')
    _operator_map = {Operator.match: 'MATCH',
                     Operator.contains: 'CONTAINS',
                     Operator.begins_with: 'BEGINGS-WITH',
                     Operator.ends_with: 'ENDS-WITH'}

    _conjunction_map = {Conjunction.and_: 'AND',
                        Conjunction.or_: 'OR',
                        Conjunction.not_: 'NOT',
                        None: ''}

    def __init__(self, operator, operand):
        self._operator = operator
        self._operand = operand
        self._conjunction = None
        self._clauses = []

    def compile(self):
        return "{} {}".format(
            Clause._operator_map[self._operator], self._operand)

    @staticmethod
    def _to_clause(obj, conjunction):
        if isinstance(obj, tuple):
            clauses = []
            for clause in obj:
                if isinstance(clause, tuple):
                    tpl = Clause._to_clause(clause, conjunction)
                    clauses += list(tpl)
                    continue

                clause._conjunction = conjunction
                clauses.append(clause)

            return tuple(clauses)

        obj._conjunction = conjunction
        return obj
