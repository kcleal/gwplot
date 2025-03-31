// Native WebSocket-based client implementation for genome visualization
let socket;

// Throttling manager to prevent overwhelming the server
const throttleManager = {
    isWaitingForResponse: false,
    lastRequestTime: 0,
    minThrottleTime: 100,
    adaptiveThrottleTime: 200,
    maxThrottleTime: 1000,
    responseTimeSamples: [],
    sampleSize: 5,
    throttleMultiplier: 1.2,
    activeKeys: {}, // Track which keys are currently active/held
    lastFrameTime: 0, // Track last frame time
    targetFrameTime: 1000 / 60, // Target 60 FPS


    // Record a new request being sent
    recordRequest: function(key) {
        this.lastRequestTime = performance.now();
        this.isWaitingForResponse = true;

        // If this is a key event, mark it as the active key
        if (key) {
            this.activeKeys[key] = true;
        }
    },

    // Record a response received
    recordResponse: function(responseTime) {
        // Add the new sample
        this.responseTimeSamples.push(responseTime);

        // Keep only the last N samples
        if (this.responseTimeSamples.length > this.sampleSize) {
            this.responseTimeSamples.shift();
        }

        // Calculate new throttle time based on average response time
        if (this.responseTimeSamples.length > 0) {
            const avgResponseTime = this.responseTimeSamples.reduce((sum, time) => sum + time, 0) /
                                   this.responseTimeSamples.length;

            // Set throttle time to average response time plus a buffer
            this.adaptiveThrottleTime = Math.min(
                this.maxThrottleTime,
                Math.max(this.minThrottleTime, avgResponseTime * this.throttleMultiplier)
            );
        }

        // Mark that we've received a response
        this.isWaitingForResponse = false;

        // Calculate time since last frame
        const now = performance.now();
        const timeSinceLastFrame = now - this.lastFrameTime;

        // If we need to delay to maintain frame rate
        if (timeSinceLastFrame < this.targetFrameTime) {
            const delay = this.targetFrameTime - timeSinceLastFrame;
            setTimeout(() => {
                this.lastFrameTime = performance.now();
                this.processPendingRequests();
            }, delay);
        } else {
            // Process immediately if we're below target frame rate
            this.lastFrameTime = now;
            this.processPendingRequests();
        }
    },

    // Register a key as active (being held down)
    activateKey: function(key) {
        this.activeKeys[key] = true;

        // If we're not currently waiting for a response, send the request immediately
        if (!this.isWaitingForResponse) {
            this.sendKeyRequest(key);
        }
    },

    // Register a key as released
    deactivateKey: function(key) {
        delete this.activeKeys[key];

        // Send the release event immediately (not throttled)
        sendKeyToServer(key, 'release');
    },

    // Send a key request and mark us as waiting
    sendKeyRequest: function(key) {
        this.lastFrameTime = performance.now();
        this.recordRequest(key);
        sendKeyToServer(key, 'press');
    },

    // Process any active keys
    processPendingRequests: function() {
        // If we're waiting for a response or there are no active keys, do nothing
        if (this.isWaitingForResponse || Object.keys(this.activeKeys).length === 0) {
            return;
        }

        // Get the first active key
        const nextKey = Object.keys(this.activeKeys)[0];

        // Send the request for this key
        this.sendKeyRequest(nextKey);
    },

    // Display current throttle state in performance monitor
    getStatus: function() {
        return {
            throttleTime: this.adaptiveThrottleTime.toFixed(0),
            activeKeys: Object.keys(this.activeKeys).join(','),
            waitingForResponse: this.isWaitingForResponse ? 'Yes' : 'No',
            avgResponseTime: this.responseTimeSamples.length > 0 ?
                (this.responseTimeSamples.reduce((sum, time) => sum + time, 0) /
                this.responseTimeSamples.length).toFixed(0) : "N/A"
        };
    }
};

