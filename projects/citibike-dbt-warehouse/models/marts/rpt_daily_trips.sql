select
    trip_date,
    count(*) as trip_count,
    round(avg(duration_sec), 1) as avg_duration_sec,
    round(100.0 * avg(case when member_casual = 'member' then 1 else 0 end), 1) as member_share_pct
from {{ ref('fct_trips') }}
group by trip_date
