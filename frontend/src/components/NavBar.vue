<script>
import { useMainStore } from '../stores/main'

export default {
  name: 'NavBar',
  computed: {
    mainStore() {
      return useMainStore()
    },
    isAuthenticated() {
      return this.mainStore.isAuthenticated
    },
    username() {
      return this.mainStore.user?.username || ''
    }
  },
  methods: {
    logout() {
      this.mainStore.logout()
      this.$router.push('/')
    }
  }
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm py-3">
    <div class="container">
      <router-link class="navbar-brand fw-bold d-flex align-items-center" :to="{ name: 'Home' }">
        <i class="bi bi-cpu text-light fs-4 me-2"></i> LogicDaily
      </router-link>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain" aria-controls="navbarMain" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarMain">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center gap-2">
          <li class="nav-item">
            <router-link class="nav-link" active-class="active fw-bold" :to="{ name: 'Home' }">Challenge</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" active-class="active fw-bold" :to="{ name: 'Leaderboard' }">Leaderboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" active-class="active fw-bold" :to="{ name: 'Admin' }">Admin</router-link>
          </li>
          
          <!-- User Auth Profile -->
          <li v-if="isAuthenticated" class="nav-item ms-lg-3 d-flex align-items-center border-start border-light border-opacity-25 ps-lg-3 pt-2 pt-lg-0">
            <span class="navbar-text text-light me-3 fw-semibold">
              <i class="bi bi-person-circle me-1 text-info fs-5 align-middle"></i> {{ username }}
            </span>
            <button @click="logout" class="btn btn-outline-light btn-sm rounded-pill px-3">
              <i class="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar-brand {
  letter-spacing: 0.5px;
}
@media (max-width: 991.98px) {
  .border-start {
    border-left: 0 !important;
    border-top: 1px solid rgba(255,255,255,0.15) !important;
    width: 100%;
    justify-content: center;
    padding-left: 0 !important;
  }
}
</style>
