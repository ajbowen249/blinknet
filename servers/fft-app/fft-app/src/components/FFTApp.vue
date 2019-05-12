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
            <div class="equalizer">
                <div>
                    <input type="range" min="0" max="10" step=".1" orient="vertical" v-model="threshold" /> <br />
                    T
                </div>
                <div>
                    <input type="range" min="0" max="10" step=".1" orient="vertical" v-model="lowScaler" /> <br />
                    L
                </div>
                <div>
                    <input type="range" min="0" max="10" step=".1" orient="vertical" v-model="midScaler" /> <br />
                    M
                </div>
                <div>
                    <input type="range" min="0" max="10" step=".1" orient="vertical" v-model="highScaler" /> <br />
                    H
                </div>
            </div>
            <div>
                <div class="frequency-ranges">
                    <table>
                        <tr>
                            <td>
                                Bass Cutoff
                            </td>
                            <td>
                                <input type="range" min="0" max="100" step="1" orient="horizontal" v-model="bassCutoff" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Midrange Start
                            </td>
                            <td>
                                <input type="range" min="0" max="100" step="1" orient="horizontal" v-model="midStart" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Treble Start
                            </td>
                            <td>
                                <input type="range" min="0" max="100" step="1" orient="horizontal" v-model="trebleStart" />
                            </td>
                        </tr>
                    </table>
                </div>
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

                threshold: this.threshold,

                low_scaler: this.lowScaler,
                mid_scaler: this.midScaler,
                high_scaler: this.highScaler,

                bass_cutoff: this.bassCutoff,
                mid_start: this.midStart,
                treble_start: this.trebleStart,
            });

            await this.getState();
        },
        async getState() {
            const state = (await api.getState()).state;
            console.log(state);
            this.microphoneOptions = state.recording_devices;

            this.selectedDevice = state.config.device;
            this.selectedBusIndex = state.config.bus_index;

            this.threshold = state.config.threshold;

            this.lowScaler = state.config.low_scaler;
            this.midScaler = state.config.mid_scaler;
            this.highScaler = state.config.high_scaler;


            this.bassCutoff = state.config.bass_cutoff;
            this.midStart = state.config.mid_start;
            this.trebleStart = state.config.treble_start;

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
            threshold: -1,
            lowScaler: -1,
            midScaler: -1,
            highScaler: -1,
        };
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.main-controls > div {
    margin-bottom: .5rem;
}

.equalizer > div {
    display: inline-block;
}

input[type=range][orient=vertical] {
    writing-mode: bt-lr; /* IE */
    -webkit-appearance: slider-vertical; /* WebKit */
    width: 8px;
    height: 175px;
    padding: 0 5px;
}

.frequency-ranges > table {
    margin: 0 auto;
}

.frequency-ranges > table > tr > td > input[type=range] {
    width: 30rem;
}

</style>
