<template>
  <div id="app">
    <f-f-t-app />
  </div>
</template>

<script>
import FFTApp from './components/FFTApp.vue'

export default {
  name: 'app',
  components: {
    FFTApp
  }
}
</script>

<style>
html, body {
    height: 100%;
    width: 100%;
    margin: 0;
    padding: 0;
    background-color: #C0C0C0;
}

#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
}
</style>
