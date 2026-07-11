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
  const micBtn = document.getElementById('mic-btn');
  const ttsBtn = document.getElementById('tts-btn');
  const clearBtn = document.getElementById('clear-btn');

  let ttsEnabled = false;
  let isRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];

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
    if (role === 'assistant' && ttsEnabled && text) {
      speak(text);
    }
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

  function speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1;
    utter.pitch = 1;
    window.speechSynthesis.speak(utter);
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };
      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', blob, 'audio.webm');
        addMsg('assistant', 'Listening...', 'system', []);
        try {
          const res = await fetch('/api/speech/transcribe', {
            method: 'POST',
            body: blob,
            headers: { 'Content-Type': 'audio/webm' },
          });
          const data = await res.json();
          if (data.text && data.text.trim()) {
            addMsg('user', data.text, 'user', []);
            ws.send(JSON.stringify({ type: 'chat', text: data.text }));
          }
        } catch (exc) {
          addMsg('assistant', 'STT failed: ' + exc.message, 'system', []);
        }
        stream.getTracks().forEach(t => t.stop());
      };
      mediaRecorder.start();
      isRecording = true;
      micBtn.classList.add('recording');
    } catch (exc) {
      addMsg('assistant', 'Microphone access denied: ' + exc.message, 'system', []);
    }
  }

  function stopRecording() {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      isRecording = false;
      micBtn.classList.remove('recording');
    }
  }

  micBtn.addEventListener('mousedown', () => startRecording());
  micBtn.addEventListener('mouseup', () => stopRecording());
  micBtn.addEventListener('mouseleave', () => { if (isRecording) stopRecording(); });
  micBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startRecording(); });
  micBtn.addEventListener('touchend', (e) => { e.preventDefault(); stopRecording(); });

  ttsBtn.addEventListener('click', () => {
    ttsEnabled = !ttsEnabled;
    ttsBtn.classList.toggle('active', ttsEnabled);
    if (!ttsEnabled) window.speechSynthesis.cancel();
  });

  clearBtn.addEventListener('click', () => {
    history.innerHTML = '';
    toolCalls.innerHTML = '';
    audit.innerHTML = '';
    pending.innerHTML = '';
    addMsg('assistant', 'Chat cleared. Ready.', 'system', []);
  });

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
