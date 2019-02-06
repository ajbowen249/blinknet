const express = require('express');
const path = require('path');
const child_process = require('child_process');
var bodyParser = require('body-parser');

const C_Port = 3000;

const C_DefaultSettings = {
    microphone_input: 'plughw:CARD=Microphone,DEV=0',
    bus_index: 2,
};

var config = Object.assign({}, C_DefaultSettings);

const guiPath = path.join(__dirname, '../fft-app/dist');
const pyFFTPath = path.join(__dirname, '../../piFFT/pifft.py');

const app = express();

app.use(bodyParser.json());

var pythonProcess = undefined;

function restart(newConfig) {
    console.log('restart');
    if (pythonProcess) {
        pythonProcess.kill();
    }

    config = Object.assign(config, newConfig);

    pythonProcess = child_process.spawn('python2', [
        pyFFTPath,
        '--bus_index', config.bus_index,
        '--device', config.microphone_input,
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

getRecordingDevices(() => {
    restart();
    app.listen(C_Port, () => {
        console.log(`Listening on port ${C_Port}\nServing UI from ${guiPath}`);
    });
});
