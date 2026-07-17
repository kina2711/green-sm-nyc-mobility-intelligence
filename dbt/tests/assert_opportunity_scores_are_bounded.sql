select zone_id, opportunity_score
from {{ ref('mart_zone_opportunity') }}
where opportunity_score < 0 or opportunity_score > 100

