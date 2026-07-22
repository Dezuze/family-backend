<template>
    <div class="h-screen w-screen text-slate-800 font-sans pt-20 relative overflow-hidden flex flex-col" style="background: linear-gradient(135deg, #faf8f5 0%, #f0ede6 30%, #e8e4db 60%, #f5f2ec 100%);">
    
    <!-- Subtle decorative background pattern -->
    <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%23A08050&quot; fill-opacity=&quot;1&quot;%3E%3Cpath d=&quot;M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');"></div>
    
    <!-- Floating Unified Controls Area -->
    <div class="w-full px-4 sm:px-6 lg:px-8 shrink-0 z-[100] mt-4 mb-2 pointer-events-none">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 bg-white/90 backdrop-blur-xl p-3 px-5 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-white pointer-events-auto">
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

                <!-- Directory Filter Controls -->
                <div v-if="viewMode === 'grid'" class="flex flex-wrap items-center gap-3 text-sm bg-white/50 backdrop-blur-sm p-3 rounded-2xl border border-slate-200/60 shadow-sm mt-2">
                    <input type="text" v-model="filterLocation" placeholder="Filter by Location..." class="w-full sm:w-48 bg-white border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-gold/50 text-slate-700 placeholder-slate-400 shadow-sm" />
                    <input type="text" v-model="filterOccupation" placeholder="Filter by Occupation..." class="w-full sm:w-48 bg-white border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-gold/50 text-slate-700 placeholder-slate-400 shadow-sm" />
                    <select v-model="filterGender" class="w-full sm:w-36 bg-white border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-gold/50 text-slate-700 shadow-sm">
                        <option value="">Any Gender</option>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                    </select>
                    <select v-model="filterBloodGroup" class="w-full sm:w-40 bg-white border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-gold/50 text-slate-700 shadow-sm">
                        <option value="">Any Blood Grp</option>
                        <option v-for="bg in uniqueBloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <!-- Visual View -->
    <div
        v-show="viewMode === 'visual'"
        :class="['w-full flex-1 relative cursor-move touch-pan-y md:touch-none transition-all duration-300', editMode ? 'md:pr-[430px]' : '']"
        :style="isMobileView ? { touchAction: 'pan-y pinch-zoom' } : {}"
        ref="chartContainer"
    >
       <!-- Tree area backdrop -->
       <div class="absolute inset-0 rounded-none" style="background: radial-gradient(ellipse at center, rgba(160,128,80,0.04) 0%, transparent 70%);"></div>
       <div v-if="isMobileView" class="absolute left-3 top-3 z-20 md:hidden">
          <button
              type="button"
              class="h-9 w-9 rounded-xl border border-slate-200 bg-white/95 text-sm font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="showMobileTreeHelp = !showMobileTreeHelp"
              aria-label="Tree help"
          >
              ?
          </button>
          <Transition name="fade-scale">
              <div
                  v-if="showMobileTreeHelp"
                  class="mt-2 w-52 rounded-xl border border-slate-200 bg-white/95 px-3 py-2 text-[11px] font-semibold text-slate-700 shadow-xl backdrop-blur"
              >
                  <p class="font-black text-slate-800">{{ t('familyTree.editor.helpTitle') }}</p>
                  <p class="mt-1 leading-relaxed">{{ t('familyTree.editor.helpTouchGesture') }}</p>
              </div>
          </Transition>
       </div>
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
      <!-- Desktop zoom controls -->
      <div class="pointer-events-none absolute right-4 top-4 z-20 hidden md:flex flex-col gap-2">
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('in')"
              aria-label="Zoom in"
          >
              +
          </button>
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('out')"
              aria-label="Zoom out"
          >
              -
          </button>
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-lg font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="toggleHorizontalCompression"
              aria-label="Toggle horizontal compression"
              title="Compress horizontally"
          >
              ↔
          </button>
      </div>
            <svg ref="svgRef" class="w-full h-full relative z-1 touch-pan-y md:touch-none"></svg>
    </div>

     <!-- Grid View -->
     <div v-if="viewMode === 'grid'" class="max-w-7xl mx-auto px-4 pb-20 pt-6 overflow-y-auto flex-1 w-full">

         <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
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
                  <MemberCard :member="member" :partner="getPartnerForMember(member)" />
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
                :member="selectedMemberForModal" 
          :canEdit="canEditSelected"
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
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">First name</label>
                    <input v-model="quickEditForm.first_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="First name" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Last name</label>
                    <input v-model="quickEditForm.last_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Last name" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Member ID</label>
                    <input v-model="quickEditForm.member_id" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Member ID" />
                </div>
                <div class="md:col-span-2">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1 block">Malayalam name</label>
                    <div class="flex gap-2">
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
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Nickname</label>
                    <input v-model="quickEditForm.nickname" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Nickname" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Gender</label>
                    <select v-model="quickEditForm.gender" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                        <option value="O">Other</option>
                    </select>
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Generation</label>
                    <select v-model="quickEditForm.generation" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
                        <option :value="null">Auto</option>
                        <option :value="0">I</option>
                        <option :value="1">II</option>
                        <option :value="2">III</option>
                        <option :value="3">IV</option>
                        <option :value="4">V</option>
                        <option :value="5">VI</option>
                        <option :value="6">VII</option>
                        <option :value="7">VIII</option>
                        <option :value="8">IX</option>
                        <option :value="9">X</option>
                    </select>
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Date of birth</label>
                    <input v-model="quickEditForm.date_of_birth" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Age</label>
                    <input v-model="quickEditForm.age" type="number" min="0" max="150" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Age" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Blood group</label>
                    <input v-model="quickEditForm.blood_group" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Blood group" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Occupation</label>
                    <input v-model="quickEditForm.occupation" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Occupation" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Place of Work</label>
                    <input v-model="quickEditForm.place_of_work" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Place of work" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Education</label>
                    <input v-model="quickEditForm.education" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Education" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Parish</label>
                    <input v-model="quickEditForm.church_parish" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Parish" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Phone</label>
                    <input v-model="quickEditForm.phone_no" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Phone" />
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
                    <input v-model="quickEditForm.email_id" type="email" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Email" />
                </div>
                <div class="md:col-span-2 flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Wedding anniversary</label>
                    <input v-model="quickEditForm.wedding_anniversary" type="date" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                </div>
                <div class="md:col-span-2 flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Address</label>
                    <textarea v-model="quickEditForm.address" rows="2" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Address"></textarea>
                </div>
                <div class="md:col-span-2 flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Bio</label>
                    <textarea v-model="quickEditForm.bio" rows="2" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Bio"></textarea>
                </div>
                <div class="md:col-span-2 flex flex-col gap-1 rounded-xl border border-slate-200 px-3 py-2">
                    <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">Is deceased</div>
                    <label class="flex items-center gap-2 text-sm text-slate-700">
                        <input v-model="quickEditForm.is_deceased" type="checkbox" class="accent-brand-gold" />
                        Yes
                    </label>
                </div>
                <div v-if="quickEditForm.is_deceased" class="md:col-span-2 flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Date of death</label>
                    <input v-model="quickEditForm.date_of_death" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                </div>
                <div class="md:col-span-2 flex flex-col gap-1">
                    <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Profile picture</label>
                    <input type="file" accept="image/*" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" @change="onQuickEditAvatarChange" />
                </div>
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
                <div class="space-y-2">
                    <div class="text-base font-black text-slate-900">
                        {{ householdTitle }}
                    </div>
                    <div class="text-[11px] text-slate-500">
                        {{ selectedMember.relation || selectedMember.role || t('familyTree.labels.member') }}
                    </div>
                    <div v-if="selectedMemberHouseholdMembers.length > 1" class="grid gap-2 sm:grid-cols-2">
                        <button
                            v-for="person in selectedMemberHouseholdMembers"
                            :key="person.id"
                            type="button"
                            @click="selectHouseholdMember(person)"
                            :class="['rounded-xl border p-3 text-left transition duration-200', person.id === selectedMember.id ? 'border-brand-gold bg-brand-gold/10 shadow-inner' : 'border-slate-200 bg-white hover:border-brand-gold/40 hover:bg-slate-50']"
                        >
                            <div class="flex items-center justify-between gap-2">
                                <div class="text-sm font-black text-slate-900">{{ person.name }}</div>
                                <span v-if="person.id === selectedMember.id" class="rounded-full bg-brand-gold/10 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-brand-gold">Selected</span>
                            </div>
                            <div class="mt-2 text-[11px] text-slate-500">
                                {{ person.member_id || person.id || t('memberDetailsModal.labels.notAvailable') }}
                            </div>
                        </button>
                    </div>
                </div>
            </div>

            <button
                class="w-full rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!canEditSelected"
                :class="canEditSelected ? 'border-brand-gold/40 bg-brand-gold/10 text-brand-gold hover:bg-brand-gold/15' : 'border-slate-200 text-slate-400'"
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
                    <input v-model="addRelativeForm.wedding_anniversary" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Wedding anniversary" />
                    <select v-model="addRelativeForm.blood_group" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="">{{ t('onboarding.placeholders.selectBloodGroup') }}</option>
                        <option value="Unknown">{{ t('onboarding.bloodGroup.unknown') }}</option>
                        <option value="A+">A+</option><option value="A-">A-</option><option value="B+">B+</option><option value="B-">B-</option><option value="O+">O+</option><option value="O-">O-</option><option value="AB+">AB+</option><option value="AB-">AB-</option>
                    </select>
                    <input v-model="addRelativeForm.occupation" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.occupation')" />
                    <input v-model="addRelativeForm.place_of_work" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Place of work" />
                    <input v-model="addRelativeForm.education" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.education')" />
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

            <button
                v-if="lastLinkedRelation"
                class="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 transition-all duration-300 hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                :disabled="editorLoading"
                @click="undoLastLinkedRelation"
            >
                Undo last link
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
import friendlyErrorMessage from '~/utils/errorNormalizer'
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
const showMobileTreeHelp = ref(false)
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
const searchQuery = ref('')
const filterLocation = ref('')
const filterOccupation = ref('')
const filterGender = ref('')
const filterBloodGroup = ref('')

