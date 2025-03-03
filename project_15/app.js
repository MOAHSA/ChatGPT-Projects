// PixelMaster - Web Drawing Application
// Main Application Logic

// Global app state
const app = {
    canvas: null,
    ctx: null,
    canvasOverlay: null,
    overlayCtx: null,
    width: 1000,
    height: 800,
    zoom: 1,
    currentTool: null,
    primaryColor: '#000000',
    secondaryColor: '#ffffff',
    layers: [],
    activeLayerIndex: 0,
    history: [],
    historyIndex: -1,
    maxHistorySteps: 50,
    isDrawing: false,
    startX: 0,
    startY: 0,
    previousX: 0,
    previousY: 0,
    selectedElement: null,
    clipboard: null,
    modalOpen: false
};

// Initialize the application
function initApp() {
    // Initialize canvas
    app.canvas = document.getElementById('canvas');
    app.ctx = app.canvas.getContext('2d');
    app.canvasOverlay = document.getElementById('canvas-overlay');
    app.overlayCtx = app.canvasOverlay.getContext('2d');

    // Set initial canvas size
    resizeCanvas(app.width, app.height);

    // Initialize tools
    initTools();

    // Create default layer
    createNewLayer('Background');

    // Set initial active tool (Brush)
    setActiveTool('brush-tool');

    // Set up event listeners
    setupEventListeners();

    // Update UI elements
    updateLayersPanel();
    updateHistoryPanel();

    // Render the canvas
    render();
}

// Canvas setup and rendering functions
function resizeCanvas(width, height) {
    app.width = width;
    app.height = height;

    // Set canvas dimensions
    app.canvas.width = width;
    app.canvas.height = height;
    app.canvasOverlay.width = width;
    app.canvasOverlay.height = height;

    // Update canvas info in status bar
    document.getElementById('canvas-dimensions').textContent = `${width} × ${height} px`;

    // Clear canvas with white background
    app.ctx.fillStyle = 'white';
    app.ctx.fillRect(0, 0, width, height);

    // Update canvas container to ensure proper positioning
    updateCanvasPosition();

    // Render the canvas
    render();
}

// Add this new function to synchronize canvas positions
function updateCanvasPosition() {
    const canvasContainer = document.querySelector('.canvas-container');

    // Position the overlay exactly on top of the main canvas
    app.canvasOverlay.style.position = 'absolute';
    app.canvasOverlay.style.top = `${app.canvas.offsetTop}px`;
    app.canvasOverlay.style.left = `${app.canvas.offsetLeft}px`;

    // Apply the same transform to both canvases
    const transform = `scale(${app.zoom})`;
    app.canvas.style.transform = transform;
    app.canvasOverlay.style.transform = transform;
}

