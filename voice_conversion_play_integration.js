/**
 * Voice Conversion Play Button Integration
 * 
 * This JavaScript module provides easy integration for voice conversion
 * with automatic play button functionality for generated audio.
 * 
 * Usage:
 * 1. Include this script in your HTML
 * 2. Call VoiceConversionPlayer.init() to initialize
 * 3. Use VoiceConversionPlayer.convertVoice() to convert and play audio
 */

class VoiceConversionPlayer {
    constructor(apiBase = 'http://localhost:8000/api/v1') {
        this.apiBase = apiBase;
        this.currentAudio = null;
    }

    /**
     * Initialize the voice conversion player
     */
    static init(apiBase) {
        window.VoiceConversionPlayer = new VoiceConversionPlayer(apiBase);
        return window.VoiceConversionPlayer;
    }

    /**
     * Convert voice and return playable audio element
     * @param {File} inputAudio - Input audio file
     * @param {File} referenceAudio - Reference audio file
     * @param {Object} options - Conversion options
     * @returns {Promise<Object>} - Conversion result with audio element
     */
    async convertVoice(inputAudio, referenceAudio, options = {}) {
        const {
            device = 'cpu',
            normalize = true,
            targetSampleRate = null
        } = options;

        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('input_audio', inputAudio);
            formData.append('reference_audio', referenceAudio);
            formData.append('device', device);
            formData.append('normalize', normalize);
            
            if (targetSampleRate) {
                formData.append('target_sample_rate', targetSampleRate);
            }

            // Show loading state
            this.showLoading();

            // Make API request
            const response = await fetch(`${this.apiBase}/convert-voice`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            this.hideLoading();

            if (result.status === 'completed') {
                // Create audio element with play controls
                const audioElement = this.createAudioElement(result);
                
                return {
                    success: true,
                    conversionId: result.conversion_id,
                    audioElement: audioElement,
                    metadata: {
                        outputFile: result.output_file,
                        fileSize: result.file_size,
                        duration: result.output_duration,
                        processingTime: result.processing_time,
                        playUrl: result.play_url
                    },
                    result: result
                };
            } else {
                throw new Error(result.message || 'Voice conversion failed');
            }
        } catch (error) {
            this.hideLoading();
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Create audio element with play controls
     * @param {Object} result - Conversion result
     * @returns {HTMLElement} - Audio element with controls
     */
    createAudioElement(result) {
        const container = document.createElement('div');
        container.className = 'voice-conversion-player';
        container.innerHTML = `
            <div class="audio-container">
                <audio controls class="audio-player">
                    <source src="${this.apiBase}${result.play_url}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <div class="audio-controls">
                    <button class="play-btn" onclick="this.parentElement.previousElementSibling.play()">▶️ Play</button>
                    <button class="pause-btn" onclick="this.parentElement.previousElementSibling.pause()">⏸️ Pause</button>
                    <button class="stop-btn" onclick="this.parentElement.previousElementSibling.currentTime = 0">⏹️ Stop</button>
                    <button class="download-btn" onclick="window.open('${this.apiBase}${result.play_url}', '_blank')">💾 Download</button>
                </div>
                <div class="audio-info">
                    <small>🎵 Streaming from database • ${(result.file_size / 1024).toFixed(1)} KB</small>
                </div>
            </div>
        `;

        // Add CSS styles
        this.addStyles();

        // Store reference to current audio
        this.currentAudio = container.querySelector('audio');

        return container;
    }

    /**
     * Add CSS styles for the audio player
     */
    addStyles() {
        if (document.getElementById('voice-conversion-styles')) return;

        const style = document.createElement('style');
        style.id = 'voice-conversion-styles';
        style.textContent = `
            .voice-conversion-player {
                margin: 20px 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                color: white;
            }
            .audio-container {
                text-align: center;
            }
            .audio-player {
                width: 100%;
                height: 50px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
            .audio-controls {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 10px;
                flex-wrap: wrap;
            }
            .audio-controls button {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            .audio-controls button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
            }
            .audio-info {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Show loading state
     */
    showLoading() {
        const existingLoading = document.getElementById('voice-conversion-loading');
        if (existingLoading) return;

        const loading = document.createElement('div');
        loading.id = 'voice-conversion-loading';
        loading.className = 'loading';
        loading.innerHTML = `
            <div class="spinner"></div>
            <p>🔄 Processing voice conversion...</p>
        `;
        document.body.appendChild(loading);
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        const loading = document.getElementById('voice-conversion-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Get conversion status
     * @param {string} conversionId - Conversion ID
     * @returns {Promise<Object>} - Status result
     */
    async getConversionStatus(conversionId) {
        try {
            const response = await fetch(`${this.apiBase}/conversion-status/${conversionId}`);
            const result = await response.json();
            
            if (response.ok) {
                return {
                    success: true,
                    status: result.status,
                    metadata: {
                        conversionId: result.conversion_id,
                        transformationType: result.transformation_type,
                        createdAt: result.created_at,
                        completedAt: result.completed_at,
                        processingTime: result.processing_time_seconds,
                        fileSize: result.output_file_size,
                        duration: result.output_duration,
                        playUrl: result.play_url
                    },
                    result: result
                };
            } else {
                throw new Error(result.detail || 'Failed to get conversion status');
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Play current audio
     */
    play() {
        if (this.currentAudio) {
            this.currentAudio.play();
        }
    }

    /**
     * Pause current audio
     */
    pause() {
        if (this.currentAudio) {
            this.currentAudio.pause();
        }
    }

    /**
     * Stop current audio
     */
    stop() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }
    }
}

// Auto-initialize if not already done
if (typeof window !== 'undefined' && !window.VoiceConversionPlayer) {
    VoiceConversionPlayer.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceConversionPlayer;
}
