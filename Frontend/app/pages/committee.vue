<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans pt-32 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Header -->
      <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
          {{ t('committee.header.title') }}
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
          {{ t('committee.header.term') }}
        </p>
      </div>

      <!-- Controls -->
      <div class="flex justify-center mb-10">
        <div class="relative w-full max-w-md">
          <input v-model="query" type="search" :placeholder="t('committee.searchPlaceholder')" 
                  class="w-full pl-10 pr-4 py-3 rounded-full bg-white border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none shadow-md transition-all" />
           <svg class="w-5 h-5 text-slate-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
      </div>

      <!-- Custom Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Skeleton Grid -->
        <template v-if="loading">
          <div v-for="n in 6" :key="n" class="bg-white rounded-2xl overflow-hidden shadow-sm border border-slate-200 animate-pulse">
            <div class="h-64 sm:h-72 bg-slate-200"></div>
            <div class="p-4 space-y-3">
              <div class="h-6 bg-slate-200 rounded w-1/2"></div>
              <div class="h-4 bg-slate-200 rounded w-1/3"></div>
            </div>
          </div>
        </template>

        <!-- Real Committee Cards -->
        <template v-else-if="filtered.length > 0">
          <div 
            v-for="m in filtered" 
            :key="m.id"
            class="group relative mx-auto w-full max-w-[320px] sm:max-w-none"
          >
            <!-- Card Container with Glassmorphism -->
            <div
              @click="openDetails(m)"
              class="relative bg-white/90 backdrop-blur-md rounded-3xl overflow-hidden shadow-xl border transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl flex flex-col h-full"
              :class="getPriority(m.role) <= 6 ? 'border-brand-gold/40 ring-1 ring-brand-gold/10' : 'border-slate-200'"
            >
              <!-- Image Section -->
              <div class="h-52 w-full relative overflow-hidden bg-slate-50 sm:h-64">
                <img 
                  v-if="m.photo" 
                  :src="m.photo" 
                  :alt="m.name || t('committee.alt.memberPhoto')"
                  class="w-full h-full object-cover object-top transition-transform duration-700 group-hover:scale-110" 
                />
                <div v-else class="w-full h-full flex items-center justify-center bg-linear-to-b from-slate-100 to-slate-200 text-brand-gold/20">
                    <span class="text-6xl font-serif font-bold select-none">{{ m.name.charAt(0) }}</span>
                </div>
                
                <!-- Premium Overlays -->
                <div class="absolute inset-x-0 bottom-0 h-40 bg-linear-to-t from-black/70 via-black/30 to-transparent"></div>
                
                <!-- Role Badge (Floating) -->
                <div class="absolute top-3 right-3 animate-in fade-in zoom-in duration-700 sm:top-4 sm:right-4">
                    <span 
                      class="px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest shadow-lg backdrop-blur-md border sm:px-4"
                      :class="getPriority(m.role) <= 6 
                         ? 'bg-brand-gold text-white border-brand-gold-dark' 
                         : 'bg-white/90 text-slate-800 border-slate-200'"
                    >
                      {{ m.role || t('committee.labels.member') }}
                    </span>
                </div>

                <!-- Subtle hover wash only (no plus icon) -->
                <div class="absolute inset-0 bg-brand-gold/8 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
              </div>
              
              <!-- Info Section -->
              <div class="p-4 sm:p-5 flex-1 flex flex-col justify-between relative">
                <!-- Name & Title -->
                <div>
                  <h3 class="text-lg sm:text-xl font-serif font-bold text-slate-900 leading-tight mb-1 group-hover:text-brand-gold transition-colors">
                    {{ displayHonorificName(m.name) }}
                  </h3>
                  <p class="text-[10px] font-sans font-extrabold uppercase tracking-[0.2em] text-brand-gold/80 mb-3">
                    {{ m.role || t('committee.labels.committeeMember') }}
                  </p>
                  <div class="space-y-1.5 text-[11px] text-slate-600 pb-3">
                    <p v-if="m.member_id" class="truncate"><span class="font-semibold text-slate-500">ID:</span> {{ m.member_id }}</p>
                    <p v-if="m.phone_no" class="truncate"><span class="font-semibold text-slate-500">Phone:</span> {{ m.phone_no }}</p>
                    <p v-if="m.email_id" class="truncate"><span class="font-semibold text-slate-500">Email:</span> {{ m.email_id }}</p>
                  </div>
                </div>

                <!-- Action Footer (removed Committee Member label) -->
                <!--
                <div class="flex items-center justify-between mt-auto pt-4 sm:pt-6 border-t border-slate-100/50">
                  <span class="text-xs font-bold text-slate-500">{{ t('committee.labels.committeeMember') }}</span>
                </div>
                -->

                <!-- Subtle Pattern Overlay for Officers -->
                <div v-if="getPriority(m.role) <= 6" class="absolute -right-4 -bottom-4 opacity-[0.03] rotate-12 pointer-events-none">
                    <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
                </div>
              </div>
            </div>
            
            <!-- Shadow Flourish for Officers -->
            <div 
              v-if="getPriority(m.role) <= 6" 
              class="absolute -inset-0.5 bg-brand-gold/20 blur-xl opacity-0 group-hover:opacity-40 transition-opacity duration-500 rounded-3xl"
            ></div>
          </div>
        </template>

        <!-- Empty State -->
        <template v-else>
          <div class="col-span-full text-center text-slate-500 py-20">
            {{ t('committee.empty.noMembers') }}
          </div>
        </template>
      </div>

    <!-- Professional Details Modal -->
    <Transition name="fade">
      <div v-if="selectedMember" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-3 sm:items-center sm:p-4" @click.self="closeDetails">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-md"></div>
        
        <div class="relative my-3 flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-2xl sm:my-0">
          <!-- Header Image -->
          <div class="h-64 sm:h-80 bg-slate-100 relative">
            <img 
              v-if="selectedMember.photo" 
              :src="selectedMember.photo" 
              :alt="selectedMember.name || t('committee.alt.memberPhoto')"
              class="w-full h-full object-cover object-top" 
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-linear-to-b from-slate-100 to-slate-200 text-brand-gold/10">
               <span class="text-9xl font-serif font-bold select-none">{{ selectedMember.name.charAt(0) }}</span>
            </div>
            <div class="absolute inset-0 bg-linear-to-t from-black/60 to-transparent"></div>
            
            <button @click="closeDetails" class="absolute top-6 right-6 p-2.5 bg-black/20 hover:bg-black/40 text-white rounded-full backdrop-blur-md transition-colors">
               <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>

            <div class="absolute bottom-6 left-8">
               <span class="px-4 py-1 bg-brand-gold text-white text-[10px] font-black uppercase tracking-widest rounded-full mb-3 inline-block">
                 {{ selectedMember.role || t('committee.labels.committee') }}
               </span>
               <h2 class="text-3xl font-serif font-bold text-white drop-shadow-md">{{ displayHonorificName(selectedMember.name) }}</h2>
            </div>
          </div>

          <!-- Professional Body -->
          <div class="space-y-8 overflow-y-auto p-6 sm:p-10">
             <div class="space-y-6">
                <div class="flex items-center gap-5 group">
                   <div class="w-12 h-12 rounded-2xl bg-brand-gold/5 flex items-center justify-center text-brand-gold border border-brand-gold/10 group-hover:bg-brand-gold group-hover:text-white transition-all duration-500">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-10V4m0 10V4m-4 6h4m-4 4h4m1 1h1m-7 1h1"></path></svg>
                   </div>
                   <div>
                     <span class="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-0.5">{{ t('committee.modal.representation') }}</span>
                     <span class="text-lg font-bold text-slate-900">{{ t('committee.modal.executiveBody') }}</span>
                   </div>
                </div>

                <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <div class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Role</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.role || t('committee.labels.committeeMember') }}</div>
                  </div>
                  <div v-if="selectedMember.member_id" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Member ID</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.member_id }}</div>
                  </div>
                  <div v-if="selectedMember.phone_no" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Phone</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.phone_no }}</div>
                  </div>
                  <div v-if="selectedMember.email_id" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 sm:col-span-2">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Email</div>
                    <div class="mt-1 text-sm font-bold text-slate-800 break-all">{{ selectedMember.email_id }}</div>
                  </div>
                  <div v-if="selectedMember.relation" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 sm:col-span-2">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Category</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.relation }}</div>
                  </div>
                  <div v-if="selectedMember.occupation" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Occupation</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.occupation }}</div>
                  </div>
                  <div v-if="selectedMember.education" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Education</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.education }}</div>
                  </div>
                  <div v-if="selectedMember.church_parish" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 sm:col-span-2">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Parish</div>
                    <div class="mt-1 text-sm font-bold text-slate-800">{{ selectedMember.church_parish }}</div>
                  </div>
                  <div v-if="selectedMember.bio" class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 sm:col-span-2">
                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">About</div>
                    <div class="mt-1 text-sm font-medium leading-relaxed text-slate-700">{{ selectedMember.bio }}</div>
                  </div>
                </div>
             </div>

             <div class="pt-8 border-t border-slate-100 flex justify-center">
                <button 
                  @click="closeDetails"
                  class="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold text-sm tracking-widest uppercase hover:bg-brand-gold transition-colors shadow-xl"
                >
                  {{ t('committee.modal.closeProfile') }}
                </button>
             </div>
          </div>
        </div>
      </div>
    </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead, useRuntimeConfig, useRoute } from '#imports'
