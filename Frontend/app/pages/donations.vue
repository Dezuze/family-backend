<script setup lang="ts">
import { ref } from 'vue'

const { t } = useI18n()

// Basic UI State
const selectedTier = ref<number | null>(null)
const customAmount = ref<string>('')
const loading = ref(false)

const tiers = [
  { id: 1, amount: 10, label: 'Supporter', description: 'Help us cover basic maintenance costs.' },
  { id: 2, amount: 50, label: 'Sponsor', description: 'Keep the platform running and secure for a year.' },
  { id: 3, amount: 100, label: 'Benefactor', description: 'Support the development of new features.' }
]

const selectTier = (amount: number) => {
    selectedTier.value = amount
    customAmount.value = ''
}

const handleCustomInput = () => {
    selectedTier.value = null
}

const initiateDonation = async () => {
    const amount = selectedTier.value || parseFloat(customAmount.value)
    if (!amount) return
    
    loading.value = true
    
    // Simulate API call for payment gateway initiation
    await new Promise(r => setTimeout(r, 1500))
    
    loading.value = false
    alert(`Thank you for your generous intended donation of $${amount}! (Payment Gateway Integration Pending)`)
}
</script>

<template>
    <div class="min-h-screen bg-slate-50 relative overflow-hidden flex flex-col">
        <!-- Background Pattern -->
        <div class="absolute inset-0 pointer-events-none opacity-40">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, rgba(148, 163, 184, 0.15) 1px, transparent 0); background-size: 32px 32px;"></div>
            <div class="absolute inset-0 bg-gradient-to-b from-transparent via-slate-50/50 to-slate-50"></div>
        </div>

        <Navbar />
        
        <main class="flex-1 w-full max-w-7xl mx-auto px-4 py-12 md:py-20 relative z-10">
            <div class="max-w-3xl mx-auto">
                <!-- Header -->
                <div class="text-center mb-12">
                    <div class="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-brand-gold/10 text-brand-gold text-sm font-bold tracking-widest uppercase mb-6">
                        Support Our Legacy
                    </div>
                    <h1 class="text-4xl md:text-5xl font-black text-slate-800 tracking-tight mb-6 leading-tight">
                        Help Us Preserve <br /> Our Family History
                    </h1>
                    <p class="text-lg text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
                        Maintaining the servers, databases, and expanding this platform requires resources. Your contribution ensures that future generations can continue to explore our shared heritage.
                    </p>
                </div>

                <!-- Donation Card -->
                <div class="bg-white/80 backdrop-blur-xl rounded-[2rem] p-8 md:p-12 shadow-2xl border border-slate-100">
                    
                    <h3 class="text-xl font-bold text-slate-800 mb-6">Select an amount</h3>
                    
                    <!-- Tiers -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                        <div 
                            v-for="tier in tiers" 
                            :key="tier.id"
                            @click="selectTier(tier.amount)"
                            class="relative p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 group overflow-hidden flex flex-col items-center text-center"
                            :class="selectedTier === tier.amount ? 'border-brand-gold bg-brand-gold/5 shadow-md shadow-brand-gold/10 scale-105' : 'border-slate-100 bg-white hover:border-brand-gold/40 hover:bg-slate-50'"
                        >
                            <div class="text-3xl font-black mb-2 transition-colors duration-300" :class="selectedTier === tier.amount ? 'text-brand-gold' : 'text-slate-800'">
                                ${{ tier.amount }}
                            </div>
                            <div class="text-sm font-bold uppercase tracking-wider mb-2 transition-colors duration-300" :class="selectedTier === tier.amount ? 'text-brand-brown' : 'text-slate-500'">
                                {{ tier.label }}
                            </div>
                            <div class="text-xs font-medium text-slate-500 leading-relaxed">
                                {{ tier.description }}
                            </div>
                        </div>
                    </div>

                    <!-- Custom Amount -->
                    <div class="mb-10">
                        <label class="block text-sm font-bold text-slate-600 uppercase tracking-wider mb-3 ml-1">Or enter custom amount</label>
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                                <span class="text-slate-400 font-bold text-lg">$</span>
                            </div>
                            <input 
                                v-model="customAmount"
                                @input="handleCustomInput"
                                type="number" 
                                min="1"
                                class="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl py-4 pl-10 pr-6 text-xl font-bold text-slate-800 focus:bg-white focus:border-brand-gold outline-none transition-all placeholder:text-slate-300"
                                placeholder="0.00"
                            >
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <button 
                        @click="initiateDonation"
                        :disabled="!selectedTier && !customAmount"
                        class="w-full py-5 rounded-2xl bg-gradient-to-r from-brand-gold to-brand-brown text-white font-bold text-lg shadow-lg hover:shadow-xl hover:shadow-brand-gold/20 active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-3"
                    >
                        <svg v-if="loading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>{{ loading ? 'Processing...' : 'Continue to Payment' }}</span>
                    </button>
                    
                    <div class="text-center mt-6 flex items-center justify-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        Secure Encrypted Transaction
                    </div>

                </div>
            </div>
        </main>
    </div>
</template>
