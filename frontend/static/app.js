const pad = document.getElementById("pad");
const status = document.getElementById("status");
const settingsButton =
document.getElementById("settingsButton");
let SCREEN_WIDTH = 1920;
let SCREEN_HEIGHT = 1080;

const settingsPanel =
document.getElementById("settingsPanel");

settingsButton.addEventListener("click", () => {
settingsPanel.classList.toggle("open");
});

const ws = new WebSocket(
    `ws://${location.host}/ws`
);


ws.onopen = () => {
    status.textContent = "Connected";
};


ws.onclose = () => {
    status.textContent = "Disconnected";
};

async function setupScreenRect() {
    const ratio = SCREEN_WIDTH / SCREEN_HEIGHT;

    const padWidth = pad.clientWidth;
    const padHeight = pad.clientHeight;

    let width;
    let height;

    if (padWidth / padHeight > ratio) {
        height = padHeight;
        width = height * ratio;
    } else {
        width = padWidth;
        height = width / ratio;
    }

    const rect = document.getElementById("screenRect");

    rect.style.width = `${width}px`;
    rect.style.height = `${height}px`;

    rect.style.left = `${(padWidth - width) / 2}px`;
    rect.style.top = `${(padHeight - height) / 2}px`;
}

setupScreenRect();
window.addEventListener("resize", setupScreenRect);

function send(data) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
    }
}


let lastTouchX = null;
let lastTouchY = null;
let pointerDown = false;

pad.addEventListener("pointerdown", event => {

    if (!isInsideScreenRect(event.clientX, event.clientY)) {
        return;
    }

    lastTouchX = event.clientX;
    lastTouchY = event.clientY;

    pointerDown = true;

    if (document.getElementById("mouseMode").value === "absolute") {

        const rect = document
		    .getElementById("screenRect")
		    .getBoundingClientRect();

		let x =
		    (event.clientX - rect.left) /
		    rect.width;

		let y =
		    (event.clientY - rect.top) /
		    rect.height;

        const xScale =
            parseFloat(document.getElementById("xScale").value);

        const yScale =
            parseFloat(document.getElementById("yScale").value);

        const xOffset =
            parseFloat(document.getElementById("xOffset").value);

        const yOffset =
            parseFloat(document.getElementById("yOffset").value);

        x = x * xScale + xOffset;
        y = y * yScale + yOffset;

        x = Math.max(0, Math.min(1, x));
        y = Math.max(0, Math.min(1, y));

        // اول موس را به محل لمس منتقل کن
        send({
            type: "move_absolute",
            x: x,
            y: y
        });
    }

    if (document.getElementById("clickEnabled").checked) {
        send({
            type: "mouse_down"
        });
    }
});


pad.addEventListener("pointermove", event => {

    if (!pointerDown && !isInsideScreenRect(event.clientX, event.clientY)) {
        return;
    }

    const mode =
        document.getElementById("mouseMode").value;


    // =========================
    // Absolute mode
    // =========================

    if (mode === "absolute") {

        const rect = document
		    .getElementById("screenRect")
		    .getBoundingClientRect();

		let x =
		    (event.clientX - rect.left) /
		    rect.width;

		let y =
		    (event.clientY - rect.top) /
		    rect.height;

        const xScale =
            parseFloat(
                document.getElementById("xScale").value
            );

        const yScale =
            parseFloat(
                document.getElementById("yScale").value
            );

        const xOffset =
            parseFloat(
                document.getElementById("xOffset").value
            );

        const yOffset =
            parseFloat(
                document.getElementById("yOffset").value
            );

        x = x * xScale + xOffset;
        y = y * yScale + yOffset;

        x = Math.max(0, Math.min(1, x));
        y = Math.max(0, Math.min(1, y));

        send({
            type: "move_absolute",
            x: x,
            y: y
        });

        return;
    }


    // =========================
    // Touchpad mode
    // =========================

    if (mode === "touchpad") {

        if (lastTouchX === null)
            return;

        const dx =
            event.clientX - lastTouchX;

        const dy =
            event.clientY - lastTouchY;

        lastTouchX = event.clientX;
        lastTouchY = event.clientY;

        send({
            type: "move_relative",
            dx: dx,
            dy: dy
        });
    }
});


pad.addEventListener("pointerup", () => {

    if (pointerDown) {
        send({
            type: "mouse_up"
        });
    }

    pointerDown = false;

    lastTouchX = null;
    lastTouchY = null;
});

pad.addEventListener("pointercancel", () => {

    if (pointerDown) {
        send({
            type: "mouse_up"
        });
    }

    pointerDown = false;

    lastTouchX = null;
    lastTouchY = null;
});

function isInsideScreenRect(x, y) {
    const rect = document
        .getElementById("screenRect")
        .getBoundingClientRect();

    return (
        x >= rect.left &&
        x <= rect.right &&
        y >= rect.top &&
        y <= rect.bottom
    );
}

function fullscreen() {
    document.documentElement.requestFullscreen();
}