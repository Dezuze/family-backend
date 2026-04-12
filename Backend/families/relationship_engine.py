from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Set, Tuple

from .models import FamilyMember, Relationship

BASE_RELATIONS = {"PARENT", "CHILD", "SPOUSE", "SIBLING"}


def _great_label(prefix: str, depth: int) -> str:
    if depth <= 1:
        return prefix
    if depth == 2:
        return f"Grand{prefix}"
    great_count = depth - 2
    return f"{'Great-' * great_count}Grand{prefix}"


@dataclass
class TreePayload:
    nodes: List[dict]
    edges: List[dict]
    computed_relations: List[dict]
    generation_depth: int


class RelationshipEngine:
    """Build graph edges and perspective-relative computed labels."""

    def __init__(self, members: Iterable[Any], relationships: Iterable[Any]):
        self.members = list(members)
        self.relationships = list(relationships)

        self.parent_children: Dict[int, Set[int]] = defaultdict(set)
        self.child_parents: Dict[int, Set[int]] = defaultdict(set)
        self.spouse_pairs: Set[Tuple[int, int]] = set()
        self.sibling_pairs: Set[Tuple[int, int]] = set()

        self._ingest_relationships()
        self._ingest_parent_links_from_members()
        self._infer_siblings_from_shared_parents()

    @staticmethod
    def canonicalize_input(label: str) -> str | None:
        normalized = (label or "").strip().lower()
        if not normalized:
            return None

        mapping = {
            "parent": "PARENT",
            "father": "PARENT",
            "mother": "PARENT",
            "child": "CHILD",
            "son": "CHILD",
            "daughter": "CHILD",
            "spouse": "SPOUSE",
            "husband": "SPOUSE",
            "wife": "SPOUSE",
            "sibling": "SIBLING",
            "brother": "SIBLING",
            "sister": "SIBLING",
            "parent of": "PARENT",
            "child of": "CHILD",
        }
        return mapping.get(normalized)

    @staticmethod
    def is_banned_label(label: str) -> bool:
        normalized = (label or "").strip().lower()
        if not normalized:
            return False
        banned_tokens = ("uncle", "cousin", "great grandfather", "great-grandfather")
        return any(token in normalized for token in banned_tokens)

    def _ingest_relationships(self) -> None:
        for rel in self.relationships:
            rtype = (rel.relation_type or "").strip().upper()
            a = rel.from_member_id
            b = rel.to_member_id
            if not a or not b or a == b:
                continue

            if rtype == "PARENT":
                # from member says: to member is my parent
                self._add_parent(parent_id=b, child_id=a)
            elif rtype == "CHILD":
                # from member says: to member is my child
                self._add_parent(parent_id=a, child_id=b)
            elif rtype == "SPOUSE":
                # Always canonicalize spouse pairs to prevent duplicates
                canonical_pair = self._pair(a, b)
                self.spouse_pairs.add(canonical_pair)
            elif rtype == "SIBLING":
                self.sibling_pairs.add(self._pair(a, b))

    def _ingest_parent_links_from_members(self) -> None:
        # Respect parent M2M as authoritative structural input without writing
        # derived Relationship rows during read operations.
        for member in self.members:
            try:
                parents = member.parents.all()
            except Exception:
                continue
            for parent in parents:
                self._add_parent(parent_id=parent.id, child_id=member.id)

    def _add_parent(self, parent_id: int, child_id: int) -> None:
        if parent_id == child_id:
            return
        self.parent_children[parent_id].add(child_id)
        self.child_parents[child_id].add(parent_id)

    @staticmethod
    def _pair(a: int, b: int) -> Tuple[int, int]:
        return (a, b) if a < b else (b, a)

    def _infer_siblings_from_shared_parents(self) -> None:
        for parent_id, children in self.parent_children.items():
            children_list = list(children)
            for i in range(len(children_list)):
                for j in range(i + 1, len(children_list)):
                    self.sibling_pairs.add(self._pair(children_list[i], children_list[j]))

    def _infer_spouses_from_coparents(self) -> None:
        for child_id, parents in self.child_parents.items():
            parent_list = list(parents)
            for i in range(len(parent_list)):
                for j in range(i + 1, len(parent_list)):
                    self.spouse_pairs.add(self._pair(parent_list[i], parent_list[j]))

    def _ancestor_depths(self, root_id: int) -> Dict[int, int]:
        depths: Dict[int, int] = {}
        q = deque([(root_id, 0)])
        seen = {root_id}

        while q:
            node_id, depth = q.popleft()
            for parent_id in self.child_parents.get(node_id, set()):
                next_depth = depth + 1
                if parent_id not in depths or next_depth < depths[parent_id]:
                    depths[parent_id] = next_depth
                if parent_id not in seen:
                    seen.add(parent_id)
                    q.append((parent_id, next_depth))
        return depths

    def _descendant_depths(self, root_id: int) -> Dict[int, int]:
        depths: Dict[int, int] = {}
        q = deque([(root_id, 0)])
        seen = {root_id}

        while q:
            node_id, depth = q.popleft()
            for child_id in self.parent_children.get(node_id, set()):
                next_depth = depth + 1
                if child_id not in depths or next_depth < depths[child_id]:
                    depths[child_id] = next_depth
                if child_id not in seen:
                    seen.add(child_id)
                    q.append((child_id, next_depth))
        return depths

    def compute_relations(self, root_id: int | None) -> Tuple[List[dict], int, Dict[int, str]]:
        if not root_id:
            return [], 0, {}

        ancestor_depth = self._ancestor_depths(root_id)
        descendant_depth = self._descendant_depths(root_id)

        computed: List[dict] = []
        relation_map: Dict[int, str] = {root_id: "Self"}

        for member in self.members:
            member_id = member.id
            if member_id == root_id:
                continue

            if member_id in ancestor_depth:
                depth = ancestor_depth[member_id]
                label = _great_label("parent", depth).title()
                relation_map[member_id] = label
                computed.append(
                    {
                        "from": root_id,
                        "to": member_id,
                        "label": label,
                        "kind": "ancestor",
                        "depth": depth,
                    }
                )
                continue

            if member_id in descendant_depth:
                depth = descendant_depth[member_id]
                label = _great_label("child", depth).title()
                relation_map[member_id] = label
                computed.append(
                    {
                        "from": root_id,
                        "to": member_id,
                        "label": label,
                        "kind": "descendant",
                        "depth": depth,
                    }
                )
                continue

            if self._pair(root_id, member_id) in self.sibling_pairs:
                relation_map[member_id] = "Sibling"
                computed.append(
                    {
                        "from": root_id,
                        "to": member_id,
                        "label": "Sibling",
                        "kind": "sibling",
                        "depth": 0,
                    }
                )
                continue

            if self._pair(root_id, member_id) in self.spouse_pairs:
                relation_map[member_id] = "Spouse"
                computed.append(
                    {
                        "from": root_id,
                        "to": member_id,
                        "label": "Spouse",
                        "kind": "spouse",
                        "depth": 0,
                    }
                )

        generation_depth = max(ancestor_depth.values()) if ancestor_depth else 0
        return computed, generation_depth, relation_map

    def build_edges(self) -> List[dict]:
        edges: List[dict] = []
        seen = set()

        for parent_id, children in self.parent_children.items():
            for child_id in children:
                key = (parent_id, child_id, "parent")
                if key not in seen:
                    seen.add(key)
                    edges.append({"source": parent_id, "target": child_id, "type": "parent"})

        for a, b in self.spouse_pairs:
            key = (a, b, "spouse")
            if key not in seen:
                seen.add(key)
                edges.append({"source": a, "target": b, "type": "spouse"})

        for a, b in self.sibling_pairs:
            key = (a, b, "sibling")
            if key not in seen:
                seen.add(key)
                edges.append({"source": a, "target": b, "type": "sibling"})

        return edges

    def build_payload(self, root_id: int | None = None) -> TreePayload:
        computed_relations, generation_depth, relation_map = self.compute_relations(root_id)

        nodes = []
        for member in self.members:
            username = getattr(getattr(member, "user_account", None), "username", None)
            viewer_label = relation_map.get(member.id)
            nodes.append(
                {
                    "id": member.id,
                    "member_id": member.member_id,
                    "name": member.name,
                    "name_ml": member.name_ml,
                    "photo": member.photo.url if member.photo else None,
                    "role": viewer_label or member.role,
                    "relation": viewer_label or member.relation,
                    "is_committee": member.is_committee,
                    "username": username,
                    "gender": member.gender,
                    "age": member.age,
                    "nickname": member.nickname,
                    "occupation": member.occupation,
                    "date_of_birth": member.date_of_birth,
                    "date_of_death": member.date_of_death,
                    "blood_group": member.blood_group,
                    "education": member.education,
                    "is_deceased": member.is_deceased,
                    "phone_no": member.phone_no,
                    "email_id": member.email_id,
                    "church_parish": member.church_parish,
                    "bio": member.bio,
                    "address": member.address_if_different,
                    "location": member.address_if_different,
                    "place_of_work": member.place_of_work,
                }
            )

        return TreePayload(
            nodes=nodes,
            edges=self.build_edges(),
            computed_relations=computed_relations,
            generation_depth=generation_depth,
        )
