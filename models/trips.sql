with typed as (
    select nullif(trim(ride_id), '') as ride_id,
           try_cast(started_at as timestamp) as started_at,
           try_cast(ended_at as timestamp) as ended_at,
           nullif(trim(start_station_name), '') as station
    from {{ source('ingest', 'raw_trips') }}
)
select *
from typed
where ride_id is not null and ended_at > started_at
qualify row_number() over (
    partition by ride_id order by started_at, ended_at, station
) = 1
