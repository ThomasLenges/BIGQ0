// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const recentDetectionsElement = document.getElementById('recentDetections');
const feedbackContentElement = document.getElementById('feedback-content');
const MAX_RECENT_SCANS = 5;
let scans = [];
const socket = io(`http://${window.location.host}`); // Initialize socket.io connection
let errorContainer = document.getElementById('error-container');
const trackingOverlay = document.getElementById('trackingOverlay');
const trackingCtx = trackingOverlay.getContext('2d');

// Stores currently visible tracks.
// key = track ID
// value = { track, lastSeen }
const activeTracks = new Map();

// Keep a track visible briefly even if the detector does not update it.
// Tune later.
const TRACK_TTL_MS = 350;

let nextUiTrackId = 1;

// Used only when the backend does not provide track_id.
// This lets the UI match boxes frame-to-frame instead of creating
// a new fake ID from coordinates.
const UI_MATCH_IOU_THRESHOLD = 0.05;
const UI_MATCH_MIN_DISTANCE = 90;

// Important:
// These should match the resolution used by the detection stream.
// If your detection/video stream is 1024x768, keep these values.
const SOURCE_WIDTH = 1024;
const SOURCE_HEIGHT = 768;

// Start the application
document.addEventListener('DOMContentLoaded', () => {
    initSocketIO();
    initializeConfidenceSlider();
    updateFeedback(null);
    renderDetections();
    setInterval(() => {
        drawTrackedObjects(getVisibleTracks());
    }, 150);

    // Popover logic
    const confidencePopoverText = "Minimum confidence score for detected objects. Lower values show more results but may include false positives.";
    const feedbackPopoverText = "When the camera detects an object like cat, cell phone, clock, cup, dog or potted plant, a picture and a message will be shown here.";
    window.addEventListener('resize', () => {
        drawTrackedObjects(getVisibleTracks());
    });
    document.querySelectorAll('.info-btn.confidence').forEach(img => {
        const popover = img.nextElementSibling;
        img.addEventListener('mouseenter', () => {
            popover.textContent = confidencePopoverText;
            popover.style.display = 'block';
        });
        img.addEventListener('mouseleave', () => {
            popover.style.display = 'none';
        });
    });

    document.querySelectorAll('.info-btn.feedback').forEach(img => {
        const popover = img.nextElementSibling;
        img.addEventListener('mouseenter', () => {
            popover.textContent = feedbackPopoverText;
            popover.style.display = 'block';
        });
        img.addEventListener('mouseleave', () => {
            popover.style.display = 'none';
        });
    });
});

function initSocketIO() {
    socket.on('connect', () => {
        if (errorContainer) {
            errorContainer.style.display = 'none';
            errorContainer.textContent = '';
        }
    });

    socket.on('disconnect', () => {
        if (errorContainer) {
            errorContainer.textContent = 'Connection to the board lost. Please check the connection.';
            errorContainer.style.display = 'block';
        }
    });

    socket.on('detection', async (message) => {
        console.log('DETECTION:', message);

        const tracks = normalizeTracksMessage(message);

        // New Kalman/tracking format
        if (tracks.length > 0 && tracks.some(track => getTrackBoundingBox(track))) {
            updateActiveTracks(tracks);

            const visibleTracks = getVisibleTracks();
            drawTrackedObjects(visibleTracks);

            const realTracks = visibleTracks.filter(track => !track.is_predicted);

            realTracks.forEach(track => {
                printDetection(track);
            });

            renderDetections();

            if (realTracks.length > 0) {
                updateFeedback(realTracks[0]);
            }

            return;
        }

        // Old/simple detection format fallback
        printDetection(message);
        renderDetections();
        updateFeedback(message);
    });

    socket.on('track', (message) => {
        console.log('TRACK:', message);

        const tracks = normalizeTracksMessage(message);
        updateActiveTracks(tracks);
        drawTrackedObjects(getVisibleTracks());
    });

    socket.on('tracks', (message) => {
        console.log('TRACKS:', message);

        const tracks = normalizeTracksMessage(message);
        updateActiveTracks(tracks);
        drawTrackedObjects(getVisibleTracks());
    });

    socket.on('track_lost', () => {
        activeTracks.clear();
        clearTrackingOverlay();
    });
}

function updateFeedback(detection) {
    if (!detection) {
        feedbackContentElement.innerHTML = `
            <img src="img/stars.svg" alt="Stars">
            <p class="feedback-text">Waiting for vehicle detections...</p>
        `;
        return;
    }

    const label = detection.content || detection.label || "vehicle";
    const confidence = typeof detection.confidence === "number"
        ? Math.floor(detection.confidence * 100)
        : 0;

    const trackIdText = (detection.track_id !== undefined && detection.track_id !== null)
    ? `<p>Track ID: ${detection.track_id}</p>`
    : "";

    feedbackContentElement.innerHTML = `
        <div class="feedback-detection">
            <div class="percentage">${confidence}%</div>
            <p>Detected: ${label}</p>
            ${trackIdText}
        </div>
    `;
}

