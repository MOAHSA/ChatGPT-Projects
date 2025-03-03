// PixelMaster - Layer Management

// Create a new layer
function createNewLayer(name) {
    // Create a new canvas for the layer
    const layerCanvas = document.createElement('canvas');
    layerCanvas.width = app.width;
    layerCanvas.height = app.height;
    const layerCtx = layerCanvas.getContext('2d');

    // Create layer object
    const layer = {
        name: name,
        canvas: layerCanvas,
        ctx: layerCtx,
        visible: true
    };

    // Add layer to array
    app.layers.push(layer);

    // Set as active layer
    app.activeLayerIndex = app.layers.length - 1;

    // Update layers panel
    updateLayersPanel();

    // Return the layer
    return layer;
}

// Update the layers panel UI
function updateLayersPanel() {
    const layersContent = document.getElementById('layers-content');
    layersContent.innerHTML = '';

    // Add layers in reverse order (top layer first)
    for (let i = app.layers.length - 1; i >= 0; i--) {
        const layer = app.layers[i];
        const isActive = i === app.activeLayerIndex;

        // Create layer item
        const layerItem = document.createElement('div');
        layerItem.className = `layer-item ${isActive ? 'active' : ''}`;
        layerItem.dataset.index = i;

        // Create layer thumbnail
        const thumbnail = document.createElement('div');
        thumbnail.className = 'layer-thumbnail';
        // Generate thumbnail (a small preview of the layer)
        updateLayerThumbnail(thumbnail, layer);

        // Create visibility toggle
        const visibilityToggle = document.createElement('div');
        visibilityToggle.className = 'layer-visibility';
        visibilityToggle.innerHTML = layer.visible ?
            '<i class="fas fa-eye"></i>' :
            '<i class="fas fa-eye-slash"></i>';

        // Create layer name
        const layerName = document.createElement('div');
        layerName.className = 'layer-name';
        layerName.textContent = layer.name;

        // Append elements to layer item
        layerItem.appendChild(thumbnail);
        layerItem.appendChild(visibilityToggle);
        layerItem.appendChild(layerName);

        // Add event listeners
        layerItem.addEventListener('click', (e) => {
            if (e.target.closest('.layer-visibility')) {
                // Toggle visibility
                toggleLayerVisibility(i);
            } else {
                // Set as active layer
                setActiveLayer(i);
            }
        });

        // Add drag and drop functionality
        layerItem.draggable = true;
        layerItem.addEventListener('dragstart', handleDragStart);
        layerItem.addEventListener('dragover', handleDragOver);
        layerItem.addEventListener('drop', handleDrop);

        // Add context menu for additional options
        layerItem.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            showLayerContextMenu(e, i);
        });

        // Add to layers panel
        layersContent.appendChild(layerItem);
    }
}

// Generate and update a thumbnail for a layer
function updateLayerThumbnail(thumbnailElement, layer) {
    const size = 30; // Thumbnail size

    // Create a tiny canvas for the thumbnail
    const thumbnailCanvas = document.createElement('canvas');
    thumbnailCanvas.width = size;
    thumbnailCanvas.height = size;
    const thumbnailCtx = thumbnailCanvas.getContext('2d');

    // Scale down the layer to fit the thumbnail
    const scale = Math.min(size / app.width, size / app.height);
    const width = app.width * scale;
    const height = app.height * scale;
    const x = (size - width) / 2;
    const y = (size - height) / 2;

    // Draw a checkerboard pattern for transparent areas
    drawCheckerboardPattern(thumbnailCtx, size);

    // Draw the layer content
    thumbnailCtx.drawImage(layer.canvas, x, y, width, height);

    // Add the thumbnail image to the element
    if (thumbnailElement.firstChild) {
        thumbnailElement.removeChild(thumbnailElement.firstChild);
    }
    thumbnailElement.appendChild(thumbnailCanvas);
}

