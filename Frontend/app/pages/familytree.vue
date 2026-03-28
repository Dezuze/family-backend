<template>
  <div class="min-h-screen text-slate-800 font-sans pt-32 relative overflow-hidden" style="background: linear-gradient(135deg, #faf8f5 0%, #f0ede6 30%, #e8e4db 60%, #f5f2ec 100%);">
    
    <!-- Subtle decorative background pattern -->
    <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%23A08050&quot; fill-opacity=&quot;1&quot;%3E%3Cpath d=&quot;M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');"></div>
    
    <!-- Standardized Premium Header -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12 relative z-20 pointer-events-auto">
        <div class="text-center space-y-4">
            <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
                {{ t('familyTree.header.title') }}
            </h1>
            <div class="h-1.5 w-24 bg-brand-gold mx-auto rounded-full"></div>
            <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
                {{ t('familyTree.header.description') }}
            </p>
        </div>

        <!-- Unified Controls Area -->
        <div class="mt-10 flex flex-col md:flex-row items-center justify-between gap-6 bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-slate-200 shadow-xl relative z-30 pointer-events-auto">
            <!-- View Mode Toggle -->
            <div class="bg-slate-100 rounded-xl p-1 flex border border-slate-200 shadow-inner relative z-40 pointer-events-auto">
                <button 
                    @click="viewMode = 'visual'"
                    :class="['px-6 py-2 rounded-lg text-sm font-bold transition-all', viewMode==='visual' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-brand-gold']"
                >
                    {{ t('familyTree.labels.visualMap') }}
                </button>
                <button 
                    @click="viewMode = 'grid'"
                    :class="['px-6 py-2 rounded-lg text-sm font-bold transition-all', viewMode==='grid' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-brand-gold']"
                >
                    {{ t('familyTree.labels.directory') }}
                </button>
            </div>

            <div class="flex items-center gap-2">
                <button
                    @click="toggleEditMode"
                    :class="[
                        'px-4 py-2 rounded-xl text-sm font-bold transition-all duration-300 border active:scale-95',
                        editMode
                            ? 'bg-brand-gold text-white border-brand-gold shadow-md'
                            : 'bg-white text-slate-600 border-slate-200 hover:text-brand-gold hover:border-brand-gold/40'
                    ]"
                >
                    {{ editMode ? t('familyTree.editor.editModeOn') : t('familyTree.editor.editMode') }}
                </button>
            </div>

            <!-- Contextual Controls (Search/Layout) -->
            <div class="flex flex-1 items-center justify-center md:justify-end gap-4 w-full">
                <!-- Search -->
                <div class="relative flex-1 max-w-xs">
                    <input v-model="searchQuery" @keyup.enter="performSearch" type="search" :placeholder="t('familyTree.header.findMember')" 
                            class="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-gold/40 transition-all">
                    <svg class="w-5 h-5 text-slate-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    
                    <!-- Search Results Dropdown -->
                    <Transition name="fade-scale">
                        <div v-if="searchResults.length > 0 && viewMode === 'visual'" class="absolute top-full right-0 mt-2 w-full bg-white rounded-xl shadow-2xl border border-slate-200 max-h-60 overflow-y-auto z-50">
                            <div v-for="res in searchResults" :key="res.id" @click="focusOnMember(res)" class="px-4 py-2 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-0 transition-colors duration-200">
                                <div class="font-bold text-slate-800 text-sm">{{ res.name }}</div>
                                <div class="text-xs text-slate-500">{{ res.relation || t('familyTree.labels.member') }}</div>
                            </div>
                        </div>
                    </Transition>
                </div>

                <!-- Directory Specific Layout Controls -->
                <div v-if="viewMode === 'grid'" class="flex items-center gap-4 text-xs font-bold text-slate-400 uppercase tracking-widest bg-slate-50 px-4 py-2 rounded-xl border border-slate-200">
                    <div class="flex items-center gap-2">
                        <label>{{ t('familyTree.labels.layout') }}</label>
                        <select v-model="layout" class="bg-transparent border-none focus:ring-0 text-slate-800 cursor-pointer">
                            <option value="grid">{{ t('familyTree.labels.grid') }}</option>
                            <option value="list">{{ t('familyTree.labels.list') }}</option>
                            <option value="compact">{{ t('familyTree.labels.compact') }}</option>
                        </select>
                    </div>
                    
                    <div v-if="layout === 'grid' || layout === 'compact'" class="hidden lg:flex items-center gap-2">
                        <label>{{ t('familyTree.labels.size') }}</label>
                        <input type="range" min="160" max="420" v-model.number="minWidth" class="w-20 accent-brand-gold cursor-pointer" />
                    </div>
                </div>
            </div>
        </div>
        <p v-if="viewMode === 'visual'" class="mt-2 text-center text-xs font-semibold text-slate-500">{{ t('familyTree.editor.zoomHint') }}</p>
    </div>

    <!-- Visual View -->
    <div v-show="viewMode === 'visual'" :class="['w-full h-[calc(100vh-100px)] cursor-move relative transition-all duration-300', editMode ? 'md:pr-[430px]' : '']" ref="chartContainer">
       <!-- Tree area backdrop -->
       <div class="absolute inset-0 rounded-none" style="background: radial-gradient(ellipse at center, rgba(160,128,80,0.04) 0%, transparent 70%);"></div>
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center z-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-gold"></div>
       </div>
       <svg ref="svgRef" class="w-full h-full relative z-1"></svg>
    </div>

     <!-- Grid View -->
     <div v-if="viewMode === 'grid'" class="max-w-7xl mx-auto px-4 pb-20 overflow-y-auto h-[calc(100vh-280px)]">

         <div :class="containerClass" :style="containerStyle">
            <!-- Skeleton Grid -->
            <template v-if="loading">
               <div v-for="n in 8" :key="n" class="bg-white rounded-xl h-48 animate-pulse border border-slate-200">
                  <div class="h-full flex items-center p-4 gap-4">
                     <div class="w-24 h-24 rounded-full bg-slate-200 shrink-0"></div>
                     <div class="flex-1 space-y-3">
                        <div class="h-5 bg-slate-200 rounded w-3/4"></div>
                        <div class="h-4 bg-slate-200 rounded w-1/2"></div>
                     </div>
                  </div>
               </div>
            </template>

            <!-- Real Cards -->
            <template v-else>
               <div 
                  v-for="member in sortedMembers" 
                  :key="member.id"
                  @click="openMember(member)"
                  class="cursor-pointer"
               >
                  <MemberCard 
                    :member="member" 
                    :variant="cardVariant"
                  />
               </div>
            </template>
         </div>
         
         <!-- Empty State -->
         <div v-if="!loading && sortedMembers.length === 0" class="text-center text-slate-500 py-20 bg-white rounded-xl border border-slate-200 shadow-sm">
            <svg class="w-16 h-16 mx-auto text-slate-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                <p class="font-bold text-slate-400">{{ t('familyTree.empty.noMembersFound') }}</p>
         </div>
     </div>

     <!-- Member Modal -->
     <MemberDetailsModal 
        v-if="selectedMember && !editMode" 
        :member="selectedMember" 
        @close="selectedMember = null" 
     />

      <div
          v-if="editMode && isEditorSheetOpen"
          class="fixed inset-0 z-30 bg-slate-900/25 backdrop-blur-[1px] md:hidden"
          @click="isEditorSheetOpen = false"
      ></div>

      <button
          v-if="editMode && !isEditorSheetOpen"
          class="fixed bottom-4 right-4 z-40 rounded-2xl border border-brand-gold/40 bg-white px-4 py-2 text-xs font-black text-brand-gold shadow-xl transition-all duration-300 hover:-translate-y-0.5 hover:shadow-2xl active:scale-95 md:hidden"
          @click="isEditorSheetOpen = true"
      >
          {{ t('familyTree.editor.openTreeEditor') }}
      </button>

      <Transition name="slide-up-editor">
      <div
          v-if="editMode && isEditorSheetOpen"
          class="fixed inset-x-2 bottom-2 z-40 max-h-[78vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white/96 p-5 shadow-2xl backdrop-blur transition-all duration-300 md:inset-x-auto md:bottom-4 md:right-4 md:top-28 md:w-[410px] md:max-h-[calc(100vh-8rem)] md:rounded-2xl"
      >
          <div class="mb-3 flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                     <h3 class="text-lg font-black text-slate-900">{{ t('familyTree.editor.title') }}</h3>
                     <p class="text-xs font-medium text-slate-500">{{ t('familyTree.editor.subtitle') }}</p>
                </div>
                <div class="flex items-center gap-2">
                     <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 transition-colors duration-200 hover:bg-slate-100 md:hidden" @click="isEditorSheetOpen = false">{{ t('familyTree.editor.hide') }}</button>
                     <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 transition-colors duration-200 hover:bg-slate-100" @click="toggleEditMode">{{ t('familyTree.editor.close') }}</button>
                </div>
          </div>

        <div v-if="selectedMember" class="space-y-3">
            <div class="rounded-2xl border border-slate-200 bg-linear-to-br from-white to-slate-50 p-3 shadow-sm">
                <div class="text-base font-black text-slate-900">{{ selectedMember.name }}</div>
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ selectedMember.relation || selectedMember.role || t('familyTree.labels.member') }}</div>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_parent" :class="addRelationType === 'PARENT' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('PARENT')">{{ t('familyTree.editor.actions.parent') }}</button>
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!canAddSpouseNow" :class="addRelationType === 'SPOUSE' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('SPOUSE')">{{ t('familyTree.editor.actions.spouse') }}</button>
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_sibling" :class="addRelationType === 'SIBLING' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('SIBLING')">{{ t('familyTree.editor.actions.sibling') }}</button>
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_child" :class="addRelationType === 'CHILD' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('CHILD')">{{ t('familyTree.editor.actions.child') }}</button>
            </div>

            <div class="space-y-2 rounded-2xl border border-slate-200 bg-slate-50/60 p-3">
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ t('familyTree.editor.addRelativeTitle') }}</div>
                <div class="grid grid-cols-2 gap-2 rounded-xl border border-slate-200 bg-white p-1">
                    <button
                        type="button"
                        class="rounded-lg px-2 py-1.5 text-xs font-bold transition-all duration-300"
                        :class="addRelativeMode === 'create' ? 'bg-brand-gold text-white' : 'text-slate-600 hover:bg-slate-100'"
                        @click="addRelativeMode = 'create'; linkSearchQuery = ''; resetLinkTarget(); editorError = ''; editorSuccess = ''"
                    >
                        {{ t('familyTree.editor.mode.create') }}
                    </button>
                    <button
                        type="button"
                        class="rounded-lg px-2 py-1.5 text-xs font-bold transition-all duration-300"
                        :class="addRelativeMode === 'link' ? 'bg-brand-gold text-white' : 'text-slate-600 hover:bg-slate-100'"
                        @click="addRelativeMode = 'link'; addRelativeName = ''; resetLinkTarget(); linkSearchQuery = ''; editorError = ''; editorSuccess = ''"
                    >
                        {{ t('familyTree.editor.mode.link') }}
                    </button>
                </div>
                <select v-model="addRelationType" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                    <option value="PARENT">{{ t('familyTree.editor.relation.parent') }}</option>
                    <option value="SPOUSE" :disabled="selectedMemberHasSpouse">{{ t('familyTree.editor.relation.spouse') }}</option>
                    <option value="SIBLING">{{ t('familyTree.editor.relation.sibling') }}</option>
                    <option value="CHILD">{{ t('familyTree.editor.relation.child') }}</option>
                </select>
                <p v-if="duplicateRelationWarning" class="text-[11px] font-semibold text-amber-700">{{ duplicateRelationWarning }}</p>
                <template v-if="addRelativeMode === 'create'">
                    <input v-model="addRelativeName" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('familyTree.editor.placeholders.relativeName')" />
                    <select v-model="addRelativeGender" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="M">{{ t('onboarding.gender.male') }}</option>
                        <option value="F">{{ t('onboarding.gender.female') }}</option>
                        <option value="O">{{ t('onboarding.gender.other') }}</option>
                    </select>
                </template>
                <template v-else>
                    <div class="relative">
                        <input
                            v-model="linkSearchQuery"
                            class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                            :placeholder="t('familyTree.editor.placeholders.searchExisting')"
                            @input="onLinkSearchInput"
                        />
                        <div v-if="linkSearchLoading" class="absolute right-3 top-2.5 text-xs font-semibold text-slate-400">{{ t('familyTree.editor.searching') }}</div>
                        <Transition name="fade-scale">
                        <div v-if="linkSearchResults.length" class="absolute z-50 mt-1 max-h-44 w-full overflow-y-auto rounded-xl border border-slate-200 bg-white shadow-xl">
                            <button
                                v-for="candidate in linkSearchResults"
                                :key="candidate.id"
                                type="button"
                                class="block w-full border-b border-slate-100 px-3 py-2 text-left last:border-b-0 transition-colors duration-200 hover:bg-slate-50"
                                @click="selectLinkTarget(candidate)"
                            >
                                <div class="text-sm font-bold text-slate-800">{{ candidate.name }}</div>
                                <div class="text-xs text-slate-500">{{ candidate.relation || t('familyTree.labels.member') }}</div>
                            </button>
                        </div>
                        </Transition>
                    </div>
                    <Transition name="fade-scale">
                        <div v-if="selectedLinkTarget" class="flex items-center justify-between rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">
                            <span>{{ t('familyTree.editor.selectedLabel', { name: selectedLinkTarget.name }) }}</span>
                            <button type="button" class="text-emerald-700 transition-colors duration-200 hover:text-emerald-900" @click="resetLinkTarget(); linkSearchQuery = ''">{{ t('familyTree.editor.clear') }}</button>
                        </div>
                    </Transition>
                </template>
                <button
                    class="w-full rounded-xl bg-brand-gold px-3 py-2.5 text-sm font-black text-white shadow-lg transition-all duration-300 hover:brightness-110 active:scale-95 disabled:opacity-50"
                    :disabled="editorLoading || !canSubmitAddRelative"
                    @click="addRelativeFromPanel"
                >
                    {{ editorLoading ? t('familyTree.editor.saving') : t('familyTree.editor.addRelative') }}
                </button>
            </div>

            <div class="space-y-2 rounded-2xl border border-slate-200 bg-slate-50/60 p-3">
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ t('familyTree.editor.accessOwnership') }}</div>
                <div class="flex flex-wrap gap-2">
                    <span class="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold uppercase text-slate-600" v-if="contextOwnership.has_account">{{ t('familyTree.editor.badges.hasAccount') }}</span>
                    <span class="rounded-full bg-green-100 px-2 py-1 text-[10px] font-bold uppercase text-green-700" v-if="contextOwnership.is_independent">{{ t('familyTree.editor.badges.independent') }}</span>
                    <span class="rounded-full bg-amber-100 px-2 py-1 text-[10px] font-bold uppercase text-amber-700" v-if="contextOwnership.created_by_me">{{ t('familyTree.editor.badges.managedByYou') }}</span>
                </div>

                <div v-if="canShowGiveAccess" class="space-y-2">
                    <input v-model="accessUsername" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.giveAccess.username')" />
                    <input v-model="accessPassword" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.giveAccess.password')" />
                    <button
                        class="w-full rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold transition-all duration-300 hover:bg-brand-gold/5 active:scale-95 disabled:opacity-50"
                        :disabled="accessLoading"
                        @click="giveAccessFromPanel"
                    >
                        {{ accessLoading ? t('onboarding.giveAccess.creating') : t('onboarding.managed.giveAccess') }}
                    </button>
                </div>

                <button
                    v-if="canGoIndependent"
                    class="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 transition-all duration-300 hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                    :disabled="accessLoading"
                    @click="goIndependentFromPanel"
                >
                    {{ t('familyTree.editor.becomeIndependent') }}
                </button>
            </div>

            <button
                class="w-full rounded-xl border border-red-200 px-3 py-2 text-xs font-bold text-red-600 transition-all duration-300 hover:bg-red-50 active:scale-95 disabled:opacity-50"
                :disabled="editorLoading || !allowedActions.can_remove"
                @click="removeSelectedMember"
            >
                {{ t('familyTree.editor.removeSelected') }}
            </button>

            <Transition name="fade-slide">
                <p v-if="!allowedActions.can_manage" class="rounded-lg bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">{{ t('familyTree.editor.permissionHint') }}</p>
            </Transition>
            <Transition name="fade-slide">
                <p v-if="editorError" class="rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{{ editorError }}</p>
            </Transition>
            <Transition name="fade-slide">
                <p v-if="editorSuccess" class="rounded-lg bg-green-50 px-3 py-2 text-xs font-medium text-green-700">{{ editorSuccess }}</p>
            </Transition>
        </div>

        <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-slate-500">
            {{ t('familyTree.editor.pickMemberHint') }}
        </div>
     </div>
      </Transition>

  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted, onUnmounted } from 'vue'
