with source as (
    select * from {{ source('tlc_raw', 'fhvhv_trips') }}
),

typed as (
    select
        cast(hvfhs_license_num as varchar) as hvfhs_license_num,
        cast(pickup_datetime as timestamp) as pickup_at,
        cast(dropoff_datetime as timestamp) as dropoff_at,
        cast("PULocationID" as integer) as pickup_zone_id,
        cast("DOLocationID" as integer) as dropoff_zone_id,
        cast(trip_miles as double) as trip_miles,
        cast(base_passenger_fare as double) as fare_amount,
        cast(tolls as double) as tolls_amount,
        cast(sales_tax as double) as sales_tax,
        cast(congestion_surcharge as double) as congestion_surcharge,
        cast(airport_fee as double) as airport_fee,
        cast(tips as double) as tip_amount,
        cast(driver_pay as double) as driver_pay,
        cast(source_file as varchar) as source_file,
        cast(source_row_number as bigint) as source_row_number
    from source
),

valid as (
    select
        *,
        datediff('second', pickup_at, dropoff_at) / 60.0 as trip_minutes,
        coalesce(fare_amount, 0)
            + coalesce(tolls_amount, 0)
            + coalesce(sales_tax, 0)
            + coalesce(congestion_surcharge, 0)
            + coalesce(airport_fee, 0)
            + coalesce(tip_amount, 0) as total_amount
    from typed
    where pickup_at is not null
      and dropoff_at > pickup_at
      and pickup_zone_id between 1 and 265
      and dropoff_zone_id between 1 and 265
      and trip_miles between 0 and 200
      and fare_amount >= 0
      and pickup_at >= cast('{{ var("analysis_start_date") }}' as timestamp)
      and pickup_at < cast('{{ var("analysis_end_date") }}' as timestamp)
),

identified as (
    select
        md5(concat_ws('|', 'fhvhv', parse_filename(source_file),
            cast(source_row_number as varchar))) as trip_id,
        'fhvhv' as service_type,
        case hvfhs_license_num
            when 'HV0002' then 'Juno'
            when 'HV0003' then 'Uber'
            when 'HV0004' then 'Via'
            when 'HV0005' then 'Lyft'
            else 'Other HVFHS'
        end as operator,
        'HVFHS' as service_category,
        cast(null as integer) as vendor_id,
        pickup_at,
        dropoff_at,
        pickup_zone_id,
        dropoff_zone_id,
        cast(null as integer) as passenger_count,
        cast(null as integer) as payment_type,
        trip_miles,
        fare_amount,
        tip_amount,
        tolls_amount,
        total_amount,
        driver_pay,
        trip_minutes
    from valid
)

select * from identified