const uniqueBloodGroups = computed(() => {
    const groups = new Set((nodes.value || []).map((n: any) => n.blood_group).filter(Boolean))
    return Array.from(groups).sort()
})
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
    wedding_anniversary: '',
    blood_group: '',
    occupation: '',
    place_of_work: '',
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

const addRelativeAvatar = ref<File | null>(null)
const addRelativeAvatarPreview = ref<string | null>(null)
const addRelativeUseDob = ref(true)
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
    place_of_work: '',
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
    generation: null as number | null,
})
const lastLinkedRelation = ref<null | { anchorId: number; targetId: number; relationType: 'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD' }>(null)

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

const selectedMemberHouseholdMembers = computed(() => {
    const member = selectedMember.value as any
    if (!member) return [] as any[]
    const byId = new Map((nodes.value || []).map((n: any) => [n.id, n]))
    const memberId = member.id
    const spouseLink = (links.value || []).find(
        (l: any) => l.type === 'spouse' && (l.source === memberId || l.target === memberId)
    )
    const spouseId = spouseLink ? (spouseLink.source === memberId ? spouseLink.target : spouseLink.source) : null
    const spouse = spouseId ? byId.get(spouseId) : null
    const household = [member, spouse].filter(Boolean)
    if (household.length < 2) return household
    const primary = member.gender === 'F' && spouse?.gender === 'M' ? spouse : member
    const partner = primary === member ? spouse : member
    return partner ? [primary, partner].filter(Boolean) : household
})

const householdTitle = computed(() => {
    if (!selectedMember.value) return ''
    const members = selectedMemberHouseholdMembers.value
    if (members.length > 1) {
        return members.map((person: any) => person.name).join(' & ')
    }
    return selectedMember.value.name
})

const canEditSelected = computed(() => {
    return editMode.value && selectedMember.value !== null && (allowedActions.value.can_manage || contextOwnership.value.is_self)
})

const selectHouseholdMember = async (member: any) => {
    selectedMember.value = member
    await loadMemberContext(member.id)
}

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

const branchPalette = ['#C9A96E', '#7A9BBD', '#C88A97', '#8BB174', '#C0825A']

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
        wedding_anniversary: '',
        blood_group: '',
        occupation: '',
        place_of_work: '',
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
const layout = ref('default')
const minWidth = ref(250)
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
       list = list.filter(m => m.name.toLowerCase().includes(q) || (m.nickname || '').toLowerCase().includes(q))
   }
   
   if (filterLocation.value) {
       const l = filterLocation.value.toLowerCase()
       list = list.filter(m => 
           (m.address || '').toLowerCase().includes(l) || 
           (m.location || '').toLowerCase().includes(l) || 
           (m.place_of_work || '').toLowerCase().includes(l) || 
           (m.church_parish || '').toLowerCase().includes(l)
       )
   }
   
   if (filterOccupation.value) {
       const o = filterOccupation.value.toLowerCase()
       list = list.filter(m => (m.occupation || '').toLowerCase().includes(o))
   }
   
   if (filterGender.value) {
       list = list.filter(m => m.gender === filterGender.value)
   }
   
   if (filterBloodGroup.value) {
       list = list.filter(m => m.blood_group === filterBloodGroup.value)
   }
   
   return list
})

const getPartnerForMember = (member: any) => {
    if (!links.value || !nodes.value || !member) return null
    const memberId = Number(member.id)
    const spouseLink = links.value.find(
        (l: any) => l.type === 'spouse' && (Number(l.source) === memberId || Number(l.target) === memberId)
    )
    if (!spouseLink) return null
    const spouseId = Number(spouseLink.source) === memberId ? Number(spouseLink.target) : Number(spouseLink.source)
    return nodes.value.find((n: any) => Number(n.id) === spouseId) || null
}

const selectedMemberForModal = computed(() => {
    if (!selectedMember.value) return null

    const member = selectedMember.value as any
    const byId = new Map((nodes.value || []).map((n: any) => [n.id, n]))
    const memberId = member.id
    const spouseLink = (links.value || []).find(
        (l: any) => l.type === 'spouse' && (l.source === memberId || l.target === memberId)
    )
    const spouseId = spouseLink ? (spouseLink.source === memberId ? spouseLink.target : spouseLink.source) : null
    const spouse = spouseId ? byId.get(spouseId) : null
    const householdMembers = selectedMemberHouseholdMembers.value
    const primaryMember = householdMembers[0] || member
    const partnerMember = householdMembers[1] || spouse || null

    const children = (links.value || [])
        .filter((l: any) => l.type === 'parent' && l.source === memberId)
        .map((l: any) => byId.get(l.target))
        .filter(Boolean)
        .map((c: any) => ({ name: c.name, age: c.age }))

    return {
        ...primaryMember,
        displayName: primaryMember?.name || member.name,
        member_id: primaryMember?.member_id || primaryMember?.id,
        spouse: partnerMember?.name || member.spouse || null,
        partner: partnerMember
            ? {
                ...partnerMember,
                spouse: primaryMember?.name || member.name,
            }
            : null,
        householdMembers: householdMembers.map((person: any) => ({
            ...person,
            spouse: person.id === primaryMember?.id ? partnerMember?.name || null : primaryMember?.name || null,
        })),
        children,
    }
})

