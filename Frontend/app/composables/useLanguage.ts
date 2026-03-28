import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import enMessages from '../../i18n/locales/en.json'
import mlMessages from '../../i18n/locales/ml.json'

type SiteLanguage = 'en' | 'ml'

const STORAGE_KEY = 'site-language'
let watchRegistered = false
let messagesHydrated = false

const messageCatalog: Record<SiteLanguage, Record<string, any>> = {
  en: enMessages as Record<string, any>,
  ml: mlMessages as Record<string, any>,
}

const normalizeLanguage = (lang: string | null | undefined): SiteLanguage => {
  return lang === 'ml' ? 'ml' : 'en'
}

const applyLanguageToDocument = (lang: SiteLanguage) => {
  if (!process.client) return

  document.documentElement.setAttribute('lang', lang)
  document.documentElement.classList.toggle('lang-ml', lang === 'ml')
  document.body.classList.toggle('lang-ml', lang === 'ml')
  localStorage.setItem(STORAGE_KEY, lang)
}

export const useLanguage = () => {
  const { locale, setLocaleMessage, getLocaleMessage } = useI18n()
  const currentLanguage = useState<SiteLanguage>('site-language', () => 'en')

  const ensureMessages = () => {
    if (messagesHydrated) return

    ;(['en', 'ml'] as SiteLanguage[]).forEach((lang) => {
      const currentMessages = getLocaleMessage(lang)
      const hasMessages = !!currentMessages && Object.keys(currentMessages).length > 0
      if (!hasMessages) {
        setLocaleMessage(lang, messageCatalog[lang])
      }
    })

    messagesHydrated = true
  }

  const syncLanguage = (lang: SiteLanguage) => {
    ensureMessages()
    const normalized = normalizeLanguage(lang)
    currentLanguage.value = normalized
    locale.value = normalized
    applyLanguageToDocument(normalized)
  }

  const initLanguage = () => {
    if (!process.client) return

    const saved = normalizeLanguage(localStorage.getItem(STORAGE_KEY) || locale.value)
    syncLanguage(saved)
  }

  if (process.client && !watchRegistered) {
    watchRegistered = true
    watch(currentLanguage, (lang) => {
      syncLanguage(normalizeLanguage(lang))
    })
  }

  const setLanguage = (lang: SiteLanguage) => {
    syncLanguage(normalizeLanguage(lang))
  }

  const reapplyLanguage = () => {
    applyLanguageToDocument(normalizeLanguage(currentLanguage.value))
  }

  return {
    currentLanguage,
    setLanguage,
    initLanguage,
    reapplyLanguage,
  }
}
