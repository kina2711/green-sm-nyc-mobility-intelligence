with source as (
    select * from {{ source('tlc_raw', 'taxi_zones') }}
)

select
    cast("LocationID" as integer) as zone_id,
    cast("Borough" as varchar) as borough,
    cast("Zone" as varchar) as zone_name,
    cast(service_zone as varchar) as service_zone,
    cast("LocationID" as integer) in (1, 132, 138) as is_airport_zone
from source
where cast("LocationID" as integer) between 1 and 265

