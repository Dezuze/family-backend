<template>
  <div class="relative bg-white/90 backdrop-blur-md rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-5 flex flex-col gap-4 border border-slate-100 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] hover:border-brand-gold/30 hover:-translate-y-1 transition-all duration-300 overflow-hidden group">
    <!-- Top section: Photo + ID/Name -->
    <div class="flex items-center gap-4">
      <div class="shrink-0 relative flex" :class="{ 'w-24': partner }">
        <img 
          :src="resolveImage(member.photo) || `https://ui-avatars.com/api/?name=${member.name}&background=f1f5f9&color=64748b`" 
          :alt="member.name || t('nav.photoAlt.member')"
          class="w-16 h-16 rounded-full object-cover ring-2 ring-white shadow-md relative z-10 group-hover:scale-105 transition-transform duration-300"
          @error="(e) => (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${member.name}&background=f1f5f9&color=64748b`"
        />
        <img v-if="partner"
          :src="resolveImage(partner.photo) || `https://ui-avatars.com/api/?name=${partner.name}&background=e2e8f0&color=475569`"
          :alt="partner.name"
          class="w-16 h-16 rounded-full object-cover ring-2 ring-white shadow-md absolute left-8 z-0 group-hover:scale-105 transition-transform duration-300"
          @error="(e) => (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${partner?.name}&background=e2e8f0&color=475569`"
        />
        <div v-if="member.is_deceased" class="absolute -top-1 -right-1 z-20 bg-slate-800 text-white w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shadow-sm">
          †
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <span class="block text-[10px] font-bold tracking-widest uppercase text-brand-gold/80 mb-0.5">{{ member.member_id || `#${member.id}` }}</span>
        <h3 class="text-base font-extrabold truncate text-slate-800 tracking-tight">{{ member.name }}</h3>
        <p v-if="partner" class="text-xs text-slate-500 font-semibold truncate">& {{ partner.name }}</p>
        <span v-if="member.is_committee" class="inline-block mt-1 bg-brand-gold/10 text-brand-gold text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider border border-brand-gold/20">{{ t('memberCard.committeeBadge') }}</span>
      </div>
    </div>
    
    <!-- Details grid -->
    <div class="grid grid-cols-2 gap-2 mt-2 pt-4 border-t border-slate-100/80">
      <div v-if="member.age" class="flex flex-col">
        <span class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Age</span>
        <span class="text-xs font-semibold text-slate-700 mt-0.5">{{ member.age }}{{ t('memberCard.ageSuffix') }}</span>
      </div>
      <div v-if="member.occupation" class="flex flex-col">
        <span class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Occupation</span>
        <span class="text-xs font-semibold text-slate-700 mt-0.5 truncate">{{ member.occupation }}</span>
      </div>
      <div v-if="memberLocation" class="flex flex-col col-span-2">
        <span class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Location</span>
        <span class="text-xs font-semibold text-slate-700 mt-0.5 truncate">{{ memberLocation }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FamilyMember } from '~/types/family'
import { computed } from 'vue'
import { useRuntimeConfig } from '#imports'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ 
    member: FamilyMember,
    partner?: FamilyMember | null
}>()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const { t } = useI18n()

const resolveImage = (path: string | undefined | null) => {
    if (!path) return undefined
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

const memberLocation = computed(() => {
    return props.member.place_of_work || props.member.location || props.member.address || props.member.church_parish || ''
})
</script>
