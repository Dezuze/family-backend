<template>
  <section class="relative min-h-screen overflow-hidden bg-linear-to-br from-[#1b3d3a] via-[#285652] to-[#c89b5c] px-4 pb-16 pt-28 text-white sm:px-8">
    <div class="pointer-events-none absolute -left-24 top-20 h-72 w-72 rounded-full bg-white/15 blur-3xl"></div>
    <div class="pointer-events-none absolute -right-20 bottom-0 h-96 w-96 rounded-full bg-[#13312f]/50 blur-3xl"></div>

    <div class="relative mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-5">
      <div class="rounded-3xl border border-white/20 bg-white/10 p-8 backdrop-blur-md lg:col-span-3">
        <p class="mb-3 text-xs font-black uppercase tracking-[0.25em] text-white/75">Support The Family Mission</p>
        <h1 class="mb-2 font-serif text-4xl font-bold leading-tight sm:text-5xl">Digital Donation</h1>
        <p class="mb-8 max-w-xl text-sm text-white/85 sm:text-base">
          Contribute securely using Razorpay UPI, cards, or net banking. A verified receipt PDF is generated instantly after payment.
        </p>

        <form class="grid gap-4 sm:grid-cols-2" @submit.prevent="payNow">
          <label class="sm:col-span-2">
            <span class="mb-1 block text-xs font-bold uppercase tracking-widest text-white/80">Full Name</span>
            <input v-model="form.donor_name" type="text" required class="w-full rounded-xl border border-white/30 bg-white/90 px-4 py-3 text-slate-900 outline-none ring-brand-gold transition focus:ring-2" placeholder="Your full name" />
          </label>

          <label>
            <span class="mb-1 block text-xs font-bold uppercase tracking-widest text-white/80">Email</span>
            <input v-model="form.donor_email" type="email" class="w-full rounded-xl border border-white/30 bg-white/90 px-4 py-3 text-slate-900 outline-none ring-brand-gold transition focus:ring-2" placeholder="name@example.com" />
          </label>

          <label>
            <span class="mb-1 block text-xs font-bold uppercase tracking-widest text-white/80">Phone</span>
            <input v-model="form.donor_phone" type="tel" class="w-full rounded-xl border border-white/30 bg-white/90 px-4 py-3 text-slate-900 outline-none ring-brand-gold transition focus:ring-2" placeholder="10-digit mobile" />
          </label>

          <label>
            <span class="mb-1 block text-xs font-bold uppercase tracking-widest text-white/80">Amount (INR)</span>
            <input v-model.number="form.amount" type="number" min="1" step="1" required class="w-full rounded-xl border border-white/30 bg-white/90 px-4 py-3 text-slate-900 outline-none ring-brand-gold transition focus:ring-2" placeholder="100" />
          </label>

          <label>
            <span class="mb-1 block text-xs font-bold uppercase tracking-widest text-white/80">Purpose</span>
            <input v-model="form.purpose" type="text" class="w-full rounded-xl border border-white/30 bg-white/90 px-4 py-3 text-slate-900 outline-none ring-brand-gold transition focus:ring-2" placeholder="General donation" />
          </label>

          <div class="sm:col-span-2 mt-2 flex flex-wrap items-center gap-3">
            <button type="submit" :disabled="loading" class="rounded-xl bg-black px-6 py-3 text-sm font-black uppercase tracking-widest text-white transition hover:bg-black/85 disabled:cursor-not-allowed disabled:opacity-60">
              {{ loading ? 'Processing...' : 'Pay With Razorpay' }}
            </button>
            <a v-if="latestReceiptUrl" :href="latestReceiptUrl" target="_blank" rel="noopener" class="rounded-xl border border-white/45 bg-white/10 px-6 py-3 text-sm font-black uppercase tracking-widest text-white transition hover:bg-white/20">
              Download Latest Receipt
            </a>
          </div>
        </form>

        <p v-if="message" class="mt-5 rounded-xl border border-white/25 bg-black/20 px-4 py-3 text-sm">{{ message }}</p>
      </div>

      <div class="space-y-4 rounded-3xl border border-white/20 bg-black/25 p-6 backdrop-blur-md lg:col-span-2">
        <h2 class="font-serif text-2xl font-bold">Recent Donations</h2>
        <p class="text-xs text-white/80">Visible when you are logged in. Each successful payment generates a downloadable PDF receipt.</p>

        <div v-if="historyLoading" class="space-y-3">
          <div v-for="n in 4" :key="n" class="h-16 animate-pulse rounded-xl bg-white/15"></div>
        </div>

        <div v-else-if="donations.length" class="space-y-3">
          <article v-for="item in donations" :key="item.public_id" class="rounded-xl border border-white/15 bg-white/8 p-4">
            <div class="mb-1 flex items-center justify-between text-xs uppercase tracking-wider text-white/80">
              <span>{{ item.status }}</span>
              <span>{{ formatDate(item.created_at) }}</span>
            </div>
            <p class="text-lg font-bold">INR {{ item.amount }}</p>
            <p class="text-xs text-white/75">{{ item.purpose || 'General Donation' }}</p>
            <p v-if="item.receipt_number" class="mt-2 text-[11px] font-semibold text-[#f5d7a9]">Receipt: {{ item.receipt_number }}</p>
            <a
              v-if="item.receipt_url"
              :href="item.receipt_url"
              target="_blank"
              rel="noopener"
              class="mt-2 inline-block text-xs font-bold uppercase tracking-wide text-white underline decoration-white/50 underline-offset-3 hover:text-[#f5d7a9]"
            >
              Download Receipt
            </a>
          </article>
        </div>

        <p v-else class="rounded-xl border border-white/15 bg-white/8 px-4 py-5 text-sm text-white/85">No donations found for this account yet.</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useHead, useRuntimeConfig } from '#imports'

