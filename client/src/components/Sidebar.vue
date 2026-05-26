<template>
  <aside class="sidebar" :class="{ collapsed }">
    <!-- Logo block -->
    <div class="sidebar-logo">
      <template v-if="!collapsed">
        <div class="logo-full">
          <span class="logo-company">{{ t('nav.companyName') }}</span>
          <span class="logo-subtitle">{{ t('nav.subtitle') }}</span>
        </div>
      </template>
      <template v-else>
        <div class="logo-monogram">CC</div>
      </template>
    </div>

    <!-- Nav list -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: $route.path === item.to }"
        :title="collapsed ? t(item.label) : undefined"
      >
        <svg
          class="nav-icon"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          v-html="item.iconPath"
        />
        <span class="nav-label">{{ t(item.label) }}</span>
      </router-link>
    </nav>

    <!-- Footer toggle -->
    <button
      v-if="!isNarrow"
      class="sidebar-toggle"
      :title="t(collapsed ? 'sidebar.expand' : 'sidebar.collapse')"
      :aria-label="t(collapsed ? 'sidebar.expand' : 'sidebar.collapse')"
      @click="toggleSidebar"
    >
      <svg
        class="toggle-chevron"
        :class="{ 'chevron-collapsed': collapsed }"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="15 18 9 12 15 6" />
      </svg>
    </button>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'

export default {
  name: 'Sidebar',
  setup() {
    const { t } = useI18n()
    const { collapsed, isNarrow, toggleSidebar } = useSidebar()

    const navItems = [
      {
        to: '/',
        label: 'nav.overview',
        iconPath: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>'
      },
      {
        to: '/inventory',
        label: 'nav.inventory',
        iconPath: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'
      },
      {
        to: '/orders',
        label: 'nav.orders',
        iconPath: '<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/>'
      },
      {
        to: '/spending',
        label: 'nav.finance',
        iconPath: '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'
      },
      {
        to: '/demand',
        label: 'nav.demandForecast',
        iconPath: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'
      },
      {
        to: '/restocking',
        label: 'nav.restocking',
        iconPath: '<polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.5"/>'
      },
      {
        to: '/reports',
        label: 'nav.reports',
        iconPath: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>'
      }
    ]

    return { t, collapsed, isNarrow, toggleSidebar, navItems }
  }
}
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  overflow: hidden;
  transition: padding .2s ease;
}

/* Logo block */
.sidebar-logo {
  padding: var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  min-height: var(--topbar-h);
  display: flex;
  align-items: center;
}

.logo-full {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.logo-company {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text);
  letter-spacing: -0.025em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-monogram {
  width: 40px;
  height: 40px;
  background: var(--color-primary-bg);
  color: var(--color-primary-text);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.025em;
  flex-shrink: 0;
  margin: 0 auto;
}

/* Nav list */
.sidebar-nav {
  flex: 1;
  padding: var(--space-3) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  overflow-y: auto;
}

.nav-item {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--color-hover-bg);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary-text);
  font-weight: var(--font-semibold);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--color-primary);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Collapsed state */
.sidebar.collapsed .sidebar-logo {
  justify-content: center;
}

.sidebar.collapsed .sidebar-nav {
  padding: var(--space-3) var(--space-2);
  align-items: center;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: var(--space-3);
  gap: 0;
}

.sidebar.collapsed .nav-label {
  display: none;
}

/* Footer toggle button */
.sidebar-toggle {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-4);
  background: none;
  border: none;
  border-top: 1px solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease, color 0.15s ease;
  width: 100%;
  min-height: 48px;
}

.sidebar-toggle:hover {
  background: var(--color-hover-bg);
  color: var(--color-text);
}

.toggle-chevron {
  transition: transform 0.2s ease;
}

.toggle-chevron.chevron-collapsed {
  transform: rotate(180deg);
}
</style>
