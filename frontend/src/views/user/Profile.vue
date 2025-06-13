<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="bi bi-person me-2"></i>User Profile</h2>
        </div>

        <div class="row">
          <div class="col-lg-8">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Profile Information</h5>
              </div>
              <div class="card-body">
                <div class="text-center py-5">
                  <i class="bi bi-person-circle display-1 text-muted mb-3"></i>
                  <h4 class="text-muted">Profile Page</h4>
                  <p class="text-muted">User profile management coming soon.</p>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-4">
            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">Quick Actions</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <router-link to="/dashboard" class="btn btn-outline-primary">
                    <i class="bi bi-speedometer2 me-2"></i>
                    Dashboard
                  </router-link>
                  <router-link to="/quiz" class="btn btn-outline-success">
                    <i class="bi bi-list-check me-2"></i>
                    Take Quiz
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Profile'
}
</script>
