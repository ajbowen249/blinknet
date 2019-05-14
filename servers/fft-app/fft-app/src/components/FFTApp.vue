<template>
    <div>
        <div v-if="!haveInitialState">
            Connecting...
        </div>
        <div v-else class="main-controls">
            <div class="equalizer">
                <div>
                    Threshold <br />
                    <input type="range" min="0" max="10" step=".1" orient="vertical" v-model.number="threshold" @change="onConfigChanged" /> <br />
                    {{ threshold }}
                </div>
                <div>
                    Max <br />
                    <input type="range" min="0" max="10" step=".1" orient="vertical" v-model.number="maximum" @change="onConfigChanged" /> <br />
                    {{ maximum }}
                </div>
                <div><!-- Spacer --></div>
                <div>
                    Bass Gain <br />
                    <input type="range" min="0" max="5" step=".1" orient="vertical" v-model.number="bassGain" @change="onConfigChanged" /> <br />
                    {{ bassGain }}
                </div>
                <div>
                    Mid Gain <br />
                    <input type="range" min="0" max="5" step=".1" orient="vertical" v-model.number="midGain" @change="onConfigChanged" /> <br />
                    {{ midGain }}
                </div>
                <div>
                    Treble Gain <br />
                    <input type="range" min="0" max="5" step=".1" orient="vertical" v-model.number="trebleGain" @change="onConfigChanged" /> <br />
                    {{ trebleGain }}
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
                                <input type="range" min="0" max="100" step="1" orient="horizontal" v-model.number="bassCutoff" @change="onConfigChanged" />
                            </td>
                            <td>
                                {{ bassCutoffFrequency }} ({{ bassCutoff }})
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Midrange Start
                            </td>
                            <td>
                                <input type="range" min="0" max="100" step="1" orient="horizontal" v-model.number="midStart" @change="onConfigChanged" />
                            </td>
                            <td>
                                {{ midStartFrequency }} ({{ midStart }})
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Treble Start
                            </td>
                            <td>
                                <input type="range" min="0" max="100" step="1" orient="horizontal" v-model.number="trebleStart" @change="onConfigChanged" />
                            </td>
                            <td>
                                {{ trebleStartFrequency }} ({{ trebleStart }})
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
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
                <button v-on:click="resetToDefaults()">Reset To Defaults</button>
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
                maximum: this.maximum,

                bass_gain: this.bassGain,
                mid_gain: this.midGain,
                treble_gain: this.trebleGain,

                bass_cutoff: this.bassCutoff,
                mid_start: this.midStart,
                treble_start: this.trebleStart,
            });

            await this.getState();
        },
        async resetToDefaults() {
            await api.resetToDefaults();
            await this.getState();
        },
        async getState() {
            const state = (await api.getState()).state;
            this.microphoneOptions = state.recording_devices;

            this.selectedDevice = state.config.device;
            this.selectedBusIndex = state.config.bus_index;

            this.threshold = state.config.threshold;
            this.maximum = state.config.maximum;

            this.bassGain = state.config.bass_gain;
            this.midGain = state.config.mid_gain;
            this.trebleGain = state.config.treble_gain;


            this.bassCutoff = state.config.bass_cutoff;
            this.midStart = state.config.mid_start;
            this.trebleStart = state.config.treble_start;

            this.haveInitialState = true;

            this.dftInfo = state.dft_info;
        },
        indexToFrequency(index) {
            var frequency = this.dftInfo.dft_frequencies[index];
            var unit = 'Hz';
            if (frequency >= 1000) {
                frequency /= 1000;
                unit = 'kHz';
            }

            return `${frequency.toFixed(2)}${unit}`;
        },
        onConfigChanged() {
            this.restart();
        }
    },
    computed: {
        bassCutoffFrequency() {
            // HACK ALERT!
            // This was an easy place to make sure we could update sliders
            // that wouldn't trigger a restart...never do this in "real"
            // code.

            if (this.bassCutoff >= this.midStart) {
                // eslint-disable-next-line
                this.midStart = this.bassCutoff + 1;
            }

            return this.indexToFrequency(this.bassCutoff);
        },
        midStartFrequency() {
            if (this.midStart >= this.trebleStart) {
                // eslint-disable-next-line
                this.trebleStart = this.midStart + 1;
            }

            return this.indexToFrequency(this.midStart);
        },
        trebleStartFrequency() {
            if (this.trebleStart <= this.midStart) {
                // eslint-disable-next-line
                this.midStart = this.trebleStart - 1;
            }

            return this.indexToFrequency(this.trebleStart);
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
            maximum: -1,
            bassGain: -1,
            midGain: -1,
            trebleGain: -1,
            bassCutoff: 0,
            midStart: 0,
            trebleStart: 0,
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
    width: 5rem;
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
