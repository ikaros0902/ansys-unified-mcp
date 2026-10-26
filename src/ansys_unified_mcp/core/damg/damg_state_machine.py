"""Directed Acyclic Multiphysics Graph (DAMG) State Machine.

Provides session-isolated causal state tracking, prerequisite verification,
and breadth-first dirty invalidation cascades across 9 physics disciplines.
All comments follow ASD-STE100 and ASCII safety standards.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Set, Union

import yaml

logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    """Lifecycle status for a node in the causal graph."""

    UNSATISFIED = "UNSATISFIED"
    SATISFIED = "SATISFIED"
    DIRTY = "DIRTY"


@dataclass(frozen=True)
class NodeDefinition:
    """Static metadata and dependency definition for a physics node."""

    id: str
    discipline: str
    level: int
    name: str
    description: str
    prerequisites: tuple[str, ...]
    invalidates: tuple[str, ...]
    suggested_recovery: str


@dataclass
class NodeState:
    """Runtime state of a node in a specific project or session."""

    id: str
    status: NodeStatus = NodeStatus.UNSATISFIED
    satisfied_at: Optional[float] = None
    invalidated_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DAMGStateMachine:
    """Session-level causal state manager for multiphysics workflows.

    Enforces Directed Acyclic Multiphysics Graph (DAMG) ordering, verifies
    prerequisites before tool execution, and cascades dirty invalidation
    along downstream dependency edges.
    """

    _registry: Dict[str, DAMGStateMachine] = {}

    def __init__(
        self,
        session_id: str = "default",
        manifest_path: Optional[Union[str, Path]] = None,
        rules_dict: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the state machine for a specific session."""
        self.session_id = str(session_id)
        self.nodes: Dict[str, NodeDefinition] = {}
        self.node_states: Dict[str, NodeState] = {}
        self.prerequisites_graph: Dict[str, Set[str]] = {}
        self.dependents_graph: Dict[str, Set[str]] = {}
        self.explicit_invalidates_graph: Dict[str, Set[str]] = {}
        self.couplings: Dict[str, Dict[str, Any]] = {}

        if rules_dict is not None:
            self._load_from_dict(rules_dict)
        else:
            manifest_file = self._resolve_manifest_path(manifest_path)
            self._load_from_manifest(manifest_file)

        self._validate_dag()

    @classmethod
    def get_instance(
        cls,
        session_id: str = "default",
        manifest_path: Optional[Union[str, Path]] = None,
    ) -> DAMGStateMachine:
        """Retrieve or create a session-isolated state machine instance."""
        sess_key = str(session_id)
        if sess_key not in cls._registry:
            cls._registry[sess_key] = cls(
                session_id=sess_key, manifest_path=manifest_path
            )
        return cls._registry[sess_key]

    @classmethod
    def clear_all_instances(cls) -> None:
        """Clear all registered session state machine instances."""
        cls._registry.clear()

    @classmethod
    def remove_instance(cls, session_id: str) -> None:
        """Remove a single session instance from registry."""
        sess_key = str(session_id)
        cls._registry.pop(sess_key, None)

    def _resolve_manifest_path(
        self, manifest_path: Optional[Union[str, Path]]
    ) -> Path:
        """Resolve absolute path to damg_rules.yaml."""
        if manifest_path:
            return Path(manifest_path).resolve()

        env_path = os.environ.get("ANSYS_MCP_DAMG_MANIFEST")
        if env_path:
            return Path(env_path).resolve()

        # DAMG state machine is located at:
        # src/ansys_unified_mcp/core/damg/damg_state_machine.py
        # Project root is parents[4]
        project_root = Path(__file__).resolve().parents[4]
        candidate = project_root / "manifests" / "damg_rules.yaml"
        if candidate.exists():
            return candidate

        # Fallback search in working directory
        cwd_candidate = Path.cwd() / "manifests" / "damg_rules.yaml"
        if cwd_candidate.exists():
            return cwd_candidate

        return candidate

    def _load_from_manifest(self, manifest_file: Path) -> None:
        """Parse damg_rules.yaml and populate node graph structures."""
        if not manifest_file.exists():
            raise FileNotFoundError(
                f"DAMG rules manifest not found at: {manifest_file}"
            )

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self._load_from_dict(data)

    def _load_from_dict(self, data: Dict[str, Any]) -> None:
        """Populate graph structures from dictionary specification."""
        self.nodes.clear()
        self.node_states.clear()
        self.prerequisites_graph.clear()
        self.dependents_graph.clear()
        self.explicit_invalidates_graph.clear()
        self.couplings.clear()

        disciplines = data.get("disciplines", {})
        for disc_id, disc_data in disciplines.items():
            nodes_data = disc_data.get("nodes", {})
            for node_key, node_info in nodes_data.items():
                canonical_id = self._canonicalize(node_key)
                level = int(node_info.get("level", 0))
                name = str(node_info.get("name", node_key))
                description = str(node_info.get("description", ""))
                prereqs = tuple(
                    self._canonicalize(p)
                    for p in node_info.get("prerequisites", [])
                )
                invals = tuple(
                    self._canonicalize(inv)
                    for inv in node_info.get("invalidates", [])
                )
                recovery = str(
                    node_info.get(
                        "suggested_recovery",
                        f"Satisfy prerequisite step '{name}'.",
                    )
                )

                definition = NodeDefinition(
                    id=canonical_id,
                    discipline=disc_id,
                    level=level,
                    name=name,
                    description=description,
                    prerequisites=prereqs,
                    invalidates=invals,
                    suggested_recovery=recovery,
                )
                self.nodes[canonical_id] = definition
                self.node_states[canonical_id] = NodeState(id=canonical_id)
                self.prerequisites_graph[canonical_id] = set(prereqs)
                self.explicit_invalidates_graph[canonical_id] = set(invals)

        # Build reverse dependency edges (node -> downstream dependents)
        for node_id in self.nodes:
            if node_id not in self.dependents_graph:
                self.dependents_graph[node_id] = set()

        for node_id, prereqs in self.prerequisites_graph.items():
            for p in prereqs:
                if p not in self.dependents_graph:
                    self.dependents_graph[p] = set()
                self.dependents_graph[p].add(node_id)

        # Register multiphysics couplings
        couplings_data = data.get("couplings", {})
        for coup_id, coup_info in couplings_data.items():
            source = self._canonicalize(coup_info.get("source_node", ""))
            target = self._canonicalize(coup_info.get("target_node", ""))
            self.couplings[coup_id] = {
                "name": coup_info.get("name", coup_id),
                "source_node": source,
                "target_node": target,
                "description": coup_info.get("description", ""),
            }

    def _canonicalize(self, node: str) -> str:
        """Normalize node identifier string."""
        if not node:
            return ""
        return str(node).strip().upper()

    def _validate_dag(self) -> None:
        """Verify graph acyclicity using Kahn topological sort algorithm."""
        in_degree: Dict[str, int] = {node: 0 for node in self.nodes}
        for node, prereqs in self.prerequisites_graph.items():
            for p in prereqs:
                if p in in_degree:
                    in_degree[node] += 1

        queue: deque[str] = deque(
            [node for node, deg in in_degree.items() if deg == 0]
        )
        visited_count = 0

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for downstream in self.dependents_graph.get(curr, set()):
                if downstream in in_degree:
                    in_degree[downstream] -= 1
                    if in_degree[downstream] == 0:
                        queue.append(downstream)

        if visited_count != len(self.nodes):
            unresolved = [node for node, deg in in_degree.items() if deg > 0]
            raise ValueError(
                f"Cyclic dependency detected in DAMG topology. Unresolved nodes: {unresolved}"
            )

    def is_node_satisfied(self, node: str) -> bool:
        """Check if a node is satisfied and not dirty.

        Returns True only if the node exists and status is SATISFIED.
        """
        c_node = self._canonicalize(node)
        state = self.node_states.get(c_node)
        if not state:
            return False
        return state.status == NodeStatus.SATISFIED

    def check_prerequisites(self, required_nodes: List[str]) -> List[str]:
        """Check a list of required nodes.

        Returns a list of node IDs that are UNSATISFIED, DIRTY, or unknown.
        Returns an empty list if all prerequisites are SATISFIED.
        """
        missing_or_dirty: List[str] = []
        for req in required_nodes:
            c_node = self._canonicalize(req)
            state = self.node_states.get(c_node)
            if not state or state.status != NodeStatus.SATISFIED:
                missing_or_dirty.append(c_node)
        return missing_or_dirty

    def mark_node_satisfied(
        self, node: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark a node as SATISFIED and record execution metadata."""
        c_node = self._canonicalize(node)
        if c_node not in self.node_states:
            # Register ad-hoc node dynamically if not present in static manifest
            self.node_states[c_node] = NodeState(id=c_node)
            if c_node not in self.dependents_graph:
                self.dependents_graph[c_node] = set()
            if c_node not in self.explicit_invalidates_graph:
                self.explicit_invalidates_graph[c_node] = set()

        state = self.node_states[c_node]
        state.status = NodeStatus.SATISFIED
        state.satisfied_at = time.time()
        state.invalidated_at = None
        if metadata:
            state.metadata.update(metadata)
        logger.debug(
            "Session '%s': node '%s' marked SATISFIED", self.session_id, c_node
        )

    def invalidate_node_and_downstream(self, dirty_node: str) -> List[str]:
        """Invalidate a node and cascade DIRTY status to downstream dependents.

        Uses Breadth-First Search (BFS) to traverse directed edges in the DAG.
        Returns a list of all affected node IDs in traversal order.
        """
        start_node = self._canonicalize(dirty_node)
        if not start_node:
            return []

        invalidated_list: List[str] = []
        queue: deque[str] = deque([start_node])
        visited: Set[str] = {start_node}
        now = time.time()

        while queue:
            curr = queue.popleft()
            invalidated_list.append(curr)

            if curr not in self.node_states:
                self.node_states[curr] = NodeState(id=curr)

            state = self.node_states[curr]
            state.status = NodeStatus.DIRTY
            state.invalidated_at = now

            # Collect downstream dependents from causal DAG edges and explicit manifests
            direct_dependents = self.dependents_graph.get(curr, set())
            explicit_invalids = self.explicit_invalidates_graph.get(curr, set())
            children = direct_dependents | explicit_invalids

            for child in sorted(children):
                if child not in visited:
                    visited.add(child)
                    queue.append(child)

        logger.info(
            "Session '%s': invalidation cascade from '%s' dirtied %d nodes: %s",
            self.session_id,
            start_node,
            len(invalidated_list),
            invalidated_list,
        )
        return invalidated_list

    def reset_state(self) -> None:
        """Reset all nodes in this session to UNSATISFIED status."""
        for state in self.node_states.values():
            state.status = NodeStatus.UNSATISFIED
            state.satisfied_at = None
            state.invalidated_at = None
            state.metadata.clear()
        logger.debug("Session '%s': state machine reset", self.session_id)

    def get_node_status(self, node: str) -> NodeStatus:
        """Retrieve current status of a node."""
        c_node = self._canonicalize(node)
        state = self.node_states.get(c_node)
        if not state:
            return NodeStatus.UNSATISFIED
        return state.status

    def get_node_definition(self, node: str) -> Optional[NodeDefinition]:
        """Retrieve static definition metadata for a node."""
        c_node = self._canonicalize(node)
        return self.nodes.get(c_node)

    def get_recovery_suggestion(self, node: str) -> str:
        """Return actionable recovery advice for a missing prerequisite."""
        c_node = self._canonicalize(node)
        defn = self.nodes.get(c_node)
        if defn and defn.suggested_recovery:
            return defn.suggested_recovery
        return f"Execute upstream tools to satisfy requirement '{c_node}'."

    def get_missing_prerequisites_details(
        self, required_nodes: List[str]
    ) -> List[Dict[str, Any]]:
        """Return structured details for missing or dirty prerequisites."""
        details: List[Dict[str, Any]] = []
        for req in required_nodes:
            c_node = self._canonicalize(req)
            state = self.node_states.get(c_node)
            defn = self.nodes.get(c_node)
            status_val = (
                state.status.value if state else NodeStatus.UNSATISFIED.value
            )
            details.append(
                {
                    "node": c_node,
                    "status": status_val,
                    "level": defn.level if defn else None,
                    "discipline": defn.discipline if defn else None,
                    "name": defn.name if defn else c_node,
                    "suggested_recovery": self.get_recovery_suggestion(c_node),
                }
            )
        return details

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Export snapshot of all node states in this session."""
        snapshot: Dict[str, Dict[str, Any]] = {}
        for node_id, state in self.node_states.items():
            defn = self.nodes.get(node_id)
            snapshot[node_id] = {
                "status": state.status.value,
                "level": defn.level if defn else None,
                "discipline": defn.discipline if defn else None,
                "satisfied_at": state.satisfied_at,
                "invalidated_at": state.invalidated_at,
                "metadata": state.metadata,
            }
        return snapshot
