"""
Comprehensive tests for the families app.
Covers: FamilyMember CRUD, Relationships, Profile management,
        Managed Members (list/create/edit/delete), Guardian permissions,
        Family tree endpoint.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import datetime
from families.models import Family, FamilyMember, Relationship
from profiles.models import CommunityRole

User = get_user_model()


class FamilyModelTests(TestCase):
    """Test Family and FamilyMember model basics."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="North", member_no="F-MODEL-001")

    def test_family_str(self):
        self.assertEqual(str(self.family), "North (F-MODEL-001)")

    def test_create_member(self):
        m = FamilyMember.objects.create(
            family=self.family, name="Alice", age=50,
            relation="Head", date_of_birth=datetime.date(1974, 5, 5),
            blood_group="A+", gender="F"
        )
        self.assertEqual(m.name, "Alice")
        self.assertEqual(m.gender, "F")
        self.assertFalse(m.is_independent)
        self.assertFalse(m.is_deceased)

    def test_member_with_date_of_death(self):
        m = FamilyMember.objects.create(
            family=self.family, name="Deceased", age=80,
            relation="Grandfather", is_deceased=True,
            date_of_death=datetime.date(2020, 3, 15), gender="M"
        )
        self.assertTrue(m.is_deceased)
        self.assertEqual(m.date_of_death, datetime.date(2020, 3, 15))

    def test_member_without_dob(self):
        """Members should be creatable without date_of_birth."""
        m = FamilyMember.objects.create(
            family=self.family, name="No DOB", relation="Other"
        )
        self.assertIsNone(m.date_of_birth)

    def test_parent_child_relationship(self):
        parent = FamilyMember.objects.create(
            family=self.family, name="Parent", age=50, relation="Head"
        )
        child = FamilyMember.objects.create(
            family=self.family, name="Child", age=25, relation="Son"
        )
        child.parents.add(parent)
        self.assertIn(parent, child.parents.all())
        self.assertIn(child, parent.children.all())

    def test_relation_choices(self):
        """Verify all relation choices are valid."""
        valid = [c[0] for c in FamilyMember.RELATION_CHOICES]
        self.assertIn('Head', valid)
        self.assertIn('Father', valid)
        self.assertIn('Mother', valid)
        self.assertIn('Son', valid)
        self.assertIn('Daughter', valid)
        self.assertIn('Brother-in-law', valid)
        self.assertIn('Other', valid)
        self.assertEqual(len(valid), 24)


