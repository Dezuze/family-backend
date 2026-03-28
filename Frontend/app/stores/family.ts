import { defineStore } from 'pinia'
import type { FamilyMember } from '~/types/family'
import { useRuntimeConfig } from '#imports'

export const useFamilyStore = defineStore('family', {
  state: () => ({
    members: [] as FamilyMember[],
    edges: [] as any[],
    computedRelations: [] as any[],
    generationDepth: 0,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchFamily() {

      this.loading = true
      this.error = null
      
      const config = useRuntimeConfig()
      const apiBase = config.public.apiBase || 'http://localhost:8000'

      try {
        const response = await fetch(`${apiBase}/api/families/tree/`, {
           credentials: 'include'
        })
        if (response.ok) {
            const data = await response.json()
          // Data is { nodes: [], edges: [], computed_relations: [], generation_depth: number }
            this.members = data.nodes || []
          this.edges = data.edges || []
          this.computedRelations = data.computed_relations || []
          this.generationDepth = data.generation_depth || 0
        } else {
            this.error = 'Failed to load family data'
        }
      } catch (err) {
        this.error = 'Error loading family data'
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    // find member by id
    findById(id: number): FamilyMember | undefined {
      return this.members.find(m => m.id === id)
    },

    // flat list accessor
    flatList(): FamilyMember[] {
      return this.members
    },
    
    // Legacy support or helper
    // addMember logic moved to backend/onboarding
  },

  persist: true,
})
