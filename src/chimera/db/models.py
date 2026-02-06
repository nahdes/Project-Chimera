"""Minimal DB model placeholders used by unit tests (src path)."""


class Agent:
    agent_id = None
    name = None
    bio = None
    soul_md_path = None
    character_reference_id = None
    wallet_address = None
    status = None
    created_at = None
    updated_at = None
    metadata = None


class Task:
    task_id = None
    agent_id = None
    campaign_id = None
    task_type = None
    priority = None
    status = None
    input_data = None
    dependencies = None
    trace_id = None