// --- Global D3 State ---
// These module-scoped variables are updated each time initGraph() runs.
// They enable the search-to-focus and auto-focus features to access
// the last-rendered tree state.
let globalZoom: any = null        // D3 zoom behavior for programmatic pan/zoom
let globalSVG: any = null         // D3 selection of the <svg> element
let globalNodeCoords = new Map<number, { x: number; y: number }>()

// Horizontal compression state (1 = normal, <1 = compressed)
const horizontalScale = ref(1)

const applyHorizontalCompression = (scale = 1, duration = 300) => {
    horizontalScale.value = scale
    if (!svgRef.value) return
    try {
        const el = svgRef.value as any
        el.style.transformOrigin = 'center top'
        el.style.transition = `transform ${duration}ms cubic-bezier(.2,.9,.2,1)`
        el.style.transform = scale && scale !== 1 ? `scaleX(${scale})` : ''
        window.setTimeout(() => {
            if (el) el.style.transition = ''
        }, duration + 20)
    } catch (e) {
        // ignore in SSR or unexpected environments
    }
}

const toggleHorizontalCompression = () => {
    const next = horizontalScale.value === 1 ? 0.78 : 1
    applyHorizontalCompression(next, 340)
}

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

const resolveLoggedInMemberId = (): number | null => {
    const rawMember = (auth.user as any)?.member
    const direct = Number(rawMember)
    if (Number.isFinite(direct) && direct > 0) return direct

    if (rawMember && typeof rawMember === 'object') {
        const nested = Number((rawMember as any).id)
        if (Number.isFinite(nested) && nested > 0) return nested
    }

    return null
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
const focusOnMember = (targetMember: any, options?: { select?: boolean }) => {
    searchQuery.value = '' // clear search
    searchResults.value = []
    const shouldSelect = options?.select ?? true
    
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
            const scale = isMobileViewport() ? 0.74 : 1.5
            globalSVG.transition().duration(1500).call(
                globalZoom.transform as any, 
                d3.zoomIdentity.translate(width/2 - targetX*scale, height/2 - targetY*scale).scale(scale)
            )
        }
        if (shouldSelect) {
            selectedMember.value = targetMember
        }
    }
}

const openMember = (m: FamilyMember) => { selectedMember.value = m }

