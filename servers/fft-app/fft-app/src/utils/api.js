import * as axios from 'axios';

const C_BaseApi = `${window.location.origin}/api`;

export async function restart() {
    return await axios.default.post(`${C_BaseApi}/restart`);
}

export async function getState() {
    const response = await axios.default.get(`${C_BaseApi}/state`);
    return response.data;
}
