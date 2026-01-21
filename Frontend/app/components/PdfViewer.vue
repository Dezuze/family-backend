<template>
  <div class="w-full flex justify-center">
    <div class="pdf-frame" ref="frameRef">
        <div class="pdf-inner" ref="innerRef" @touchstart.passive="onTouchStart" @touchend.passive="onTouchEnd">
          <canvas v-for="c in canvases" :key="c.key" :ref="el => registerCanvas(el, c.index)" class="pdf-canvas" />
        </div>
        <div v-if="loading" class="absolute inset-0 bg-white/80 z-20 flex flex-col gap-3 items-center justify-center backdrop-blur-sm">
            <div class="w-10 h-10 border-4 border-gray-300 border-t-indigo-600 rounded-full animate-spin"></div>
            <span class="text-sm font-medium text-gray-700">Loading Document...</span>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useHead } from '#imports'

const props = defineProps<{ src: string; initialPage?: number }>()

const frameRef = ref<HTMLElement | null>(null)
const innerRef = ref<HTMLElement | null>(null)
// Non-reactive variable for PDF document to avoid Proxy/Private field issues
let pdfDoc: any = null

const error = ref<string | null>(null)
const loading = ref(true)
const canvases = ref<Array<{ key: string; index: number }>>([])
const canvasEls = ref<HTMLCanvasElement[]>([])
const currentPage = ref(props.initialPage ?? 1)
const isTwoUp = ref(false)
const numPages = ref(0) // Reactive tracker for pages

let touchStartX = 0

// Inject PDF.js from CDN
useHead({
  script: [
    {
      src: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
      onload: () => {
        console.debug('PDF.js CDN script loaded')
        // Give it a moment to initialize global
        setTimeout(loadPdf, 100)
      },
      onerror: (e) => {
        console.error('Failed to load PDF.js from CDN', e)
        error.value = 'Failed to load PDF library'
        loading.value = false
      }
    }
  ]
})

function registerCanvas(el: unknown, index: number) {
  const canvas = el as HTMLCanvasElement | null
  if (!canvas) {
    return
  }
  canvasEls.value[index] = canvas
}

async function loadPdf() {
  loading.value = true
  
  // Access global variable injected by CDN script
  const pdfjsLib = (window as any).pdfjsLib
  if (!pdfjsLib) {
    if (loading.value) setTimeout(loadPdf, 200) // retry if not ready
    return
  }

  // Set worker to CDN as well to match version perfectly
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'

  try {
    // Force disable worker to avoid Cross-Origin worker issues with CDN
    const loadingTask = pdfjsLib.getDocument({ url: props.src, disableWorker: true })
    pdfDoc = await loadingTask.promise
    numPages.value = pdfDoc.numPages
    
    console.debug('PDF loaded via CDN, numPages=', numPages.value)
    updateCanvases()
    await nextTick()
    await renderVisible()
    loading.value = false
  } catch (err) {
    console.error('PDF load/render error', err)
    error.value = String(err)
    loading.value = false
  }
}

function updateCanvases() {
  const w = window.innerWidth
  isTwoUp.value = w >= 768
  canvases.value = []
  if (isTwoUp.value) {
    canvases.value.push({ key: 'left', index: 0 })
    canvases.value.push({ key: 'right', index: 1 })
  } else {
    canvases.value.push({ key: 'single', index: 0 })
  }
  canvasEls.value = []
}

