<script>
import NavBar from './components/NavBar.vue'
import FooterBar from './components/FooterBar.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    FooterBar
  }
}
</script>

<template>
  <div class="d-flex flex-column min-vh-100 bg-light">
    <NavBar />
    
    <main class="flex-grow-1">
      <!-- 
        router-view is dynamically replaced by the routed component 
        (e.g., HomeView, LeaderboardView, AdminView)
      -->
      <router-view />
    </main>
    
    <FooterBar />
  </div>
</template>

<style>
/* Base application typography and smoothing */
body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Page transition animations can be added here later */
</style>
