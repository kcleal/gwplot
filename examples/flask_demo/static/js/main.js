// Performance monitoring system
const performanceMonitor = {
    frameCount: 0,
    lastFpsUpdate: 0,
    frameRateElement: null,
    renderTimes: [],
    networkTimes: [],

    init: function() {
        // Create FPS display element if it doesn't exist
        if (!this.frameRateElement) {
            this.frameRateElement = document.createElement('div');
            this.frameRateElement.id = 'fpsCounter';
            this.frameRateElement.style.position = 'fixed'; // Use fixed instead of absolute
            this.frameRateElement.style.top = '10px';
            this.frameRateElement.style.right = '10px';
            this.frameRateElement.style.backgroundColor = 'rgba(0, 0, 0, 0.7)'; // More visible
            this.frameRateElement.style.color = 'white';
            this.frameRateElement.style.padding = '8px';
            this.frameRateElement.style.borderRadius = '4px';
            this.frameRateElement.style.fontFamily = 'monospace';
            this.frameRateElement.style.fontSize = '14px';
            this.frameRateElement.style.zIndex = '9999'; // Very high z-index
            this.frameRateElement.style.pointerEvents = 'none'; // Don't block mouse events
            this.frameRateElement.textContent = "Initializing performance monitor...";
            document.body.appendChild(this.frameRateElement);

            // Log to console for debugging
            console.log("Performance monitor initialized - stats display created");
        }

        // Start the monitoring loop
        this.update();
    },

    // Record a frame render
    recordFrame: function() {
        this.frameCount++;
    },

    // Record network request time (in ms)
    recordNetworkTime: function(time) {
        this.networkTimes.push(time);
        if (this.networkTimes.length > 60) {
            this.networkTimes.shift();
        }
    },

    // Record render time (in ms)
    recordRenderTime: function(time) {
        this.renderTimes.push(time);
        if (this.renderTimes.length > 60) {
            this.renderTimes.shift();
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
                Queue: ${eventQueue.queue.length}
            `;

            this.frameCount = 0;
            this.lastFpsUpdate = now;
        }

        requestAnimationFrame(() => this.update());
    }
};

// Event queue implementation for smoother interaction
const eventQueue = {
    queue: [],
    processing: false,
    maxBatchSize: 3,
    lastProcessTime: 0,
    minProcessInterval: 16, // Target ~60fps (1000ms/60 ≈ 16ms)

    // Add an event to the queue
    enqueue: function(eventType, eventData) {
        // For sequential arrow keys, update the latest one rather than adding a new event
        if (eventType === 'key' && this.queue.length > 0) {
            const lastEvent = this.queue[this.queue.length - 1];
            if (lastEvent.type === 'key' && lastEvent.data.key === eventData.key) {
                // Just update the timestamp to keep it fresh
                lastEvent.timestamp = Date.now();
                return;
            }
        }

        // Add the event to the queue
        this.queue.push({
            type: eventType,
            data: eventData,
            timestamp: Date.now()
        });

        // Start processing if not already doing so
        if (!this.processing) {
            this.processQueue();
        }
    },

    // Process events in the queue
    processQueue: function() {
        if (this.queue.length === 0) {
            this.processing = false;
            return;
        }

        const now = performance.now();

        // Enforce minimum processing interval to maintain consistent frame rate
        if (now - this.lastProcessTime < this.minProcessInterval) {
            // Schedule next processing attempt
            requestAnimationFrame(() => this.processQueue());
            return;
        }

        this.processing = true;
        this.lastProcessTime = now;

        // Take the next event from the queue
        const event = this.queue.shift();

        // Handle the event based on its type
        switch(event.type) {
            case 'key':
                this.handleKeyEvent(event.data.key);
                break;
            case 'mouse':
                this.handleMouseEvent(event.data);
                break;
            case 'resize':
                this.handleResizeEvent(event.data);
                break;
            default:
                console.error('Unknown event type:', event.type);
                this.processNextEvent();
        }
    },

    // Process the next event after the current one completes
    processNextEvent: function() {
        // Use requestAnimationFrame to sync with browser rendering cycle
        requestAnimationFrame(() => this.processQueue());
    },

    // Handle key events
    handleKeyEvent: function(key) {
        const startTime = performance.now();

        fetch('/key-event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify({ key: key })
        })
        .then(response => {
            const networkTime = performance.now() - startTime;
            performanceMonitor.recordNetworkTime(networkTime);

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json().then(data => {
                    if (data.image && data.image !== '') {
                        updateCanvas(data.image);
                    }
                    // Only fetch output if we're not processing too many events
                    if (this.queue.length < 5) {
                        fetchOutput();
                    }
                    this.processNextEvent();
                });
            } else if (contentType && contentType.includes('image/')) {
                return response.blob().then(blob => {
                    const imageUrl = URL.createObjectURL(blob);
                    updateCanvas(imageUrl);
                    // Only fetch output if we're not processing too many events
                    if (this.queue.length < 5) {
                        fetchOutput();
                    }
                    this.processNextEvent();
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.processNextEvent();
        });
    },

    // Handle mouse events
    handleMouseEvent: function(mouseData) {
        fetch('/mouse-event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                x: mouseData.x,
                y: mouseData.y,
                button: mouseData.button,
                action: mouseData.action,
                nocache: new Date().getTime()
            })
        })
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json().then(data => {
                    if (data.image && data.image !== '') {
                        updateCanvas(data.image);
                    }
                    fetchOutput();
                    this.processNextEvent();
                });
            } else if (contentType && contentType.includes('image/')) {
                return response.blob().then(blob => {
                    const imageUrl = URL.createObjectURL(blob);
                    updateCanvas(imageUrl);
                    fetchOutput();
                    this.processNextEvent();
                });
            }
        })
        .catch(error => {
            console.error('Error sending mouse event:', error);
            this.processNextEvent();
        });
    },

    // Handle resize events
    handleResizeEvent: function(sizeData) {
        fetch('/update-canvas-size', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                width: sizeData.width,
                height: sizeData.height,
                dpr: sizeData.dpr
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server updated canvas size:', data);
            loadImage(); // Load image after size update
            this.processNextEvent();
        })
        .catch(error => {
            console.error('Error sending canvas size:', error);
            this.processNextEvent();
        });
    }
};

// Enhanced double buffering with preloading
const canvasManager = {
    frontCanvas: null,
    backCanvas: null,
    loadingCanvas: null,
    currentCanvas: null,
    pendingImages: [],
    isLoading: false,
    lastImageTimestamp: 0,

    init: function() {
        this.frontCanvas = document.getElementById('genomePlot');
        this.backCanvas = document.createElement('canvas');
        this.loadingCanvas = document.createElement('canvas');
        this.currentCanvas = this.frontCanvas;

        // Apply hardware acceleration hints where available
        this.frontCanvas.style.willChange = 'transform';
        this.frontCanvas.style.transform = 'translateZ(0)'; // Hint for GPU acceleration
    },

    updateCanvas: function(imageData) {
        performanceMonitor.recordFrame();

        // Store the URL for settings changes
        this.lastImageUrl = imageData;

        // Add to pending images if we're already loading one
        if (this.isLoading) {
            // Only keep the latest image if we have a backlog
            if (this.pendingImages.length > 0) {
                this.pendingImages = [imageData];
            } else {
                this.pendingImages.push(imageData);
            }
            return;
        }

        const renderStartTime = performance.now();
        this.isLoading = true;
        this.lastImageTimestamp = renderStartTime;

        const img = new Image();

        // Use decode() for faster image processing where available
        img.onload = () => {
            // Use image.decode() API if available for faster decoding
            const processImage = () => {
                // Set dimensions and draw to the loading canvas
                this.loadingCanvas.width = img.width;
                this.loadingCanvas.height = img.height;

                const ctx = this.loadingCanvas.getContext('2d', {
                    alpha: false,
                    desynchronized: true // Use desynchronized for lower latency where supported
                });

                // Clear the canvas
                ctx.clearRect(0, 0, this.loadingCanvas.width, this.loadingCanvas.height);

                // Apply saturation enhancement for JPEG images
                if (imageData.includes("jpeg") || imageData.includes("jpg")) {
                    // Get user settings or use defaults
                    const settings = window.imageEnhancementSettings || { saturation: 0.3, contrast: 0.2 };

                    // Save the current canvas state
                    ctx.save();

                    // First draw the image normally
                    ctx.drawImage(img, 0, 0);

                    // Apply saturation enhancement
                    if (settings.saturation > 0) {
                        ctx.globalCompositeOperation = 'saturation';
                        ctx.fillStyle = `rgba(0,0,255,${settings.saturation})`;
                        ctx.fillRect(0, 0, this.loadingCanvas.width, this.loadingCanvas.height);
                    }

                    // Apply contrast enhancement
                    if (settings.contrast > 0) {
                        ctx.globalCompositeOperation = 'overlay';
                        ctx.fillStyle = `rgba(128,128,128,${settings.contrast})`;
                        ctx.fillRect(0, 0, this.loadingCanvas.width, this.loadingCanvas.height);
                    }

                    // Restore the canvas state
                    ctx.restore();
                } else {
                    // For non-JPEG images, just draw normally
                    ctx.drawImage(img, 0, 0);
                }

                // Swap canvases using requestAnimationFrame to align with browser render cycle
                requestAnimationFrame(() => {
                    // Swap canvases
                    const temp = this.currentCanvas;
                    this.currentCanvas = this.loadingCanvas;
                    this.loadingCanvas = temp;

                    // If front canvas changed, update the DOM
                    if (this.currentCanvas !== this.frontCanvas) {
                        this.frontCanvas.width = this.currentCanvas.width;
                        this.frontCanvas.height = this.currentCanvas.height;
                        const frontCtx = this.frontCanvas.getContext('2d', {
                            alpha: false,
                            desynchronized: true
                        });
                        frontCtx.imageSmoothingEnabled = false;
                        frontCtx.drawImage(this.currentCanvas, 0, 0);
                    }

                    const renderTime = performance.now() - renderStartTime;
                    performanceMonitor.recordRenderTime(renderTime);

                    console.log(`Image rendered: ${img.width}x${img.height} in ${renderTime.toFixed(1)}ms`);
                    adjustOutputBoxHeight();

                    // Clean up the blob URL if needed
                    if (imageData.startsWith('blob:')) {
                        URL.revokeObjectURL(imageData);
                    }

                    // Process any pending images
                    this.isLoading = false;
                    if (this.pendingImages.length > 0) {
                        const nextImage = this.pendingImages.shift();
                        this.updateCanvas(nextImage);
                    }
                });
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
            this.isLoading = false;

            // Try next image if any
            if (this.pendingImages.length > 0) {
                const nextImage = this.pendingImages.shift();
                this.updateCanvas(nextImage);
            }
        };

        // Set attributes for faster loading
        img.decoding = 'async';
        img.importance = 'high';
        img.fetchPriority = 'high';
        img.src = imageData;
    }
};

// Calculate canvas dimensions accounting for device pixel ratio
function getCanvasDimensions() {
    // Get device pixel ratio
    const dpr = window.devicePixelRatio || 1;

    // Visual dimensions (CSS pixels)
    const cssWidth = Math.max(window.innerWidth - 20, 300);
    const cssHeight = Math.max(Math.floor(window.innerHeight * 0.6), 300);

    // Physical dimensions (actual pixels, accounting for high DPI)
    const physicalWidth = Math.round(cssWidth * dpr);
    const physicalHeight = Math.round(cssHeight * dpr);

    return {
        cssWidth,           // Size for display (CSS)
        cssHeight,          // Size for display (CSS)
        physicalWidth,      // Actual pixel dimensions for rendering
        physicalHeight,     // Actual pixel dimensions for rendering
        dpr                 // Device pixel ratio
    };
}

// Function to ensure output box takes up remaining space
function adjustOutputBoxHeight() {
    const genomePlot = document.getElementById('genomePlot');
    const commandNav = document.querySelector('.command-nav-container');

    // Calculate available height
    const windowHeight = window.innerHeight;
    const usedHeight = genomePlot.offsetHeight + commandNav.offsetHeight + 40; // 40px for margins/padding

    // Set the outputContainer to use the remaining space
    const outputContainer = document.getElementById('outputContainer');
    outputContainer.style.height = (windowHeight - usedHeight) + 'px';
}

// Updated function to use the event queue
function sendKeyToServer(key) {
    eventQueue.enqueue('key', { key: key });
}

// Updated function to use canvas manager
function updateCanvas(imageData) {
    canvasManager.updateCanvas(imageData);
}

document.getElementById('commandForm').onsubmit = function(event) {
    event.preventDefault();
    var inputElement = document.getElementById('user_input');
    var userInput = inputElement.value;

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_input=' + encodeURIComponent(userInput)
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (data.image && data.image !== '') {
                    updateCanvas(data.image);
                }
                // Clear the input after submission
                inputElement.value = '';
                fetchOutput();
            });
        } else if (contentType && contentType.includes('image/')) {
            return response.blob().then(blob => {
                const imageUrl = URL.createObjectURL(blob);
                updateCanvas(imageUrl);
                // Clear the input after submission
                inputElement.value = '';
                fetchOutput();
            });
        }
    })
    .catch(error => console.error('Error:', error));
};

// Setup navigation buttons
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

// Setup clear output button
document.getElementById('clearOutput').addEventListener('click', function() {
    // Clear the server-side log
    fetch('/clear-output', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('outputBox').textContent = '';
        }
    })
    .catch(error => console.error('Error clearing output:', error));
});

function resizeCanvas() {
    const canvas = document.getElementById('genomePlot');
    const dimensions = getCanvasDimensions();

    // Set CSS dimensions for display size
    canvas.style.width = dimensions.cssWidth + 'px';
    canvas.style.height = dimensions.cssHeight + 'px';

    // Tell the server to generate a high-resolution image
    eventQueue.enqueue('resize', {
        width: dimensions.physicalWidth,
        height: dimensions.physicalHeight,
        dpr: dimensions.dpr
    });

    console.log(`Canvas display size: ${dimensions.cssWidth}x${dimensions.cssHeight},
                 Physical size: ${dimensions.physicalWidth}x${dimensions.physicalHeight},
                 DPR: ${dimensions.dpr}`);

    // Also adjust the output box height
    adjustOutputBoxHeight();
}

function loadImage() {
    fetch('/display_image?nocache=' + new Date().getTime())
        .then(response => {
            // Check if the response is JSON or binary
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json().then(data => updateCanvas(data.image));
            } else if (contentType && contentType.includes('image/')) {
                // For binary image, convert to object URL
                return response.blob().then(blob => {
                    const imageUrl = URL.createObjectURL(blob);
                    updateCanvas(imageUrl);
                });
            }
        })
        .catch(error => console.error('Error loading image:', error));
}

// Variables to store previous output length to prevent scroll jumping
let previousOutputLength = 0;
let userHasScrolled = false;

// Function to fetch and update the output box with better scroll handling
function fetchOutput() {
    // Save current scroll position and check if user has scrolled up
    const outputBox = document.getElementById('outputBox');
    const isScrolledToBottom = (outputBox.scrollHeight - outputBox.clientHeight) <= (outputBox.scrollTop + 5);

    fetch('/get-output')
        .then(response => response.json())
        .then(data => {
            // Check if content actually changed before updating
            if (data.output.length !== previousOutputLength) {
                outputBox.textContent = data.output;
                previousOutputLength = data.output.length;

                // Only auto-scroll if user was already at the bottom
                if (isScrolledToBottom) {
                    outputBox.scrollTop = outputBox.scrollHeight;
                }
            }
        })
        .catch(error => console.error('Error fetching output:', error));
}

// Manual scroll detection to control auto-scrolling behavior
document.getElementById('outputBox').addEventListener('scroll', function() {
    const outputBox = document.getElementById('outputBox');
    userHasScrolled = true;

    // Check if scrolled to bottom
    if ((outputBox.scrollHeight - outputBox.clientHeight) <= (outputBox.scrollTop + 5)) {
        userHasScrolled = false;
    }
});

// Set up mouse event handling for the canvas
document.addEventListener('DOMContentLoaded', function() {
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
        handleMouseEvent(event, 'wheel', wheelAction);
    });

    function handleMouseEvent(event, button, action) {
        // Get canvas and its dimensions
        const canvas = event.target;
        const rect = canvas.getBoundingClientRect();

        // Calculate mouse position relative to canvas in CSS pixels
        const cssX = event.clientX - rect.left;
        const cssY = event.clientY - rect.top;

        // Convert to canvas coordinates
        const canvasX = Math.round(cssX * (canvas.width / rect.width));
        const canvasY = Math.round(cssY * (canvas.height / rect.height));

        console.log(`Mouse ${button} ${action} at canvas coordinates: ${canvasX}, ${canvasY}`);

        // Send to event queue instead of directly to server
        eventQueue.enqueue('mouse', {
            x: canvasX,
            y: canvasY,
            button: button,
            action: action
        });
    }
});

// Set up a polling mechanism to refresh the output periodically
let outputPollInterval;
function startOutputPolling() {
    // Poll at a slower rate (1 second) to reduce jitter
    outputPollInterval = setInterval(fetchOutput, 1000);
}

// Handle canvas resizing and initial load
document.addEventListener('DOMContentLoaded', function() {
    console.log(`Device Pixel Ratio: ${window.devicePixelRatio}`);

    // Initialize the canvas manager
    canvasManager.init();

    // Apply resize and fetch initial image
    resizeCanvas();

    // Start polling for output updates with reduced frequency during high activity
    startOutputPolling();

    // Add debounce to avoid too many resize events
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            resizeCanvas();
        }, 250); // Wait 250ms after resize finishes
    });

    // Add optimization for visibility changes - don't process events when tab is hidden
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden, pause event processing to save resources
            if (outputPollInterval) {
                clearInterval(outputPollInterval);
                outputPollInterval = null;
            }
        } else {
            // Page is visible again, resume event processing
            if (!outputPollInterval) {
                startOutputPolling();
            }
            // Force a refresh of the canvas
            loadImage();
        }
    });

    // Forward keystrokes to command box (except arrow keys)
    document.addEventListener('keydown', function(event) {
        const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];

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
    });
});


// Initialize everything when the DOM is fully loaded
function initializeApp() {

    // Initialize the performance monitor with a slight delay to ensure DOM is ready
    setTimeout(() => {
        console.log("Initializing performance monitor...");
        performanceMonitor.init();
        console.log("Performance monitor initialization complete");
    }, 500);

    // Add keyboard handling for FPS display toggle
    document.addEventListener('keydown', function(e) {
        // Toggle FPS counter with F key
        if (e.key === 'f' && e.ctrlKey) {
            e.preventDefault();
            const fpsElement = document.getElementById('fpsCounter');
            if (fpsElement) {
                fpsElement.style.display = fpsElement.style.display === 'none' ? 'block' : 'none';
            }
        }
    });

    // Detect support for various performance features
    const features = {
        requestAnimationFrame: window.requestAnimationFrame !== undefined,
        imageDecodeAPI: 'decode' in new Image(),
        offscreenCanvas: window.OffscreenCanvas !== undefined,
        desynchronized: true, // Assume supported, browser will fall back if not
        devicePixelRatio: window.devicePixelRatio || 1
    };

    console.log("Browser performance features:", features);
}

// Run initialization
document.addEventListener('DOMContentLoaded', initializeApp);