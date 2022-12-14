from redis.exceptions import DataError

ADD_CMD = "TS.ADD"
ALTER_CMD = "TS.ALTER"
CREATERULE_CMD = "TS.CREATERULE"
CREATE_CMD = "TS.CREATE"
DECRBY_CMD = "TS.DECRBY"
DELETERULE_CMD = "TS.DELETERULE"
DEL_CMD = "TS.DEL"
GET_CMD = "TS.GET"
INCRBY_CMD = "TS.INCRBY"
INFO_CMD = "TS.INFO"
MADD_CMD = "TS.MADD"
MGET_CMD = "TS.MGET"
MRANGE_CMD = "TS.MRANGE"
MREVRANGE_CMD = "TS.MREVRANGE"
QUERYINDEX_CMD = "TS.QUERYINDEX"
RANGE_CMD = "TS.RANGE"
REVRANGE_CMD = "TS.REVRANGE"


class TimeSeriesCommands:
    """RedisTimeSeries Commands."""

    async def create(self, key, **kwargs):
        """
        Create a new time-series.

        Args:

        key:
            time-series key
        retention_msecs:
            Maximum age for samples compared to last event time (in milliseconds).
            If None or 0 is passed then  the series is not trimmed at all.
        uncompressed:
            Since RedisTimeSeries v1.2, both timestamps and values are
            compressed by default.
            Adding this flag will keep data in an uncompressed form.
            Compression not only saves
            memory but usually improve performance due to lower number
            of memory accesses.
        labels:
            Set of label-value pairs that represent metadata labels of the key.
        chunk_size:
            Each time-serie uses chunks of memory of fixed size for
            time series samples.
            You can alter the default TSDB chunk size by passing the
            chunk_size argument (in Bytes).
        duplicate_policy:
            Since RedisTimeSeries v1.4 you can specify the duplicate sample policy
            ( Configure what to do on duplicate sample. )
            Can be one of:
            - 'block': an error will occur for any out of order sample.
            - 'first': ignore the new value.
            - 'last': override with latest value.
            - 'min': only override if the value is lower than the existing value.
            - 'max': only override if the value is higher than the existing value.
            When this is not set, the server-wide default will be used.

        For more information: https://oss.redis.com/redistimeseries/commands/#tscreate
        """  # noqa
        retention_msecs = kwargs.get("retention_msecs", None)
        uncompressed = kwargs.get("uncompressed", False)
        labels = kwargs.get("labels", {})
        chunk_size = kwargs.get("chunk_size", None)
        duplicate_policy = kwargs.get("duplicate_policy", None)
        params = [key]
        self._append_retention(params, retention_msecs)
        self._append_uncompressed(params, uncompressed)
        self._append_chunk_size(params, chunk_size)
        self._append_duplicate_policy(params, CREATE_CMD, duplicate_policy)
        self._append_labels(params, labels)

        return await self.execute_command(CREATE_CMD, *params)

    async def alter(self, key, **kwargs):
        """
        Update the retention, labels of an existing key.
        For more information see

        The parameters are the same as TS.CREATE.

        For more information: https://oss.redis.com/redistimeseries/commands/#tsalter
        """  # noqa
        retention_msecs = kwargs.get("retention_msecs", None)
        labels = kwargs.get("labels", {})
        duplicate_policy = kwargs.get("duplicate_policy", None)
        params = [key]
        self._append_retention(params, retention_msecs)
        self._append_duplicate_policy(params, ALTER_CMD, duplicate_policy)
        self._append_labels(params, labels)

        return await self.execute_command(ALTER_CMD, *params)

    async def add(self, key, timestamp, value, **kwargs):
        """
        Append (or create and append) a new sample to the series.
        For more information see

        Args:

        key:
            time-series key
        timestamp:
            Timestamp of the sample. * can be used for automatic timestamp (using the system clock).
        value:
            Numeric data value of the sample
        retention_msecs:
            Maximum age for samples compared to last event time (in milliseconds).
            If None or 0 is passed then  the series is not trimmed at all.
        uncompressed:
            Since RedisTimeSeries v1.2, both timestamps and values are compressed by default.
            Adding this flag will keep data in an uncompressed form. Compression not only saves
            memory but usually improve performance due to lower number of memory accesses.
        labels:
            Set of label-value pairs that represent metadata labels of the key.
        chunk_size:
            Each time-serie uses chunks of memory of fixed size for time series samples.
            You can alter the default TSDB chunk size by passing the chunk_size argument (in Bytes).
        duplicate_policy:
            Since RedisTimeSeries v1.4 you can specify the duplicate sample policy
            (Configure what to do on duplicate sample).
            Can be one of:
            - 'block': an error will occur for any out of order sample.
            - 'first': ignore the new value.
            - 'last': override with latest value.
            - 'min': only override if the value is lower than the existing value.
            - 'max': only override if the value is higher than the existing value.
            When this is not set, the server-wide default will be used.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsadd
        """  # noqa
        retention_msecs = kwargs.get("retention_msecs", None)
        uncompressed = kwargs.get("uncompressed", False)
        labels = kwargs.get("labels", {})
        chunk_size = kwargs.get("chunk_size", None)
        duplicate_policy = kwargs.get("duplicate_policy", None)
        params = [key, timestamp, value]
        self._append_retention(params, retention_msecs)
        self._append_uncompressed(params, uncompressed)
        self._append_chunk_size(params, chunk_size)
        self._append_duplicate_policy(params, ADD_CMD, duplicate_policy)
        self._append_labels(params, labels)

        return await self.execute_command(ADD_CMD, *params)

    async def madd(self, ktv_tuples):
        """
        Append (or create and append) a new `value` to series
        `key` with `timestamp`.
        Expects a list of `tuples` as (`key`,`timestamp`, `value`).
        Return value is an array with timestamps of insertions.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsmadd
        """  # noqa
        params = []
        for ktv in ktv_tuples:
            for item in ktv:
                params.append(item)

        return await self.execute_command(MADD_CMD, *params)

    async def incrby(self, key, value, **kwargs):
        """
        Increment (or create an time-series and increment) the latest
        sample's of a series.
        This command can be used as a counter or gauge that automatically gets
        history as a time series.

        Args:

        key:
            time-series key
        value:
            Numeric data value of the sample
        timestamp:
            Timestamp of the sample. None can be used for automatic timestamp (using the system clock).
        retention_msecs:
            Maximum age for samples compared to last event time (in milliseconds).
            If None or 0 is passed then  the series is not trimmed at all.
        uncompressed:
            Since RedisTimeSeries v1.2, both timestamps and values are compressed by default.
            Adding this flag will keep data in an uncompressed form. Compression not only saves
            memory but usually improve performance due to lower number of memory accesses.
        labels:
            Set of label-value pairs that represent metadata labels of the key.
        chunk_size:
            Each time-series uses chunks of memory of fixed size for time series samples.
            You can alter the default TSDB chunk size by passing the chunk_size argument (in Bytes).

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsincrbytsdecrby
        """  # noqa
        timestamp = kwargs.get("timestamp", None)
        retention_msecs = kwargs.get("retention_msecs", None)
        uncompressed = kwargs.get("uncompressed", False)
        labels = kwargs.get("labels", {})
        chunk_size = kwargs.get("chunk_size", None)
        params = [key, value]
        self._append_timestamp(params, timestamp)
        self._append_retention(params, retention_msecs)
        self._append_uncompressed(params, uncompressed)
        self._append_chunk_size(params, chunk_size)
        self._append_labels(params, labels)

        return await self.execute_command(INCRBY_CMD, *params)

    async def decrby(self, key, value, **kwargs):
        """
        Decrement (or create an time-series and decrement) the
        latest sample's of a series.
        This command can be used as a counter or gauge that
        automatically gets history as a time series.

        Args:

        key:
            time-series key
        value:
            Numeric data value of the sample
        timestamp:
            Timestamp of the sample. None can be used for automatic
            timestamp (using the system clock).
        retention_msecs:
            Maximum age for samples compared to last event time (in milliseconds).
            If None or 0 is passed then  the series is not trimmed at all.
        uncompressed:
            Since RedisTimeSeries v1.2, both timestamps and values are
            compressed by default.
            Adding this flag will keep data in an uncompressed form.
            Compression not only saves
            memory but usually improve performance due to lower number
            of memory accesses.
        labels:
            Set of label-value pairs that represent metadata labels of the key.
        chunk_size:
            Each time-series uses chunks of memory of fixed size for time series samples.
            You can alter the default TSDB chunk size by passing the chunk_size argument (in Bytes).

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsincrbytsdecrby
        """  # noqa
        timestamp = kwargs.get("timestamp", None)
        retention_msecs = kwargs.get("retention_msecs", None)
        uncompressed = kwargs.get("uncompressed", False)
        labels = kwargs.get("labels", {})
        chunk_size = kwargs.get("chunk_size", None)
        params = [key, value]
        self._append_timestamp(params, timestamp)
        self._append_retention(params, retention_msecs)
        self._append_uncompressed(params, uncompressed)
        self._append_chunk_size(params, chunk_size)
        self._append_labels(params, labels)

        return await self.execute_command(DECRBY_CMD, *params)

    async def delete(self, key, from_time, to_time):
        """
        Delete data points for a given timeseries and interval range
        in the form of start and end delete timestamps.
        The given timestamp interval is closed (inclusive), meaning start
        and end data points will also be deleted.
        Return the count for deleted items.
        For more information see

        Args:

        key:
            time-series key.
        from_time:
            Start timestamp for the range deletion.
        to_time:
            End timestamp for the range deletion.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsdel
        """  # noqa
        return await self.execute_command(DEL_CMD, key, from_time, to_time)

    async def createrule(self, source_key, dest_key, aggregation_type, bucket_size_msec):
        """
        Create a compaction rule from values added to `source_key` into `dest_key`.
        Aggregating for `bucket_size_msec` where an `aggregation_type` can be
        [`avg`, `sum`, `min`, `max`, `range`, `count`, `first`, `last`,
        `std.p`, `std.s`, `var.p`, `var.s`]

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tscreaterule
        """  # noqa
        params = [source_key, dest_key]
        self._append_aggregation(params, aggregation_type, bucket_size_msec)

        return await self.execute_command(CREATERULE_CMD, *params)

    async def deleterule(self, source_key, dest_key):
        """
        Delete a compaction rule.
        For more information see

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsdeleterule
        """  # noqa
        return await self.execute_command(DELETERULE_CMD, source_key, dest_key)

    def __range_params(
        self,
        key,
        from_time,
        to_time,
        count,
        aggregation_type,
        bucket_size_msec,
        filter_by_ts,
        filter_by_min_value,
        filter_by_max_value,
        align,
    ):
        """Create TS.RANGE and TS.REVRANGE arguments."""
        params = [key, from_time, to_time]
        self._append_filer_by_ts(params, filter_by_ts)
        self._append_filer_by_value(params, filter_by_min_value, filter_by_max_value)
        self._append_count(params, count)
        self._append_align(params, align)
        self._append_aggregation(params, aggregation_type, bucket_size_msec)

        return params

    async def range(
        self,
        key,
        from_time,
        to_time,
        count=None,
        aggregation_type=None,
        bucket_size_msec=0,
        filter_by_ts=None,
        filter_by_min_value=None,
        filter_by_max_value=None,
        align=None,
    ):
        """
        Query a range in forward direction for a specific time-serie.

        Args:

        key:
            Key name for timeseries.
        from_time:
            Start timestamp for the range query. - can be used to express
            the minimum possible timestamp (0).
        to_time:
            End timestamp for range query, + can be used to express the
            maximum possible timestamp.
        count:
            Optional maximum number of returned results.
        aggregation_type:
            Optional aggregation type. Can be one of
            [`avg`, `sum`, `min`, `max`, `range`, `count`,
            `first`, `last`, `std.p`, `std.s`, `var.p`, `var.s`]
        bucket_size_msec:
            Time bucket for aggregation in milliseconds.
        filter_by_ts:
            List of timestamps to filter the result by specific timestamps.
        filter_by_min_value:
            Filter result by minimum value (must mention also filter
            by_max_value).
        filter_by_max_value:
            Filter result by maximum value (must mention also filter
            by_min_value).
        align:
            Timestamp for alignment control for aggregation.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsrangetsrevrange
        """  # noqa
        params = self.__range_params(
            key,
            from_time,
            to_time,
            count,
            aggregation_type,
            bucket_size_msec,
            filter_by_ts,
            filter_by_min_value,
            filter_by_max_value,
            align,
        )
        return await self.execute_command(RANGE_CMD, *params)

    async def revrange(
        self,
        key,
        from_time,
        to_time,
        count=None,
        aggregation_type=None,
        bucket_size_msec=0,
        filter_by_ts=None,
        filter_by_min_value=None,
        filter_by_max_value=None,
        align=None,
    ):
        """
        Query a range in reverse direction for a specific time-series.

        **Note**: This command is only available since RedisTimeSeries >= v1.4

        Args:

        key:
            Key name for timeseries.
        from_time:
            Start timestamp for the range query. - can be used to express the minimum possible timestamp (0).
        to_time:
            End timestamp for range query, + can be used to express the maximum possible timestamp.
        count:
            Optional maximum number of returned results.
        aggregation_type:
            Optional aggregation type. Can be one of [`avg`, `sum`, `min`, `max`, `range`, `count`,
            `first`, `last`, `std.p`, `std.s`, `var.p`, `var.s`]
        bucket_size_msec:
            Time bucket for aggregation in milliseconds.
        filter_by_ts:
            List of timestamps to filter the result by specific timestamps.
        filter_by_min_value:
            Filter result by minimum value (must mention also filter_by_max_value).
        filter_by_max_value:
            Filter result by maximum value (must mention also filter_by_min_value).
        align:
            Timestamp for alignment control for aggregation.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsrangetsrevrange
        """  # noqa
        params = self.__range_params(
            key,
            from_time,
            to_time,
            count,
            aggregation_type,
            bucket_size_msec,
            filter_by_ts,
            filter_by_min_value,
            filter_by_max_value,
            align,
        )
        return await self.execute_command(REVRANGE_CMD, *params)

    def __mrange_params(
        self,
        aggregation_type,
        bucket_size_msec,
        count,
        filters,
        from_time,
        to_time,
        with_labels,
        filter_by_ts,
        filter_by_min_value,
        filter_by_max_value,
        groupby,
        reduce,
        select_labels,
        align,
    ):
        """Create TS.MRANGE and TS.MREVRANGE arguments."""
        params = [from_time, to_time]
        self._append_filer_by_ts(params, filter_by_ts)
        self._append_filer_by_value(params, filter_by_min_value, filter_by_max_value)
        self._append_count(params, count)
        self._append_align(params, align)
        self._append_aggregation(params, aggregation_type, bucket_size_msec)
        self._append_with_labels(params, with_labels, select_labels)
        params.extend(["FILTER"])
        params += filters
        self._append_groupby_reduce(params, groupby, reduce)
        return params

    async def mrange(
        self,
        from_time,
        to_time,
        filters,
        count=None,
        aggregation_type=None,
        bucket_size_msec=0,
        with_labels=False,
        filter_by_ts=None,
        filter_by_min_value=None,
        filter_by_max_value=None,
        groupby=None,
        reduce=None,
        select_labels=None,
        align=None,
    ):
        """
        Query a range across multiple time-series by filters in forward direction.

        Args:

        from_time:
            Start timestamp for the range query. `-` can be used to
            express the minimum possible timestamp (0).
        to_time:
            End timestamp for range query, `+` can be used to express
            the maximum possible timestamp.
        filters:
            filter to match the time-series labels.
        count:
            Optional maximum number of returned results.
        aggregation_type:
            Optional aggregation type. Can be one of
            [`avg`, `sum`, `min`, `max`, `range`, `count`,
            `first`, `last`, `std.p`, `std.s`, `var.p`, `var.s`]
        bucket_size_msec:
            Time bucket for aggregation in milliseconds.
        with_labels:
            Include in the reply the label-value pairs that represent metadata
            labels of the time-series.
            If this argument is not set, by default, an empty Array will be
            replied on the labels array position.
        filter_by_ts:
            List of timestamps to filter the result by specific timestamps.
        filter_by_min_value:
            Filter result by minimum value (must mention also
            filter_by_max_value).
        filter_by_max_value:
            Filter result by maximum value (must mention also
            filter_by_min_value).
        groupby:
            Grouping by fields the results (must mention also reduce).
        reduce:
            Applying reducer functions on each group. Can be one
            of [`sum`, `min`, `max`].
        select_labels:
            Include in the reply only a subset of the key-value
            pair labels of a series.
        align:
            Timestamp for alignment control for aggregation.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsmrangetsmrevrange
        """  # noqa
        params = self.__mrange_params(
            aggregation_type,
            bucket_size_msec,
            count,
            filters,
            from_time,
            to_time,
            with_labels,
            filter_by_ts,
            filter_by_min_value,
            filter_by_max_value,
            groupby,
            reduce,
            select_labels,
            align,
        )

        return await self.execute_command(MRANGE_CMD, *params)

    async def mrevrange(
        self,
        from_time,
        to_time,
        filters,
        count=None,
        aggregation_type=None,
        bucket_size_msec=0,
        with_labels=False,
        filter_by_ts=None,
        filter_by_min_value=None,
        filter_by_max_value=None,
        groupby=None,
        reduce=None,
        select_labels=None,
        align=None,
    ):
        """
        Query a range across multiple time-series by filters in reverse direction.

        Args:

        from_time:
            Start timestamp for the range query. - can be used to express
            the minimum possible timestamp (0).
        to_time:
            End timestamp for range query, + can be used to express
            the maximum possible timestamp.
        filters:
            Filter to match the time-series labels.
        count:
            Optional maximum number of returned results.
        aggregation_type:
            Optional aggregation type. Can be one of
            [`avg`, `sum`, `min`, `max`, `range`, `count`,
            `first`, `last`, `std.p`, `std.s`, `var.p`, `var.s`]
        bucket_size_msec:
            Time bucket for aggregation in milliseconds.
        with_labels:
            Include in the reply the label-value pairs that represent
            metadata labels
            of the time-series.
            If this argument is not set, by default, an empty Array
            will be replied
            on the labels array position.
        filter_by_ts:
            List of timestamps to filter the result by specific timestamps.
        filter_by_min_value:
            Filter result by minimum value (must mention also filter
            by_max_value).
        filter_by_max_value:
            Filter result by maximum value (must mention also filter
            by_min_value).
        groupby:
            Grouping by fields the results (must mention also reduce).
        reduce:
            Applying reducer functions on each group. Can be one
            of [`sum`, `min`, `max`].
        select_labels:
            Include in the reply only a subset of the key-value pair
            labels of a series.
        align:
            Timestamp for alignment control for aggregation.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsmrangetsmrevrange
        """  # noqa
        params = self.__mrange_params(
            aggregation_type,
            bucket_size_msec,
            count,
            filters,
            from_time,
            to_time,
            with_labels,
            filter_by_ts,
            filter_by_min_value,
            filter_by_max_value,
            groupby,
            reduce,
            select_labels,
            align,
        )

        return await self.execute_command(MREVRANGE_CMD, *params)

    async def get(self, key):
        """# noqa
        Get the last sample of `key`.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsget
        """  # noqa
        return await self.execute_command(GET_CMD, key)

    async def mget(self, filters, with_labels=False):
        """# noqa
        Get the last samples matching the specific `filter`.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsmget
        """  # noqa
        params = []
        self._append_with_labels(params, with_labels)
        params.extend(["FILTER"])
        params += filters
        return await self.execute_command(MGET_CMD, *params)

    async def info(self, key):
        """# noqa
        Get information of `key`.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsinfo
        """  # noqa
        return await self.execute_command(INFO_CMD, key)

    async def queryindex(self, filters):
        """# noqa
        Get all the keys matching the `filter` list.

        For more information: https://oss.redis.com/redistimeseries/master/commands/#tsqueryindex
        """  # noq
        return await self.execute_command(QUERYINDEX_CMD, *filters)

    @staticmethod
    def _append_uncompressed(params, uncompressed):
        """Append UNCOMPRESSED tag to params."""
        if uncompressed:
            params.extend(["UNCOMPRESSED"])

    @staticmethod
    def _append_with_labels(params, with_labels, select_labels=None):
        """Append labels behavior to params."""
        if with_labels and select_labels:
            raise DataError(
                "with_labels and select_labels cannot be provided together."
            )

        if with_labels:
            params.extend(["WITHLABELS"])
        if select_labels:
            params.extend(["SELECTED_LABELS", *select_labels])

    @staticmethod
    def _append_groupby_reduce(params, groupby, reduce):
        """Append GROUPBY REDUCE property to params."""
        if groupby is not None and reduce is not None:
            params.extend(["GROUPBY", groupby, "REDUCE", reduce.upper()])

    @staticmethod
    def _append_retention(params, retention):
        """Append RETENTION property to params."""
        if retention is not None:
            params.extend(["RETENTION", retention])

    @staticmethod
    def _append_labels(params, labels):
        """Append LABELS property to params."""
        if labels:
            params.append("LABELS")
            for k, v in labels.items():
                params.extend([k, v])

    @staticmethod
    def _append_count(params, count):
        """Append COUNT property to params."""
        if count is not None:
            params.extend(["COUNT", count])

    @staticmethod
    def _append_timestamp(params, timestamp):
        """Append TIMESTAMP property to params."""
        if timestamp is not None:
            params.extend(["TIMESTAMP", timestamp])

    @staticmethod
    def _append_align(params, align):
        """Append ALIGN property to params."""
        if align is not None:
            params.extend(["ALIGN", align])

    @staticmethod
    def _append_aggregation(params, aggregation_type, bucket_size_msec):
        """Append AGGREGATION property to params."""
        if aggregation_type is not None:
            params.append("AGGREGATION")
            params.extend([aggregation_type, bucket_size_msec])

    @staticmethod
    def _append_chunk_size(params, chunk_size):
        """Append CHUNK_SIZE property to params."""
        if chunk_size is not None:
            params.extend(["CHUNK_SIZE", chunk_size])

    @staticmethod
    def _append_duplicate_policy(params, command, duplicate_policy):
        """Append DUPLICATE_POLICY property to params on CREATE
        and ON_DUPLICATE on ADD.
        """
        if duplicate_policy is not None:
            if command == "TS.ADD":
                params.extend(["ON_DUPLICATE", duplicate_policy])
            else:
                params.extend(["DUPLICATE_POLICY", duplicate_policy])

    @staticmethod
    def _append_filer_by_ts(params, ts_list):
        """Append FILTER_BY_TS property to params."""
        if ts_list is not None:
            params.extend(["FILTER_BY_TS", *ts_list])

    @staticmethod
    def _append_filer_by_value(params, min_value, max_value):
        """Append FILTER_BY_VALUE property to params."""
        if min_value is not None and max_value is not None:
            params.extend(["FILTER_BY_VALUE", min_value, max_value])
