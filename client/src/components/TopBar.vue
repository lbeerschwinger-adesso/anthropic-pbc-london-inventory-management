<template>
  <header class="topbar">
    <div class="topbar-filters">
      <FilterBar />
    </div>
    <div class="topbar-actions">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </header>
</template>

<script>
import FilterBar from './FilterBar.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

export default {
  name: 'TopBar',
  components: {
    FilterBar,
    LanguageSwitcher,
    ProfileMenu
  },
  emits: ['show-profile-details', 'show-tasks']
}
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 90;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-6);
  gap: var(--space-4);
  min-height: var(--topbar-h);
}

.topbar-filters {
  flex: 1;
  min-width: 0;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}
</style>