// Performance monitoring system
const performanceMonitor = {
    frameCount: 0,
    lastFpsUpdate: 0,
    frameRateElement: null,
    renderTimes: [],
    networkTimes: [],
    requestTimes: {},

    init: function() {
        // Create FPS display element
        if (!this.frameRateElement) {
            this.frameRateElement = document.createElement('div');
            this.frameRateElement.id = 'fpsCounter';
            // CSS is now handled in styles.css
            this.frameRateElement.textContent = "Initializing performance monitor...";
            document.body.appendChild(this.frameRateElement);
        }

        // Start the monitoring loop
        this.update();
    },

    // Record a frame render
    recordFrame: function() {
        this.frameCount++;
    },

    // Start timing a request
    startTiming: function(requestId) {
        this.requestTimes[requestId] = performance.now();
    },

    // Record network time for a completed request
    endTiming: function(requestId) {
        if (this.requestTimes[requestId]) {
            const time = performance.now() - this.requestTimes[requestId];
            this.networkTimes.push(time);
            if (this.networkTimes.length > 60) {
                this.networkTimes.shift();
            }
            delete this.requestTimes[requestId];
        }
    },

    // Record render time (in ms)
    recordRenderTime: function(time) {
        this.renderTimes.push(time);
        if (this.renderTimes.length > 60) {
            this.renderTimes.shift();
        }
    },

    // Record receiving an image
    recordImageReceived: function() {
        // Record a frame render
        this.recordFrame();

        // End timing for any pending requests
        const now = performance.now();
        for (const requestId in this.requestTimes) {
            const time = now - this.requestTimes[requestId];
            this.networkTimes.push(time);
            if (this.networkTimes.length > 60) {
                this.networkTimes.shift();
            }
            delete this.requestTimes[requestId];
        }
    },

    // Update statistics display
    update: function() {
        const now = performance.now();

        // Update FPS counter every second
        if (now - this.lastFpsUpdate >= 1000) {
            const fps = this.frameCount;
            const avgNetworkTime = this.networkTimes.length > 0
                ? this.networkTimes.reduce((sum, val) => sum + val, 0) / this.networkTimes.length
                : 0;
            const avgRenderTime = this.renderTimes.length > 0
                ? this.renderTimes.reduce((sum, val) => sum + val, 0) / this.renderTimes.length
                : 0;

            // Get throttling status
            const throttleStatus = throttleManager.getStatus();

            this.frameRateElement.innerHTML = `
                FPS: ${fps}<br>
                Network: ${avgNetworkTime.toFixed(1)}ms<br>
                Render: ${avgRenderTime.toFixed(1)}ms<br>
                Throttle: ${throttleStatus.throttleTime}ms<br>
                Keys: ${throttleStatus.activeKeys || 'None'}<br>
                Waiting: ${throttleStatus.waitingForResponse}<br>
                Avg Resp: ${throttleStatus.avgResponseTime}ms
            `;

            this.frameCount = 0;
            this.lastFpsUpdate = now;
        }

        requestAnimationFrame(() => this.update());
    }
};