import { useHead, useRuntimeConfig, useRoute, useRouter } from '#imports'
import { useI18n } from 'vue-i18n'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import MemberCard from '~/components/MemberCard.vue'

// ============================================================
// familytree.vue — Interactive Family Tree & Member Directory
// ============================================================
// Renders an interactive D3.js genealogy tree with:
//   • Gender-coded cards (blue=male, rose=female, gold=current user)
//   • Dynamic separation (spouse-aware spacing prevents overlap)
//   • Multi-tree forest rendering (separate family heads side-by-side)
//   • Pan, zoom, auto-focus on logged-in user, search-to-focus
//   • Switchable grid/list/compact directory view
// ============================================================

import * as d3 from 'd3'
import { useFamilyStore } from '~/stores/family'
import type { FamilyMember } from '~/types/family'
import { useAuthStore } from '~/stores/auth'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const { t } = useI18n()

const familyStore = useFamilyStore()
const auth = useAuthStore()
const router = useRouter()

// --- Refs & UI State ---
const route = useRoute()

useHead(() => ({
    title: t('familyTree.meta.title'),
    meta: [
        { name: 'description', content: t('familyTree.meta.description') }
    ],
    link: [
        { rel: 'canonical', href: `${config.public.siteUrl || 'http://localhost:3000'}${route.path}` }
    ]
}))

