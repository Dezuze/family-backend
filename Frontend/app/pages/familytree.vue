<template>
    <div class="min-h-screen text-slate-800 font-sans pt-32 relative overflow-x-hidden" style="background: linear-gradient(135deg, #faf8f5 0%, #f0ede6 30%, #e8e4db 60%, #f5f2ec 100%);">
    
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
    <div v-show="viewMode === 'visual'" :class="['w-full h-[calc(100vh-100px)] cursor-move touch-none relative transition-all duration-300', editMode ? 'md:pr-[430px]' : '']" ref="chartContainer">
       <!-- Tree area backdrop -->
       <div class="absolute inset-0 rounded-none" style="background: radial-gradient(ellipse at center, rgba(160,128,80,0.04) 0%, transparent 70%);"></div>
       <div v-if="isMobileView" class="pointer-events-none absolute bottom-16 right-3 z-20 flex flex-col gap-2 md:hidden">
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('in')"
          >
              +
          </button>
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('out')"
          >
              -
          </button>
       </div>
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center z-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-gold"></div>
       </div>
         <svg ref="svgRef" class="w-full h-full relative z-1 touch-none"></svg>
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
          :canEdit="editMode && allowedActions.can_manage"
        @edit="openQuickEditForSelected"
        @close="selectedMember = null" 
     />

     <div v-if="quickEditOpen && quickEditMemberId" class="fixed inset-0 z-50 flex items-end justify-center p-0 md:items-center md:p-4">
        <div class="absolute inset-0 bg-black/60" @click="quickEditOpen = false"></div>
        <div class="quick-edit-sheet relative w-full max-h-[90vh] overflow-y-auto rounded-t-3xl border border-slate-200 bg-white p-4 pb-5 shadow-2xl md:max-w-2xl md:rounded-2xl md:p-5">
            <div class="sticky top-0 z-10 mb-4 flex items-center justify-between border-b border-slate-100 bg-white pb-3 pt-1">
                <div>
                    <h3 class="text-lg font-black text-slate-900">Edit Member</h3>
                    <p class="text-xs text-slate-500">Update selected member details</p>
                </div>
                <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 hover:bg-slate-100" @click="quickEditOpen = false">Close</button>
            </div>

            <div class="grid grid-cols-1 gap-3.5 md:grid-cols-2">
                <input v-model="quickEditForm.first_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="First name" />
                <input v-model="quickEditForm.last_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Last name" />
                <input v-model="quickEditForm.member_id" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Member ID" />
                <div class="md:col-span-2 flex gap-2">
                    <input v-model="quickEditForm.name_ml" class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Malayalam name" />
                    <button
                        type="button"
                        class="shrink-0 rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold hover:bg-brand-gold/10 disabled:opacity-50"
                        :disabled="nameLookupLoadingQuick"
                        @click="lookupMalayalamNameForQuickEdit"
                    >
                        {{ nameLookupLoadingQuick ? 'Searching...' : 'Malayalam' }}
                    </button>
                </div>
                <input v-model="quickEditForm.nickname" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Nickname" />
                <select v-model="quickEditForm.gender" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="O">Other</option>
                </select>
                <input v-model="quickEditForm.date_of_birth" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                <input v-model="quickEditForm.age" type="number" min="0" max="150" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Age" />
                <input v-model="quickEditForm.blood_group" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Blood group" />
                <input v-model="quickEditForm.occupation" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Occupation" />
                <input v-model="quickEditForm.education" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Education" />
                <input v-model="quickEditForm.church_parish" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Parish" />
                <select v-model="quickEditForm.committee_role" class="rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold">
                    <option value="">Community role (none)</option>
                    <option v-for="role in communityRoles" :key="`quick-role-${role.id}`" :value="role.name">{{ role.name }}</option>
                </select>
                <input v-model="quickEditForm.phone_no" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Phone" />
                <input v-model="quickEditForm.email_id" type="email" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Email" />
                <input v-model="quickEditForm.wedding_anniversary" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Wedding anniversary" />
                <textarea v-model="quickEditForm.address" rows="2" class="md:col-span-2 rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Address"></textarea>
                <textarea v-model="quickEditForm.bio" rows="2" class="md:col-span-2 rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Bio"></textarea>
                <label class="md:col-span-2 flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm">
                    <input v-model="quickEditForm.is_deceased" type="checkbox" class="accent-brand-gold" />
                    Is deceased
                </label>
                <input v-if="quickEditForm.is_deceased" v-model="quickEditForm.date_of_death" type="date" class="md:col-span-2 rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                <input type="file" accept="image/*" class="md:col-span-2 rounded-xl border border-slate-200 px-3 py-2 text-sm" @change="onQuickEditAvatarChange" />
            </div>

            <p v-if="quickEditError" class="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{{ quickEditError }}</p>
            <p v-if="quickEditSuccess" class="mt-3 rounded-lg bg-green-50 px-3 py-2 text-xs font-medium text-green-700">{{ quickEditSuccess }}</p>

            <div class="sticky bottom-0 mt-4 flex justify-end gap-2 border-t border-slate-100 bg-white pt-3">
                <button class="rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700" @click="quickEditOpen = false">Cancel</button>
                <button class="rounded-xl bg-brand-gold px-3 py-2 text-xs font-black text-white disabled:opacity-50" :disabled="quickEditLoading" @click="saveQuickEditMember">
                    {{ quickEditLoading ? 'Saving...' : 'Save Changes' }}
                </button>
            </div>
        </div>
     </div>

      <div
          v-if="editMode && isEditorSheetOpen"
          class="fixed inset-0 z-30 pointer-events-none bg-slate-900/10 backdrop-blur-[0.5px] md:hidden"
      ></div>

      <button
          v-if="editMode && !isEditorSheetOpen"
          class="fixed bottom-4 right-4 z-40 rounded-2xl border border-brand-gold/40 bg-white px-4 py-2 text-xs font-black text-brand-gold shadow-xl transition-all duration-300 hover:-translate-y-0.5 hover:shadow-2xl active:scale-95 md:hidden"
          @click="openEditorSheet"
      >
          {{ t('familyTree.editor.openTreeEditor') }}
      </button>

      <Transition name="slide-up-editor">
      <div
          v-if="editMode && isEditorSheetOpen"
          class="editor-sheet fixed inset-x-0 bottom-0 z-40 max-h-[72vh] overflow-y-auto rounded-t-3xl border border-slate-200 bg-white/96 px-4 pt-0 pb-6 shadow-2xl backdrop-blur transition-all duration-300 md:inset-x-auto md:bottom-4 md:right-4 md:top-28 md:w-[410px] md:max-h-[calc(100vh-8rem)] md:rounded-2xl md:p-5"
          :style="mobileEditorSheetStyle"
          :class="isResizingEditorSheet ? 'duration-0' : ''"
      >
          <div class="mb-2 flex justify-center md:hidden">
                <button
                    type="button"
                    class="h-8 w-24 touch-none rounded-full border border-slate-200 bg-white/90"
                    aria-label="Resize editor panel"
                    @pointerdown.prevent="startEditorResize"
                >
                    <span class="mx-auto block h-1.5 w-10 rounded-full bg-slate-300"></span>
                </button>
          </div>
          <div class="sticky top-0 z-20 mb-3 flex items-center justify-between border-b border-slate-100 bg-white/95 pb-3 pt-3 backdrop-blur">
                <div>
                     <h3 class="text-lg font-black text-slate-900">{{ t('familyTree.editor.title') }}</h3>
                     <p class="text-xs font-medium text-slate-500">{{ t('familyTree.editor.subtitle') }}</p>
                </div>
                <div class="flex items-center gap-2">
                     <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 transition-colors duration-200 hover:bg-slate-100 md:hidden" @click="closeEditorSheet">{{ t('familyTree.editor.hide') }}</button>
                     <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 transition-colors duration-200 hover:bg-slate-100" @click="toggleEditMode">{{ t('familyTree.editor.close') }}</button>
                </div>
          </div>

        <div v-if="selectedMember" class="space-y-4">
            <div class="rounded-2xl border border-slate-200 bg-linear-to-br from-white to-slate-50 p-3 shadow-sm">
                <div class="text-base font-black text-slate-900">{{ selectedMember.name }}</div>
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ selectedMember.relation || selectedMember.role || t('familyTree.labels.member') }}</div>
            </div>

            <button
                class="w-full rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!allowedActions.can_manage"
                :class="allowedActions.can_manage ? 'border-brand-gold/40 bg-brand-gold/10 text-brand-gold hover:bg-brand-gold/15' : 'border-slate-200 text-slate-400'"
                @click="openQuickEditForSelected"
            >
                Edit Profile
            </button>

            <div class="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_parent" :class="addRelationType === 'PARENT' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('PARENT')">{{ t('familyTree.editor.actions.parent') }}</button>
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!canAddSpouseNow" :class="addRelationType === 'SPOUSE' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('SPOUSE')">{{ t('familyTree.editor.actions.spouse') }}</button>
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_sibling" :class="addRelationType === 'SIBLING' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('SIBLING')">{{ t('familyTree.editor.actions.sibling') }}</button>
                <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_child" :class="addRelationType === 'CHILD' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('CHILD')">{{ t('familyTree.editor.actions.child') }}</button>
            </div>

            <div class="space-y-3 rounded-2xl border border-slate-200 bg-slate-50/60 p-3.5">
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ t('familyTree.editor.addRelativeTitle') }}</div>
                <div class="grid grid-cols-2 gap-2.5 rounded-xl border border-slate-200 bg-white p-1.5">
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
                        @click="addRelativeMode = 'link'; resetAddRelativeForm(); resetLinkTarget(); linkSearchQuery = ''; editorError = ''; editorSuccess = ''"
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
                    <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                        <input v-model="addRelativeForm.first_name" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.firstName')" />
                        <input v-model="addRelativeForm.last_name" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.lastName')" />
                    </div>
                    <div class="w-full flex gap-2">
                        <input v-model="addRelativeForm.name_ml" class="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Malayalam name (optional)" />
                        <button
                            type="button"
                            class="shrink-0 rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold hover:bg-brand-gold/10 disabled:opacity-50"
                            :disabled="nameLookupLoadingAdd"
                            @click="lookupMalayalamNameForAddRelative"
                        >
                            {{ nameLookupLoadingAdd ? 'Searching...' : 'Malayalam' }}
                        </button>
                    </div>
                    <input v-model="addRelativeForm.nickname" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.nickname')" />
                    <input v-model="addRelativeForm.member_id" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Member ID (optional)" />
                    <select v-model="addRelativeForm.gender" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="M">{{ t('onboarding.gender.male') }}</option>
                        <option value="F">{{ t('onboarding.gender.female') }}</option>
                        <option value="O">{{ t('onboarding.gender.other') }}</option>
                    </select>
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" class="rounded-xl border px-2 py-2 text-xs font-bold" :class="addRelativeUseDob ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-600'" @click="addRelativeUseDob = true">{{ t('onboarding.fields.dateOfBirth') }}</button>
                        <button type="button" class="rounded-xl border px-2 py-2 text-xs font-bold" :class="!addRelativeUseDob ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-600'" @click="addRelativeUseDob = false">{{ t('onboarding.managedModal.age') }}</button>
                    </div>
                    <input v-if="addRelativeUseDob" v-model="addRelativeForm.date_of_birth" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" />
                    <input v-else v-model="addRelativeForm.age" type="number" min="0" max="150" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.managedModal.enterAge')" />
                    <select v-model="addRelativeForm.blood_group" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="">{{ t('onboarding.placeholders.selectBloodGroup') }}</option>
                        <option value="Unknown">{{ t('onboarding.bloodGroup.unknown') }}</option>
                        <option value="A+">A+</option><option value="A-">A-</option><option value="B+">B+</option><option value="B-">B-</option><option value="O+">O+</option><option value="O-">O-</option><option value="AB+">AB+</option><option value="AB-">AB-</option>
                    </select>
                    <input v-model="addRelativeForm.occupation" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.occupation')" />
                    <input v-model="addRelativeForm.education" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.education')" />
                    <select v-model="addRelativeForm.committee_role" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="">Community role (none)</option>
                        <option v-for="role in communityRoles" :key="`add-role-${role.id}`" :value="role.name">{{ role.name }}</option>
                    </select>
                    <input v-model="addRelativeForm.phone_no" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.phoneNumber')" />
                    <input v-model="addRelativeForm.email_id" type="email" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.email')" />
                    <input v-model="addRelativeForm.church_parish" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.parishChurch')" />
                    <textarea v-model="addRelativeForm.address" rows="2" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.address')"></textarea>
                    <textarea v-model="addRelativeForm.bio" rows="2" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.bio')"></textarea>
                    <label class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700">
                        <input v-model="addRelativeForm.is_deceased" type="checkbox" class="accent-brand-gold" />
                        {{ t('onboarding.managedModal.isDeceased') }}
                    </label>
                    <input v-if="addRelativeForm.is_deceased" v-model="addRelativeForm.date_of_death" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" />
                    <div class="space-y-2">
                        <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500">Profile photo</label>
                        <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2">
                            <div class="h-12 w-12 shrink-0 overflow-hidden rounded-full border border-slate-200 bg-slate-50">
                                <img v-if="addRelativeAvatarPreview" :src="addRelativeAvatarPreview" alt="Member preview" class="h-full w-full object-cover" />
                                <div v-else class="flex h-full w-full items-center justify-center text-[10px] font-bold text-slate-400">No photo</div>
                            </div>
                            <label class="inline-flex cursor-pointer rounded-lg border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold transition-colors hover:bg-brand-gold/10">
                                Upload & Crop
                                <input type="file" accept="image/*" class="hidden" @change="onAddRelativeAvatarChange" />
                            </label>
                            <button
                                v-if="addRelativeAvatarPreview"
                                type="button"
                                class="rounded-lg border border-slate-200 px-2 py-1.5 text-[11px] font-bold text-slate-600 hover:bg-slate-100"
                                @click="clearAddRelativeAvatar"
                            >
                                Remove
                            </button>
                        </div>
                    </div>
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

                <button
                    class="w-full rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold transition-all duration-300 hover:bg-brand-gold/5 active:scale-95 disabled:opacity-50"
                    :disabled="inviteLoading"
                    @click="generateInviteLink"
                >
                    {{ inviteLoading ? t('onboarding.giveAccess.creating') : t('nav.inviteMember') }}
                </button>
                <div v-if="inviteLink" class="rounded-xl border border-slate-200 bg-white p-2">
                    <p class="break-all text-[11px] font-medium text-slate-600">{{ inviteLink }}</p>
                    <button
                        type="button"
                        class="mt-2 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs font-bold text-slate-700 transition-colors hover:bg-slate-50"
                        @click="copyInviteLink"
                    >
                        {{ t('familyTree.editor.copyLink', 'Copy Link') }}
                    </button>
                </div>
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

            <ClientOnly>
                <Teleport to="body">
                    <div v-if="showAddRelativeCropper" class="fixed inset-0 z-60 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
                        <div class="w-full max-w-lg overflow-hidden rounded-3xl bg-white shadow-2xl">
                            <div class="flex items-center justify-between border-b border-gray-100 bg-slate-50 p-4">
                                <h3 class="font-bold text-slate-800">Crop profile photo</h3>
                                <button class="text-slate-400 hover:text-slate-600" @click="cancelAddRelativeCrop">
                                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                </button>
                            </div>
                            <div class="flex justify-center bg-slate-900 p-4">
                                <Cropper
                                    ref="addRelativeCropperRef"
                                    class="h-96 w-full"
                                    :src="addRelativeTempImage || ''"
                                    :stencil-component="CircleStencil"
                                    :stencil-props="{ aspectRatio: 1 / 1 }"
                                />
                            </div>
                            <div class="flex justify-end gap-3 border-t border-gray-100 bg-white p-4">
                                <button class="rounded-xl px-6 py-2.5 font-bold text-slate-600 transition-colors hover:bg-slate-100" @click="cancelAddRelativeCrop">Cancel</button>
                                <button class="rounded-xl bg-brand-gold px-6 py-2.5 font-bold text-white shadow-lg shadow-brand-gold/30 transition-all hover:brightness-110" @click="cropAddRelativeImage">Set photo</button>
                            </div>
                        </div>
                    </div>
                </Teleport>
            </ClientOnly>

  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted, onUnmounted } from 'vue'
import { useHead, useRuntimeConfig, useRoute, useRouter } from '#imports'
import { useI18n } from 'vue-i18n'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import MemberCard from '~/components/MemberCard.vue'
import { Cropper, CircleStencil } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

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
const { t, locale, te } = useI18n()

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

const isMobileViewport = () => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(max-width: 767px)').matches
}

// View mode can be visual graph or directory grid
const viewMode = ref<'visual' | 'grid'>(resolveInitialViewMode())
const editMode = ref(resolveInitialEditMode())
const isEditorSheetOpen = ref(true)
const isMobileView = ref(false)
const MOBILE_EDITOR_MIN_VH = 34
const MOBILE_EDITOR_MAX_VH = 88
const MOBILE_EDITOR_DEFAULT_VH = 58
const mobileEditorSheetVh = ref(MOBILE_EDITOR_DEFAULT_VH)
const isResizingEditorSheet = ref(false)
const loading = computed(() => familyStore.loading)
const svgRef = ref<SVGSVGElement | null>(null)
const chartContainer = ref<HTMLDivElement | null>(null)
const selectedMember = ref<FamilyMember | null>(null)

const clampMobileEditorHeight = (value: number) => {
    return Math.max(MOBILE_EDITOR_MIN_VH, Math.min(MOBILE_EDITOR_MAX_VH, value))
}

const mobileEditorSheetStyle = computed(() => {
    if (!isMobileViewport()) return {}
    const h = clampMobileEditorHeight(mobileEditorSheetVh.value)
    return {
        height: `${h}vh`,
        maxHeight: `${h}vh`,
        minHeight: `${MOBILE_EDITOR_MIN_VH}vh`,
    }
})

const adjustMobileZoom = (direction: 'in' | 'out') => {
    if (!svgRef.value || !chartContainer.value || !globalZoom || !globalSVG) return
    const current = d3.zoomTransform(svgRef.value)
    const factor = direction === 'in' ? 1.24 : 1 / 1.24
    const minScale = 0.35
    const maxScale = 4
    const nextScale = Math.max(minScale, Math.min(maxScale, current.k * factor))
    if (Math.abs(nextScale - current.k) < 0.0001) return

    const cx = chartContainer.value.clientWidth / 2
    const cy = chartContainer.value.clientHeight / 2
    const nextX = cx - ((cx - current.x) * nextScale) / current.k
    const nextY = cy - ((cy - current.y) * nextScale) / current.k
    const nextTransform = d3.zoomIdentity.translate(nextX, nextY).scale(nextScale)
    globalSVG.transition().duration(180).call(globalZoom.transform as any, nextTransform)
}

// Directory UI state
const layout = ref<'grid'|'list'|'compact'>('grid')
const minWidth = ref(250)
const searchQuery = ref('')
const searchResults = ref<FamilyMember[]>([])
const communityRoles = ref<Array<{ id: number; name: string; priority: number }>>([])

const addRelationType = ref<'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD'>('CHILD')
const addRelativeMode = ref<'create' | 'link'>('create')
const addRelativeForm = ref({
    first_name: '',
    last_name: '',
    name_ml: '',
    nickname: '',
    member_id: '',
    gender: 'M' as 'M' | 'F' | 'O',
    age: '',
    date_of_birth: '',
    blood_group: '',
    occupation: '',
    education: '',
    committee_role: '',
    phone_no: '',
    email_id: '',
    address: '',
    bio: '',
    church_parish: '',
    is_deceased: false,
    date_of_death: '',
})
const addRelativeUseDob = ref(true)
const addRelativeAvatar = ref<File | null>(null)
const addRelativeAvatarPreview = ref<string | null>(null)
const showAddRelativeCropper = ref(false)
const addRelativeTempImage = ref<string | null>(null)
const addRelativeCropperRef = ref<any>(null)
const linkSearchQuery = ref('')
const linkSearchResults = ref<any[]>([])
const linkSearchLoading = ref(false)
const selectedLinkTarget = ref<any | null>(null)
const nameLookupLoadingAdd = ref(false)
const nameLookupLoadingQuick = ref(false)
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
const inviteLoading = ref(false)
const inviteLink = ref('')

const quickEditOpen = ref(false)
const quickEditLoading = ref(false)
const quickEditError = ref('')
const quickEditSuccess = ref('')
const quickEditMemberId = ref<number | null>(null)
const quickEditAvatar = ref<File | null>(null)
const quickEditForm = ref({
    first_name: '',
    last_name: '',
    member_id: '',
    name_ml: '',
    nickname: '',
    gender: 'M' as 'M' | 'F' | 'O',
    age: '',
    date_of_birth: '',
    blood_group: '',
    occupation: '',
    education: '',
    committee_role: '',
    phone_no: '',
    email_id: '',
    wedding_anniversary: '',
    church_parish: '',
    address: '',
    bio: '',
    is_deceased: false,
    date_of_death: '',
})

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
            : addRelativeForm.value.gender
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
    const fullName = `${addRelativeForm.value.first_name} ${addRelativeForm.value.last_name}`.trim()
    return fullName.length > 0
})

const resetAddRelativeForm = () => {
    addRelativeForm.value = {
        first_name: '',
        last_name: '',
        name_ml: '',
        nickname: '',
        member_id: '',
        gender: 'M',
        age: '',
        date_of_birth: '',
        blood_group: '',
        occupation: '',
        education: '',
        committee_role: '',
        phone_no: '',
        email_id: '',
        address: '',
        bio: '',
        church_parish: '',
        is_deceased: false,
        date_of_death: '',
    }
    addRelativeUseDob.value = true
    addRelativeAvatar.value = null
    addRelativeAvatarPreview.value = null
}

const onAddRelativeAvatarChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0] || null
    if (!file) return

    if (addRelativeTempImage.value) {
        URL.revokeObjectURL(addRelativeTempImage.value)
    }
    addRelativeTempImage.value = URL.createObjectURL(file)
    showAddRelativeCropper.value = true
    target.value = ''
}

const clearAddRelativeAvatar = () => {
    addRelativeAvatar.value = null
    addRelativeAvatarPreview.value = null
}

const cropAddRelativeImage = () => {
    const result = addRelativeCropperRef.value?.getResult?.()
    if (!result?.canvas) return

    result.canvas.toBlob((blob: Blob | null) => {
        if (!blob) return
        const file = new File([blob], 'member_profile.jpg', { type: 'image/jpeg' })
        addRelativeAvatar.value = file
        addRelativeAvatarPreview.value = URL.createObjectURL(file)
        showAddRelativeCropper.value = false
        if (addRelativeTempImage.value) {
            URL.revokeObjectURL(addRelativeTempImage.value)
            addRelativeTempImage.value = null
        }
    }, 'image/jpeg')
}

const cancelAddRelativeCrop = () => {
    showAddRelativeCropper.value = false
    if (addRelativeTempImage.value) {
        URL.revokeObjectURL(addRelativeTempImage.value)
        addRelativeTempImage.value = null
    }
}

const fetchMalayalamEquivalent = async (name: string): Promise<string | null> => {
    const query = String(name || '').trim()
    if (!query) return null

    try {
        const url = `https://inputtools.google.com/request?text=${encodeURIComponent(query)}&itc=ml-t-i0-und&num=1`
        const res = await fetch(url)
        if (!res.ok) return null
        const data = await res.json().catch(() => null) as any
        if (!Array.isArray(data) || data[0] !== 'SUCCESS') return null

        const suggestions = data?.[1]?.[0]?.[1]
        if (Array.isArray(suggestions) && suggestions.length > 0) {
            const translated = String(suggestions[0] || '').trim()
            return translated || null
        }
        return null
    } catch {
        return null
    }
}

const lookupMalayalamNameForAddRelative = async () => {
    const fullName = `${addRelativeForm.value.first_name} ${addRelativeForm.value.last_name}`.trim()
    if (!fullName) {
        editorError.value = 'Enter first and last name before Malayalam lookup.'
        return
    }

    nameLookupLoadingAdd.value = true
    const translated = await fetchMalayalamEquivalent(fullName)
    nameLookupLoadingAdd.value = false

    if (!translated) {
        editorError.value = 'Malayalam lookup failed. Try again.'
        return
    }

    addRelativeForm.value.name_ml = translated
    editorError.value = ''
}

const lookupMalayalamNameForQuickEdit = async () => {
    const fullName = `${quickEditForm.value.first_name} ${quickEditForm.value.last_name}`.trim()
    if (!fullName) {
        quickEditError.value = 'Enter first and last name before Malayalam lookup.'
        return
    }

    nameLookupLoadingQuick.value = true
    const translated = await fetchMalayalamEquivalent(fullName)
    nameLookupLoadingQuick.value = false

    if (!translated) {
        quickEditError.value = 'Malayalam lookup failed. Try again.'
        return
    }

    quickEditForm.value.name_ml = translated
    quickEditError.value = ''
}

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
let globalNodeCoords = new Map<number, { x: number; y: number }>()

const resolveImage = (path: string | null) => {
    if (!path) return null
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

const computeAgeFromDob = (dob?: string | null): number | null => {
    if (!dob) return null
    const birth = new Date(dob)
    if (Number.isNaN(birth.getTime())) return null

    const now = new Date()
    let years = now.getFullYear() - birth.getFullYear()
    const beforeBirthday =
        now.getMonth() < birth.getMonth() ||
        (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())

    if (beforeBirthday) years -= 1
    return years >= 0 ? years : null
}

const getDisplayAge = (member: any): string => {
    if (member?.age !== null && member?.age !== undefined && member?.age !== '') {
        return String(member.age)
    }
    const derived = computeAgeFromDob(member?.date_of_birth)
    return derived !== null ? String(derived) : '?'
}

const getDisplayName = (member: any): string => {
    const baseName = String(member?.name || '').trim()
    const localizedNameKey = `memberNames.${member?.id}`

    if (locale.value === 'ml' && member?.name_ml) {
        const malayalamName = String(member.name_ml).trim()
        if (malayalamName) return malayalamName
    }

    if (locale.value !== 'en' && member?.nickname) {
        const nickname = String(member.nickname).trim()
        if (nickname) return nickname
    }

    if (member?.name_en && locale.value === 'en') {
        return String(member.name_en).trim()
    }

    if (member?.id && te(localizedNameKey)) {
        return String(t(localizedNameKey)).trim()
    }

    return baseName || t('familyTree.labels.member')
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
 * Searches across ALL forest trees (not just the first).
 */
