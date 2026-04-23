import fs from 'fs';
import { execSync } from 'child_process';

const stateFile = '/Users/apple/.openclaw/workspace/memory/ops/state.json';
let state = { providerHealth: { lastCheckedAt: null, status: 'unknown', dead: [], recovered: [], lastErrors: {} } };

try {
  if (fs.existsSync(stateFile)) {
    const data = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    if (data.providerHealth) state.providerHealth = data.providerHealth;
  }
} catch (e) {
  console.error("Error reading state file:", e);
}

const models = [
  { id: 'mynewapi/claude-sonnet-4-6', name: 'mynewapi' },
  { id: 'xjrouter/claude-opus-4-6-max', name: 'xjrouter' }
];

const results = {};
const now = new Date().toISOString();

for (const m of models) {
  try {
    execSync(`openclaw generate "hi" --model ${m.id} --max-tokens 1`, { timeout: 15000, stdio: 'pipe' });
    results[m.id] = { ok: true };
  } catch (err) {
    results[m.id] = { ok: false, error: err.message.slice(0, 100) };
  }
}

const prevDead = state.providerHealth.dead || [];
const newDead = [];
const recovered = [];
const lastErrors = { ...state.providerHealth.lastErrors };

for (const m of models) {
  if (results[m.id].ok) {
    if (prevDead.includes(m.id)) recovered.push(m.id);
    delete lastErrors[m.id];
  } else {
    newDead.push(m.id);
    lastErrors[m.id] = results[m.id].error;
  }
}

state.providerHealth = {
  lastCheckedAt: now,
  status: newDead.length === 0 ? 'healthy' : (newDead.length === models.length ? 'down' : 'degraded'),
  dead: newDead,
  recovered: recovered,
  lastErrors: lastErrors
};

// Ensure directory exists
fs.mkdirSync('/Users/apple/.openclaw/workspace/memory/ops', { recursive: true });
fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));

console.log(JSON.stringify({ recovered, newDead, status: state.providerHealth.status }));
