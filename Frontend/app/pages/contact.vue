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

      <!-- Content Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
        
        <!-- Contact Info -->
        <div class="space-y-8">
          <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all">
            <h3 class="text-xl font-bold text-brand-gold mb-4 uppercase tracking-wide">{{ t('contact.info.addressTitle') }}</h3>
            <p class="text-slate-600 leading-relaxed font-medium">
              {{ t('contact.info.addressLine1') }}<br>
              {{ t('contact.info.addressLine2') }}<br>
              {{ t('contact.info.addressLine3') }}
            </p>
          </div>

          <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all">
            <h3 class="text-xl font-bold text-brand-gold mb-4 uppercase tracking-wide">{{ t('contact.info.emailTitle') }}</h3>
            <a href="mailto:contact@kollamparambil.com" class="text-slate-600 hover:text-brand-gold transition-colors flex items-center gap-2 font-medium">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
              contact@kollamparambil.com
            </a>
          </div>

          <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all">
            <h3 class="text-xl font-bold text-brand-gold mb-4 uppercase tracking-wide">{{ t('contact.info.phoneTitle') }}</h3>
             <a href="tel:+919876543210" class="text-slate-600 hover:text-brand-gold transition-colors flex items-center gap-2 font-medium">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
              +91 98765 43210
            </a>
          </div>
        </div>

        <!-- Message Form -->
        <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-xl">
          <h3 class="text-2xl font-bold text-slate-800 mb-6">{{ t('contact.form.title') }}</h3>
          <form class="space-y-6" @submit.prevent>
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-2">{{ t('contact.form.nameLabel') }}</label>
              <input type="text" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-4 py-3 text-slate-900 focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none transition-all placeholder-slate-400" :placeholder="t('contact.form.namePlaceholder')" />
            </div>
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-2">{{ t('contact.form.emailLabel') }}</label>
              <input type="email" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-4 py-3 text-slate-900 focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none transition-all placeholder-slate-400" :placeholder="t('contact.form.emailPlaceholder')" />
            </div>
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-2">{{ t('contact.form.messageLabel') }}</label>
              <textarea rows="4" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-4 py-3 text-slate-900 focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none transition-all placeholder-slate-400" :placeholder="t('contact.form.messagePlaceholder')"></textarea>
            </div>
            <button class="w-full bg-brand-gold hover:bg-brand-gold/90 text-white font-bold py-3 rounded-lg shadow-md transform transition active:scale-95">
              {{ t('contact.form.send') }}
            </button>
          </form>
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
