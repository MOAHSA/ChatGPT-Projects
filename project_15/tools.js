// PixelMaster - Drawing Tools Implementation

// Tool settings
const tools = {
    brush: {
        size: 10,
        opacity: 1,
        hardness: 1,
        flow: 1
    },
    eraser: {
        size: 20,
        hardness: 0.5
    },
    shape: {
        type: 'rectangle',
        strokeWidth: 2,
        fill: false
    },
    text: {
        font: 'Arial',
        size: 24,
        bold: false,
        italic: false,
        underline: false
    },
    selection: {
        type: 'rectangle',
        feather: 0
    },
    move: {
        constrainProportions: false
    },
    eyedropper: {},
    crop: {},
    fill: {
        tolerance: 30
    },
    pen: {
        size: 2,
        smoothing: 0.5
    }
};

// Initialize tools
function initTools() {
    // Set up default properties for each tool
    updateColorDisplay();
}

// Mouse event handlers
function handleMouseDown(e) {
    if (app.modalOpen) return;

    const rect = app.canvasOverlay.getBoundingClientRect();
    app.startX = (e.clientX - rect.left) / app.zoom;
    app.startY = (e.clientY - rect.top) / app.zoom;
    app.previousX = app.startX;
    app.previousY = app.startY;

    app.isDrawing = true;

    // Get current layer
    const activeLayer = app.layers[app.activeLayerIndex];

    // Tool-specific behavior on mouse down
    switch (app.currentTool) {
        case 'brush-tool':
            // Start drawing a dot at the current position
            drawBrush(activeLayer.ctx, app.startX, app.startY, app.startX, app.startY);
            break;

        case 'eraser-tool':
            // Start erasing at current position
            erase(activeLayer.ctx, app.startX, app.startY, app.startX, app.startY);
            break;

        case 'text-tool':
            // Open text entry modal
            app.textX = app.startX;
            app.textY = app.startY;
            openModal('text-modal');
            document.getElementById('text-input').focus();
            break;

        case 'shape-tool':
            // Clear overlay to prepare for shape preview
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            break;

        case 'eyedropper-tool':
            // Pick color from canvas
            pickColor(app.startX, app.startY);
            break;

        case 'fill-tool':
            // Fill area with color
            floodFill(activeLayer.ctx, Math.floor(app.startX), Math.floor(app.startY), app.primaryColor);
            saveState();
            render();
            break;

        case 'select-tool':
            // Start selection
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            app.selectedElement = null;
            break;

        case 'crop-tool':
            // Start crop area selection
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            break;
    }
}

function handleMouseMove(e) {
    if (!app.isDrawing || app.modalOpen) return;

    const rect = app.canvasOverlay.getBoundingClientRect();
    const currentX = (e.clientX - rect.left) / app.zoom;
    const currentY = (e.clientY - rect.top) / app.zoom;

    // Get current layer
    const activeLayer = app.layers[app.activeLayerIndex];

    // Tool-specific behavior on mouse move
    switch (app.currentTool) {
        case 'brush-tool':
            // Draw line from previous position to current position
            drawBrush(activeLayer.ctx, app.previousX, app.previousY, currentX, currentY);
            break;

        case 'eraser-tool':
            // Erase from previous position to current position
            erase(activeLayer.ctx, app.previousX, app.previousY, currentX, currentY);
            break;

        case 'shape-tool':
            // Preview shape on overlay
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            drawShape(app.overlayCtx, app.startX, app.startY, currentX, currentY, true);
            break;

        case 'select-tool':
            // Preview selection area on overlay
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            drawSelectionRect(app.startX, app.startY, currentX, currentY);
            break;

        case 'move-tool':
            // Move the selected element
            if (app.selectedElement) {
                moveSelectedElement(currentX - app.previousX, currentY - app.previousY);
                render();
            }
            break;

        case 'crop-tool':
            // Preview crop area on overlay
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            drawCropRect(app.startX, app.startY, currentX, currentY);
            break;

        case 'pen-tool':
            // Draw smooth curve with pen
            drawPen(activeLayer.ctx, app.previousX, app.previousY, currentX, currentY);
            break;
    }

    app.previousX = currentX;
    app.previousY = currentY;
}

