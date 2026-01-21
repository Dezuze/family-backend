<template>
  <div :class="cardClass" class="bg-white rounded-lg shadow-sm p-4 flex items-center gap-4 border border-transparent hover:shadow-md transition">
    <div class="flex-shrink-0">
      <img v-if="member.photo" :src="member.photo" alt="photo" class="w-16 h-16 rounded-full object-cover" />
      <div v-else class="w-16 h-16 rounded-full bg-brand.gold/20 flex items-center justify-center text-lg font-semibold text-brand.slate">
        {{ initials }}
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold truncate text-brand.slate">{{ member.name }}</h3>
        <span class="text-xs text-gray-500">#{{ member.id }}</span>
      </div>
      <p class="text-xs text-gray-500 truncate">
        <span v-if="member.relation">{{ member.relation }}</span>
        <span v-if="member.age"> • {{ member.age }}y</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FamilyMember } from '~/types/family'
import { computed } from 'vue'

const props = defineProps<{ member: FamilyMember; variant?: 'default' | 'compact' | 'list' }>()

const initials = computed(() => {
  const n = props.member?.name ?? ''
  return n.split(' ').map((s) => s.charAt(0).toUpperCase()).slice(0,2).join('')
})

const cardClass = computed(() => {
  if (props.variant === 'compact') return 'py-2 px-3'
  if (props.variant === 'list') return 'w-full'
  return 'py-3 px-4'
})
</script>

<style scoped>
/* minimal scoped styling; layout handled via Tailwind */
</style>
