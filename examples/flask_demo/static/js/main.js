// WebSocket-based client implementation for genome visualization
let socket;


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

            this.frameRateElement.innerHTML = `
                FPS: ${fps}<br>
                Network: ${avgNetworkTime.toFixed(1)}ms<br>
                Render: ${avgRenderTime.toFixed(1)}ms<br>
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
    const cssWidth = Math.max(window.innerWidth - 20, 300);
    const cssHeight = Math.max(Math.floor(window.innerHeight * 0.6), 300);
    const physicalWidth = Math.round(cssWidth * dpr);
    const physicalHeight = Math.round(cssHeight * dpr);

    return {
        cssWidth, cssHeight, physicalWidth, physicalHeight, dpr
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

        // Ensure canvas dimensions match the bitmap
        if (canvasManager.canvas.width !== bitmap.width ||
            canvasManager.canvas.height !== bitmap.height) {
            console.log("Resizing canvas to match bitmap dimensions");
            canvasManager.canvas.width = bitmap.width;
            canvasManager.canvas.height = bitmap.height;
        }

        // Clear the canvas before drawing
        canvasManager.context.clearRect(0, 0, canvasManager.canvas.width, canvasManager.canvas.height);

        // Draw the bitmap on the canvas
        canvasManager.context.drawImage(bitmap, 0, 0);
        console.log("Bitmap drawn to canvas");

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
    socket.emit('refresh_image');
}

// Initialize Socket.IO connection
function initializeWebSocket() {
    // Create Socket.IO connection
    socket = io();

    // Handle binary data
    socket.on('image_update', function(binaryData, jsonData) {
        console.log("Received image_update event", {
            binaryDataReceived: !!binaryData,
            jsonDataReceived: !!jsonData,
            jsonDataContent: jsonData
        });

        // First argument is binary data, second has the JSON metadata
        processBinaryImage(binaryData);

        // Handle any other data like logs
        if (jsonData && jsonData.log) {
            console.log("Log:", jsonData.log);
            // Make sure to update the output box with the log content
            updateOutputBox(jsonData.log);
        }
    });

    // Connection events
    socket.on('connect', function() {
        console.log('Socket.IO connection established');
        requestImage(); // Request initial image
    });

    socket.on('disconnect', function() {
        console.log('Socket.IO connection closed');
    });

    socket.on('connect_error', function(error) {
        console.error('Socket.IO connection error:', error);
    });
}


// Send key events to server via WebSocket
function sendKeyToServer(key) {
    const requestId = Date.now().toString();
    performanceMonitor.startTiming(requestId);

    socket.emit('key_event', {
        key: key,
        requestId: requestId,
    });
}

// Send mouse events to server via WebSocket
function sendMouseEventToServer(x, y, button, action) {
    const requestId = Date.now().toString();
    performanceMonitor.startTiming(requestId);

    socket.emit('mouse_event', {
        x: x,
        y: y,
        button: button,
        action: action,
        requestId: requestId,
    });
}

// Send canvas size updates to server
function updateCanvasSize() {
    const dimensions = getCanvasDimensions();

    // Set CSS dimensions for display size
    const canvas = document.getElementById('genomePlot');
    canvas.style.width = dimensions.cssWidth + 'px';
    canvas.style.height = dimensions.cssHeight + 'px';

    // Tell the server via WebSocket
    socket.emit('update_canvas_size', {
        width: dimensions.physicalWidth,
        height: dimensions.physicalHeight,
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

        socket.emit('command', {
            command: userInput
        });

        // Clear the input after submission
        inputElement.value = '';
    };
}

// Setup navigation buttons
function setupNavigationButtons() {
    document.getElementById('btn-left').addEventListener('click', function() {
        sendKeyToServer('ArrowLeft');
    });
    document.getElementById('btn-right').addEventListener('click', function() {
        sendKeyToServer('ArrowRight');
    });
    document.getElementById('btn-zoom-in').addEventListener('click', function() {
        sendKeyToServer('ArrowUp');
    });
    document.getElementById('btn-zoom-out').addEventListener('click', function() {
        sendKeyToServer('ArrowDown');
    });
    document.getElementById('btn-up').addEventListener('click', function() {
        sendKeyToServer('PageUp');
    });
    document.getElementById('btn-down').addEventListener('click', function() {
        sendKeyToServer('PageDown');
    });
}

// Setup clear output button
function setupClearButton() {
    document.getElementById('clearOutput').addEventListener('click', function() {
        socket.emit('clear_output');
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
            sendKeyToServer(event.key);
            return;
        }

        // If it's not an arrow key and not a control combo
        if (!event.ctrlKey && !event.metaKey && !event.altKey) {
            // Get the command input box
            const commandInput = document.getElementById('user_input');

            // If we're not already focused on the input or a text element
            if (document.activeElement !== commandInput &&
                !(document.activeElement.tagName === 'INPUT' && document.activeElement.type === 'text') &&
                document.activeElement.tagName !== 'TEXTAREA') {

                // Focus the input
                commandInput.focus();
            }
        }

        // Toggle FPS counter with F key - Fixed bug: 'e' was used instead of 'event'
        if (event.key === 'f' && event.ctrlKey) {
            event.preventDefault();
            const fpsElement = document.getElementById('fpsCounter');
            if (fpsElement) {
                fpsElement.style.display = fpsElement.style.display === 'none' ? 'block' : 'none';
            }
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
            socket.emit('refresh_image');
        }
    });
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

    // Apply initial resize and request image
    updateCanvasSize();

    // Initialize the performance monitor
    setTimeout(() => {
        performanceMonitor.init();
    }, 500);
});