const focusOnMember = (targetMember: any) => {
    searchQuery.value = '' // clear search
    searchResults.value = []
    
    if (!targetMember || !globalZoom || !globalSVG) return

    const coords = globalNodeCoords.get(targetMember.id)
    const found = Boolean(coords)
    const targetX = coords?.x || 0
    const targetY = coords?.y || 0

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

const openQuickEditForSelected = () => {
    if (!selectedMember.value || !editMode.value || !allowedActions.value.can_manage) return
    const member = selectedMember.value as any
    const parts = String(member.name || '').trim().split(' ').filter(Boolean)
    quickEditMemberId.value = member.id
    quickEditForm.value = {
        first_name: parts[0] || '',
        last_name: parts.slice(1).join(' ') || '',
        member_id: member.member_id || '',
        name_ml: member.name_ml || '',
        nickname: member.nickname || '',
        gender: (member.gender || 'M') as 'M' | 'F' | 'O',
        age: member.age !== undefined && member.age !== null ? String(member.age) : '',
        date_of_birth: member.date_of_birth || '',
        blood_group: member.blood_group || '',
        occupation: member.occupation || '',
        education: member.education || '',
        committee_role: member.committee_role || '',
        phone_no: member.phone_no || '',
        email_id: member.email_id || '',
        wedding_anniversary: member.wedding_anniversary || '',
        church_parish: member.church_parish || '',
        address: member.location || member.address || '',
        bio: member.bio || '',
        is_deceased: Boolean(member.is_deceased),
        date_of_death: member.date_of_death || '',
    }
    quickEditError.value = ''
    quickEditSuccess.value = ''
    quickEditAvatar.value = null
    quickEditOpen.value = true
}

const onQuickEditAvatarChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    quickEditAvatar.value = target.files?.[0] || null
}