function handleMouseUp(e) {
    if (!app.isDrawing || app.modalOpen) return;

    const rect = app.canvasOverlay.getBoundingClientRect();
    const endX = (e.clientX - rect.left) / app.zoom;
    const endY = (e.clientY - rect.top) / app.zoom;

    // Get current layer
    const activeLayer = app.layers[app.activeLayerIndex];

    // Tool-specific behavior on mouse up
    switch (app.currentTool) {
        case 'brush-tool':
        case 'eraser-tool':
        case 'pen-tool':
            // Save state for undo/redo
            saveState();
            break;

        case 'shape-tool':
            // Draw final shape on the active layer
            app.overlayCtx.clearRect(0, 0, app.width, app.height);
            drawShape(activeLayer.ctx, app.startX, app.startY, endX, endY, false);
            saveState();
            break;

        case 'select-tool':
            // Finalize selection
            if (Math.abs(endX - app.startX) > 5 && Math.abs(endY - app.startY) > 5) {
                // Create a selection area
                app.selectedElement = {
                    type: 'selection',
                    x: Math.min(app.startX, endX),
                    y: Math.min(app.startY, endY),
                    width: Math.abs(endX - app.startX),
                    height: Math.abs(endY - app.startY),
                    layerIndex: app.activeLayerIndex
                };

                // Draw selection outline
                drawSelectionRect(app.startX, app.startY, endX, endY);
            }
            break;

        case 'crop-tool':
            // Apply crop if area is large enough
            if (Math.abs(endX - app.startX) > 10 && Math.abs(endY - app.startY) > 10) {
                const cropX = Math.floor(Math.min(app.startX, endX));
                const cropY = Math.floor(Math.min(app.startY, endY));
                const cropWidth = Math.floor(Math.abs(endX - app.startX));
                const cropHeight = Math.floor(Math.abs(endY - app.startY));

                if (confirm(`Crop to ${cropWidth} × ${cropHeight} px?`)) {
                    cropImageToArea(cropX, cropY, cropWidth, cropHeight);
                } else {
                    app.overlayCtx.clearRect(0, 0, app.width, app.height);
                }
            } else {
                app.overlayCtx.clearRect(0, 0, app.width, app.height);
            }
            break;
    }

    app.isDrawing = false;
}

// Tool implementations
function drawBrush(ctx, startX, startY, endX, endY) {
    ctx.globalAlpha = tools.brush.opacity;
    ctx.strokeStyle = app.primaryColor;
    ctx.lineWidth = tools.brush.size;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.stroke();

    // Reset global alpha
    ctx.globalAlpha = 1;

    // Update the composite canvas
    render();
}

function erase(ctx, startX, startY, endX, endY) {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.globalAlpha = tools.eraser.hardness;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = tools.eraser.size;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.stroke();

    // Reset composite operation and alpha
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;

    // Update the composite canvas
    render();
}

function drawShape(ctx, startX, startY, endX, endY, isPreview) {
    const type = tools.shape.type;
    const strokeWidth = tools.shape.strokeWidth;
    const fill = tools.shape.fill;

    // Set up context
    ctx.strokeStyle = app.primaryColor;
    ctx.fillStyle = app.primaryColor;
    ctx.lineWidth = strokeWidth;

    // If it's a preview, use a semi-transparent style
    if (isPreview) {
        ctx.globalAlpha = 0.6;
    }

    // Draw the shape based on type
    switch (type) {
        case 'rectangle':
            if (fill) {
                ctx.fillRect(
                    Math.min(startX, endX),
                    Math.min(startY, endY),
                    Math.abs(endX - startX),
                    Math.abs(endY - startY)
                );
            } else {
                ctx.strokeRect(
                    Math.min(startX, endX),
                    Math.min(startY, endY),
                    Math.abs(endX - startX),
                    Math.abs(endY - startY)
                );
            }
            break;

        case 'ellipse':
            const centerX = (startX + endX) / 2;
            const centerY = (startY + endY) / 2;
            const radiusX = Math.abs(endX - startX) / 2;
            const radiusY = Math.abs(endY - startY) / 2;

            ctx.beginPath();
            ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
            if (fill) {
                ctx.fill();
            } else {
                ctx.stroke();
            }
            break;

        case 'line':
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
            break;

        case 'polygon':
            // For polygon, we'd need to track multiple points
            // This is a simplified triangle implementation
            ctx.beginPath();
            ctx.moveTo(startX, endY); // Bottom left
            ctx.lineTo((startX + endX) / 2, startY); // Top middle
            ctx.lineTo(endX, endY); // Bottom right
            ctx.closePath();
            if (fill) {
                ctx.fill();
            } else {
                ctx.stroke();
            }
            break;
    }

    // Reset global alpha
    ctx.globalAlpha = 1;

    // Update the composite canvas if we're not just previewing
    if (!isPreview) {
        render();
    }
}

