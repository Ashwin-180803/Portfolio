select
    ride_id,
    lower(trim(rideable_type)) as rideable_type,
    cast(started_at as timestamp) as started_at,
    cast(ended_at as timestamp) as ended_at,
    start_station_name,
    start_station_id,
    end_station_name,
    end_station_id,
    cast(start_lat as double) as start_lat,
    cast(start_lng as double) as start_lng,
    cast(end_lat as double) as end_lat,
    cast(end_lng as double) as end_lng,
    lower(trim(member_casual)) as member_casual,
    cast(duration_sec as bigint) as duration_sec,
    cast(started_at as date) as trip_date
from {{ ref('trips') }}
