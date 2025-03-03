// PixelMaster - History Management (Undo/Redo)

// Update the history panel UI
function updateHistoryPanel() {
    const historyContent = document.getElementById('history-content');
    historyContent.innerHTML = '';

    // Add history states to panel
    app.history.forEach((state, index) => {
        const isActive = index === app.historyIndex;

        // Create history item
        const historyItem = document.createElement('div');
        historyItem.className = `history-item ${isActive ? 'active' : ''}`;
        historyItem.dataset.index = index;

        // Set history item text
        let stateName = 'Initial State';
        if (index > 0) {
            stateName = `State ${index}`;
        }
        historyItem.textContent = stateName;

        // Add click event to jump to this state
        historyItem.addEventListener('click', () => {
            jumpToHistoryState(index);
        });

        // Add to history panel
        historyContent.appendChild(historyItem);
    });

    // Scroll to active state
    const activeItem = historyContent.querySelector('.history-item.active');
    if (activeItem) {
        activeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Jump to a specific history state
function jumpToHistoryState(index) {
    if (index >= 0 && index < app.history.length && index !== app.historyIndex) {
        // Determine if we're going forward or backward
        const direction = index > app.historyIndex ? 'forward' : 'backward';

        // Update history index
        app.historyIndex = index;

        // Restore state
        restoreState(app.history[index]);

        // Update history panel
        updateHistoryPanel();
    }
}

// Clear history (e.g., when creating a new file)
function clearHistory() {
    app.history = [];
    app.historyIndex = -1;

    // Save initial state
    saveState();

    // Update history panel
    updateHistoryPanel();
}

// Create a snapshot of the current canvas state for the history
function createHistorySnapshot() {
    return {
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
}

// Animation for history navigation
function animateHistoryTransition(fromState, toState, direction) {
    // Create a temporary canvas for the animation
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = app.width;
    tempCanvas.height = app.height;
    const tempCtx = tempCanvas.getContext('2d');

    // Function to draw a state to the context
    function drawState(state, ctx) {
        ctx.clearRect(0, 0, app.width, app.height);

        // Draw white background
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, app.width, app.height);

        // Draw all visible layers
        state.layers.forEach(layer => {
            if (layer.visible) {
                ctx.drawImage(layer.canvas, 0, 0);
            }
        });
    }

    // Draw the "from" state
    drawState(fromState, tempCtx);

    // Create an image data of the "from" state
    const fromImageData = tempCtx.getImageData(0, 0, app.width, app.height);

    // Draw the "to" state
    drawState(toState, tempCtx);

    // Create an image data of the "to" state
    const toImageData = tempCtx.getImageData(0, 0, app.width, app.height);

    // Animation variables
    const duration = 300; // ms
    const startTime = Date.now();

    // Animation function
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Clear main canvas
        app.ctx.clearRect(0, 0, app.width, app.height);

        // Draw white background
        app.ctx.fillStyle = 'white';
        app.ctx.fillRect(0, 0, app.width, app.height);

        // Create a blended image data
        const blendedImageData = app.ctx.createImageData(app.width, app.height);
        const blendedData = blendedImageData.data;
        const fromData = fromImageData.data;
        const toData = toImageData.data;

        for (let i = 0; i < blendedData.length; i += 4) {
            blendedData[i] = Math.round(fromData[i] * (1 - progress) + toData[i] * progress);
            blendedData[i + 1] = Math.round(fromData[i + 1] * (1 - progress) + toData[i + 1] * progress);
            blendedData[i + 2] = Math.round(fromData[i + 2] * (1 - progress) + toData[i + 2] * progress);
            blendedData[i + 3] = Math.round(fromData[i + 3] * (1 - progress) + toData[i + 3] * progress);
        }

        // Draw the blended image
        app.ctx.putImageData(blendedImageData, 0, 0);

        // Continue animation if not done
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            // Finalize by rendering the actual layers
            render();
        }
    }

    // Start animation
    animate();
}

// Export history as a JSON file
function exportHistory() {
    // Create a simplified version of the history for export
    const exportableHistory = app.history.map((state, index) => {
        return {
            index: index,
            layers: state.layers.map(layer => {
                return {
                    name: layer.name,
                    visible: layer.visible,
                    dataURL: layer.canvas.toDataURL('image/png')
                };
            }),
            activeLayerIndex: state.activeLayerIndex
        };
    });

    // Convert to JSON
    const historyJSON = JSON.stringify(exportableHistory);

    // Create a download link
    const a = document.createElement('a');
    const file = new Blob([historyJSON], { type: 'application/json' });
    a.href = URL.createObjectURL(file);
    a.download = 'pixelmaster_history.json';
    a.click();
}