function pickColor(x, y) {
    // Create a temporary canvas to get the pixel data
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = app.width;
    tempCanvas.height = app.height;
    const tempCtx = tempCanvas.getContext('2d');

    // Draw all visible layers
    tempCtx.fillStyle = 'white'; // White background
    tempCtx.fillRect(0, 0, app.width, app.height);
    app.layers.forEach(layer => {
        if (layer.visible) {
            tempCtx.drawImage(layer.canvas, 0, 0);
        }
    });

    // Get the pixel color
    const pixel = tempCtx.getImageData(Math.floor(x), Math.floor(y), 1, 1).data;
    const color = `#${pixel[0].toString(16).padStart(2, '0')}${pixel[1].toString(16).padStart(2, '0')}${pixel[2].toString(16).padStart(2, '0')}`;

    // Set as primary color
    app.primaryColor = color;
    updateColorDisplay();
    updateToolProperties();
}

function floodFill(ctx, x, y, fillColor) {
    // Get the pixel data from the context
    const imageData = ctx.getImageData(0, 0, app.width, app.height);
    const data = imageData.data;

    // Get the target color (the color we're replacing)
    const targetColor = getPixelColor(imageData, x, y);

    // Convert fill color to RGBA
    const fill = hexToRgba(fillColor);

    // Don't do anything if the target color is the same as the fill color
    if (colorsMatch(targetColor, fill)) {
        return;
    }

    // Start flood fill (using a simple stack-based approach)
    const stack = [[x, y]];
    const visited = new Set();
    const tolerance = tools.fill.tolerance;

    while (stack.length > 0) {
        const [currentX, currentY] = stack.pop();
        const position = currentY * app.width + currentX;

        // Skip if outside canvas or already visited
        if (currentX < 0 || currentX >= app.width ||
            currentY < 0 || currentY >= app.height ||
            visited.has(position)) {
            continue;
        }

        // Get current pixel color
        const currentColor = getPixelColor(imageData, currentX, currentY);

        // Skip if color doesn't match target within tolerance
        if (!colorsMatchWithTolerance(currentColor, targetColor, tolerance)) {
            continue;
        }

        // Set pixel color
        setPixelColor(imageData, currentX, currentY, fill);
        visited.add(position);

        // Add adjacent pixels to stack
        stack.push([currentX + 1, currentY]);
        stack.push([currentX - 1, currentY]);
        stack.push([currentX, currentY + 1]);
        stack.push([currentX, currentY - 1]);
    }

    // Put the modified image data back on the canvas
    ctx.putImageData(imageData, 0, 0);
}

function getPixelColor(imageData, x, y) {
    const position = (y * imageData.width + x) * 4;
    return {
        r: imageData.data[position],
        g: imageData.data[position + 1],
        b: imageData.data[position + 2],
        a: imageData.data[position + 3]
    };
}

function setPixelColor(imageData, x, y, color) {
    const position = (y * imageData.width + x) * 4;
    imageData.data[position] = color.r;
    imageData.data[position + 1] = color.g;
    imageData.data[position + 2] = color.b;
    imageData.data[position + 3] = color.a;
}

function colorsMatch(color1, color2) {
    return color1.r === color2.r &&
        color1.g === color2.g &&
        color1.b === color2.b &&
        color1.a === color2.a;
}

function colorsMatchWithTolerance(color1, color2, tolerance) {
    return Math.abs(color1.r - color2.r) <= tolerance &&
        Math.abs(color1.g - color2.g) <= tolerance &&
        Math.abs(color1.b - color2.b) <= tolerance &&
        Math.abs(color1.a - color2.a) <= tolerance;
}

function hexToRgba(hex) {
    // Remove # if present
    hex = hex.replace('#', '');

    // Parse the hex values
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    return { r, g, b, a: 255 };
}