import { useI18n } from 'vue-i18n'
import type { FamilyMember } from '~/types/family'

const runtimeConfig = useRuntimeConfig()
const route = useRoute()
const { t } = useI18n()

useHead(() => ({
  title: t('committee.meta.title'),
  meta: [
    { name: 'description', content: t('committee.meta.description') }
  ],
  link: [
    { rel: 'canonical', href: `${runtimeConfig.public.siteUrl || 'http://localhost:3000'}${route.path}` }
  ]
}))

// Types
type LayoutType = 'grid' | 'list' | 'compact'

// State
const committee = ref<FamilyMember[]>([])
const loading = ref(true)
const query = ref('')
const selectedMember = ref<FamilyMember | null>(null)
const committeeRefreshMs = 30000
let committeeRefreshTimer: ReturnType<typeof setInterval> | null = null

const openDetails = (m: FamilyMember) => {
    selectedMember.value = m
    document.body.style.overflow = 'hidden'
}

const closeDetails = () => {
    selectedMember.value = null
    document.body.style.overflow = ''
}

// Role Priority Map (Lower number = Higher priority)
const rolePriority: Record<string, number> = {
    'Patron': 1,
    'President': 2,
  'Working President': 3,
    'Vice President': 3,
  'Secretary': 4,
  'Joint Secretary': 5,
  'Treasurer': 6,
  'Auditor': 7,
    'Committee Member': 99
}

