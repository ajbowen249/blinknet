const express = require('express');
const path = require('path');
const child_process = require('child_process');
const bodyParser = require('body-parser');
const fixedColor = require('./fixedColor');

const C_FixedBroadcastIntervalMS = 250;
const C_Port = 3000;

var fixedBoadcastInterval = null;

var defaultSettings = {};
var config = {};
var dftInfo = {};

var defaultServerConfig = {
    mode: 'fixed',
};

var serverConfig = Object.assign({}, defaultServerConfig);

const guiPath = path.join(__dirname, '../fft-app/dist');
const pyFFTPath = path.join(__dirname, '../../piFFT/pifft.py');

const app = express();

app.use(bodyParser.json());

var pythonProcess = undefined;

function getDefaults(done) {
    const getDefaults = child_process.spawn('python2', [
        pyFFTPath,
        '--print-defaults',
    ]);

    var output = '';
    getDefaults.stdout.on('data', (data) => {
        output += data.toString('utf8');
    });

    getDefaults.stdout.on('close', () => {
        defaultSettings = JSON.parse(output);
        config = Object.assign( { chosen_color: { r: 127, g: 0, b: 255 } }, defaultSettings);

        const getFrequencies = child_process.spawn('python2', [
            pyFFTPath,
            '--print-dft-info',
        ]);

        var output2 = '';
        getFrequencies.stdout.on('data', (data) => {
            output2 += data.toString('utf8');
        });

        getFrequencies.stdout.on('close', () => {
            dftInfo = JSON.parse(output2);
            done();
        });
    });
}

function restart(newConfig, newServerConfig) {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = undefined;
    }

    if (fixedBoadcastInterval !== null) {
        clearInterval(fixedBoadcastInterval);
        fixedBoadcastInterval = null;
    }

    config = Object.assign(config, newConfig);
    serverConfig = Object.assign(serverConfig, newServerConfig);

    if (serverConfig.mode === 'fft') {
        pythonProcess = child_process.spawn('python2', [
            pyFFTPath,
            '--bus-index', config.bus_index,
            '--device', config.device,

            '--threshold', config.threshold,
            '--maximum', config.maximum,

            '--master-gain', config.master_gain,
            '--low-gain', config.bass_gain,
            '--mid-gain', config.mid_gain,
            '--high-gain', config.treble_gain,

            '--bass-cutoff', config.bass_cutoff,
            '--mid-start', config.mid_start,
            '--treble-start', config.treble_start,
        ]);
    } else if (serverConfig.mode === 'fixed') {
        const updateColor = () => {
            fixedColor.sendFixedColor({
                r: config.chosen_color.r,
                g: config.chosen_color.g,
                b: config.chosen_color.b,
            });
        };

        updateColor();

        // In case any clients flake out, continue to occasionally send out the
        //  fixed color while in this mode.
        fixedBoadcastInterval = setInterval(updateColor, C_FixedBroadcastIntervalMS);
    }
}

var recordingDevices = [];

function getRecordingDevices(done) {
    const arecord = child_process.spawn('arecord', [ '-L' ]);

    var output = '';
    arecord.stdout.on('data', (data) => {
        output += data.toString('utf8');
    });

    arecord.stdout.on('close', () => {
        const lines = output.split(/\r?\n/);

        var currentItem = undefined;
        lines.forEach((line) => {
            if (line.startsWith('    ')) {
                currentItem.meta.push(line);
            } else {
                if (currentItem) {
                    recordingDevices.push(currentItem);
                }

                currentItem = { name: line, meta: [] };
            }
        });

        recordingDevices.push(currentItem);

        done();
    });
}

function checkRecordingDevice(deviceName) {
    return recordingDevices.some((device) => device.name === deviceName);
}

app.use('/', express.static(guiPath));

app.post('/api/restart', (req, res) => {
    restart(req.body.config, req.body.server_config);
    res.send(true);
});

app.post('/api/reset', (req, res) => {
    restart(defaultSettings, defaultServerConfig);
    res.send(true);
});

app.get('/api/state', async (req, res) => {
    res.send(JSON.stringify({
        state: {
            recording_devices: recordingDevices,
            config: config,
            dft_info: dftInfo,
            server_config: serverConfig,
        }
    }));
});

getDefaults(() => {
    getRecordingDevices(() => {
        restart();
        app.listen(C_Port, () => {
            console.log(`Listening on port ${C_Port}\nServing UI from ${guiPath}`);
        });
    });
});
