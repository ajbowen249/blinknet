import * as axios from 'axios';

const C_BaseApi = `${window.location.origin}/api`;

export async function restart(config, serverConfig) {
    return await axios.default.post(`${C_BaseApi}/restart`, { config, server_config: serverConfig });
}

export async function resetToDefaults() {
    return await axios.default.post(`${C_BaseApi}/reset`);
}

export async function getState() {
    const response = await axios.default.get(`${C_BaseApi}/state`);
    return response.data;
}