// Canvas manager for image handling
const canvasManager = {
    canvas: null,
    context: null,

    init: function() {
        this.canvas = document.getElementById('genomePlot');
        if (!this.canvas) {
            console.error("Canvas element 'genomePlot' not found!");
            return;
        }

        console.log("Initializing canvas:", this.canvas);

        this.context = this.canvas.getContext('2d', {
            alpha: false,
            desynchronized: true // Lower latency where supported
        });

        if (!this.context) {
            console.error("Failed to get 2d context from canvas!");
            return;
        }

        console.log("Canvas context initialized successfully");

        // Apply hardware acceleration hints
        this.canvas.style.willChange = 'transform';
        this.canvas.style.transform = 'translateZ(0)';
    },

    updateCanvas: function(imageData) {
        performanceMonitor.recordFrame();
        const renderStartTime = performance.now();

        const img = new Image();

        img.onload = () => {
            // Use image.decode() API if available for faster decoding
            const processImage = () => {
                // Resize canvas if needed
                if (this.canvas.width !== img.width || this.canvas.height !== img.height) {
                    this.canvas.width = img.width;
                    this.canvas.height = img.height;
                }

                // Clear and draw the new image
                this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
                this.context.drawImage(img, 0, 0);

                const renderTime = performance.now() - renderStartTime;
                performanceMonitor.recordRenderTime(renderTime);

                // Adjust output box height
                adjustOutputBoxHeight();
            };

            // Use decode() if available, otherwise proceed directly
            if ('decode' in img) {
                img.decode().then(processImage).catch(err => {
                    console.error("Image decode error:", err);
                    processImage(); // Fall back to standard processing
                });
            } else {
                processImage();
            }
        };

        img.onerror = (e) => {
            console.error("Error loading image:", e);
        };

        // Set attributes for faster loading
        img.decoding = 'async';
        img.importance = 'high';
        img.src = imageData;
    }
};

// Calculate canvas dimensions accounting for device pixel ratio
function getCanvasDimensions() {
    const dpr = window.devicePixelRatio || 1;

    // Get available space for the canvas
    const containerWidth = Math.max(window.innerWidth - 20, 300);
    const containerHeight = Math.max(Math.floor(window.innerHeight * 0.6), 300);

    // Calculate physical dimensions (what the canvas actually renders at)
    const physicalWidth = Math.round(containerWidth * dpr);
    const physicalHeight = Math.round(containerHeight * dpr);

    return {
        containerWidth,  // CSS width
        containerHeight, // CSS height
        physicalWidth,   // Actual canvas width in pixels
        physicalHeight,  // Actual canvas height in pixels
        dpr
    };
}

// Function to ensure output box takes up remaining space
function adjustOutputBoxHeight() {
    const genomePlot = document.getElementById('genomePlot');
    const commandNav = document.querySelector('.command-nav-container');
    const windowHeight = window.innerHeight;
    const usedHeight = genomePlot.offsetHeight + commandNav.offsetHeight + 40;
    const outputContainer = document.getElementById('outputContainer');
    outputContainer.style.height = (windowHeight - usedHeight) + 'px';
}

// Process binary image data and draw to canvas
function processBinaryImage(binaryData) {
    console.log("Processing binary image data:", {
        type: Object.prototype.toString.call(binaryData),
        byteLength: binaryData.byteLength || (binaryData.length ? binaryData.length : "unknown"),
        isEmpty: !binaryData || binaryData.byteLength === 0 || binaryData.length === 0
    });

    const renderStartTime = performance.now();

    // Create a blob from the binary data
    const blob = new Blob([binaryData], {type: 'image/jpeg'});
    console.log("Created blob:", blob.size, "bytes");

    // Use createImageBitmap for efficient rendering
    createImageBitmap(blob).then(bitmap => {
        console.log("Bitmap created successfully:", {
            width: bitmap.width,
            height: bitmap.height
        });

        const canvas = canvasManager.canvas;
        const context = canvasManager.context;
        const dimensions = getCanvasDimensions();

        // Set the canvas's internal dimensions to match the image
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;

        // Calculate CSS dimensions to maintain aspect ratio while fitting the container
        const containerRatio = dimensions.containerWidth / dimensions.containerHeight;
        const imageRatio = bitmap.width / bitmap.height;

        let cssWidth, cssHeight;

        if (imageRatio > containerRatio) {
            // Image is wider than container (relative to heights)
            cssWidth = dimensions.containerWidth;
            cssHeight = dimensions.containerWidth / imageRatio;
        } else {
            // Image is taller than container (relative to widths)
            cssHeight = dimensions.containerHeight;
            cssWidth = dimensions.containerHeight * imageRatio;
        }

        // Apply CSS dimensions to fit container while maintaining aspect ratio
        canvas.style.width = cssWidth + 'px';
        canvas.style.height = cssHeight + 'px';

        // Clear and draw the bitmap at its native resolution
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(bitmap, 0, 0);

        console.log(`Canvas physical size: ${canvas.width}x${canvas.height}`);
        console.log(`Canvas display size: ${cssWidth}x${cssHeight}`);

        // Record render time
        const renderTime = performance.now() - renderStartTime;
        performanceMonitor.recordRenderTime(renderTime);

        // Adjust output box height after rendering
        adjustOutputBoxHeight();

        // Update performance metrics
        performanceMonitor.recordImageReceived();
    }).catch(err => {
        console.error('Error creating image bitmap:', err);
    });
}

