import type { FamilyMember } from '~/types/family'

// Start with an empty family root. The tree will be built from registered users.
export const familyData: FamilyMember = {
  id: 1,
  name: 'Family Root',
  relation: 'Root',
  children: []
}
