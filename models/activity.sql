select 'day' as metric, cast(started_at::date as varchar) as label, count(*) as rides
from {{ ref('trips') }} group by 2
union all
select 'hour', strftime(started_at, '%H:00'), count(*)
from {{ ref('trips') }} group by 2
union all
select 'station', station, count(*)
from {{ ref('trips') }} where station is not null group by 2
