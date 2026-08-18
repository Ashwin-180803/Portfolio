select
    station_id,
    any_value(station_name) as station_name
from (
    select start_station_id as station_id, start_station_name as station_name
    from {{ ref('stg_trips') }}
    union all
    select end_station_id as station_id, end_station_name as station_name
    from {{ ref('stg_trips') }}
) stations
group by station_id