const resolveInitialViewMode = (): 'visual' | 'grid' => {
    const requested = Array.isArray(route.query.view) ? route.query.view[0] : route.query.view
    if (requested === 'grid' || requested === 'visual') return requested
    return 'visual'
}

const resolveInitialEditMode = (): boolean => {
    const requested = Array.isArray(route.query.edit) ? route.query.edit[0] : route.query.edit
    return requested === '1' || requested === 'true'
}

// View mode can be visual graph or directory grid
const viewMode = ref<'visual' | 'grid'>(resolveInitialViewMode())
const editMode = ref(resolveInitialEditMode())
const isEditorSheetOpen = ref(true)
const loading = computed(() => familyStore.loading)
const svgRef = ref<SVGSVGElement | null>(null)
const chartContainer = ref<HTMLDivElement | null>(null)
const selectedMember = ref<FamilyMember | null>(null)

// Directory UI state
const layout = ref<'grid'|'list'|'compact'>('grid')
const minWidth = ref(250)
const searchQuery = ref('')
const searchResults = ref<FamilyMember[]>([])

const addRelationType = ref<'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD'>('CHILD')
const addRelativeMode = ref<'create' | 'link'>('create')
const addRelativeName = ref('')
const addRelativeGender = ref<'M' | 'F' | 'O'>('M')
const linkSearchQuery = ref('')
const linkSearchResults = ref<any[]>([])
const linkSearchLoading = ref(false)
const selectedLinkTarget = ref<any | null>(null)
let linkSearchDebounce: ReturnType<typeof setTimeout> | null = null
const editorLoading = ref(false)
const editorError = ref('')
const editorSuccess = ref('')

