const express = require('express');
const path = require('path');
const child_process = require('child_process');
var bodyParser = require('body-parser');

const C_Port = 3000;

var defaultSettings = {};
var config = {};

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
        config = Object.assign({}, defaultSettings);
        done();
    });
}

function restart(newConfig) {
    if (pythonProcess) {
        pythonProcess.kill();
    }

    config = Object.assign(config, newConfig);

    pythonProcess = child_process.spawn('python2', [
        pyFFTPath,
        '--bus-index', config.bus_index,
        '--device', config.device,

        '--threshold', config.threshold,

        '--low-scaler', config.low_scaler,
        '--mid-scaler', config.mid_scaler,
        '--high-scaler', config.high_scaler,

        '--bass-cutoff', config.bass_cutoff,
        '--mid-start', config.mid_start,
        '--treble-start', config.treble_start,
    ]);
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
    restart(req.body.config);
    res.send(true);
});

app.get('/api/state', async (req, res) => {
    res.send(JSON.stringify({
        state: {
            recording_devices: recordingDevices,
            config: config,
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
