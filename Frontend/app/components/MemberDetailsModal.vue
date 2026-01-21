<template>
  <Transition name="fade">
    <div v-if="member" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="$emit('close')"></div>
      
      <div class="relative bg-slate-800 rounded-2xl w-full max-w-lg shadow-2xl border border-white/10 overflow-hidden transform transition-all">
        
        <!-- Header Image -->
        <div class="h-32 bg-amber-600/20 relative">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-800 to-transparent"></div>
          <button @click="$emit('close')" class="absolute top-4 right-4 p-2 bg-black/20 hover:bg-black/40 rounded-full text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <!-- Profile Pic & Name -->
        <div class="px-8 pb-8 -mt-16 relative">
          <div class="flex flex-col items-center">
            <div class="w-32 h-32 rounded-full border-4 border-slate-800 bg-slate-700 overflow-hidden shadow-xl mb-4">
              <img 
                :src="member.photo || `https://ui-avatars.com/api/?name=${member.name}&background=1e293b&color=cbd5e1`" 
                class="w-full h-full object-cover"
              />
            </div>
            <h2 class="text-2xl font-serif font-bold text-white text-center">{{ member.name }}</h2>
            <p class="text-amber-500 font-medium">{{ member.relation }}</p>
          </div>

          <!-- Details Grid -->
          <div class="mt-8 space-y-4">
            <div class="grid grid-cols-2 gap-4">
               <div class="bg-slate-700/50 p-3 rounded-lg border border-white/5">
                 <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">Born</p>
                 <p class="text-white font-medium">{{ member.date_of_birth || 'Unknown' }}</p>
               </div>
               <div class="bg-slate-700/50 p-3 rounded-lg border border-white/5">
                 <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">Blood Group</p>
                 <p class="text-white font-medium">{{ member.blood_group || '-' }}</p>
               </div>
               <div class="bg-slate-700/50 p-3 rounded-lg border border-white/5">
                 <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">Occupation</p>
                 <p class="text-white font-medium">{{ member.occupation || '-' }}</p>
               </div>
               <div class="bg-slate-700/50 p-3 rounded-lg border border-white/5">
                 <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">Age</p>
                 <p class="text-white font-medium">{{ member.age || '-' }}</p>
               </div>
            </div>

            <!-- Bio -->
            <div v-if="member.bio" class="bg-slate-700/30 p-4 rounded-lg border border-white/5">
               <p class="text-gray-300 text-sm leading-relaxed italic">"{{ member.bio }}"</p>
            </div>

            <!-- Family Links -->
             <div class="pt-4 border-t border-white/10">
               <p class="text-xs text-gray-400 uppercase tracking-wider mb-3">Family Connections</p>
               <div class="flex flex-wrap gap-2">
                 <span v-if="member.spouse" class="px-3 py-1 bg-pink-500/10 text-pink-400 rounded-full text-xs font-semibold border border-pink-500/20">
                   Spouse: Verified
                 </span>
                 <span v-if="member.parents && member.parents.length" class="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs font-semibold border border-blue-500/20">
                   Parents: {{ member.parents.length }}
                 </span>
                 <span v-if="member.children && member.children.length" class="px-3 py-1 bg-green-500/10 text-green-400 rounded-full text-xs font-semibold border border-green-500/20">
                   Children: {{ member.children.length }}
                 </span>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  member: Object
})
defineEmits(['close'])
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
