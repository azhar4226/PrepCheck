<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="bi bi-clock-history me-2"></i>UGC NET Mock Test History</h2>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="text-center py-5">
              <i class="bi bi-mortarboard display-1 text-muted mb-3"></i>
              <h4 class="text-muted">No Mock Test History Yet</h4>
              <p class="text-muted mb-4">Start taking UGC NET mock tests to see your history here.</p>
              <router-link to="/ugc-net" class="btn btn-primary">
                <i class="bi bi-mortarboard me-2"></i>
                Browse UGC NET Mock Tests
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'History'
}
</script>