const getPriority = (role?: string): number => {
    if (!role) return 100
  const cleanRole = role.trim()
  const exact = rolePriority[cleanRole]
  if (exact !== undefined) return exact

  const lowered = cleanRole.toLowerCase()
  if (lowered.includes('working president')) return rolePriority['Working President'] ?? 3
  if (lowered.includes('vice president') || lowered.includes('vice-president')) return rolePriority['Vice President'] ?? 3
  if (lowered.includes('joint secretary') || lowered.includes('joint-secretary')) return rolePriority['Joint Secretary'] ?? 5
  if (lowered.includes('secretary')) return rolePriority['Secretary'] ?? 4
  if (lowered.includes('treasurer')) return rolePriority['Treasurer'] ?? 6
  if (lowered.includes('auditor')) return rolePriority['Auditor'] ?? 7
  if (lowered.includes('president')) return rolePriority['President'] ?? 2
  if (lowered.includes('committee member')) return rolePriority['Committee Member'] ?? 99
  return 100
}

const apiBase = runtimeConfig.public.apiBase || 'http://localhost:8000'

const honorificOverrides: Record<string, string> = {
  'k c varghese': 'Sri.',
  'saju elias': 'Prof.',
  'jojo jacob': 'Mr.',
  'praveen mani': 'Mr.',
  'korula issac': 'Mr.',
  'korula isaac': 'Mr.',
  'anish chacko': 'Mr.',
  'manoj andrews': 'Mr.',
  'k a abraham': 'Mr.',
  'baby kuriakose': 'Mr.',
  'kurian mathew': 'Mr.',
  'mini phillip': 'Mrs.',
  'mini philip': 'Mrs.',
  'gabi praveen': 'Mrs.',
}

