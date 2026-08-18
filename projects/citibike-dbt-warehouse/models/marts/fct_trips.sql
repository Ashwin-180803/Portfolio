select
    ride_id,
    trip_date,
    started_at,
    ended_at,
    duration_sec,
    rideable_type,
    member_casual,
    start_station_id,
    end_station_id
from {{ ref('stg_trips') }}