function drawSelectionRect(startX, startY, endX, endY) {
    const x = Math.min(startX, endX);
    const y = Math.min(startY, endY);
    const width = Math.abs(endX - startX);
    const height = Math.abs(endY - startY);

    // Draw selection rectangle with dashed lines
    app.overlayCtx.setLineDash([5, 5]);
    app.overlayCtx.strokeStyle = '#000000';
    app.overlayCtx.lineWidth = 1;
    app.overlayCtx.strokeRect(x, y, width, height);

    // Draw another rectangle with offset to create 'marching ants' effect
    app.overlayCtx.strokeStyle = '#ffffff';
    app.overlayCtx.setLineDash([5, 5]);
    app.overlayCtx.lineDashOffset = 5;
    app.overlayCtx.strokeRect(x, y, width, height);

    // Reset dash settings
    app.overlayCtx.setLineDash([]);
    app.overlayCtx.lineDashOffset = 0;
}

function drawCropRect(startX, startY, endX, endY) {
    const x = Math.min(startX, endX);
    const y = Math.min(startY, endY);
    const width = Math.abs(endX - startX);
    const height = Math.abs(endY - startY);

    // Darken the areas outside the crop
    app.overlayCtx.fillStyle = 'rgba(0, 0, 0, 0.5)';

    // Top area
    app.overlayCtx.fillRect(0, 0, app.width, y);

    // Bottom area
    app.overlayCtx.fillRect(0, y + height, app.width, app.height - (y + height));

    // Left area
    app.overlayCtx.fillRect(0, y, x, height);

    // Right area
    app.overlayCtx.fillRect(x + width, y, app.width - (x + width), height);

    // Draw crop rectangle outline
    app.overlayCtx.strokeStyle = '#ffffff';
    app.overlayCtx.lineWidth = 2;
    app.overlayCtx.strokeRect(x, y, width, height);

    // Draw dimensions text
    app.overlayCtx.fillStyle = '#ffffff';
    app.overlayCtx.font = '14px Arial';
    app.overlayCtx.fillText(`${Math.round(width)} × ${Math.round(height)}`, x + 5, y + 20);
}

function moveSelectedElement(deltaX, deltaY) {
    if (!app.selectedElement) return;

    app.selectedElement.x += deltaX;
    app.selectedElement.y += deltaY;

    // Update selection rectangle
    app.overlayCtx.clearRect(0, 0, app.width, app.height);
    drawSelectionRect(
        app.selectedElement.x,
        app.selectedElement.y,
        app.selectedElement.x + app.selectedElement.width,
        app.selectedElement.y + app.selectedElement.height
    );
}

function drawPen(ctx, startX, startY, endX, endY) {
    ctx.strokeStyle = app.primaryColor;
    ctx.lineWidth = tools.pen.size;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Begin drawing path
    ctx.beginPath();
    ctx.moveTo(startX, startY);

    // Apply smoothing if enabled
    if (tools.pen.smoothing > 0) {
        // Calculate control points for quadratic curve
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

        if (distance > 2) {
            const midX = (startX + endX) / 2;
            const midY = (startY + endY) / 2;
            const smoothingFactor = tools.pen.smoothing;

            // Use quadratic curve for smoother lines
            ctx.quadraticCurveTo(
                startX + (deltaX * smoothingFactor),
                startY + (deltaY * smoothingFactor),
                midX,
                midY
            );

            ctx.quadraticCurveTo(
                endX - (deltaX * smoothingFactor),
                endY - (deltaY * smoothingFactor),
                endX,
                endY
            );
        } else {
            ctx.lineTo(endX, endY);
        }
    } else {
        ctx.lineTo(endX, endY);
    }

    ctx.stroke();

    // Update the composite canvas
    render();
}

function addTextToCanvas() {
    const text = document.getElementById('text-input').value;
    if (!text.trim()) {
        closeModal();
        return;
    }

    // Get text properties
    const fontFamily = document.getElementById('font-family').value;
    const fontSize = parseInt(document.getElementById('font-size').value);
    const isBold = document.getElementById('bold-text').classList.contains('active');
    const isItalic = document.getElementById('italic-text').classList.contains('active');
    const isUnderline = document.getElementById('underline-text').classList.contains('active');

    // Construct font string
    let fontString = '';
    if (isItalic) fontString += 'italic ';
    if (isBold) fontString += 'bold ';
    fontString += `${fontSize}px ${fontFamily}`;

    // Get current layer context
    const activeLayer = app.layers[app.activeLayerIndex];
    const ctx = activeLayer.ctx;

    // Set text properties
    ctx.font = fontString;
    ctx.fillStyle = app.primaryColor;
    ctx.textBaseline = 'top';

    // Draw text
    ctx.fillText(text, app.textX, app.textY);

    // Draw underline if selected
    if (isUnderline) {
        const textWidth = ctx.measureText(text).width;
        ctx.lineWidth = fontSize / 15;
        ctx.strokeStyle = app.primaryColor;
        ctx.beginPath();
        ctx.moveTo(app.textX, app.textY + fontSize + 2);
        ctx.lineTo(app.textX + textWidth, app.textY + fontSize + 2);
        ctx.stroke();
    }

    // Save state and update canvas
    saveState();
    render();
    closeModal();
}

