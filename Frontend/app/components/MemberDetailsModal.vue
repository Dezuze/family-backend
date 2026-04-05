<template>
  <Transition name="fade">
    <div v-if="member" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="$emit('close')"></div>
      
      <div class="relative bg-white rounded-2xl w-full max-w-4xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col md:flex-row max-h-[90vh]">
        
        <!-- Close Button (Mobile) -->
        <button @click="$emit('close')" class="absolute top-4 right-4 z-10 p-2 bg-black/10 hover:bg-black/20 rounded-full text-slate-600 md:hidden">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <!-- Left Side: Image & Age -->
        <div class="w-full md:w-1/3 bg-slate-50 p-8 flex flex-col items-center justify-center border-r border-slate-100 relative">
             <div class="w-48 h-48 rounded-full border-4 border-white overflow-hidden shadow-xl mb-6 ring-1 ring-slate-200">
               <img 
                 :src="resolveImage(member.photo) || `https://ui-avatars.com/api/?name=${member.name}&background=cbd5e1&color=fff`" 
                 :alt="member.name || t('nav.photoAlt.member')"
                 class="w-full h-full object-cover"
               />
             </div>
             
             <h2 class="text-2xl font-serif font-bold text-slate-800 text-center mb-2">{{ member.name }}</h2>
             <span class="px-4 py-1 rounded-full bg-white text-slate-600 text-sm font-bold shadow-sm border border-slate-200">
              {{ t('memberDetailsModal.labels.age') }}: {{ member.age }}
             </span>
             
             <div class="mt-6 flex gap-2">
               <span v-if="member.gender=='M'" class="text-brand-gold text-xs uppercase font-bold tracking-wider bg-brand-gold/5 px-2 py-1 rounded-md">{{ t('memberDetailsModal.labels.male') }}</span>
               <span v-if="member.gender=='F'" class="text-pink-600 text-xs uppercase font-bold tracking-wider bg-pink-50 px-2 py-1 rounded-md">{{ t('memberDetailsModal.labels.female') }}</span>
               <span v-if="member.is_deceased" class="text-slate-500 text-xs uppercase font-bold tracking-wider bg-slate-200 px-2 py-1 rounded-md">{{ t('memberDetailsModal.labels.deceased') }}</span>
             </div>
        </div>

        <!-- Right Side: Details -->
        <div class="w-full md:w-2/3 p-8 overflow-y-auto custom-scrollbar bg-white">
            <!-- Header & Close -->
            <div class="flex justify-between items-start mb-6">
                <div>
                <h3 class="text-lg font-bold text-brand-gold uppercase tracking-widest">{{ t('memberDetailsModal.labels.member') }}</h3>
                <p class="text-xs text-slate-500">{{ t('memberDetailsModal.labels.profileDetails') }}</p>
                </div>
                <div class="hidden md:flex items-center gap-2">
                  <button
                    v-if="canEdit"
                    @click="$emit('edit')"
                    class="rounded-lg border border-brand-gold/40 px-3 py-1.5 text-xs font-bold text-brand-gold transition-colors hover:bg-brand-gold/10"
                  >
                    Edit Member
                  </button>
                  <button @click="$emit('close')" class="p-2 text-slate-400 hover:text-slate-800 transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
                </div>
            </div>

            <!-- Details Grid -->
            <div class="grid grid-cols-2 gap-6 mb-8">
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">Member ID</span>
                 <p class="text-slate-800 font-medium">{{ member.member_id || member.id || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ member.is_deceased ? t('memberDetailsModal.labels.dateOfDeath') : t('memberDetailsModal.labels.dateOfBirth') }}</span>
                   <p class="text-slate-800 font-medium">
                    {{ member.is_deceased && member.date_of_death ? member.date_of_death : (member.date_of_birth || t('memberDetailsModal.labels.notAvailable')) }}
                   </p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.bloodGroup') }}</span>
                 <p class="text-slate-800 font-medium">{{ member.blood_group || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.occupation') }}</span>
                 <p class="text-slate-800 font-medium">{{ member.occupation || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div v-if="member.place_of_work">
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.workplace') }}</span>
                   <p class="text-slate-800 font-medium">{{ member.place_of_work }}</p>
                </div>
                <div v-if="member.church_parish">
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.parish') }}</span>
                   <p class="text-slate-800 font-medium">{{ member.church_parish }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.spouse') }}</span>
                 <p class="text-slate-800 font-medium">{{ member.spouse || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">Committee Role</span>
                 <p class="text-slate-800 font-medium">{{ member.committee_role || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">Wedding Anniversary</span>
                 <p class="text-slate-800 font-medium">{{ member.wedding_anniversary || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.location') }}</span>
                 <p class="text-slate-800 font-medium">{{ member.location || member.address || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div>
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.education') }}</span>
                 <p class="text-slate-800 font-medium">{{ member.education || t('memberDetailsModal.labels.notAvailable') }}</p>
                </div>
                <div v-if="member.email_id">
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.email') }}</span>
                   <p class="text-slate-800 font-medium break-all">{{ member.email_id }}</p>
                </div>
                <div v-if="member.phone_no">
                 <span class="text-xs text-slate-400 uppercase font-bold">{{ t('memberDetailsModal.labels.phone') }}</span>
                   <p class="text-slate-800 font-medium">{{ member.phone_no }}</p>
                </div>
            </div>

            <!-- Bio -->
            <div v-if="member.bio" class="mb-8">
               <span class="text-xs text-slate-400 uppercase font-bold block mb-2">{{ t('memberDetailsModal.labels.biography') }}</span>
                <p class="text-slate-600 text-sm leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100 italic">
                    "{{ member.bio }}"
                </p>
            </div>
            
            <!-- Children Table -->
            <div v-if="member.children && member.children.length > 0">
               <span class="text-xs text-slate-400 uppercase font-bold block mb-3">{{ t('memberDetailsModal.labels.children') }}</span>
                <div class="overflow-hidden rounded-lg border border-slate-200">
                    <table class="w-full text-sm text-left text-slate-600">
                        <thead class="text-xs text-slate-500 uppercase bg-slate-50">
                            <tr>
                          <th class="px-4 py-2 font-medium">{{ t('memberDetailsModal.labels.name') }}</th>
                          <th class="px-4 py-2 font-medium w-24">{{ t('memberDetailsModal.labels.age') }}</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            <tr v-for="child in member.children" :key="child.name" class="bg-white hover:bg-slate-50 transition-colors">
                                <td class="px-4 py-2 font-medium text-slate-800">{{ child.name }}</td>
                                <td class="px-4 py-2 text-slate-500">{{ child.age }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-else class="text-slate-400 text-sm italic">
                {{ t('memberDetailsModal.labels.noChildren') }}
            </div>

        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useRuntimeConfig } from '#imports'
import { useI18n } from 'vue-i18n'
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const { t } = useI18n()

defineProps({
  member: Object,
  canEdit: {
    type: Boolean,
    default: false,
  },
})
defineEmits(['close', 'edit'])

const resolveImage = (path) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
