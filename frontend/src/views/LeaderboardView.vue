<script>
import { submissionService } from '../services/api'

export default {
  name: 'LeaderboardView',
  data() {
    return {
      leaderboard: [],
      loading: false,
      error: null
    }
  },
  created() {
    this.fetchLeaderboard()
  },
  methods: {
    async fetchLeaderboard() {
      this.loading = true
      this.error = null
      try {
        const data = await submissionService.getLeaderboard()
        this.leaderboard = data
      } catch (err) {
        console.error('Failed to fetch leaderboard:', err)
        this.error = 'Failed to load leaderboard data. Please try again later.'
        this.leaderboard = []
      } finally {
        this.loading = false
      }
    },
    getRandomAvatarBg(username) {
      const colors = ['bg-info-subtle text-info', 'bg-warning-subtle text-warning-dark', 'bg-danger-subtle text-danger', 'bg-success-subtle text-success', 'bg-primary-subtle text-primary']
      let hash = 0
      for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash)
      }
      return colors[Math.abs(hash) % colors.length]
    }
  }
}
</script>

<template>
  <div class="container mt-5 mx-auto pb-5 leaderboard-container">
    <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
      <!-- Card Header -->
      <div class="card-header bg-primary text-white py-4 px-4 border-0 d-flex align-items-center justify-content-between">
        <div>
          <h2 class="fw-bold mb-0 text-white"><i class="bi bi-trophy-fill me-2 text-warning animate-bounce"></i>Global Leaderboard</h2>
          <small class="opacity-75">Top performers ranked by correct daily answers</small>
        </div>
        <button class="btn btn-outline-light btn-sm rounded-pill px-3" @click="fetchLeaderboard" :disabled="loading">
          <i class="bi bi-arrow-clockwise me-1" :class="{ 'spin-icon': loading }"></i> Refresh
        </button>
      </div>

      <!-- Card Body -->
      <div class="card-body p-4 bg-white">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h5 class="mt-4 text-muted fw-semibold">Calculating ranks...</h5>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger shadow-sm border-0 rounded-3 p-4 text-center">
          <i class="bi bi-exclamation-triangle-fill fs-3 text-danger mb-2 d-block"></i>
          <p class="mb-3 fw-medium">{{ error }}</p>
          <button class="btn btn-outline-danger btn-sm rounded-pill px-4 fw-bold shadow-sm" @click="fetchLeaderboard">
            <i class="bi bi-arrow-clockwise me-1"></i> Try Again
          </button>
        </div>

        <!-- Leaderboard Table -->
        <div v-else-if="leaderboard.length" class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light text-uppercase fs-7 fw-bold text-secondary">
              <tr>
                <th scope="col" class="py-3 px-4" style="width: 10%">Rank</th>
                <th scope="col" class="py-3">User</th>
                <th scope="col" class="py-3 text-center" style="width: 25%">Correct Answers</th>
                <th scope="col" class="py-3 text-center" style="width: 25%">Accuracy</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entry, index) in leaderboard" :key="index" :class="{ 'table-gold-glow': index === 0 }">
                <td class="py-3 px-4">
                  <span v-if="index === 0" class="badge bg-warning text-dark rounded-pill rank-badge" title="1st Place Gold">
                    <i class="bi bi-award-fill"></i> 1
                  </span>
                  <span v-else-if="index === 1" class="badge bg-secondary text-white rounded-pill rank-badge" title="2nd Place Silver">
                    <i class="bi bi-award-fill"></i> 2
                  </span>
                  <span v-else-if="index === 2" class="badge bg-bronze text-white rounded-pill rank-badge" title="3rd Place Bronze">
                    <i class="bi bi-award-fill"></i> 3
                  </span>
                  <span v-else class="text-muted fw-bold ps-2">{{ index + 1 }}</span>
                </td>
                <td class="py-3">
                  <div class="d-flex align-items-center">
                    <div class="avatar me-3" :class="getRandomAvatarBg(entry.username)">
                      {{ entry.username.slice(0, 2).toUpperCase() }}
                    </div>
                    <div>
                      <span class="fw-bold text-dark fs-5">{{ entry.username }}</span>
                      <span v-if="index === 0" class="badge bg-warning bg-opacity-15 text-warning-dark ms-2 fw-semibold fs-7 px-2">Top Mind</span>
                    </div>
                  </div>
                </td>
                <td class="py-3 text-center fw-bolder text-primary fs-5">
                  {{ entry.score }}
                </td>
                <td class="py-3 text-center">
                  <span class="fw-bold text-success">{{ entry.accuracy.toFixed(1) }}%</span>
                  <div class="progress mt-1 mx-auto" style="height: 6px; max-width: 120px;">
                    <div class="progress-bar bg-success rounded" role="progressbar" :style="{ width: entry.accuracy + '%' }" :aria-valuenow="entry.accuracy" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-5">
          <i class="bi bi-clipboard-x fs-1 text-muted mb-3 d-block"></i>
          <h4 class="fw-bold text-dark">No records yet!</h4>
          <p class="text-muted">Be the first to submit a correct answer to top the leaderboard.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.leaderboard-container {
  max-width: 900px;
}
.rank-badge {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}
.bg-bronze {
  background-color: #cd7f32;
}
.text-warning-dark {
  color: #856404;
}
.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
}
.progress {
  background-color: #f1f3f5;
}
.table-gold-glow {
  background-color: rgba(255, 193, 7, 0.02);
}
.table-gold-glow:hover {
  background-color: rgba(255, 193, 7, 0.04) !important;
}
.spin-icon {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  100% { transform: rotate(360deg); }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.animate-bounce {
  display: inline-block;
  animation: bounce 2s infinite ease-in-out;
}
</style>