// Import history from a JSON file
function importHistory(jsonData) {
    try {
        const importedHistory = JSON.parse(jsonData);

        // Clear existing history
        app.history = [];

        // Convert imported data back to usable history states
        app.history = importedHistory.map(importedState => {
            const state = {
                layers: [],
                activeLayerIndex: importedState.activeLayerIndex
            };

            // Recreate layers from data URLs
            state.layers = importedState.layers.map(importedLayer => {
                return new Promise(resolve => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);

                        resolve({
                            name: importedLayer.name,
                            visible: importedLayer.visible,
                            canvas: canvas,
                            ctx: ctx
                        });
                    };
                    img.src = importedLayer.dataURL;
                });
            });

            return Promise.all(state.layers).then(resolvedLayers => {
                state.layers = resolvedLayers;
                return state;
            });
        });

        // Wait for all promises to resolve
        Promise.all(app.history).then(resolvedHistory => {
            app.history = resolvedHistory;
            app.historyIndex = app.history.length - 1;

            // Restore the latest state
            restoreState(app.history[app.historyIndex]);

            // Update history panel
            updateHistoryPanel();
        });

        return true;
    } catch (error) {
        console.error('Error importing history:', error);
        return false;
    }
}

// Add an entry to the history panel without adding a new state
// Useful for actions that modify the state but don't need a new snapshot
function updateHistoryEntryName(index, name) {
    const historyContent = document.getElementById('history-content');
    const historyItems = historyContent.querySelectorAll('.history-item');

    if (index >= 0 && index < historyItems.length) {
        historyItems[index].textContent = name;
    }
}

// Auto-save history to local storage
function autoSaveHistory() {
    // Only save if there's something to save
    if (app.history.length === 0) return;

    // Create a simplified version for storage (just the latest state)
    const latestState = app.history[app.historyIndex];
    const saveableState = {
        timestamp: Date.now(),
        width: app.width,
        height: app.height,
        layers: latestState.layers.map(layer => {
            return {
                name: layer.name,
                visible: layer.visible,
                dataURL: layer.canvas.toDataURL('image/png', 0.5) // Lower quality for storage
            };
        }),
        activeLayerIndex: latestState.activeLayerIndex
    };

    // Save to local storage
    try {
        localStorage.setItem('pixelmaster_autosave', JSON.stringify(saveableState));
    } catch (e) {
        console.warn('Unable to autosave to local storage:', e);
    }
}

// Check for auto-saved data on startup
function checkForAutoSave() {
    try {
        const savedData = localStorage.getItem('pixelmaster_autosave');
        if (savedData) {
            const saveState = JSON.parse(savedData);

            // Check if the save is recent (within the last day)
            const isRecent = (Date.now() - saveState.timestamp) < 24 * 60 * 60 * 1000;

            if (isRecent && confirm('Unsaved work from a previous session was found. Would you like to restore it?')) {
                // Clear existing history
                app.history = [];
                app.historyIndex = -1;

                // Set canvas dimensions
                app.width = saveState.width;
                app.height = saveState.height;
                resizeCanvas(app.width, app.height);

                // Create layers from saved data
                const layerPromises = saveState.layers.map(savedLayer => {
                    return new Promise(resolve => {
                        const img = new Image();
                        img.onload = () => {
                            const layer = createNewLayer(savedLayer.name);
                            layer.visible = savedLayer.visible;
                            layer.ctx.drawImage(img, 0, 0);
                            resolve();
                        };
                        img.src = savedLayer.dataURL;
                    });
                });

                // Once all layers are loaded
                Promise.all(layerPromises).then(() => {
                    app.activeLayerIndex = saveState.activeLayerIndex;
                    updateLayersPanel();
                    render();
                    saveState(); // Create initial history state
                });

                return true;
            }
        }
    } catch (e) {
        console.warn('Error checking for autosave:', e);
    }

    return false;
}

// Set up auto-save interval
function setupAutoSave() {
    // Auto-save every 1 minute
    setInterval(autoSaveHistory, 60 * 1000);
}

// Initialize auto-save
setupAutoSave(); 