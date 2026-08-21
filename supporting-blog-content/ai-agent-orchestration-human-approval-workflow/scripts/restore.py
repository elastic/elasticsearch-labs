#!/usr/bin/env python3
"""
Restore the tutorial's Agent Builder skills, agents, and workflow.

Usage:
    python3 -m pip install requests python-dotenv
    python3 scripts/restore.py

Required environment variables, either exported or placed in .env:

    KIBANA_ENDPOINT=https://your-project.kb.region.gcp.elastic.cloud
    ES_API_KEY=<your-api-key>

Optional:

    KIBANA_SPACE_ID=your-space-id

When KIBANA_SPACE_ID is omitted, the default Kibana space is used.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT_DIR / "backup"
WORKFLOW_FILE = ROOT_DIR / "workflow" / "failure-store-remediation.yaml"

load_dotenv(ROOT_DIR / ".env")

KIBANA_ENDPOINT = os.getenv("KIBANA_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("ES_API_KEY", "") or os.getenv("ELASTIC_API_KEY", "")
SPACE_ID = os.getenv("KIBANA_SPACE_ID", "").strip()

if not KIBANA_ENDPOINT or not API_KEY:
    print("Error: KIBANA_ENDPOINT and ES_API_KEY must be set.")
    print("")
    print("Export them or create a .env file in the repository root:")
    print("")
    print("KIBANA_ENDPOINT=https://your-project.kb.region.gcp.elastic.cloud")
    print("ES_API_KEY=<your-api-key>")
    sys.exit(1)

HEADERS = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json",
    "kbn-xsrf": "true",
}

AGENT_TOP_LEVEL_FIELDS = {
    "name",
    "description",
    "labels",
    "avatar_color",
    "avatar_symbol",
    "visibility",
}

AGENT_CONFIGURATION_FIELDS = {
    "instructions",
    "tools",
    "skill_ids",
    "enable_elastic_capabilities",
    "workflow_ids",
    "plugin_ids",
    "connector_ids",
}

SKILL_FIELDS = {
    "name",
    "description",
    "content",
    "referenced_content",
    "tool_ids",
}


def api_url(path: str) -> str:
    """Build a Kibana API URL, optionally scoped to a space."""
    normalized_path = "/" + path.lstrip("/")

    if SPACE_ID:
        encoded_space = quote(SPACE_ID, safe="")
        return f"{KIBANA_ENDPOINT}/s/{encoded_space}{normalized_path}"

    return f"{KIBANA_ENDPOINT}{normalized_path}"


def request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> requests.Response:
    """Run a Kibana API request and include useful error details."""
    response = requests.request(
        method=method,
        url=api_url(path),
        headers=HEADERS,
        params=params,
        json=json_body,
        timeout=60,
    )

    if not response.ok:
        body = response.text.strip()
        if len(body) > 2000:
            body = body[:2000] + "..."

        raise RuntimeError(
            f"{method} {path} failed with HTTP {response.status_code}\n{body}"
        )

    return response


def request_agent(
    method: str,
    path: str,
    payload: dict[str, Any],
) -> requests.Response:
    """
    Create or update an agent.

    Some Agent Builder deployments do not yet accept the Technical Preview
    'visibility' field. Retry without it when the target API rejects it.
    """
    try:
        return request(method, path, json_body=payload)
    except RuntimeError as error:
        message = str(error)

        visibility_not_supported = (
            "visibility" in payload
            and "visibility" in message
            and "unexpected" in message
        )

        if not visibility_not_supported:
            raise

        compatible_payload = dict(payload)
        compatible_payload.pop("visibility", None)

        print("  note: target API does not accept 'visibility'; " "retrying without it")

        return request(method, path, json_body=compatible_payload)


def read_json_file(path: Path, collection_name: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    collection = data.get(collection_name)

    if not isinstance(collection, list):
        raise ValueError(f"{path} must contain a JSON array named '{collection_name}'.")

    return collection


def extract_results(
    data: Any,
    possible_keys: tuple[str, ...],
) -> list[dict[str, Any]]:
    """Handle list and paginated API response shapes."""
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in possible_keys:
        value = data.get(key)
        if isinstance(value, list):
            return value

    return []


def build_skill_payload(
    skill: dict[str, Any],
    *,
    include_id: bool,
) -> dict[str, Any]:
    payload = {key: value for key, value in skill.items() if key in SKILL_FIELDS}

    payload.setdefault("referenced_content", [])
    payload.setdefault("tool_ids", [])

    if include_id:
        skill_id = skill.get("id")
        if not isinstance(skill_id, str) or not skill_id:
            raise ValueError("Every skill must contain a non-empty 'id'.")
        payload["id"] = skill_id

    return payload


def build_agent_payload(
    agent: dict[str, Any],
    *,
    include_id: bool,
) -> dict[str, Any]:
    payload = {
        key: value for key, value in agent.items() if key in AGENT_TOP_LEVEL_FIELDS
    }

    # Older/read APIs can return access_control rather than visibility.
    if "visibility" not in payload:
        access_mode = (
            agent.get("access_control", {})
            if isinstance(agent.get("access_control"), dict)
            else {}
        ).get("access_mode")

        if access_mode in {"public", "shared", "private"}:
            payload["visibility"] = access_mode

    configuration = agent.get("configuration")
    if not isinstance(configuration, dict):
        raise ValueError(
            f"Agent {agent.get('id', '<unknown>')} has no valid configuration."
        )

    normalized_configuration = {
        key: value
        for key, value in configuration.items()
        if key in AGENT_CONFIGURATION_FIELDS
    }

    # The API requires a tools array, even when it contains no tool IDs.
    normalized_configuration.setdefault(
        "tools",
        [{"tool_ids": []}],
    )
    normalized_configuration.setdefault("skill_ids", [])
    normalized_configuration.setdefault("workflow_ids", [])
    normalized_configuration.setdefault("plugin_ids", [])

    payload["configuration"] = normalized_configuration

    if include_id:
        agent_id = agent.get("id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("Every agent must contain a non-empty 'id'.")
        payload["id"] = agent_id

    return payload


def restore_skills() -> None:
    skills = read_json_file(
        BACKUP_DIR / "save_skills.json",
        "skills",
    )

    response = request("GET", "/api/agent_builder/skills")
    existing_skills = extract_results(
        response.json(),
        ("results", "skills"),
    )
    existing_ids = {
        skill["id"] for skill in existing_skills if isinstance(skill.get("id"), str)
    }

    created = 0
    updated = 0

    for skill in skills:
        skill_id = skill.get("id")
        if not isinstance(skill_id, str) or not skill_id:
            raise ValueError("A skill export is missing its ID.")

        if skill_id in existing_ids:
            payload = build_skill_payload(skill, include_id=False)
            request(
                "PUT",
                f"/api/agent_builder/skills/{quote(skill_id, safe='')}",
                json_body=payload,
            )
            print(f"  updated  {skill_id}")
            updated += 1
        else:
            payload = build_skill_payload(skill, include_id=True)
            request(
                "POST",
                "/api/agent_builder/skills",
                json_body=payload,
            )
            print(f"  created  {skill_id}")
            created += 1

    print(f"  Skills: created={created}, updated={updated}")


def restore_agents() -> None:
    agents = read_json_file(
        BACKUP_DIR / "save_agents.json",
        "agents",
    )

    response = request("GET", "/api/agent_builder/agents")
    existing_agents = extract_results(
        response.json(),
        ("results", "agents"),
    )
    existing_ids = {
        agent["id"] for agent in existing_agents if isinstance(agent.get("id"), str)
    }

    created = 0
    updated = 0

    for agent in agents:
        agent_id = agent.get("id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("An agent export is missing its ID.")

        if agent_id in existing_ids:
            payload = build_agent_payload(agent, include_id=False)
            request_agent(
                "PUT",
                f"/api/agent_builder/agents/{quote(agent_id, safe='')}",
                payload,
            )
            print(f"  updated  {agent_id}")
            updated += 1
        else:
            payload = build_agent_payload(agent, include_id=True)
            request_agent(
                "POST",
                "/api/agent_builder/agents",
                payload,
            )
            print(f"  created  {agent_id}")
            created += 1

    print(f"  Agents: created={created}, updated={updated}")


def restore_workflow() -> None:
    if not WORKFLOW_FILE.exists():
        raise FileNotFoundError(f"Required workflow YAML not found: {WORKFLOW_FILE}")

    workflow_yaml = WORKFLOW_FILE.read_text(encoding="utf-8")

    # Reuse an existing workflow ID when the workflow was created manually.
    response = request(
        "GET",
        "/api/workflows",
        params={"page": 1, "size": 100},
    )
    existing_workflows = extract_results(
        response.json(),
        ("results", "workflows"),
    )

    workflow_name = "failure_store_remediation"
    workflow_id = "failure-store-remediation"

    for workflow in existing_workflows:
        if workflow.get("name") == workflow_name:
            existing_id = workflow.get("id")
            if isinstance(existing_id, str) and existing_id:
                workflow_id = existing_id
            break

    payload = {
        "workflows": [
            {
                "id": workflow_id,
                "yaml": workflow_yaml,
            }
        ]
    }

    response = request(
        "POST",
        "/api/workflows",
        params={"overwrite": "true"},
        json_body=payload,
    )

    result = response.json()
    failures = result.get("failures", [])

    if failures:
        raise RuntimeError(
            "Workflow import returned failures:\n" + json.dumps(failures, indent=2)
        )

    print(f"  imported {workflow_name} ({workflow_id})")


def main() -> None:
    destination = KIBANA_ENDPOINT
    if SPACE_ID:
        destination += f" [space: {SPACE_ID}]"

    print(f"Restoring to: {destination}")
    print("")

    try:
        print("=" * 60)
        print("Restoring skills")
        print("=" * 60)
        restore_skills()

        print("")
        print("=" * 60)
        print("Restoring agents")
        print("=" * 60)
        restore_agents()

        print("")
        print("=" * 60)
        print("Restoring workflow")
        print("=" * 60)
        restore_workflow()

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError,
        requests.RequestException,
    ) as error:
        print("")
        print(f"Restore failed: {error}", file=sys.stderr)
        sys.exit(1)

    print("")
    print("=" * 60)
    print("Restore completed successfully")
    print("=" * 60)
    print("")
    print("Next steps:")
    print("  1. Review the restored skills and agents in Agent Builder.")
    print("  2. Review and enable the workflow.")
    print("  3. Create the alerting rule described in README.md.")


if __name__ == "__main__":
    main()