const contextOwnership = ref({
    is_independent: false,
    has_account: false,
    created_by_me: false,
    is_self: false,
})

const allowedActions = ref({
    can_manage: false,
    can_add_parent: false,
    can_add_spouse: false,
    can_add_sibling: false,
    can_add_child: false,
    can_remove: false,
})

const accessUsername = ref('')
const accessPassword = ref('')
const accessLoading = ref(false)

const canShowGiveAccess = computed(() => {
    if (!selectedMember.value) return false
    return contextOwnership.value.created_by_me && !contextOwnership.value.has_account && !contextOwnership.value.is_independent
})

const canGoIndependent = computed(() => {
    if (!selectedMember.value) return false
    return contextOwnership.value.is_self && !contextOwnership.value.is_independent
})

const selectedMemberHasSpouse = computed(() => {
    const memberId = selectedMember.value?.id
    if (!memberId) return false
    return links.value.some((l: any) => l.type === 'spouse' && (l.source === memberId || l.target === memberId))
})

const selectedMemberParents = computed(() => {
    const memberId = selectedMember.value?.id
    if (!memberId) return [] as any[]
    const parentIds = links.value
        .filter((l: any) => l.type === 'parent' && l.target === memberId)
        .map((l: any) => l.source)
    return nodes.value.filter((n: any) => parentIds.includes(n.id))
})

const selectedMemberHasFather = computed(() => {
    return selectedMemberParents.value.some((p: any) => p.gender === 'M')
})

const selectedMemberHasMother = computed(() => {
    return selectedMemberParents.value.some((p: any) => p.gender === 'F')
})

const canAddSpouseNow = computed(() => {
    return allowedActions.value.can_add_spouse && !selectedMemberHasSpouse.value
})

const selectedTargetAlreadyLinked = computed(() => {
    if (addRelativeMode.value !== 'link' || !selectedMember.value || !selectedLinkTarget.value) return false
    const anchorId = selectedMember.value.id
    const targetId = selectedLinkTarget.value.id

    if (addRelationType.value === 'PARENT') {
        return links.value.some((l: any) => l.type === 'parent' && l.source === targetId && l.target === anchorId)
    }
    if (addRelationType.value === 'CHILD') {
        return links.value.some((l: any) => l.type === 'parent' && l.source === anchorId && l.target === targetId)
    }
    if (addRelationType.value === 'SPOUSE') {
        return links.value.some((l: any) => l.type === 'spouse' && ((l.source === anchorId && l.target === targetId) || (l.source === targetId && l.target === anchorId)))
    }
    if (addRelationType.value === 'SIBLING') {
        return links.value.some((l: any) => l.type === 'sibling' && ((l.source === anchorId && l.target === targetId) || (l.source === targetId && l.target === anchorId)))
    }
    return false
})

const duplicateRelationWarning = computed(() => {
    if (selectedTargetAlreadyLinked.value) {
        return t('familyTree.editor.warnings.alreadyLinked')
    }

    if (addRelationType.value === 'SPOUSE' && selectedMemberHasSpouse.value) {
        return t('familyTree.editor.warnings.spouseExists')
    }

    if (addRelationType.value === 'PARENT') {
        if (selectedMemberParents.value.length >= 2) {
            return t('familyTree.editor.warnings.parentCap')
        }
        const pendingParentGender = addRelativeMode.value === 'link'
            ? (selectedLinkTarget.value?.gender || 'O')
            : addRelativeGender.value
        if (pendingParentGender === 'M' && selectedMemberHasFather.value) {
            return t('familyTree.editor.warnings.fatherExists')
        }
        if (pendingParentGender === 'F' && selectedMemberHasMother.value) {
            return t('familyTree.editor.warnings.motherExists')
        }
    }

    return ''
})

const canSubmitAddRelative = computed(() => {
    if (!allowedActions.value.can_manage || !!duplicateRelationWarning.value) return false
    if (addRelativeMode.value === 'link') {
        return !!selectedLinkTarget.value
    }
    return true
})

// --- Computed Data ---
// Flatten the store's tree data into a simple array of nodes and links.
// Nodes = all FamilyMembers, Links = parent/spouse/sibling connections.
const nodes = computed(() => familyStore.flatList())
const links = computed(() => familyStore.edges)

// When user presses Enter in search, auto-focus the first result
const performSearch = () => {
    if (viewMode.value !== 'visual') return
  if (searchResults.value.length > 0) {
    focusOnMember(searchResults.value[0])
  }
}

// Dynamic layout helpers
const cardVariant = computed(() => layout.value === 'compact' ? 'compact' : (layout.value === 'list' ? 'list' : 'default'))
const containerClass = computed(() => {
  if (layout.value === 'list') return 'flex flex-col gap-3'
  if (layout.value === 'compact') return 'grid gap-2'
  return 'grid gap-4'
})
const containerStyle = computed(() => {
  if (layout.value === 'list') return {}
  const minVal = minWidth.value || 250
  return { gridTemplateColumns: `repeat(auto-fit, minmax(${minVal}px, 1fr))` }
})

const sortedMembers = computed(() => {
   let list = [...nodes.value].sort((a,b) => a.name.localeCompare(b.name))
   if (searchQuery.value) {
       const q = searchQuery.value.toLowerCase()
       return list.filter(m => m.name.toLowerCase().includes(q))
   }
   return list
})

// --- Global D3 State ---
// These module-scoped variables are updated each time initGraph() runs.
// They enable the search-to-focus and auto-focus features to access
// the last-rendered tree state.
let globalZoom: any = null        // D3 zoom behavior for programmatic pan/zoom
let globalSVG: any = null         // D3 selection of the <svg> element
let globalRoot: any = null        // Root of the first tree (for fallback searches)
let globalForestData: { root: any, xOffset: number }[] = [] // All trees + X offsets

