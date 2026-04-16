<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans pt-32 pb-16 px-4 md:px-12">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
          {{ t('contact.header.title') }}
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
          {{ t('contact.header.description') }}
        </p>
      </div>

      <!-- Contact Info -->
      <div class="space-y-8 max-w-3xl mx-auto">
        <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all">
          <h3 class="text-xl font-bold text-brand-gold mb-4 uppercase tracking-wide">{{ t('contact.info.emailTitle') }}</h3>
          <a href="mailto:kollamparambilkudumbam@gmail.com" class="text-slate-600 hover:text-brand-gold transition-colors flex items-center gap-2 font-medium break-all">
            <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            kollamparambilkudumbam@gmail.com
          </a>
        </div>

        <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all">
          <h3 class="text-xl font-bold text-brand-gold mb-4 uppercase tracking-wide">{{ t('contact.info.phoneTitle') }}</h3>
          <div class="space-y-3 text-slate-700 font-medium">
            <a href="tel:+919447077644" class="block hover:text-brand-gold transition-colors">9447077644 - Prof Saju Elias (Working President)</a>
            <a href="tel:+919447008165" class="block hover:text-brand-gold transition-colors">9447008165 - Mr Jojo Jacob (Secretary)</a>
            <a href="tel:+919605957133" class="block hover:text-brand-gold transition-colors">9605957133 - Mr Praveen Mani (Treasurer)</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '#imports'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

useHead(() => ({
  title: t('contact.meta.title')
}))
</script>