function printDetection(newDetection) {
    scans.unshift(newDetection);
    if (scans.length > MAX_RECENT_SCANS) { scans.pop(); }
}

// Function to render the list of scans
function renderDetections() {
    // Clear the list
    recentDetectionsElement.innerHTML = ``;

    if (scans.length === 0) {
        recentDetectionsElement.innerHTML = `
            <div class="no-recent-scans">
                <img src="./img/no-face.svg">
                No object detected yet
            </div>
        `;
        return;
    }

    scans.forEach((scan) => {
        const row = document.createElement('div');
        row.className = 'scan-container';

        // Create a container for content and time
        const cellContainer = document.createElement('span');
        cellContainer.className = 'scan-cell-container cell-border';

        // Content (text + icon)
        const contentText = document.createElement('span');
        contentText.className = 'scan-content';
		const value = scan.confidence ?? 0;
        const result = Math.floor(value * 1000) / 10;

        const label = scan.content || scan.label || scan.detector_label || "vehicle";
        const trackId = (scan.track_id !== undefined && scan.track_id !== null) ? ` ID ${scan.track_id}` : "";

        contentText.innerHTML = `${result}% - ${label}${trackId}`;

        // Time
        const timeText = document.createElement('span');
        timeText.className = 'scan-content-time';
        const timestamp = scan.timestamp || Date.now();
        timeText.textContent = new Date(timestamp).toLocaleString('it-IT').replace(',', ' -');

        // Append content and time to the container
        cellContainer.appendChild(contentText);
        cellContainer.appendChild(timeText);

        row.appendChild(cellContainer);
        recentDetectionsElement.appendChild(row);
    });
}


function initializeConfidenceSlider() {
    const confidenceSlider = document.getElementById('confidenceSlider');
    const confidenceInput = document.getElementById('confidenceInput');
    const confidenceResetButton = document.getElementById('confidenceResetButton');

    confidenceSlider.addEventListener('input', updateConfidenceDisplay);
    confidenceInput.addEventListener('input', handleConfidenceInputChange);
    confidenceInput.addEventListener('blur', validateConfidenceInput);
    updateConfidenceDisplay();

    confidenceResetButton.addEventListener('click', (e) => {
        if (e.target.classList.contains('reset-icon') || e.target.closest('.reset-icon')) {
            resetConfidence();
        }
    });
}

function handleConfidenceInputChange() {
    const confidenceInput = document.getElementById('confidenceInput');
    const confidenceSlider = document.getElementById('confidenceSlider');

    let value = parseFloat(confidenceInput.value);

    if (isNaN(value)) value = 0.5;
    if (value < 0) value = 0;
    if (value > 1) value = 1;

    confidenceSlider.value = value;
    updateConfidenceDisplay();
}

function validateConfidenceInput() {
    const confidenceInput = document.getElementById('confidenceInput');
    let value = parseFloat(confidenceInput.value);

    if (isNaN(value)) value = 0.5;
    if (value < 0) value = 0;
    if (value > 1) value = 1;

    confidenceInput.value = value.toFixed(2);

    handleConfidenceInputChange();
}

function updateConfidenceDisplay() {
    const confidenceSlider = document.getElementById('confidenceSlider');
    const confidenceInput = document.getElementById('confidenceInput');
    const confidenceValueDisplay = document.getElementById('confidenceValueDisplay');
    const sliderProgress = document.getElementById('sliderProgress');

    const value = parseFloat(confidenceSlider.value);
    socket.emit('override_th', value); // Send confidence to backend
    const percentage = (value - confidenceSlider.min) / (confidenceSlider.max - confidenceSlider.min) * 100;

    const displayValue = value.toFixed(2);
    confidenceValueDisplay.textContent = displayValue;

    if (document.activeElement !== confidenceInput) {
        confidenceInput.value = displayValue;
    }

    sliderProgress.style.width = percentage + '%';
    confidenceValueDisplay.style.left = percentage + '%';
}

function resetConfidence() {
    const confidenceSlider = document.getElementById('confidenceSlider');
    const confidenceInput = document.getElementById('confidenceInput');

    confidenceSlider.value = '0.5';
    confidenceInput.value = '0.50';
    updateConfidenceDisplay();
}

function clearTrackingOverlay() {
    trackingCtx.clearRect(0, 0, trackingOverlay.width, trackingOverlay.height);
}

