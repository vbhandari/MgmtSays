"""Initial migration with all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('ticker', sa.String(20), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_companies_name', 'companies', ['name'])
    op.create_index('ix_companies_ticker', 'companies', ['ticker'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(2000), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('publish_date', sa.Date, nullable=True),
        sa.Column('fiscal_period', sa.String(20), nullable=True),
        sa.Column('fiscal_year', sa.Integer, nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('processing_status', sa.String(20), server_default='pending'),
        sa.Column('chunk_count', sa.Integer, server_default='0'),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_documents_company_id', 'documents', ['company_id'])
    op.create_index('ix_documents_document_type', 'documents', ['document_type'])
    op.create_index('ix_documents_publish_date', 'documents', ['publish_date'])
    op.create_index('ix_documents_processing_status', 'documents', ['processing_status'])

    # Create insights table
    op.create_table(
        'insights',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insight_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('importance_score', sa.Float, server_default='0.5'),
        sa.Column('confidence_score', sa.Float, server_default='0.5'),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_insights_company_id', 'insights', ['company_id'])
    op.create_index('ix_insights_document_id', 'insights', ['document_id'])
    op.create_index('ix_insights_insight_type', 'insights', ['insight_type'])
    op.create_index('ix_insights_category', 'insights', ['category'])

    # Create initiatives table
    op.create_table(
        'initiatives',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('status', sa.String(30), server_default='active'),
        sa.Column('timeline', sa.String(200), nullable=True),
        sa.Column('metrics', postgresql.JSONB, nullable=True),
        sa.Column('first_mentioned_date', sa.Date, nullable=True),
        sa.Column('last_mentioned_date', sa.Date, nullable=True),
        sa.Column('mention_count', sa.Integer, server_default='1'),
        sa.Column('confidence_score', sa.Float, server_default='0.5'),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_initiatives_company_id', 'initiatives', ['company_id'])
    op.create_index('ix_initiatives_category', 'initiatives', ['category'])
    op.create_index('ix_initiatives_status', 'initiatives', ['status'])
    op.create_index('ix_initiatives_first_mentioned', 'initiatives', ['first_mentioned_date'])

    # Create evidence table
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('initiative_id', sa.String(36), sa.ForeignKey('initiatives.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_id', sa.String(100), nullable=True),
        sa.Column('quote', sa.Text, nullable=False),
        sa.Column('context', sa.Text, nullable=True),
        sa.Column('page_number', sa.Integer, nullable=True),
        sa.Column('speaker', sa.String(200), nullable=True),
        sa.Column('speaker_role', sa.String(100), nullable=True),
        sa.Column('relevance_score', sa.Float, server_default='0.5'),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_evidence_initiative_id', 'evidence', ['initiative_id'])
    op.create_index('ix_evidence_document_id', 'evidence', ['document_id'])


def downgrade() -> None:
    op.drop_table('evidence')
    op.drop_table('initiatives')
    op.drop_table('insights')
    op.drop_table('documents')
    op.drop_table('companies')
