import * as axios from 'axios';

const C_BaseApi = `${window.location.origin}/api`;

export function restart() {
    axios.default.post(`${C_BaseApi}/restart`);
}