async function renderVisible() {
  if (!pdfDoc) return
  const total = numPages.value
  const pages: number[] = []
  if (isTwoUp.value) {
    pages.push(currentPage.value)
    if (currentPage.value + 1 <= total) pages.push(currentPage.value + 1)
  } else {
    pages.push(currentPage.value)
  }

  // Iterate over all available canvases to render or clear them
  for (let i = 0; i < canvasEls.value.length; i++) {
    const canvas = canvasEls.value[i]
    if (!canvas) continue
    const ctx = canvas.getContext('2d')
    if (!ctx) continue

    // If we have a page for this slot, render it
    if (i < pages.length) {
        const pnum = pages[i]
        const page = await pdfDoc.getPage(pnum)
        const viewport = page.getViewport({ scale: 1 })

        // scale logic
        const container = innerRef.value
        let scale = 1
        if (container) {
           const containerWidth = container.clientWidth
           // In Two-Up mode, always divide by 2 to keep scale consistent
           const divisor = isTwoUp.value ? 2 : 1
           const maxWidth = (containerWidth - 8) / divisor
           scale = Math.min(3.0, maxWidth / viewport.width)
        }
        
        const v = page.getViewport({ scale })
        
        // High DPI Support
        const outputScale = window.devicePixelRatio || 1
        canvas.width = Math.floor(v.width * outputScale)
        canvas.height = Math.floor(v.height * outputScale)
        
        // Scale back down with CSS
        canvas.style.width = Math.floor(v.width) + 'px'
        canvas.style.height = Math.floor(v.height) + 'px'
        canvas.style.display = 'block' // Ensure visible

        const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null

        const renderContext = { 
            canvasContext: ctx, 
            viewport: v,
            transform: transform
        }
        await page.render(renderContext).promise
    } else {
        // No page for this slot (e.g. last page in two-up view), clear it
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        canvas.width = 0
        canvas.height = 0
        canvas.style.width = '0px'
        canvas.style.height = '0px'
        // Optional: hide it to collapse space if flex gap is an issue, 
        // though maintaining width might be better for layout stability.
        // For now, let's just make it blank/invisible.
        canvas.style.display = 'none' 
    }
  }
}

function nextPage() {
  const total = numPages.value
  if (isTwoUp.value) {
    if (currentPage.value + 2 <= total) currentPage.value += 2
    else if (currentPage.value + 1 <= total) currentPage.value += 1
  } else {
    if (currentPage.value < total) currentPage.value += 1
  }
}

function prevPage() {
  if (isTwoUp.value) {
    if (currentPage.value - 2 >= 1) currentPage.value -= 2
    else if (currentPage.value - 1 >= 1) currentPage.value -= 1
  } else {
    if (currentPage.value > 1) currentPage.value -= 1
  }
}

function onTouchStart(e: TouchEvent) {
  const ct = e.changedTouches
  if (!ct || ct.length === 0) return
  touchStartX = ct[0].clientX
}

function onTouchEnd(e: TouchEvent) {
  const ct = e.changedTouches
  if (!ct || ct.length === 0) return
  const dx = ct[0].clientX - touchStartX
  const thresh = 40
  if (dx < -thresh) nextPage()
  else if (dx > thresh) prevPage()
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') nextPage()
  if (e.key === 'ArrowLeft') prevPage()
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    // If library is already loaded (from previous nav), use it
    if ((window as any).pdfjsLib) {
        loadPdf()
    }
    // Else, script onload will call it
  }

  window.addEventListener('resize', () => {
    updateCanvases()
    setTimeout(async () => {
      await nextTick()
      renderVisible()
    }, 50)
  })
  window.addEventListener('keydown', onKey)
})

watch([currentPage, isTwoUp], async () => {
  await nextTick()
  renderVisible()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
})
</script>

<style scoped>
.pdf-frame {
  position: relative; /* For loading overlay */
  border: 8px solid #c59d0f;
  padding: 4px; /* Reduced usage of space */
  background: #fff8e1;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-width: 100%; /* Allow full width */
  width: 100%;
  display: flex;
  justify-content: center;
  min-height: 400px;
}
.pdf-inner {
  display: flex;
  gap: 4px; /* Tighter gap */
  justify-content: center;
  align-items: center;
  padding: 2px;
  width: 100%; /* Ensure it fills frame */
}
.pdf-canvas {
  background: white;
  display: block;
  max-width: 100%;
  height: auto;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
@media (max-width: 767px) {
  .pdf-frame { border-width: 6px; padding: 4px; }
  .pdf-inner { gap: 2px; }
}
</style>
