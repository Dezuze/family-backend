<template>
  <div class="min-h-screen bg-slate-800 text-gray-100 font-sans pt-32 pb-16 px-4 md:px-12">
    <div class="max-w-7xl mx-auto">
      
      <!-- Header -->
      <div class="text-center mb-16">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-white mb-4">Committee Members</h1>
        <div class="h-1 w-24 bg-amber-500 mx-auto rounded-full"></div>
        <p class="mt-6 text-lg text-gray-400 max-w-2xl mx-auto">
          Meet the dedicated members serving our family association for the current term.
        </p>
      </div>

      <!-- Current Term Badge -->
      <div class="flex justify-center mb-12">
        <span class="bg-slate-700/50 text-amber-500 px-6 py-2 rounded-full border border-amber-500/20 font-bold tracking-widest text-sm uppercase shadow-lg backdrop-blur-sm">
            Term 2025 - 2027
        </span>
      </div>

      <div v-if="loading" class="text-center text-gray-500">Loading committee...</div>
      <div v-else-if="committee.length === 0" class="text-center text-gray-500">No committee members found.</div>

      <!-- Committee Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        
        <div v-for="member in committee" :key="member.id" 
             class="group relative bg-slate-700 rounded-xl overflow-hidden shadow-xl hover:-translate-y-2 transition-transform duration-300">
            
            <!-- Image Area -->
            <div class="relative h-64 overflow-hidden">
                <img :src="resolveImage(member.pic) || `https://ui-avatars.com/api/?name=${member.name}&background=1e293b&color=cbd5e1`" :alt="member.name"
                     class="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500" />
                <div class="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-transparent to-transparent"></div>
                
                <!-- Position Badge -->
                <div class="absolute bottom-4 left-4 right-4">
                    <div class="text-amber-500 text-xs font-bold uppercase tracking-widest mb-1">{{ member.role }}</div>
                    <h3 class="text-xl font-bold text-white leading-tight font-serif">{{ member.name }}</h3>
                </div>
            </div>

            <!-- Details -->
            <div class="p-6 border-t border-white/5">
                <div class="space-y-3 text-sm text-gray-400">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                        +91 98XXX XXXXX
                    </div>
                </div>
                
                <button class="mt-6 w-full py-2 rounded bg-slate-800 hover:bg-amber-500 hover:text-slate-900 border border-white/10 text-xs font-bold uppercase tracking-wider transition-all duration-300">
                    Contact
                </button>
            </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useHead, useRuntimeConfig } from '#imports'

useHead({
  title: 'Committee - Kollaparambil Family'
})

const config = useRuntimeConfig()
const committee = ref<any[]>([])
const loading = ref(true)

const resolveImage = (path: string) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `http://localhost:8000${path}`
}

onMounted(async () => {
    try {
        const res = await fetch('http://localhost:8000/api/profiles/committee/')
        if (res.ok) {
            committee.value = await res.json()
        }
    } catch (e) {
        console.error("Failed to load committee", e)
    } finally {
        loading.value = false
    }
})
</script>
