from datetime import datetime, timezone

import sqlalchemy as sa


def pg_timestampz():
    return sa.Column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
