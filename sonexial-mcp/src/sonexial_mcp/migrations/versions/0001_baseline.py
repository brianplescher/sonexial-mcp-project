"""baseline schema

Revision ID: 0001_baseline
Revises: 
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('authors',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('slug', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('pen_names', sa.JSON(), nullable=True),
    sa.Column('website', sa.String(length=512), nullable=True),
    sa.Column('bio_short', sa.Text(), nullable=True),
    sa.Column('bio_long', sa.Text(), nullable=True),
    sa.Column('genres', sa.JSON(), nullable=True),
    sa.Column('tropes', sa.JSON(), nullable=True),
    sa.Column('themes', sa.JSON(), nullable=True),
    sa.Column('audience', sa.JSON(), nullable=True),
    sa.Column('verification_status', sa.String(length=32), nullable=False),
    sa.Column('source_urls', sa.JSON(), nullable=True),
    sa.Column('last_verified_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.create_index('idx_author_genres', ['genres'], unique=False, postgresql_using='gin')
        batch_op.create_index(batch_op.f('ix_authors_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_authors_slug'), ['slug'], unique=True)
        batch_op.create_index(batch_op.f('ix_authors_verification_status'), ['verification_status'], unique=False)

    op.create_table('author_relationships',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('source_author_id', sa.String(length=64), nullable=False),
    sa.Column('target_author_id', sa.String(length=64), nullable=False),
    sa.Column('relationship_type', sa.String(length=64), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['source_author_id'], ['authors.id'], ),
    sa.ForeignKeyConstraint(['target_author_id'], ['authors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('author_relationships', schema=None) as batch_op:
        batch_op.create_index('idx_relationship_pair', ['source_author_id', 'target_author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_author_relationships_relationship_type'), ['relationship_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_author_relationships_source_author_id'), ['source_author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_author_relationships_target_author_id'), ['target_author_id'], unique=False)

    op.create_table('books',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('author_id', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('subtitle', sa.String(length=512), nullable=True),
    sa.Column('series_name', sa.String(length=256), nullable=True),
    sa.Column('series_position', sa.Integer(), nullable=True),
    sa.Column('publication_date', sa.String(length=32), nullable=True),
    sa.Column('asin', sa.String(length=32), nullable=True),
    sa.Column('isbn', sa.String(length=32), nullable=True),
    sa.Column('blurb', sa.Text(), nullable=True),
    sa.Column('genres', sa.JSON(), nullable=True),
    sa.Column('tropes', sa.JSON(), nullable=True),
    sa.Column('themes', sa.JSON(), nullable=True),
    sa.Column('audience', sa.JSON(), nullable=True),
    sa.Column('spice', sa.Integer(), nullable=True),
    sa.Column('cover_url', sa.String(length=512), nullable=True),
    sa.Column('book_status', sa.String(length=32), nullable=False),
    sa.Column('word_count_estimate', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.CheckConstraint('spice IS NULL OR (spice >= 0 AND spice <= 5)', name='ck_book_spice_range'),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_books_author_id'), ['author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_books_title'), ['title'], unique=False)

    op.create_table('lore_entries',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('author_id', sa.String(length=64), nullable=False),
    sa.Column('book_id', sa.String(length=64), nullable=True),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('category', sa.String(length=64), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('canonical', sa.Boolean(), nullable=False),
    sa.Column('spoiler_level', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('lore_entries', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_lore_entries_author_id'), ['author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_lore_entries_category'), ['category'], unique=False)
        batch_op.create_index(batch_op.f('ix_lore_entries_title'), ['title'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('lore_entries', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_lore_entries_title'))
        batch_op.drop_index(batch_op.f('ix_lore_entries_category'))
        batch_op.drop_index(batch_op.f('ix_lore_entries_author_id'))

    op.drop_table('lore_entries')
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_books_title'))
        batch_op.drop_index(batch_op.f('ix_books_author_id'))

    op.drop_table('books')
    with op.batch_alter_table('author_relationships', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_author_relationships_target_author_id'))
        batch_op.drop_index(batch_op.f('ix_author_relationships_source_author_id'))
        batch_op.drop_index(batch_op.f('ix_author_relationships_relationship_type'))
        batch_op.drop_index('idx_relationship_pair')

    op.drop_table('author_relationships')
    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_authors_verification_status'))
        batch_op.drop_index(batch_op.f('ix_authors_slug'))
        batch_op.drop_index(batch_op.f('ix_authors_name'))
        batch_op.drop_index('idx_author_genres', postgresql_using='gin')

    op.drop_table('authors')
