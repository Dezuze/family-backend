import { defineStore } from 'pinia'
import { familyData } from '~/data/family'
import type { FamilyMember } from '~/types/family'

function clone<T>(v: T): T { return JSON.parse(JSON.stringify(v)) }

export const useFamilyStore = defineStore('family', {
  state: () => ({
    root: clone<FamilyMember>(familyData),
  }),

  actions: {
    // find member by id (DFS)
    findById(id: number, node: FamilyMember | null = null): FamilyMember | null {
      const n = node ?? this.root
      if (!n) return null
      if (n.id === id) return n
      if (!n.children) return null
      for (const c of n.children) {
        const found = this.findById(id, c)
        if (found) return found
      }
      return null
    },

    // find member by name + age (or dob stored in relation/age) - simple match
    findByNameDob(name: string, age?: number): FamilyMember | null {
      const flat = this.flatList()
      return flat.find((m) => m.name.toLowerCase() === name.trim().toLowerCase() && (age == null || m.age === age)) ?? null
    },

    // get flat list of members for selects
    flatList(): FamilyMember[] {
      const out: FamilyMember[] = []
      const walk = (n: FamilyMember) => {
        out.push({ id: n.id, name: n.name, relation: n.relation, age: n.age, photo: n.photo })
        if (n.children) n.children.forEach(walk)
      }
      walk(this.root)
      return out
    },

    // Adds a new member under parentId. If parentId is null, push as child of root.
    // `member` may include `parents` array of parent ids; if provided, the new member is appended
    // to each parent.children array as well.
    addMember(parentId: number | null, member: Omit<FamilyMember, 'id' | 'children'> & { parents?: number[] }) {
      // compute next id by scanning flat list
      const flat = this.flatList()
      const maxId = flat.reduce((m, x) => Math.max(m, x.id), 0)
      const newMember: FamilyMember = { id: maxId + 1, ...member }

      // attach to parentId if given
      if (parentId) {
        const parent = this.findById(parentId)
        if (parent) {
          if (!parent.children) parent.children = []
          parent.children.push(newMember)
        }
      } else {
        if (!this.root.children) this.root.children = []
        this.root.children.push(newMember)
      }

      // also attach to any parents listed
      if (member.parents && member.parents.length) {
        for (const pid of member.parents) {
          const p = this.findById(pid)
          if (p) {
            if (!p.children) p.children = []
            // avoid duplicates
            if (!p.children.find((c) => c.id === newMember.id)) p.children.push(newMember)
          }
        }
      }

      return newMember
    }
  },

  persist: true,
})
