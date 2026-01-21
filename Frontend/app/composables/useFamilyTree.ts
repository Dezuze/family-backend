import * as d3 from 'd3'
import type { FamilyMember } from '~/types/family'

export function useFamilyTree(data: FamilyMember): d3.HierarchyPointNode<FamilyMember> {
  const hierarchy = d3.hierarchy<FamilyMember>(data)
  // increase node spacing for card layout (horizontal spacing, vertical spacing)
  const treeLayout = d3.tree<FamilyMember>().nodeSize([300, 300])

  return treeLayout(hierarchy)
}
