<template>
  <div class="min-h-screen bg-slate-900 text-gray-100 font-sans pt-32 relative overflow-hidden">
    
    <!-- Controls Layout -->
    <div class="absolute top-24 left-0 w-full z-10 px-4 md:px-8 flex justify-between items-start pointer-events-none">
       <!-- Title -->
       <div class="pointer-events-auto">
          <h1 class="text-3xl font-serif font-bold text-white shadow-black drop-shadow-md">Family Tree</h1>
          <p class="text-xs text-gray-400">Interactive Genealogy</p>
       </div>

       <!-- Switch & Legend -->
       <div class="flex flex-col items-end gap-4 pointer-events-auto">
          <!-- View Switch -->
          <div class="bg-slate-800/80 backdrop-blur rounded-lg p-1 flex border border-white/10">
             <button 
                @click="viewMode = 'visual'"
                :class="['px-4 py-2 rounded-md text-sm font-bold transition-all', viewMode==='visual' ? 'bg-amber-600 text-white shadow-lg' : 'text-gray-400 hover:text-white']"
             >
               Visual
             </button>
             <button 
                @click="viewMode = 'grid'"
                :class="['px-4 py-2 rounded-md text-sm font-bold transition-all', viewMode==='grid' ? 'bg-amber-600 text-white shadow-lg' : 'text-gray-400 hover:text-white']"
             >
               Directory
             </button>
          </div>

          <!-- Legend (Visual Only) -->
           <div v-if="viewMode === 'visual'" class="bg-slate-800/80 backdrop-blur p-3 rounded-lg border border-white/10 text-xs text-gray-300 space-y-2">
              <div class="flex items-center gap-2">
                 <span class="w-3 h-3 rounded-full bg-amber-500 border border-white/20"></span> You
              </div>
               <div class="flex items-center gap-2">
                 <span class="w-3 h-3 rounded-full bg-blue-500 border border-white/20"></span> Male
              </div>
               <div class="flex items-center gap-2">
                 <span class="w-3 h-3 rounded-full bg-pink-500 border border-white/20"></span> Female
              </div>
           </div>
       </div>
    </div>

    <!-- Visual View -->
    <div v-show="viewMode === 'visual'" class="w-full h-[calc(100vh-100px)] cursor-move" ref="chartContainer">
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-500"></div>
       </div>
       <svg ref="svgRef" class="w-full h-full"></svg>
    </div>

    <!-- Grid View -->
     <div v-if="viewMode === 'grid'" class="max-w-7xl mx-auto px-4 pt-10 pb-20 overflow-y-auto h-[calc(100vh-100px)]">
         <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <div 
               v-for="member in sortedMembers" 
               :key="member.id"
               @click="openMember(member)"
               class="bg-slate-800 rounded-xl overflow-hidden border border-white/5 hover:border-amber-500/50 transition-all cursor-pointer group hover:-translate-y-1 shadow-lg"
            >
               <div class="h-24 bg-gradient-to-r from-slate-700 to-slate-600 relative">
                   <div class="absolute -bottom-8 left-4 w-16 h-16 rounded-full border-4 border-slate-800 overflow-hidden bg-slate-500">
                     <img :src="member.photo || `https://ui-avatars.com/api/?name=${member.name}&background=random`" class="w-full h-full object-cover">
                   </div>
               </div>
               <div class="pt-10 px-4 pb-4">
                  <h3 class="font-bold text-white truncate">{{ member.name }}</h3>
                   <p class="text-xs text-amber-500 uppercase tracking-wide">{{ member.relation }}</p>
                   <div class="mt-3 flex items-center gap-2 text-xs text-gray-400">
                      <span>{{ member.age }} Years</span>
                      <span>•</span>
                      <span>{{ member.occupation || 'N/A' }}</span>
                   </div>
               </div>
            </div>
         </div>
     </div>

     <!-- Member Modal -->
     <MemberDetailsModal 
        v-if="selectedMember" 
        :member="selectedMember" 
        @close="selectedMember = null" 
     />

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import * as d3 from 'd3'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const viewMode = ref('visual')
const loading = ref(true)
const svgRef = ref(null)
const chartContainer = ref(null)
const nodes = ref([])
const links = ref([])
const selectedMember = ref(null)

const sortedMembers = computed(() => {
   return [...nodes.value].sort((a,b) => a.name.localeCompare(b.name))
})

const openMember = (m) => { selectedMember.value = m }

// --- D3 Logic ---
let simulation = null

const initGraph = () => {
   if (!nodes.value.length) return

   const width = chartContainer.value.clientWidth
   const height = chartContainer.value.clientHeight

   const svg = d3.select(svgRef.value)
      .attr("viewBox", [0, 0, width, height])
      .call(d3.zoom().on("zoom", (event) => g.attr("transform", event.transform)))

   svg.selectAll("*").remove() // Clear prev
   
   const g = svg.append("g")

   simulation = d3.forceSimulation(nodes.value)
      .force("link", d3.forceLink(links.value).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(40))

   // Links
   const link = g.append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links.value)
      .join("line")
      .attr("stroke-width", d => Math.sqrt(d.value || 1))

   // Nodes group
   const node = g.append("g")
       .selectAll("g")
       .data(nodes.value)
       .join("g")
       .call(drag(simulation))
       .on("click", (e, d) => openMember(d))

    // Node Circles
    node.append("circle")
       .attr("r", 25)
       .attr("stroke", "#fff")
       .attr("stroke-width", 2)
       .attr("fill", d => {
          if (auth.user && d.username === auth.user.username) return "#f59e0b" // You (Amber)
          // Simple gender guess or explicit if available
          // Since we might not have gender in graph data explicitly unless we added it
          // We can default or update API to send it.
          // For now let's random color based on ID to differentiate or just Slate
          return "#334155" 
       })

    // Node Images (Clipped)  
   node.append("image")
      .attr("xlink:href", d => d.photo || `https://ui-avatars.com/api/?name=${d.name}&background=1e293b&color=cbd5e1`)
      .attr("x", -25)
      .attr("y", -25)
      .attr("width", 50)
      .attr("height", 50)
      .attr("clip-path", "circle(25px at 25px 25px)")
      .style("pointer-events", "none") // Let click pass to group

   // Labels
   node.append("text")
      .text(d => d.name.split(' ')[0]) // First name only
      .attr("x", 0)
      .attr("y", 35)
      .attr("text-anchor", "middle")
      .attr("font-size", "10px")
      .attr("fill", "#cbd5e1")
      .style("pointer-events", "none")

   simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)

      node
        .attr("transform", d => `translate(${d.x},${d.y})`)
   })
}

const drag = (simulation) => {
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
  
  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}


onMounted(async () => {
    try {
        const res = await fetch('http://localhost:8000/api/families/tree/')
        if (res.ok) {
            const data = await res.json()
            nodes.value = data.nodes
            links.value = data.links
            initGraph()
        }
    } catch (e) {
        console.error("Tree Error", e)
    } finally {
        loading.value = false
    }
})

// Re-init graph when switching back to visual
watch(viewMode, (val) => {
    if (val === 'visual') {
        setTimeout(initGraph, 100) // wait for DOM
    }
})
</script>
