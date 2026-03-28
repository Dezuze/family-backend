<template>
    <div class="min-h-screen bg-slate-50 flex flex-col items-center px-4 pt-32 pb-16 text-slate-800 font-sans overflow-x-hidden">
        <div class="w-full max-w-7xl mx-auto">
        <div class="mb-12 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
            {{ t('history.header.title') }}
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
    </div>
        
                <div class="bg-white rounded-xl p-3 md:p-6 backdrop-blur-sm border border-slate-200 shadow-xl w-full overflow-hidden">
            <client-only>
                        <div class="w-full h-[62vh] md:h-[70vh] lg:h-[74vh]">
                <PdfViewer :src="pdfUrl" />
            </div>
            </client-only>
        </div>

                <p class="text-sm text-slate-500 mt-6 text-center">{{ t('history.header.hint') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '#imports'
import { useI18n } from 'vue-i18n'
import PdfViewer from '~/components/PdfViewer.vue'

const pdfUrl = '/Document/history.pdf'
const { t } = useI18n()

useHead(() => ({
    title: t('history.meta.title')
}))
</script>

<style scoped>
/* center page content */
</style>
