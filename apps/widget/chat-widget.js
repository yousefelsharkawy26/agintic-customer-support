(function (global) {
  'use strict';

  var SCRIPT = document.currentScript;
  var TENANT_ID = SCRIPT.getAttribute('data-tenant-id');
  var API_BASE = SCRIPT.getAttribute('data-api-base') || '/api/v1/widget';
  var VISITOR_ID =
    SCRIPT.getAttribute('data-visitor-id') ||
    'anon-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8);

  var CONFIG = {
    apiBase: API_BASE,
    tenantId: TENANT_ID,
    visitorId: VISITOR_ID,
    primaryColor: '#2563eb',
    position: 'bottom-right',
    title: 'Support',
    greeting: 'Hi! How can I help you today?',
    locale: 'en',
    brandLogoUrl: null,
    customCss: null,
    showBranding: true,
    sessionId: null,
  };

  var I18N = {
    en: {
      placeholder: 'Type a message...',
      send: 'Send',
      typing: '...',
      error: 'Connection error. Please try again.',
      greeting: 'Hi! How can I help you today?',
    },
    es: {
      placeholder: 'Escribe un mensaje...',
      send: 'Enviar',
      typing: '...',
      error: 'Error de conexión. Intente de nuevo.',
      greeting: '¡Hola! ¿Cómo puedo ayudarte hoy?',
    },
    fr: {
      placeholder: 'Écrivez un message...',
      send: 'Envoyer',
      typing: '...',
      error: 'Erreur de connexion. Réessayez.',
      greeting: 'Bonjour ! Comment puis-je vous aider ?',
    },
    de: {
      placeholder: 'Nachricht schreiben...',
      send: 'Senden',
      typing: '...',
      error: 'Verbindungsfehler. Bitte versuchen Sie es erneut.',
      greeting: 'Hallo! Wie kann ich Ihnen helfen?',
    },
  };

  function t(key) {
    return (I18N[CONFIG.locale] || I18N.en)[key] || key;
  }

  function trackEvent(eventType, metadata) {
    if (!CONFIG.sessionId) return;
    fetch(CONFIG.apiBase + '/analytics/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tenant_id: CONFIG.tenantId,
        session_id: CONFIG.sessionId,
        visitor_id: CONFIG.visitorId,
        event_type: eventType,
        metadata: metadata || null,
      }),
    }).catch(function () {});
  }

  function injectStyles(css) {
    var el = document.createElement('style');
    el.textContent = css;
    document.head.appendChild(el);
  }

  function positionStyles() {
    var p = CONFIG.position === 'bottom-left' ? 'left:20px;' : 'right:20px;';
    return (
      '#cs-widget-container{' +
      p +
      'bottom:20px;position:fixed;z-index:999999;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}'
    );
  }

  function buildStyles() {
    var pc = CONFIG.primaryColor;
    var custom = CONFIG.customCss || '';
    return (
      positionStyles() +
      `
#cs-widget-toggle { width:56px; height:56px; border-radius:28px; background:${pc}; color:#fff; border:none; cursor:pointer; font-size:24px; box-shadow:0 4px 12px rgba(0,0,0,0.15); transition:transform 0.2s; }
#cs-widget-toggle:hover { transform:scale(1.1); }
#cs-widget-panel { display:none; width:380px; height:560px; background:#fff; border-radius:12px; box-shadow:0 8px 32px rgba(0,0,0,0.12); flex-direction:column; overflow:hidden; position:absolute; bottom:76px; ${
        CONFIG.position === 'bottom-left' ? 'left:0' : 'right:0'
      }; }
#cs-widget-header { padding:16px; background:${pc}; color:#fff; font-weight:600; display:flex; justify-content:space-between; align-items:center; }
#cs-widget-header-logo { width:24px; height:24px; border-radius:50%; margin-right:8px; vertical-align:middle; object-fit:cover; }
#cs-widget-close { background:none; border:none; color:#fff; cursor:pointer; font-size:20px; }
#cs-widget-messages { flex:1; overflow-y:auto; padding:12px; display:flex; flex-direction:column; gap:8px; }
.cs-msg { max-width:80%; padding:10px 14px; border-radius:12px; font-size:14px; line-height:1.4; white-space:pre-wrap; }
.cs-msg.user { align-self:flex-end; background:${pc}; color:#fff; border-bottom-right-radius:4px; }
.cs-msg.assistant { align-self:flex-start; background:#f1f5f9; color:#1e293b; border-bottom-left-radius:4px; }
.cs-msg.typing { align-self:flex-start; background:#f1f5f9; color:#94a3b8; border-bottom-left-radius:4px; }
.cs-msg .cs-citations { font-size:12px; color:#64748b; margin-top:4px; }
#cs-widget-input { display:flex; padding:12px; border-top:1px solid #e2e8f0; gap:8px; align-items:center; }
#cs-widget-input input { flex:1; padding:8px 12px; border:1px solid #e2e8f0; border-radius:8px; outline:none; font-size:14px; }
#cs-widget-input input:focus { border-color:${pc}; }
#cs-widget-send { padding:8px 16px; background:${pc}; color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:14px; }
#cs-widget-send:disabled { opacity:0.5; cursor:not-allowed; }
.cs-branding { text-align:center; font-size:11px; color:#94a3b8; padding:4px 0; border-top:1px solid #e2e8f0; }
.cs-branding a { color:${pc}; text-decoration:none; }
.cs-satisfaction { display:flex; gap:8px; justify-content:center; padding:8px 0; border-top:1px solid #e2e8f0; }
.cs-satisfaction button { background:none; border:1px solid #e2e8f0; border-radius:50%; width:36px; height:36px; cursor:pointer; font-size:18px; transition:transform 0.15s; }
.cs-satisfaction button:hover { transform:scale(1.2); border-color:${pc}; }
` +
      custom
    );
  }

  function init() {
    if (!CONFIG.tenantId) {
      console.warn('Customer Support Widget: missing data-tenant-id attribute');
      return;
    }

    injectStyles(buildStyles());

    var container = document.createElement('div');
    container.id = 'cs-widget-container';
    container.innerHTML =
      '<div id="cs-widget-panel">' +
      '<div id="cs-widget-header">' +
      (CONFIG.brandLogoUrl
        ? '<img id="cs-widget-header-logo" src="' + CONFIG.brandLogoUrl + '" alt="" />'
        : '') +
      '<span id="cs-widget-title">' +
      CONFIG.title +
      '</span>' +
      '<button id="cs-widget-close">&times;</button>' +
      '</div>' +
      '<div id="cs-widget-messages">' +
      '<div class="cs-msg assistant">' +
      t('greeting') +
      '</div>' +
      '</div>' +
      '<div id="cs-widget-input">' +
      '<input type="text" id="cs-widget-input-field" placeholder="' +
      t('placeholder') +
      '" />' +
      '<button id="cs-widget-send">' +
      t('send') +
      '</button>' +
      '</div>' +
      (CONFIG.showBranding
        ? '<div class="cs-branding">Powered by <a href="https://opencode.ai" target="_blank">Customer Support AI</a></div>'
        : '') +
      '</div>' +
      '<button id="cs-widget-toggle">&#x1f4ac;</button>';
    document.body.appendChild(container);

    var toggle = document.getElementById('cs-widget-toggle');
    var panel = document.getElementById('cs-widget-panel');
    var closeBtn = document.getElementById('cs-widget-close');
    var messagesEl = document.getElementById('cs-widget-messages');
    var input = document.getElementById('cs-widget-input-field');
    var sendBtn = document.getElementById('cs-widget-send');
    var isOpen = false;
    var conversationId = null;
    var satisfactionBar = null;

    function startSession() {
      fetch(CONFIG.apiBase + '/sessions/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: CONFIG.tenantId,
          visitor_id: CONFIG.visitorId,
          locale: CONFIG.locale,
        }),
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          CONFIG.sessionId = data.session_id;
          trackEvent('session_started', { resumed: data.resumed });
          if (data.resumed) {
            fetchOfflineMessages();
          }
        })
        .catch(function () {});
    }

    function fetchOfflineMessages() {
      fetch(CONFIG.apiBase + '/messages/offline/' + CONFIG.tenantId + '/' + CONFIG.visitorId)
        .then(function (r) {
          return r.json();
        })
        .then(function (msgs) {
          msgs.forEach(function (m) {
            addMessage('assistant', m.content);
          });
        })
        .catch(function () {});
    }

    function togglePanel() {
      isOpen = !isOpen;
      panel.style.display = isOpen ? 'flex' : 'none';
      toggle.style.display = isOpen ? 'none' : 'block';
      if (isOpen) {
        input.focus();
        trackEvent('widget_opened', {});
        if (!CONFIG.sessionId) startSession();
      } else {
        trackEvent('widget_closed', {});
      }
    }

    toggle.onclick = togglePanel;
    closeBtn.onclick = togglePanel;

    function addMessage(role, content) {
      var el = document.createElement('div');
      el.className = 'cs-msg ' + role;
      el.textContent = content;
      messagesEl.appendChild(el);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return el;
    }

    function showSatisfaction() {
      if (satisfactionBar) return;
      satisfactionBar = document.createElement('div');
      satisfactionBar.className = 'cs-satisfaction';
      satisfactionBar.innerHTML =
        '<button data-score="1" title="Very dissatisfied">&#x1f620;</button>' +
        '<button data-score="2" title="Dissatisfied">&#x1f61e;</button>' +
        '<button data-score="3" title="Neutral">&#x1f610;</button>' +
        '<button data-score="4" title="Satisfied">&#x1f60a;</button>' +
        '<button data-score="5" title="Very satisfied">&#x1f929;</button>';
      messagesEl.appendChild(satisfactionBar);
      satisfactionBar.querySelectorAll('button').forEach(function (btn) {
        btn.onclick = function () {
          var score = parseInt(btn.getAttribute('data-score'), 10);
          trackEvent('satisfaction_rating', { score: score });
          satisfactionBar.innerHTML =
            '<div style="text-align:center;color:#64748b;font-size:13px;padding:4px;">Thanks for your feedback!</div>';
        };
      });
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function sendMessage() {
      var text = input.value.trim();
      if (!text) return;
      input.value = '';
      sendBtn.disabled = true;

      addMessage('user', text);
      trackEvent('message_sent', { length: text.length });

      var typingEl = addMessage('assistant', '...');
      typingEl.classList.add('typing');

      var apiUrl = CONFIG.apiBase.replace('/widget', '/chat');

      var body = JSON.stringify({ message: text, stream: true });
      if (conversationId)
        body = JSON.stringify({ message: text, stream: true, conversation_id: conversationId });

      fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Request failed');
          conversationId = res.headers.get('X-Conversation-ID') || conversationId;

          typingEl.classList.remove('typing');
          typingEl.textContent = '';
          trackEvent('message_received', {});

          var reader = res.body.getReader();
          var decoder = new TextDecoder();
          var buffer = '';

          function read() {
            reader
              .read()
              .then(function (result) {
                if (result.done) {
                  showSatisfaction();
                  sendBtn.disabled = false;
                  input.focus();
                  return;
                }
                buffer += decoder.decode(result.value, { stream: true });
                var lines = buffer.split('\n');
                buffer = lines.pop() || '';
                for (var i = 0; i < lines.length; i++) {
                  var line = lines[i];
                  if (!line.startsWith('data: ')) continue;
                  try {
                    var data = JSON.parse(line.slice(6));
                    if (data.type === 'token') {
                      typingEl.textContent += data.content;
                    } else if (data.type === 'citations') {
                      var citeEl = document.createElement('div');
                      citeEl.className = 'cs-citations';
                      citeEl.textContent = 'Sources: ' + (data.citations || []).join(', ');
                      messagesEl.appendChild(citeEl);
                    } else if (data.type === 'done') {
                      conversationId = data.conversation_id || conversationId;
                    } else if (data.type === 'error') {
                      typingEl.textContent = 'Error: ' + data.content;
                      typingEl.style.color = '#dc2626';
                    }
                  } catch (e) {}
                }
                messagesEl.scrollTop = messagesEl.scrollHeight;
                read();
              })
              .catch(function () {
                typingEl.textContent = t('error');
                typingEl.style.color = '#dc2626';
                sendBtn.disabled = false;
              });
          }
          read();
        })
        .catch(function () {
          typingEl.textContent = t('error');
          typingEl.style.color = '#dc2626';
          sendBtn.disabled = false;
        });
    }

    sendBtn.onclick = sendMessage;
    input.onkeydown = function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
      }
    };

    trackEvent('widget_loaded', {});
  }

  // Fetch settings from API, then initialize
  if (TENANT_ID) {
    fetch(API_BASE + '/settings/' + TENANT_ID)
      .then(function (r) {
        return r.json();
      })
      .then(function (settings) {
        for (var key in settings) {
          if (settings.hasOwnProperty(key) && CONFIG.hasOwnProperty(key)) {
            CONFIG[key] = settings[key];
          }
        }
        init();
      })
      .catch(function () {
        init();
      });
  }
})(window);
