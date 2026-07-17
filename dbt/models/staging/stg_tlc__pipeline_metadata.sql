select
    cast(data_mode as varchar) as data_mode,
    cast(loaded_at_utc as timestamp) as loaded_at_utc,
    cast(source_file_count as integer) as source_file_count
from {{ source('tlc_raw', 'pipeline_metadata') }}

