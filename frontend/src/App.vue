<template>
  <div id="app-layout">
    <header class="navbar-wrapper">
      <nav class="navigation-links">
        <router-link to="/">Home</router-link> |
        <router-link to="/leaderboard">Leaderboard</router-link> |
        <router-link to="/admin">Admin</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Simple styling for validation; will be upgraded to beautiful Bootstrap next */
#app-layout {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}
.navigation-links {
  padding: 15px;
}
.navigation-links a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}
.navigation-links a.router-link-exact-active {
  color: #42b983;
}
</style>
