import { ref, computed } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'
const manualCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')

const mql = window.matchMedia('(max-width: 1024px)')
const isNarrow = ref(mql.matches)
mql.addEventListener('change', (e) => { isNarrow.value = e.matches })

// Narrow screens force icons-only; otherwise honor the saved manual preference.
const collapsed = computed(() => isNarrow.value || manualCollapsed.value)

function toggleSidebar() {
  manualCollapsed.value = !manualCollapsed.value
  localStorage.setItem(STORAGE_KEY, String(manualCollapsed.value))
}

export function useSidebar() {
  return { collapsed, isNarrow, manualCollapsed, toggleSidebar }
}