function cropImageToArea(x, y, width, height) {
    // Save state before crop
    saveState();

    // Create temp canvas for each layer
    app.layers.forEach(layer => {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = width;
        tempCanvas.height = height;
        const tempCtx = tempCanvas.getContext('2d');

        // Draw portion of layer to temp canvas
        tempCtx.drawImage(
            layer.canvas,
            x, y, width, height,
            0, 0, width, height
        );

        // Resize layer canvas
        layer.canvas.width = width;
        layer.canvas.height = height;

        // Draw cropped content back to layer
        layer.ctx.drawImage(tempCanvas, 0, 0);
    });

    // Update canvas size
    resizeCanvas(width, height);

    // Clear overlay
    app.overlayCtx.clearRect(0, 0, app.width, app.height);

    // Update UI and render
    render();
}

function cutSelection() {
    if (!app.selectedElement) return;

    copySelection();

    // Clear the selected area on the canvas
    const layer = app.layers[app.selectedElement.layerIndex];
    layer.ctx.clearRect(
        app.selectedElement.x,
        app.selectedElement.y,
        app.selectedElement.width,
        app.selectedElement.height
    );

    // Save state, clear overlay, and render
    saveState();
    app.overlayCtx.clearRect(0, 0, app.width, app.height);
    app.selectedElement = null;
    render();
}

function copySelection() {
    if (!app.selectedElement) return;

    // Create clipboard canvas
    const clipboardCanvas = document.createElement('canvas');
    clipboardCanvas.width = app.selectedElement.width;
    clipboardCanvas.height = app.selectedElement.height;
    const clipboardCtx = clipboardCanvas.getContext('2d');

    // Copy the selected area
    const layer = app.layers[app.selectedElement.layerIndex];
    clipboardCtx.drawImage(
        layer.canvas,
        app.selectedElement.x,
        app.selectedElement.y,
        app.selectedElement.width,
        app.selectedElement.height,
        0, 0,
        app.selectedElement.width,
        app.selectedElement.height
    );

    // Store in clipboard
    app.clipboard = {
        canvas: clipboardCanvas,
        width: app.selectedElement.width,
        height: app.selectedElement.height
    };
}

function pasteSelection() {
    if (!app.clipboard) return;

    // Get current layer
    const activeLayer = app.layers[app.activeLayerIndex];

    // Paste at center or at a slight offset from previous paste
    const pasteX = (app.width - app.clipboard.width) / 2;
    const pasteY = (app.height - app.clipboard.height) / 2;

    // Draw clipboard content to canvas
    activeLayer.ctx.drawImage(app.clipboard.canvas, pasteX, pasteY);

    // Create a selection for the pasted content
    app.selectedElement = {
        type: 'selection',
        x: pasteX,
        y: pasteY,
        width: app.clipboard.width,
        height: app.clipboard.height,
        layerIndex: app.activeLayerIndex
    };

    // Draw selection outline
    app.overlayCtx.clearRect(0, 0, app.width, app.height);
    drawSelectionRect(
        pasteX, pasteY,
        pasteX + app.clipboard.width,
        pasteY + app.clipboard.height
    );

    // Save state and render
    saveState();
    render();
}

function rotateImage() {
    // This is a simple 90-degree rotation for the entire canvas
    saveState();

    // Swap width and height
    const newWidth = app.height;
    const newHeight = app.width;

    // Rotate each layer
    app.layers.forEach(layer => {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = newWidth;
        tempCanvas.height = newHeight;
        const tempCtx = tempCanvas.getContext('2d');

        // Rotate 90 degrees clockwise
        tempCtx.translate(newWidth, 0);
        tempCtx.rotate(Math.PI / 2);
        tempCtx.drawImage(layer.canvas, 0, 0);

        // Update layer canvas dimensions
        layer.canvas.width = newWidth;
        layer.canvas.height = newHeight;

        // Draw rotated image back to layer
        layer.ctx.drawImage(tempCanvas, 0, 0);
    });

    // Update canvas size
    resizeCanvas(newWidth, newHeight);

    // Render the canvas
    render();
}

