
import utils.backfill as backfill


details_tables = ["zones", "laps", "streams"]

backfill.details_backfill(
    table_name=details_tables[2]
)
