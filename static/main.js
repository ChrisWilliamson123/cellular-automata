const ws = new WebSocket(`ws://${location.host}/ws`);
ws.binaryType = "arraybuffer";

const canvas = document.getElementById("ca");
const ctx = canvas.getContext("2d");

ws.onmessage = (event) => {
    if (typeof event.data === "string") {
        // JSON messages will come through as strings
        const message = JSON.parse(event.data);
        if (message.type === "metadata") {
            const metadata = message.data;
            document.getElementById("subtitle").textContent = metadata.subtitle;
            document.getElementById("iterations").textContent = metadata.iterations;
        } else if (message.type === "init") {
            const data = message.data;
            updateFramerateContent(data.framerate);
        }
    } else {
        // Binary data (frame)
        const bytes = new Uint8ClampedArray(event.data);
        const imgData = new ImageData(bytes, 300, 300);
        ctx.putImageData(imgData, 0, 0);
    }
};

document.getElementById("toggle").onclick = () => {
    ws.send(JSON.stringify({ type: "toggle" }));
};

document.getElementById("reset").onclick = () => {
    ws.send(JSON.stringify({ type: "reset" }));
};

document.getElementById("rule").onchange = (e) => {
    ws.send(JSON.stringify({ type: "rule", rule: e.target.value }));
};

const slider = document.getElementById("framerateSlider");
const output = document.getElementById("framerateValue");
output.innerHTML = slider.value; // Display the default slider value
slider.oninput = (e) => {
    output.innerHTML = e.target.value;
    ws.send(JSON.stringify({ type: "framerate", framerate: e.target.value }));
}

function updateBSNotation(notation) {
    document.getElementById("bs-value").textContent = notation;
}

// Sidebar automata click selection
// document.querySelectorAll("#automataList .list-group-item").forEach(item => {
//   item.addEventListener("click", () => {
//     document.querySelectorAll("#automataList .list-group-item").forEach(i => i.classList.remove("active"));
//     item.classList.add("active");
//     ws.send(JSON.stringify({ type: "rule", rule: item.textContent.trim() }));
//   });
// });

// FRAMERATE HANDLING
const updateFramerateContent = (framerate) => {
    document.getElementById("framerateValue").textContent = framerate;
    document.getElementById("framerateSlider").value = framerate;
};