const resolveImage = (path: string | null) => {
    if (!path) return null
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

watch(searchQuery, (val) => {
    if (!val || viewMode.value !== 'visual') {
        searchResults.value = []
        return
    }
    const q = val.toLowerCase()
    searchResults.value = nodes.value.filter((n: any) => n.name.toLowerCase().includes(q)).slice(0, 5)
})

/**
 * Search-to-Focus: smoothly pan/zoom the tree to center on a member.
 * Searches across ALL forest trees (not just the first) and handles
 * both direct tree nodes and spouse-rendered cards.
 */
const focusOnMember = (targetMember: any) => {
    searchQuery.value = '' // clear search
    searchResults.value = []
    
    if (!targetMember || !globalZoom || !globalSVG) return

    let targetX = 0
    let targetY = 0
    let found = false

    // Search across ALL forest trees, not just the first
    for (const { root, xOffset } of globalForestData) {
        if (found) break
        
        // Check direct node
        const targetNode = root.descendants().find((d: any) => d.data.id === targetMember.id)
        if (targetNode) {
            targetX = xOffset + targetNode.x
            targetY = 100 + targetNode.y
            found = true
            break
        }
        
        // Check if target is a spouse rendered next to a tree node
        const spouseLink = links.value.find((l: any) => l.type === 'spouse' && (l.source === targetMember.id || l.target === targetMember.id))
        if (spouseLink) {
            const partnerId = spouseLink.source === targetMember.id ? spouseLink.target : spouseLink.source
            const partnerNode = root.descendants().find((d: any) => d.data.id === partnerId)
            if (partnerNode) {
                targetX = xOffset + partnerNode.x + 180
                targetY = 100 + partnerNode.y
                found = true
                break
            }
        }
    }

    if (found) {
        const container = chartContainer.value
        if (container) {
            const width = container.clientWidth
            const height = container.clientHeight
            const scale = 1.5
            globalSVG.transition().duration(1500).call(
                globalZoom.transform as any, 
                d3.zoomIdentity.translate(width/2 - targetX*scale, height/2 - targetY*scale).scale(scale)
            )
        }
        selectedMember.value = targetMember 
    }
}

const openMember = (m: FamilyMember) => { selectedMember.value = m }

const setRelationType = (value: 'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD') => {
    if (value === 'SPOUSE' && selectedMemberHasSpouse.value) {
        editorError.value = t('familyTree.editor.errors.spouseAlreadyLinked')
        return
    }
    addRelationType.value = value
}

function getCookie(name: string) {
    if (typeof document === 'undefined') return null
    const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
    return matches ? matches[2] : null
}

const withCsrfHeaders = async () => {
    const csrfRes = await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrfData = await csrfRes.json().catch(() => ({}))
    const csrftoken = getCookie('csrftoken') || csrfData.csrfToken
    return csrftoken ? { 'X-CSRFToken': csrftoken } : {}
}

const loadMemberContext = async (memberId: number) => {
    try {
        const res = await fetch(`${apiBase}/api/families/member-context/${memberId}/`, { credentials: 'include' })
        if (!res.ok) return
        const data = await res.json()
        contextOwnership.value = data.ownership_status || contextOwnership.value
        allowedActions.value = data.allowed_actions || allowedActions.value
    } catch (err) {
        console.error('Failed to load member context', err)
    }
}

const resetLinkTarget = () => {
    selectedLinkTarget.value = null
    linkSearchResults.value = []
}

const selectLinkTarget = (member: any) => {
    selectedLinkTarget.value = member
    linkSearchQuery.value = member.name || ''
    linkSearchResults.value = []
}

const searchExistingMembers = async () => {
    const query = linkSearchQuery.value.trim()
    if (addRelativeMode.value !== 'link' || query.length < 2) {
        linkSearchResults.value = []
        return
    }

    linkSearchLoading.value = true
    try {
        const anchorId = selectedMember.value?.id
        const params = new URLSearchParams({ q: query })
        if (anchorId) params.set('exclude_id', String(anchorId))

        const res = await fetch(`${apiBase}/api/families/member-search/?${params.toString()}`, {
            credentials: 'include',
        })
        if (!res.ok) {
            linkSearchResults.value = []
            return
        }

        const payload = await res.json().catch(() => ({ results: [] }))
        const results = Array.isArray(payload.results) ? payload.results : []
        linkSearchResults.value = results
    } catch (err) {
        linkSearchResults.value = []
        console.error('Failed to search existing members', err)
    } finally {
        linkSearchLoading.value = false
    }
}

const onLinkSearchInput = () => {
    selectedLinkTarget.value = null
    if (linkSearchDebounce) {
        clearTimeout(linkSearchDebounce)
    }
    linkSearchDebounce = setTimeout(() => {
        searchExistingMembers()
    }, 250)
}

const addRelativeFromPanel = async () => {
    if (!selectedMember.value) return
    const anchorMemberId = selectedMember.value.id
    if (!allowedActions.value.can_manage) {
        editorError.value = t('familyTree.editor.errors.managePermission')
        return
    }
    if (addRelativeMode.value === 'create' && !addRelativeName.value.trim()) {
        editorError.value = t('familyTree.editor.errors.relativeNameRequired')
        return
    }
    if (addRelativeMode.value === 'link' && !selectedLinkTarget.value) {
        editorError.value = t('familyTree.editor.errors.selectExistingMember')
        return
    }
    if (duplicateRelationWarning.value) {
        editorError.value = duplicateRelationWarning.value
        return
    }

    editorLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const endpoint = addRelativeMode.value === 'link'
            ? `${apiBase}/api/families/tree-edit/${selectedMember.value.id}/link-existing/`
            : `${apiBase}/api/families/tree-edit/${selectedMember.value.id}/add-relative/`
        const body = addRelativeMode.value === 'link' && selectedLinkTarget.value
            ? {
                target_member_id: selectedLinkTarget.value.id,
                relation_type: addRelationType.value,
            }
            : {
                name: addRelativeName.value.trim(),
                gender: addRelativeGender.value,
                relation_type: addRelationType.value,
            }

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...csrfHeaders,
            },
            credentials: 'include',
            body: JSON.stringify(body),
        })
        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || t('familyTree.editor.errors.addRelativeFailed')
            return
        }

        if (addRelativeMode.value === 'create') {
            addRelativeName.value = ''
        } else {
            linkSearchQuery.value = ''
            resetLinkTarget()
        }
        editorSuccess.value = addRelativeMode.value === 'create'
            ? t('familyTree.editor.success.relativeAdded')
            : t('familyTree.editor.success.existingLinked')
        await familyStore.fetchFamily()
        await auth.fetchProfile()
        setTimeout(initGraph, 120)
        const anchor = nodes.value.find((n: any) => n.id === anchorMemberId)
        if (anchor) {
            selectedMember.value = anchor as FamilyMember
            await loadMemberContext(anchorMemberId)
        }
    } catch (err) {
        editorError.value = t('familyTree.editor.errors.addRelativeFailed')
        console.error(err)
    } finally {
        editorLoading.value = false
    }
}

