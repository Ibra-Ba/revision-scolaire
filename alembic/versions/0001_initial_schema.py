"""Initial PostgreSQL schema for Revi’Pote.

Revision ID: 0001_initial_schema
Revises: None
"""

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TABLE adult_users (\n\tid UUID NOT NULL, \n\tusername VARCHAR(100) NOT NULL, \n\tpassword_hash VARCHAR(255) NOT NULL, \n\tis_active BOOLEAN DEFAULT 'true' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (username)\n)")
    op.execute('CREATE TABLE audit_events (\n\tid UUID NOT NULL, \n\tactor_type VARCHAR(20) NOT NULL, \n\tactor_id UUID, \n\taction VARCHAR(100) NOT NULL, \n\tresource_type VARCHAR(50), \n\tresource_id UUID, \n\tdetails JSONB, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id)\n)')
    op.execute("CREATE TABLE children (\n\tid UUID NOT NULL, \n\tfirst_name VARCHAR(80) NOT NULL, \n\tpassword_hash VARCHAR(255) NOT NULL, \n\tgrade_level VARCHAR(30) NOT NULL, \n\tcurriculum_version VARCHAR(100), \n\tis_active BOOLEAN DEFAULT 'true' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id)\n)")
    op.execute("CREATE TABLE monitoring_alerts (\n\tid UUID NOT NULL, \n\tseverity VARCHAR(20) NOT NULL, \n\tcategory VARCHAR(50) NOT NULL, \n\ttitle VARCHAR(200) NOT NULL, \n\tdetails TEXT, \n\tstatus VARCHAR(20) DEFAULT 'open' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tresolved_at TIMESTAMP WITH TIME ZONE, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_monitoring_alert_severity CHECK (severity IN ('info','warning','critical')), \n\tCONSTRAINT ck_monitoring_alert_status CHECK (status IN ('open','acknowledged','resolved'))\n)")
    op.execute('CREATE TABLE system_metrics (\n\tid UUID NOT NULL, \n\tmetric_name VARCHAR(100) NOT NULL, \n\tmetric_value FLOAT NOT NULL, \n\tunit VARCHAR(30), \n\tmeasured_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tlabels JSONB, \n\tPRIMARY KEY (id)\n)')
    op.execute("CREATE TABLE subjects (\n\tid UUID NOT NULL, \n\tchild_id UUID NOT NULL, \n\tname VARCHAR(100) NOT NULL, \n\tposition INTEGER DEFAULT '1' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_subject_child_name UNIQUE (child_id, name), \n\tCONSTRAINT ck_subject_position_positive CHECK (position > 0), \n\tFOREIGN KEY(child_id) REFERENCES children (id) ON DELETE CASCADE\n)")
    op.execute("CREATE TABLE chapters (\n\tid UUID NOT NULL, \n\tsubject_id UUID NOT NULL, \n\ttitle VARCHAR(200) NOT NULL, \n\tposition INTEGER DEFAULT '1' NOT NULL, \n\tstatus VARCHAR(20) DEFAULT 'in_progress' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_chapter_position_positive CHECK (position > 0), \n\tCONSTRAINT ck_chapter_status CHECK (status IN ('draft','in_progress','completed','archived')), \n\tFOREIGN KEY(subject_id) REFERENCES subjects (id) ON DELETE CASCADE\n)")
    op.execute("CREATE TABLE resources (\n\tid UUID NOT NULL, \n\tresource_type VARCHAR(30) NOT NULL, \n\tscope VARCHAR(20) NOT NULL, \n\tchapter_id UUID, \n\tversion INTEGER DEFAULT '1' NOT NULL, \n\tstatus VARCHAR(20) DEFAULT 'draft' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tcreated_by_type VARCHAR(20), \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_resource_type CHECK (resource_type IN ('revision_sheet','exercise_set')), \n\tCONSTRAINT ck_resource_scope CHECK (scope IN ('chapter','subsections')), \n\tCONSTRAINT ck_resource_status CHECK (status IN ('draft','needs_review','approved','published','rejected')), \n\tCONSTRAINT ck_resource_version_positive CHECK (version > 0), \n\tCONSTRAINT ck_resource_scope_target CHECK ((scope = 'chapter' AND chapter_id IS NOT NULL) OR (scope = 'subsections' AND chapter_id IS NULL)), \n\tFOREIGN KEY(chapter_id) REFERENCES chapters (id) ON DELETE RESTRICT\n)")
    op.execute("CREATE TABLE subsections (\n\tid UUID NOT NULL, \n\tchapter_id UUID NOT NULL, \n\ttitle VARCHAR(200) NOT NULL, \n\tposition INTEGER NOT NULL, \n\tlesson_date DATE, \n\tsource_text TEXT, \n\tstatus VARCHAR(20) DEFAULT 'draft' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_subsection_chapter_position UNIQUE (chapter_id, position), \n\tCONSTRAINT ck_subsection_position_positive CHECK (position > 0), \n\tCONSTRAINT ck_subsection_status CHECK (status IN ('draft','needs_review','approved','published','rejected')), \n\tFOREIGN KEY(chapter_id) REFERENCES chapters (id) ON DELETE CASCADE\n)")
    op.execute('CREATE TABLE exercise_sets (\n\tresource_id UUID NOT NULL, \n\ttitle VARCHAR(200) NOT NULL, \n\tinstructions TEXT NOT NULL, \n\tPRIMARY KEY (resource_id), \n\tFOREIGN KEY(resource_id) REFERENCES resources (id) ON DELETE CASCADE\n)')
    op.execute("CREATE TABLE generation_runs (\n\tid UUID NOT NULL, \n\tsubsection_id UUID, \n\toperation_type VARCHAR(50) NOT NULL, \n\tprovider VARCHAR(80), \n\tmodel_name VARCHAR(120), \n\tstatus VARCHAR(20) DEFAULT 'queued' NOT NULL, \n\tstarted_at TIMESTAMP WITH TIME ZONE, \n\tfinished_at TIMESTAMP WITH TIME ZONE, \n\tduration_ms INTEGER, \n\tinput_tokens INTEGER, \n\toutput_tokens INTEGER, \n\testimated_cost_eur FLOAT, \n\terror_code VARCHAR(100), \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_generation_run_status CHECK (status IN ('queued','running','succeeded','failed','cancelled')), \n\tCONSTRAINT ck_generation_cost_nonnegative CHECK (estimated_cost_eur IS NULL OR estimated_cost_eur >= 0), \n\tCONSTRAINT ck_generation_duration_nonnegative CHECK (duration_ms IS NULL OR duration_ms >= 0), \n\tFOREIGN KEY(subsection_id) REFERENCES subsections (id) ON DELETE SET NULL\n)")
    op.execute("CREATE TABLE resource_reviews (\n\tid UUID NOT NULL, \n\tresource_id UUID NOT NULL, \n\tstatus VARCHAR(30) DEFAULT 'pending' NOT NULL, \n\treason VARCHAR(500), \n\treviewed_by UUID, \n\treviewed_at TIMESTAMP WITH TIME ZONE, \n\treview_comment TEXT, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_resource_review_status CHECK (status IN ('pending','approved','rejected','changes_requested')), \n\tCONSTRAINT ck_resource_review_reason_length CHECK (reason IS NULL OR length(reason) <= 500), \n\tFOREIGN KEY(resource_id) REFERENCES resources (id) ON DELETE CASCADE, \n\tFOREIGN KEY(reviewed_by) REFERENCES adult_users (id) ON DELETE SET NULL\n)")
    op.execute("CREATE TABLE resource_subsections (\n\tresource_id UUID NOT NULL, \n\tsubsection_id UUID NOT NULL, \n\tposition INTEGER DEFAULT '1' NOT NULL, \n\tPRIMARY KEY (resource_id, subsection_id), \n\tCONSTRAINT ck_resource_subsection_position_positive CHECK (position > 0), \n\tFOREIGN KEY(resource_id) REFERENCES resources (id) ON DELETE CASCADE, \n\tFOREIGN KEY(subsection_id) REFERENCES subsections (id) ON DELETE RESTRICT\n)")
    op.execute('CREATE TABLE revision_sheets (\n\tresource_id UUID NOT NULL, \n\ttitle VARCHAR(200) NOT NULL, \n\tcontent TEXT NOT NULL, \n\tPRIMARY KEY (resource_id), \n\tFOREIGN KEY(resource_id) REFERENCES resources (id) ON DELETE CASCADE\n)')
    op.execute("CREATE TABLE exercise_sessions (\n\tid UUID NOT NULL, \n\tchild_id UUID NOT NULL, \n\texercise_set_id UUID NOT NULL, \n\tstarted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tcompleted_at TIMESTAMP WITH TIME ZONE, \n\tstatus VARCHAR(20) DEFAULT 'in_progress' NOT NULL, \n\tscore NUMERIC(8, 2), \n\tmax_score NUMERIC(8, 2), \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_exercise_session_status CHECK (status IN ('in_progress','completed','abandoned')), \n\tCONSTRAINT ck_session_score_nonnegative CHECK (score IS NULL OR score >= 0), \n\tCONSTRAINT ck_session_max_score_nonnegative CHECK (max_score IS NULL OR max_score >= 0), \n\tFOREIGN KEY(child_id) REFERENCES children (id) ON DELETE RESTRICT, \n\tFOREIGN KEY(exercise_set_id) REFERENCES exercise_sets (resource_id) ON DELETE RESTRICT\n)")
    op.execute("CREATE TABLE exercises (\n\tid UUID NOT NULL, \n\texercise_set_id UUID NOT NULL, \n\tposition INTEGER NOT NULL, \n\texercise_type VARCHAR(40) NOT NULL, \n\tstatement TEXT NOT NULL, \n\texpected_answer TEXT NOT NULL, \n\taccepted_answers JSONB, \n\tcorrection TEXT NOT NULL, \n\texplanation TEXT, \n\tpoints INTEGER DEFAULT '1' NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_exercise_set_position UNIQUE (exercise_set_id, position), \n\tCONSTRAINT ck_exercise_position_positive CHECK (position > 0), \n\tCONSTRAINT ck_exercise_points_nonnegative CHECK (points >= 0), \n\tFOREIGN KEY(exercise_set_id) REFERENCES exercise_sets (resource_id) ON DELETE CASCADE\n)")
    op.execute("CREATE TABLE quality_checks (\n\tid UUID NOT NULL, \n\tgeneration_run_id UUID NOT NULL, \n\tcheck_type VARCHAR(80) NOT NULL, \n\tstatus VARCHAR(20) NOT NULL, \n\tscore FLOAT, \n\tdetails JSONB, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_quality_check_status CHECK (status IN ('passed','failed','warning','skipped')), \n\tFOREIGN KEY(generation_run_id) REFERENCES generation_runs (id) ON DELETE CASCADE\n)")
    op.execute("CREATE TABLE exercise_attempts (\n\tid UUID NOT NULL, \n\tsession_id UUID NOT NULL, \n\texercise_id UUID NOT NULL, \n\tattempt_number INTEGER DEFAULT '1' NOT NULL, \n\tanswer TEXT NOT NULL, \n\tis_correct BOOLEAN, \n\tpoints_awarded NUMERIC(8, 2), \n\tanswered_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_attempt_session_exercise_number UNIQUE (session_id, exercise_id, attempt_number), \n\tCONSTRAINT ck_attempt_number_positive CHECK (attempt_number > 0), \n\tCONSTRAINT ck_attempt_points_nonnegative CHECK (points_awarded IS NULL OR points_awarded >= 0), \n\tFOREIGN KEY(session_id) REFERENCES exercise_sessions (id) ON DELETE CASCADE, \n\tFOREIGN KEY(exercise_id) REFERENCES exercises (id) ON DELETE RESTRICT\n)")
    op.execute('CREATE INDEX ix_audit_events_action ON audit_events (action)')
    op.execute('CREATE INDEX ix_audit_events_created_at ON audit_events (created_at)')
    op.execute('CREATE INDEX ix_monitoring_alerts_severity ON monitoring_alerts (severity)')
    op.execute('CREATE INDEX ix_monitoring_alerts_status ON monitoring_alerts (status)')
    op.execute('CREATE INDEX ix_system_metrics_measured_at ON system_metrics (measured_at)')
    op.execute('CREATE INDEX ix_system_metrics_metric_name ON system_metrics (metric_name)')
    op.execute('CREATE INDEX ix_subjects_child_id ON subjects (child_id)')
    op.execute('CREATE INDEX ix_chapters_subject_id ON chapters (subject_id)')
    op.execute('CREATE INDEX ix_resources_chapter_id ON resources (chapter_id)')
    op.execute('CREATE INDEX ix_resources_status ON resources (status)')
    op.execute('CREATE INDEX ix_subsections_chapter_id ON subsections (chapter_id)')
    op.execute('CREATE INDEX ix_generation_runs_status ON generation_runs (status)')
    op.execute('CREATE INDEX ix_generation_runs_subsection_id ON generation_runs (subsection_id)')
    op.execute('CREATE INDEX ix_resource_reviews_resource_id ON resource_reviews (resource_id)')
    op.execute('CREATE INDEX ix_resource_reviews_status ON resource_reviews (status)')
    op.execute('CREATE INDEX ix_exercise_sessions_child_id ON exercise_sessions (child_id)')
    op.execute('CREATE INDEX ix_exercise_sessions_exercise_set_id ON exercise_sessions (exercise_set_id)')
    op.execute('CREATE INDEX ix_exercises_exercise_set_id ON exercises (exercise_set_id)')
    op.execute('CREATE INDEX ix_quality_checks_generation_run_id ON quality_checks (generation_run_id)')
    op.execute('CREATE INDEX ix_exercise_attempts_exercise_id ON exercise_attempts (exercise_id)')
    op.execute('CREATE INDEX ix_exercise_attempts_session_id ON exercise_attempts (session_id)')


def downgrade() -> None:
    op.drop_table("exercise_attempts")
    op.drop_table("quality_checks")
    op.drop_table("exercises")
    op.drop_table("exercise_sessions")
    op.drop_table("revision_sheets")
    op.drop_table("resource_subsections")
    op.drop_table("resource_reviews")
    op.drop_table("generation_runs")
    op.drop_table("exercise_sets")
    op.drop_table("subsections")
    op.drop_table("resources")
    op.drop_table("chapters")
    op.drop_table("subjects")
    op.drop_table("system_metrics")
    op.drop_table("monitoring_alerts")
    op.drop_table("children")
    op.drop_table("audit_events")
    op.drop_table("adult_users")
