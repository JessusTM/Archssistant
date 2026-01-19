/**
 * Frontend de Arch-Assistant.
 *
 * Responsabilidades:
 * - Gestionar el input del usuario y renderizar mensajes en el chat.
 * - Enviar el historial al backend (`POST /api/chat`) y persistir estado local.
 * - Mostrar progreso de inferencia (parámetros inferidos) y recomendaciones finales.
 * - Renderizar un fondo de partículas en canvas.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    initParticleBackground();
    
    let conversationHistory = [];

    // Cache DOM elements
    const elements = {
        chatContainer: document.getElementById('chat-container'),
        chatForm: document.getElementById('chat-form'),
        chatInput: document.getElementById('chat-input'),
        sendBtn: document.getElementById('send-btn'),
        progressCounter: document.getElementById('progress-counter'),
        parameterList: document.getElementById('parameter-list'),
        progressRingCircle: document.querySelector('.progress-ring__circle'),
        statusBanner: document.getElementById('status-banner')
    };

    const PARAMETER_LABELS = {
        complexity: 'Complejidad',
        scalability: 'Escalabilidad',
        teamExperience: 'Experiencia',
        dataVolume: 'Volumen de Datos',
        teamSize: 'Tamaño del Equipo',
        availability: 'Disponibilidad',
        maintainability: 'Mantenibilidad',
        interoperability: 'Interoperabilidad',
    };

    elements.chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = elements.chatInput.value.trim();
        if (!userInput) return;

        appendMessage('user', `<p>${escapeHtml(userInput)}</p>`);
        conversationHistory.push({ role: 'user', content: userInput });
        elements.chatInput.value = '';
        toggleForm(false);
        clearStatus();
        const typingIndicator = appendTypingIndicator();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history: conversationHistory }),
            });

            if (typingIndicator?.parentNode) {
                elements.chatContainer.removeChild(typingIndicator);
            }

            if (!res.ok) {
                let msg = 'Error de comunicación con el servidor.';
                try { 
                    const j = await res.json(); 
                    if (j?.detail) msg = j.detail; 
                } catch {}
                showStatus('error', msg);
                throw new Error(msg);
            }

            const { response, state } = await res.json();
            response.state = state;
            conversationHistory.push(response);
            
            updateProgress(state);

            if (response.recommendation) {
                appendMessage('assistant', generateRecommendationHtml(response.recommendation));
            } else {
                appendMessage('assistant', `<p>${response.content}</p>`);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            if (typingIndicator?.parentNode) {
                elements.chatContainer.removeChild(typingIndicator);
            }
            appendMessage('assistant', '<p>Error del sistema. No se pudo procesar la solicitud. Por favor, reintenta.</p>');
        } finally {
            toggleForm(true);
        }
    });

    /**
     * Agrega un mensaje al contenedor de chat.
     *
     * @param {'user'|'assistant'} sender - Quién envía el mensaje.
     * @param {string} htmlContent - Contenido HTML ya preparado para insertar.
     *   Importante: si contiene texto proveniente del usuario, debe venir escapado
     *   con `escapeHtml` para evitar inyección de HTML.
     *
     * @returns {HTMLDivElement} El wrapper DOM del mensaje insertado.
     */
    function appendMessage(sender, htmlContent) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `chat-message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = sender === 'assistant' ? 'avatar glass-avatar' : 'avatar';
        
        const icons = {
            assistant: `<div class="avatar-glow"></div>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 1v6m0 6v6m10.71-8.29l-5.66 5.66M6.95 6.95L1.29 1.29m20.42 0l-5.66 5.66M6.95 17.05l-5.66 5.66"/>
                </svg>`,
            user: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M20 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M4 21v-2a4 4 0 0 1 3-3.87"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>`
        };
        
        avatar.innerHTML = icons[sender];
        
        const messageContent = document.createElement('div');
        messageContent.className = sender === 'assistant' ? 'message-content glass-message' : 'message-content';
        messageContent.innerHTML = sender === 'assistant' ? '<div class="glass-shine"></div>' + htmlContent : htmlContent;
        
        messageWrapper.append(sender === 'assistant' ? avatar : messageContent, sender === 'assistant' ? messageContent : avatar);
        elements.chatContainer.appendChild(messageWrapper);
        
        setTimeout(() => {
            elements.chatContainer.scrollTo({
                top: elements.chatContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
        
        return messageWrapper;
    }
    
    /**
     * Muestra un indicador de “escribiendo…” del asistente.
     *
     * @returns {HTMLDivElement} Nodo DOM del mensaje que contiene el indicador.
     *   Se usa para removerlo cuando el backend responde.
     */
    function appendTypingIndicator() {
        const html = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        return appendMessage('assistant', html);
    }

    /**
     * Genera el HTML para renderizar las recomendaciones finales.
     *
     * @param {Array<Object>} recommendations - Lista de recomendaciones del backend.
     *   Se espera que cada elemento tenga al menos:
     *   - `name` (string)
     *   - `description` (string, opcional)
     *   - `justification` (string, opcional)
     *   - y los parámetros técnicos (complexity, scalability, etc.).
     *
     * @returns {string} Fragmento HTML listo para insertar en un mensaje.
     */
    function generateRecommendationHtml(recommendations) {
        markInferenceComplete();
        
        let html = '<p class="highlight-text"><strong>⚡ Análisis Completado.</strong></p><p>Basándose en los parámetros inferidos, se recomiendan las siguientes arquitecturas:</p>';
        
        recommendations.forEach((rec, index) => {
            const isPrimary = index === 0;
            const cardClass = isPrimary ? 'primary' : 'secondary';
            const icon = isPrimary 
                ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                     <polygon points="12 2 15 11 24 11 17 17 20 26 12 20 4 26 7 17 0 11 9 11 12 2"/>
                   </svg>`
                : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                     <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                   </svg>`;
            
            const titleText = isPrimary ? `⭐ Recomendación Principal: ${rec.name}` : `Alternativa: ${rec.name}`;

            html += `
                <div class="recommendation-card ${cardClass}">
                    <div class="rec-header">
                        ${icon}
                        <h3>${escapeHtml(titleText)}</h3>
                    </div>
                    <div class="rec-body">
                        <div class="rec-section">
                            <h5>💡 Concepto</h5>
                            <p>${escapeHtml(rec.description || 'N/A')}</p>
                        </div>
                        <div class="rec-section">
                            <h5>🎯 Justificación</h5>
                            <p>${escapeHtml(rec.justification || 'N/A')}</p>
                        </div>
                        <details>
                            <summary>📊 Ver Especificaciones Técnicas</summary>
                            <ul class="tech-specs">
                                <li><strong>Complejidad</strong> ${escapeHtml(rec.complexity)}</li>
                                <li><strong>Escalabilidad</strong> ${escapeHtml(rec.scalability)}</li>
                                <li><strong>Experiencia</strong> ${escapeHtml(rec.teamExperience)}</li>
                                <li><strong>Volumen de Datos</strong> ${escapeHtml(rec.dataVolume)}</li>
                                <li><strong>Tamaño del Equipo</strong> ${escapeHtml(rec.teamSize)}</li>
                                <li><strong>Disponibilidad</strong> ${escapeHtml(rec.availability)}</li>
                                <li><strong>Mantenibilidad</strong> ${escapeHtml(rec.maintainability)}</li>
                                <li><strong>Interoperabilidad</strong> ${escapeHtml(rec.interoperability)}</li>
                            </ul>
                        </details>
                    </div>
                </div>
            `;
        });
        return html;
    }

    /**
     * Habilita o deshabilita el formulario de chat.
     *
     * @param {boolean} enabled - Si `true`, habilita input y botón y enfoca el input.
     *   Si `false`, los deshabilita para prevenir envíos duplicados.
     */
    function toggleForm(enabled) {
        elements.chatInput.disabled = !enabled;
        elements.sendBtn.disabled = !enabled;
        if(enabled) elements.chatInput.focus();
    }

    /**
     * Actualiza el panel de progreso de inferencia en base al `state` del backend.
     *
     * @param {Object} [state] - Estado enviado por el backend.
     * @param {Object<string,string>} [state.inferredParams] - Parámetros inferidos.
     * @param {Object} [state.lastQuestion] - Última pregunta generada.
     * @param {string} [state.lastQuestion.parameter_to_infer] - Parámetro actualmente activo.
     *
     * @returns {void}
     */
    function updateProgress(state) {
        if (!state?.inferredParams) {
            elements.progressCounter.textContent = '0/5';
            elements.parameterList.innerHTML = '';
            setCircleProgress(0);
            return;
        }

        const inferredParams = state.inferredParams;
        const inferredCount = Object.keys(inferredParams).length;
        
        elements.progressCounter.textContent = `${inferredCount}/5`;
        setCircleProgress(Math.min(100, (inferredCount / 5) * 100));

        elements.parameterList.innerHTML = '';
        const relevantParams = new Set([
            ...Object.keys(inferredParams), 
            ...(state.lastQuestion ? [state.lastQuestion.parameter_to_infer] : [])
        ]);
        
        relevantParams.forEach(param => {
            const li = document.createElement('li');
            const value = inferredParams[param];
            const label = PARAMETER_LABELS[param] || param;
            
            li.className = `parameter-item ${value ? 'completed' : 'active'}`;
            li.innerHTML = value 
                ? `<span class="parameter-label">${escapeHtml(label)}</span>
                   <span class="parameter-value">${escapeHtml(value)}</span>`
                : `<span class="parameter-label">${escapeHtml(label)}</span>
                   <div class="typing-dots"><span></span><span></span><span></span></div>`;
            
            elements.parameterList.appendChild(li);
        });
    }

    /**
     * Actualiza el anillo circular de progreso usando stroke-dashoffset.
     *
     * @param {number} percent - Porcentaje 0..100.
     * @returns {void}
     */
    function setCircleProgress(percent) {
        if (!elements.progressRingCircle) return;
        const circumference = 60 * 2 * Math.PI;
        const offset = circumference - (percent / 100) * circumference;
        elements.progressRingCircle.style.strokeDashoffset = offset;
    }
    
    /**
     * Marca visualmente el proceso de inferencia como completado.
     *
     * @returns {void}
     */
    function markInferenceComplete() {
        document.getElementById('pulse-indicator')?.classList.add('completed');
    }
    
    /**
     * Escapa caracteres especiales para evitar inyección de HTML.
     *
     * @param {*} str - Valor a escapar. Si no es string, se retorna tal cual.
     * @returns {*} Si `str` es string, retorna string escapado. En otro caso, retorna `str`.
     */
    const escapeHtml = (str) => typeof str === 'string' 
        ? str.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))
        : str;
    
    /**
     * Muestra un banner de estado temporal.
     *
     * @param {'error'|'info'|'success'|string} type - Tipo lógico. Actualmente no cambia estilos,
     *   pero se conserva para extensibilidad.
     * @param {string} message - Mensaje (HTML permitido). Si viene de entrada usuario, debe escaparse.
     * @returns {void}
     */
    function showStatus(type, message) {
        elements.statusBanner.innerHTML = '<div class="glass-shine"></div>' + message;
        elements.statusBanner.hidden = false;
        setTimeout(() => elements.statusBanner.hidden = true, 5000);
    }
    
    /**
     * Limpia y oculta el banner de estado.
     *
     * @returns {void}
     */
    function clearStatus() {
        elements.statusBanner.hidden = true;
        elements.statusBanner.textContent = '';
    }
    
    updateProgress();
    elements.chatInput.focus();
});

