<template>
    <div class="main">
        <div v-if="!haveInitialState">
            Connecting...
        </div>
        <div v-else class="main-controls">
            <div class="equalizer">
                <div>
                    Threshold <br />
                    <vue-slider class="vertical-slider" v-model.number="threshold" v-bind="thresholdSliderOptions" @change="onConfigChanged" /> <br />
                    {{ threshold }}
                </div>
                <div>
                    Max <br />
                    <vue-slider class="vertical-slider" v-model.number="maximum" v-bind="thresholdSliderOptions" @change="onConfigChanged" /> <br />
                    {{ maximum }}
                </div>
                <div class="middle-buttons">
                    
                </div>
                <div>
                    Master<br />
                    <vue-slider class="vertical-slider" v-model.number="masterGain" v-bind="gainSliderOptions" @change="onConfigChanged" /> <br />
                    {{ masterGain }}
                </div>
                <div>
                    Bass<br />
                    <vue-slider class="vertical-slider" v-model.number="bassGain" v-bind="gainSliderOptions" @change="onConfigChanged" /> <br />
                    {{ bassGain }}
                </div>
                <div>
                    Mid<br />
                    <vue-slider class="vertical-slider" v-model.number="midGain" v-bind="gainSliderOptions" @change="onConfigChanged" /> <br />
                    {{ midGain }}
                </div>
                <div>
                    Treble<br />
                    <vue-slider class="vertical-slider" v-model.number="trebleGain" v-bind="gainSliderOptions" @change="onConfigChanged" /> <br />
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
                                <vue-slider class="horizontal-slider" v-model.number="bassCutoff" v-bind="frequencySliderOptions" @change="onConfigChanged" />
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
                                <vue-slider class="horizontal-slider" v-model.number="midStart" v-bind="frequencySliderOptions" @change="onConfigChanged" />
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
                                <vue-slider class="horizontal-slider" v-model.number="trebleStart" v-bind="frequencySliderOptions" @change="onConfigChanged" />
                            </td>
                            <td>
                                {{ trebleStartFrequency }} ({{ trebleStart }})
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div>
                <button v-on:click="enterFullscreen()">Fullscreen</button>
                <button v-on:click="restart()">Restart</button>
                <button v-on:click="resetToDefaults()">Reset To Defaults</button>
                <input type="checkbox" id="shouldLockhardware" v-model="lockHardware">
                <label for="shouldLockhardware">Lock Hardware&nbsp;&nbsp;&nbsp;&nbsp;</label>
                <div :class="lockHardware ? 'hidden' : ''">Bus Index</div>
                <select :class="lockHardware ? 'hidden' : ''" v-model="selectedBusIndex" :disabled="lockHardware">
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                </select>
            </div>
            <div :class="lockHardware ? 'hidden' : ''">
                Device
                <select v-model="selectedDevice" :disabled="lockHardware">
                    <option v-for="microphone in microphoneOptions"
                            v-bind:key="microphone.name"
                            v-bind:value="microphone.name">
                            {{ microphone.name }}
                            ( {{ microphone.meta.join(' ') }} )
                    </option>
                </select>
            </div>
        </div>
    </div>
</template>

<script>

import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'

import * as api from '../utils/api';

export default {
    methods: {
        async restart() {
            await api.restart({
                bus_index: this.selectedBusIndex,
                device: this.selectedDevice,

                threshold: this.threshold,
                maximum: this.maximum,

                master_gain: this.masterGain,
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

            this.masterGain = state.config.master_gain;
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
        },
        enterFullscreen() {
            var doc = window.document;
            var docEl = doc.documentElement;

            var requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;
            var cancelFullScreen = doc.exitFullscreen || doc.mozCancelFullScreen || doc.webkitExitFullscreen || doc.msExitFullscreen;

            if(!doc.fullscreenElement && !doc.mozFullScreenElement && !doc.webkitFullscreenElement && !doc.msFullscreenElement) {
                requestFullScreen.call(docEl);
            } else {
                cancelFullScreen.call(doc);
            }
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
        const baseSlider = {
            lazy: true,
        };

        const baseVerticalSlider = Object.assign({
            height: 215,
            width: 16,
            direction: 'btt',
            dotSize: 50,
        }, baseSlider);

        const baseHorizontalSlider = Object.assign({
            height: 8,
            width: 400,
            direction: 'ltr',
            dotSize: 20,
        }, baseSlider);

        return {
            haveInitialState: false,

            lockHardware: true,
            selectedDevice: '',
            microphoneOptions: [],
            selectedBusIndex: -1,

            threshold: -1,
            maximum: -1,
            masterGain: -1,
            bassGain: -1,
            midGain: -1,
            trebleGain: -1,
            bassCutoff: 0,
            midStart: 0,
            trebleStart: 0,

            thresholdSliderOptions: Object.assign({
                min: 0,
                max: 10,
                interval: .1,
            }, baseVerticalSlider),

            gainSliderOptions: Object.assign({
                min: 0,
                max: 1.5,
                interval: .01,
            }, baseVerticalSlider),

            frequencySliderOptions: Object.assign({
                min: 0,
                max: 100,
                interval: 1,
            }, baseHorizontalSlider),
        };
    },
    metaInfo: {
        title: 'BlinkNet Control Panel',
        titleTemplate: '%s',
        meta: [
            {
                name: 'viewport',
                content: 'width=device-width, initial-scale=1',
            },
        ]
    },
    components: {
        VueSlider
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.main {
    margin: 0;
    color: #ffffff;
}

.equalizer > div {
    display: inline-block;
    width: 5rem;
}

.vertical-slider {
    margin: 0 auto;
}

.horizontal-slider {
    margin: auto 0;
}

.frequency-ranges > table {
    margin: 0 auto;
}

.hidden {
    display: none;
}

.middle-buttons > button {
    margin-bottom: 10px;
}

</style>
