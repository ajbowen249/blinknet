<template>
    <div>
        <div>
            <button v-on:click="restart()">Restart</button>
        </div>
        <div>
            Microphone
            <select v-model="selectedMicrophone">
                <option v-for="microphone in microphoneOptions"
                        v-bind:key="microphone.name"
                        v-bind:value="microphone.name">
                        {{ microphone.name }}
                        ( {{ microphone.meta.join(' ') }} )
                </option>
            </select>
        </div>
    </div>
</template>

<script>

import * as api from '../utils/api';

export default {
    methods: {
        async restart() {
            await api.restart();
            await this.getState();
        },
        async getState() {
            const state = (await api.getState()).state;
            this.selectedMicrophone = state.config.microphone_input;
            this.selectedBusIndex = state.config.bus_index;
            this.microphoneOptions = state.recording_devices;
        }
    },
    mounted: async function() {
        await this.getState();
    },
    data() {
        return {
            selectedMicrophone: '',
            microphoneOptions: [],
            selectedBusIndex: 2,
        };
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