const removeSelectedMember = async () => {
    if (!selectedMember.value) return
    if (!allowedActions.value.can_remove) {
        editorError.value = t('familyTree.editor.errors.removePermission')
        return
    }
    if (!confirm(t('familyTree.editor.confirmRemove', { name: selectedMember.value.name }))) return

    editorLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const res = await fetch(`${apiBase}/api/families/tree-edit/${selectedMember.value.id}/remove/`, {
            method: 'DELETE',
            headers: {
                ...csrfHeaders,
            },
            credentials: 'include',
        })

        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            editorError.value = err.error || t('familyTree.editor.errors.removeFailed')
            return
        }

        editorSuccess.value = t('familyTree.editor.success.memberRemoved')
        selectedMember.value = null
        await familyStore.fetchFamily()
        await auth.fetchProfile()
        setTimeout(initGraph, 120)
    } catch (err) {
        editorError.value = t('familyTree.editor.errors.removeFailed')
        console.error(err)
    } finally {
        editorLoading.value = false
    }
}

const giveAccessFromPanel = async () => {
    if (!selectedMember.value) return
    if (!accessUsername.value.trim() || !accessPassword.value.trim()) {
        editorError.value = t('onboarding.giveAccess.errors.requiredFields')
        return
    }

    accessLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    const result = await auth.giveAccess(selectedMember.value.id, accessUsername.value.trim(), accessPassword.value.trim())
    accessLoading.value = false

    if (!result.ok) {
        editorError.value = result.error || t('familyTree.editor.errors.giveAccessFailed')
        return
    }

    editorSuccess.value = result.data?.message || 'Access granted.'
    accessUsername.value = ''
    accessPassword.value = ''
    await loadMemberContext(selectedMember.value.id)
    await familyStore.fetchFamily()
}

const goIndependentFromPanel = async () => {
    accessLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    const result = await auth.goIndependent()
    accessLoading.value = false

    if (!result.ok) {
        editorError.value = result.error || t('familyTree.editor.errors.independenceFailed')
        return
    }

    editorSuccess.value = result.data?.message || t('familyTree.editor.success.profileIndependent')
    if (selectedMember.value) {
        await loadMemberContext(selectedMember.value.id)
    }
}

const toggleEditMode = () => {
    const next = !editMode.value
    editMode.value = next
    if (next) {
        isEditorSheetOpen.value = true
    }

    const query: Record<string, string> = {}
    if (viewMode.value) query.view = viewMode.value
    if (next) {
        query.edit = '1'
        if (selectedMember.value?.id) query.focus = String(selectedMember.value.id)
    }

    router.replace({ path: '/familytree', query })
}

const focusFromQuery = () => {
    const qFocus = Array.isArray(route.query.focus) ? route.query.focus[0] : route.query.focus
    const focusId = qFocus ? parseInt(qFocus) : NaN
    if (!focusId || Number.isNaN(focusId)) return

    const member = nodes.value.find((n: any) => n.id === focusId)
    if (!member) return
    selectedMember.value = member as FamilyMember
    setTimeout(() => focusOnMember(member), 120)
}