function drawTrackedObjects(tracks) {
    clearTrackingOverlay();

    if (!Array.isArray(tracks) || tracks.length === 0) {
        return;
    }

    const scaleX = trackingOverlay.width / SOURCE_WIDTH;
    const scaleY = trackingOverlay.height / SOURCE_HEIGHT;

    tracks.forEach((track) => {
        const bbox = getTrackBoundingBox(track);

        if (!bbox) {
            return;
        }

        const [x1, y1, x2, y2] = bbox;

        const scaledX1 = x1 * scaleX;
        const scaledY1 = y1 * scaleY;
        const scaledX2 = x2 * scaleX;
        const scaledY2 = y2 * scaleY;

        const width = scaledX2 - scaledX1;
        const height = scaledY2 - scaledY1;

        const centerX = (scaledX1 + scaledX2) / 2;
        const centerY = (scaledY1 + scaledY2) / 2;

        const trackId = getDisplayTrackId(track);
        const label = getTrackLabel(track);
        const confidence = typeof track.confidence === "number"
            ? Math.round(track.confidence * 100)
            : null;

        const isPredicted = Boolean(track.is_predicted);

        // Predicted tracks are objects that the Kalman filter is keeping alive
        // even though the detector missed them in the current frame.
        // We draw them with a dashed box.
        trackingCtx.save();

        trackingCtx.lineWidth = 3;
        trackingCtx.strokeStyle = isPredicted
            ? 'rgba(255, 165, 0, 0.9)'
            : 'rgba(0, 255, 0, 0.9)';

        if (isPredicted) {
            trackingCtx.setLineDash([8, 6]);
        } else {
            trackingCtx.setLineDash([]);
        }

        // Draw smoothed bounding box
        trackingCtx.strokeRect(scaledX1, scaledY1, width, height);

        // Draw center point
        trackingCtx.beginPath();
        trackingCtx.arc(centerX, centerY, 8, 0, 2 * Math.PI);
        trackingCtx.fillStyle = isPredicted
            ? 'rgba(255, 165, 0, 0.95)'
            : 'rgba(255, 0, 0, 0.95)';
        trackingCtx.fill();

        trackingCtx.lineWidth = 2;
        trackingCtx.strokeStyle = 'white';
        trackingCtx.stroke();

        // Draw label background
        const text = confidence !== null
            ? `${label} ID ${trackId} ${confidence}%`
            : `${label} ID ${trackId}`;

        trackingCtx.font = 'bold 16px Arial';
        const textWidth = trackingCtx.measureText(text).width;
        const textHeight = 22;

        const labelX = scaledX1;
        const labelY = Math.max(0, scaledY1 - textHeight);

        trackingCtx.fillStyle = isPredicted
            ? 'rgba(255, 165, 0, 0.9)'
            : 'rgba(0, 160, 0, 0.9)';

        trackingCtx.fillRect(labelX, labelY, textWidth + 12, textHeight);

        // Draw label text
        trackingCtx.fillStyle = 'white';
        trackingCtx.textAlign = 'left';
        trackingCtx.textBaseline = 'middle';
        trackingCtx.fillText(text, labelX + 6, labelY + textHeight / 2);

        trackingCtx.restore();
    });
}


// Helper 
function normalizeTracksMessage(message) {
    if (!message) {
        return [];
    }

    // Some frameworks wrap the real payload
    if (message.payload) {
        return normalizeTracksMessage(message.payload);
    }

    // Format: { tracks: [...] }
    if (Array.isArray(message.tracks)) {
        return message.tracks;
    }

    // Format: { detections: [...] }
    if (Array.isArray(message.detections)) {
        return message.detections;
    }

    // Format: direct array
    if (Array.isArray(message)) {
        return message;
    }

    // Format: one track object
    if (
        message.bounding_box_xyxy ||
        message.raw_bounding_box_xyxy ||
        message.bbox
    ) {
        return [message];
    }

    // Format: grouped by label
    // Example: { vehicle: [{...}, {...}] }
    const tracks = [];

    Object.keys(message).forEach((label) => {
        const objects = message[label];

        if (Array.isArray(objects)) {
            objects.forEach((obj) => {
                tracks.push({
                    ...obj,
                    label: obj.label || label,
                });
            });
        }
    });

    return tracks;
}

function getTrackBoundingBox(track) {
    const bbox =
        track.bounding_box_xyxy ||
        track.raw_bounding_box_xyxy ||
        track.bbox;

    if (!Array.isArray(bbox) || bbox.length !== 4) {
        return null;
    }

    return bbox.map(Number);
}

function getTrackLabel(track) {
    return track.label || track.content || track.detector_label || "vehicle";
}

