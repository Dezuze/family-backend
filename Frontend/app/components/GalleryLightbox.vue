<template>
  <div class="gl-overlay" @click.self="close">
    <div class="gl-inner">
        <button class="gl-close" @click.stop="close">✕</button>
        <button class="gl-prev" @click.stop="prev">◀</button>

        <div class="gl-img" :style="{ backgroundImage: `url(${image.photo})` }" role="img" :aria-label="image.title || 'Image'"></div>
        <!-- blocker captures contextmenu/long-press to make downloading harder -->
        <div class="gl-img-blocker" @contextmenu.prevent @touchstart.prevent @mousedown.prevent></div>

        <button class="gl-next" @click.stop="next">▶</button>

        <div class="gl-caption">
          <div class="title">{{ image.title }}</div>
          <div class="date">{{ formattedDate }}</div>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed } from 'vue'

interface GalleryItem {
  id: number
  photo: string
  title?: string
  created_at?: string | null
}

const props = defineProps<{ image: GalleryItem }>()
const emit = defineEmits(['close', 'next', 'prev'])

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
  try { return new Date(props.image.created_at).toLocaleString() } catch { return props.image.created_at as any }
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
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
}
.gl-inner { position: relative; max-width: 95%; max-height: 95%; display:flex; align-items:center; touch-action: none }
.gl-img { width: 100%; height: 80vh; border-radius: 8px; display:block; margin:0 40px; background-size: contain; background-position: center; background-repeat: no-repeat; -webkit-user-drag: none; user-select: none }
.gl-img-blocker { position: absolute; left: 0; right: 0; top: 0; bottom: 0; z-index: 2 }
.gl-close { position: absolute; right: -8px; top: -36px; background: transparent; color: white; border: none; font-size: 24px }
.gl-prev, .gl-next { position: absolute; background: rgba(0,0,0,0.4); color: white; border: none; font-size: 22px; padding: 8px 12px; border-radius: 6px }
.gl-prev { left: -60px }
.gl-next { right: -60px }
.gl-caption { position: absolute; left: 0; bottom: -56px; color: white; width: 100%; text-align: center }
.gl-caption .title { font-weight: 600 }
.gl-caption .date { font-size: 12px; color: #d1d5db }

@media (max-width: 700px) {
  .gl-prev { left: 8px }
  .gl-next { right: 8px }
  .gl-img { margin: 0 12px }
  .gl-close { right: 8px; top: 8px }
}
</style>