declare global {
  interface Window {
    Razorpay?: any
  }
}

interface DonationItem {
  public_id: string
  amount: string
  status: string
  purpose?: string | null
  receipt_number?: string | null
  receipt_url?: string | null
  created_at: string
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

const loading = ref(false)
const historyLoading = ref(true)
const message = ref('')
const latestReceiptUrl = ref('')
const donations = ref<DonationItem[]>([])

const form = reactive({
  donor_name: '',
  donor_email: '',
  donor_phone: '',
  amount: 100,
  purpose: '',
})

useHead({
  title: 'Donate | Kollamparambil Family',
})

function formatDate(value: string) {
  return new Date(value).toLocaleDateString()
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

async function ensureCsrf() {
  const res = await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
  const data = await res.json().catch(() => ({}))
  return getCookie('csrftoken') || data.csrfToken
}

async function loadRazorpayScript() {
  if (window.Razorpay) return true
  return await new Promise<boolean>((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.body.appendChild(script)
  })
}

async function fetchDonationHistory() {
  historyLoading.value = true
  try {
    const res = await fetch(`${apiBase}/api/payments/my-donations/`, { credentials: 'include' })
    if (!res.ok) {
      donations.value = []
      return
    }
    donations.value = await res.json()
  } catch {
    donations.value = []
  } finally {
    historyLoading.value = false
  }
}

async function payNow() {
  message.value = ''
  latestReceiptUrl.value = ''
  if (!form.amount || form.amount < 1) {
    message.value = 'Please enter a valid amount.'
    return
  }

  loading.value = true
  try {
    const scriptReady = await loadRazorpayScript()
    if (!scriptReady || !window.Razorpay) {
      message.value = 'Unable to load Razorpay checkout. Please try again.'
      return
    }

    const csrftoken = await ensureCsrf()
    const createRes = await fetch(`${apiBase}/api/payments/create-order/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
      },
      body: JSON.stringify(form),
    })
    const orderData = await createRes.json().catch(() => ({}))
    if (!createRes.ok) {
      message.value = orderData.error || 'Failed to create payment order.'
      return
    }

    const options = {
      key: orderData.key_id,
      amount: orderData.amount_paise,
      currency: orderData.currency,
      name: 'Kollamparambil Family Association',
      description: form.purpose || 'Donation',
      order_id: orderData.order_id,
      prefill: {
        name: form.donor_name,
        email: form.donor_email,
        contact: form.donor_phone,
      },
      method: {
        upi: true,
        card: true,
        netbanking: true,
        wallet: true,
      },
      theme: {
        color: '#1B3D3A',
      },
      handler: async (response: any) => {
        const verifyRes = await fetch(`${apiBase}/api/payments/verify/`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
          },
          body: JSON.stringify(response),
        })
        const verifyData = await verifyRes.json().catch(() => ({}))
        if (!verifyRes.ok) {
          message.value = verifyData.error || 'Payment verification failed.'
          return
        }

        latestReceiptUrl.value = verifyData.receipt_url || ''
        message.value = `Payment successful. Receipt ${verifyData.receipt_number} is ready.`
        await fetchDonationHistory()
      },
      modal: {
        ondismiss: () => {
          message.value = 'Payment cancelled before completion.'
        },
      },
    }

    const checkout = new window.Razorpay(options)
    checkout.open()
  } catch {
    message.value = 'Something went wrong while starting payment.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDonationHistory()
})
</script>
