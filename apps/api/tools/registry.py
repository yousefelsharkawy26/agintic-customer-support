from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class ToolSpec:
    name: str
    version: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    permissions: list[str] = field(default_factory=lambda: ["all"])
    owner: str = "system"
    health_status: bool = True
    timeout_ms: int = 30000
    retry_count: int = 2
    rate_limit_per_minute: int = 60
    visibility: str = "public"
    deprecation_date: datetime | None = None
    changelog: list[str] = field(default_factory=list)


TOOL_REGISTRY: dict[str, ToolSpec] = {}
TOOL_VERSIONS: dict[str, list[ToolSpec]] = {}


def register_tool(spec: ToolSpec) -> None:
    TOOL_REGISTRY[spec.name] = spec
    if spec.name not in TOOL_VERSIONS:
        TOOL_VERSIONS[spec.name] = []
    TOOL_VERSIONS[spec.name].append(spec)
    logger.info("tool_registered", name=spec.name, version=spec.version)


def get_tool(name: str) -> ToolSpec | None:
    return TOOL_REGISTRY.get(name)


def list_tools(visibility: str = "public") -> list[ToolSpec]:
    return [t for t in TOOL_REGISTRY.values() if t.visibility == visibility and t.health_status]


def get_tool_versions(name: str) -> list[ToolSpec]:
    return TOOL_VERSIONS.get(name, [])


def rollback_tool(name: str, version: str) -> ToolSpec | None:
    versions = TOOL_VERSIONS.get(name, [])
    for v in versions:
        if v.version == version:
            TOOL_REGISTRY[name] = v
            logger.info("tool_rolled_back", name=name, version=version)
            return v
    return None
