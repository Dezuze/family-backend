"""
Families App Views
==================
REST API endpoints for managing family members, the interactive family tree,
media galleries, and member relationships.

Key Views:
    - UserProfileView: CRUD for the authenticated user's own profile.
    - FamilyTreeView: Builds hierarchical tree data (nodes + links) from
      Relationship records, chaining all relation types into a renderable
      parent/spouse graph for the D3.js frontend.
    - ManagedMembersView: List/create members managed by the current user.
    - FamilyMembersCRUD: Generic detail view for a single member.
    - FamilyMediaCRUD: Gallery list/create and detail endpoints.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FamilyMember, FamilyMedia, Family, Relationship
from .serializers import FamilyMemberSerializer, FamilyTreeSerializer, FamilyMediaSerializer
from .permissions import IsGuardianOrSelf
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date
from .relationship_engine import BASE_RELATIONS, RelationshipEngine


def _normalize_relation_label(value, fallback='Other', max_len=50):
    label = str(value or '').strip()
    if not label:
        return fallback
    return label[:max_len]


def _storable_member_relation(value):
    relation = _normalize_relation_label(value)
    known_member_relations = {choice[0] for choice in FamilyMember.RELATION_CHOICES}
    if relation in known_member_relations:
        return relation
    return 'Other'


def _normalize_user_relation_or_error(value):
    relation = _normalize_relation_label(value, fallback='')
    canonical = RelationshipEngine.canonicalize_input(relation)
    if canonical:
        return canonical

    if RelationshipEngine.is_banned_label(relation):
        raise ValueError('Only parent, child, spouse, or sibling can be defined directly.')

    if relation:
        raise ValueError('Unsupported relationship. Use parent, child, spouse, or sibling only.')
    raise ValueError('Relationship is required and must be parent, child, spouse, or sibling.')


def _safe_create_base_relationship(from_member, to_member, relation_type):
    if relation_type not in BASE_RELATIONS:
        return
    if from_member.id == to_member.id:
        return
    try:
        obj, created = Relationship.objects.get_or_create(
            from_member=from_member,
            to_member=to_member,
            relation_type=relation_type,
        )
        if created:
            obj.full_clean()
    except Exception:
        # If validation fails, the relationship already exists in reverse
        pass


def _parse_iso_date(value):
    if isinstance(value, date):
        return value
    text = str(value or '').strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _parse_optional_date_or_error(value, label='date'):
    if value in (None, ''):
        return None
    parsed = _parse_iso_date(value)
    if not parsed:
        raise ValueError(f'Invalid {label} format. Use YYYY-MM-DD.')
    return parsed


def _normalize_committee_role_or_error(value):
    role = ' '.join(str(value or '').strip().split())
    if not role:
        return None

    from profiles.models import CommunityRole

    matched = CommunityRole.objects.filter(
        is_active=True,
        name__iexact=role,
    ).values_list('name', flat=True).first()
    if matched:
        return matched
    raise ValueError('Invalid community role. Select one of the predefined roles.')


def _calculate_age(dob_value, end_value=None):
    dob = _parse_iso_date(dob_value)
    if not dob:
        return None

    end_date = _parse_iso_date(end_value) or date.today()
    if end_date < dob:
        return None

    years = end_date.year - dob.year - ((end_date.month, end_date.day) < (dob.month, dob.day))
    return years if years >= 0 else None

class UserProfileView(APIView):
    """
    GET  /api/families/profile/  → Return the authenticated user's FamilyMember.
    POST /api/families/profile/  → Create or update the user's profile,
         including demographics, photo, parents (M2M), and relationships.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        member = FamilyMember.objects.filter(user_account=request.user).first()
        if member:
            serializer = FamilyMemberSerializer(member, context={'request': request})
            return Response(serializer.data)
        return Response({"error": "Profile not linked"}, status=404)

    def post(self, request):
        try:
            data = request.data
            user = request.user
            
            # Check if member exists via OneToOne relationship
            member = getattr(user, 'member', None)
            
            if not member:
                 # Create new member if not exists - needs a family
                 family = Family.objects.first()
                 if not family:
                     # Fallback: Create a default family if none exists
                     family = Family.objects.create(
                         sl_no="1",
                         branch="Main Branch",
                         member_no="KFA-0001"
                     )
                 
                 dob = data.get('date_of_birth')
                 if not dob:
                     return Response({"error": "Date of birth is required for new profile."}, status=400)
                 
                 dob_date = _parse_iso_date(dob)
                 if not dob_date:
                     return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

                 is_deceased_flag = data.get('is_deceased', 'false') in (True, 'true', 'True', '1', 1)
                 death_input = data.get('date_of_death') if is_deceased_flag else None
                 if death_input and not _parse_iso_date(death_input):
                     return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
                 death_date = _parse_iso_date(death_input) if is_deceased_flag else None
                 calculated_age = _calculate_age(dob_date, death_date)

                 try:
                     committee_role_value = _normalize_committee_role_or_error(data.get('committee_role'))
                 except ValueError as e:
                     return Response({"error": str(e)}, status=400)

                 requested_member_id = (data.get('member_id') or '').strip()
                 if requested_member_id and FamilyMember.objects.filter(member_id=requested_member_id).exists():
                     return Response({"error": "Member ID already exists."}, status=400)

                 member = FamilyMember.objects.create(
                     family=family,
                     name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or user.username,
                     member_id=requested_member_id or None,
                     age=calculated_age,
                     date_of_birth=dob_date,
                     date_of_death=death_date,
                     is_deceased=is_deceased_flag,
                     blood_group=data.get('blood_group', 'Unknown'),
                     committee_role=committee_role_value,
                     relation='Member'
                 )
                 # Link user to member (since User.member is the field)
                 user.member = member
                 user.save()

            # Update Fields
            if 'first_name' in data or 'last_name' in data:
                f_name = data.get('first_name', '')
                l_name = data.get('last_name', '')
                member.name = f"{f_name} {l_name}".strip()
            elif 'name' in data:
                member.name = data['name']
            
            if 'nickname' in data: member.nickname = data['nickname']
            if 'gender' in data: member.gender = data['gender']
            if 'bio' in data: member.bio = data['bio']
            if 'phone_no' in data: member.phone_no = data['phone_no']
            if 'email_id' in data: member.email_id = data['email_id']
            if 'church_parish' in data: member.church_parish = data['church_parish']
            if 'committee_role' in data:
                try:
                    member.committee_role = _normalize_committee_role_or_error(data.get('committee_role'))
                except ValueError as e:
                    return Response({"error": str(e)}, status=400)
            if 'member_id' in data:
                requested_member_id = (data.get('member_id') or '').strip()
                if requested_member_id and FamilyMember.objects.filter(member_id=requested_member_id).exclude(pk=member.pk).exists():
                    return Response({"error": "Member ID already exists."}, status=400)
                member.member_id = requested_member_id or None
            
            if 'date_of_birth' in data:
                dob_input = data.get('date_of_birth') or None
                if dob_input and not _parse_iso_date(dob_input):
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
                member.date_of_birth = dob_input

            if 'education' in data: member.education = data['education']
            if 'occupation' in data: member.occupation = data['occupation']
            if 'place_of_work' in data: member.place_of_work = data['place_of_work']
            if 'blood_group' in data: member.blood_group = data['blood_group']
            if 'is_deceased' in data: member.is_deceased = data['is_deceased'] == 'true' or data['is_deceased'] == True
            if 'date_of_death' in data:
                death_input = data.get('date_of_death') or None
                if death_input and not _parse_iso_date(death_input):
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
                member.date_of_death = death_input
            elif not member.is_deceased:
                member.date_of_death = None

            computed_age = _calculate_age(
                member.date_of_birth,
                member.date_of_death if member.is_deceased else None,
            )
            if computed_age is not None:
                member.age = computed_age
            elif 'age' in data:
                member.age = data.get('age') or None
            if 'address' in data: member.address_if_different = data['address']
            elif 'address_if_different' in data: member.address_if_different = data['address_if_different']
            
            # Update Parents (ManyToMany)
            if 'parents' in data:
                # Handle FormData getlist or JSON list
                if hasattr(data, 'getlist'):
                    parent_ids = data.getlist('parents')
                else:
                    parent_ids = data['parents']
                
                if isinstance(parent_ids, str):
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                
                member.parents.set(parent_ids)
            
            # Update Relationships
            if 'relationships' in data:
                import json
                try:
                    rel_data = data['relationships']
                    if isinstance(rel_data, str):
                        rel_data = json.loads(rel_data)
                    
                    # Clear existing and re-add? Or just add new ones?
                    # For onboarding, clearing might be cleaner
                    Relationship.objects.filter(from_member=member).delete()
                    for item in rel_data:
                        to_id = item.get('to_member') or item.get('to_member_id')
                        rel_type = _normalize_user_relation_or_error(item.get('relation_type'))
                        name = item.get('name') or item.get('to_member_name')
                        
                        if not to_id and name:
                            # Auto-create unlinked member and connect using base relation.
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation='Other',
                                gender='M',
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id

                        if to_id and rel_type:
                            target = FamilyMember.objects.filter(id=to_id).first()
                            if target:
                                _safe_create_base_relationship(member, target, rel_type)
                                if rel_type == 'PARENT':
                                    member.parents.add(target)
                                elif rel_type == 'CHILD':
                                    target.parents.add(member)
                except Exception as e:
                    return Response({"error": str(e)}, status=400)

            # Update Profile Pic
            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            elif 'photo' in request.FILES:
                member.photo = request.FILES['photo']
            
            member.save()
            
            return Response(FamilyMemberSerializer(member, context={'request': request}).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc() # Print to server logs for debugging
            return Response({"error": str(e)}, status=500)


class FamilyTreeView(APIView):
    """
    GET /api/families/tree/  → Return { nodes, links } for the D3 tree.

    Link generation algorithm:
        1. Collect all FamilyMembers as nodes.
        2. Convert each Relationship into the correct link type:
           - Father/Mother       → parent link (to_member is parent of from_member)
           - Son/Daughter         → parent link (from_member is parent of to_member)
           - Grandparent variants → chain through Father/Mother as intermediate
           - Siblings             → share parent (both become children of Father)
           - Uncle/Aunt           → child of grandparent (father's sibling)
           - Cousin               → child of uncle/aunt
           - In-laws              → spouse of sibling or parent of spouse
           - Father/Mother-in-law → parent of the user's spouse
           - Nephew/Niece         → child of sibling
        3. Auto-detect co-parents (two parents sharing a child) and add
           spouse links between them.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        viewer_member = getattr(request.user, 'member', None) if getattr(request.user, 'is_authenticated', False) else None

        members_qs = FamilyMember.objects.all().prefetch_related('parents')
        if viewer_member and viewer_member.family_id:
            members_qs = members_qs.filter(family_id=viewer_member.family_id)

        member_ids = list(members_qs.values_list('id', flat=True))
        relationships = Relationship.objects.filter(
            from_member_id__in=member_ids,
            to_member_id__in=member_ids,
        )

        members = members_qs
        engine = RelationshipEngine(members=members, relationships=relationships)
        payload = engine.build_payload(root_id=getattr(viewer_member, 'id', None))

        return Response(
            {
                "nodes": payload.nodes,
                "edges": payload.edges,
                "computed_relations": payload.computed_relations,
                "generation_depth": payload.generation_depth,
            }
        )


class FamilyMediaList(generics.ListCreateAPIView):
    queryset = FamilyMedia.objects.all()
    serializer_class = FamilyMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class FamilyMediaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FamilyMedia.objects.all()
    serializer_class = FamilyMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

def _create_auto_relationship(member, creator_member, relation_override=None):
    if not creator_member:
        return

    relation_label = relation_override if relation_override is not None else member.relation
    relation = _normalize_user_relation_or_error(relation_label)

    Relationship.objects.filter(
        Q(from_member=member, to_member=creator_member) |
        Q(from_member=creator_member, to_member=member)
    ).exclude(relation_type__in=BASE_RELATIONS).delete()

    member.parents.remove(creator_member)
    creator_member.parents.remove(member)

    if relation == 'PARENT':
        _safe_create_base_relationship(member, creator_member, 'PARENT')
        creator_member.parents.add(member)
    elif relation == 'CHILD':
        _safe_create_base_relationship(member, creator_member, 'CHILD')
        member.parents.add(creator_member)
    elif relation == 'SPOUSE':
        _safe_create_base_relationship(member, creator_member, 'SPOUSE')
        _safe_create_base_relationship(creator_member, member, 'SPOUSE')
    elif relation == 'SIBLING':
        _safe_create_base_relationship(member, creator_member, 'SIBLING')
        _safe_create_base_relationship(creator_member, member, 'SIBLING')
        for parent in creator_member.parents.all():
            member.parents.add(parent)
            _safe_create_base_relationship(member, parent, 'PARENT')


def _member_has_account(member):
    return hasattr(member, 'user_account') and member.user_account is not None


def _member_spouse_ids(member_id):
    spouse_qs = Relationship.objects.filter(relation_type='SPOUSE').filter(
        Q(from_member_id=member_id) | Q(to_member_id=member_id)
    )
    spouse_ids = set()
    for rel in spouse_qs:
        if rel.from_member_id == member_id:
            spouse_ids.add(rel.to_member_id)
        else:
            spouse_ids.add(rel.from_member_id)
    return spouse_ids


def _member_child_ids(member_id):
    child_ids = set(
        Relationship.objects.filter(
            relation_type='CHILD',
            from_member_id=member_id,
        ).values_list('to_member_id', flat=True)
    )
    child_ids.update(
        Relationship.objects.filter(
            relation_type='PARENT',
            to_member_id=member_id,
        ).values_list('from_member_id', flat=True)
    )
    child_ids.update(
        FamilyMember.objects.filter(parents__id=member_id).values_list('id', flat=True)
    )
    child_ids.discard(member_id)
    return child_ids


def _managed_branch_ids(user):
    root_member = getattr(user, 'member', None)
    if not root_member:
        return set()

    managed_ids = {root_member.id}
    queue = [root_member.id]
    seen = set()

    while queue:
        current_id = queue.pop(0)
        if current_id in seen:
            continue
        seen.add(current_id)

        for spouse_id in _member_spouse_ids(current_id):
            if spouse_id not in managed_ids:
                managed_ids.add(spouse_id)
                queue.append(spouse_id)

        for child_id in _member_child_ids(current_id):
            if child_id not in managed_ids:
                managed_ids.add(child_id)
                queue.append(child_id)

    return managed_ids


def _can_manage_member(user, member):
    if not getattr(user, 'is_authenticated', False):
        return False

    if _member_has_account(member) and member.user_account == user:
        return True

    managed_branch_ids = _managed_branch_ids(user)
    if member.id in managed_branch_ids:
        if member.is_independent and member.user_account != user:
            return False
        return True

    if member.created_by == user and not member.is_independent and not _member_has_account(member):
        return True
    return False


def _normalized_gender(value, default='M'):
    gender = (value or default or 'O').strip().upper()
    if gender not in {'M', 'F', 'O'}:
        return 'O'
    return gender


def _get_member_parent_queryset(member):
    parent_ids = set(member.parents.values_list('id', flat=True))
    parent_ids.update(
        Relationship.objects.filter(from_member=member, relation_type='PARENT').values_list('to_member_id', flat=True)
    )
    return FamilyMember.objects.filter(id__in=parent_ids)


def _validate_relation_constraints(member, relation, requested_gender='O', target_member=None):
    if relation == 'SPOUSE':
        spouse_links = Relationship.objects.filter(relation_type='SPOUSE').filter(
            Q(from_member=member) | Q(to_member=member)
        )
        if target_member and spouse_links.filter(Q(from_member=target_member) | Q(to_member=target_member)).exists():
            return "These members are already linked as spouse."
        if spouse_links.exists():
            return "This member already has a spouse linked in the tree."

    if relation == 'PARENT':
        existing_parents = _get_member_parent_queryset(member)
        if target_member and existing_parents.filter(id=target_member.id).exists():
            return "These members are already linked as parent."

        if existing_parents.count() >= 2:
            return "This member already has two parents linked in the tree."

        if requested_gender in {'M', 'F'} and existing_parents.filter(gender=requested_gender).exists():
            parent_label = 'father' if requested_gender == 'M' else 'mother'
            return f"This member already has a {parent_label} linked in the tree."

    return None


def _apply_relation_link(anchor_member, target_member, relation, anniversary_date=None):
    if relation == 'PARENT':
        _safe_create_base_relationship(anchor_member, target_member, 'PARENT')
        anchor_member.parents.add(target_member)
    elif relation == 'CHILD':
        _safe_create_base_relationship(anchor_member, target_member, 'CHILD')
        target_member.parents.add(anchor_member)
    elif relation == 'SPOUSE':
        # Only create relationship in one direction (canonical: min_id -> max_id)
        # to prevent bidirectional duplicates
        if anchor_member.id < target_member.id:
            _safe_create_base_relationship(anchor_member, target_member, 'SPOUSE')
            Relationship.objects.filter(
                from_member=anchor_member,
                to_member=target_member,
                relation_type='SPOUSE',
            ).update(anniversary_date=anniversary_date)
        else:
            _safe_create_base_relationship(target_member, anchor_member, 'SPOUSE')
            Relationship.objects.filter(
                from_member=target_member,
                to_member=anchor_member,
                relation_type='SPOUSE',
            ).update(anniversary_date=anniversary_date)
    elif relation == 'SIBLING':
        _safe_create_base_relationship(anchor_member, target_member, 'SIBLING')
        _safe_create_base_relationship(target_member, anchor_member, 'SIBLING')
        for parent in anchor_member.parents.all():
            target_member.parents.add(parent)
            _safe_create_base_relationship(target_member, parent, 'PARENT')


class FamilyMemberContextView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        member = get_object_or_404(FamilyMember.objects.prefetch_related('parents', 'children'), pk=pk)

        can_manage = _can_manage_member(request.user, member)
        has_account = _member_has_account(member)

        parents = list(member.parents.all())
        siblings = (
            FamilyMember.objects.filter(parents__in=parents)
            .exclude(id=member.id)
            .distinct()
            if parents
            else FamilyMember.objects.none()
        )
        children = member.children.all()

        return Response(
            {
                "member": FamilyMemberSerializer(member, context={'request': request}).data,
                "parents": FamilyMemberSerializer(parents, many=True, context={'request': request}).data,
                "siblings": FamilyMemberSerializer(siblings, many=True, context={'request': request}).data,
                "children": FamilyMemberSerializer(children, many=True, context={'request': request}).data,
                "allowed_actions": {
                    "can_manage": can_manage,
                    "can_add_parent": can_manage,
                    "can_add_spouse": can_manage,
                    "can_add_sibling": can_manage,
                    "can_add_child": can_manage,
                    "can_remove": can_manage,
                },
                "ownership_status": {
                    "is_independent": member.is_independent,
                    "has_account": has_account,
                    "created_by_me": member.created_by_id == request.user.id,
                    "is_self": has_account and member.user_account == request.user,
                },
            }
        )


class FamilyMemberSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = (request.query_params.get('q') or '').strip()
        exclude_id = request.query_params.get('exclude_id')

        members = FamilyMember.objects.all().order_by('name')
        if query:
            members = members.filter(name__icontains=query)

        if exclude_id:
            try:
                members = members.exclude(id=int(exclude_id))
            except (TypeError, ValueError):
                pass

        members = members[:20]
        payload = []
        for member in members:
            payload.append(
                {
                    "id": member.id,
                    "name": member.name,
                    "gender": member.gender,
                    "relation": member.relation,
                    "age": member.age,
                    "photo": member.photo.url if member.photo else None,
                }
            )

        return Response({"results": payload})


class FamilyTreeAddRelativeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        member = get_object_or_404(FamilyMember.objects.prefetch_related('parents', 'children'), pk=pk)
        if not _can_manage_member(request.user, member):
            return Response({"error": "You do not have permission to edit this member."}, status=403)

        data = request.data
        relation = _normalize_user_relation_or_error(data.get('relation_type') or data.get('relation'))
        requested_gender = _normalized_gender(data.get('gender'))
        if relation not in BASE_RELATIONS:
            return Response({"error": "Unsupported relation type."}, status=400)

        constraint_error = _validate_relation_constraints(member, relation, requested_gender=requested_gender)
        if constraint_error:
            return Response({"error": constraint_error}, status=400)

        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        full_name = (data.get('name') or f"{first_name} {last_name}".strip()).strip()
        if not full_name:
            return Response({"error": "Member name is required."}, status=400)

        requested_member_id = (data.get('member_id') or '').strip()
        if requested_member_id and FamilyMember.objects.filter(member_id=requested_member_id).exists():
            return Response({"error": "Member ID already exists."}, status=400)

        is_deceased_flag = data.get('is_deceased', 'false') in (True, 'true', 'True', '1', 1)
        dob_input = data.get('date_of_birth') or None
        death_input = data.get('date_of_death') or None
        if dob_input and not _parse_iso_date(dob_input):
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        if death_input and not _parse_iso_date(death_input):
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        computed_age = _calculate_age(dob_input, death_input if is_deceased_flag else None)
        manual_age = data.get('age') if data.get('age') not in ('', None) else None

        try:
            committee_role_value = _normalize_committee_role_or_error(data.get('committee_role'))
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        new_member = FamilyMember.objects.create(
            family=member.family,
            name=full_name,
            member_id=requested_member_id or None,
            nickname=data.get('nickname', ''),
            age=computed_age if computed_age is not None else manual_age,
            gender=requested_gender,
            relation='Other',
            date_of_birth=dob_input,
            date_of_death=death_input if is_deceased_flag else None,
            blood_group=data.get('blood_group') or None,
            is_deceased=is_deceased_flag,
            occupation=data.get('occupation') or None,
            education=data.get('education') or None,
            phone_no=data.get('phone_no') or None,
            email_id=data.get('email_id') or None,
            address_if_different=data.get('address') or data.get('address_if_different') or None,
            bio=data.get('bio') or None,
            church_parish=data.get('church_parish') or None,
            committee_role=committee_role_value,
            created_by=request.user,
        )

        try:
            anniversary_date = _parse_optional_date_or_error(data.get('anniversary_date'), label='anniversary_date')
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        _apply_relation_link(member, new_member, relation, anniversary_date=anniversary_date)

        if 'profile_pic' in request.FILES:
            new_member.photo = request.FILES['profile_pic']
            new_member.save(update_fields=['photo'])

        return Response(
            {
                "member": FamilyMemberSerializer(new_member, context={'request': request}).data,
                "anchor_member_id": member.id,
                "relation_type": relation,
            },
            status=status.HTTP_201_CREATED,
        )


class FamilyTreeLinkExistingMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        member = get_object_or_404(FamilyMember.objects.prefetch_related('parents', 'children'), pk=pk)
        if not _can_manage_member(request.user, member):
            return Response({"error": "You do not have permission to edit this member."}, status=403)

        data = request.data
        relation = _normalize_user_relation_or_error(data.get('relation_type') or data.get('relation'))
        if relation not in BASE_RELATIONS:
            return Response({"error": "Unsupported relation type."}, status=400)

        target_member_id = data.get('target_member_id')
        try:
            target_member_id = int(target_member_id)
        except (TypeError, ValueError):
            return Response({"error": "Valid target_member_id is required."}, status=400)

        target_member = get_object_or_404(FamilyMember, pk=target_member_id)
        if target_member.id == member.id:
            return Response({"error": "Cannot link a member to itself."}, status=400)

        requested_gender = _normalized_gender(target_member.gender, default='O')
        constraint_error = _validate_relation_constraints(
            member,
            relation,
            requested_gender=requested_gender,
            target_member=target_member,
        )
        if constraint_error:
            return Response({"error": constraint_error}, status=400)

        try:
            anniversary_date = _parse_optional_date_or_error(data.get('anniversary_date'), label='anniversary_date')
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        _apply_relation_link(member, target_member, relation, anniversary_date=anniversary_date)

        return Response(
            {
                "member": FamilyMemberSerializer(target_member, context={'request': request}).data,
                "anchor_member_id": member.id,
                "relation_type": relation,
                "linked_existing": True,
            },
            status=status.HTTP_200_OK,
        )


class FamilyTreeRemoveMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        member = get_object_or_404(FamilyMember, pk=pk)
        if not _can_manage_member(request.user, member):
            return Response({"error": "You do not have permission to remove this member."}, status=403)

        if _member_has_account(member) and member.user_account == request.user:
            return Response({"error": "You cannot remove your own account member."}, status=400)

        if _member_has_account(member) and member.user_account != request.user:
            return Response({"error": "This member has a user account and cannot be removed by guardian."}, status=403)

        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagedMembersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # List all members created by this user that are NOT independent
        members = FamilyMember.objects.filter(created_by=request.user, is_independent=False)
        serializer = FamilyMemberSerializer(members, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        # Create a new member managed by this user
        try:
            data = request.data
            from .models import Family

            creator_member = getattr(request.user, 'member', None)
            family = creator_member.family if creator_member and creator_member.family_id else Family.objects.first()
            if not family:
                return Response({"error": "No family found"}, status=400)

            # Extract fields
            f_name = data.get('first_name', '')
            l_name = data.get('last_name', '')
            full_name = data.get('name', f"{f_name} {l_name}".strip())
            relation_label = _normalize_user_relation_or_error(data.get('relation', 'child'))
            requested_member_id = (data.get('member_id') or '').strip()

            if requested_member_id and FamilyMember.objects.filter(member_id=requested_member_id).exists():
                return Response({"error": "Member ID already exists."}, status=400)

            is_deceased_flag = data.get('is_deceased', 'false') == 'true' or data.get('is_deceased') == True
            dob_input = data.get('date_of_birth') or None
            death_input = data.get('date_of_death') or None
            if dob_input and not _parse_iso_date(dob_input):
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
            if death_input and not _parse_iso_date(death_input):
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            computed_age = _calculate_age(dob_input, death_input if is_deceased_flag else None)
            manual_age = data.get('age') if data.get('age') not in ('', None) else None

            try:
                committee_role_value = _normalize_committee_role_or_error(data.get('committee_role'))
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

            member = FamilyMember.objects.create(
                family=family,
                name=full_name,
                member_id=requested_member_id or None,
                age=computed_age if computed_age is not None else manual_age,
                gender=data.get('gender', 'M'),
                relation='Other',
                date_of_birth=dob_input,
                date_of_death=death_input if is_deceased_flag else None,
                blood_group=data.get('blood_group', 'Unknown'),
                occupation=data.get('occupation', ''),
                education=data.get('education', ''),
                place_of_work=data.get('place_of_work', ''),
                is_deceased=is_deceased_flag,
                phone_no=data.get('phone_no', ''),
                email_id=data.get('email_id', ''),
                address_if_different=data.get('address', ''),
                bio=data.get('bio', ''),
                church_parish=data.get('church_parish', ''),
                committee_role=committee_role_value,
                nickname=data.get('nickname', ''),
                created_by=request.user
            )

            # Auto-create reciprocal Relationship based on relation field
            if creator_member:
                _create_auto_relationship(member, creator_member, relation_override=relation_label)

            # Link parents if provided
            if 'parents' in data:
                if hasattr(data, 'getlist'):
                    parent_ids = data.getlist('parents')
                else:
                    parent_ids = data['parents']
                
                if isinstance(parent_ids, str):
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                member.parents.set(parent_ids)

            # Relationships
            if 'relationships' in data:
                import json
                try:
                    rel_data = data['relationships']
                    if isinstance(rel_data, str):
                        rel_data = json.loads(rel_data)
                    for item in rel_data:
                        to_id = item.get('to_member') or item.get('to_member_id')
                        rel_type = _normalize_user_relation_or_error(item.get('relation_type'))
                        name = item.get('name') or item.get('to_member_name')

                        if not to_id and name:
                            # Auto-create member if not found
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation='Other',
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id

                        if to_id and rel_type:
                            target = FamilyMember.objects.filter(id=to_id).first()
                            if target:
                                _safe_create_base_relationship(member, target, rel_type)
                                if rel_type == 'PARENT':
                                    member.parents.add(target)
                                elif rel_type == 'CHILD':
                                    target.parents.add(member)
                except Exception as e:
                    return Response({"error": str(e)}, status=400)

            # Profile Pic
            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            elif 'photo' in request.FILES:
                member.photo = request.FILES['photo']
            
            member.save()

            return Response(FamilyMemberSerializer(member, context={'request': request}).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ManagedMemberDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        member = get_object_or_404(FamilyMember, pk=pk, created_by=user)
        # Enforce guardian permission: can only edit if not independent
        if member.is_independent:
            return None
        return member

    def get(self, request, pk):
        member = get_object_or_404(FamilyMember, pk=pk, created_by=request.user)
        return Response(FamilyMemberSerializer(member, context={'request': request}).data)

    def put(self, request, pk):
        member = self.get_object(pk, request.user)
        if member is None:
            return Response({"error": "This profile is independent and cannot be edited by the guardian."}, status=403)
        # Prevent editing if the member has their own account now?
        # The user said "if there isnt an account for them".
        if hasattr(member, 'user_account') and member.user_account:
             return Response({"error": "Member has their own account and cannot be managed by others."}, status=403)

        try:
            data = request.data
            
            f_name = data.get('first_name')
            l_name = data.get('last_name')
            if f_name is not None or l_name is not None:
                member.name = f"{f_name or ''} {l_name or ''}".strip()
            elif 'name' in data:
                member.name = data['name']

            if 'age' in data: member.age = data['age']
            if 'gender' in data: member.gender = data['gender']
            if 'relation' in data:
                input_relation = _normalize_user_relation_or_error(data['relation'])
                member.relation = 'Other'
                # Re-create auto-relationship when relation changes
                member.save()  # Save relation first
                creator_member = getattr(request.user, 'member', None)
                if creator_member:
                    _create_auto_relationship(member, creator_member, relation_override=input_relation)
            if 'date_of_birth' in data:
                dob_input = data.get('date_of_birth') or None
                if dob_input and not _parse_iso_date(dob_input):
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
                member.date_of_birth = dob_input
            if 'blood_group' in data: member.blood_group = data['blood_group']
            if 'occupation' in data: member.occupation = data['occupation']
            if 'place_of_work' in data: member.place_of_work = data['place_of_work']
            if 'education' in data: member.education = data['education']
            if 'phone_no' in data: member.phone_no = data['phone_no']
            if 'email_id' in data: member.email_id = data['email_id']
            if 'is_deceased' in data: member.is_deceased = data['is_deceased'] == 'true' or data['is_deceased'] == True
            if 'date_of_death' in data:
                death_input = data.get('date_of_death') or None
                if death_input and not _parse_iso_date(death_input):
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
                member.date_of_death = death_input
            elif not member.is_deceased:
                member.date_of_death = None

            computed_age = _calculate_age(
                member.date_of_birth,
                member.date_of_death if member.is_deceased else None,
            )
            if computed_age is not None:
                member.age = computed_age
            elif 'age' in data:
                member.age = data.get('age') or None
            if 'address' in data: member.address_if_different = data['address']
            if 'bio' in data: member.bio = data['bio']
            if 'nickname' in data: member.nickname = data['nickname']
            if 'name_ml' in data: member.name_ml = (data.get('name_ml') or '').strip() or None
            if 'church_parish' in data: member.church_parish = data['church_parish']
            if 'committee_role' in data:
                try:
                    member.committee_role = _normalize_committee_role_or_error(data.get('committee_role'))
                except ValueError as e:
                    return Response({"error": str(e)}, status=400)
            if 'wedding_anniversary' in data:
                anniv_input = data.get('wedding_anniversary') or None
                if anniv_input and not _parse_iso_date(anniv_input):
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
                member.wedding_anniversary = anniv_input
            if 'member_id' in data:
                requested_member_id = (data.get('member_id') or '').strip()
                if requested_member_id and FamilyMember.objects.filter(member_id=requested_member_id).exclude(pk=member.pk).exists():
                    return Response({"error": "Member ID already exists."}, status=400)
                member.member_id = requested_member_id or None

            # Relationships
            if 'relationships' in data:
                import json
                try:
                    rel_data = data['relationships']
                    if isinstance(rel_data, str):
                        rel_data = json.loads(rel_data)
                    
                    Relationship.objects.filter(from_member=member).delete()
                    for item in rel_data:
                        to_id = item.get('to_member') or item.get('to_member_id')
                        rel_type = _normalize_user_relation_or_error(item.get('relation_type'))
                        name = item.get('name') or item.get('to_member_name')

                        if not to_id and name:
                            # Auto-create member if not found
                            new_member = FamilyMember.objects.create(
                                name=name,
                                relation='Other',
                                age=0, 
                                created_by=request.user,
                                family=member.family
                            )
                            to_id = new_member.id

                        if to_id and rel_type:
                            target = FamilyMember.objects.filter(id=to_id).first()
                            if target:
                                _safe_create_base_relationship(member, target, rel_type)
                                if rel_type == 'PARENT':
                                    member.parents.add(target)
                                elif rel_type == 'CHILD':
                                    target.parents.add(member)
                except Exception as e:
                    return Response({"error": str(e)}, status=400)

            if 'parents' in data:
                if hasattr(data, 'getlist'):
                    parent_ids = data.getlist('parents')
                else:
                    parent_ids = data['parents']
                
                if isinstance(parent_ids, str):
                    parent_ids = [p.strip() for p in parent_ids.split(',')]
                member.parents.set(parent_ids)

            if 'profile_pic' in request.FILES:
                member.photo = request.FILES['profile_pic']
            elif 'photo' in request.FILES:
                member.photo = request.FILES['photo']

            member.save()
            return Response(FamilyMemberSerializer(member, context={'request': request}).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def delete(self, request, pk):
        member = self.get_object(pk, request.user)
        if member is None:
            return Response({"error": "This profile is independent and cannot be deleted by the guardian."}, status=403)
        if hasattr(member, 'user_account') and member.user_account:
             return Response({"error": "Member has their own account and cannot be deleted by others."}, status=403)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