// --- D3 Tree Rendering Pipeline ---
   const initGraph = () => {
      if (!nodes.value.length || !svgRef.value || !chartContainer.value) {
          return
      }
   
      const width = chartContainer.value.clientWidth
      const height = chartContainer.value.clientHeight
      
      if (width === 0 || height === 0) {
          setTimeout(initGraph, 500)
          return
      }

      const svg = d3.select(svgRef.value) as d3.Selection<SVGSVGElement, unknown, null, undefined>
      svg.attr("viewBox", `0 0 ${width} ${height}`)
      
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .filter((event: any) => {
            if (event.type === 'wheel') {
                return Boolean(event.ctrlKey || event.metaKey)
            }
            return true
        })
        .on("zoom", (event) => {
            g.attr("transform", event.transform)
        })
      svg.call(zoom)
      
      globalZoom = zoom
      globalSVG = svg
   
      svg.selectAll("*").remove()
      const g = svg.append("g")

      const hasParent = new Set(links.value.filter(l => l.type === 'parent').map(l => l.target))
      const potentialRoots = nodes.value.filter(n => !hasParent.has(n.id))
      const roots = potentialRoots.filter((r, idx) => {
          const spouseLink = links.value.find(l => (l.source === r.id || l.target === r.id) && l.type === 'spouse')
          if (spouseLink) {
              const spouseId = spouseLink.source === r.id ? spouseLink.target : spouseLink.source
              const spouseObj = potentialRoots.find(pr => pr.id === spouseId)
              if (spouseObj && potentialRoots.indexOf(spouseObj) < idx) {
                  return false
              }
          }
          return true
      })
      
      const getChildrenIds = (parentId: number): number[] => {
         return links.value
            .filter((l: any) => l.type === 'parent' && l.source === parentId)
            .map((l: any) => l.target)
      }

      const buildHierarchy = (id: number, visited: Set<number> = new Set()): any => {
         if (visited.has(id)) return null 
         visited.add(id)
         const node = nodes.value.find((n: any) => n.id === id)
         const childrenIds = getChildrenIds(id)
         return {
            ...node,
            children: childrenIds.map(cid => buildHierarchy(cid, visited)).filter(Boolean)
         }
      }

      const forest: any[] = []
      const globalVisited = new Set<number>()
      
      potentialRoots.sort((a: any, b: any) => {
          const childrenA = getChildrenIds(a.id).length
          const childrenB = getChildrenIds(b.id).length
          return childrenB - childrenA
      })

      // Track which nodes are part of a "real" tree (have children or are children)
      const treeNodeIds = new Set<number>()
      
      potentialRoots.forEach((rootNode: any) => {
          if (globalVisited.has(rootNode.id)) return
          
          // Check if this root is a spouse of any node already in a real tree
          const isSpouseOfTreeNode = links.value.some((l: any) => 
              l.type === 'spouse' && (
                  (l.source === rootNode.id && treeNodeIds.has(l.target)) ||
                  (l.target === rootNode.id && treeNodeIds.has(l.source))
              )
          )
          if (isSpouseOfTreeNode) {
              globalVisited.add(rootNode.id) // Mark visited so it doesn't float
              return
          }
          
          const treeData = buildHierarchy(rootNode.id, globalVisited)
          if (treeData) {
              forest.push(treeData)
              // Track all nodes in this tree that have actual hierarchy (children)
              const collectIds = (node: any) => {
                  treeNodeIds.add(node.id)
                  if (node.children) node.children.forEach(collectIds)
              }
              collectIds(treeData)
          }
      })

      // Any remaining unvisited nodes that are spouses of tree nodes should not float
      const spouseRendered = new Set<number>()
      links.value.filter(l => l.type === 'spouse').forEach((l: any) => {
          if (treeNodeIds.has(l.source) || globalVisited.has(l.source)) {
              spouseRendered.add(l.target)
          }
          if (treeNodeIds.has(l.target) || globalVisited.has(l.target)) {
              spouseRendered.add(l.source)
          }
      })

      nodes.value.forEach((node: any) => {
          if (!globalVisited.has(node.id) && !spouseRendered.has(node.id)) {
              forest.push({...node, children: []})
              globalVisited.add(node.id)
          }
      })

      // Build a set of node IDs that have spouses for dynamic separation
      const nodesWithSpouse = new Set<number>()
      links.value.filter(l => l.type === 'spouse').forEach((l: any) => {
          nodesWithSpouse.add(l.source)
          nodesWithSpouse.add(l.target)
      })

      const treeLayout = d3.tree<any>()
        .nodeSize([200, 300])
        .separation((a: any, b: any) => {
            // Base separation = 1 (200px)
            // If either node has a spouse, add extra space for the spouse card
            const aHasSpouse = nodesWithSpouse.has(a.data?.id)
            const bHasSpouse = nodesWithSpouse.has(b.data?.id)
            if (aHasSpouse && bHasSpouse) return 2.5 // Both have spouses: 500px
            if (aHasSpouse || bHasSpouse) return 2.2 // One has spouse: 440px
            return a.parent === b.parent ? 1.5 : 2  // Siblings: 300px, cousins: 400px
        })

      const forestGroups = forest.map((treeData) => {
          const strategyRoot = d3.hierarchy(treeData)
          treeLayout(strategyRoot)
          return strategyRoot
      })

      // Calculate actual tree widths for dynamic spacing
      const getTreeBounds = (root: any) => {
          let minX = Infinity, maxX = -Infinity
          root.descendants().forEach((d: any) => {
              // Account for node card (75px half-width) plus possible spouse offset (180+75)
              const nodeLeft = d.x - 75
              const hasSpouse = nodesWithSpouse.has(d.data?.id)
              const nodeRight = hasSpouse ? d.x + 180 + 75 : d.x + 75
              if (nodeLeft < minX) minX = nodeLeft
              if (nodeRight > maxX) maxX = nodeRight
          })
          return { minX, maxX, width: maxX - minX }
      }

      let currentXOffset = width / 2
      const forestOffsets: number[] = []
      forestGroups.forEach((root, i) => {
          const bounds = getTreeBounds(root)
          // Offset so tree starts after previous tree with padding
          if (i > 0) currentXOffset += -bounds.minX + 80
          
          forestOffsets.push(currentXOffset)
          const treeG = g.append("g").attr("transform", `translate(${currentXOffset}, 100)`)
          
          if (i === 0) globalRoot = root 

          treeG.selectAll(".link")
            .data(root.links())
            .join("path")
            .attr("class", "link")
            .attr("fill", "none")
            .attr("stroke", "#a89060")
            .attr("stroke-width", 2.5)
            .attr("stroke-linecap", "round")
            .attr("stroke-opacity", 0.7)
            .attr("d", d3.linkVertical<any, d3.HierarchyPointNode<any>>()
                .x(d => d.x)
                .y(d => d.y) as any)

          const nodeGroup = treeG.selectAll(".node")
            .data(root.descendants())
            .join("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x},${d.y})`)

          nodeGroup.each(function(this: any, d: any) {
              renderCard(d3.select(this), 0, d.data)
              const spouse = getSpouse(d.data.id)
               if (spouse) {
                   const sel = d3.select(this)
                   const spouseOffset = 180 
                         const halfCard = 164 / 2
                   sel.append("line")
                             .attr("x1", halfCard).attr("x2", spouseOffset - halfCard) 
                      .attr("y1", 0).attr("y2", 0)
                      .attr("stroke", "#c9a96e").attr("stroke-width", 2).attr("stroke-dasharray", "6,4")
                      .attr("stroke-linecap", "round")
                   renderCard(sel, spouseOffset, spouse)
               }
          })

          // Advance offset past this tree's right edge
          const treeBounds = getTreeBounds(root)
          currentXOffset += treeBounds.maxX + 80
      })

      function renderCard(selection: d3.Selection<any, any, any, any>, dx=0, d: any) {
          if (!d) return
          const cardWidth = 164
          const cardHeight = 210
          const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
          const isUser = auth.user && d.username === auth.user.username
          const isMale = d.gender === 'M'
          const isFemale = d.gender === 'F'
          const relationLabel = String(d.role || d.relation || t('familyTree.labels.member'))
          const shortRelation = relationLabel.length > 20 ? `${relationLabel.slice(0, 20)}...` : relationLabel
          const genderSymbol = isMale ? 'M' : (isFemale ? 'F' : 'O')
          const firstName = String(d.name || '').trim().split(' ')[0] || t('familyTree.labels.member')
          
          // Color scheme based on gender
          const cardFill = isUser ? '#F9EFC8' : (isMale ? '#EEF4FB' : isFemale ? '#FCEFF3' : '#EEF2F7')
          const cardStroke = isUser ? '#C9A96E' : (isMale ? '#90A7C7' : isFemale ? '#D5A1AF' : '#A6B0BE')
          const accentColor = isUser ? '#A08050' : (isMale ? '#4A6B8A' : isFemale ? '#9C4F63' : '#596577')
          const avatarBg = isUser ? '#EED89D' : (isMale ? '#DCE6F0' : isFemale ? '#F5DDE1' : '#E2E8F0')
          const avatarRing = isUser ? '#B9914E' : (isMale ? '#7A9BBD' : isFemale ? '#C88A97' : '#93A1B5')
          
          const clipId = `clip-${d.id}-${Math.random().toString(36).substr(2, 9)}`
          const gradId = `grad-${d.id}-${Math.random().toString(36).substr(2, 9)}`

                    // Card shadow layer
          group.append("rect")
                        .attr("x", -cardWidth/2 + 4).attr("y", -cardHeight/2 + 8)
            .attr("width", cardWidth).attr("height", cardHeight).attr("rx", 16)
                        .attr("fill", "rgba(15,23,42,0.04)")
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "")
                        .style("filter", `drop-shadow(0 10px 22px ${isMale ? 'rgba(74,107,138,0.20)' : isFemale ? 'rgba(156,79,99,0.20)' : 'rgba(89,101,119,0.18)'})`)

          // Main card rect with rounded corners
          group.append("rect")
            .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
            .attr("width", cardWidth).attr("height", cardHeight).attr("rx", 16)
            .attr("fill", cardFill)
            .attr("stroke", cardStroke)
            .attr("stroke-width", isUser ? 3 : 1.8)
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "")
            .style("cursor", "pointer")
            .on("click", () => openMember(d))

          // Colored accent bar at top
          const defs = group.append("defs")
          const grad = defs.append("linearGradient").attr("id", gradId)
            .attr("x1", "0%").attr("y1", "0%").attr("x2", "100%").attr("y2", "0%")
          grad.append("stop").attr("offset", "0%").attr("stop-color", accentColor).attr("stop-opacity", 0.8)
          grad.append("stop").attr("offset", "100%").attr("stop-color", accentColor).attr("stop-opacity", 0.3)

                    group.append("rect")
            .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
                        .attr("width", cardWidth).attr("height", 8).attr("rx", 0)
            .attr("fill", `url(#${gradId})`)
            .attr("clip-path", `inset(0 round 16px 16px 0 0)`)

          // Avatar ring
          group.append("circle")
            .attr("cx", 0).attr("cy", -cardHeight/4 + 2)
            .attr("r", 40)
            .attr("fill", avatarBg)
            .attr("stroke", avatarRing)
            .attr("stroke-width", 2.5)

          // Define ClipPath for photo
          defs.append("clipPath")
            .attr("id", clipId)
            .append("circle")
            .attr("cx", 0)
            .attr("cy", -cardHeight/4 + 2)
            .attr("r", 36)

          group.append("image")
            .attr("href", resolveImage(d.photo || null) || `https://ui-avatars.com/api/?name=${encodeURIComponent(d.name)}&background=${avatarBg.replace('#','')}&color=${accentColor.replace('#','')}&bold=true`)
                        .attr("x", -36).attr("y", -cardHeight/4 + 2 - 36).attr("width", 72).attr("height", 72)
            .attr("preserveAspectRatio", "xMidYMid slice")
            .attr("clip-path", `url(#${clipId})`)
            .style("pointer-events", "none")

          // Name
          group.append("text")
                        .text(firstName)
                        .attr("x", 0).attr("y", 26)
            .attr("text-anchor", "middle")
            .attr("fill", accentColor)
            .attr("font-weight", "800")
                        .attr("font-size", "13px")
            .attr("font-family", "'Inter', 'Segoe UI', sans-serif")
            .style("pointer-events", "none")
          
          // Role / Relation
          group.append("text")
                        .text(shortRelation)
                        .attr("x", 0).attr("y", 44)
            .attr("text-anchor", "middle")
                        .attr("fill", isUser ? '#8C6D2C' : '#66768B')
                        .attr("font-weight", "700")
                        .attr("font-size", "10.5px")
            .attr("text-transform", "uppercase")
            .attr("letter-spacing", "0.5px")
            .style("pointer-events", "none")

          // Gender & Age pill
                    const pillWidth = 72
                    const pillHeight = 22
                    const pillY = 64
          group.append("rect")
            .attr("x", -pillWidth/2).attr("y", pillY - pillHeight/2)
            .attr("width", pillWidth).attr("height", pillHeight).attr("rx", 10)
                        .attr("fill", isMale ? 'rgba(74,107,138,0.11)' : isFemale ? 'rgba(156,79,99,0.11)' : 'rgba(89,101,119,0.11)')

          group.append("text")
                        .text(t('familyTree.labels.agePill', { symbol: genderSymbol, age: d.age || '?' }))
                        .attr("x", 0).attr("y", pillY + 4)
            .attr("text-anchor", "middle")
            .attr("fill", accentColor)
                        .attr("font-size", "10.5px")
            .attr("font-weight", "700")
      }

      function getSpouse(id: number) {
          const l = links.value.find((l: any) => l.type === 'spouse' && (l.source === id || l.target === id))
          if (!l) return null
          const spouseId = l.source === id ? l.target : l.source
          return nodes.value.find((n: any) => n.id === spouseId)
      }
      
      // Store forest data globally for search-to-focus
      globalForestData = forestGroups.map((root, i) => ({
          root,
          xOffset: forestOffsets[i] || (width/2 + i * 1200)
      }))
      
      // FOCUS ON LOGGED-IN USER (search all trees)
      let userCoords = {x: 0, y: 0, found: false}
      
      for (const { root, xOffset } of globalForestData) {
          if (userCoords.found) break
          
          root.descendants().forEach((d: any) => {
              if (userCoords.found) return
              const nodeUsername = d.data.username
              if (nodeUsername === auth.user?.username) {
                  userCoords = { x: xOffset + (d.x || 0), y: 100 + (d.y || 0), found: true }
                  return
              }
              const spouse = getSpouse(d.data.id)
              if (spouse && (spouse as any).username === auth.user?.username) {
                  userCoords = { x: xOffset + (d.x || 0) + 180, y: 100 + (d.y || 0), found: true }
              }
          })
      }
      
      if (userCoords.found) {
         const scale = 1.2
         svg.transition().duration(1500).call(
             zoom.transform as any, 
             d3.zoomIdentity.translate(width/2 - userCoords.x*scale, height/2 - userCoords.y*scale).scale(scale)
         )
      } else {
         svg.transition().duration(750).call(
             zoom.transform as any, 
             d3.zoomIdentity.translate(width/2, 50).scale(0.5)
         )
      }
   }

