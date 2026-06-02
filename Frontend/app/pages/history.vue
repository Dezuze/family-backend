<template>
    <div class="min-h-screen bg-slate-50 px-2 sm:px-4 pt-32 pb-10 text-slate-800 font-sans overflow-x-hidden">
        <div class="mx-auto flex min-h-[calc(100vh-10rem)] w-full max-w-full flex-col md:max-w-7xl">
            <div class="mb-8 text-center space-y-4">
                <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
                    {{ t('history.header.title') }}
                </h1>
                <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
            </div>

            <div class="flex flex-1 min-h-0 flex-col rounded-xl border border-slate-200 bg-white p-0 shadow-xl md:p-6">
                <client-only>
                    <div class="relative flex-1 min-h-0 overflow-hidden">
                        <PdfViewer ref="pdfRef" :src="pdfUrl" />

                        <!-- Navigation arrows overlay -->
                        <button
                            aria-label="Previous page"
                            @click="prev()"
                            class="absolute left-2 top-1/2 -translate-y-1/2 z-30 flex h-10 w-10 items-center justify-center rounded-full bg-white/45 shadow-md backdrop-blur-sm transition-colors hover:bg-white/70 md:bg-white/90 md:hover:bg-white"
                        >
                            <svg class="h-6 w-6 text-slate-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>

                        <button
                            aria-label="Next page"
                            @click="next()"
                            class="absolute right-2 top-1/2 -translate-y-1/2 z-30 flex h-10 w-10 items-center justify-center rounded-full bg-white/45 shadow-md backdrop-blur-sm transition-colors hover:bg-white/70 md:bg-white/90 md:hover:bg-white"
                        >
                            <svg class="h-6 w-6 text-slate-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                            </svg>
                        </button>

                        <!-- Page indicator (bottom center) -->
                        <div class="absolute bottom-3 left-1/2 -translate-x-1/2 z-30 rounded-full bg-black/60 px-3 py-1 text-white text-sm backdrop-blur-sm">
                            <span v-if="pageInfo">{{ pageInfo }}</span>
                        </div>
                    </div>
                </client-only>
            </div>

            <p class="mt-6 text-center text-sm text-slate-500">{{ t('history.header.hint') }}</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useHead } from '#imports'
import { useI18n } from 'vue-i18n'
import PdfViewer from '~/components/PdfViewer.vue'
import { ref, computed } from 'vue'

const pdfUrl = '/Document/history.pdf'
const { t } = useI18n()

const pdfRef = ref<any | null>(null)

const next = () => {
    pdfRef.value?.nextPage?.()
}

const prev = () => {
    pdfRef.value?.prevPage?.()
}

const pageInfo = computed(() => {
    const cur = pdfRef.value?.currentPage?.value ?? pdfRef.value?.currentPage ?? null
    const total = pdfRef.value?.numPages?.value ?? pdfRef.value?.numPages ?? null
    if (!cur || !total) return ''
    return `${cur} / ${total}`
})

useHead(() => ({
    title: t('history.meta.title')
}))
</script>

<style scoped>
/* center page content */
</style>
