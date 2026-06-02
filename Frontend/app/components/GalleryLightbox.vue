<template>
  <div class="gl-overlay" @click.self="close">
    <div class="gl-inner">
        <!-- Close button -->
        <button class="gl-close" @click.stop="close" :aria-label="t('gallery.lightbox.close')">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <!-- Prev button -->
        <button class="gl-prev" @click.stop="prev" :aria-label="t('gallery.lightbox.previous')">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        </button>

        <div class="gl-content-wrapper">
          <!-- Loading Spinner -->
          <div v-if="loading" class="gl-loading">
            <div class="gl-spinner"></div>
          </div>

          <img
            v-if="!isVideo"
            class="gl-img"
            :class="{ 'opacity-0': loading }"
            :src="image.photo"
            :alt="image.title || t('gallery.lightbox.imageFallback')"
            @load="handleLoad"
          />

          <video
            v-else
            class="gl-video"
            controls
            autoplay
            muted
            playsinline
            preload="metadata"
            :class="{ 'opacity-0': loading }"
            :src="image.photo"
            @loadeddata="handleLoad"
          />
          
          <!-- Hidden preload element keeps image/video load state consistent -->
          <img v-if="!isVideo" :src="image.photo" @load="handleLoad" class="hidden" alt="" />

          <!-- blocker captures contextmenu/long-press to make downloading harder -->
          <div class="gl-img-blocker" @contextmenu.prevent @touchstart.prevent @mousedown.prevent></div>
        </div>

        <!-- Next button -->
        <button class="gl-next" @click.stop="next" :aria-label="t('gallery.lightbox.next')">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </button>

        <button class="gl-delete" @click.stop="$emit('delete', image)" :aria-label="t('gallery.lightbox.delete')">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v3m-4 0h14"></path></svg>
        </button>

        <div class="gl-caption" v-if="image.title || image.created_at">
          <div class="title" v-if="image.title">{{ image.title }}</div>
          <div class="date" v-if="image.created_at">{{ formattedDate }}</div>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

interface GalleryItem {
  id: number
  photo: string
  media_type?: 'image' | 'video'
  title?: string
  created_at?: string | null
}

const props = defineProps<{ image: GalleryItem }>()
const emit = defineEmits(['close', 'next', 'prev', 'delete'])
const { locale, t } = useI18n()

const loading = ref(true)

const isVideo = computed(() => props.image?.media_type === 'video')

const handleLoad = () => {
  loading.value = false
}

// Reset loading state when image changes (next/prev)
watch(() => props.image.id, () => {
  loading.value = true
})

watch(isVideo, () => {
  loading.value = true
})

const close = () => emit('close')
const next = () => emit('next')
const prev = () => emit('prev')

// Touch/swipe support for mobile
let touchStartX = 0
let touchStartY = 0
const SWIPE_THRESHOLD = 50

const onTouchStart = (e: TouchEvent) => {
  const t = e.touches?.[0]
  if (!t) return
  touchStartX = t.clientX
  touchStartY = t.clientY
}

const onTouchEnd = (e: TouchEvent) => {
  const t = e.changedTouches?.[0]
  if (!t) return
  const dx = t.clientX - touchStartX
  const dy = t.clientY - touchStartY
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > SWIPE_THRESHOLD) {
    if (dx < 0) next()
    else prev()
  }
}

const formattedDate = computed(() => {
  if (!props.image?.created_at) return ''
  try {
    const dateLocale = locale.value === 'ml' ? 'ml-IN' : 'en-US'
    return new Date(props.image.created_at).toLocaleString(dateLocale)
  } catch {
    return props.image.created_at as any
  }
})

const onKey = (e: KeyboardEvent) => {
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowRight') next()
  if (e.key === 'ArrowLeft') prev()
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('touchstart', onTouchStart, { passive: true })
  window.addEventListener('touchend', onTouchEnd)
  // Prevent background scroll while lightbox open
  document.body.style.overflow = 'hidden'
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('touchstart', onTouchStart)
  window.removeEventListener('touchend', onTouchEnd)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.gl-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}
.gl-inner { position: relative; width: 100%; max-width: 1200px; height: 90vh; display:flex; align-items:center; justify-content:center; touch-action: none; padding: 0 80px; }
.gl-content-wrapper { position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
  .gl-img {
    display: block;
    border-radius: 4px;
    -webkit-user-drag: none;
    user-select: none;
    transition: opacity 0.3s ease;
    /* Desktop: leave room for controls/padding; Mobile override below */
    max-width: calc(100vw - 160px);
    max-height: calc(100vh - 160px);
    width: auto;
    height: auto;
    object-fit: contain;
  }
.gl-video { max-width: calc(100vw - 160px); max-height: calc(100vh - 160px); border-radius: 14px; background: #050816; box-shadow: 0 20px 80px rgba(0,0,0,0.45); transition: opacity 0.3s ease; object-fit: contain; }
.gl-img.opacity-0 { opacity: 0; }
.gl-img-blocker { position: absolute; left: 0; right: 0; top: 0; bottom: 0; z-index: 2; cursor: default; }

.gl-loading { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 5; }
.gl-spinner { 
  width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #A08050; border-radius: 50%;
  animation: gl-spin 0.8s linear infinite;
}
@keyframes gl-spin { to { transform: rotate(360deg); } }

.gl-close { 
  position: absolute; right: 20px; top: 20px; background: rgba(0,0,0,0.3); color: white; border: none; 
  padding: 8px; border-radius: 50%; z-index: 1001; cursor: pointer; transition: background 0.2s;
}
.gl-close:hover { background: rgba(255,255,255,0.1); }

.gl-prev, .gl-next, .gl-delete { 
  position: absolute; background: rgba(255,255,255,0.05); color: white; border: none; 
  width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;
  border-radius: 50%; z-index: 1001; cursor: pointer; transition: all 0.2s;
}
.gl-prev:hover, .gl-next:hover, .gl-delete:hover { background: rgba(255,255,255,0.15); scale: 1.1; }
.gl-prev { left: 16px }
.gl-next { right: 16px }
.gl-delete { right: 74px }

.gl-caption { position: absolute; left: 0; bottom: 20px; color: white; width: 100%; text-align: center; z-index: 1001; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
.gl-caption .title { font-weight: 600; font-size: 1.1rem; margin-bottom: 4px; }
.gl-caption .date { font-size: 13px; color: #a1a1aa }

.hidden { display: none; }

@media (max-width: 768px) {
  .gl-inner { max-width: none; height: 100vh; padding: 0; }
  .gl-prev, .gl-next { width: 40px; height: 40px; background: rgba(0,0,0,0.2); }
  .gl-delete { width: 40px; height: 40px; right: 56px; background: rgba(0,0,0,0.2); }
  .gl-img, .gl-video { max-width: 100vw; max-height: 100vh; }
  .gl-prev { left: 8px }
  .gl-next { right: 8px }
  .gl-close { right: 10px; top: 10px; background: rgba(0,0,0,0.5); }
}
</style>
