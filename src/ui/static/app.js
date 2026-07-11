(() => {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  const history = document.getElementById('chat-history');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const pending = document.getElementById('pending-actions');
  const toolCalls = document.getElementById('tool-calls');
  const audit = document.getElementById('audit-log');
  const status = document.getElementById('system-status');
  const agentBadge = document.getElementById('agent-badge');
  const agentPills = document.querySelectorAll('.agent-pill');

  function addMsg(role, text, agent, tools) {
    const el = document.createElement('div');
    el.className = `msg ${role}`;
    let html = '';
    if (agent) html += `<div class="agent-tag">Agent: ${agent}</div>`;
    html += `<div>${text}</div>`;
    html += `<div class="meta">${new Date().toLocaleTimeString()}</div>`;
    if (tools && tools.length) {
      html += `<div class="tool-tag">Tools: ${tools.join(', ')}</div>`;
    }
    el.innerHTML = html;
    history.appendChild(el);
    history.scrollTop = history.scrollHeight;
  }

  function addToolCall(tool, server, status) {
    const li = document.createElement('li');
    li.textContent = `${tool} (${server}) — ${status}`;
    toolCalls.prepend(li);
  }

  function addAudit(item) {
    const li = document.createElement('li');
    li.textContent = `${new Date(item.created_at || Date.now()).toLocaleTimeString()} — ${item.agent || 'system'} ${item.action || ''}`;
    audit.prepend(li);
  }

  function setActiveAgent(name) {
    agentPills.forEach(p => p.classList.toggle('active', p.dataset.agent === name));
    if (name) agentBadge.textContent = name;
  }

  ws.onopen = () => {
    addMsg('assistant', 'Connected to JARVIS. All systems online.', 'system', []);
    setActiveAgent('system');
  };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === 'response') {
      addMsg('assistant', msg.text, msg.agent || 'assistant', msg.tools || []);
      setActiveAgent(msg.agent || '');
    } else if (msg.type === 'error') {
      addMsg('assistant', 'Error: ' + msg.error, 'system', []);
    } else if (msg.type === 'tool_call') {
      addToolCall(msg.tool, msg.server, msg.status || 'called');
    }
  };

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addMsg('user', text, 'user', []);
    ws.send(JSON.stringify({ type: 'chat', text }));
    input.value = '';
  });

  pending.addEventListener('click', (e) => {
    if (e.target.classList.contains('approve') || e.target.classList.contains('reject')) {
      const idx = parseInt(e.target.dataset.idx, 10);
      const items = JSON.parse(localStorage.getItem('pending_actions') || '[]');
      items.splice(idx, 1);
      localStorage.setItem('pending_actions', JSON.stringify(items));
      ws.send(JSON.stringify({ type: 'approve_action', idx }));
      renderPending();
    }
  });

  async function loadStatus() {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      status.textContent = JSON.stringify(data, null, 2);
    } catch {
      status.textContent = 'unreachable';
    }
  }

  loadStatus();
  setInterval(loadStatus, 5000);
  renderPending();
})();