// Request a fresh image from the server
function requestImage() {
    sendWebSocketMessage({
        type: 'refresh_image'
    });
}

// Original send WebSocket message function
function sendWebSocketMessageBase(data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const requestId = Date.now().toString();
        data.requestId = requestId;
        performanceMonitor.startTiming(requestId);

        socket.send(JSON.stringify(data));
    } else {
        console.warn('WebSocket not connected, cannot send message:', data);
    }
}

// Send message to server via WebSocket with throttling support
function sendWebSocketMessage(data) {
    // For key events, apply special handling
    if (data.type === 'key_event') {
        // Release events are sent immediately (no throttling)
        if (data.action === 'release') {
            console.log(`Sending key release for ${data.key} immediately`);
            sendWebSocketMessageBase(data);
            return;
        }

        // Key press events are managed by the throttle system
        // We don't need additional handling here for press events,
        // since throttleManager.activateKey handles it
        return;
    }

    // For mouse events, check if it's a release
    if (data.type === 'mouse_event' && data.action === 'release') {
        // Send mouse release events immediately
        sendWebSocketMessageBase(data);
        return;
    }

    // For all other messages
    sendWebSocketMessageBase(data);
}

// Send key events to server via WebSocket
function sendKeyToServer(key, action = 'press') {
    sendWebSocketMessageBase({
        type: 'key_event',
        key: key,
        action: action
    });
}

// Send mouse events to server via WebSocket
function sendMouseEventToServer(x, y, button, action) {
    sendWebSocketMessage({
        type: 'mouse_event',
        x: x,
        y: y,
        button: button,
        action: action
    });
}

// Send canvas size updates to server
function updateCanvasSize() {
    const dimensions = getCanvasDimensions();
    const canvas = document.getElementById('genomePlot');

    // Set CSS dimensions for the display container
    canvas.style.width = dimensions.containerWidth + 'px';
    canvas.style.height = dimensions.containerHeight + 'px';

    // Set the actual dimensions of the canvas element
    // We'll let the server dictate the actual rendering size
    // But we inform it of our container size and DPR

    console.log(`Updating canvas size: ${dimensions.containerWidth}x${dimensions.containerHeight} (DPR: ${dimensions.dpr})`);

    // Tell the server our container size and DPR
    sendWebSocketMessage({
        type: 'update_canvas_size',
        width: dimensions.containerWidth,
        height: dimensions.containerHeight,
        dpr: dimensions.dpr
    });

    // Adjust the output box height
    adjustOutputBoxHeight();
}

// Update the output box with new content
function updateOutputBox(text) {
    const outputBox = document.getElementById('outputBox');
    const isScrolledToBottom = (outputBox.scrollHeight - outputBox.clientHeight) <= (outputBox.scrollTop + 5);

    outputBox.textContent = text;

    // Auto-scroll if user was at the bottom
    if (isScrolledToBottom) {
        outputBox.scrollTop = outputBox.scrollHeight;
    }
}

// Handle form submission
function setupCommandForm() {
    document.getElementById('commandForm').onsubmit = function(event) {
        event.preventDefault();
        const inputElement = document.getElementById('user_input');
        const userInput = inputElement.value;

        sendWebSocketMessage({
            type: 'command',
            command: userInput
        });

        // Clear the input after submission
        inputElement.value = '';
    };
}

