with source as (
    select * from {{ source('tlc_raw', 'yellow_trips') }}
),

typed as (
    select
        cast("VendorID" as integer) as vendor_id,
        cast(tpep_pickup_datetime as timestamp) as pickup_at,
        cast(tpep_dropoff_datetime as timestamp) as dropoff_at,
        cast("PULocationID" as integer) as pickup_zone_id,
        cast("DOLocationID" as integer) as dropoff_zone_id,
        cast(passenger_count as integer) as passenger_count,
        cast(payment_type as integer) as payment_type,
        cast(trip_distance as double) as trip_miles,
        cast(fare_amount as double) as fare_amount,
        cast(tip_amount as double) as tip_amount,
        cast(tolls_amount as double) as tolls_amount,
        cast(total_amount as double) as total_amount,
        cast(source_file as varchar) as source_file,
        cast(source_row_number as bigint) as source_row_number
    from source
),

valid as (
    select
        *,
        datediff('second', pickup_at, dropoff_at) / 60.0 as trip_minutes
    from typed
    where pickup_at is not null
      and dropoff_at > pickup_at
      and pickup_zone_id between 1 and 265
      and dropoff_zone_id between 1 and 265
      and trip_miles between 0 and 200
      and fare_amount >= 0
      and total_amount >= 0
      and pickup_at >= cast('{{ var("analysis_start_date") }}' as timestamp)
      and pickup_at < cast('{{ var("analysis_end_date") }}' as timestamp)
),

identified as (
    select
        md5(concat_ws('|', 'yellow', parse_filename(source_file),
            cast(source_row_number as varchar))) as trip_id,
        'yellow' as service_type,
        'Yellow Taxi' as operator,
        'Taxi' as service_category,
        vendor_id,
        pickup_at,
        dropoff_at,
        pickup_zone_id,
        dropoff_zone_id,
        passenger_count,
        payment_type,
        trip_miles,
        fare_amount,
        tip_amount,
        tolls_amount,
        total_amount,
        cast(null as double) as driver_pay,
        trip_minutes
    from valid
)

select * from identified
