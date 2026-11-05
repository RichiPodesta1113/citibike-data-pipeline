select * from {{ ref('trips') }} where ended_at <= started_at
