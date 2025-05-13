"""Fetch data from API"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'xxxxxxxxxxxx'
down_revision = None  # or the previous revision
branch_labels = None
depends_on = None


def upgrade():
    import subprocess
    import sys
    import os

    print("Running database_fetching.py via Alembic...")

    result = subprocess.run(
        [sys.executable, "database_fetching.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Error running database_fetching.py:\n", result.stderr)
        raise RuntimeError("Data fetch failed during Alembic upgrade")
    else:
        print("Data fetch completed successfully.\n", result.stdout)


def downgrade():
    pass  # No rollback for data fetching
