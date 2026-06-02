<template>
  <div
    class="gallery-item"
    :title="image.title || ''"
    role="button"
    tabindex="0"
    @click.stop="$emit('open', image)"
    @keydown.enter.stop="$emit('open', image)"
    @contextmenu.prevent
  >
    <div v-if="!loaded || failed" class="gallery-placeholder" :class="{ 'gallery-placeholder--video': image.media_type === 'video' }">
      <div class="gallery-placeholder-spinner"></div>
      <div class="gallery-placeholder-text">{{ failed ? t('gallery.errors.loadFailed') : t('gallery.status.loading') }}</div>
    </div>

    <img
      v-if="image.media_type !== 'video'"
      :data-src="image.photo"
      :alt="image.title || t('gallery.imageAlt')"
      loading="lazy"
      class="gallery-img"
      @load="loaded = true"
      @error="failed = true; loaded = true"
      ref="imgEl"
      draggable="false"
    />

    <video
      v-else
      :src="image.photo"
      class="gallery-img gallery-video"
      muted
      playsinline
      preload="metadata"
      @loadeddata="loaded = true"
      @error="failed = true; loaded = true"
      ref="imgEl"
      draggable="false"
    />

    <div v-if="image.media_type === 'video'" class="gallery-video-badge">Video</div>

    <!-- Removed committee member display from card bottom -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface GalleryItem {
  id: number
  photo: string
  media_type?: 'image' | 'video'
  title?: string
  created_at?: string
}

const props = defineProps<{ image: GalleryItem }>()
const emit = defineEmits(['open'])
const imgEl = ref<HTMLElement | null>(null)
const loaded = ref(false)
const failed = ref(false)
const { locale, t } = useI18n()

const formattedDate = computed(() => {
  if (!props.image?.created_at) return ''
  try {
    const dateLocale = locale.value === 'ml' ? 'ml-IN' : 'en-US'
    return new Date(props.image.created_at).toLocaleDateString(dateLocale)
  } catch {
    return props.image.created_at
  }
})

let io: IntersectionObserver | null = null

onMounted(() => {
  loaded.value = false
  failed.value = false
  // Ensure src set when element becomes visible
  if (imgEl.value) {
    io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          if (imgEl.value instanceof HTMLImageElement && imgEl.value.dataset.src) {
            imgEl.value.src = imgEl.value.dataset.src
          }
          io?.disconnect()
        }
      })
    })
    io.observe(imgEl.value)
  }
})

onBeforeUnmount(() => {
  io?.disconnect()
})
</script>

<style scoped>
.gallery-item {
  display: block;
  width: 100%;
  margin: 0;
  padding: 0;
  position: relative;
  break-inside: avoid;
  cursor: pointer;
  overflow: hidden;
}

.gallery-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  color: #64748b;
  z-index: 1;
}

.gallery-placeholder--video {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #cbd5e1;
}

.gallery-placeholder-spinner {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 3px solid rgba(100, 116, 139, 0.18);
  border-top-color: #c9a96e;
  animation: gallery-spin 0.8s linear infinite;
}

.gallery-placeholder--video .gallery-placeholder-spinner {
  border-color: rgba(203, 213, 225, 0.15);
  border-top-color: #e2c56f;
}

.gallery-placeholder-text {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

@keyframes gallery-spin {
  to { transform: rotate(360deg); }
}

.gallery-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 0;
  background: #f3f4f6;
  transition: opacity 180ms ease-in-out, transform 160ms ease;
  will-change: opacity, transform;
  -webkit-user-drag: none;
  user-select: none;
}

.gallery-video {
  aspect-ratio: 1 / 1;
  object-fit: cover;
  background: #0f172a;
}

.gallery-video-badge {
  position: absolute;
  left: 10px;
  top: 10px;
  z-index: 2;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.72);
  color: white;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.gallery-item:active .gallery-img { transform: scale(0.995) }

.meta {
  position: absolute;
  left: 8px;
  bottom: 8px;
  background: rgba(0,0,0,0.5);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
}

.date { font-weight: 500 }

@media (max-width: 768px) {
  .gallery-item {
    aspect-ratio: 1 / 1;
  }

  .gallery-img {
    height: 100%;
    object-fit: cover;
    object-position: center;
  }
}
</style>
