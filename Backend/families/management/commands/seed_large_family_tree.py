import random
from dataclasses import dataclass
import json

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError, call_command
from rest_framework.test import APIClient

from families.models import Family, FamilyMember, Relationship


@dataclass
class SeedStats:
    members_created: int = 0
    add_relative_calls: int = 0
    link_existing_calls: int = 0


class Command(BaseCommand):
    help = "Reset local DB and seed a large multi-generation family tree using tree-edit API paths."

    def add_arguments(self, parser):
        parser.add_argument("--reset-db", action="store_true", help="Run flush before seeding.")
        parser.add_argument("--up-depth", type=int, default=7, help="Ancestor generations above anchor.")
        parser.add_argument("--down-depth", type=int, default=6, help="Descendant generations below anchor.")
        parser.add_argument("--children-min", type=int, default=3, help="Min children per couple.")
        parser.add_argument("--children-max", type=int, default=5, help="Max children per couple.")
        parser.add_argument(
            "--continuation-couples",
            type=int,
            default=2,
            help="How many child branches per couple continue into next generation.",
        )
        parser.add_argument(
            "--max-members",
            type=int,
            default=420,
            help="Hard cap for total FamilyMember rows to prevent runaway growth.",
        )
        parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed.")
        parser.add_argument("--username", type=str, default="seeduser", help="Seed login username.")
        parser.add_argument("--password", type=str, default="SeedPass123!", help="Seed login password.")
        parser.add_argument("--email", type=str, default="seeduser@example.com", help="Seed login email.")

    def handle(self, *args, **options):
        up_depth = max(1, options["up_depth"])
        down_depth = max(1, options["down_depth"])
        children_min = max(2, options["children_min"])
        children_max = max(children_min, options["children_max"])
        continuation_couples = max(1, options["continuation_couples"])
        self.max_members = max(20, options["max_members"])
        seed = options["seed"]
        limit_hit = False

        random.seed(seed)

        if options["reset_db"]:
            self.stdout.write(self.style.WARNING("Flushing database..."))
            call_command("flush", interactive=False)

        user, anchor_member = self._bootstrap_user_and_anchor(
            username=options["username"],
            password=options["password"],
            email=options["email"],
        )

        client = APIClient()
        # APIClient defaults to testserver; use localhost to satisfy ALLOWED_HOSTS.
        client.defaults["HTTP_HOST"] = "localhost"
        client.force_authenticate(user=user)

        stats = SeedStats()

        # Build upward generations using a lineage chain while adding siblings,
        # so each ancestor couple has multiple children instead of single-child chains.
        self.stdout.write(self.style.NOTICE(f"Creating {up_depth} generations upward..."))
        current_member_id = anchor_member.id
        for gen in range(1, up_depth + 1):
            father = self._add_relative(
                client,
                anchor_id=current_member_id,
                relation_type="PARENT",
                full_name=self._name("AncFather", gen, "M"),
                gender="M",
                age=max(30, 38 + (up_depth - gen) * 5),
                stats=stats,
            )
            if not father:
                limit_hit = True
                break

            mother = self._add_relative(
                client,
                anchor_id=current_member_id,
                relation_type="PARENT",
                full_name=self._name("AncMother", gen, "F"),
                gender="F",
                age=max(30, 36 + (up_depth - gen) * 5),
                stats=stats,
            )
            if not mother:
                limit_hit = True
                break

            self._link_existing(
                client,
                anchor_id=father["id"],
                relation_type="SPOUSE",
                target_id=mother["id"],
                stats=stats,
            )

            # Ensure this ancestor couple has multiple children.
            sibling_count = random.randint(1, 3)
            for sib_idx in range(sibling_count):
                sibling_gender = random.choice(["M", "F"])
                sibling = self._add_relative(
                    client,
                    anchor_id=current_member_id,
                    relation_type="SIBLING",
                    full_name=self._name(f"AncSib{sib_idx+1}", gen, sibling_gender),
                    gender=sibling_gender,
                    age=max(1, 30 - gen),
                    stats=stats,
                )
                if not sibling:
                    limit_hit = True
                    break

            if limit_hit:
                break

            # Continue lineage depth through alternating parent sides.
            current_member_id = father["id"] if gen % 2 else mother["id"]

        # Build downward generations with broad branching and no leaf-only spouse rows.
        self.stdout.write(self.style.NOTICE(f"Creating {down_depth} generations downward..."))
        anchor = FamilyMember.objects.get(id=anchor_member.id)
        anchor_spouse_gender = "F" if anchor.gender == "M" else "M"
        anchor_spouse = self._add_relative(
            client,
            anchor_id=anchor.id,
            relation_type="SPOUSE",
            full_name=self._name("RootSpouse", 0, anchor_spouse_gender),
            gender=anchor_spouse_gender,
            age=max(20, (anchor.age or 30) - random.randint(0, 3)),
            stats=stats,
        )
        if not anchor_spouse:
            limit_hit = True

        active_couples = [(anchor.id, anchor_spouse["id"])] if anchor_spouse else []

        for gen in range(1, down_depth + 1):
            if limit_hit or not active_couples:
                break

            next_active = []
            for parent_a_id, parent_b_id in active_couples:
                child_count = random.randint(children_min, children_max)
                children = []

                for idx in range(child_count):
                    if not self._can_create_more():
                        limit_hit = True
                        break

                    child_gender = random.choice(["M", "F"])
                    child_name = self._name(f"DescG{gen}C{idx+1}", gen, child_gender)
                    child_age = max(0, 28 - (gen * 2))

                    child = self._add_relative(
                        client,
                        anchor_id=parent_a_id,
                        relation_type="CHILD",
                        full_name=child_name,
                        gender=child_gender,
                        age=child_age,
                        stats=stats,
                    )
                    if not child:
                        limit_hit = True
                        break

                    # Link second parent to child to complete family path.
                    self._link_existing(
                        client,
                        anchor_id=child["id"],
                        relation_type="PARENT",
                        target_id=parent_b_id,
                        stats=stats,
                    )

                    children.append(child)

                if limit_hit:
                    break

                if len(children) >= 2:
                    # Explicit sibling link to exercise link-existing pathway.
                    self._link_existing(
                        client,
                        anchor_id=children[0]["id"],
                        relation_type="SIBLING",
                        target_id=children[1]["id"],
                        stats=stats,
                    )

                # Only create spouses for branches that will continue.
                if gen < down_depth:
                    random.shuffle(children)
                    continue_children = children[: min(len(children), continuation_couples)]

                    for idx, child in enumerate(continue_children):
                        if not self._can_create_more():
                            limit_hit = True
                            break

                        spouse_gender = "F" if child["gender"] == "M" else "M"
                        spouse = self._add_relative(
                            client,
                            anchor_id=child["id"],
                            relation_type="SPOUSE",
                            full_name=self._name(f"DescSpG{gen}C{idx+1}", gen, spouse_gender),
                            gender=spouse_gender,
                            age=max(18, (child.get("age") or 24) + random.randint(-2, 2)),
                            stats=stats,
                        )
                        if not spouse:
                            limit_hit = True
                            break

                        next_active.append((child["id"], spouse["id"]))

                if limit_hit:
                    break

            active_couples = next_active

        self._print_summary(stats)

        if limit_hit:
            self.stdout.write(self.style.WARNING("Stopped early because max-members cap was reached."))

    def _bootstrap_user_and_anchor(self, username: str, password: str, email: str):
        User = get_user_model()

        family = Family.objects.create(sl_no="1", branch="Seed Branch", member_no="SEED-0001")
        anchor_member = FamilyMember.objects.create(
            family=family,
            name="Seed Anchor",
            relation="Head",
            gender="M",
            age=34,
        )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            member=anchor_member,
        )

        return user, anchor_member

    def _name(self, prefix: str, generation: int, gender: str) -> str:
        token = random.randint(1000, 9999)
        suffix = "M" if gender == "M" else "F"
        return f"{prefix}_{generation}_{suffix}_{token}"

    def _can_create_more(self) -> bool:
        return FamilyMember.objects.count() < self.max_members

    def _add_relative(self, client: APIClient, anchor_id: int, relation_type: str, full_name: str, gender: str, age: int, stats: SeedStats):
        if not self._can_create_more():
            return None

        payload = {
            "relation_type": relation_type,
            "name": full_name,
            "gender": gender,
            "age": age,
            "blood_group": random.choice(["A+", "B+", "O+", "AB+", "A-", "B-"]),
            "occupation": random.choice(["Engineer", "Teacher", "Doctor", "Farmer", "Artist", "Developer"]),
            "education": random.choice(["High School", "Diploma", "Bachelor", "Master"]),
            "phone_no": f"9{random.randint(100000000, 999999999)}",
            "email_id": f"{full_name.lower()}@seed.local".replace(" ", ""),
            "address": random.choice(["Main Street", "Lake Road", "Hill View", "Central Colony"]),
            "church_parish": random.choice(["St. Mary", "St. Joseph", "Holy Family", "St. Peter"]),
        }

        res = client.post(f"/api/families/tree-edit/{anchor_id}/add-relative/", payload, format="json")
        stats.add_relative_calls += 1

        if res.status_code != 201:
            raise CommandError(
                f"add-relative failed | anchor={anchor_id} relation={relation_type} "
                f"status={res.status_code} body={self._response_body(res)}"
            )

        body = self._response_body(res)
        data = body.get("member") if isinstance(body, dict) else None
        if not data or "id" not in data:
            raise CommandError("add-relative succeeded but member payload missing id.")

        stats.members_created += 1
        return data

    def _link_existing(self, client: APIClient, anchor_id: int, relation_type: str, target_id: int, stats: SeedStats):
        payload = {
            "relation_type": relation_type,
            "target_member_id": target_id,
        }
        res = client.post(f"/api/families/tree-edit/{anchor_id}/link-existing/", payload, format="json")
        stats.link_existing_calls += 1

        if res.status_code != 200:
            raise CommandError(
                f"link-existing failed | anchor={anchor_id} target={target_id} relation={relation_type} "
                f"status={res.status_code} body={self._response_body(res)}"
            )

    def _response_body(self, response):
        if hasattr(response, "data"):
            return response.data

        raw = getattr(response, "content", b"")
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="replace")
        else:
            text = str(raw)

        try:
            return json.loads(text)
        except Exception:
            return text[:500]

    def _print_summary(self, stats: SeedStats):
        members_total = FamilyMember.objects.count()
        rel_total = Relationship.objects.count()
        spouse_total = Relationship.objects.filter(relation_type="SPOUSE").count()

        reverse_spouse_duplicates = 0
        seen = set()
        for rel in Relationship.objects.filter(relation_type="SPOUSE"):
            pair = tuple(sorted((rel.from_member_id, rel.to_member_id)))
            if pair in seen:
                reverse_spouse_duplicates += 1
            else:
                seen.add(pair)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(f"Members created via add-relative: {stats.members_created}")
        self.stdout.write(f"add-relative API calls: {stats.add_relative_calls}")
        self.stdout.write(f"link-existing API calls: {stats.link_existing_calls}")
        self.stdout.write(f"Total FamilyMember rows: {members_total}")
        self.stdout.write(f"Total Relationship rows: {rel_total}")
        self.stdout.write(f"Total SPOUSE rows: {spouse_total}")
        self.stdout.write(f"Reverse spouse duplicates found: {reverse_spouse_duplicates}")

        if reverse_spouse_duplicates:
            raise CommandError("Reverse spouse duplicates detected after seed.")
