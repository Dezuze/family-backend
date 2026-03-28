export type FamilyRelationSide = 'paternal' | 'maternal'

export type FamilyRelationClass =
  | 'parent'
  | 'child'
  | 'peer'
  | 'grandparent'
  | 'grandchild'
  | 'in-law'
  | 'extended-family'
  | 'member'
  | 'other'

export interface FamilyRelationDefinition {
  label: string
  offset: number
  side: FamilyRelationSide
  relationClass: FamilyRelationClass
  keywords: string[]
}

export const FAMILY_RELATION_DEFINITIONS: readonly FamilyRelationDefinition[] = [
  { label: 'Child', offset: 1, side: 'paternal', relationClass: 'child', keywords: ['child'] },
  { label: 'Member', offset: 0, side: 'paternal', relationClass: 'member', keywords: ['member'] },
  { label: 'Father', offset: -1, side: 'paternal', relationClass: 'parent', keywords: ['father', 'dad'] },
  { label: 'Mother', offset: -1, side: 'maternal', relationClass: 'parent', keywords: ['mother', 'mom'] },
  { label: 'Son', offset: 1, side: 'paternal', relationClass: 'child', keywords: ['son'] },
  { label: 'Daughter', offset: 1, side: 'maternal', relationClass: 'child', keywords: ['daughter'] },
  { label: 'Spouse', offset: 0, side: 'paternal', relationClass: 'peer', keywords: ['spouse', 'husband', 'wife'] },
  { label: 'Brother', offset: 0, side: 'paternal', relationClass: 'peer', keywords: ['brother'] },
  { label: 'Sister', offset: 0, side: 'paternal', relationClass: 'peer', keywords: ['sister'] },
  { label: 'Grandfather', offset: -2, side: 'paternal', relationClass: 'grandparent', keywords: ['grandfather', 'grandpa'] },
  { label: 'Grandmother', offset: -2, side: 'maternal', relationClass: 'grandparent', keywords: ['grandmother', 'grandma'] },
  { label: 'Grandson', offset: 2, side: 'paternal', relationClass: 'grandchild', keywords: ['grandson'] },
  { label: 'Granddaughter', offset: 2, side: 'maternal', relationClass: 'grandchild', keywords: ['granddaughter'] },
  { label: 'Uncle', offset: -1, side: 'paternal', relationClass: 'extended-family', keywords: ['uncle'] },
  { label: 'Aunt', offset: -1, side: 'paternal', relationClass: 'extended-family', keywords: ['aunt'] },
  { label: 'Nephew', offset: 1, side: 'paternal', relationClass: 'extended-family', keywords: ['nephew'] },
  { label: 'Niece', offset: 1, side: 'paternal', relationClass: 'extended-family', keywords: ['niece'] },
  { label: 'Cousin', offset: 0, side: 'paternal', relationClass: 'peer', keywords: ['cousin'] },
  {
    label: 'Paternal Grandfather',
    offset: -2,
    side: 'paternal',
    relationClass: 'grandparent',
    keywords: ['paternal grandfather'],
  },
  {
    label: 'Paternal Grandmother',
    offset: -2,
    side: 'paternal',
    relationClass: 'grandparent',
    keywords: ['paternal grandmother'],
  },
  {
    label: 'Maternal Grandfather',
    offset: -2,
    side: 'maternal',
    relationClass: 'grandparent',
    keywords: ['maternal grandfather'],
  },
  {
    label: 'Maternal Grandmother',
    offset: -2,
    side: 'maternal',
    relationClass: 'grandparent',
    keywords: ['maternal grandmother'],
  },
  {
    label: 'Father-in-law',
    offset: -1,
    side: 'paternal',
    relationClass: 'in-law',
    keywords: ['father-in-law', 'father in law'],
  },
  {
    label: 'Mother-in-law',
    offset: -1,
    side: 'maternal',
    relationClass: 'in-law',
    keywords: ['mother-in-law', 'mother in law'],
  },
  {
    label: 'Son-in-law',
    offset: 1,
    side: 'paternal',
    relationClass: 'in-law',
    keywords: ['son-in-law', 'son in law'],
  },
  {
    label: 'Daughter-in-law',
    offset: 1,
    side: 'maternal',
    relationClass: 'in-law',
    keywords: ['daughter-in-law', 'daughter in law'],
  },
  {
    label: 'Brother-in-law',
    offset: 0,
    side: 'paternal',
    relationClass: 'in-law',
    keywords: ['brother-in-law', 'brother in law'],
  },
  {
    label: 'Sister-in-law',
    offset: 0,
    side: 'paternal',
    relationClass: 'in-law',
    keywords: ['sister-in-law', 'sister in law'],
  },
  { label: 'Other', offset: 0, side: 'paternal', relationClass: 'other', keywords: ['other'] },
] as const

export const FAMILY_RELATION_TYPES = FAMILY_RELATION_DEFINITIONS.map((item) => item.label)

export const IN_LAW_RELATION_TYPES = FAMILY_RELATION_DEFINITIONS.filter(
  (item) => item.relationClass === 'in-law'
).map((item) => item.label)

export const MARRIED_TO_ELIGIBLE_RELATIONS = ['Brother', 'Sister', 'Son', 'Daughter'] as const