"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Repositories
    op.create_table(
        'repositories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_branch', sa.String(100), server_default='main'),
        sa.Column('stars', sa.Integer(), server_default='0'),
        sa.Column('forks', sa.Integer(), server_default='0'),
        sa.Column('open_issues', sa.Integer(), server_default='0'),
        sa.Column('language', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_repositories_full_name', 'repositories', ['full_name'], unique=True)

    # Analyses
    op.create_table(
        'analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('repository_id', postgresql.UUID(as_uuid=True),
                   sa.ForeignKey('repositories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                   sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('total_commits', sa.Integer(), server_default='0'),
        sa.Column('avg_commit_size', sa.Float(), server_default='0'),
        sa.Column('commits_per_day', sa.Float(), server_default='0'),
        sa.Column('commits_per_month', sa.Float(), server_default='0'),
        sa.Column('code_churn_additions', sa.Integer(), server_default='0'),
        sa.Column('code_churn_deletions', sa.Integer(), server_default='0'),
        sa.Column('avg_time_between_commits_hours', sa.Float(), server_default='0'),
        sa.Column('bus_factor', sa.Integer(), server_default='0'),
        sa.Column('language_distribution', postgresql.JSON(), server_default='{}'),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('readme_quality_score', sa.Float(), nullable=True),
        sa.Column('readme_quality_feedback', sa.Text(), nullable=True),
        sa.Column('detected_tech_stack', postgresql.JSON(), server_default='[]'),
        sa.Column('architecture_analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_analyses_status', 'analyses', ['status'])
    op.create_index('ix_analyses_repo_status', 'analyses', ['repository_id', 'status'])

    # Commits Stats
    op.create_table(
        'commits_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True),
                   sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sha', sa.String(40), nullable=False),
        sa.Column('author_name', sa.String(255), nullable=False),
        sa.Column('author_email', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('additions', sa.Integer(), server_default='0'),
        sa.Column('deletions', sa.Integer(), server_default='0'),
        sa.Column('files_changed', sa.Integer(), server_default='0'),
        sa.Column('committed_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_commits_stats_analysis', 'commits_stats', ['analysis_id'])
    op.create_index('ix_commits_stats_sha', 'commits_stats', ['sha'])

    # Contributors
    op.create_table(
        'contributors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True),
                   sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('total_commits', sa.Integer(), server_default='0'),
        sa.Column('additions', sa.Integer(), server_default='0'),
        sa.Column('deletions', sa.Integer(), server_default='0'),
        sa.Column('first_commit_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_commit_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_contributors_analysis', 'contributors', ['analysis_id'])


def downgrade() -> None:
    op.drop_table('contributors')
    op.drop_table('commits_stats')
    op.drop_table('analyses')
    op.drop_table('repositories')
    op.drop_table('users')
