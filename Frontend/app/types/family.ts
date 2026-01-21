export interface FamilyMember {
  id: number
  name: string
  photo?: string
  age?: number
  relation?: string
  children?: FamilyMember[]
  parents?: number[]
}