// Draw a checkerboard pattern (for transparent backgrounds)
function drawCheckerboardPattern(ctx, size, squareSize = 5) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, size, size);

    ctx.fillStyle = '#e0e0e0';
    for (let x = 0; x < size; x += squareSize * 2) {
        for (let y = 0; y < size; y += squareSize * 2) {
            ctx.fillRect(x, y, squareSize, squareSize);
            ctx.fillRect(x + squareSize, y + squareSize, squareSize, squareSize);
        }
    }
}

// Set the active layer
function setActiveLayer(index) {
    if (index >= 0 && index < app.layers.length) {
        app.activeLayerIndex = index;
        updateLayersPanel();
    }
}

// Toggle layer visibility
function toggleLayerVisibility(index) {
    if (index >= 0 && index < app.layers.length) {
        app.layers[index].visible = !app.layers[index].visible;
        updateLayersPanel();
        render();
    }
}

// Duplicate the current layer
function duplicateCurrentLayer() {
    if (app.activeLayerIndex >= 0) {
        const sourceLayer = app.layers[app.activeLayerIndex];

        // Create a new layer with a copy of the source layer's content
        const newLayer = createNewLayer(`${sourceLayer.name} Copy`);

        // Copy content from source layer
        newLayer.ctx.drawImage(sourceLayer.canvas, 0, 0);

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }
}

// Merge the current layer with the one below it
function mergeLayers() {
    if (app.activeLayerIndex > 0) {
        // Get the current and lower layers
        const currentLayer = app.layers[app.activeLayerIndex];
        const lowerLayer = app.layers[app.activeLayerIndex - 1];

        // Draw the current layer onto the lower layer
        lowerLayer.ctx.drawImage(currentLayer.canvas, 0, 0);

        // Remove the current layer
        app.layers.splice(app.activeLayerIndex, 1);

        // Set the lower layer as active
        app.activeLayerIndex--;

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }
}

// Rename the current layer
function renameLayer(index, newName) {
    if (index >= 0 && index < app.layers.length) {
        app.layers[index].name = newName;
        updateLayersPanel();
    }
}

// Show context menu for a layer
function showLayerContextMenu(e, layerIndex) {
    // Remove any existing context menu
    const existingMenu = document.querySelector('.layer-context-menu');
    if (existingMenu) {
        document.body.removeChild(existingMenu);
    }

    // Create context menu
    const contextMenu = document.createElement('div');
    contextMenu.className = 'layer-context-menu';
    contextMenu.style.position = 'absolute';
    contextMenu.style.left = `${e.clientX}px`;
    contextMenu.style.top = `${e.clientY}px`;
    contextMenu.style.backgroundColor = 'white';
    contextMenu.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
    contextMenu.style.borderRadius = '4px';
    contextMenu.style.padding = '5px 0';
    contextMenu.style.zIndex = '1000';

    // Add menu items
    const menuItems = [
        { text: 'Rename', action: () => promptLayerRename(layerIndex) },
        { text: 'Duplicate', action: () => duplicateLayer(layerIndex) },
        { text: 'Delete', action: () => deleteLayer(layerIndex) },
        { text: 'Merge Down', action: () => mergeDown(layerIndex) },
        { text: 'Move Up', action: () => moveLayer(layerIndex, -1) },
        { text: 'Move Down', action: () => moveLayer(layerIndex, 1) }
    ];

    menuItems.forEach(item => {
        const menuItem = document.createElement('div');
        menuItem.className = 'layer-context-menu-item';
        menuItem.textContent = item.text;
        menuItem.style.padding = '8px 15px';
        menuItem.style.cursor = 'pointer';

        menuItem.addEventListener('mouseenter', () => {
            menuItem.style.backgroundColor = '#f5f5f5';
        });

        menuItem.addEventListener('mouseleave', () => {
            menuItem.style.backgroundColor = 'transparent';
        });

        menuItem.addEventListener('click', () => {
            // Close menu and perform action
            document.body.removeChild(contextMenu);
            item.action();
        });

        contextMenu.appendChild(menuItem);
    });

    // Add to body
    document.body.appendChild(contextMenu);

    // Close menu when clicking elsewhere
    const closeMenu = (e) => {
        if (!contextMenu.contains(e.target)) {
            document.body.removeChild(contextMenu);
            document.removeEventListener('click', closeMenu);
        }
    };

    // Use setTimeout to avoid the menu being closed immediately
    setTimeout(() => {
        document.addEventListener('click', closeMenu);
    }, 0);
}

