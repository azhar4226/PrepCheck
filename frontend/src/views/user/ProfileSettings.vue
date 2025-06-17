<template>
  <SharedProfileSettings 
    :is-admin="false"
    header-title="Profile Settings"
    header-icon="bi bi-person-circle"
    api-endpoint="/api/user/profile"
  >
    <template #additional-content>
      <!-- User-specific additional content can go here if needed -->
    </template>
  </SharedProfileSettings>
</template>

<script>
import SharedProfileSettings from '@/components/features/SharedProfileSettings.vue'

export default {
  name: 'ProfileSettings',
  components: {
    SharedProfileSettings
  }
}
</script>