function getBackendTrackKey(track) {
    if (track.track_id !== undefined && track.track_id !== null) {
        return `backend-${track.track_id}`;
    }

    if (track.id !== undefined && track.id !== null) {
        return `backend-${track.id}`;
    }

    return null;
}

function getDisplayTrackId(track) {
    if (track.track_id !== undefined && track.track_id !== null) {
        return track.track_id;
    }

    if (track.id !== undefined && track.id !== null) {
        return track.id;
    }

    if (track._ui_display_id !== undefined && track._ui_display_id !== null) {
        return track._ui_display_id;
    }

    return "?";
}

function computeIoU(a, b) {
    const [ax1, ay1, ax2, ay2] = a;
    const [bx1, by1, bx2, by2] = b;

    const ix1 = Math.max(ax1, bx1);
    const iy1 = Math.max(ay1, by1);
    const ix2 = Math.min(ax2, bx2);
    const iy2 = Math.min(ay2, by2);

    const iw = Math.max(0, ix2 - ix1);
    const ih = Math.max(0, iy2 - iy1);

    const intersection = iw * ih;

    const areaA = Math.max(0, ax2 - ax1) * Math.max(0, ay2 - ay1);
    const areaB = Math.max(0, bx2 - bx1) * Math.max(0, by2 - by1);

    const union = areaA + areaB - intersection;

    if (union <= 0) {
        return 0;
    }

    return intersection / union;
}

function centerDistance(a, b) {
    const acx = (a[0] + a[2]) / 2;
    const acy = (a[1] + a[3]) / 2;

    const bcx = (b[0] + b[2]) / 2;
    const bcy = (b[1] + b[3]) / 2;

    const dx = acx - bcx;
    const dy = acy - bcy;

    return Math.sqrt(dx * dx + dy * dy);
}

function getStableTrackKey(track, bbox, usedKeys) {
    // Best case: backend/Kalman gives a real track ID.
    const backendKey = getBackendTrackKey(track);
    if (backendKey) {
        return {
            key: backendKey,
            displayId: track.track_id ?? track.id,
        };
    }

    // Fallback case:
    // Backend does not provide track_id, so the UI tries to match this
    // detection to an existing visible track using IoU and center distance.
    let bestKey = null;
    let bestDisplayId = null;
    let bestScore = -Infinity;

    activeTracks.forEach((entry, key) => {
        if (usedKeys.has(key)) {
            return;
        }

        const oldTrack = entry.track;
        const oldBox = getTrackBoundingBox(oldTrack);

        if (!oldBox) {
            return;
        }

        const iou = computeIoU(bbox, oldBox);
        const distance = centerDistance(bbox, oldBox);

        const currentWidth = Math.abs(bbox[2] - bbox[0]);
        const currentHeight = Math.abs(bbox[3] - bbox[1]);
        const oldWidth = Math.abs(oldBox[2] - oldBox[0]);
        const oldHeight = Math.abs(oldBox[3] - oldBox[1]);

        const sizeLimit = Math.max(
            UI_MATCH_MIN_DISTANCE,
            currentWidth,
            currentHeight,
            oldWidth,
            oldHeight
        );

        const isCloseEnough = distance <= sizeLimit;
        const overlapsEnough = iou >= UI_MATCH_IOU_THRESHOLD;

        if (!isCloseEnough && !overlapsEnough) {
            return;
        }

        // Higher IoU is better, smaller distance is better.
        const score = iou * 1000 - distance;

        if (score > bestScore) {
            bestScore = score;
            bestKey = key;
            bestDisplayId = oldTrack._ui_display_id;
        }
    });

    if (bestKey) {
        return {
            key: bestKey,
            displayId: bestDisplayId,
        };
    }

    const newDisplayId = nextUiTrackId++;

    return {
        key: `ui-${newDisplayId}`,
        displayId: newDisplayId,
    };
}

function updateActiveTracks(tracks) {
    const now = Date.now();
    const usedKeys = new Set();

    tracks.forEach((track) => {
        const bbox = getTrackBoundingBox(track);

        if (!bbox) {
            return;
        }

        const stable = getStableTrackKey(track, bbox, usedKeys);
        usedKeys.add(stable.key);

        activeTracks.set(stable.key, {
            track: {
                ...track,
                _ui_track_key: stable.key,
                _ui_display_id: stable.displayId,
            },
            lastSeen: now,
        });
    });

    removeExpiredTracks();
}

function removeExpiredTracks() {
    const now = Date.now();

    activeTracks.forEach((entry, trackId) => {
        if (now - entry.lastSeen > TRACK_TTL_MS) {
            activeTracks.delete(trackId);
        }
    });
}

function getVisibleTracks() {
    removeExpiredTracks();
    return Array.from(activeTracks.values()).map(entry => entry.track);
}