<template>
    <div>
        <div v-if="!haveInitialState">
            Connecting...
        </div>
        <div v-else class="main-controls">
            <div>
                Bus Index
                <select v-model="selectedBusIndex">
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                </select>
            </div>
            <div>
                FFT Bins
                <select v-model="selectedFFTBins">
                    <option value="4">4</option>
                    <option value="8">8</option>
                    <option value="16">16</option>
                    <option value="32">32</option>
                    <option value="64">64</option>
                </select>
            </div>
            <div>
                Device
                <select v-model="selectedDevice">
                    <option v-for="microphone in microphoneOptions"
                            v-bind:key="microphone.name"
                            v-bind:value="microphone.name">
                            {{ microphone.name }}
                            ( {{ microphone.meta.join(' ') }} )
                    </option>
                </select>
            </div>
            <div>
                <button v-on:click="restart()">Restart</button>
            </div>
        </div>
    </div>
</template>

<script>

import * as api from '../utils/api';

export default {
    methods: {
        async restart() {
            await api.restart({
                bus_index: this.selectedBusIndex,
                device: this.selectedDevice,
                fft_bins: this.selectedFFTBins,
            });

            await this.getState();
        },
        async getState() {
            const state = (await api.getState()).state;
            this.microphoneOptions = state.recording_devices;

            this.selectedDevice = state.config.device;
            this.selectedBusIndex = state.config.bus_index;
            this.selectedFFTBins = state.config.fft_bins;

            this.haveInitialState = true;
        }
    },
    mounted: async function() {
        await this.getState();
    },
    data() {
        return {
            haveInitialState: false,
            selectedDevice: '',
            microphoneOptions: [],
            selectedBusIndex: -1,
            selectedFFTBins: -1,
        };
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.main-controls > div {
    margin-bottom: .5rem;
}

</style>