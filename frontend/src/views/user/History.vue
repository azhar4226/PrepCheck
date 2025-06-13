<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="bi bi-clock-history me-2"></i>Quiz History</h2>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="text-center py-5">
              <i class="bi bi-clock-history display-1 text-muted mb-3"></i>
              <h4 class="text-muted">No Quiz History Yet</h4>
              <p class="text-muted mb-4">Start taking quizzes to see your history here.</p>
              <router-link to="/quiz" class="btn btn-primary">
                <i class="bi bi-list-check me-2"></i>
                Browse Quizzes
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
