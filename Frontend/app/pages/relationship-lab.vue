<template>
  <main class="min-h-screen bg-slate-50 px-4 py-24 md:px-10">
    <div class="mx-auto max-w-6xl space-y-4 animate-in">
      <h1 class="text-3xl font-serif font-bold text-slate-900">{{ t('relationshipLab.page.title') }}</h1>
      <p class="text-sm text-slate-600">
        {{ t('relationshipLab.page.description') }}
      </p>

      <PerspectiveRelationshipTree />
    </div>
  </main>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<style scoped>
.animate-in {
  animation: fadeUp 0.45s ease both;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