const saveQuickEditMember = async () => {
    if (!quickEditMemberId.value || !selectedMember.value) return
    quickEditLoading.value = true
    quickEditError.value = ''
    quickEditSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const fd = new FormData()
        const fullName = `${quickEditForm.value.first_name} ${quickEditForm.value.last_name}`.trim()

        fd.append('first_name', quickEditForm.value.first_name || '')
        fd.append('last_name', quickEditForm.value.last_name || '')
        fd.append('member_id', quickEditForm.value.member_id || '')
        fd.append('name_ml', quickEditForm.value.name_ml || '')
        if (!quickEditForm.value.first_name && !quickEditForm.value.last_name && fullName) fd.append('name', fullName)
        fd.append('nickname', quickEditForm.value.nickname || '')
        fd.append('gender', quickEditForm.value.gender || 'O')
        if (quickEditForm.value.date_of_birth) {
            fd.append('date_of_birth', quickEditForm.value.date_of_birth)
        }
        if (quickEditForm.value.age) {
            fd.append('age', quickEditForm.value.age)
        }
        fd.append('blood_group', quickEditForm.value.blood_group || '')
        fd.append('occupation', quickEditForm.value.occupation || '')
        fd.append('education', quickEditForm.value.education || '')
        fd.append('committee_role', quickEditForm.value.committee_role || '')
        fd.append('phone_no', quickEditForm.value.phone_no || '')
        fd.append('email_id', quickEditForm.value.email_id || '')
        fd.append('wedding_anniversary', quickEditForm.value.wedding_anniversary || '')
        fd.append('church_parish', quickEditForm.value.church_parish || '')
        fd.append('address', quickEditForm.value.address || '')
        fd.append('bio', quickEditForm.value.bio || '')
        fd.append('is_deceased', quickEditForm.value.is_deceased ? 'true' : 'false')
        fd.append('date_of_death', quickEditForm.value.is_deceased ? (quickEditForm.value.date_of_death || '') : '')
        if (quickEditAvatar.value) fd.append('profile_pic', quickEditAvatar.value)

        let endpoint = `${apiBase}/api/families/managed/${quickEditMemberId.value}/`
        let method: 'PUT' | 'POST' = 'PUT'

        if (contextOwnership.value.is_self) {
            endpoint = `${apiBase}/api/families/profile/`
            method = 'POST'
        }

        const res = await fetch(endpoint, {
            method,
            headers: {
                ...csrfHeaders,
            },
            credentials: 'include',
            body: fd,
        })

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            quickEditError.value = payload.error || 'Failed to update member.'
            return
        }

        quickEditSuccess.value = 'Member details updated.'
        await familyStore.fetchFamily()
        await auth.fetchProfile()
        const refreshed = nodes.value.find((n: any) => n.id === quickEditMemberId.value)
        if (refreshed) {
            selectedMember.value = refreshed as FamilyMember
            await loadMemberContext(refreshed.id)
        }
        setTimeout(initGraph, 120)
    } catch (err) {
        quickEditError.value = 'Failed to update member.'
        console.error(err)
    } finally {
        quickEditLoading.value = false
    }
}

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