const hasHonorificPrefix = (name: string) => {
  return /^(mr\.|mrs\.|ms\.|dr\.|prof\.|sri\.)\s+/i.test(String(name || '').trim())
}

const normalizeNameKey = (name: string) => {
  return String(name || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9 ]+/g, ' ')
    .replace(/\s+/g, ' ')
}

const displayHonorificName = (name: string) => {
  const safeName = String(name || '').trim()
  if (!safeName) return ''
  if (hasHonorificPrefix(safeName)) return safeName

  const prefix = honorificOverrides[normalizeNameKey(safeName)] || 'Mr.'
  return `${prefix} ${safeName}`
}

// Fetch Data
const resolveImage = (path: string) => {
    if (!path) return undefined
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

const fetchCommittee = async (opts?: { silent?: boolean }) => {
  if (!opts?.silent) loading.value = true
  try {
    let rows: any[] = []

    // Preferred source: dedicated families committee dataset.
    const newRes = await fetch(`${apiBase}/api/families/committee-members/?term_label=2026-28`)
    if (newRes.ok) {
      rows = await newRes.json()
      committee.value = rows.map((item: any) => ({
        id: item.id,
        name: item.name,
        photo: resolveImage(item.photo_url || item.photo),
        role: item.role_title,
        member_id: item.member_id,
        phone_no: item.phone_no,
        email_id: item.email_id,
        occupation: item.occupation,
        education: item.education,
        church_parish: item.church_parish,
        relation: item.category === 'office_bearer' ? 'Office Bearer' : 'Committee',
        bio: item.bio || item.house_name || '',
      }))
      return
    }

    // Backward compatibility: legacy profiles endpoint.
    const legacyRes = await fetch(`${apiBase}/api/profiles/committee/`)
    if (legacyRes.ok) {
      rows = await legacyRes.json()
      committee.value = rows.map((item: any) => ({
        id: item.id,
        name: item.name,
        photo: resolveImage(item.pic),
        role: item.role,
        member_id: item.member_id,
        occupation: item.occupation,
        education: item.education,
        church_parish: item.church_parish,
        bio: item.bio,
        relation: 'Committee',
      }))
    }
    } catch (e) {
        console.error("Failed to load committee", e)
    } finally {
      if (!opts?.silent) loading.value = false
    }
  }

  const onWindowFocus = () => {
    fetchCommittee({ silent: true })
  }

  const onVisibilityChange = () => {
    if (!document.hidden) {
      fetchCommittee({ silent: true })
    }
  }

  onMounted(async () => {
    await fetchCommittee()

    committeeRefreshTimer = setInterval(() => {
      fetchCommittee({ silent: true })
    }, committeeRefreshMs)

    window.addEventListener('focus', onWindowFocus)
    document.addEventListener('visibilitychange', onVisibilityChange)
})

  onUnmounted(() => {
    if (committeeRefreshTimer) {
      clearInterval(committeeRefreshTimer)
      committeeRefreshTimer = null
    }
    window.removeEventListener('focus', onWindowFocus)
    document.removeEventListener('visibilitychange', onVisibilityChange)
    document.body.style.overflow = ''
  })

// Search & Filter
const normalized = (s: string) => s.trim().toLowerCase()

const filtered = computed(() => {
    let result = [...committee.value]

    // 1. Search Filter
    if (query.value) {
        const q = normalized(query.value)
        result = result.filter(m => {
            const name = normalized(m.name || '')
            const role = normalized(m.role || '')
            return name.includes(q) || role.includes(q)
        })
    }

    // 2. Sort with office roles first and generic committee members last.
    const isGenericCommitteeMember = (m: FamilyMember) => {
      const role = normalized(m.role || '')
      return role === 'committee member' || role.includes('committee member')
    }

    result.sort((a, b) => {
        const aIsCommittee = isGenericCommitteeMember(a)
        const bIsCommittee = isGenericCommitteeMember(b)

        // Keep special/named roles above the generic committee block.
        if (aIsCommittee !== bIsCommittee) return aIsCommittee ? 1 : -1

        const pA = getPriority(a.role)
        const pB = getPriority(b.role)
        if (pA !== pB) return pA - pB
        // Secondary sort by name
        return (a.name || '').localeCompare(b.name || '')
    })

    return result
})

</script>

<style scoped>
/* Ensure grid works properly */
</style>
