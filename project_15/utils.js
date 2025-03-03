// PixelMaster - Utility Functions

// Calculate the distance between two points
function calculateDistance(x1, y1, x2, y2) {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

// Convert degrees to radians
function degToRad(degrees) {
    return degrees * Math.PI / 180;
}

// Convert radians to degrees
function radToDeg(radians) {
    return radians * 180 / Math.PI;
}

// Clamp a value between min and max
function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

// Linear interpolation between two values
function lerp(a, b, t) {
    return a + (b - a) * t;
}

// Generate a random color
function randomColor() {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// Brighten or darken a color
function adjustColorBrightness(color, percent) {
    const num = parseInt(color.replace('#', ''), 16);
    const r = (num >> 16) + percent;
    const g = ((num >> 8) & 0x00FF) + percent;
    const b = (num & 0x0000FF) + percent;

    // Clamp the values
    const rClamp = clamp(r, 0, 255);
    const gClamp = clamp(g, 0, 255);
    const bClamp = clamp(b, 0, 255);

    return `#${(1 << 24 | rClamp << 16 | gClamp << 8 | bClamp).toString(16).slice(1)}`;
}

// Get complementary color
function getComplementaryColor(color) {
    const hex = color.replace('#', '');
    const r = 255 - parseInt(hex.substr(0, 2), 16);
    const g = 255 - parseInt(hex.substr(2, 2), 16);
    const b = 255 - parseInt(hex.substr(4, 2), 16);

    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// Calculate file size from data URL
function calculateDataURLSize(dataURL) {
    // Remove metadata and calculate base64 string size
    const base64 = dataURL.split(',')[1];
    const sizeInBytes = Math.ceil((base64.length * 3) / 4);

    // Convert to kilobytes
    return Math.round(sizeInBytes / 1024);
}

// Format file size with appropriate units
function formatFileSize(sizeInKB) {
    if (sizeInKB < 1024) {
        return `${sizeInKB} KB`;
    } else {
        return `${(sizeInKB / 1024).toFixed(1)} MB`;
    }
}

// Create a canvas with checkerboard pattern
function createCheckerboardCanvas(width, height, squareSize = 10) {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = '#e0e0e0';
    for (let x = 0; x < width; x += squareSize * 2) {
        for (let y = 0; y < height; y += squareSize * 2) {
            ctx.fillRect(x, y, squareSize, squareSize);
            ctx.fillRect(x + squareSize, y + squareSize, squareSize, squareSize);
        }
    }

    return canvas;
}

// Function to apply an image filter
function applyFilter(imageData, filterType, strength = 1) {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;

    // Create a copy of the image data for filters that need original values
    const origData = new Uint8ClampedArray(data);

    switch (filterType) {
        case 'grayscale':
            for (let i = 0; i < data.length; i += 4) {
                // Apply grayscale formula with weighted rgb values for perceptual accuracy
                const gray = (0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
                data[i] = data[i + 1] = data[i + 2] = gray;
            }
            break;

        case 'sepia':
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];

                // Apply sepia transformation
                data[i] = Math.min(255, (r * 0.393) + (g * 0.769) + (b * 0.189));
                data[i + 1] = Math.min(255, (r * 0.349) + (g * 0.686) + (b * 0.168));
                data[i + 2] = Math.min(255, (r * 0.272) + (g * 0.534) + (b * 0.131));
            }
            break;

        case 'invert':
            for (let i = 0; i < data.length; i += 4) {
                data[i] = 255 - data[i];
                data[i + 1] = 255 - data[i + 1];
                data[i + 2] = 255 - data[i + 2];
            }
            break;

        case 'brightness':
            for (let i = 0; i < data.length; i += 4) {
                data[i] = clamp(data[i] + strength * 255, 0, 255);
                data[i + 1] = clamp(data[i + 1] + strength * 255, 0, 255);
                data[i + 2] = clamp(data[i + 2] + strength * 255, 0, 255);
            }
            break;

        case 'contrast':
            const factor = (259 * (strength * 100 + 255)) / (255 * (259 - strength * 100));
            for (let i = 0; i < data.length; i += 4) {
                data[i] = clamp(factor * (data[i] - 128) + 128, 0, 255);
                data[i + 1] = clamp(factor * (data[i + 1] - 128) + 128, 0, 255);
                data[i + 2] = clamp(factor * (data[i + 2] - 128) + 128, 0, 255);
            }
            break;

        case 'blur':
            // Simple box blur
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    let r = 0, g = 0, b = 0, a = 0, count = 0;

                    // Kernel size based on strength
                    const kernelSize = Math.ceil(strength * 10);
                    const halfKernel = Math.floor(kernelSize / 2);

                    // Sample neighboring pixels
                    for (let ky = -halfKernel; ky <= halfKernel; ky++) {
                        for (let kx = -halfKernel; kx <= halfKernel; kx++) {
                            const px = clamp(x + kx, 0, width - 1);
                            const py = clamp(y + ky, 0, height - 1);
                            const i = (py * width + px) * 4;

                            r += origData[i];
                            g += origData[i + 1];
                            b += origData[i + 2];
                            a += origData[i + 3];
                            count++;
                        }
                    }

                    // Set averaged value
                    const i = (y * width + x) * 4;
                    data[i] = r / count;
                    data[i + 1] = g / count;
                    data[i + 2] = b / count;
                    data[i + 3] = a / count;
                }
            }
            break;

        case 'sharpen':
            // Apply unsharp mask (blur and subtract)
            const tempImageData = new ImageData(
                new Uint8ClampedArray(origData),
                width,
                height
            );

            // Create a blurred version
            applyFilter(tempImageData, 'blur', 0.5);

            // Subtract blurred from original with scaling
            for (let i = 0; i < data.length; i += 4) {
                data[i] = clamp(origData[i] + (origData[i] - tempImageData.data[i]) * strength, 0, 255);
                data[i + 1] = clamp(origData[i + 1] + (origData[i + 1] - tempImageData.data[i + 1]) * strength, 0, 255);
                data[i + 2] = clamp(origData[i + 2] + (origData[i + 2] - tempImageData.data[i + 2]) * strength, 0, 255);
            }
            break;
    }

    return imageData;
}

