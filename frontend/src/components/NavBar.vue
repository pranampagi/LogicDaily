<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container">
      <router-link class="navbar-brand fw-bold d-flex align-items-center" :to="{ name: 'Home' }">
        <i class="bi bi-cpu text-light fs-4 me-2"></i> LogicDaily
      </router-link>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain" aria-controls="navbarMain" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarMain">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" active-class="active fw-bold" :to="{ name: 'Home' }">Challenge</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" active-class="active fw-bold" :to="{ name: 'Leaderboard' }">Leaderboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" active-class="active fw-bold" :to="{ name: 'Admin' }">Admin</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar'
}
</script>

<style scoped>
.navbar-brand {
  letter-spacing: 0.5px;
}
</style>
