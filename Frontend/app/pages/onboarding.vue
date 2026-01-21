<template>
  <div class="min-h-screen bg-slate-900 text-white pt-32 pb-16 px-4 flex flex-col items-center">
    
    <div class="max-w-2xl w-full">
        <!-- Progress Steps -->
        <div class="flex items-center justify-center mb-8 gap-4">
             <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold', step >= 1 ? 'bg-amber-500 text-black' : 'bg-slate-700 text-gray-400']">1</div>
             <div class="h-1 w-12 bg-slate-700"></div>
             <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold', step >= 2 ? 'bg-amber-500 text-black' : 'bg-slate-700 text-gray-400']">2</div>
        </div>

        <div class="bg-slate-800 p-8 rounded-2xl border border-white/10 shadow-xl">
            <h1 class="text-3xl font-serif font-bold mb-2 text-center">Complete Your Profile</h1>
            <p class="text-gray-400 text-center mb-8">Help us build the family tree by adding your details.</p>

            <form @submit.prevent="saveProfile">
                
                <!-- Step 1: Personal Info -->
                <div v-if="step === 1" class="space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm text-gray-400 mb-2">Given Name</label>
                            <input v-model="form.name" type="text" class="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-white focus:border-amber-500 outline-none" placeholder="First Name">
                        </div>
                        <div>
                            <label class="block text-sm text-gray-400 mb-2">Date of Birth</label>
                            <input v-model="form.date_of_birth" type="date" class="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-white focus:border-amber-500 outline-none">
                        </div>
                    </div>

                    <div>
                         <label class="block text-sm text-gray-400 mb-2">Short Bio</label>
                         <textarea v-model="form.bio" rows="3" class="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-white focus:border-amber-500 outline-none" placeholder="Tell us about yourself..."></textarea>
                    </div>

                    <div class="grid grid-cols-2 gap-6">
                         <div>
                            <label class="block text-sm text-gray-400 mb-2">Blood Group</label>
                            <select v-model="form.blood_group" class="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-white focus:border-amber-500 outline-none">
                                <option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>O+</option><option>O-</option><option>AB+</option><option>AB-</option>
                            </select>
                        </div>
                         <div>
                            <label class="block text-sm text-gray-400 mb-2">Occupation</label>
                            <input v-model="form.occupation" type="text" class="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-white focus:border-amber-500 outline-none">
                        </div>
                    </div>
                </div>

                <!-- Step 2: Relations (Placeholder for now) -->
                <div v-if="step === 2" class="space-y-6">
                     <div class="bg-amber-900/20 p-4 rounded border border-amber-500/30 text-amber-200 text-sm">
                        Additional family linking features coming soon. For now, we will create your profile card.
                     </div>
                     
                     <div>
                        <label class="block text-sm text-gray-400 mb-2">Father's Name (Optional)</label>
                         <input v-model="form.father_name" type="text" class="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-white focus:border-amber-500 outline-none">
                     </div>
                </div>

                <!-- Actions -->
                <div class="mt-8 flex justify-between">
                    <button v-if="step > 1" type="button" @click="step--" class="text-gray-400 hover:text-white font-bold">Back</button>
                    <div v-else></div> <!-- spacer -->

                    <button v-if="step < 2" type="button" @click="step++" class="bg-amber-600 hover:bg-amber-500 text-white px-8 py-3 rounded-lg font-bold shadow-lg">Next</button>
                    <button v-else type="submit" class="bg-gradient-to-r from-amber-600 to-amber-500 hover:brightness-110 text-white px-8 py-3 rounded-lg font-bold shadow-lg">
                        {{ loading ? 'Saving...' : 'Finish Profile' }}
                    </button>
                </div>

            </form>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const step = ref(1)
const loading = ref(false)
const form = ref({
    name: auth.user?.name || '',
    date_of_birth: '',
    bio: '',
    blood_group: 'O+',
    occupation: '',
    father_name: ''
})

const saveProfile = async () => {
    loading.value = true
    try {
        const res = await fetch('http://localhost:8000/api/families/profile/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.token}` // Assuming token store
            },
            body: JSON.stringify(form.value)
        })
        
        if (res.ok) {
            router.push('/familytree')
        } else {
            alert('Failed to save profile')
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}
</script>