// Update the setZoom function to maintain alignment
function setZoom(zoomLevel) {
    // Clamp zoom between 0.1 and 5
    app.zoom = Math.max(0.1, Math.min(5, zoomLevel));

    // Update zoom display
    document.getElementById('zoom-level').textContent = `${Math.round(app.zoom * 100)}%`;

    // Update canvas position with new zoom
    updateCanvasPosition();
}
function render() {
    // Clear the main canvas
    app.ctx.clearRect(0, 0, app.width, app.height);

    // Draw all visible layers from bottom to top
    app.layers.forEach(layer => {
        if (layer.visible) {
            app.ctx.drawImage(layer.canvas, 0, 0);
        }
    });
}
function debounce(func, wait) {
    let timeout;
    return function () {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

// Event listener setup
function setupEventListeners() {
    // Tool selection
    document.querySelectorAll('.tool').forEach(tool => {
        tool.addEventListener('click', (e) => {
            const toolId = e.currentTarget.id;
            setActiveTool(toolId);
        });
    });

    // Canvas mouse events
    app.canvasOverlay.addEventListener('mousedown', handleMouseDown);
    app.canvasOverlay.addEventListener('mousemove', handleMouseMove);
    app.canvasOverlay.addEventListener('mouseup', handleMouseUp);
    app.canvasOverlay.addEventListener('mouseleave', handleMouseUp);
    handleCanvasScroll();
    window.addEventListener('resize', debounce(() => {
        updateCanvasPosition();
    }, 100));
    // Update cursor coordinates
    app.canvasOverlay.addEventListener('mousemove', updateCursorCoordinates);

    // Color picker events
    document.getElementById('primary-color').addEventListener('click', () => {
        document.getElementById('color-picker').click();
    });

    document.getElementById('secondary-color').addEventListener('click', () => {
        const temp = app.primaryColor;
        app.primaryColor = app.secondaryColor;
        app.secondaryColor = temp;
        updateColorDisplay();
    });

    document.getElementById('color-picker').addEventListener('input', (e) => {
        app.primaryColor = e.target.value;
        updateColorDisplay();
        updateToolProperties();
    });

    // Layer panel events
    document.getElementById('add-layer').addEventListener('click', () => {
        createNewLayer(`Layer ${app.layers.length + 1}`);
        updateLayersPanel();
        saveState();
    });

    document.getElementById('delete-selected-layer').addEventListener('click', () => {
        if (app.layers.length > 1) {
            app.layers.splice(app.activeLayerIndex, 1);
            app.activeLayerIndex = Math.min(app.activeLayerIndex, app.layers.length - 1);
            updateLayersPanel();
            render();
            saveState();
        }
    });

    // Menu events - File
    document.getElementById('new-file').addEventListener('click', createNewFile);
    document.getElementById('open-file').addEventListener('click', openFile);
    document.getElementById('save-file').addEventListener('click', saveFile);
    document.getElementById('export-file').addEventListener('click', exportFile);

    // Menu events - Edit
    document.getElementById('undo').addEventListener('click', undo);
    document.getElementById('redo').addEventListener('click', redo);
    document.getElementById('cut').addEventListener('click', cutSelection);
    document.getElementById('copy').addEventListener('click', copySelection);
    document.getElementById('paste').addEventListener('click', pasteSelection);

    // Menu events - Image
    document.getElementById('resize-image').addEventListener('click', openResizeModal);
    document.getElementById('crop-image').addEventListener('click', cropImage);
    document.getElementById('rotate-image').addEventListener('click', rotateImage);
    document.getElementById('flip-image').addEventListener('click', flipImage);

    // Menu events - Layer
    document.getElementById('new-layer').addEventListener('click', () => {
        createNewLayer(`Layer ${app.layers.length + 1}`);
        updateLayersPanel();
        saveState();
    });
    document.getElementById('duplicate-layer').addEventListener('click', duplicateCurrentLayer);
    document.getElementById('delete-layer').addEventListener('click', () => {
        if (app.layers.length > 1) {
            app.layers.splice(app.activeLayerIndex, 1);
            app.activeLayerIndex = Math.min(app.activeLayerIndex, app.layers.length - 1);
            updateLayersPanel();
            render();
            saveState();
        }
    });
    document.getElementById('merge-layers').addEventListener('click', mergeLayers);

    // Menu events - Help
    document.getElementById('about').addEventListener('click', showAbout);
    document.getElementById('shortcuts').addEventListener('click', showShortcuts);

    // Zoom controls
    document.getElementById('zoom-in').addEventListener('click', () => {
        setZoom(app.zoom + 0.1);
    });

    document.getElementById('zoom-out').addEventListener('click', () => {
        setZoom(app.zoom - 0.1);
    });

    // Modal events
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    document.getElementById('cancel-resize').addEventListener('click', closeModal);
    document.getElementById('apply-resize').addEventListener('click', applyResize);

    document.getElementById('cancel-text').addEventListener('click', closeModal);
    document.getElementById('add-text').addEventListener('click', addTextToCanvas);

    // Handle keyboard shortcuts
    window.addEventListener('keydown', handleKeyDown);

    // Maintain aspect ratio in resize modal
    const widthInput = document.getElementById('width-input');
    const heightInput = document.getElementById('height-input');
    const aspectRatioCheckbox = document.getElementById('maintain-aspect-ratio');

    widthInput.addEventListener('input', () => {
        if (aspectRatioCheckbox.checked) {
            const ratio = app.height / app.width;
            heightInput.value = Math.round(widthInput.value * ratio);
        }
    });

    heightInput.addEventListener('input', () => {
        if (aspectRatioCheckbox.checked) {
            const ratio = app.width / app.height;
            widthInput.value = Math.round(heightInput.value * ratio);
        }
    });

    // File input change
    document.getElementById('file-input').addEventListener('change', handleFileInput);
}

// Tool functions
function setActiveTool(toolId) {
    // Remove active class from all tools
    document.querySelectorAll('.tool').forEach(tool => {
        tool.classList.remove('active');
    });

    // Add active class to selected tool
    document.getElementById(toolId).classList.add('active');

    // Set current tool
    app.currentTool = toolId;

    // Update properties panel for the selected tool
    updateToolProperties();

    // Clear overlay canvas
    app.overlayCtx.clearRect(0, 0, app.width, app.height);
}

function updateToolProperties() {
    const propertiesContent = document.getElementById('properties-content');
    propertiesContent.innerHTML = '';

    switch (app.currentTool) {
        case 'brush-tool':
            propertiesContent.innerHTML = `
                <div class="tool-property">
                    <label for="brush-size">Brush Size:</label>
                    <input type="range" id="brush-size" min="1" max="100" value="${tools.brush.size}">
                    <span>${tools.brush.size}px</span>
                </div>
                <div class="tool-property">
                    <label for="brush-opacity">Opacity:</label>
                    <input type="range" id="brush-opacity" min="1" max="100" value="${tools.brush.opacity * 100}">
                    <span>${Math.round(tools.brush.opacity * 100)}%</span>
                </div>
                <div class="tool-property">
                    <label>Brush Preview:</label>
                    <div class="brush-preview">
                        <div class="brush-preview-dot" style="width: ${tools.brush.size}px; height: ${tools.brush.size}px; opacity: ${tools.brush.opacity}; background-color: ${app.primaryColor}"></div>
                    </div>
                </div>
            `;

            // Add event listeners to update brush properties
            document.getElementById('brush-size').addEventListener('input', (e) => {
                tools.brush.size = parseInt(e.target.value);
                e.target.nextElementSibling.textContent = `${tools.brush.size}px`;
                updateBrushPreview();
            });

            document.getElementById('brush-opacity').addEventListener('input', (e) => {
                tools.brush.opacity = parseInt(e.target.value) / 100;
                e.target.nextElementSibling.textContent = `${Math.round(tools.brush.opacity * 100)}%`;
                updateBrushPreview();
            });
            break;

        case 'eraser-tool':
            propertiesContent.innerHTML = `
                <div class="tool-property">
                    <label for="eraser-size">Eraser Size:</label>
                    <input type="range" id="eraser-size" min="1" max="100" value="${tools.eraser.size}">
                    <span>${tools.eraser.size}px</span>
                </div>
                <div class="tool-property">
                    <label for="eraser-hardness">Hardness:</label>
                    <input type="range" id="eraser-hardness" min="0" max="100" value="${tools.eraser.hardness * 100}">
                    <span>${Math.round(tools.eraser.hardness * 100)}%</span>
                </div>
            `;

            // Add event listeners to update eraser properties
            document.getElementById('eraser-size').addEventListener('input', (e) => {
                tools.eraser.size = parseInt(e.target.value);
                e.target.nextElementSibling.textContent = `${tools.eraser.size}px`;
            });

            document.getElementById('eraser-hardness').addEventListener('input', (e) => {
                tools.eraser.hardness = parseInt(e.target.value) / 100;
                e.target.nextElementSibling.textContent = `${Math.round(tools.eraser.hardness * 100)}%`;
            });
            break;

        case 'shape-tool':
            propertiesContent.innerHTML = `
                <div class="tool-property">
                    <label for="shape-type">Shape Type:</label>
                    <select id="shape-type">
                        <option value="rectangle" ${tools.shape.type === 'rectangle' ? 'selected' : ''}>Rectangle</option>
                        <option value="ellipse" ${tools.shape.type === 'ellipse' ? 'selected' : ''}>Ellipse</option>
                        <option value="line" ${tools.shape.type === 'line' ? 'selected' : ''}>Line</option>
                        <option value="polygon" ${tools.shape.type === 'polygon' ? 'selected' : ''}>Polygon</option>
                    </select>
                </div>
                <div class="tool-property">
                    <label for="shape-stroke-width">Stroke Width:</label>
                    <input type="range" id="shape-stroke-width" min="1" max="50" value="${tools.shape.strokeWidth}">
                    <span>${tools.shape.strokeWidth}px</span>
                </div>
                <div class="tool-property">
                    <label>
                        <input type="checkbox" id="shape-fill" ${tools.shape.fill ? 'checked' : ''}>
                        Fill Shape
                    </label>
                </div>
            `;

            // Add event listeners to update shape properties
            document.getElementById('shape-type').addEventListener('change', (e) => {
                tools.shape.type = e.target.value;
            });

            document.getElementById('shape-stroke-width').addEventListener('input', (e) => {
                tools.shape.strokeWidth = parseInt(e.target.value);
                e.target.nextElementSibling.textContent = `${tools.shape.strokeWidth}px`;
            });

            document.getElementById('shape-fill').addEventListener('change', (e) => {
                tools.shape.fill = e.target.checked;
            });
            break;

        // Add other tools' properties here...
        case 'text-tool':
            propertiesContent.innerHTML = `
                <div class="tool-property">
                    <label for="font-family">Font:</label>
                    <select id="font-family">
                        <option value="Arial" ${tools.text.font === 'Arial' ? 'selected' : ''}>Arial</option>
                        <option value="Times New Roman" ${tools.text.font === 'Times New Roman' ? 'selected' : ''}>Times New Roman</option>
                        <option value="Courier New" ${tools.text.font === 'Courier New' ? 'selected' : ''}>Courier New</option>
                    </select>
                </div>
                <div class="tool-property">
                    <label for="font-size">Size:</label>
                    <input type="number" id="font-size" min="8" max="144" value="${tools.text.size}">
                </div>
                <div class="tool-property">
                    <label>
                        <input type="checkbox" id="font-bold" ${tools.text.bold ? 'checked' : ''}>
                        Bold
                    </label>
                    <label>
                        <input type="checkbox" id="font-italic" ${tools.text.italic ? 'checked' : ''}>
                        Italic
                    </label>
                </div>
            `;

            // Add event listeners for text properties
            document.getElementById('font-family').addEventListener('change', (e) => {
                tools.text.font = e.target.value;
            });
            document.getElementById('font-size').addEventListener('input', (e) => {
                tools.text.size = parseInt(e.target.value);
            });
            document.getElementById('font-bold').addEventListener('change', (e) => {
                tools.text.bold = e.target.checked;
            });
            document.getElementById('font-italic').addEventListener('change', (e) => {
                tools.text.italic = e.target.checked;
            });
            break;

        case 'gradient-tool':
            propertiesContent.innerHTML = `
                <div class="tool-property">
                    <label for="gradient-type">Type:</label>
                    <select id="gradient-type">
                        <option value="linear" ${tools.gradient.type === 'linear' ? 'selected' : ''}>Linear</option>
                        <option value="radial" ${tools.gradient.type === 'radial' ? 'selected' : ''}>Radial</option>
                    </select>
                </div>
                <div class="tool-property">
                    <label for="gradient-start-color">Start Color:</label>
                    <input type="color" id="gradient-start-color" value="${tools.gradient.startColor}">
                </div>
                <div class="tool-property">
                    <label for="gradient-end-color">End Color:</label>
                    <input type="color" id="gradient-end-color" value="${tools.gradient.endColor}">
                </div>
            `;

            // Add event listeners for gradient properties
            document.getElementById('gradient-type').addEventListener('change', (e) => {
                tools.gradient.type = e.target.value;
            });
            document.getElementById('gradient-start-color').addEventListener('input', (e) => {
                tools.gradient.startColor = e.target.value;
            });
            document.getElementById('gradient-end-color').addEventListener('input', (e) => {
                tools.gradient.endColor = e.target.value;
            });
            break;

        case 'fill-tool':
            propertiesContent.innerHTML = `
                <div class="tool-property">
                    <label for="fill-tolerance">Tolerance:</label>
                    <input type="range" id="fill-tolerance" min="0" max="255" value="${tools.fill.tolerance}">
                    <span>${tools.fill.tolerance}</span>
                </div>
            `;

            document.getElementById('fill-tolerance').addEventListener('input', (e) => {
                tools.fill.tolerance = parseInt(e.target.value);
                e.target.nextElementSibling.textContent = tools.fill.tolerance;
            });
            break;
    }
}
function updateBrushPreview() {
    const previewDot = document.querySelector('.brush-preview-dot');
    if (previewDot) {
        previewDot.style.width = `${tools.brush.size}px`;
        previewDot.style.height = `${tools.brush.size}px`;
        previewDot.style.opacity = tools.brush.opacity;
        previewDot.style.backgroundColor = app.primaryColor;
    }
}

// Color functions
function updateColorDisplay() {
    document.getElementById('primary-color').style.backgroundColor = app.primaryColor;
    document.getElementById('secondary-color').style.backgroundColor = app.secondaryColor;
}

// Modal functions
function openModal(modalId) {
    app.modalOpen = true;
    const modal = document.getElementById(modalId);
    modal.style.display = 'flex';

    if (modalId === 'resize-modal') {
        document.getElementById('width-input').value = app.width;
        document.getElementById('height-input').value = app.height;
    }
}

function closeModal() {
    app.modalOpen = false;
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

function openResizeModal() {
    openModal('resize-modal');
}

function applyResize() {
    const width = parseInt(document.getElementById('width-input').value);
    const height = parseInt(document.getElementById('height-input').value);

    if (width > 0 && height > 0 && (width !== app.width || height !== app.height)) {
        saveState();
        resizeCanvas(width, height);

        // Resize all layer canvases
        app.layers.forEach(layer => {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = width;
            tempCanvas.height = height;
            const tempCtx = tempCanvas.getContext('2d');

            // Draw original content
            tempCtx.drawImage(layer.canvas, 0, 0, width, height);

            // Update layer canvas
            layer.canvas.width = width;
            layer.canvas.height = height;
            layer.ctx.drawImage(tempCanvas, 0, 0);
        });

        render();
    }

    closeModal();
}

// Menu function implementations
function createNewFile() {
    if (confirm('Are you sure you want to create a new file? All unsaved changes will be lost.')) {
        // Reset app state
        app.layers = [];
        app.activeLayerIndex = 0;
        app.history = [];
        app.historyIndex = -1;

        // Reset canvas
        resizeCanvas(1000, 800);

        // Create default layer
        createNewLayer('Background');

        // Update UI
        updateLayersPanel();
        updateHistoryPanel();
    }
}

function openFile() {
    document.getElementById('file-input').click();
}

function handleFileInput(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            const img = new Image();
            img.onload = function () {
                createNewFile();

                // Resize canvas to image dimensions
                resizeCanvas(img.width, img.height);

                // Draw image on the background layer
                const activeLayer = app.layers[app.activeLayerIndex];
                activeLayer.ctx.drawImage(img, 0, 0);

                // Update canvas
                render();
                saveState();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    // Reset file input so the same file can be selected again
    e.target.value = '';
}

function saveFile() {
    // Create a temporary canvas with all visible layers
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = app.width;
    tempCanvas.height = app.height;
    const tempCtx = tempCanvas.getContext('2d');

    // Draw white background
    tempCtx.fillStyle = 'white';
    tempCtx.fillRect(0, 0, app.width, app.height);

    // Draw all visible layers
    app.layers.forEach(layer => {
        if (layer.visible) {
            tempCtx.drawImage(layer.canvas, 0, 0);
        }
    });

    // Convert to data URL and create download link
    const dataURL = tempCanvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataURL;
    a.download = 'pixelmaster_image.png';
    a.click();
}

function exportFile() {
    // Similar to saveFile but with more options for format, quality, etc.
    // For now, we'll just use the same implementation
    saveFile();
}
// Image manipulation functions
function cropImage() {
    if (app.selectedElement) {
        // Get the selected area
        const { x, y, width, height } = app.selectedElement;

        // Save current state before cropping
        saveState();

        // Create a new canvas with the cropped dimensions
        app.width = width;
        app.height = height;
        resizeCanvas(width, height);

        // Update all layers to be cropped
        app.layers.forEach(layer => {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = width;
            tempCanvas.height = height;
            const tempCtx = tempCanvas.getContext('2d');

            // Draw only the cropped portion
            tempCtx.drawImage(layer.canvas, x, y, width, height, 0, 0, width, height);

            // Update layer dimensions
            layer.canvas.width = width;
            layer.canvas.height = height;
            layer.ctx.clearRect(0, 0, width, height);
            layer.ctx.drawImage(tempCanvas, 0, 0);
        });

        // Clear selection
        app.selectedElement = null;
        app.overlayCtx.clearRect(0, 0, app.width, app.height);

        // Update UI
        render();
        updateLayersPanel();

        // Make sure canvas position is updated after cropping
        updateCanvasPosition();
        setZoom(app.zoom); // Refresh zoom to ensure proper alignment
    }
}
function rotateImage() {
    saveState();
    const angle = 90; // Rotate 90 degrees clockwise

    // Create a temporary canvas
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = app.height;
    tempCanvas.height = app.width;
    const tempCtx = tempCanvas.getContext('2d');

    // Rotate each layer
    app.layers.forEach(layer => {
        tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height);
        tempCtx.save();
        tempCtx.translate(tempCanvas.width / 2, tempCanvas.height / 2);
        tempCtx.rotate(angle * Math.PI / 180);
        tempCtx.drawImage(layer.canvas, -app.width / 2, -app.height / 2);
        tempCtx.restore();

        // Update layer dimensions
        layer.canvas.width = tempCanvas.width;
        layer.canvas.height = tempCanvas.height;
        layer.ctx.drawImage(tempCanvas, 0, 0);
    });

    // Update canvas dimensions
    const oldWidth = app.width;
    app.width = app.height;
    app.height = oldWidth;
    resizeCanvas(app.width, app.height);

    render();
}

function flipImage() {
    saveState();
    const direction = 'horizontal'; // or 'vertical'

    app.layers.forEach(layer => {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = app.width;
        tempCanvas.height = app.height;
        const tempCtx = tempCanvas.getContext('2d');

        tempCtx.save();
        if (direction === 'horizontal') {
            tempCtx.scale(-1, 1);
            tempCtx.drawImage(layer.canvas, -app.width, 0);
        } else {
            tempCtx.scale(1, -1);
            tempCtx.drawImage(layer.canvas, 0, -app.height);
        }
        tempCtx.restore();

        layer.ctx.clearRect(0, 0, app.width, app.height);
        layer.ctx.drawImage(tempCanvas, 0, 0);
    });

    render();
}

// Undo/Redo functions
function saveState() {
    // If we're not at the end of history, remove future states
    if (app.historyIndex < app.history.length - 1) {
        app.history = app.history.slice(0, app.historyIndex + 1);
    }

    // Create a snapshot of the current state
    const state = {
        layers: app.layers.map(layer => {
            // Clone each layer canvas
            const clonedCanvas = document.createElement('canvas');
            clonedCanvas.width = layer.canvas.width;
            clonedCanvas.height = layer.canvas.height;
            const clonedCtx = clonedCanvas.getContext('2d');
            clonedCtx.drawImage(layer.canvas, 0, 0);

            return {
                name: layer.name,
                visible: layer.visible,
                canvas: clonedCanvas,
                ctx: clonedCtx
            };
        }),
        activeLayerIndex: app.activeLayerIndex
    };

    // Add state to history
    app.history.push(state);
    app.historyIndex++;

    // Limit history size
    if (app.history.length > app.maxHistorySteps) {
        app.history.shift();
        app.historyIndex--;
    }

    // Update history panel
    updateHistoryPanel();
}

function undo() {
    if (app.historyIndex > 0) {
        app.historyIndex--;
        restoreState(app.history[app.historyIndex]);
        updateHistoryPanel();
    }
}

function redo() {
    if (app.historyIndex < app.history.length - 1) {
        app.historyIndex++;
        restoreState(app.history[app.historyIndex]);
        updateHistoryPanel();
    }
}

function restoreState(state) {
    // Restore layers from state
    app.layers = state.layers.map(layer => {
        const restoredCanvas = document.createElement('canvas');
        restoredCanvas.width = layer.canvas.width;
        restoredCanvas.height = layer.canvas.height;
        const restoredCtx = restoredCanvas.getContext('2d');
        restoredCtx.drawImage(layer.canvas, 0, 0);

        return {
            name: layer.name,
            visible: layer.visible,
            canvas: restoredCanvas,
            ctx: restoredCtx
        };
    });

    app.activeLayerIndex = state.activeLayerIndex;

    // Update UI
    updateLayersPanel();
    render();
}

// Helper functions
// Update the mouse position calculation in handleMouseDown
function handleMouseDown(e) {
    if (app.modalOpen) return;

    const rect = app.canvasOverlay.getBoundingClientRect();
    const container = document.querySelector('.canvas-container');

    // Calculate position accounting for zoom and scroll
    app.startX = (e.clientX - rect.left) / app.zoom;
    app.startY = (e.clientY - rect.top) / app.zoom;
    app.previousX = app.startX;
    app.previousY = app.startY;

    app.isDrawing = true;

    // Get current layer
    const activeLayer = app.layers[app.activeLayerIndex];

    // Tool-specific behavior on mouse down
    if (app.currentTool === 'brush-tool') {
        const ctx = activeLayer.ctx;
        ctx.beginPath();
        ctx.moveTo(app.startX, app.startY);
        ctx.lineTo(app.startX, app.startY); // Draw a dot
        ctx.strokeStyle = app.primaryColor;
        ctx.lineWidth = tools.brush.size;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.globalAlpha = tools.brush.opacity;
        ctx.stroke();
        ctx.globalAlpha = 1;
    }
}
function handleMouseMove(e) {
    if (!app.isDrawing || app.modalOpen) return;
    const rect = app.canvasOverlay.getBoundingClientRect();
    const currentX = (e.clientX - rect.left) / app.zoom;
    const currentY = (e.clientY - rect.top) / app.zoom;
    const activeLayer = app.layers[app.activeLayerIndex];
    switch (app.currentTool) {
        case 'brush-tool':
            const ctx = activeLayer.ctx;
            ctx.beginPath();
            ctx.moveTo(app.previousX, app.previousY);
            ctx.lineTo(currentX, currentY);
            ctx.strokeStyle = app.primaryColor;
            ctx.lineWidth = tools.brush.size;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.globalAlpha = tools.brush.opacity;
            ctx.stroke();
            ctx.globalAlpha = 1;
    }
    app.previousX = currentX;
    app.previousY = currentY;
    render();
}

function updateCursorCoordinates(e) {
    const rect = app.canvasOverlay.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / app.zoom);
    const y = Math.floor((e.clientY - rect.top) / app.zoom);
    // Update status bar with cursor position
    document.getElementById('cursor-coordinates').textContent = `X: ${x}, Y: ${y}`;
}
// Update the setZoom function to properly handle canvas sizing and positioning
function setZoom(zoomLevel) {
    // Clamp zoom between 0.1 and 5
    app.zoom = Math.max(0.1, Math.min(5, zoomLevel));

    // Update zoom display
    document.getElementById('zoom-level').textContent = `${Math.round(app.zoom * 100)}%`;

    // Update canvas position with new zoom
    updateCanvasPosition();
}

// Add a function to handle canvas scrolling
function handleCanvasScroll() {
    const container = document.querySelector('.canvas-container');

    container.addEventListener('scroll', () => {
        // Synchronize overlay position with main canvas during scrolling
        app.canvasOverlay.style.top = `${app.canvas.offsetTop}px`;
        app.canvasOverlay.style.left = `${app.canvas.offsetLeft}px`;
    });
}

function showAbout() {
    alert('PixelMaster v1.0 A web-based drawing application Created with HTML, CSS, and JavaScript');
}
function showShortcuts() {
    openModal('shortcut-modal');
}

// Initialize app when window loads
window.onload = initApp;