// Function to optimize image data (e.g., for export)
function optimizeImageData(ctx, width, height, quality = 0.8) {
    // Get the image data
    const imageData = ctx.getImageData(0, 0, width, height);

    // Create a canvas for the optimized image
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const tempCtx = tempCanvas.getContext('2d');

    // Draw the image data to the canvas
    tempCtx.putImageData(imageData, 0, 0);

    // Convert to JPEG data URL with quality setting
    const dataURL = tempCanvas.toDataURL('image/jpeg', quality);

    // Create an image, load the data URL, and draw back to original context
    const img = new Image();
    img.onload = () => {
        ctx.clearRect(0, 0, width, height);
        ctx.drawImage(img, 0, 0);
    };
    img.src = dataURL;

    // Return the optimized data URL
    return dataURL;
}

// Function to create gradient
function createGradient(ctx, x1, y1, x2, y2, colorStops) {
    const gradient = ctx.createLinearGradient(x1, y1, x2, y2);

    // Add color stops
    colorStops.forEach(stop => {
        gradient.addColorStop(stop.position, stop.color);
    });

    return gradient;
}

// Function to create radial gradient
function createRadialGradient(ctx, x1, y1, r1, x2, y2, r2, colorStops) {
    const gradient = ctx.createRadialGradient(x1, y1, r1, x2, y2, r2);

    // Add color stops
    colorStops.forEach(stop => {
        gradient.addColorStop(stop.position, stop.color);
    });

    return gradient;
}

// Function to resize an image proportionally
function resizeImageProportionally(img, maxWidth, maxHeight) {
    let width = img.width;
    let height = img.height;

    // Calculate the new dimensions
    if (width > maxWidth) {
        const ratio = maxWidth / width;
        width = maxWidth;
        height = height * ratio;
    }

    if (height > maxHeight) {
        const ratio = maxHeight / height;
        height = maxHeight;
        width = width * ratio;
    }

    return { width, height };
}

// Function to detect image edges (for selection tools)
function detectEdges(imageData, threshold = 30) {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;

    // Create a new image data for the edge map
    const edgeMap = new Uint8ClampedArray(width * height);

    // Apply Sobel operator for edge detection
    for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
            // Get surrounding pixels
            const tl = (y - 1) * width * 4 + (x - 1) * 4;
            const t = (y - 1) * width * 4 + x * 4;
            const tr = (y - 1) * width * 4 + (x + 1) * 4;
            const l = y * width * 4 + (x - 1) * 4;
            const r = y * width * 4 + (x + 1) * 4;
            const bl = (y + 1) * width * 4 + (x - 1) * 4;
            const b = (y + 1) * width * 4 + x * 4;
            const br = (y + 1) * width * 4 + (x + 1) * 4;

            // Calculate Sobel gradient
            const gx =
                data[tl] + 2 * data[l] + data[bl] -
                data[tr] - 2 * data[r] - data[br];

            const gy =
                data[tl] + 2 * data[t] + data[tr] -
                data[bl] - 2 * data[b] - data[br];

            // Calculate gradient magnitude
            const magnitude = Math.sqrt(gx * gx + gy * gy);

            // Set edge map value
            edgeMap[y * width + x] = magnitude > threshold ? 255 : 0;
        }
    }

    return edgeMap;
}

