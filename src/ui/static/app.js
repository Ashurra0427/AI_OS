(() => {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  const history = document.getElementById('chat-history');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const pending = document.getElementById('pending-actions');
  const audit = document.getElementById('audit-log');
  const status = document.getElementById('system-status');

  function addMsg(role, text) {
    const el = document.createElement('div');
    el.className = `msg ${role}`;
    el.innerHTML = `<div>${text}</div><div class="meta">${new Date().toLocaleTimeString()}</div>`;
    history.appendChild(el);
    history.scrollTop = history.scrollHeight;
  }

  function addAudit(item) {
    const li = document.createElement('li');
    li.textContent = `${new Date(item.created_at || Date.now()).toLocaleTimeString()} — ${item.agent || 'system'} ${item.action || ''}`;
    audit.prepend(li);
  }

  function renderPending() {
    pending.innerHTML = '';
    const items = JSON.parse(localStorage.getItem('pending_actions') || '[]');
    items.forEach((it, idx) => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${it.agent}</strong>: ${it.action}<br><button data-idx="${idx}" class="approve">Approve</button> <button data-idx="${idx}" class="reject">Reject</button>`;
      pending.appendChild(li);
    });
  }

  ws.onopen = () => addMsg('assistant', 'Connected to JARVIS.');
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === 'response') addMsg('assistant', msg.text);
    else if (msg.type === 'error') addMsg('assistant', 'Error: ' + msg.error);
  };

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addMsg('user', text);
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
