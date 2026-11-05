select count(*) as rides from {{ ref('trips') }} having count(*) = 0
