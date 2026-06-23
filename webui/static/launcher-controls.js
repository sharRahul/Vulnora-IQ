(() => {
  const TOKEN_STORAGE_KEY = 'vulnoraiq.token';
  const qs = (selector) => document.querySelector(selector);

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function bootstrapTokenFromUrl() {
    const url = new URL(window.location.href);
    const token = url.searchParams.get('token');
    if (!token) return;
    try {
      sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch (error) {
      /* Ignore storage failures; normal sign-in still works. */
    }
    url.searchParams.delete('token');
    if (url.searchParams.get('launcher') === '1') url.searchParams.delete('launcher');
    window.history.replaceState({}, document.title, `${url.pathname}${url.search}${url.hash}`);
  }

  function authHeaders(extra = {}) {
    const headers = { ...extra };
    try {
      const token = sessionStorage.getItem(TOKEN_STORAGE_KEY) || '';
      if (token) headers['X-VulnoraIQ-Token'] = token;
    } catch (error) {
      /* No persisted token available. */
    }
    return headers;
  }

  function setStartupState(status, title, message) {
    const badge = qs('#startup-status-badge');
    qs('#startup-status-title').textContent = title;
    qs('#startup-status-message').textContent = message;
    badge.textContent = status.replaceAll('_', ' ');
    badge.className = `startup-badge ${status}`;
  }

  function removeQuickStartColumn() {
    const actionList = qs('#startup-action-list');
    if (actionList) actionList.closest('section')?.remove();
  }

  function injectLicenseBadge() {
    if (qs('#license-badge')) return;
    const badge = document.createElement('a');
    badge.id = 'license-badge';
    badge.className = 'license-badge';
    badge.href = 'https://www.apache.org/licenses/LICENSE-2.0';
    badge.target = '_blank';
    badge.rel = 'noopener noreferrer';
    badge.setAttribute('aria-label', 'VulnoraIQ license: Licensed under the Apache License, Version 2.0');
    badge.textContent = 'Licensed under the Apache License, Version 2.0';
    Object.assign(badge.style, {
      position: 'fixed',
      left: '14px',
      bottom: '12px',
      zIndex: '50',
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      maxWidth: 'calc(100vw - 28px)',
      padding: '7px 10px',
      border: '1px solid color-mix(in srgb, var(--border-strong) 75%, transparent)',
      borderRadius: '999px',
      color: 'var(--muted)',
      background: 'color-mix(in srgb, var(--panel-strong) 88%, transparent)',
      boxShadow: '0 10px 28px rgba(0, 0, 0, 0.14)',
      backdropFilter: 'blur(12px)',
      fontSize: '0.72rem',
      fontWeight: '900',
      letterSpacing: '0.01em',
      lineHeight: '1',
      textDecoration: 'none',
      textTransform: 'none',
    });
    badge.addEventListener('mouseenter', () => {
      badge.style.color = 'var(--navy)';
      badge.style.borderColor = 'var(--accent)';
    });
    badge.addEventListener('mouseleave', () => {
      badge.style.color = 'var(--muted)';
      badge.style.borderColor = 'color-mix(in srgb, var(--border-strong) 75%, transparent)';
    });
    document.body.appendChild(badge);
  }

  function renderList(selector, items, emptyMessage) {
    const container = qs(selector);
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = `<div class="startup-item"><p>${escapeHtml(emptyMessage)}</p></div>`;
      return;
    }
    container.innerHTML = items.map((item) => `
      <article class="startup-item">
        <strong>
          ${escapeHtml(item.name || item.key || 'Check')}
          <span class="startup-pill ${escapeHtml(item.status || 'pending')}">${escapeHtml(item.status || 'pending')}</span>
        </strong>
        <p>${escapeHtml(item.detail || item.value || '')}</p>
      </article>
    `).join('');
  }

  function optionInput(option) {
    const key = escapeHtml(option.key || option.name || 'option');
    const inputType = escapeHtml(option.input_type || 'text');
    const value = escapeHtml(option.value ?? '');
    const disabled = option.editable === false ? 'disabled' : '';
    return `
      <label class="startup-config-field">
        <span>${escapeHtml(option.name || option.key || 'Option')}</span>
        <input data-startup-config-input="true" name="${key}" type="${inputType}" value="${value}" ${disabled}>
        <small>${escapeHtml(option.detail || '')}</small>
      </label>
    `;
  }

  function renderConfigForm(items, message = '') {
    const container = qs('#startup-config-list');
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<div class="startup-item"><p>No configuration options reported.</p></div>';
      return;
    }
    container.innerHTML = `
      <form id="startup-config-form" class="startup-config-form">
        ${items.map(optionInput).join('')}
        <div class="startup-config-actions">
          <button type="submit" class="secondary compact">Apply settings</button>
          <span id="startup-config-message" class="form-message">${escapeHtml(message)}</span>
        </div>
      </form>
    `;
    qs('#startup-config-form')?.addEventListener('submit', saveStartupSettings);
  }

  function renderStartupStatus(data, configMessage = '') {
    const status = data.status || 'warning';
    const title = status === 'ready' ? 'Ready for local assessment' : 'Startup checks need attention';
    const message = data.message || 'Review startup checks before running scans.';
    setStartupState(status, title, message);
    renderList('#startup-check-list', data.dependency_checks, 'No dependency checks reported.');
    renderConfigForm(data.configuration_options || data.change_options, configMessage);
    const stopButton = qs('#stop-server');
    stopButton.disabled = !data.shutdown_allowed;
    qs('#stop-server-message').textContent = data.shutdown_allowed
      ? 'Local launcher mode is active. Use this button to stop the server cleanly.'
      : 'Stop is unavailable unless the local launcher enabled it and your session has admin runtime permission.';
  }

  async function refreshStartupStatus() {
    setStartupState('pending', 'Checking startup state', 'Contacting the local Web UI launcher.');
    try {
      const response = await fetch('/api/startup', { headers: authHeaders() });
      if (response.status === 401) {
        setStartupState('blocked', 'Sign in required', 'Enter the access token or launch from the double-click startup file to view checks.');
        renderList('#startup-check-list', [], 'Sign in to see checks.');
        renderConfigForm([], 'Sign in to update settings.');
        qs('#stop-server').disabled = true;
        return;
      }
      if (response.status === 404) {
        setStartupState('unavailable', 'Standard server mode', 'Startup controls are available when the Web UI is opened through the local launcher.');
        renderList('#startup-check-list', [], 'This server was not started by the local launcher.');
        renderConfigForm([], 'Configuration editing is available in local launcher mode.');
        qs('#stop-server').disabled = true;
        return;
      }
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to load startup checks');
      renderStartupStatus(data);
    } catch (error) {
      setStartupState('blocked', 'Startup check failed', error.message || 'Unable to load startup checks.');
      qs('#stop-server').disabled = true;
    }
  }

  async function getCsrfToken() {
    const response = await fetch('/api/csrf-token', { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to request CSRF token');
    return data.csrf_token;
  }

  async function saveStartupSettings(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const submitButton = form.querySelector('button[type="submit"]');
    const message = qs('#startup-config-message');
    const payload = {};
    form.querySelectorAll('[data-startup-config-input]').forEach((input) => {
      if (!input.disabled) payload[input.name] = input.value;
    });
    submitButton.disabled = true;
    message.textContent = 'Applying settings...';
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch('/api/startup/settings', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }),
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to update settings');
      renderStartupStatus(data, data.settings_message || 'Settings updated.');
    } catch (error) {
      message.textContent = error.message || 'Unable to update settings.';
    } finally {
      submitButton.disabled = false;
    }
  }

  async function stopServer() {
    const message = qs('#stop-server-message');
    const confirmed = window.confirm('Stop the local VulnoraIQ Web UI server now? The browser page will disconnect.');
    if (!confirmed) return;
    qs('#stop-server').disabled = true;
    message.textContent = 'Stopping local server...';
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch('/api/server/shutdown', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }),
        body: JSON.stringify({ confirm: true }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to stop server');
      setStartupState('stopping', 'Server stopping', data.message || 'The local server is shutting down.');
      message.textContent = 'Server stop requested successfully. You can close this browser tab.';
    } catch (error) {
      message.textContent = error.message || 'Unable to stop server.';
      qs('#stop-server').disabled = false;
    }
  }

  bootstrapTokenFromUrl();

  document.addEventListener('DOMContentLoaded', () => {
    injectLicenseBadge();
    removeQuickStartColumn();
    const refreshButton = qs('#startup-refresh');
    const stopButton = qs('#stop-server');
    if (refreshButton) refreshButton.addEventListener('click', refreshStartupStatus);
    if (stopButton) stopButton.addEventListener('click', stopServer);
    refreshStartupStatus();
  });
})();
