<template>
  <footer class="bg-primary text-light py-3 mt-auto border-top border-secondary">
    <div class="container text-center">
      <p class="mb-1 fw-semibold">&copy; {{ currentYear }} LogicDaily. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'FooterBar',
  data() {
    return {
      currentYear: new Date().getFullYear()
    }
  }
}
</script>