function flipImage() {
    // Toggle between horizontal and vertical flip based on previous state
    if (!app.flipped) {
        flipHorizontal();
        app.flipped = 'horizontal';
    } else if (app.flipped === 'horizontal') {
        flipHorizontal(); // Undo horizontal flip
        flipVertical();
        app.flipped = 'vertical';
    } else {
        flipVertical(); // Undo vertical flip
        app.flipped = null;
    }
}

function flipHorizontal() {
    saveState();

    app.layers.forEach(layer => {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = app.width;
        tempCanvas.height = app.height;
        const tempCtx = tempCanvas.getContext('2d');

        // Flip horizontally
        tempCtx.translate(app.width, 0);
        tempCtx.scale(-1, 1);
        tempCtx.drawImage(layer.canvas, 0, 0);

        // Clear and draw flipped image
        layer.ctx.clearRect(0, 0, app.width, app.height);
        layer.ctx.drawImage(tempCanvas, 0, 0);
    });

    render();
}

function flipVertical() {
    saveState();

    app.layers.forEach(layer => {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = app.width;
        tempCanvas.height = app.height;
        const tempCtx = tempCanvas.getContext('2d');

        // Flip vertically
        tempCtx.translate(0, app.height);
        tempCtx.scale(1, -1);
        tempCtx.drawImage(layer.canvas, 0, 0);

        // Clear and draw flipped image
        layer.ctx.clearRect(0, 0, app.width, app.height);
        layer.ctx.drawImage(tempCanvas, 0, 0);
    });

    render();
}

// Keyboard shortcuts handler
function handleKeyDown(e) {
    // Don't handle shortcuts if a modal is open or if inside a text input
    if (app.modalOpen ||
        e.target.tagName === 'INPUT' ||
        e.target.tagName === 'TEXTAREA') {
        return;
    }

    const key = e.key.toLowerCase();

    // Tool shortcuts
    switch (key) {
        case 'v': // Move tool
            setActiveTool('move-tool');
            break;
        case 'b': // Brush tool
            setActiveTool('brush-tool');
            break;
        case 'e': // Eraser tool
            setActiveTool('eraser-tool');
            break;
        case 't': // Text tool
            setActiveTool('text-tool');
            break;
        case 's': // Selection tool
            setActiveTool('select-tool');
            break;
        case 'u': // Shape tool
            setActiveTool('shape-tool');
            break;
        case 'i': // Eyedropper tool
            setActiveTool('eyedropper-tool');
            break;
        case 'c': // Crop tool
            setActiveTool('crop-tool');
            break;
        case 'g': // Fill tool
            setActiveTool('fill-tool');
            break;
        case 'p': // Pen tool
            setActiveTool('pen-tool');
            break;
    }

    // Command shortcuts
    if (e.ctrlKey || e.metaKey) {
        switch (key) {
            case 'z': // Undo
                e.preventDefault();
                undo();
                break;
            case 'y': // Redo
                e.preventDefault();
                redo();
                break;
            case 's': // Save
                e.preventDefault();
                saveFile();
                break;
            case 'o': // Open
                e.preventDefault();
                openFile();
                break;
            case 'n': // New
                e.preventDefault();
                if (e.shiftKey) { // Ctrl+Shift+N for new layer
                    createNewLayer(`Layer ${app.layers.length + 1}`);
                    updateLayersPanel();
                    saveState();
                } else { // Ctrl+N for new file
                    createNewFile();
                }
                break;
            case 'x': // Cut
                e.preventDefault();
                cutSelection();
                break;
            case 'c': // Copy
                e.preventDefault();
                copySelection();
                break;
            case 'v': // Paste
                e.preventDefault();
                pasteSelection();
                break;
        }
    }

    // Other shortcuts
    switch (key) {
        case '+': // Zoom in
        case '=': // Also for zoom in (without shift)
            setZoom(app.zoom + 0.1);
            break;
        case '-': // Zoom out
        case '_': // Also for zoom out (with shift)
            setZoom(app.zoom - 0.1);
            break;
        case 'delete': // Delete selection
        case 'backspace':
            if (app.selectedElement) {
                cutSelection();
            }
            break;
        case 'escape': // Cancel selection
            if (app.selectedElement) {
                app.overlayCtx.clearRect(0, 0, app.width, app.height);
                app.selectedElement = null;
            } else if (app.modalOpen) {
                closeModal();
            }
            break;
    }
} 