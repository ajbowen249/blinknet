const express = require('express');
const path = require('path');
const child_process = require('child_process');

const C_Port = 3000;

const guiPath = path.join(__dirname, '../fft-app/dist');
const pyFFTPath = path.join(__dirname, '../../piFFT/pifft.py');

const app = express();

var pythonProcess = undefined;

function restart() {
    console.log('restart');
    if (pythonProcess) {
        pythonProcess.kill();
    }
    pythonProcess = child_process.spawn('python2', [ pyFFTPath ]);
}

app.use('/', express.static(guiPath));

app.post('/api/restart', (req, res) => {
    restart();
    res.send(true);
});

restart();

app.listen(C_Port, () => {
    console.log(`Listening on port ${C_Port}\nServing UI from ${guiPath}`);
});
