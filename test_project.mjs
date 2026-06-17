import fs from 'fs';

// Mock DOM
global.window = { location: { pathname: '/project/30' } };
global.document = {
    getElementById: (id) => ({ textContent: '', value: '', addEventListener: () => {}, cloneNode: function() { return this; }, replaceWith: () => {}, classList: { toggle: () => {}, remove: () => {}, add: () => {} }, style: {} }),
    addEventListener: () => {},
    querySelectorAll: () => [],
    querySelector: () => ({ dataset: { view: 'agents' } }),
    title: ''
};
global.localStorage = { getItem: () => 'token', removeItem: () => {} };
global.API_BASE_URL = 'http://localhost:8000';

// Mock fetch
global.fetch = async (url) => {
    console.log("FETCH:", url);
    return { ok: true, json: async () => ({ project: { name: 'Test' }, agents: [] }), status: 200 };
};

try {
    const code = fs.readFileSync('./frontend/project.js', 'utf-8');
    eval(code);
    console.log("Parsed and executed top level successfully.");
} catch (e) {
    console.error("RUNTIME ERROR:", e);
}
