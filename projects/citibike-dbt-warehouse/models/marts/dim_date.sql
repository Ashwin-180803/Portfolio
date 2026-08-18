select distinct
    trip_date,
    extract(year from trip_date) as year,
    extract(month from trip_date) as month,
    extract(day from trip_date) as day,
    extract(dow from trip_date) as day_of_week
from {{ ref('stg_trips') }}