// Setup navigation buttons
function setupNavigationButtons() {
    // Left button
    document.getElementById('btn-left').addEventListener('mousedown', function() {
        throttleManager.activateKey('ArrowLeft');
    });
    document.getElementById('btn-left').addEventListener('mouseup', function() {
        throttleManager.deactivateKey('ArrowLeft');
    });

    // Right button
    document.getElementById('btn-right').addEventListener('mousedown', function() {
        throttleManager.activateKey('ArrowRight');
    });
    document.getElementById('btn-right').addEventListener('mouseup', function() {
        throttleManager.deactivateKey('ArrowRight');
    });

    // Zoom in
    document.getElementById('btn-zoom-in').addEventListener('mousedown', function() {
        throttleManager.activateKey('ArrowUp');
    });
    document.getElementById('btn-zoom-in').addEventListener('mouseup', function() {
        throttleManager.deactivateKey('ArrowUp');
    });

    // Zoom out
    document.getElementById('btn-zoom-out').addEventListener('mousedown', function() {
        throttleManager.activateKey('ArrowDown');
    });
    document.getElementById('btn-zoom-out').addEventListener('mouseup', function() {
        throttleManager.deactivateKey('ArrowDown');
    });

    // Scroll up
    document.getElementById('btn-up').addEventListener('mousedown', function() {
        throttleManager.activateKey('PageUp');
    });
    document.getElementById('btn-up').addEventListener('mouseup', function() {
        throttleManager.deactivateKey('PageUp');
    });

    // Scroll down
    document.getElementById('btn-down').addEventListener('mousedown', function() {
        throttleManager.activateKey('PageDown');
    });
    document.getElementById('btn-down').addEventListener('mouseup', function() {
        throttleManager.deactivateKey('PageDown');
    });

}

// Setup clear output button
function setupClearButton() {
    document.getElementById('clearOutput').addEventListener('click', function() {
        sendWebSocketMessage({
            type: 'clear_output'
        });
    });
}

// Set up mouse event handling for the canvas
function setupMouseHandling() {
    const canvas = document.getElementById('genomePlot');

    // Mouse down handler
    canvas.addEventListener('mousedown', function(event) {
        const button = event.button === 0 ? 'left' : 'right';
        handleMouseEvent(event, button, 'press');
    });

    // Mouse up handler
    canvas.addEventListener('mouseup', function(event) {
        const button = event.button === 0 ? 'left' : 'right';
        handleMouseEvent(event, button, 'release');
    });

    // Mouse wheel handler
    canvas.addEventListener('wheel', function(event) {
        event.preventDefault(); // Prevent page scrolling
        const wheelAction = event.deltaY > 0 ? 'wheel_down' : 'wheel_up';
        handleMouseEvent(event, wheelAction, 'press');
    });

    function handleMouseEvent(event, button, action) {
        const canvas = event.target;
        const rect = canvas.getBoundingClientRect();
        const cssX = event.clientX - rect.left;
        const cssY = event.clientY - rect.top;
        const canvasX = Math.round(cssX * (canvas.width / rect.width));
        const canvasY = Math.round(cssY * (canvas.height / rect.height));

        sendMouseEventToServer(canvasX, canvasY, button, action);
    }
}