// Function to get dominant colors from an image
function getDominantColors(imageData, numColors = 5) {
    const data = imageData.data;
    const pixels = [];

    // Extract pixels from image data
    for (let i = 0; i < data.length; i += 4) {
        // Skip fully transparent pixels
        if (data[i + 3] > 128) {
            pixels.push({
                r: data[i],
                g: data[i + 1],
                b: data[i + 2]
            });
        }
    }

    // Simple k-means clustering to find dominant colors
    let clusters = [];

    // Initialize clusters with random pixels
    for (let i = 0; i < numColors; i++) {
        const randomIndex = Math.floor(Math.random() * pixels.length);
        clusters.push({
            center: { ...pixels[randomIndex] },
            pixels: []
        });
    }

    // Maximum iterations for k-means
    const maxIterations = 10;

    for (let iteration = 0; iteration < maxIterations; iteration++) {
        // Reset clusters
        clusters.forEach(cluster => {
            cluster.pixels = [];
        });

        // Assign pixels to nearest cluster
        pixels.forEach(pixel => {
            let minDistance = Infinity;
            let nearestCluster = 0;

            clusters.forEach((cluster, i) => {
                const distance = Math.sqrt(
                    Math.pow(pixel.r - cluster.center.r, 2) +
                    Math.pow(pixel.g - cluster.center.g, 2) +
                    Math.pow(pixel.b - cluster.center.b, 2)
                );

                if (distance < minDistance) {
                    minDistance = distance;
                    nearestCluster = i;
                }
            });

            clusters[nearestCluster].pixels.push(pixel);
        });

        // Update cluster centers
        let centersChanged = false;
        clusters.forEach(cluster => {
            if (cluster.pixels.length > 0) {
                const newCenter = {
                    r: 0,
                    g: 0,
                    b: 0
                };

                cluster.pixels.forEach(pixel => {
                    newCenter.r += pixel.r;
                    newCenter.g += pixel.g;
                    newCenter.b += pixel.b;
                });

                newCenter.r = Math.round(newCenter.r / cluster.pixels.length);
                newCenter.g = Math.round(newCenter.g / cluster.pixels.length);
                newCenter.b = Math.round(newCenter.b / cluster.pixels.length);

                // Check if center changed
                if (
                    newCenter.r !== cluster.center.r ||
                    newCenter.g !== cluster.center.g ||
                    newCenter.b !== cluster.center.b
                ) {
                    cluster.center = newCenter;
                    centersChanged = true;
                }
            }
        });

        // If no centers changed, we've converged
        if (!centersChanged) break;
    }

    // Sort clusters by size (number of pixels)
    clusters.sort((a, b) => b.pixels.length - a.pixels.length);

    // Convert to hex colors
    return clusters.filter(cluster => cluster.pixels.length > 0).map(cluster => {
        return {
            color: `#${cluster.center.r.toString(16).padStart(2, '0')}${cluster.center.g.toString(16).padStart(2, '0')}${cluster.center.b.toString(16).padStart(2, '0')}`,
            count: cluster.pixels.length
        };
    });
}

// Generate a unique ID (for elements, layers, etc.)
function generateUniqueId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

// Debounce function to limit how often a function is called
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Throttle function to limit the rate at which a function is called
function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Check if browser supports a specific feature
function supportsFeature(feature) {
    switch (feature) {
        case 'canvas':
            return !!document.createElement('canvas').getContext;
        case 'webp':
            const canvas = document.createElement('canvas');
            canvas.width = 1;
            canvas.height = 1;
            return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
        case 'touch':
            return 'ontouchstart' in window;
        case 'fileapi':
            return window.File && window.FileReader && window.FileList && window.Blob;
        case 'draganddrop':
            return 'draggable' in document.createElement('div');
        default:
            return false;
    }
}

// Format a timestamp into a readable date string
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Format a date for use in filenames
function formatDateForFilename() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    const second = String(now.getSeconds()).padStart(2, '0');

    return `${year}${month}${day}_${hour}${minute}${second}`;
} 