onMounted(async () => {
    await familyStore.fetchFamily()
    initGraph()
    focusFromQuery()
})

onUnmounted(() => {
    globalForestData = []
    if (linkSearchDebounce) {
        clearTimeout(linkSearchDebounce)
    }
})

// Re-init graph when data or view changes
watch([nodes, links], () => {
    if (viewMode.value === 'visual') {
        setTimeout(initGraph, 100)
        focusFromQuery()
    }
}, { deep: true })

watch(viewMode, (val) => {
    if (val === 'visual') {
        setTimeout(initGraph, 100) 
    }
})

watch(
    () => selectedMember.value?.id,
    (memberId) => {
        linkSearchQuery.value = ''
        resetLinkTarget()
        if (!editMode.value || !memberId) return
        loadMemberContext(memberId)
    }
)

watch(addRelativeMode, (mode) => {
    editorError.value = ''
    editorSuccess.value = ''
    if (mode === 'create') {
        linkSearchQuery.value = ''
        resetLinkTarget()
    } else {
        addRelativeName.value = ''
    }
})

watch(
    () => route.query,
    () => {
        editMode.value = resolveInitialEditMode()
        if (editMode.value) {
            isEditorSheetOpen.value = true
        }
        focusFromQuery()
    },
    { deep: true }
)
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
    transition: opacity 0.22s ease, transform 0.22s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
    opacity: 0;
    transform: translateY(-4px) scale(0.985);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: opacity 0.24s ease, transform 0.24s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(6px);
}

.slide-up-editor-enter-active,
.slide-up-editor-leave-active {
    transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.26s ease;
}

.slide-up-editor-enter-from,
.slide-up-editor-leave-to {
    opacity: 0;
    transform: translateY(14px) scale(0.99);
}
</style>
