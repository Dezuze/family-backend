<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const open = ref(false)
const email = ref('')
const password = ref('')
const sponsorId = ref('')

const registering = ref(false)
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const error = ref('')

const menuOpen = ref(false)

// Check for referral link
onMounted(() => {
  if (route.query.ref) {
      sponsorId.value = route.query.ref as string
      open.value = true
      registering.value = true
  }
})

const displayName = computed<string>(() => {
  const u = auth.user as { name?: string; email?: string } | null
  return (u?.name ?? u?.email) ?? ''
})

const initials = computed<string>(() => {
  const n = (displayName.value ?? '').trim()
  if (!n) return ''
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return (parts[0] ?? '').slice(0, 2).toUpperCase()
  const a = parts[0]?.charAt(0) ?? ''
  const b = parts[parts.length - 1]?.charAt(0) ?? ''
  return (a + b).toUpperCase()
})

const userPhoto = computed<string>(() => {
  const u = auth.user as any
  // Check for various photo fields
  return u?.photo || u?.image || u?.profile_pic || ''
})

const toggle = () => (open.value = !open.value)
const close = () => {
  open.value = false
  error.value = ''
  registering.value = false
}

const submit = async () => {
  error.value = ''
  const res: any = await (auth as any).login(email.value, password.value)
  if (res && res.ok) {
    close()
  } else {
    const msg = (res && res.error) || 'Invalid email or password'
    error.value = typeof msg === 'string' ? msg : 'Invalid email or password'
  }
}

const logout = async () => {
  await (auth as any).logout()
  menuOpen.value = false
  router.push('/')
}

const openEdit = () => {
  menuOpen.value = false
  router.push('/onboarding')
}

const copyInvite = () => {
    menuOpen.value = false
    const u = auth.user as any
    if (u && u.member_id) {
        const link = `${window.location.origin}/?ref=${u.member_id}`
        navigator.clipboard.writeText(link)
        alert('Invite link copied to clipboard!')
    } else {
        alert('Member ID not found.')
    }
}

const register = async () => {
  error.value = ''
  if (!regName.value || !regEmail.value || !regPassword.value || !sponsorId.value) {
    error.value = 'Please fill all fields, including Sponsor ID.'
    return
  }

  const signupResult = await (auth as any).signup({ 
      username: regName.value || regEmail.value, 
      email: regEmail.value, 
      sponsor_id: sponsorId.value, 
      password: regPassword.value 
  })

  if (!signupResult || !signupResult.ok) {
    const msg = (signupResult && signupResult.error && signupResult.error.error) || 'Signup failed'
    error.value = typeof msg === 'string' ? msg : 'Signup failed'
    return
  }

  // Success 
  close()
  router.push('/onboarding')
}

defineExpose({ toggle })
</script>

<template>
  <!-- LOGIN / AVATAR (keeps yellow bar) -->
  <div class="z-20 h-15 w-full lg:w-40 flex items-center
           transition-all duration-500 max-lg:rounded-4xl
           lg:rounded-br-[80px] lg:rounded-tr-[10px]"
       style="background: linear-gradient(to bottom, #A08050, #6d5030);">
    <div class="w-full">
      <div v-if="!auth.isAuthenticated">
        <button
          @click="toggle"
          class="w-full lg:pl-10 font-bold text-white py-3
                 transition lg:rounded-br-[80px] lg:rounded-tr-[10px] lg:hover:rounded-br-[100px] lg:hover:rounded-tr-[10px] hover:brightness-110 active:scale-95"
        >
          Login
        </button>
      </div>

      <div v-else class="flex items-center justify-end pr-4 w-full h-full">
        <div class="relative flex items-center gap-3">
          <!-- Name (Visible on Mobile, Hidden on Desktop to keep pill shape clean) -->
          <span class="text-white font-bold text-sm md:text-base lg:hidden drop-shadow-md">{{ displayName }}</span>

          <button @click="menuOpen = !menuOpen" class="h-10 w-10 rounded-full bg-[#1A3C3B] border-2 border-white/20 text-white flex items-center justify-center font-bold overflow-hidden shrink-0 shadow-md transition-transform active:scale-95">
             <img v-if="userPhoto" :src="userPhoto" alt="User" class="w-full h-full object-cover" />
             <span v-else>{{ initials }}</span>
          </button>

          <div v-if="menuOpen" class="absolute z-50 top-12 right-0 w-48 bg-white rounded-lg shadow-xl p-2 text-sm text-gray-800 border border-gray-100 flex flex-col gap-1">
            <div class="px-2 py-1.5 font-bold text-[#1A3C3B] border-b border-gray-100 mb-1 lg:block hidden">{{ displayName }}</div>
            <button @click="copyInvite" class="w-full text-left px-2 py-1.5 hover:bg-slate-100 rounded-md transition-colors text-amber-600 font-bold">Invite Member</button>
            <button @click="openEdit" class="w-full text-left px-2 py-1.5 hover:bg-slate-100 rounded-md transition-colors">Edit profile</button>
            <button @click="logout" class="w-full text-left px-2 py-1.5 hover:bg-slate-100 rounded-md transition-colors text-red-600">Logout</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- BACKDROP -->
  <teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        @click="close"
        class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
      />
    </Transition>

    <!-- LOGIN MODAL -->
    <Transition name="scale-fade">
      <div v-if="open" class="fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl p-6 w-80 shadow-xl">
      <template v-if="!registering">
        <h2 class="text-xl font-bold mb-4 text-[#1A3C3B]">Login</h2>
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full mb-3 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#A08050]"
        />

        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full mb-3 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#A08050]"
        />

        <div v-if="error" class="text-sm text-red-600 mb-2">{{ error }}</div>

        <button
          @click.prevent="submit"
          class="w-full bg-linear-to-b from-[#A08050] to-[#6d5030] py-2 rounded-lg text-white font-bold
                 transition hover:brightness-110 active:scale-95"
        >
          Continue
        </button>

        <div class="mt-4 text-center text-sm">
          <button @click="registering = true" class="text-lime-800 font-medium">Create an account</button>
        </div>
      </template>

      <template v-else>
        <h2 class="text-xl font-bold mb-4 text-lime-800">Create Account</h2>

        <div class="mb-4 text-xs text-gray-500">
           Enter your Sponsor's Member ID to join.
        </div>

        <input v-model="sponsorId" placeholder="Sponsor Member ID" class="w-full mb-3 px-3 py-2 border rounded-lg border-amber-500 bg-amber-50" />
        <input v-model="regName" placeholder="Full name" class="w-full mb-3 px-3 py-2 border rounded-lg" />
        <input v-model="regEmail" placeholder="Email" class="w-full mb-3 px-3 py-2 border rounded-lg" />
        <input v-model="regPassword" type="password" placeholder="Password" class="w-full mb-3 px-3 py-2 border rounded-lg" />

        <div v-if="error" class="text-sm text-red-600 mb-2">{{ error }}</div>

        <div class="flex gap-2">
          <button @click.prevent="register" class="flex-1 bg-lime-700 text-white py-2 rounded">Create</button>
          <button @click.prevent="registering = false" class="flex-1 bg-slate-100 py-2 rounded">Cancel</button>
        </div>
      </template>
    </div>
    </Transition>
  </teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: all 0.3s ease;
}
.scale-fade-enter-from,
.scale-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.95);
}
</style>
