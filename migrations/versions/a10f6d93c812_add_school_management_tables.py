"""add school management tables

Revision ID: a10f6d93c812
Revises: c88ecfd8df5b
Create Date: 2026-10-04 10:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "a10f6d93c812"
down_revision = "c88ecfd8df5b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("credits", sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column("teacher", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_code"),
    )
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_no", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("gender", sa.String(length=10), nullable=False),
        sa.Column("major", sa.String(length=100), nullable=False),
        sa.Column("class_name", sa.String(length=50), nullable=False),
        sa.Column("enrollment_year", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_no"),
    )
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("semester", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id",
            "course_id",
            "semester",
            name="uq_score_student_course_semester",
        ),
    )
    op.create_index(op.f("ix_scores_course_id"), "scores", ["course_id"], unique=False)
    op.create_index(op.f("ix_scores_student_id"), "scores", ["student_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_scores_student_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_course_id"), table_name="scores")
    op.drop_table("scores")
    op.drop_table("students")
    op.drop_table("courses")
