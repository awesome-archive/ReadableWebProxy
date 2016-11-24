"""Adding header column

Revision ID: ddcb08ebb9e1
Revises: 1b4006c4f120
Create Date: 2016-11-24 07:26:09.796411

"""

# revision identifiers, used by Alembic.
revision = 'ddcb08ebb9e1'
down_revision = '1b4006c4f120'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable
import sqlalchemy_utils

# Patch in knowledge of the citext type, so it reflects properly.
from sqlalchemy.dialects.postgresql.base import ischema_names
import citext
import queue
import datetime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
ischema_names['citext'] = citext.CIText

from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nu_resolved_outbound', sa.Column('resolved_title', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('nu_resolved_outbound', 'resolved_title')
    ### end Alembic commands ###
