function refresh() {
    const img = document.getElementById("cam");
    const newImg = new Image();

    newImg.onload = function() {
        img.src = newImg.src;
        setTimeout(refresh, 0); // Load next image once previous image is loaded
    };

    newImg.onerror = function() {
        setTimeout(refresh, 200); // Retry 200ms later if failed to load img
    };

    // Cache-busting : timestamp within URL
    newImg.src = "/latest.jpg?t=" + Date.now();
}

refresh();