// Setup keyboard event handling
function setupKeyboardHandling() {
    document.addEventListener('keydown', function(event) {
        const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "PageUp", "PageDown"];

        // If it's an arrow key, prevent default behavior (scrolling)
        if (arrowKeys.includes(event.key)) {
            event.preventDefault();

            // Register with throttle manager
            throttleManager.activateKey(event.key);
            return;
        }

        // Rest of keydown handling unchanged
        if (!event.ctrlKey && !event.metaKey && !event.altKey) {
            const commandInput = document.getElementById('user_input');
            if (document.activeElement !== commandInput &&
                !(document.activeElement.tagName === 'INPUT' && document.activeElement.type === 'text') &&
                document.activeElement.tagName !== 'TEXTAREA') {
                commandInput.focus();
            }
        }

        // Toggle FPS counter with F key
        if (event.key === 'f' && event.ctrlKey) {
            event.preventDefault();
            const fpsElement = document.getElementById('fpsCounter');
            if (fpsElement) {
                fpsElement.style.display = fpsElement.style.display === 'none' ? 'block' : 'none';
            }
        }
    });

    document.addEventListener('keyup', function(event) {
        const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "PageUp", "PageDown"];

        if (arrowKeys.includes(event.key)) {
            event.preventDefault();

            // Tell throttle manager this key is released
            throttleManager.deactivateKey(event.key);
        }
    });

    // Handle page visibility change
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Release all active keys when tab loses focus
            const activeKeys = [...Object.keys(throttleManager.activeKeys)];
            activeKeys.forEach(key => {
                throttleManager.deactivateKey(key);
            });
        }
    });
}

// Handle window resize events
function setupResizeHandling() {
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            updateCanvasSize();
        }, 250); // Wait 250ms after resize finishes
    });
}

// Handle visibility changes
function setupVisibilityHandling() {
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            // Page is visible again, request a refresh of the canvas
            requestImage();
        }
    });
}

// Initialize WebSocket connection
function initializeWebSocket() {
    // Create WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    socket = new WebSocket(wsUrl);

    const dimensions = getCanvasDimensions();

    // Handle connection open
    socket.onopen = function() {
        console.log('WebSocket connection established');
        sendWebSocketMessage({
            type: 'update_canvas_size',
            width: dimensions.containerWidth,
            height: dimensions.containerHeight,
            dpr: dimensions.dpr
        });
    };

    // Handle binary data and text messages
    socket.onmessage = function(event) {
        if (event.data instanceof Blob) {
            // Binary data (image)
            console.log("Received binary data", event.data.size, "bytes");

            // Calculate response time
            const now = performance.now();
            let responseTime = 0;

            if (Object.keys(performanceMonitor.requestTimes).length > 0) {
                const oldestRequestId = Object.keys(performanceMonitor.requestTimes)
                    .reduce((oldest, current) => {
                        return performanceMonitor.requestTimes[current] <
                               performanceMonitor.requestTimes[oldest] ?
                               current : oldest;
                    }, Object.keys(performanceMonitor.requestTimes)[0]);

                responseTime = now - performanceMonitor.requestTimes[oldestRequestId];
                delete performanceMonitor.requestTimes[oldestRequestId];
            }

            // Process the image data
            event.data.arrayBuffer().then(buffer => {
                processBinaryImage(buffer);

                // Record response AFTER image is processed
                throttleManager.recordResponse(responseTime);
            });
        } else {
            // JSON data handling (unchanged)
            try {
                const jsonData = JSON.parse(event.data);
                console.log("Received JSON data:", jsonData);

                if (jsonData.log !== undefined) {
                    updateOutputBox(jsonData.log);
                }
            } catch (e) {
                console.error("Error parsing WebSocket message:", e);
                console.log("Raw message:", event.data);
            }
        }
    };

    // Connection events
    socket.onclose = function(event) {
        console.log('WebSocket connection closed:', event.code, event.reason);
        // Attempt to reconnect after a delay
        setTimeout(function() {
            console.log('Attempting to reconnect WebSocket...');
            initializeWebSocket();
        }, 3000);
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

// Initialize everything when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log(`Device Pixel Ratio: ${window.devicePixelRatio}`);

    // Initialize the WebSocket connection
    initializeWebSocket();

    // Initialize the canvas manager
    canvasManager.init();

    // Setup various event handlers
    setupCommandForm();
    setupNavigationButtons();
    setupClearButton();
    setupMouseHandling();
    setupKeyboardHandling();
    setupResizeHandling();
    setupVisibilityHandling();

    // Apply initial resize
    updateCanvasSize();

    // Initialize the performance monitor
    setTimeout(() => {
        performanceMonitor.init();
    }, 500);
});