const fetchCommunityRoles = async () => {
    try {
        const res = await fetch(`${apiBase}/api/profiles/community-roles/`, { credentials: 'include' })
        if (!res.ok) return
        const data = await res.json().catch(() => []) as any[]
        communityRoles.value = Array.isArray(data)
            ? data
                .filter((item) => item && item.name)
                .map((item) => ({
                    id: Number(item.id),
                    name: String(item.name),
                    priority: Number(item.priority || 100),
                }))
            : []
    } catch (err) {
        console.error('Failed to load community roles', err)
        communityRoles.value = []
    }
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
    const fullName = `${addRelativeForm.value.first_name} ${addRelativeForm.value.last_name}`.trim()
    if (addRelativeMode.value === 'create' && !fullName) {
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
        let res: Response
        if (addRelativeMode.value === 'link' && selectedLinkTarget.value) {
            const body = {
                target_member_id: selectedLinkTarget.value.id,
                relation_type: addRelationType.value,
                anniversary_date: null,
            }
            res = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...csrfHeaders,
                },
                credentials: 'include',
                body: JSON.stringify(body),
            })
        } else {
            const formData = new FormData()
            formData.append('relation_type', addRelationType.value)
            formData.append('name', fullName)
            formData.append('first_name', addRelativeForm.value.first_name)
            formData.append('last_name', addRelativeForm.value.last_name)
            if (addRelativeForm.value.name_ml) formData.append('name_ml', addRelativeForm.value.name_ml)
            formData.append('nickname', addRelativeForm.value.nickname)
            if (addRelativeForm.value.member_id) formData.append('member_id', addRelativeForm.value.member_id)
            formData.append('gender', addRelativeForm.value.gender)
            if (addRelativeUseDob.value && addRelativeForm.value.date_of_birth) formData.append('date_of_birth', addRelativeForm.value.date_of_birth)
            if (!addRelativeUseDob.value && addRelativeForm.value.age) formData.append('age', addRelativeForm.value.age)
            if (addRelativeForm.value.blood_group) formData.append('blood_group', addRelativeForm.value.blood_group)
            if (addRelativeForm.value.occupation) formData.append('occupation', addRelativeForm.value.occupation)
            if (addRelativeForm.value.education) formData.append('education', addRelativeForm.value.education)
            if (addRelativeForm.value.committee_role) formData.append('committee_role', addRelativeForm.value.committee_role)
            if (addRelativeForm.value.phone_no) formData.append('phone_no', addRelativeForm.value.phone_no)
            if (addRelativeForm.value.email_id) formData.append('email_id', addRelativeForm.value.email_id)
            if (addRelativeForm.value.address) formData.append('address', addRelativeForm.value.address)
            if (addRelativeForm.value.bio) formData.append('bio', addRelativeForm.value.bio)
            if (addRelativeForm.value.church_parish) formData.append('church_parish', addRelativeForm.value.church_parish)
            formData.append('is_deceased', addRelativeForm.value.is_deceased ? 'true' : 'false')
            if (addRelativeForm.value.is_deceased && addRelativeForm.value.date_of_death) formData.append('date_of_death', addRelativeForm.value.date_of_death)
            if (addRelativeAvatar.value) formData.append('profile_pic', addRelativeAvatar.value)

            res = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    ...csrfHeaders,
                },
                credentials: 'include',
                body: formData,
            })
        }

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || t('familyTree.editor.errors.addRelativeFailed')
            return
        }

        if (addRelativeMode.value === 'create') {
            resetAddRelativeForm()
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

const generateInviteLink = async () => {
    inviteLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    try {
        const csrfHeaders = await withCsrfHeaders()
        const res = await fetch(`${apiBase}/api/auth/generate-invite-token/`, {
            method: 'POST',
            headers: {
                ...csrfHeaders,
            },
            credentials: 'include',
        })
        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || t('login.errors.inviteFailed')
            return
        }

        inviteLink.value = `${window.location.origin}/?token=${payload.token}`
        editorSuccess.value = t('login.alerts.inviteCopied')
    } catch (err) {
        editorError.value = t('login.errors.inviteError')
        console.error(err)
    } finally {
        inviteLoading.value = false
    }
}

