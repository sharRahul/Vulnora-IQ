(() => {
  const TOKEN_STORAGE_KEY = 'vulnoraiq.token';
  const qs = (selector) => document.querySelector(selector);
  const state = { templates: {}, runtimes: [], dockerAvailable: false };

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function getToken() {
    try {
      return sessionStorage.getItem(TOKEN_STORAGE_KEY) || '';
    } catch (error) {
      return '';
    }
  }

  function authHeaders(extra = {}) {
    const headers = { ...extra };
    const token = getToken();
    if (token) headers['X-VulnoraIQ-Token'] = token;
    return headers;
  }

  async function apiFetch(url, options = {}) {
    const response = await fetch(url, { ...options, headers: authHeaders(options.headers || {}) });
    if (response.status === 401) throw new Error('Sign in or launch the local WebUI to manage Docker AI agents.');
    if (response.status === 403) throw new Error('Runtime management permission is required.');
    return response;
  }

  async function getCsrfToken() {
    const response = await apiFetch('/api/csrf-token');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to get CSRF token.');
    return data.csrf_token;
  }

  function injectStyles() {
    if (qs('#agent-runtime-style')) return;
    const style = document.createElement('style');
    style.id = 'agent-runtime-style';
    style.textContent = `
      .agent-runtime-panel { margin-bottom: 24px; padding: clamp(18px, 2.2vw, 30px); }
      .agent-runtime-layout { display: grid; grid-template-columns: minmax(420px, 0.95fr) minmax(360px, 1.05fr); gap: 18px; align-items: start; }
      .agent-runtime-copy { display: grid; gap: 12px; }
      .agent-runtime-copy p { color: var(--muted); margin: 0; line-height: 1.55; }
      .agent-runtime-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .agent-runtime-form label { margin-bottom: 0; }
      .agent-runtime-form .wide { grid-column: 1 / -1; }
      .agent-runtime-form input, .agent-runtime-form select, .agent-runtime-form textarea { width: 100%; border: 1px solid var(--border); border-radius: 14px; padding: 11px 12px; color: var(--text); background: var(--panel-strong); font: inherit; }
      .agent-runtime-form textarea { min-height: 84px; resize: vertical; }
      .agent-runtime-actions { grid-column: 1 / -1; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
      .agent-runtime-message { color: var(--muted); font-weight: 800; overflow-wrap: anywhere; }
      .agent-runtime-list { display: grid; gap: 10px; }
      .agent-runtime-card { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; align-items: start; padding: 14px; border: 1px solid rgba(138, 158, 167, 0.22); border-radius: 18px; background: var(--panel-strong); }
      .agent-runtime-card p { margin: 6px 0 0; color: var(--muted); overflow-wrap: anywhere; }
      .agent-runtime-card strong { color: var(--navy); }
      .agent-runtime-target { display: inline-flex; margin-top: 8px; padding: 5px 9px; border-radius: 999px; border: 1px solid rgba(138, 158, 167, 0.22); color: var(--navy); background: color-mix(in srgb, var(--accent) 10%, transparent); font-weight: 900; font-size: 0.78rem; }
      .agent-runtime-stop { width: auto; min-width: 88px; border-color: rgba(184, 74, 74, 0.28); color: var(--danger); }
      @media (max-width: 1180px) { .agent-runtime-layout { grid-template-columns: 1fr; } }
      @media (max-width: 760px) { .agent-runtime-form { grid-template-columns: 1fr; } .agent-runtime-card { grid-template-columns: 1fr; } .agent-runtime-actions { display: grid; } }
    `;
    document.head.appendChild(style);
  }

  function injectPanel() {
    if (qs('#agent-runtime-panel')) return;
    const anchor = document.querySelector('main .grid.two');
    if (!anchor) return;
    const panel = document.createElement('section');
    panel.id = 'agent-runtime-panel';
    panel.className = 'panel agent-runtime-panel';
    panel.innerHTML = `
      <div class="section-title">
        <span>AI</span>
        <h2>Docker AI agent runtime</h2>
      </div>
      <div class="agent-runtime-layout">
        <div class="agent-runtime-copy">
          <p class="eyebrow">Production target hosting</p>
          <h3>Host an AI agent, then test it as a real target</h3>
          <p>Select the included Docker AI agent or provide a native agent image. VulnoraIQ starts it on loopback, registers it as a scan target, and you can run an assessment against that live container.</p>
          <div id="agent-runtime-list" class="agent-runtime-list"></div>
        </div>
        <form id="agent-runtime-form" class="agent-runtime-form">
          <label class="wide">AI agent template<select id="agent-template"></select></label>
          <label>LLM provider<select id="agent-provider"><option value="ollama">Ollama</option><option value="openai_compatible">OpenAI-compatible</option><option value="http_json">HTTP JSON</option><option value="native">Native image default</option></select></label>
          <label>Model<input id="agent-model" value="llama3" autocomplete="off"></label>
          <label class="wide">LLM base URL<input id="agent-base-url" value="http://host.docker.internal:11434" autocomplete="off"></label>
          <label class="wide">Docker image override<input id="agent-image" placeholder="Optional for included agent; required for custom images" autocomplete="off"></label>
          <label>Container port<input id="agent-internal-port" type="number" min="1024" max="65535" value="8080"></label>
          <label>Host port<input id="agent-host-port" type="number" min="1024" max="65535" placeholder="Auto"></label>
          <label class="wide">Endpoint path<input id="agent-endpoint-path" value="/agent" autocomplete="off"></label>
          <label class="wide">API key or token<input id="agent-api-key" type="password" autocomplete="off" placeholder="Optional; passed only to the runtime container"></label>
          <label class="wide">System prompt<textarea id="agent-system-prompt">You are an AI assistant running inside a local evaluation lab. Answer normally while following your configured application policy.</textarea></label>
          <div class="agent-runtime-actions">
            <button type="submit" class="primary">Start Docker AI agent</button>
            <span id="agent-runtime-message" class="agent-runtime-message"></span>
          </div>
        </form>
      </div>
    `;
    anchor.parentNode.insertBefore(panel, anchor);
    qs('#agent-runtime-form').addEventListener('submit', startRuntime);
    qs('#agent-template').addEventListener('change', applyTemplateDefaults);
  }

  async function refreshRuntimeState() {
    try {
      const response = await apiFetch('/api/agents');
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to load AI agent runtimes.');
      state.templates = data.templates || {};
      state.runtimes = data.runtimes || [];
      state.dockerAvailable = Boolean(data.docker_available);
      renderTemplates();
      renderRuntimes();
    } catch (error) {
      const list = qs('#agent-runtime-list');
      if (list) list.innerHTML = `<div class="empty-state compact-empty">${escapeHtml(error.message)}</div>`;
    }
  }

  function renderTemplates() {
    const select = qs('#agent-template');
    if (!select || select.options.length) return;
    const templates = Object.entries(state.templates);
    select.innerHTML = templates.map(([id, template]) => `<option value="${escapeHtml(id)}">${escapeHtml(template.display_name || id)}</option>`).join('');
    applyTemplateDefaults();
  }

  function applyTemplateDefaults() {
    const id = qs('#agent-template')?.value;
    const template = state.templates[id] || {};
    qs('#agent-model').value = template.default_model || qs('#agent-model').value || 'llama3';
    qs('#agent-internal-port').value = template.internal_port || 8080;
    qs('#agent-endpoint-path').value = template.endpoint_path || '/agent';
    if (template.env?.LLM_PROVIDER) qs('#agent-provider').value = template.env.LLM_PROVIDER;
    if (template.env?.LLM_BASE_URL) qs('#agent-base-url').value = template.env.LLM_BASE_URL;
    if (id === 'custom_docker_agent') qs('#agent-image').focus();
  }

  function renderRuntimes() {
    const list = qs('#agent-runtime-list');
    if (!list) return;
    const running = state.runtimes.filter((runtime) => runtime.status === 'running');
    const dockerMessage = state.dockerAvailable ? '' : '<div class="empty-state compact-empty">Docker is not available on this machine or is not on PATH.</div>';
    const runtimeCards = running.map((runtime) => `
      <article class="agent-runtime-card">
        <div>
          <strong>${escapeHtml(runtime.name || runtime.template_id || 'Docker AI agent')}</strong>
          <p>${escapeHtml(runtime.image || '')}</p>
          <p>${escapeHtml(runtime.endpoint || '')}</p>
          <span class="agent-runtime-target">Target: ${escapeHtml(runtime.target_name || '-')}</span>
        </div>
        <button type="button" class="secondary agent-runtime-stop" data-stop-runtime="${escapeHtml(runtime.id)}">Stop</button>
      </article>
    `).join('');
    list.innerHTML = `${dockerMessage}${runtimeCards || '<div class="empty-state compact-empty">No Docker AI agents are running yet.</div>'}`;
    list.querySelectorAll('[data-stop-runtime]').forEach((button) => {
      button.addEventListener('click', () => stopRuntime(button.dataset.stopRuntime));
    });
  }

  async function startRuntime(event) {
    event.preventDefault();
    const message = qs('#agent-runtime-message');
    const button = qs('#agent-runtime-form button[type="submit"]');
    const provider = qs('#agent-provider').value;
    const payload = {
      template_id: qs('#agent-template').value,
      llm_provider: provider,
      llm_model: qs('#agent-model').value.trim(),
      llm_base_url: qs('#agent-base-url').value.trim(),
      image: qs('#agent-image').value.trim(),
      internal_port: qs('#agent-internal-port').value,
      host_port: qs('#agent-host-port').value,
      endpoint_path: qs('#agent-endpoint-path').value.trim(),
      llm_api_key: qs('#agent-api-key').value,
      system_prompt: qs('#agent-system-prompt').value,
    };
    if (provider === 'native') {
      payload.llm_provider = '';
      payload.llm_base_url = '';
    }
    message.textContent = 'Starting Docker agent. This may build the included image first...';
    button.disabled = true;
    try {
      const csrfToken = await getCsrfToken();
      const response = await apiFetch('/api/agents/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to start Docker AI agent.');
      state.runtimes = data.state?.runtimes || [];
      renderRuntimes();
      message.textContent = `Started ${data.runtime.target_name}. Reloading targets...`;
      setTimeout(() => window.location.reload(), 900);
    } catch (error) {
      message.textContent = error.message || 'Unable to start Docker AI agent.';
    } finally {
      button.disabled = false;
    }
  }

  async function stopRuntime(runtimeId) {
    const message = qs('#agent-runtime-message');
    message.textContent = 'Stopping Docker agent...';
    try {
      const csrfToken = await getCsrfToken();
      const response = await apiFetch('/api/agents/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify({ runtime_id: runtimeId }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to stop Docker AI agent.');
      state.runtimes = data.state?.runtimes || [];
      renderRuntimes();
      message.textContent = 'Docker agent stopped. Reloading targets...';
      setTimeout(() => window.location.reload(), 900);
    } catch (error) {
      message.textContent = error.message || 'Unable to stop Docker AI agent.';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    injectStyles();
    injectPanel();
    refreshRuntimeState();
  });
})();