// Prompt for layer rename
function promptLayerRename(index) {
    const layer = app.layers[index];
    const newName = prompt('Enter new layer name:', layer.name);
    if (newName !== null) {
        renameLayer(index, newName);
    }
}

// Duplicate a specific layer
function duplicateLayer(index) {
    if (index >= 0 && index < app.layers.length) {
        const sourceLayer = app.layers[index];

        // Create a new layer with a copy of the source layer's content
        const newLayer = createNewLayer(`${sourceLayer.name} Copy`);

        // Copy content from source layer
        newLayer.ctx.drawImage(sourceLayer.canvas, 0, 0);

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }
}

// Delete a specific layer
function deleteLayer(index) {
    if (app.layers.length > 1 && index >= 0 && index < app.layers.length) {
        app.layers.splice(index, 1);

        // Adjust active layer index if needed
        if (app.activeLayerIndex >= index) {
            app.activeLayerIndex = Math.max(0, app.activeLayerIndex - 1);
        }

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }
}

// Merge a layer with the one below it
function mergeDown(index) {
    if (index > 0 && index < app.layers.length) {
        // Get the current and lower layers
        const currentLayer = app.layers[index];
        const lowerLayer = app.layers[index - 1];

        // Draw the current layer onto the lower layer
        lowerLayer.ctx.drawImage(currentLayer.canvas, 0, 0);

        // Remove the current layer
        app.layers.splice(index, 1);

        // Adjust active layer index if needed
        if (app.activeLayerIndex === index) {
            app.activeLayerIndex = index - 1;
        } else if (app.activeLayerIndex > index) {
            app.activeLayerIndex--;
        }

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }
}

// Move a layer up or down
function moveLayer(index, direction) {
    const newIndex = index + direction;

    if (newIndex >= 0 && newIndex < app.layers.length) {
        // Swap layers
        const temp = app.layers[index];
        app.layers[index] = app.layers[newIndex];
        app.layers[newIndex] = temp;

        // Adjust active layer index if needed
        if (app.activeLayerIndex === index) {
            app.activeLayerIndex = newIndex;
        } else if (app.activeLayerIndex === newIndex) {
            app.activeLayerIndex = index;
        }

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }
}

// Drag and drop functionality for layer reordering
function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.index);
    e.target.style.opacity = '0.4';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDrop(e) {
    e.preventDefault();
    const sourceIndex = parseInt(e.dataTransfer.getData('text/plain'));
    const targetIndex = parseInt(e.target.closest('.layer-item').dataset.index);

    if (sourceIndex !== targetIndex) {
        // Reorder layers
        const sourceLayer = app.layers[sourceIndex];
        app.layers.splice(sourceIndex, 1);
        app.layers.splice(targetIndex, 0, sourceLayer);

        // Adjust active layer index
        if (app.activeLayerIndex === sourceIndex) {
            app.activeLayerIndex = targetIndex;
        } else if (
            app.activeLayerIndex > sourceIndex &&
            app.activeLayerIndex <= targetIndex
        ) {
            app.activeLayerIndex--;
        } else if (
            app.activeLayerIndex < sourceIndex &&
            app.activeLayerIndex >= targetIndex
        ) {
            app.activeLayerIndex++;
        }

        // Update UI and save state
        updateLayersPanel();
        render();
        saveState();
    }

    // Reset opacity of dragged element
    document.querySelectorAll('.layer-item').forEach(item => {
        item.style.opacity = '1';
    });

    return false;
} 