const copyInviteLink = async () => {
    if (!inviteLink.value) return
    try {
        await navigator.clipboard.writeText(inviteLink.value)
        editorSuccess.value = t('login.alerts.inviteCopied')
    } catch (err) {
        editorError.value = t('login.errors.inviteError')
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

const openEditorSheet = () => {
    if (isMobileViewport()) {
        mobileEditorSheetVh.value = clampMobileEditorHeight(mobileEditorSheetVh.value || MOBILE_EDITOR_DEFAULT_VH)
    }
    isEditorSheetOpen.value = true
}

const closeEditorSheet = () => {
    isEditorSheetOpen.value = false
}

let editorResizeStartY = 0
let editorResizeStartHeight = MOBILE_EDITOR_DEFAULT_VH

const onEditorResizeMove = (event: PointerEvent) => {
    if (!isResizingEditorSheet.value || !isMobileViewport()) return
    event.preventDefault()
    const deltaVh = ((editorResizeStartY - event.clientY) / Math.max(1, window.innerHeight)) * 100
    mobileEditorSheetVh.value = clampMobileEditorHeight(editorResizeStartHeight + deltaVh)
}

const stopEditorResize = () => {
    isResizingEditorSheet.value = false
    window.removeEventListener('pointermove', onEditorResizeMove)
    window.removeEventListener('pointerup', stopEditorResize)
    window.removeEventListener('pointercancel', stopEditorResize)
}

const startEditorResize = (event: PointerEvent) => {
    if (!isMobileViewport()) return
    isResizingEditorSheet.value = true
    editorResizeStartY = event.clientY
    editorResizeStartHeight = mobileEditorSheetVh.value
    window.addEventListener('pointermove', onEditorResizeMove, { passive: false })
    window.addEventListener('pointerup', stopEditorResize)
    window.addEventListener('pointercancel', stopEditorResize)
}

const onViewportResize = () => {
    isMobileView.value = isMobileViewport()
    mobileEditorSheetVh.value = clampMobileEditorHeight(mobileEditorSheetVh.value)
}

const toggleEditMode = () => {
    const next = !editMode.value
    editMode.value = next
    if (next) {
        openEditorSheet()
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
            const mobileTwoFingerOnly = isMobileViewport()
      
            const zoom = d3.zoom<SVGSVGElement, unknown>()
                .scaleExtent([0.35, 4])
        .wheelDelta((event: any) => {
            if (!(event.ctrlKey || event.metaKey)) return 0
            const factor = event.deltaMode === 1 ? 0.04 : 0.002
            const delta = -event.deltaY * factor
            return Math.max(-0.22, Math.min(0.22, delta))
        })
        .filter((event: any) => {
            if (event.type === 'wheel') {
                return Boolean(event.ctrlKey || event.metaKey)
            }

            const isTouchEvent = String(event.type || '').startsWith('touch')
            if (mobileTwoFingerOnly && isTouchEvent) {
                if (event.type === 'touchend' || event.type === 'touchcancel') {
                    return true
                }
                const touches = Number(event.touches?.length || 0)
                return touches >= 2
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

    const rawParentLinks = links.value.filter((l: any) => l.type === 'parent')
    const rawSiblingLinks = links.value.filter((l: any) => l.type === 'sibling')
      const spouseLinks = links.value.filter((l: any) => l.type === 'spouse')

      // Deduplicate and sanitize parent edges before generation layering.
      const parentLinks: Array<{ source: number; target: number }> = []
      const seenParentEdge = new Set<string>()
      const addParentEdge = (source: number, target: number) => {
          if (source === target) return
          const key = `${source}->${target}`
          if (seenParentEdge.has(key)) return
          seenParentEdge.add(key)
          parentLinks.push({ source, target })
      }
      for (const l of rawParentLinks) addParentEdge(l.source, l.target)

      const parentByChild = new Map<number, Set<number>>()
      const childrenByParent = new Map<number, Set<number>>()
    const siblingsByMember = new Map<number, Set<number>>()
      const spouseByMember = new Map<number, number>()

      for (const l of parentLinks) {
          if (!parentByChild.has(l.target)) parentByChild.set(l.target, new Set<number>())
          if (!childrenByParent.has(l.source)) childrenByParent.set(l.source, new Set<number>())
          parentByChild.get(l.target)!.add(l.source)
          childrenByParent.get(l.source)!.add(l.target)
      }

      for (const l of rawSiblingLinks) {
          if (!siblingsByMember.has(l.source)) siblingsByMember.set(l.source, new Set<number>())
          if (!siblingsByMember.has(l.target)) siblingsByMember.set(l.target, new Set<number>())
          siblingsByMember.get(l.source)!.add(l.target)
          siblingsByMember.get(l.target)!.add(l.source)
      }

      // Sibling links imply shared parents; reinforce parent edges so siblings
      // remain connected to the branch even when one sibling lacks direct parent rows.
      for (const l of rawSiblingLinks) {
          const a = l.source as number
          const b = l.target as number
          const aParents = parentByChild.get(a) || new Set<number>()
          const bParents = parentByChild.get(b) || new Set<number>()
          const merged = new Set<number>([...aParents, ...bParents])
          merged.forEach((parentId) => {
              addParentEdge(parentId, a)
              addParentEdge(parentId, b)
          })
      }

      // Rebuild parent maps after sibling reinforcement.
      parentByChild.clear()
      childrenByParent.clear()
      for (const l of parentLinks) {
          if (!parentByChild.has(l.target)) parentByChild.set(l.target, new Set<number>())
          if (!childrenByParent.has(l.source)) childrenByParent.set(l.source, new Set<number>())
          parentByChild.get(l.target)!.add(l.source)
          childrenByParent.get(l.source)!.add(l.target)
      }

      for (const l of spouseLinks) {
          // Prefer first explicit spouse link if duplicates exist.
          if (!spouseByMember.has(l.source)) spouseByMember.set(l.source, l.target)
          if (!spouseByMember.has(l.target)) spouseByMember.set(l.target, l.source)
      }

      const membersById = new Map<number, any>(nodes.value.map((n: any) => [n.id, n]))

      // Pick a person context, climb to root patriarch parent, then render only
      // that downwards subtree (+ spouses). This intentionally excludes spouse
      // parents and their side branches.
      const loggedInMember = nodes.value.find((n: any) => n.username === auth.user?.username)
    const contextPersonId = loggedInMember?.id || nodes.value[0]?.id

      const choosePatriarchParent = (childId: number): number | null => {
          const parentIds = Array.from(parentByChild.get(childId) || []).filter((pid) => membersById.has(pid))
          if (!parentIds.length) return null
          const maleParent = parentIds.find((pid) => membersById.get(pid)?.gender === 'M')
          return maleParent ?? parentIds[0]
      }

      let rootPatriarchId = contextPersonId
      const climbGuard = new Set<number>()
      while (rootPatriarchId && !climbGuard.has(rootPatriarchId)) {
          climbGuard.add(rootPatriarchId)
          const nextParent = choosePatriarchParent(rootPatriarchId)
          if (!nextParent) break
          rootPatriarchId = nextParent
      }

      const descendants = new Set<number>()
      const q: number[] = rootPatriarchId ? [rootPatriarchId] : []
      while (q.length) {
          const id = q.shift()!
          if (descendants.has(id)) continue
          descendants.add(id)

          const spouseId = spouseByMember.get(id)
          const parentSources = spouseId ? [id, spouseId] : [id]
          for (const src of parentSources) {
              const kids = Array.from(childrenByParent.get(src) || [])
              for (const childId of kids) {
                  if (!descendants.has(childId)) q.push(childId)
              }
          }
      }

      // If scoped traversal ends up tiny, fall back to full graph visibility
      // rather than collapsing the rendered tree.
      if (descendants.size <= 2 && nodes.value.length > 2) {
          nodes.value.forEach((n: any) => descendants.add(n.id))
      }

      const visibleIds = new Set<number>(descendants)
      descendants.forEach((id) => {
          const spouseId = spouseByMember.get(id)
          if (spouseId && membersById.has(spouseId)) visibleIds.add(spouseId)
      })

      // Include siblings of descendants in the same patriarchal branch.
      descendants.forEach((id) => {
          const sibs = Array.from(siblingsByMember.get(id) || []).filter((sid) => membersById.has(sid))
          sibs.forEach((sid) => visibleIds.add(sid))
      })

      // Include co-parents of descendants so wives/mothers render even when
      // no explicit spouse relationship row exists.
      descendants.forEach((childId) => {
          const parents = Array.from(parentByChild.get(childId) || []).filter((pid) => membersById.has(pid))
          if (parents.some((pid) => descendants.has(pid))) {
              parents.forEach((pid) => visibleIds.add(pid))
          }
      })

      // Also keep spouses of included siblings visible.
      Array.from(visibleIds).forEach((id) => {
          const spouseId = spouseByMember.get(id)
          if (spouseId && membersById.has(spouseId)) visibleIds.add(spouseId)
      })

      const pairKey = (a: number, b: number) => (a < b ? `${a}-${b}` : `${b}-${a}`)
      const spousePairSet = new Set<string>()
      const explicitSpouseByMember = new Map<number, Set<number>>()

      // Explicit spouse links within visible subtree.
      spouseLinks.forEach((l) => {
          if (visibleIds.has(l.source) && visibleIds.has(l.target)) {
              spousePairSet.add(pairKey(l.source, l.target))
              if (!explicitSpouseByMember.has(l.source)) explicitSpouseByMember.set(l.source, new Set<number>())
              if (!explicitSpouseByMember.has(l.target)) explicitSpouseByMember.set(l.target, new Set<number>())
              explicitSpouseByMember.get(l.source)!.add(l.target)
              explicitSpouseByMember.get(l.target)!.add(l.source)
          }
      })

      // Infer spouse only for clean co-parent cases to avoid wrong pairings.
      descendants.forEach((childId) => {
          const parents = Array.from(parentByChild.get(childId) || []).filter((pid) => visibleIds.has(pid))
          if (parents.length !== 2) return

          const [p1, p2] = parents
          const p1Member = membersById.get(p1)
          const p2Member = membersById.get(p2)
          if (!p1Member || !p2Member) return

          // Prefer opposite-gender co-parent inference only.
          const p1Gender = p1Member.gender || 'O'
          const p2Gender = p2Member.gender || 'O'
          if (!((p1Gender === 'M' && p2Gender === 'F') || (p1Gender === 'F' && p2Gender === 'M'))) {
              return
          }

          // If explicit spouse exists and points elsewhere, do not infer.
          const p1Explicit = explicitSpouseByMember.get(p1)
          if (p1Explicit && !p1Explicit.has(p2)) return
          const p2Explicit = explicitSpouseByMember.get(p2)
          if (p2Explicit && !p2Explicit.has(p1)) return

          spousePairSet.add(pairKey(p1, p2))
      })

      const spousePairs = Array.from(spousePairSet).map((k) => {
          const [a, b] = k.split('-').map((x) => parseInt(x, 10))
          return { a, b }
      })

      const spouseByMemberVisible = new Map<number, number>()
      spousePairs.forEach(({ a, b }) => {
          if (!spouseByMemberVisible.has(a)) spouseByMemberVisible.set(a, b)
          if (!spouseByMemberVisible.has(b)) spouseByMemberVisible.set(b, a)
      })

      const visibleNodes = nodes.value.filter((n: any) => visibleIds.has(n.id))

    const nodeIds = visibleNodes.map((n: any) => n.id)
      const nodeIdSet = new Set<number>(nodeIds)
      const generation = new Map<number, number>()
      nodeIds.forEach((id) => generation.set(id, 0))

      // Kahn layering avoids runaway levels when data contains cycles.
      const indegree = new Map<number, number>()
      const children = new Map<number, number[]>()
      nodeIds.forEach((id) => {
          indegree.set(id, 0)
          children.set(id, [])
      })

      for (const l of parentLinks) {
          if (!nodeIdSet.has(l.source) || !nodeIdSet.has(l.target)) continue
          children.get(l.source)!.push(l.target)
          indegree.set(l.target, (indegree.get(l.target) || 0) + 1)
      }

      const queue: number[] = nodeIds.filter((id) => (indegree.get(id) || 0) === 0)
      queue.sort((a, b) => a - b)
      const processed = new Set<number>()

      while (queue.length) {
          const id = queue.shift()!
          processed.add(id)
          const nextChildren = children.get(id) || []
          for (const childId of nextChildren) {
              const nextLevel = (generation.get(id) || 0) + 1
              if ((generation.get(childId) || 0) < nextLevel) {
                  generation.set(childId, nextLevel)
              }
              const nextIn = (indegree.get(childId) || 0) - 1
              indegree.set(childId, nextIn)
              if (nextIn === 0) queue.push(childId)
          }
      }

      // Remaining cyclic nodes are anchored near any processed parent if possible.
      const cyclicIds = nodeIds.filter((id) => !processed.has(id))
      for (const id of cyclicIds) {
          const parentIds = Array.from(parentByChild.get(id) || [])
          const processedParentLevels = parentIds
              .filter((pid) => processed.has(pid))
              .map((pid) => generation.get(pid) || 0)
          if (processedParentLevels.length) {
              generation.set(id, Math.max(...processedParentLevels) + 1)
          }
      }

      // Harmonize spouse + sibling rows iteratively to avoid spouse floating above
      // a sibling after a later sibling-alignment update.
      for (let pass = 0; pass < 4; pass += 1) {
          let changed = false

          spousePairs.forEach(({ a, b }) => {
              if (!nodeIdSet.has(a) || !nodeIdSet.has(b)) return
              const aligned = Math.max(generation.get(a) || 0, generation.get(b) || 0)
              if ((generation.get(a) || 0) !== aligned) {
                  generation.set(a, aligned)
                  changed = true
              }
              if ((generation.get(b) || 0) !== aligned) {
                  generation.set(b, aligned)
                  changed = true
              }
          })

          rawSiblingLinks.forEach((l: any) => {
              if (!nodeIdSet.has(l.source) || !nodeIdSet.has(l.target)) return
              const aligned = Math.max(generation.get(l.source) || 0, generation.get(l.target) || 0)
              if ((generation.get(l.source) || 0) !== aligned) {
                  generation.set(l.source, aligned)
                  changed = true
              }
              if ((generation.get(l.target) || 0) !== aligned) {
                  generation.set(l.target, aligned)
                  changed = true
              }
          })

          if (!changed) break
      }

      // Only keep parent edges that move downward exactly one+ generation.
      const renderParentLinks = parentLinks.filter((l) => {
          const sourceGen = generation.get(l.source) || 0
          const targetGen = generation.get(l.target) || 0
          return nodeIdSet.has(l.source) && nodeIdSet.has(l.target) && targetGen > sourceGen
      })
    const maxLevel = Math.max(...Array.from(generation.values()))
      const levels = Array.from({ length: maxLevel + 1 }, () => [] as number[])
      nodeIds.forEach((id) => levels[generation.get(id) ?? 0].push(id))

      const levelGap = 300
    const siblingGap = 236
    const spouseGap = 186
      const topOffset = 100
      const nodeCanvasCoords = new Map<number, { x: number; y: number }>()
      const previousLevelX = new Map<number, number>()

      levels.forEach((levelIds, level) => {
          const units: number[][] = []
          const placed = new Set<number>()
          const sortedIds = [...levelIds].sort((a, b) => {
              const aName = String(membersById.get(a)?.name || '')
              const bName = String(membersById.get(b)?.name || '')
              return aName.localeCompare(bName)
          })

          for (const id of sortedIds) {
              if (placed.has(id)) continue
              const spouse = spouseByMemberVisible.get(id)
              if (spouse && generation.get(spouse) === level && !placed.has(spouse)) {
                  const me = membersById.get(id)
                  const partner = membersById.get(spouse)
                  let pair: number[]
                  if (me?.gender === 'M' && partner?.gender === 'F') {
                      pair = [id, spouse]
                  } else if (me?.gender === 'F' && partner?.gender === 'M') {
                      pair = [spouse, id]
                  } else {
                      pair = id < spouse ? [id, spouse] : [spouse, id]
                  }
                  units.push(pair)
                  placed.add(id)
                  placed.add(spouse)
              } else {
                  units.push([id])
                  placed.add(id)
              }
          }

          const parentCenterScore = (memberId: number) => {
              const parents = Array.from(parentByChild.get(memberId) || [])
              if (!parents.length) return Number.MAX_SAFE_INTEGER
              const xs = parents.map((pid) => previousLevelX.get(pid)).filter((x) => x !== undefined) as number[]
              if (!xs.length) return Number.MAX_SAFE_INTEGER
              return xs.reduce((a, b) => a + b, 0) / xs.length
          }

          units.sort((a, b) => {
              const aScore = a.reduce((sum, id) => sum + parentCenterScore(id), 0) / a.length
              const bScore = b.reduce((sum, id) => sum + parentCenterScore(id), 0) / b.length
              if (aScore !== bScore) return aScore - bScore
              return a[0] - b[0]
          })

          const fallbackStartX = width / 2 - ((Math.max(units.length, 1) - 1) * siblingGap) / 2
          const unitDesiredCenter = new Map<number, number>()
          units.forEach((unit, idx) => {
              const parentXs: number[] = []
              unit.forEach((memberId) => {
                  const parents = Array.from(parentByChild.get(memberId) || [])
                  parents.forEach((pid) => {
                      const px = previousLevelX.get(pid)
                      if (px !== undefined) parentXs.push(px)
                  })
              })
              const desired = parentXs.length
                  ? parentXs.reduce((sum, x) => sum + x, 0) / parentXs.length
                  : fallbackStartX + idx * siblingGap
              unitDesiredCenter.set(idx, desired)
          })

          const unitHalfWidths = units.map((unit) => (unit.length === 2 ? spouseGap / 2 : 0))
          const centers = units.map((_, idx) => unitDesiredCenter.get(idx) ?? (fallbackStartX + idx * siblingGap))

          for (let pass = 0; pass < 4; pass += 1) {
              for (let idx = 1; idx < centers.length; idx += 1) {
                  const minCenter = centers[idx - 1] + unitHalfWidths[idx - 1] + siblingGap + unitHalfWidths[idx]
                  if (centers[idx] < minCenter) centers[idx] = minCenter
              }

              for (let idx = centers.length - 2; idx >= 0; idx -= 1) {
                  const maxCenter = centers[idx + 1] - (unitHalfWidths[idx] + siblingGap + unitHalfWidths[idx + 1])
                  if (centers[idx] > maxCenter) centers[idx] = maxCenter
              }
          }

          const localUnitPositions: Array<{ unit: number[]; x: number[] }> = []
          for (let idx = 0; idx < units.length; idx += 1) {
              const unit = units[idx]
              const halfWidth = unitHalfWidths[idx]
              const center = centers[idx]

              if (unit.length === 2) {
                  localUnitPositions.push({ unit, x: [center - halfWidth, center + halfWidth] })
              } else {
                  localUnitPositions.push({ unit, x: [center] })
              }
          }

          const y = topOffset + level * levelGap

          for (const block of localUnitPositions) {
              block.unit.forEach((id, idx) => {
                  const x = block.x[idx]
                  nodeCanvasCoords.set(id, { x, y })
                  previousLevelX.set(id, x)
              })
          }
      })

      globalNodeCoords = nodeCanvasCoords

      const parentOverlayData = Array.from(new Set(renderParentLinks.map((l) => l.target)))
          .map((childId) => {
              const child = nodeCanvasCoords.get(childId)
              if (!child) return null

              const parentIds = renderParentLinks
                  .filter((l) => l.target === childId)
                  .map((l) => l.source)
              const parentCoords = parentIds
                  .map((pid) => nodeCanvasCoords.get(pid))
                  .filter(Boolean) as Array<{ x: number; y: number }>
              if (!parentCoords.length) return null

              const anchorParents = parentCoords.length <= 2
                  ? parentCoords
                  : [...parentCoords]
                      .sort((a, b) => Math.abs(a.x - child.x) - Math.abs(b.x - child.x))
                      .slice(0, 2)
              const avgX = anchorParents.reduce((sum, p) => sum + p.x, 0) / anchorParents.length
              const sourceY = Math.max(...parentCoords.map((p) => p.y))
              return {
                  source: { x: avgX, y: sourceY },
                  target: child,
              }
          })
          .filter(Boolean) as Array<{ source: { x: number; y: number }; target: { x: number; y: number } }>

      g.append("g")
          .attr("class", "parent-links")
          .selectAll("path")
          .data(parentOverlayData)
          .join("path")
          .attr("fill", "none")
          .attr("stroke", "#a89060")
          .attr("stroke-width", 2.5)
          .attr("stroke-linecap", "round")
          .attr("stroke-opacity", 0.7)
          .attr("d", (d) => {
              const sourceY = d.source.y + 96
              const targetY = d.target.y - 106
              const midY = (sourceY + targetY) / 2
              return `M ${d.source.x} ${sourceY} C ${d.source.x} ${midY}, ${d.target.x} ${midY}, ${d.target.x} ${targetY}`
          })

      const nodeGroup = g.append("g")
          .attr("class", "nodes")
          .selectAll(".node")
          .data(visibleNodes)
          .join("g")
          .attr("class", "node")
          .attr("transform", (d: any) => {
              const c = nodeCanvasCoords.get(d.id)
              return `translate(${c?.x || width / 2},${c?.y || topOffset})`
          })

      nodeGroup.each(function(this: any, d: any) {
          renderCard(d3.select(this), 0, d)
      })

      const spouseOverlayData = spousePairs
          .filter(({ a, b }) => {
              if (!nodeIdSet.has(a) || !nodeIdSet.has(b)) return false
              const gA = generation.get(a)
              const gB = generation.get(b)
              return gA !== undefined && gA === gB
          })
          .map(({ a: aId, b: bId }) => {
              const a = nodeCanvasCoords.get(aId)
              const b = nodeCanvasCoords.get(bId)
              if (!a || !b) return null
              return { a, b }
          })
          .filter(Boolean) as Array<{ a: { x: number; y: number }; b: { x: number; y: number } }>

      g.append("g")
          .attr("class", "spouse-links")
          .selectAll("path")
          .data(spouseOverlayData)
          .join("path")
          .attr("d", (d) => {
              const cardHalfWidth = 82
              const yOffset = -10
              const leftFirst = d.a.x <= d.b.x
              const startX = leftFirst ? d.a.x + cardHalfWidth : d.a.x - cardHalfWidth
              const endX = leftFirst ? d.b.x - cardHalfWidth : d.b.x + cardHalfWidth
              const startY = d.a.y + yOffset
              const endY = d.b.y + yOffset
              const dir = endX >= startX ? 1 : -1
              const control = Math.max(24, Math.abs(endX - startX) * 0.28)
              return `M ${startX} ${startY} C ${startX + dir * control} ${startY}, ${endX - dir * control} ${endY}, ${endX} ${endY}`
          })
          .attr("fill", "none")
          .attr("stroke", "#c9a96e")
          .attr("stroke-width", 2)
          .attr("stroke-dasharray", "6,4")
          .attr("stroke-linecap", "round")
          .attr("stroke-linejoin", "round")
          .attr("stroke-opacity", 0.8)
          .lower()

      function renderCard(selection: d3.Selection<any, any, any, any>, dx=0, d: any) {
          if (!d) return
          const cardWidth = 164
          const cardHeight = 210
          const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
          const isUser = auth.user && d.username === auth.user.username
          const isMale = d.gender === 'M'
          const isFemale = d.gender === 'F'
          const genderSymbol = isMale ? 'M' : (isFemale ? 'F' : 'O')
          const fullName = getDisplayName(d)
          
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

                    if (d.is_deceased) {
                        const badgeR = 8
                        const badgeCx = cardWidth / 2 - 14
                        const badgeCy = -cardHeight / 2 + 18

                        group.append("circle")
                            .attr("cx", badgeCx)
                            .attr("cy", badgeCy)
                            .attr("r", badgeR)
                            .attr("fill", "#475569")
                            .attr("fill-opacity", 0.92)

                        group.append("text")
                            .text("†")
                            .attr("x", badgeCx)
                            .attr("y", badgeCy + 3)
                            .attr("text-anchor", "middle")
                            .attr("fill", "#F8FAFC")
                            .attr("font-size", "11px")
                            .attr("font-weight", "800")
                            .style("pointer-events", "none")

                        group.append("title").text(String(t('memberDetailsModal.labels.deceased')))
                    }

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
                        .attr("href", resolveImage(d.photo || null) || `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=${avatarBg.replace('#','')}&color=${accentColor.replace('#','')}&bold=true`)
                        .attr("x", -36).attr("y", -cardHeight/4 + 2 - 36).attr("width", 72).attr("height", 72)
            .attr("preserveAspectRatio", "xMidYMid slice")
            .attr("clip-path", `url(#${clipId})`)
            .style("pointer-events", "none")

          // Name
          group.append("text")
                        .text(fullName)
                        .attr("x", 0).attr("y", 26)
            .attr("text-anchor", "middle")
            .attr("fill", accentColor)
            .attr("font-weight", "800")
                        .attr("font-size", "13px")
            .attr("font-family", "'Inter', 'Segoe UI', sans-serif")
            .style("pointer-events", "none")
          
          // Gender & Age pill
                    const pillWidth = 72
                    const pillHeight = 22
                                        const pillY = 52
          group.append("rect")
            .attr("x", -pillWidth/2).attr("y", pillY - pillHeight/2)
            .attr("width", pillWidth).attr("height", pillHeight).attr("rx", 10)
                        .attr("fill", isMale ? 'rgba(74,107,138,0.11)' : isFemale ? 'rgba(156,79,99,0.11)' : 'rgba(89,101,119,0.11)')

          group.append("text")
                        .text(t('familyTree.labels.agePill', { symbol: genderSymbol, age: getDisplayAge(d) }))
                        .attr("x", 0).attr("y", pillY + 4)
            .attr("text-anchor", "middle")
            .attr("fill", accentColor)
                        .attr("font-size", "10.5px")
            .attr("font-weight", "700")
      }

    const userCoords = loggedInMember ? nodeCanvasCoords.get(loggedInMember.id) : null
      
      if (userCoords) {
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
    window.addEventListener('resize', onViewportResize)
    onViewportResize()
    if (isMobileViewport() && editMode.value) {
        isEditorSheetOpen.value = false
    }
    await Promise.all([
        familyStore.fetchFamily(),
        fetchCommunityRoles(),
    ])
    initGraph()
    focusFromQuery()
})

onUnmounted(() => {
    stopEditorResize()
    window.removeEventListener('resize', onViewportResize)
    globalNodeCoords = new Map<number, { x: number; y: number }>()
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

watch(locale, () => {
    if (viewMode.value === 'visual') {
        setTimeout(initGraph, 100)
    }
})

watch(
    () => selectedMember.value?.id,
    (memberId) => {
        linkSearchQuery.value = ''
        resetLinkTarget()
        if (!memberId) return
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
        resetAddRelativeForm()
    }
})

watch(
    () => route.query,
    () => {
        editMode.value = resolveInitialEditMode()
        if (editMode.value) {
            isEditorSheetOpen.value = !isMobileViewport()
            if (isMobileViewport()) {
                mobileEditorSheetVh.value = MOBILE_EDITOR_DEFAULT_VH
            }
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

@media (max-width: 767px) {
    .quick-edit-sheet input,
    .quick-edit-sheet select,
    .quick-edit-sheet textarea,
    .editor-sheet input,
    .editor-sheet select,
    .editor-sheet textarea {
        min-height: 44px;
        padding-top: 0.625rem;
        padding-bottom: 0.625rem;
        font-size: 0.95rem;
    }

    .quick-edit-sheet button,
    .editor-sheet button {
        min-height: 42px;
    }

    .quick-edit-sheet {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }

    .editor-sheet {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }
}
</style>
