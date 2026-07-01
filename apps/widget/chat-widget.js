(function () {
  'use strict';

  let CONFIG = {
    apiUrl: '/api/v1/chat',
    primaryColor: '#2563eb',
    title: 'Support',
    position: 'bottom-right',
    locale: 'en',
    i18n: {
      placeholder: 'Type a message...',
      send: 'Send',
      fileUpload: 'Attach file',
      typing: '...',
      error: 'Connection error. Please try again.',
      errorGeneric: 'An error occurred.',
      sources: 'Sources',
    },
  };

  const I18N = {
    en: {
      placeholder: 'Type a message...',
      send: 'Send',
      fileUpload: 'Attach file',
      typing: '...',
      error: 'Connection error. Please try again.',
      errorGeneric: 'An error occurred.',
      sources: 'Sources',
    },
    es: {
      placeholder: 'Escribe un mensaje...',
      send: 'Enviar',
      fileUpload: 'Adjuntar archivo',
      typing: '...',
      error: 'Error de conexión. Intente de nuevo.',
      errorGeneric: 'Ocurrió un error.',
      sources: 'Fuentes',
    },
    fr: {
      placeholder: 'Écrivez un message...',
      send: 'Envoyer',
      fileUpload: 'Joindre un fichier',
      typing: '...',
      error: 'Erreur de connexion. Réessayez.',
      errorGeneric: 'Une erreur est survenue.',
      sources: 'Sources',
    },
    de: {
      placeholder: 'Nachricht schreiben...',
      send: 'Senden',
      fileUpload: 'Datei anhängen',
      typing: '...',
      error: 'Verbindungsfehler. Bitte versuchen Sie es erneut.',
      errorGeneric: 'Ein Fehler ist aufgetreten.',
      sources: 'Quellen',
    },
  };

  function t(key) {
    return (I18N[CONFIG.locale] || I18N.en)[key] || CONFIG.i18n[key] || key;
  }

  let styles = `
#cs-widget-container { position:fixed; bottom:20px; right:20px; z-index:999999; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
#cs-widget-toggle { width:56px; height:56px; border-radius:28px; background:${CONFIG.primaryColor}; color:#fff; border:none; cursor:pointer; font-size:24px; box-shadow:0 4px 12px rgba(0,0,0,0.15); transition:transform 0.2s; }
#cs-widget-toggle:hover { transform:scale(1.1); }
#cs-widget-panel { display:none; width:380px; height:560px; background:#fff; border-radius:12px; box-shadow:0 8px 32px rgba(0,0,0,0.12); flex-direction:column; overflow:hidden; }
#cs-widget-header { padding:16px; background:${CONFIG.primaryColor}; color:#fff; font-weight:600; display:flex; justify-content:space-between; align-items:center; }
#cs-widget-close { background:none; border:none; color:#fff; cursor:pointer; font-size:20px; }
#cs-widget-messages { flex:1; overflow-y:auto; padding:12px; display:flex; flex-direction:column; gap:8px; }
.cs-msg { max-width:80%; padding:10px 14px; border-radius:12px; font-size:14px; line-height:1.4; white-space:pre-wrap; }
.cs-msg.user { align-self:flex-end; background:${CONFIG.primaryColor}; color:#fff; border-bottom-right-radius:4px; }
.cs-msg.assistant { align-self:flex-start; background:#f1f5f9; color:#1e293b; border-bottom-left-radius:4px; }
.cs-msg.typing { align-self:flex-start; background:#f1f5f9; color:#94a3b8; border-bottom-left-radius:4px; }
.cs-msg .cs-citations { font-size:12px; color:#64748b; margin-top:4px; }
.cs-card { border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin:4px 0; background:#fff; }
.cs-card p { margin:0 0 8px; font-size:14px; }
.cs-card-btn { display:block; width:100%; padding:8px; margin:4px 0; border:1px solid ${CONFIG.primaryColor}; border-radius:6px; background:#fff; color:${CONFIG.primaryColor}; cursor:pointer; font-size:13px; text-align:center; }
.cs-card-btn:hover { background:${CONFIG.primaryColor}; color:#fff; }
.cs-file-upload { display:inline-block; }
.cs-file-upload label { display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:50%; cursor:pointer; color:#64748b; font-size:18px; transition:background 0.2s; }
.cs-file-upload label:hover { background:#f1f5f9; }
.cs-file-name { font-size:12px; color:#64748b; padding:8px; background:#f8fafc; border-radius:6px; margin:4px 0; display:flex; align-items:center; gap:4px; }
#cs-widget-input { display:flex; padding:12px; border-top:1px solid #e2e8f0; gap:8px; align-items:center; }
#cs-widget-input input { flex:1; padding:8px 12px; border:1px solid #e2e8f0; border-radius:8px; outline:none; font-size:14px; }
#cs-widget-input input:focus { border-color:${CONFIG.primaryColor}; }
#cs-widget-send { padding:8px 16px; background:${CONFIG.primaryColor}; color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:14px; }
#cs-widget-send:disabled { opacity:0.5; cursor:not-allowed; }
`;

  let styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);

  let container = document.createElement('div');
  container.id = 'cs-widget-container';
  container.innerHTML = `
    <div id="cs-widget-panel">
      <div id="cs-widget-header">
        <span>${CONFIG.title}</span>
        <button id="cs-widget-close">&times;</button>
      </div>
      <div id="cs-widget-messages"></div>
      <div id="cs-widget-input">
        <div class="cs-file-upload">
          <label for="cs-file-input" title="${t('fileUpload')}">&#x1f4ce;</label>
          <input type="file" id="cs-file-input" style="display:none" />
        </div>
        <input type="text" id="cs-widget-input-field" placeholder="${t('placeholder')}" />
        <button id="cs-widget-send">${t('send')}</button>
      </div>
    </div>
    <button id="cs-widget-toggle">&#x1f4ac;</button>
  `;
  document.body.appendChild(container);

  let toggle = document.getElementById('cs-widget-toggle');
  let panel = document.getElementById('cs-widget-panel');
  let close = document.getElementById('cs-widget-close');
  let messagesEl = document.getElementById('cs-widget-messages');
  let input = document.getElementById('cs-widget-input-field');
  let sendBtn = document.getElementById('cs-widget-send');
  let fileInput = document.getElementById('cs-file-input');
  let uploadedFiles = [];
  let isOpen = false;
  let conversationId = null;

  function togglePanel() {
    isOpen = !isOpen;
    panel.style.display = isOpen ? 'flex' : 'none';
    toggle.style.display = isOpen ? 'none' : 'block';
    if (isOpen) input.focus();
  }

  toggle.onclick = togglePanel;
  close.onclick = togglePanel;

  function addMessage(role, content) {
    let el = document.createElement('div');
    el.className = 'cs-msg ' + role;
    el.textContent = content;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return el;
  }

  function addCard(data) {
    let el = document.createElement('div');
    el.className = 'cs-card';
    let p = document.createElement('p');
    p.textContent = data.text || '';
    el.appendChild(p);
    if (data.buttons) {
      for (let btn of data.buttons) {
        let b = document.createElement('button');
        b.className = 'cs-card-btn';
        b.textContent = btn.label || btn.text || '';
        b.onclick = function () {
          input.value = btn.value || btn.label || '';
          sendMessage();
        };
        el.appendChild(b);
      }
    }
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return el;
  }

  function showFileInfo(files) {
    let existing = document.querySelector('.cs-file-name');
    if (existing) existing.remove();
    if (!files || files.length === 0) return;
    let el = document.createElement('div');
    el.className = 'cs-file-name';
    el.textContent =
      '\u{1f4ce} ' +
      files
        .map(function (f) {
          return f.name;
        })
        .join(', ');
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  fileInput.onchange = function () {
    uploadedFiles = Array.from(fileInput.files);
    showFileInfo(uploadedFiles);
    fileInput.value = '';
  };

  async function sendMessage() {
    let text = input.value.trim();
    if (!text && uploadedFiles.length === 0) return;
    input.value = '';
    sendBtn.disabled = true;

    if (text) addMessage('user', text);

    let typingEl = addMessage('assistant', '...');
    typingEl.classList.add('typing');

    try {
      let body = { message: text || '(file upload)', stream: true };
      if (conversationId) body.conversation_id = conversationId;

      let res = await fetch(CONFIG.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error('Request failed');

      conversationId = res.headers.get('X-Conversation-ID') || conversationId;

      typingEl.classList.remove('typing');
      typingEl.textContent = '';

      let reader = res.body.getReader();
      let decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        let { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (let line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            let data = JSON.parse(line.slice(6));
            if (data.type === 'token') {
              typingEl.textContent += data.content;
              messagesEl.scrollTop = messagesEl.scrollHeight;
            } else if (data.type === 'card') {
              typingEl.remove();
              addCard(data);
            } else if (data.type === 'citations') {
              let citeEl = document.createElement('div');
              citeEl.className = 'cs-citations';
              citeEl.textContent = t('sources') + ': ' + (data.citations || []).join(', ');
              messagesEl.appendChild(citeEl);
            } else if (data.type === 'done') {
              conversationId = data.conversation_id || conversationId;
            } else if (data.type === 'error') {
              typingEl.textContent = 'Error: ' + data.content;
              typingEl.style.color = '#dc2626';
            }
          } catch (e) {
            /* skip parse errors */
          }
        }
      }
    } catch (err) {
      typingEl.classList.remove('typing');
      typingEl.textContent = t('error');
      typingEl.style.color = '#dc2626';
    }
    uploadedFiles = [];
    let fileInfo = document.querySelector('.cs-file-name');
    if (fileInfo) fileInfo.remove();
    sendBtn.disabled = false;
    input.focus();
  }

  sendBtn.onclick = sendMessage;
  input.onkeydown = function (e) {
    if (e.key === 'Enter') sendMessage();
  };
})();