const openQuickEditForSelected = () => {
    if (!selectedMember.value || !editMode.value || !canEditSelected.value) return
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
        place_of_work: member.place_of_work || '',
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
        generation: member.generation !== undefined ? member.generation : null,
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
        const headers = {
            Accept: 'application/json',
            ...(csrfHeaders as Record<string, string> || {}),
        }
        const fd = new FormData()
        const fullName = `${quickEditForm.value.first_name} ${quickEditForm.value.last_name}`.trim()

        fd.append('first_name', quickEditForm.value.first_name || '')
        fd.append('last_name', quickEditForm.value.last_name || '')
        fd.append('member_id', quickEditForm.value.member_id || '')
        fd.append('name_ml', quickEditForm.value.name_ml || '')
        if (!quickEditForm.value.first_name && !quickEditForm.value.last_name && fullName) fd.append('name', fullName)
        fd.append('nickname', quickEditForm.value.nickname || '')
        fd.append('gender', quickEditForm.value.gender || 'O')
        fd.append('date_of_birth', quickEditForm.value.date_of_birth || '')
        if (quickEditForm.value.age) {
            fd.append('age', quickEditForm.value.age)
        }
        fd.append('blood_group', quickEditForm.value.blood_group || '')
        fd.append('occupation', quickEditForm.value.occupation || '')
        fd.append('place_of_work', quickEditForm.value.place_of_work || '')
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
        fd.append(
            'generation',
            quickEditForm.value.generation === null || quickEditForm.value.generation === undefined
                ? ''
                : String(quickEditForm.value.generation)
        )

        let endpoint = `${apiBase}/api/families/managed/${quickEditMemberId.value}/`
        let method: 'PUT' | 'POST' = 'PUT'

        if (contextOwnership.value.is_self) {
            endpoint = `${apiBase}/api/families/profile/`
            method = 'POST'
        }

        const res = await fetch(endpoint, {
            method,
            headers,
            credentials: 'include',
            body: fd,
        })

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            quickEditError.value = friendlyErrorMessage(payload, res.status)
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
        quickEditError.value = friendlyErrorMessage(err)
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

const withCsrfHeaders = async (): Promise<HeadersInit | undefined> => {
    const csrfRes = await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrfData = await csrfRes.json().catch(() => ({}))
    const csrftoken = getCookie('csrftoken') || csrfData.csrfToken
    return csrftoken ? { 'X-CSRFToken': String(csrftoken) } : undefined
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
    if (!auth.user) return
    try {
        const res = await fetch(`${apiBase}/api/families/member-context/${memberId}/`, { credentials: 'include' })
        if (!res.ok) {
            if (res.status === 401 || res.status === 403) {
                contextOwnership.value = {
                    is_independent: false,
                    has_account: false,
                    created_by_me: false,
                    is_self: false,
                }
                allowedActions.value = {
                    can_manage: false,
                    can_add_parent: false,
                    can_add_spouse: false,
                    can_add_sibling: false,
                    can_add_child: false,
                    can_remove: false,
                }
            }
            return
        }
        const data = await res.json()
        contextOwnership.value = data.ownership_status || contextOwnership.value
        const allowed = data.allowed_actions || allowedActions.value
        if (data.ownership_status?.is_self) {
            allowed.can_manage = true
            allowed.can_add_parent = true
            allowed.can_add_spouse = true
            allowed.can_add_sibling = true
            allowed.can_add_child = true
            allowed.can_remove = true
        }
        allowedActions.value = allowed
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
    const linkedTarget = selectedLinkTarget.value

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
            const headers = {
                'Content-Type': 'application/json',
                ...(csrfHeaders ? (csrfHeaders as Record<string, string>) : {}),
            }
            res = await fetch(endpoint, {
                method: 'POST',
                headers,
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
            if (addRelativeForm.value.place_of_work) formData.append('place_of_work', addRelativeForm.value.place_of_work)
            if (addRelativeForm.value.education) formData.append('education', addRelativeForm.value.education)
            if (addRelativeForm.value.wedding_anniversary) formData.append('wedding_anniversary', addRelativeForm.value.wedding_anniversary)
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
            lastLinkedRelation.value = null
        } else {
            linkSearchQuery.value = ''
            resetLinkTarget()
            if (linkedTarget) {
                lastLinkedRelation.value = {
                    anchorId: anchorMemberId,
                    targetId: linkedTarget.id,
                    relationType: addRelationType.value,
                }
            }
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

const undoLastLinkedRelation = async () => {
    if (!lastLinkedRelation.value) return
    if (!selectedMember.value || selectedMember.value.id !== lastLinkedRelation.value.anchorId) {
        editorError.value = 'Select the same member to undo the last link.'
        return
    }

    editorLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const headers = {
            'Content-Type': 'application/json',
            ...(csrfHeaders ? (csrfHeaders as Record<string, string>) : {}),
        }
        const res = await fetch(`${apiBase}/api/families/tree-edit/${lastLinkedRelation.value.anchorId}/unlink-existing/`, {
            method: 'POST',
            headers,
            credentials: 'include',
            body: JSON.stringify({
                target_member_id: lastLinkedRelation.value.targetId,
                relation_type: lastLinkedRelation.value.relationType,
            }),
        })

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || 'Unable to undo the last link.'
            return
        }

        lastLinkedRelation.value = null
        editorSuccess.value = 'Last link undone.'
        await familyStore.fetchFamily()
        await auth.fetchProfile()
        setTimeout(initGraph, 120)
        const refreshed = nodes.value.find((n: any) => n.id === selectedMember.value?.id)
        if (refreshed) {
            selectedMember.value = refreshed as FamilyMember
            await loadMemberContext(refreshed.id)
        }
    } catch (err) {
        editorError.value = 'Unable to undo the last link.'
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
        const headers = csrfHeaders ? (csrfHeaders as Record<string, string>) : undefined
        const res = await fetch(`${apiBase}/api/auth/generate-invite-token/`, {
            method: 'POST',
            headers,
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
        const headers = csrfHeaders ? (csrfHeaders as Record<string, string>) : undefined
        const res = await fetch(`${apiBase}/api/families/tree-edit/${selectedMember.value.id}/remove/`, {
            method: 'DELETE',
            headers,
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
    if (!isMobileView.value) {
        showMobileTreeHelp.value = false
    }
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

    if (!focusId || Number.isNaN(focusId)) {
        const meId = resolveLoggedInMemberId()
        if (!meId) return
        const me = nodes.value.find((n: any) => n.id === meId)
        if (!me) return
        setTimeout(() => focusOnMember(me, { select: false }), 120)
        return
    }

    const member = nodes.value.find((n: any) => n.id === focusId)
    if (!member) return
    selectedMember.value = member as FamilyMember
    setTimeout(() => focusOnMember(member), 120)
}

// --- D3 Tree Rendering Pipeline ---
const initGraph = () => {
    if (!nodes.value.length || !svgRef.value || !chartContainer.value) return

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight
    if (width === 0 || height === 0) {
        setTimeout(initGraph, 250)
        return
    }

    const svg = d3.select(svgRef.value) as d3.Selection<SVGSVGElement, unknown, null, undefined>
    svg.attr('viewBox', `0 0 ${width} ${height}`)
    svg.selectAll('*').remove()

    const g = svg.append('g')
    const mobileTwoFingerOnly = isMobileViewport()
    const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.32, 4])
        .wheelDelta((event: any) => {
            if (!(event.ctrlKey || event.metaKey)) return 0
            const factor = event.deltaMode === 1 ? 0.04 : 0.002
            return Math.max(-0.22, Math.min(0.22, -event.deltaY * factor))
        })
        .filter((event: any) => {
            if (event.type === 'wheel') return Boolean(event.ctrlKey || event.metaKey)
            const isTouchEvent = String(event.type || '').startsWith('touch')
            if (!mobileTwoFingerOnly || !isTouchEvent) return true
            if (event.type === 'touchend' || event.type === 'touchcancel') return true
            return Number(event.touches?.length || 0) >= 2
        })
        .on('zoom', (event) => {
            g.attr('transform', event.transform)
        })
    svg.call(zoom)

    globalZoom = zoom
    globalSVG = svg

    const isCompactMobileCard = isMobileViewport()
    const cardWidth = isCompactMobileCard ? 128 : 164
    const cardHeight = isCompactMobileCard ? 170 : 210
    const siblingGap = isCompactMobileCard ? 50 : 80
    const levelGap = isCompactMobileCard ? 210 : 250
    const topOffset = isCompactMobileCard ? 96 : 120
    const spouseGap = isCompactMobileCard ? 32 : 48
    const cardHalfWidth = cardWidth / 2
    const spouseCenterOffset = (cardWidth + spouseGap) / 2

    const visibleNodeMap = new Map<number, any>()
    const duplicateNodeIds = new Set<number>()
    for (const node of nodes.value) {
        const id = Number((node as any)?.id)
        if (!Number.isFinite(id)) continue
        if (visibleNodeMap.has(id)) {
            duplicateNodeIds.add(id)
            continue
        }
        visibleNodeMap.set(id, node)
    }
    if (duplicateNodeIds.size && import.meta.dev) {
        console.warn('Duplicate family tree node ids ignored:', Array.from(duplicateNodeIds))
    }

    const visibleNodes = Array.from(visibleNodeMap.values())
    const membersById = new Map<number, any>(visibleNodes.map((node: any) => [Number(node.id), node]))
    const nodeIdSet = new Set<number>(visibleNodes.map((node: any) => Number(node.id)))

    type GraphLink = { source: number; target: number }

    const dedupeLinks = (items: Array<{ source: number; target: number; key: string }>): GraphLink[] => {
        const map = new Map<string, GraphLink>()
        for (const item of items) {
            if (!Number.isFinite(item.source) || !Number.isFinite(item.target) || item.source === item.target) continue
            if (!map.has(item.key)) {
                map.set(item.key, { source: item.source, target: item.target })
            }
        }
        return Array.from(map.values())
    }

    const parentLinks = dedupeLinks(
        links.value
            .filter((link: any) => link && link.type === 'parent')
            .map((link: any) => {
                const source = Number(link.source)
                const target = Number(link.target)
                return {
                    source,
                    target,
                    key: `${source}->${target}`,
                }
            })
    )

    const spouseLinks = dedupeLinks(
        links.value
            .filter((link: any) => link && link.type === 'spouse')
            .map((link: any) => {
                const source = Number(link.source)
                const target = Number(link.target)
                const key = source < target ? `${source}-${target}` : `${target}-${source}`
                return { source, target, key }
            })
    )

    const siblingLinks = dedupeLinks(
        links.value
            .filter((link: any) => link && link.type === 'sibling')
            .map((link: any) => {
                const source = Number(link.source)
                const target = Number(link.target)
                const key = source < target ? `${source}-${target}` : `${target}-${source}`
                return { source, target, key }
            })
    )

    const spouseByMember = new Map<number, number>()

    for (const link of spouseLinks) {
        if (!nodeIdSet.has(link.source) || !nodeIdSet.has(link.target)) continue
        if (!spouseByMember.has(link.source)) spouseByMember.set(link.source, link.target)
        if (!spouseByMember.has(link.target)) spouseByMember.set(link.target, link.source)
    }

    const activeSpouseLinks = spouseLinks.filter(
        (link) => spouseByMember.get(link.source) === link.target && spouseByMember.get(link.target) === link.source
    )

    const componentAdjacency = new Map<number, Set<number>>()
    const addComponentEdge = (a: number, b: number) => {
        if (!nodeIdSet.has(a) || !nodeIdSet.has(b) || a === b) return
        if (!componentAdjacency.has(a)) componentAdjacency.set(a, new Set<number>())
        if (!componentAdjacency.has(b)) componentAdjacency.set(b, new Set<number>())
        componentAdjacency.get(a)!.add(b)
        componentAdjacency.get(b)!.add(a)
    }

    for (const link of parentLinks) addComponentEdge(link.source, link.target)
    for (const link of activeSpouseLinks) addComponentEdge(link.source, link.target)
    for (const link of siblingLinks) addComponentEdge(link.source, link.target)

    const componentGroups: any[][] = []
    const visitedComponentNodes = new Set<number>()
    for (const node of visibleNodes) {
        const startId = Number(node.id)
        if (visitedComponentNodes.has(startId)) continue

        const componentIds: number[] = []
        const queue = [startId]
        visitedComponentNodes.add(startId)

        while (queue.length) {
            const id = queue.shift()!
            componentIds.push(id)
            for (const nextId of componentAdjacency.get(id) || []) {
                if (visitedComponentNodes.has(nextId)) continue
                visitedComponentNodes.add(nextId)
                queue.push(nextId)
            }
        }

        componentGroups.push(
            componentIds
                .map((id) => membersById.get(id))
                .filter(Boolean)
                .sort((a, b) => String(a.name || '').localeCompare(String(b.name || ''))),
        )
    }
    componentGroups.sort((a, b) => {
        const aFamily = Math.min(...a.map((node) => Number(node.family_id || node.id)))
        const bFamily = Math.min(...b.map((node) => Number(node.family_id || node.id)))
        return aFamily - bFamily || String(a[0]?.name || '').localeCompare(String(b[0]?.name || ''))
    })

    type LayoutUnit = {
        key: string
        memberIds: number[]
        children: LayoutUnit[]
    }

    const buildComponentLayout = (componentNodes: any[], startX: number) => {
        const componentNodeIds = new Set<number>(componentNodes.map((node) => Number(node.id)))
        const unitByKey = new Map<string, LayoutUnit>()
        const unitKeyByMember = new Map<number, string>()

        const orderedComponentIds = componentNodes
            .map((node) => Number(node.id))
            .filter((id) => Number.isFinite(id))
            .sort((a, b) => a - b)

        const getUnitKey = (id: number) => {
            const spouseId = spouseByMember.get(id)
            if (spouseId && componentNodeIds.has(spouseId)) {
                const first = Math.min(id, spouseId)
                const second = Math.max(id, spouseId)
                return `${first}+${second}`
            }
            return String(id)
        }

        for (const id of orderedComponentIds) {
            const key = getUnitKey(id)
            if (!unitByKey.has(key)) {
                const memberIds = key.split('+').map(Number).filter((memberId) => componentNodeIds.has(memberId))
                unitByKey.set(key, { key, memberIds, children: [] })
            }
            unitKeyByMember.set(id, key)
        }

        const childKeysByUnit = new Map<string, Set<string>>()
        const parentKeysByUnit = new Map<string, Set<string>>()
        const addUnitEdge = (parentKey: string, childKey: string) => {
            if (!unitByKey.has(parentKey) || !unitByKey.has(childKey) || parentKey === childKey) return
            if (!childKeysByUnit.has(parentKey)) childKeysByUnit.set(parentKey, new Set<string>())
            if (!parentKeysByUnit.has(childKey)) parentKeysByUnit.set(childKey, new Set<string>())
            childKeysByUnit.get(parentKey)!.add(childKey)
            parentKeysByUnit.get(childKey)!.add(parentKey)
        }

        for (const link of parentLinks) {
            if (!componentNodeIds.has(link.source) || !componentNodeIds.has(link.target)) continue
            const parentKey = unitKeyByMember.get(link.source)
            const childKey = unitKeyByMember.get(link.target)
            if (parentKey && childKey) addUnitEdge(parentKey, childKey)
        }

        const nameForUnit = (unit: LayoutUnit) => {
            return unit.memberIds
                .map((id) => String(membersById.get(id)?.name || ''))
                .join(' ')
        }

        const unitSort = (a: LayoutUnit, b: LayoutUnit) => {
            const aName = nameForUnit(a)
            const bName = nameForUnit(b)
            return aName.localeCompare(bName) || a.key.localeCompare(b.key)
        }

        const sortedUnits = Array.from(unitByKey.values()).sort(unitSort)
        const roots = sortedUnits.filter((unit) => !parentKeysByUnit.has(unit.key) || parentKeysByUnit.get(unit.key)!.size === 0)
        if (!roots.length && sortedUnits.length) roots.push(sortedUnits[0]!)

        const attached = new Set<string>()
        const cloneAsTree = (unit: LayoutUnit, path = new Set<string>()): LayoutUnit => {
            attached.add(unit.key)
            const nextPath = new Set(path)
            nextPath.add(unit.key)
            const childUnits: LayoutUnit[] = []
            for (const key of Array.from(childKeysByUnit.get(unit.key) || [])) {
                const child = unitByKey.get(key)
                if (!child || nextPath.has(child.key) || attached.has(child.key)) continue
                childUnits.push(child)
            }
            childUnits.sort(unitSort)

            return {
                key: unit.key,
                memberIds: unit.memberIds,
                children: childUnits.map((child) => cloneAsTree(child, nextPath)),
            }
        }

        const forestRoots = roots.map((root) => cloneAsTree(root))
        for (const unit of sortedUnits) {
            if (!attached.has(unit.key)) forestRoots.push(cloneAsTree(unit))
        }

        const hierarchy = d3.hierarchy<LayoutUnit>(
            { key: 'component-root', memberIds: [], children: forestRoots },
            (unit) => unit.children,
        )

        const nodeSpacingX = cardWidth + siblingGap * 0.92
        const treeLayout = d3.tree<LayoutUnit>()
            .nodeSize([nodeSpacingX, levelGap])
            .separation((a, b) => {
                const aWidth = a.data.memberIds.length > 1 ? 1.25 : 1
                const bWidth = b.data.memberIds.length > 1 ? 1.25 : 1
                const siblingMultiplier = a.parent === b.parent ? 1.05 : 1.35
                return siblingMultiplier * Math.max(aWidth, bWidth)
            })

        const laidOut = treeLayout(hierarchy)
        const realNodes = laidOut.descendants().filter((node) => node.depth > 0)
        const coords = new Map<number, { x: number; y: number }>()
        // Map member id -> member object for quick lookup of generation override
        const memberById = new Map<number, any>((nodes.value || []).map((n: any) => [n.id, n]))
        const minTreeX = Math.min(0, ...realNodes.map((node) => node.x))
        const maxTreeX = Math.max(0, ...realNodes.map((node) => node.x))
        const xOffset = startX - minTreeX + cardWidth

        for (const treeNode of realNodes) {
            const x = xOffset + treeNode.x
            const members = treeNode.data.memberIds
            if (members.length > 1) {
                const leftId = members[0]
                const rightId = members[1]
                const leftGen = leftId !== undefined ? memberById.get(leftId)?.generation : null
                const rightGen = rightId !== undefined ? memberById.get(rightId)?.generation : null
                const leftY = topOffset + ((leftGen !== null && leftGen !== undefined) ? leftGen : (treeNode.depth - 1)) * levelGap
                const rightY = topOffset + ((rightGen !== null && rightGen !== undefined) ? rightGen : (treeNode.depth - 1)) * levelGap
                if (leftId !== undefined) coords.set(leftId, { x: x - spouseCenterOffset, y: leftY })
                if (rightId !== undefined) coords.set(rightId, { x: x + spouseCenterOffset, y: rightY })
            } else {
                const singleId = members[0]
                const gen = singleId !== undefined ? memberById.get(singleId)?.generation : null
                const y = topOffset + ((gen !== null && gen !== undefined) ? gen : (treeNode.depth - 1)) * levelGap
                if (singleId !== undefined) coords.set(singleId, { x, y })
            }
        }

        return {
            coords,
            width: Math.max(maxTreeX - minTreeX + cardWidth * 2, cardWidth * 2),
            height: topOffset + Math.max(1, laidOut.height) * levelGap + cardHeight,
        }
    }

    const componentGap = isCompactMobileCard ? 120 : 180
    const nodeCanvasCoords = new Map<number, { x: number; y: number }>()
    const componentLayouts = new Map<number, { coords: Map<number, { x: number; y: number }>; width: number; height: number }>()
    const componentIndexByNodeId = new Map<number, number>()

    let familyCursorX = 80
    for (let componentIndex = 0; componentIndex < componentGroups.length; componentIndex += 1) {
        const componentNodes = componentGroups[componentIndex] || []
        const layout = buildComponentLayout(componentNodes, familyCursorX)
        componentLayouts.set(componentIndex, layout)
        for (const node of componentNodes) {
            const coord = layout.coords.get(Number(node.id))
            if (coord) nodeCanvasCoords.set(Number(node.id), coord)
            if (coord) componentIndexByNodeId.set(Number(node.id), componentIndex)
        }
        familyCursorX += layout.width + componentGap
    }

    globalNodeCoords = nodeCanvasCoords

    const bounds = Array.from(nodeCanvasCoords.values()).reduce(
        (acc, coord) => ({
            minX: Math.min(acc.minX, coord.x),
            maxX: Math.max(acc.maxX, coord.x),
            minY: Math.min(acc.minY, coord.y),
            maxY: Math.max(acc.maxY, coord.y),
        }),
        { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity }
    )

    if (Number.isFinite(bounds.minX) && Number.isFinite(bounds.maxX) && Number.isFinite(bounds.minY) && Number.isFinite(bounds.maxY)) {
        const padding = cardWidth * 2
        const contentWidth = Math.max(1, (bounds.maxX - bounds.minX) + padding * 2)
        const contentHeight = Math.max(1, (bounds.maxY - bounds.minY) + padding * 2)
        const scaleX = (width * 0.92) / contentWidth
        const scaleY = (height * 0.92) / contentHeight
        const scale = Math.max(0.15, Math.min(0.7, scaleX, scaleY))
        const centerX = (bounds.minX + bounds.maxX) / 2
        const centerY = (bounds.minY + bounds.maxY) / 2
        const fittedTransform = d3.zoomIdentity.translate(
            width / 2 - centerX * scale,
            height / 2 - centerY * scale,
        ).scale(scale)
        svg.call(zoom.transform as any, fittedTransform)
    }

    type ParentOverlayLink = {
        source: { x: number; y: number }
        target: { x: number; y: number }
        childId: number
        parentIds: number[]
        crossFamily: boolean
        branchColor?: string
    }

    const renderedNodes = (() => {
        const rendered: Array<{ key: string; members: any[]; primary: any; partner: any | null; x: number; y: number; branchIndex: number }> = []
        const seen = new Set<string>()

        for (const node of visibleNodes) {
            const id = Number(node.id)
            if (seen.has(String(id))) continue
            const spouseId = spouseByMember.get(id)
            const spouse = spouseId !== undefined ? membersById.get(spouseId) : null
            const hasCouple = Boolean(spouse && spouseId !== undefined && nodeIdSet.has(spouseId) && !seen.has(String(spouseId)))

            if (hasCouple) {
                const primary = node.gender === 'F' && spouse.gender === 'M' ? spouse : node
                const partner = primary === node ? spouse : node
                const pairIds = [Number(primary.id), Number(partner.id)].sort((a, b) => a - b)
                const key = `couple-${pairIds[0]}-${pairIds[1]}`
                seen.add(String(primary.id))
                seen.add(String(partner.id))
                const primaryCoord = nodeCanvasCoords.get(Number(primary.id))
                const partnerCoord = nodeCanvasCoords.get(Number(partner.id))
                rendered.push({
                    key,
                    members: [primary, partner],
                    primary,
                    partner,
                    x: ((primaryCoord?.x || 0) + (partnerCoord?.x || 0)) / 2,
                    y: ((primaryCoord?.y || 0) + (partnerCoord?.y || 0)) / 2,
                    branchIndex: componentIndexByNodeId.get(Number(primary.id)) || componentIndexByNodeId.get(Number(partner.id)) || 0,
                })
                continue
            }

            seen.add(String(id))
            const coord = nodeCanvasCoords.get(id)
            rendered.push({
                key: `single-${id}`,
                members: [node],
                primary: node,
                partner: null,
                x: coord?.x || width / 2,
                y: coord?.y || topOffset,
                branchIndex: componentIndexByNodeId.get(id) || 0,
            })
        }

        return rendered
    })()

    const renderedNodeCoords = new Map<number, { x: number; y: number }>()
    for (const node of renderedNodes) {
        for (const member of node.members) {
            const memberId = Number(member?.id)
            if (!Number.isFinite(memberId)) continue
            renderedNodeCoords.set(memberId, { x: node.x, y: node.y })
        }
    }

    const getRenderCoord = (id: number) => renderedNodeCoords.get(id) || nodeCanvasCoords.get(id)

    const parentLinksByChild = new Map<number, GraphLink[]>()
    for (const link of parentLinks) {
        if (!nodeCanvasCoords.has(link.source) || !nodeCanvasCoords.has(link.target)) continue
        if (!parentLinksByChild.has(link.target)) parentLinksByChild.set(link.target, [])
        parentLinksByChild.get(link.target)!.push(link)
    }

    const parentOverlayData: ParentOverlayLink[] = []
    for (const [childId, childParentLinks] of parentLinksByChild.entries()) {
        const pending = [...childParentLinks].sort((a, b) => a.source - b.source)

        while (pending.length) {
            const link = pending.shift()!
            const spouseIndex = pending.findIndex((candidate) => spouseByMember.get(link.source) === candidate.source)
            const target = getRenderCoord(childId)!

            if (spouseIndex >= 0) {
                const spouseLink = pending.splice(spouseIndex, 1)[0]!
                const firstParent = getRenderCoord(link.source)!
                const secondParent = getRenderCoord(spouseLink.source)!
                parentOverlayData.push({
                    source: {
                        x: (firstParent.x + secondParent.x) / 2,
                        y: (firstParent.y + secondParent.y) / 2,
                    },
                    target,
                    childId,
                    parentIds: [link.source, spouseLink.source],
                    crossFamily:
                        membersById.get(link.source)?.family_id !== membersById.get(childId)?.family_id ||
                        membersById.get(spouseLink.source)?.family_id !== membersById.get(childId)?.family_id,
                    branchColor: branchPalette[(componentIndexByNodeId.get(childId) || 0) % branchPalette.length],
                })
                continue
            }

            parentOverlayData.push({
                source: getRenderCoord(link.source)!,
                target,
                childId,
                parentIds: [link.source],
                crossFamily: membersById.get(link.source)?.family_id !== membersById.get(childId)?.family_id,
                branchColor: branchPalette[(componentIndexByNodeId.get(childId) || 0) % branchPalette.length],
            })
        }
    }

    // Group parent links by rounded horizontal endpoints to separate overlapping connectors
    const parentGroups = new Map<string, ParentOverlayLink[]>()
    for (const item of parentOverlayData) {
        const key = `${Math.round(item.source.x)}:${Math.round(item.target.x)}`
        if (!parentGroups.has(key)) parentGroups.set(key, [])
        parentGroups.get(key)!.push(item)
    }

    // Assign deterministic groupIndex and groupSize to each item
    for (const group of parentGroups.values()) {
        const size = group.length
        for (let i = 0; i < group.length; i++) {
            ;(group[i] as any)._groupIndex = i
            ;(group[i] as any)._groupSize = size
        }
    }

    const spouseOverlayData = activeSpouseLinks
        .filter((link) => getRenderCoord(link.source) && getRenderCoord(link.target))
        .map((link) => ({
            a: getRenderCoord(link.source)!,
            b: getRenderCoord(link.target)!,
            crossFamily: membersById.get(link.source)?.family_id !== membersById.get(link.target)?.family_id,
            branchColor: branchPalette[(componentIndexByNodeId.get(link.source) || 0) % branchPalette.length],
        }))

    const siblingOverlayData = siblingLinks
        .filter((link) => getRenderCoord(link.source) && getRenderCoord(link.target))
        .map((link) => ({
            a: getRenderCoord(link.source)!,
            b: getRenderCoord(link.target)!,
            crossFamily: membersById.get(link.source)?.family_id !== membersById.get(link.target)?.family_id,
            branchColor: branchPalette[(componentIndexByNodeId.get(link.source) || 0) % branchPalette.length],
        }))

    g.append('g')
        .attr('class', 'parent-links')
        .selectAll('path')
        .data(parentOverlayData)
        .join('path')
        .attr('fill', 'none')
        .attr('stroke', (d: any) => d.crossFamily ? '#7f6640' : d.branchColor || '#6f5a36')
        .attr('stroke-width', 2.4)
        .attr('stroke-dasharray', (d) => d.crossFamily ? '4,4' : null)
        .attr('stroke-linecap', 'round')
        .attr('stroke-opacity', (d) => d.crossFamily ? 0.6 : 1)
        .attr('data-child-id', (d) => d.childId)
        .attr('data-parent-ids', (d) => d.parentIds.join(','))
        .attr('d', (d: any) => {
            const sourceY = d.source.y + (isCompactMobileCard ? 76 : 96)
            const targetY = d.target.y - (isCompactMobileCard ? 84 : 104)
            const spread = isCompactMobileCard ? 8 : 14
            const groupSize = Number(d._groupSize || 1)
            const groupIndex = Number(d._groupIndex || 0)
            const centerIndex = (groupSize - 1) / 2
            const offsetIndex = groupSize > 1 ? (groupIndex - centerIndex) : ((Number(d.childId) % 7) - 3)
            const midYBase = sourceY + (targetY - sourceY) * 0.5
            const midY = midYBase + offsetIndex * (spread * 0.4)
            return `M ${d.source.x} ${sourceY} C ${d.source.x} ${midY} ${d.target.x} ${midY} ${d.target.x} ${targetY}`
        })

    g.append('g')
        .attr('class', 'spouse-links')
        .selectAll('path')
        .data(spouseOverlayData)
        .join('path')
        .attr('fill', 'none')
        .attr('stroke', (d: any) => d.crossFamily ? '#b08f48' : d.branchColor || '#a07b44')
        .attr('stroke-width', 2.4)
        .attr('stroke-dasharray', (d) => d.crossFamily ? '6,6' : '6,4')
        .attr('stroke-linecap', 'round')
        .attr('stroke-linejoin', 'round')
        .attr('stroke-opacity', (d) => d.crossFamily ? 0.6 : 1)
        .attr('d', (d) => {
            const leftFirst = d.a.x <= d.b.x
            const startX = leftFirst ? d.a.x + cardHalfWidth : d.a.x - cardHalfWidth
            const endX = leftFirst ? d.b.x - cardHalfWidth : d.b.x + cardHalfWidth
            const startY = d.a.y - 10
            const endY = d.b.y - 10
            const midX = startX + (endX - startX) * 0.5
            const dx = Math.min(60, Math.abs(endX - startX) * 0.35)
            const sign = leftFirst ? 1 : -1
            const c1x = midX - dx * sign
            const c2x = midX + dx * sign
            return `M ${startX} ${startY} C ${c1x} ${startY} ${c2x} ${endY} ${endX} ${endY}`
        })

    // sibling-links rendering disabled per request (no visible sibling connector lines)

    const nodeGroup = g.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(renderedNodes)
        .join('g')
        .attr('class', 'node')
        .attr('data-member-ids', (d: any) => d.members.map((m: any) => Number(m.id)).join(','))
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`)

    nodeGroup.each(function(this: any, d: any) {
        renderCard(d3.select(this), 0, d, branchPalette[d.branchIndex % branchPalette.length])
    })

}

      function renderCard(selection: d3.Selection<any, any, any, any>, dx=0, d: any, branchColor?: string) {
          if (!d) return
          const compact = isMobileViewport()
          const members = Array.isArray(d.members) && d.members.length ? d.members.filter(Boolean) : [d.primary || d]
          const primary = d.primary || members[0] || d
          const partner = d.partner || members[1] || null
          const isCouple = Boolean(partner)
          const cardWidth = compact ? 128 : 164
          const cardHeight = compact ? (isCouple ? 188 : 170) : (isCouple ? 224 : 210)
          const cardRadius = compact ? 13 : 16
          const avatarRadius = compact ? 30 : 40
          const avatarClipRadius = compact ? 27 : 36
          const avatarDiameter = avatarClipRadius * 2
          const avatarCenterY = isCouple ? (compact ? -56 : -66) : -cardHeight/4 + 2
          const nameFontSize = compact ? 11.5 : 13
          const coupleNameFontSize = compact ? 10.8 : 12.2
          const pillWidth = compact ? 62 : 72
          const pillHeight = compact ? 20 : 22
          const pillY = isCouple ? (compact ? 55 : 68) : (compact ? 43 : 52)
          const pillFontSize = compact ? 9.5 : 10.5
          const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
          const isUser = auth.user && (primary.username === auth.user.username || partner?.username === auth.user.username)
          const isMale = primary.gender === 'M'
          const isFemale = primary.gender === 'F'
          const genderSymbol = isCouple ? '2' : (isMale ? 'M' : (isFemale ? 'F' : 'O'))
          const primaryName = getDisplayName(primary)
          const partnerName = partner ? getDisplayName(partner) : ''
          const displayMemberId = partner
            ? `${primary.member_id || primary.id} / ${partner.member_id || partner.id}`
            : `${primary.member_id || primary.id}`

          const cardFill = isUser ? '#FDFBF7' : '#FFFFFF'
          const cardStroke = isUser ? '#E2C881' : 'rgba(15,23,42,0.08)'
          const accentColor = branchColor || (isUser ? '#A08050' : (isMale ? '#4A6B8A' : isFemale ? '#9C4F63' : '#596577'))
          const avatarBg = isUser ? '#F5E6B3' : (isMale ? '#E6F0FA' : isFemale ? '#FAE6EB' : '#F1F5F9')
          const avatarRing = '#FFFFFF' // Clean white ring for avatars

          const clipId = `clip-${members.map((member: any) => Number(member.id)).join('-')}`
          const gradId = `grad-${members.map((member: any) => Number(member.id)).join('-')}`
          const avatarSource = primary.photo || partner?.photo || null

          // Outer shadow for the card
          group.append("rect")
              .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
              .attr("width", cardWidth).attr("height", cardHeight).attr("rx", cardRadius)
              .attr("fill", "rgba(0,0,0,0)")
              .style("filter", "drop-shadow(0 15px 35px rgba(15,23,42,0.06)) drop-shadow(0 5px 15px rgba(15,23,42,0.03))")

          // Main Card Background
          group.append("rect")
              .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
              .attr("width", cardWidth).attr("height", cardHeight).attr("rx", cardRadius)
              .attr("fill", cardFill)
              .attr("stroke", cardStroke)
              .attr("stroke-width", isUser ? 2 : 1)
              .attr("filter", primary.is_deceased || partner?.is_deceased ? "grayscale(100%) opacity(90%)" : "")
              .style("cursor", "pointer")
              .on("click", () => openMember(primary))

          const defs = group.append("defs")
          
          // Subtle glow behind avatar
          const glowId = `glow-${members.map((member: any) => Number(member.id)).join('-')}`
          const glowFilter = defs.append("filter").attr("id", glowId).attr("x", "-20%").attr("y", "-20%").attr("width", "140%").attr("height", "140%")
          glowFilter.append("feGaussianBlur").attr("stdDeviation", "8").attr("result", "blur")
          glowFilter.append("feComposite").attr("in", "SourceGraphic").attr("in2", "blur").attr("operator", "over")

          // Deceased Badge (Sleek Dark Tag)
          if (primary.is_deceased || partner?.is_deceased) {
              const badgeR = 9
              const badgeCx = cardWidth / 2 - 14
              const badgeCy = -cardHeight / 2 + 14

              group.append("circle")
                  .attr("cx", badgeCx)
                  .attr("cy", badgeCy)
                  .attr("r", badgeR)
                  .attr("fill", "#0f172a")
                  .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.15))")

              group.append("text")
                  .text("†")
                  .attr("x", badgeCx)
                  .attr("y", badgeCy + 4)
                  .attr("text-anchor", "middle")
                  .attr("fill", "#F8FAFC")
                  .attr("font-size", "13px")
                  .attr("font-weight", "800")
                  .style("pointer-events", "none")

              group.append("title").text(String(t('memberDetailsModal.labels.deceased')))
          }

          // Avatar Base & Ring
          if (isCouple) {
              const shift = avatarRadius * 0.45;
              // Partner (underneath, shifted right)
              group.append("circle")
                  .attr("cx", shift).attr("cy", avatarCenterY)
                  .attr("r", avatarRadius)
                  .attr("fill", avatarBg)
                  .attr("stroke", avatarRing)
                  .attr("stroke-width", 3.5)
                  .style("filter", "drop-shadow(0 6px 12px rgba(15,23,42,0.08))")

              defs.append("clipPath")
                  .attr("id", clipId + '-partner')
                  .append("circle")
                  .attr("cx", shift)
                  .attr("cy", avatarCenterY)
                  .attr("r", avatarClipRadius)

              group.append("image")
                  .attr("href", resolveImage(partner?.photo || null) || `https://ui-avatars.com/api/?name=${encodeURIComponent(partnerName)}&background=e2e8f0&color=475569&bold=true`)
                  .attr("x", shift - avatarClipRadius).attr("y", avatarCenterY - avatarClipRadius).attr("width", avatarDiameter).attr("height", avatarDiameter)
                  .attr("preserveAspectRatio", "xMidYMid slice")
                  .attr("clip-path", `url(#${clipId}-partner)`)
                  .style("pointer-events", "none")

              // Primary (on top, shifted left)
              group.append("circle")
                  .attr("cx", -shift).attr("cy", avatarCenterY)
                  .attr("r", avatarRadius)
                  .attr("fill", avatarBg)
                  .attr("stroke", avatarRing)
                  .attr("stroke-width", 3.5)
                  .style("filter", "drop-shadow(0 6px 12px rgba(15,23,42,0.08))")

              defs.append("clipPath")
                  .attr("id", clipId + '-primary')
                  .append("circle")
                  .attr("cx", -shift)
                  .attr("cy", avatarCenterY)
                  .attr("r", avatarClipRadius)

              group.append("image")
                  .attr("href", resolveImage(primary.photo || null) || `https://ui-avatars.com/api/?name=${encodeURIComponent(primaryName)}&background=${avatarBg.replace('#','')}&color=${accentColor.replace('#','')}&bold=true`)
                  .attr("x", -shift - avatarClipRadius).attr("y", avatarCenterY - avatarClipRadius).attr("width", avatarDiameter).attr("height", avatarDiameter)
                  .attr("preserveAspectRatio", "xMidYMid slice")
                  .attr("clip-path", `url(#${clipId}-primary)`)
                  .style("pointer-events", "none")
          } else {
              group.append("circle")
                  .attr("cx", 0).attr("cy", avatarCenterY)
                  .attr("r", avatarRadius)
                  .attr("fill", avatarBg)
                  .attr("stroke", avatarRing)
                  .attr("stroke-width", 3.5)
                  .style("filter", "drop-shadow(0 6px 12px rgba(15,23,42,0.08))")

              defs.append("clipPath")
                  .attr("id", clipId)
                  .append("circle")
                  .attr("cx", 0)
                  .attr("cy", avatarCenterY)
                  .attr("r", avatarClipRadius)

              group.append("image")
                  .attr("href", resolveImage(avatarSource || null) || `https://ui-avatars.com/api/?name=${encodeURIComponent(primaryName)}&background=${avatarBg.replace('#','')}&color=${accentColor.replace('#','')}&bold=true`)
                  .attr("x", -avatarClipRadius).attr("y", avatarCenterY - avatarClipRadius).attr("width", avatarDiameter).attr("height", avatarDiameter)
                  .attr("preserveAspectRatio", "xMidYMid slice")
                  .attr("clip-path", `url(#${clipId})`)
                  .style("pointer-events", "none")
          }

          // Names & Pills
          if (isCouple) {
            group.append("text")
                .text(primaryName)
                .attr("x", 0).attr("y", compact ? 24 : 30)
                .attr("text-anchor", "middle")
                .attr("fill", "#0f172a") // Slate-900
                .attr("font-weight", "800")
                .attr("font-size", `${coupleNameFontSize + 0.5}px`)
                .attr("font-family", "'Inter', 'Segoe UI', sans-serif")
                .style("pointer-events", "none")

            group.append("text")
                .text(partnerName)
                .attr("x", 0).attr("y", compact ? 40 : 48)
                .attr("text-anchor", "middle")
                .attr("fill", "#334155") // Slate-700
                .attr("font-weight", "600")
                .attr("font-size", `${coupleNameFontSize - 0.5}px`)
                .attr("font-family", "'Inter', 'Segoe UI', sans-serif")
                .style("pointer-events", "none")

            // Minimalist capsule for ID
            group.append("rect")
              .attr("x", -Math.min(82, cardWidth * 0.62)).attr("y", pillY - pillHeight/2)
              .attr("width", Math.min(164, cardWidth * 1.24)).attr("height", pillHeight).attr("rx", pillHeight/2)
              .attr("fill", 'rgba(241,245,249,0.7)') // slate-100/70
              .attr("stroke", 'rgba(226,232,240,0.8)') // slate-200/80

            group.append("text")
                .text(`ID ${displayMemberId}`)
                .attr("x", 0).attr("y", pillY + 3.5)
                .attr("text-anchor", "middle")
                .attr("fill", "#64748b") // slate-500
                .attr("font-size", `${pillFontSize}px`)
                .attr("font-weight", "700")
                .attr("letter-spacing", "0.5px")
          } else {
            group.append("text")
                .text(primaryName)
                .attr("x", 0).attr("y", 26)
                .attr("text-anchor", "middle")
                .attr("fill", "#0f172a") // Slate-900
                .attr("font-weight", "800")
                .attr("font-size", `${nameFontSize + 0.5}px`)
                .attr("font-family", "'Inter', 'Segoe UI', sans-serif")
                .style("pointer-events", "none")

            // Minimalist capsule for Age/Gender
            group.append("rect")
              .attr("x", -pillWidth/2).attr("y", pillY - pillHeight/2)
              .attr("width", pillWidth).attr("height", pillHeight).attr("rx", pillHeight/2)
              .attr("fill", 'rgba(241,245,249,0.7)')
              .attr("stroke", 'rgba(226,232,240,0.8)')

            group.append("text")
                .text(t('familyTree.labels.agePill', { symbol: genderSymbol, age: getDisplayAge(primary) }))
                .attr("x", 0).attr("y", pillY + 3.5)
                .attr("text-anchor", "middle")
                .attr("fill", "#64748b") // slate-500
                .attr("font-size", `${pillFontSize}px`)
                .attr("font-weight", "700")
                .attr("letter-spacing", "0.5px")
          }
      }

onMounted(async () => {
    window.addEventListener('resize', onViewportResize)
    onViewportResize()
    if (isMobileViewport() && editMode.value) {
        isEditorSheetOpen.value = false
    }
    // Ensure user is authenticated before loading this page. Redirect to login modal if not.
    const profile = await auth.fetchProfile()
    if (!profile) {
        auth.clearAuth()
        // Open site-wide login modal (Login component opens when ?login=1)
        router.replace({ path: '/', query: { login: '1', next: route.path } })
        return
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
    showMobileTreeHelp.value = false
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
        if (lastLinkedRelation.value && memberId !== lastLinkedRelation.value.anchorId) {
            lastLinkedRelation.value = null
        }
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
            isEditorSheetOpen.value = true
            if (isMobileViewport()) {
                mobileEditorSheetVh.value = MOBILE_EDITOR_DEFAULT_VH
            }
        } else {
            isEditorSheetOpen.value = false
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
