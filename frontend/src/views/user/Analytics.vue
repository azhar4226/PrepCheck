<template>
  <div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="h2 text-primary">
              <i class="bi bi-graph-up me-2"></i>My Analytics
            </h1>
            <p class="text-muted mb-0">Detailed insights into your test performance and learning progress</p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-primary" @click="refreshAnalytics">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
            <router-link to="/dashboard" class="btn btn-secondary">
              <i class="bi bi-arrow-left me-1"></i>Back to Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- User Analytics Component -->
    <div class="row">
      <div class="col-12">
        <UserAnalytics ref="userAnalytics" />
      </div>
    </div>
  </div>
</template>

<script>
import UserAnalytics from '@/components/features/UserAnalytics.vue'

export default {
  name: 'UserAnalyticsPage',
  components: {
    UserAnalytics
  },
  methods: {
    refreshAnalytics() {
      if (this.$refs.userAnalytics) {
        this.$refs.userAnalytics.refreshAnalytics()
      }
    }
  }
}
</script>

<style scoped>
.container-fluid {
  padding: 2rem;
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 1rem;
  }
}
</style>
