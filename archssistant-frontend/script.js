/**
 * Arch-Assistant Frontend.
 *
 * Responsibilities:
 * - Manage user input and render chat messages.
 * - Send history to backend (`POST /api/chat`) and persist local state.
 * - Display inference progress (inferred parameters) and final recommendations.
 * - Render particle background on canvas.
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
        complexity: 'Complexity',
        scalability: 'Scalability',
        teamExperience: 'Experience',
        dataVolume: 'Data Volume',
        teamSize: 'Team Size',
        availability: 'Availability',
        maintainability: 'Maintainability',
        interoperability: 'Interoperability',
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
                let msg = 'Server communication error.';
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
            appendMessage('assistant', '<p>System error. Unable to process request. Please try again.</p>');
        } finally {
            toggleForm(true);
        }
    });

    /**
     * Adds a message to the chat container.
     *
     * @param {'user'|'assistant'} sender - Who is sending the message.
     * @param {string} htmlContent - HTML content ready to insert.
     *   Important: if it contains text from the user, it must be escaped
     *   with `escapeHtml` to prevent HTML injection.
     *
     * @returns {HTMLDivElement} The DOM wrapper of the inserted message.
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
     * Shows an assistant "typing..." indicator.
     *
     * @returns {HTMLDivElement} DOM node of the message containing the indicator.
     *   Used to remove it when the backend responds.
     */
    function appendTypingIndicator() {
        const html = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        return appendMessage('assistant', html);
    }

    /**
     * Generates HTML to render final recommendations.
     *
     * @param {Array<Object>} recommendations - List of recommendations from backend.
     *   Each element is expected to have at least:
     *   - `name` (string)
     *   - `description` (string, optional)
     *   - `justification` (string, optional)
     *   - and technical parameters (complexity, scalability, etc.).
     *
     * @returns {string} HTML fragment ready to insert in a message.
     */
    function generateRecommendationHtml(recommendations) {
        markInferenceComplete();
        
        let html = '<p class="highlight-text"><strong>⚡ Analysis Complete.</strong></p><p>Based on the inferred parameters, the following architectures are recommended:</p>';
        
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
            
            const titleText = isPrimary ? `⭐ Primary Recommendation: ${rec.name}` : `Alternative: ${rec.name}`;

            html += `
                <div class="recommendation-card ${cardClass}">
                    <div class="rec-header">
                        ${icon}
                        <h3>${escapeHtml(titleText)}</h3>
                    </div>
                    <div class="rec-body">
                        <div class="rec-section">
                            <h5>💡 Concept</h5>
                            <p>${escapeHtml(rec.description || 'N/A')}</p>
                        </div>
                        <div class="rec-section">
                            <h5>🎯 Justification</h5>
                            <p>${escapeHtml(rec.justification || 'N/A')}</p>
                        </div>
                        <details>
                            <summary>📊 View Technical Specifications</summary>
                            <ul class="tech-specs">
                                <li><strong>Complexity</strong> ${escapeHtml(rec.complexity)}</li>
                                <li><strong>Scalability</strong> ${escapeHtml(rec.scalability)}</li>
                                <li><strong>Experience</strong> ${escapeHtml(rec.teamExperience)}</li>
                                <li><strong>Data Volume</strong> ${escapeHtml(rec.dataVolume)}</li>
                                <li><strong>Team Size</strong> ${escapeHtml(rec.teamSize)}</li>
                                <li><strong>Availability</strong> ${escapeHtml(rec.availability)}</li>
                                <li><strong>Maintainability</strong> ${escapeHtml(rec.maintainability)}</li>
                                <li><strong>Interoperability</strong> ${escapeHtml(rec.interoperability)}</li>
                            </ul>
                        </details>
                    </div>
                </div>
            `;
        });
        return html;
    }

    /**
     * Enables or disables the chat form.
     *
     * @param {boolean} enabled - If `true`, enables input and button and focuses input.
     *   If `false`, disables them to prevent duplicate submissions.
     */
    function toggleForm(enabled) {
        elements.chatInput.disabled = !enabled;
        elements.sendBtn.disabled = !enabled;
        if(enabled) elements.chatInput.focus();
    }

    /**
     * Updates the inference progress panel based on backend `state`.
     *
     * @param {Object} [state] - State sent by the backend.
     * @param {Object<string,string>} [state.inferredParams] - Inferred parameters.
     * @param {Object} [state.lastQuestion] - Last generated question.
     * @param {string} [state.lastQuestion.parameter_to_infer] - Currently active parameter.
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
     * Updates the circular progress ring using stroke-dashoffset.
     *
     * @param {number} percent - Percentage 0..100.
     * @returns {void}
     */
    function setCircleProgress(percent) {
        if (!elements.progressRingCircle) return;
        const circumference = 60 * 2 * Math.PI;
        const offset = circumference - (percent / 100) * circumference;
        elements.progressRingCircle.style.strokeDashoffset = offset;
    }
    
    /**
     * Visually marks the inference process as completed.
     *
     * @returns {void}
     */
    function markInferenceComplete() {
        document.getElementById('pulse-indicator')?.classList.add('completed');
    }
    
    /**
     * Escapes special characters to prevent HTML injection.
     *
     * @param {*} str - Value to escape. If not a string, returns as is.
     * @returns {*} If `str` is a string, returns escaped string. Otherwise, returns `str`.
     */
    const escapeHtml = (str) => typeof str === 'string' 
        ? str.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))
        : str;
    
    /**
     * Shows a temporary status banner.
     *
     * @param {'error'|'info'|'success'|string} type - Logical type. Currently doesn't change styles,
     *   but kept for extensibility.
     * @param {string} message - Message (HTML allowed). If from user input, must be escaped.
     * @returns {void}
     */
    function showStatus(type, message) {
        elements.statusBanner.innerHTML = '<div class="glass-shine"></div>' + message;
        elements.statusBanner.hidden = false;
        setTimeout(() => elements.statusBanner.hidden = true, 5000);
    }
    
    /**
     * Clears and hides the status banner.
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
 * Initializes the particle background on a `<canvas>`.
 *
 * Looks for an element with id `particle-canvas`. If it doesn't exist, does nothing.
 *
 * @returns {void}
 */
function initParticleBackground() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    /**
     * Adjusts canvas size to current viewport.
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
         * Resets the particle to initial position (top of canvas).
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
         * Updates the particle position over time.
         * If it exits the canvas from below, it resets.
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
         * Draws the particle on the 2D context.
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
     * Draws connection lines between nearby particles.
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
     * Main animation loop.
     *
     * Clears the canvas, updates and draws particles, then draws connections.
     * Self-schedules with `requestAnimationFrame`.
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
