<template>
    <div>
        <button v-on:click="restart()">Restart</button>
    </div>
</template>

<script>

import * as api from '../utils/api';

export default {
    methods: {
        restart() {
            api.restart();
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