class RelationshipModelTests(TestCase):
    """Test the simplified Relationship model (PARENT/SPOUSE/SIBLING)."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-REL-001")
        self.m1 = FamilyMember.objects.create(family=self.family, name="A", relation="Head")
        self.m2 = FamilyMember.objects.create(family=self.family, name="B", relation="Spouse")

    def test_create_relationship(self):
        rel = Relationship.objects.create(
            from_member=self.m1, to_member=self.m2, relation_type="SPOUSE"
        )
        self.assertEqual(rel.relation_type, "SPOUSE")

    def test_relationship_str(self):
        rel = Relationship.objects.create(
            from_member=self.m1, to_member=self.m2, relation_type="PARENT"
        )
        self.assertIn("PARENT", str(rel))

    def test_unique_constraint(self):
        """Same from/to/type should not be duplicated."""
        Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SPOUSE")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SPOUSE")

    def test_different_types_allowed(self):
        """Same pair can have different relationship types."""
        Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SPOUSE")
        Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SIBLING")
        self.assertEqual(Relationship.objects.filter(from_member=self.m1).count(), 2)


class UserProfileViewTests(TestCase):
    """Test the /api/families/profile/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-PROF-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="Profile User", age=30,
            relation="Head", gender="M"
        )
        self.user = User.objects.create_user(
            username="profuser", email="prof@example.com",
            password="Pass123!", member=self.member
        )

    def test_get_own_profile(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/families/profile/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], "Profile User")
        self.assertIn('is_independent', res.data)
        self.assertIn('has_account', res.data)

    def test_update_own_profile(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/families/profile/', {
            "first_name": "Updated",
            "last_name": "Name",
            "gender": "M",
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_profile_without_dob(self):
        """Saving profile without DOB should not error."""
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/families/profile/', {
            "first_name": "No",
            "last_name": "DOB",
            "gender": "F",
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_unauthenticated_profile(self):
        res = self.client.get('/api/families/profile/')
        self.assertIn(res.status_code, [401, 403])


class ManagedMembersViewTests(TestCase):
    """Test managed members CRUD operations via /api/families/managed/."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-MNG-001")
        CommunityRole.objects.get_or_create(name='Youth Coordinator', defaults={'priority': 15, 'is_active': True})
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guardian", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="mng_guard", email="mng_guard@example.com",
            password="Pass123!", member=self.guardian_member
        )

    def test_list_managed_empty(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.get('/api/families/managed/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_create_managed_member(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "Child",
            "last_name": "One",
            "relation": "Son",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)
        self.assertIn("Child One", res.data['name'])

    def test_create_managed_deceased_with_death_date(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "Grandpa",
            "last_name": "Joe",
            "relation": "Parent",
            "gender": "M",
            "is_deceased": True,
            "date_of_death": "2020-01-15"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)

    def test_create_managed_member_rejects_unknown_community_role(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "Child",
            "last_name": "Role",
            "relation": "Son",
            "gender": "M",
            "committee_role": "Non Existing Role"
        }, format='multipart')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid community role', str(res.data))

    def test_list_managed_excludes_independent(self):
        """Independent members should not appear in managed list."""
        managed = FamilyMember.objects.create(
            family=self.family, name="Indep", relation="Son",
            created_by=self.guardian, is_independent=True
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.get('/api/families/managed/')
        self.assertEqual(res.status_code, 200)
        ids = [m['id'] for m in res.data]
        self.assertNotIn(managed.id, ids)

    def test_edit_managed_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Edit Me", relation="Son",
            created_by=self.guardian, is_independent=False
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.put(f'/api/families/managed/{managed.id}/', {
            "first_name": "Edited",
            "last_name": "Name",
            "relation": "Daughter",
            "gender": "F"
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_cannot_edit_independent_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Free", relation="Son",
            created_by=self.guardian, is_independent=True
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.put(f'/api/families/managed/{managed.id}/', {
            "first_name": "Hacked"
        }, format='multipart')
        self.assertEqual(res.status_code, 403)

    def test_delete_managed_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Delete Me", relation="Son",
            created_by=self.guardian, is_independent=False
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/managed/{managed.id}/')
        self.assertEqual(res.status_code, 204)

    def test_cannot_delete_independent_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Free Delete", relation="Son",
            created_by=self.guardian, is_independent=True
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/managed/{managed.id}/')
        self.assertEqual(res.status_code, 403)

    def test_get_managed_member_detail(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Detail", relation="Son",
            created_by=self.guardian, is_independent=False
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.get(f'/api/families/managed/{managed.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], "Detail")

    def test_create_son_creates_relationship(self):
        """Adding a 'Son' managed member should auto-create a Relationship."""
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "My",
            "last_name": "Son",
            "relation": "Son",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)
        son_id = res.data['id']

        # Son means child edge from member to creator.
        self.assertTrue(
            Relationship.objects.filter(
                from_member_id=son_id,
                to_member=self.guardian_member,
                relation_type='CHILD'
            ).exists()
        )
        # Verify parents M2M is set
        son = FamilyMember.objects.get(id=son_id)
        self.assertIn(self.guardian_member, son.parents.all())

    def test_create_spouse_creates_relationship(self):
        """Adding a 'Spouse' managed member should auto-create a Spouse Relationship."""
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "My",
            "last_name": "Wife",
            "relation": "Spouse",
            "gender": "F"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)
        spouse_id = res.data['id']

        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member_id=spouse_id,
                relation_type='SPOUSE'
            ).exists()
        )

    def test_create_father_creates_relationship(self):
        """Adding a 'Father' managed member should make him parent of creator."""
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "My",
            "last_name": "Dad",
            "relation": "Father",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)
        father_id = res.data['id']

        # Verify: creator has parent edge to the new member.
        self.assertTrue(
            Relationship.objects.filter(
                from_member_id=father_id,
                to_member=self.guardian_member,
                relation_type='PARENT'
            ).exists()
        )
        # Verify parents M2M: creator's parent should include new member
        self.assertIn(
            FamilyMember.objects.get(id=father_id),
            self.guardian_member.parents.all()
        )

    def test_create_custom_relation_is_rejected(self):
        """Derived labels are rejected; only parent/child/spouse/sibling can be defined."""
        self.client.force_authenticate(user=self.guardian)
        custom_relation = "great great great grandfather"
        res = self.client.post('/api/families/managed/', {
            "first_name": "Great",
            "last_name": "Ancestor",
            "relation": custom_relation,
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 400)

    def test_derived_relation_in_tree_is_computed_from_base_edges(self):
        self.client.force_authenticate(user=self.guardian)
        parent = FamilyMember.objects.create(
            family=self.family,
            name="Parent Node",
            relation="Other",
            gender="M",
            created_by=self.guardian,
        )
        grandparent = FamilyMember.objects.create(
            family=self.family,
            name="Grandparent Node",
            relation="Other",
            gender="F",
            created_by=self.guardian,
        )
        Relationship.objects.create(from_member=self.guardian_member, to_member=parent, relation_type='PARENT')
        Relationship.objects.create(from_member=parent, to_member=grandparent, relation_type='PARENT')

        tree_for_guardian = self.client.get('/api/families/tree/')
        self.assertEqual(tree_for_guardian.status_code, 200)
        guardian_node = next((n for n in tree_for_guardian.data['nodes'] if n['id'] == grandparent.id), None)
        self.assertIsNotNone(guardian_node)
        self.assertEqual(guardian_node['relation'], 'Grandparent')

        other_member = FamilyMember.objects.create(
            family=self.family, name="Other Viewer", age=31, relation="Head", gender="M"
        )
        other_user = User.objects.create_user(
            username="other_viewer", email="other_viewer@example.com",
            password="Pass123!", member=other_member
        )
        self.client.force_authenticate(user=other_user)

        tree_for_other = self.client.get('/api/families/tree/')
        self.assertEqual(tree_for_other.status_code, 200)
        other_node = next((n for n in tree_for_other.data['nodes'] if n['id'] == grandparent.id), None)
        self.assertIsNotNone(other_node)
        self.assertNotEqual(other_node['relation'], 'Grandparent')

    def test_son_appears_in_tree(self):
        """A managed Son should appear connected in /api/families/tree/."""
        self.client.force_authenticate(user=self.guardian)
        self.client.post('/api/families/managed/', {
            "first_name": "Tree",
            "last_name": "Son",
            "relation": "Son",
            "gender": "M"
        }, format='multipart')

        res = self.client.get('/api/families/tree/')
        self.assertEqual(res.status_code, 200)
        edges = res.data['edges']

        # There should be a parent link from guardian to the new son
        parent_links = [l for l in edges if l['type'] == 'parent' and l['source'] == self.guardian_member.id]
        self.assertTrue(len(parent_links) > 0, "Son should be linked as child of guardian in tree")


class FamilyTreeViewTests(TestCase):
    """Test the /api/families/tree/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-TREE-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="Tree User", name_ml="ട്രി യൂസർ", age=30, relation="Head"
        )
        self.user = User.objects.create_user(
            username="treeuser", email="tree@example.com",
            password="Pass123!", member=self.member
        )

    def test_get_tree(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/families/tree/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('nodes', res.data)
        self.assertIn('edges', res.data)
        self.assertIn('computed_relations', res.data)
        self.assertIn('generation_depth', res.data)

        me = next((n for n in res.data['nodes'] if n['id'] == self.member.id), None)
        self.assertIsNotNone(me)
        self.assertEqual(me.get('name_ml'), "ട്രി യൂസർ")

    def test_tree_unauthenticated(self):
        res = self.client.get('/api/families/tree/')
        self.assertEqual(res.status_code, 200)  # Tree is public

    def test_authenticated_user_sees_members_from_other_families(self):
        other_family = Family.objects.create(sl_no="2", branch="Other", member_no="F-TREE-002")
        other_member = FamilyMember.objects.create(
            family=other_family,
            name="Other Family Member",
            relation="Head",
            gender="F",
        )

        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/families/tree/')
        self.assertEqual(res.status_code, 200)

        node_ids = {node['id'] for node in res.data.get('nodes', [])}
        self.assertIn(self.member.id, node_ids)
        self.assertIn(other_member.id, node_ids)


class PerspectiveBranchingTests(TestCase):
    """Ensure relationship creation stays perspective-safe unless explicit targets are provided."""

    def setUp(self):
        self.client = APIClient()
        self.family1 = Family.objects.create(sl_no="1", branch="Branch A", member_no="F-BR-001")
        self.family2 = Family.objects.create(sl_no="2", branch="Branch B", member_no="F-BR-002")

        self.user1_member = FamilyMember.objects.create(
            family=self.family1, name="User One", age=30, relation="Head", gender="M"
        )
        self.user2_member = FamilyMember.objects.create(
            family=self.family2, name="User Two", age=28, relation="Head", gender="F"
        )

        self.user1 = User.objects.create_user(
            username="branch_user_1", email="branch1@example.com", password="Pass123!", member=self.user1_member
        )
        self.user2 = User.objects.create_user(
            username="branch_user_2", email="branch2@example.com", password="Pass123!", member=self.user2_member
        )

    def test_managed_member_uses_creator_family(self):
        self.client.force_authenticate(user=self.user2)
        res = self.client.post('/api/families/managed/', {
            "first_name": "Child",
            "last_name": "B",
            "relation": "Daughter",
            "gender": "F"
        }, format='multipart')

        self.assertEqual(res.status_code, 201)
        created = FamilyMember.objects.get(id=res.data['id'])
        self.assertEqual(created.family_id, self.family2.id)

    def test_same_name_members_do_not_auto_link_across_users(self):
        self.client.force_authenticate(user=self.user1)
        res1 = self.client.post('/api/families/managed/', {
            "first_name": "Shared",
            "last_name": "Father",
            "relation": "Father",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res1.status_code, 201)
        user1_father_id = res1.data['id']

        self.client.force_authenticate(user=self.user2)
        res2 = self.client.post('/api/families/managed/', {
            "first_name": "Shared",
            "last_name": "Father",
            "relation": "Father",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res2.status_code, 201)
        user2_father_id = res2.data['id']

        self.assertNotEqual(user1_father_id, user2_father_id)

        self.assertFalse(
            Relationship.objects.filter(
                from_member=self.user2_member,
                to_member_id=user1_father_id,
                relation_type='PARENT'
            ).exists()
        )
        self.assertTrue(
            Relationship.objects.filter(
                from_member_id=user2_father_id,
                to_member=self.user2_member,
                relation_type='PARENT'
            ).exists()
        )

    def test_explicit_member_id_creates_cross_user_connection(self):
        self.client.force_authenticate(user=self.user1)
        res1 = self.client.post('/api/families/managed/', {
            "first_name": "Explicit",
            "last_name": "Target",
            "relation": "Father",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res1.status_code, 201)
        target_member_id = res1.data['id']

        self.client.force_authenticate(user=self.user2)
        res2 = self.client.post('/api/families/profile/', {
            "relationships": [
                {"to_member": target_member_id, "relation_type": "Parent"}
            ]
        }, format='json')
        self.assertEqual(res2.status_code, 200)

        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.user2_member,
                to_member_id=target_member_id,
                relation_type='PARENT'
            ).exists()
        )
        self.user2_member.refresh_from_db()
        self.assertIn(FamilyMember.objects.get(id=target_member_id), self.user2_member.parents.all())


class PermissionsTests(TestCase):
    """Test IsGuardianOrSelf permission logic via managed member endpoints."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-PERM-001")
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guard", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="perm_guard", email="pg@example.com",
            password="Pass123!", member=self.guardian_member
        )
        self.managed = FamilyMember.objects.create(
            family=self.family, name="Managed", relation="Son",
            created_by=self.guardian, is_independent=False
        )

    def test_guardian_can_read(self):
        client = APIClient()
        client.force_authenticate(user=self.guardian)
        res = client.get(f'/api/families/managed/{self.managed.id}/')
        self.assertEqual(res.status_code, 200)

    def test_guardian_can_write_non_independent(self):
        client = APIClient()
        client.force_authenticate(user=self.guardian)
        res = client.put(f'/api/families/managed/{self.managed.id}/', {
            "first_name": "Updated", "last_name": "Child",
            "relation": "Son", "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_guardian_blocked_when_independent(self):
        self.managed.is_independent = True
        self.managed.save()
        client = APIClient()
        client.force_authenticate(user=self.guardian)
        res = client.put(f'/api/families/managed/{self.managed.id}/', {
            "first_name": "Blocked"
        }, format='multipart')
        self.assertEqual(res.status_code, 403)


class TreeEditEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-EDIT-001")
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guardian", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="tree_guard", email="tree_guard@example.com", password="Pass123!", member=self.guardian_member
        )
        self.other_member = FamilyMember.objects.create(
            family=self.family, name="Other Root", age=33, relation="Head"
        )
        self.other_user = User.objects.create_user(
            username="tree_other", email="tree_other@example.com", password="Pass123!", member=self.other_member
        )

    def test_context_endpoint_returns_relatives(self):
        parent = FamilyMember.objects.create(family=self.family, name="Parent", relation="Father")
        sibling = FamilyMember.objects.create(family=self.family, name="Sibling", relation="Brother")
        child = FamilyMember.objects.create(family=self.family, name="Child", relation="Son")

        self.guardian_member.parents.add(parent)
        sibling.parents.add(parent)
        child.parents.add(self.guardian_member)

        self.client.force_authenticate(user=self.guardian)
        res = self.client.get(f'/api/families/member-context/{self.guardian_member.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['member']['id'], self.guardian_member.id)
        self.assertEqual(len(res.data['parents']), 1)
        self.assertEqual(len(res.data['siblings']), 1)
        self.assertEqual(len(res.data['children']), 1)

    def test_add_child_from_tree_edit(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Tree Child",
                "relation": "child",
                "gender": "M",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 201)
        child_id = res.data['member']['id']
        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member_id=child_id,
                relation_type='CHILD'
            ).exists()
        )

    def test_add_parent_from_tree_edit(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Tree Parent",
                "relation_type": "PARENT",
                "gender": "F",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 201)
        parent_id = res.data['member']['id']
        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member_id=parent_id,
                relation_type='PARENT'
            ).exists()
        )

    def test_add_sibling_inherits_parents(self):
        parent = FamilyMember.objects.create(family=self.family, name="Parent", relation="Father")
        self.guardian_member.parents.add(parent)

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Tree Sibling",
                "relation": "sibling",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 201)
        sibling = FamilyMember.objects.get(id=res.data['member']['id'])
        self.assertIn(parent, sibling.parents.all())
        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member=sibling,
                relation_type='SIBLING'
            ).exists()
        )

    def test_remove_tree_member(self):
        managed = FamilyMember.objects.create(
            family=self.family,
            name="Managed Kid",
            relation="Son",
            created_by=self.guardian,
            is_independent=False,
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/tree-edit/{managed.id}/remove/')
        self.assertEqual(res.status_code, 204)
        self.assertFalse(FamilyMember.objects.filter(id=managed.id).exists())

    def test_remove_member_with_account_is_blocked(self):
        managed = FamilyMember.objects.create(
            family=self.family,
            name="Managed Kid",
            relation="Son",
            created_by=self.guardian,
            is_independent=False,
        )
        User.objects.create_user(
            username="managed_login",
            email="managed_login@example.com",
            password="Pass123!",
            member=managed,
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/tree-edit/{managed.id}/remove/')
        self.assertEqual(res.status_code, 403)

    def test_cannot_add_relative_to_foreign_member(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.other_member.id}/add-relative/',
            {
                "name": "Unauthorized Child",
                "relation_type": "CHILD",
                "gender": "M",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 403)

    def test_cannot_remove_foreign_member(self):
        foreign_dependent = FamilyMember.objects.create(
            family=self.family,
            name="Foreign Dependent",
            relation="Son",
            created_by=self.other_user,
            is_independent=False,
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/tree-edit/{foreign_dependent.id}/remove/')
        self.assertEqual(res.status_code, 403)

    def test_add_parent_keeps_existing_spouse_link(self):
        spouse = FamilyMember.objects.create(
            family=self.family,
            name="Existing Spouse",
            relation="Spouse",
            created_by=self.guardian,
        )
        Relationship.objects.create(
            from_member=self.guardian_member,
            to_member=spouse,
            relation_type='SPOUSE',
        )
        Relationship.objects.create(
            from_member=spouse,
            to_member=self.guardian_member,
            relation_type='SPOUSE',
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Tree Father",
                "relation_type": "PARENT",
                "gender": "M",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 201)
        father_id = res.data['member']['id']

        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member=spouse,
                relation_type='SPOUSE',
            ).exists()
        )
        self.assertFalse(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member_id=father_id,
                relation_type='SPOUSE',
            ).exists()
        )

    def test_cannot_add_second_spouse_from_tree_edit(self):
        spouse = FamilyMember.objects.create(
            family=self.family,
            name="Existing Spouse",
            relation="Spouse",
            created_by=self.guardian,
        )
        Relationship.objects.create(
            from_member=self.guardian_member,
            to_member=spouse,
            relation_type='SPOUSE',
        )
        Relationship.objects.create(
            from_member=spouse,
            to_member=self.guardian_member,
            relation_type='SPOUSE',
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Another Spouse",
                "relation_type": "SPOUSE",
                "gender": "F",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('already has a spouse', str(res.data.get('error', '')).lower())

    def test_cannot_add_second_father_from_tree_edit(self):
        father = FamilyMember.objects.create(
            family=self.family,
            name="Existing Father",
            relation="Father",
            gender="M",
            created_by=self.guardian,
        )
        Relationship.objects.create(
            from_member=self.guardian_member,
            to_member=father,
            relation_type='PARENT',
        )
        self.guardian_member.parents.add(father)

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Another Father",
                "relation_type": "PARENT",
                "gender": "M",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('already has a father', str(res.data.get('error', '')).lower())

    def test_member_search_returns_matches(self):
        FamilyMember.objects.create(family=self.family, name="Tree Person", relation="Other")
        FamilyMember.objects.create(family=self.family, name="Another Person", relation="Other")

        self.client.force_authenticate(user=self.guardian)
        res = self.client.get('/api/families/member-search/?q=tree')
        self.assertEqual(res.status_code, 200)
        self.assertIn('results', res.data)
        self.assertTrue(any(item['name'] == 'Tree Person' for item in res.data['results']))

    def test_link_existing_parent_success(self):
        father = FamilyMember.objects.create(
            family=self.family,
            name="Existing Father",
            relation="Father",
            gender="M",
            created_by=self.other_user,
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/link-existing/',
            {
                "target_member_id": father.id,
                "relation_type": "PARENT",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member=father,
                relation_type='PARENT',
            ).exists()
        )

    def test_unlink_existing_parent_success(self):
        father = FamilyMember.objects.create(
            family=self.family,
            name="Undo Father",
            relation="Father",
            gender="M",
            created_by=self.other_user,
        )
        self.guardian_member.parents.add(father)
        Relationship.objects.create(
            from_member=self.guardian_member,
            to_member=father,
            relation_type='PARENT',
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/unlink-existing/',
            {
                "target_member_id": father.id,
                "relation_type": "PARENT",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(
            Relationship.objects.filter(
                from_member=self.guardian_member,
                to_member=father,
                relation_type='PARENT',
            ).exists()
        )
        self.assertFalse(self.guardian_member.parents.filter(id=father.id).exists())

    def test_link_existing_rejects_second_spouse(self):
        spouse = FamilyMember.objects.create(
            family=self.family,
            name="Existing Spouse",
            relation="Spouse",
            gender="F",
            created_by=self.guardian,
        )
        another = FamilyMember.objects.create(
            family=self.family,
            name="Another Person",
            relation="Other",
            gender="F",
            created_by=self.guardian,
        )
        Relationship.objects.create(
            from_member=self.guardian_member,
            to_member=spouse,
            relation_type='SPOUSE',
        )
        Relationship.objects.create(
            from_member=spouse,
            to_member=self.guardian_member,
            relation_type='SPOUSE',
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/link-existing/',
            {
                "target_member_id": another.id,
                "relation_type": "SPOUSE",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('already has a spouse', str(res.data.get('error', '')).lower())

    def test_link_existing_requires_anchor_permission(self):
        target = FamilyMember.objects.create(
            family=self.family,
            name="Target",
            relation="Other",
            gender="M",
            created_by=self.guardian,
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.other_member.id}/link-existing/',
            {
                "target_member_id": target.id,
                "relation_type": "SIBLING",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 403)

    def test_link_existing_rejects_self_link(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/link-existing/',
            {
                "target_member_id": self.guardian_member.id,
                "relation_type": "SIBLING",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('cannot link a member to itself', str(res.data.get('error', '')).lower())

    def test_link_existing_rejects_second_father(self):
        father_one = FamilyMember.objects.create(
            family=self.family,
            name="Father One",
            relation="Father",
            gender="M",
            created_by=self.guardian,
        )
        father_two = FamilyMember.objects.create(
            family=self.family,
            name="Father Two",
            relation="Father",
            gender="M",
            created_by=self.other_user,
        )
        self.guardian_member.parents.add(father_one)
        Relationship.objects.create(
            from_member=self.guardian_member,
            to_member=father_one,
            relation_type='PARENT',
        )

        self.client.force_authenticate(user=self.guardian)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/link-existing/',
            {
                "target_member_id": father_two.id,
                "relation_type": "PARENT",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('already has a father', str(res.data.get('error', '')).lower())

    def test_claimed_relative_can_manage_spouse_and_descendants(self):
        child = FamilyMember.objects.create(
            family=self.family,
            name="Claimed Child",
            relation="Son",
            gender="M",
            created_by=self.guardian,
            is_independent=False,
        )
        spouse = FamilyMember.objects.create(
            family=self.family,
            name="Claimed Spouse",
            relation="Spouse",
            gender="F",
            created_by=self.guardian,
            is_independent=False,
        )
        grandchild = FamilyMember.objects.create(
            family=self.family,
            name="Claimed Grandchild",
            relation="Daughter",
            gender="F",
            created_by=self.guardian,
            is_independent=False,
        )

        self.guardian_member.parents.clear()
        child.parents.add(self.guardian_member)
        grandchild.parents.add(child)

        Relationship.objects.create(from_member=self.guardian_member, to_member=child, relation_type='CHILD')
        Relationship.objects.create(from_member=child, to_member=self.guardian_member, relation_type='PARENT')
        Relationship.objects.create(from_member=child, to_member=spouse, relation_type='SPOUSE')
        Relationship.objects.create(from_member=spouse, to_member=child, relation_type='SPOUSE')
        Relationship.objects.create(from_member=child, to_member=grandchild, relation_type='CHILD')
        Relationship.objects.create(from_member=grandchild, to_member=child, relation_type='PARENT')

        claimed_user = User.objects.create_user(
            username="claimed_child_user",
            email="claimed_child_user@example.com",
            password="Pass123!",
            member=child,
        )

        self.client.force_authenticate(user=claimed_user)

        add_res = self.client.post(
            f'/api/families/tree-edit/{spouse.id}/add-relative/',
            {
                "name": "Descendant Via Spouse",
                "relation_type": "CHILD",
                "gender": "M",
            },
            format='json',
        )
        self.assertEqual(add_res.status_code, 201)

        remove_res = self.client.delete(f'/api/families/tree-edit/{grandchild.id}/remove/')
        self.assertEqual(remove_res.status_code, 204)

    def test_claimed_relative_can_manage_spouse_with_account(self):
        child = FamilyMember.objects.create(
            family=self.family,
            name="Claimed Child",
            relation="Son",
            gender="M",
            created_by=self.guardian,
            is_independent=False,
        )
        spouse = FamilyMember.objects.create(
            family=self.family,
            name="Spouse With Account",
            relation="Spouse",
            gender="F",
            created_by=self.guardian,
            is_independent=False,
        )

        Relationship.objects.create(from_member=child, to_member=spouse, relation_type='SPOUSE')
        Relationship.objects.create(from_member=spouse, to_member=child, relation_type='SPOUSE')

        claimed_user = User.objects.create_user(
            username="claimed_child_branch_mgr",
            email="claimed_child_branch_mgr@example.com",
            password="Pass123!",
            member=child,
        )
        User.objects.create_user(
            username="spouse_owned_account",
            email="spouse_owned_account@example.com",
            password="Pass123!",
            member=spouse,
        )

        self.client.force_authenticate(user=claimed_user)
        add_res = self.client.post(
            f'/api/families/tree-edit/{spouse.id}/add-relative/',
            {
                "name": "Child Through Accounted Spouse",
                "relation_type": "CHILD",
                "gender": "M",
            },
            format='json',
        )
        self.assertEqual(add_res.status_code, 201)

    def test_claimed_relative_cannot_manage_parent_branch(self):
        child = FamilyMember.objects.create(
            family=self.family,
            name="Claimed Child",
            relation="Son",
            gender="M",
            created_by=self.guardian,
            is_independent=False,
        )
        Relationship.objects.create(from_member=self.guardian_member, to_member=child, relation_type='CHILD')
        Relationship.objects.create(from_member=child, to_member=self.guardian_member, relation_type='PARENT')
        child.parents.add(self.guardian_member)

        claimed_user = User.objects.create_user(
            username="claimed_child_forbidden",
            email="claimed_child_forbidden@example.com",
            password="Pass123!",
            member=child,
        )

        self.client.force_authenticate(user=claimed_user)
        res = self.client.post(
            f'/api/families/tree-edit/{self.guardian_member.id}/add-relative/',
            {
                "name": "Should Be Forbidden",
                "relation_type": "SIBLING",
            },
            format='json',
        )
        self.assertEqual(res.status_code, 403)