/**
 * Inicializa el fondo de partículas en un `<canvas>`.
 *
 * Busca un elemento con id `particle-canvas`. Si no existe, no hace nada.
 *
 * @returns {void}
 */
function initParticleBackground() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    /**
     * Ajusta el tamaño del canvas al viewport actual.
     *
     * @returns {void}
     */
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    class Particle {
        constructor() {
            this.reset();
            this.y = Math.random() * canvas.height;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        /**
         * Reinicia la partícula a una posición inicial (arriba del canvas).
         *
         * @returns {void}
         */
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = -10;
            this.speed = Math.random() * 0.5 + 0.2;
            this.size = Math.random() * 2 + 0.5;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        /**
         * Actualiza la posición de la partícula en el tiempo.
         * Si sale del canvas por abajo, se reinicia.
         *
         * @returns {void}
         */
        update() {
            this.y += this.speed;
            if (this.y > canvas.height) {
                this.reset();
            }
        }
        
        /**
         * Dibuja la partícula en el contexto 2D.
         *
         * @returns {void}
         */
        draw() {
            ctx.fillStyle = `rgba(0, 245, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.shadowBlur = 10;
            ctx.shadowColor = `rgba(0, 245, 255, ${this.opacity})`;
        }
    }
    
    const particles = [];
    const particleCount = 80;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    /**
     * Dibuja líneas de conexión entre partículas cercanas.
     *
     * @returns {void}
     */
    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    ctx.strokeStyle = `rgba(0, 245, 255, ${0.1 * (1 - distance / 150)})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    /**
     * Loop de animación principal.
     *
     * Limpia el canvas, actualiza y dibuja partículas, luego dibuja conexiones.
     * Se auto-programa con `requestAnimationFrame`.
     *
     * @returns {void}
     */
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        drawConnections();
        
        requestAnimationFrame(animate);
    }
    
    animate();
}
