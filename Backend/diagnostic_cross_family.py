#!/usr/bin/env python
"""
Diagnostic script to find why specific members are in wrong family trees.
Run this in Django shell or as a management command.
"""

from families.models import FamilyMember, Relationship


def find_member_by_name(name: str):
    """Find members by partial name match."""
    return FamilyMember.objects.filter(name__icontains=name)


def diagnose_member(member_id: int):
    """Diagnose why a member appears in wrong family tree."""
    try:
        member = FamilyMember.objects.get(id=member_id)
    except FamilyMember.DoesNotExist:
        print(f"Member {member_id} not found")
        return

    print(f"\n{'='*60}")
    print(f"Diagnosing: {member.name}")
    print(f"Family: {member.family.branch} (ID: {member.family.id})")
    print(f"{'='*60}\n")

    # Check direct relationships
    print("📌 DIRECT RELATIONSHIPS:")
    
    relationships_from = Relationship.objects.filter(from_member=member).select_related('to_member')
    relationships_to = Relationship.objects.filter(to_member=member).select_related('from_member')
    
    if relationships_from.exists():
        print(f"\n  Outgoing relationships:")
        for rel in relationships_from:
            cross_family = "❌ CROSS-FAMILY" if rel.from_member.family_id != rel.to_member.family_id else "✓"
            print(f"    → {rel.to_member.name} [{rel.relation_type}] (Fam: {rel.to_member.family.branch}) {cross_family}")
    
    if relationships_to.exists():
        print(f"\n  Incoming relationships:")
        for rel in relationships_to:
            cross_family = "❌ CROSS-FAMILY" if rel.from_member.family_id != rel.to_member.family_id else "✓"
            print(f"    ← {rel.from_member.name} [{rel.relation_type}] (Fam: {rel.from_member.family.branch}) {cross_family}")

    # Check parent links
    print("\n📌 PARENT LINKS (M2M):")
    parents = member.parents.all()
    if parents.exists():
        print(f"  Parents:")
        for parent in parents:
            cross_family = "❌ CROSS-FAMILY" if parent.family_id != member.family_id else "✓"
            print(f"    ← {parent.name} (Fam: {parent.family.branch}) {cross_family}")
    else:
        print(f"  No parents set")

    children = member.children.all()
    if children.exists():
        print(f"\n  Children:")
        for child in children:
            cross_family = "❌ CROSS-FAMILY" if child.family_id != member.family_id else "✓"
            print(f"    → {child.name} (Fam: {child.family.branch}) {cross_family}")
    else:
        print(f"  No children set")

    # Check siblings
    print("\n📌 SIBLING RELATIONSHIPS:")
    from django.db.models import Q
    siblings_relationships = Relationship.objects.filter(
        relation_type__in=['Sibling', 'SIBLING', 'Brother', 'Sister']
    ).filter(
        Q(from_member=member) | Q(to_member=member)
    ).select_related('from_member', 'to_member')
    
    if siblings_relationships.exists():
        print(f"  Sibling relationships:")
        for rel in siblings_relationships:
            other = rel.to_member if rel.from_member_id == member.id else rel.from_member
            cross_family = "❌ CROSS-FAMILY" if other.family_id != member.family_id else "✓"
            print(f"    ↔ {other.name} (Fam: {other.family.branch}) {cross_family}")


def find_all_cross_family_issues():
    """Find all cross-family relationships."""
    print("\n🔍 SCANNING FOR ALL CROSS-FAMILY RELATIONSHIPS...\n")
    
    cross_family_count = 0
    by_family = {}
    
    for rel in Relationship.objects.select_related('from_member', 'to_member'):
        if rel.from_member.family_id != rel.to_member.family_id:
            cross_family_count += 1
            from_fam = rel.from_member.family.branch
            if from_fam not in by_family:
                by_family[from_fam] = []
            by_family[from_fam].append(rel)
    
    if cross_family_count == 0:
        print("✓ No cross-family relationships found!")
        return
    
    print(f"❌ Found {cross_family_count} cross-family relationships:\n")
    
    for family_branch, rels in sorted(by_family.items()):
        print(f"\n{family_branch}:")
        for rel in rels:
            print(f"  {rel.from_member.name} ({rel.from_member.family.branch})")
            print(f"    --[{rel.relation_type}]-->")
            print(f"  {rel.to_member.name} ({rel.to_member.family.branch})")


# Usage:
if __name__ == '__main__':
    import django
    django.setup()
    
    # Find Kurian Chacko
    print("Searching for 'Kurian Chacko'...")
    kurian_results = find_member_by_name('Kurian Chacko')
    if kurian_results.exists():
        for member in kurian_results:
            diagnose_member(member.id)
    else:
        print("Not found. Trying 'Kurian'...")
        kurian_results = find_member_by_name('Kurian')
        if kurian_results.exists():
            for member in kurian_results:
                print(f"  - {member.name} (ID: {member.id})")
    
    # Find Sussama Chacko
    print("\n\nSearching for 'Sussama Chacko'...")
    sussama_results = find_member_by_name('Sussama')
    if sussama_results.exists():
        for member in sussama_results:
            diagnose_member(member.id)
    else:
        print("Not found")
    
    # Scan all
    find_all_cross_family_issues()
