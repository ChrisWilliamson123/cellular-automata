const ws = new WebSocket(`ws://${location.host}/ws`);
ws.binaryType = "arraybuffer";

const canvas = document.getElementById("ca");
const ctx = canvas.getContext("2d");

ws.onmessage = (event) => {
    if (typeof event.data === "string") {
        // JSON messages will come through as strings
        const message = JSON.parse(event.data);
        if (message.type === "automatonMetadata") {
            const metadata = message.data;
            updateMetadata(metadata);
        } else if (message.type === "init") {
            const data = message.data;
            performInitialisation(data);
        } else if (message.type === "state") {
            const state = message.data;
            updateState(state)
        }
    } else {
        // Binary data (frame)
        const bytes = new Uint8ClampedArray(event.data);
        const imgData = new ImageData(bytes, 300, 300);
        ctx.putImageData(imgData, 0, 0);
    }
};

// Updates to perform as a result of a state message
const updateState = (state) => {
    updatePlayPauseButton(state.isPaused);
    updateRewindButton(state.isRewinding);
    updateFramerateMultiplier(state.framerateMultiplier);
};

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ] : null;
}

const areColoursEqual = (incomingColours) => {
    const coloursContainer = document.getElementById("coloursContainer");
    const pickers = Array.from(coloursContainer.getElementsByClassName("colourPicker"));
    const colours = pickers.map((p) => {
        const hexValue = p.value;
        const rgb = hexToRgb(hexValue);
        return rgb;
    });
    return JSON.stringify(colours) === JSON.stringify(incomingColours);
}

// Updates to perform as a result of an automaton metadata message
const updateMetadata = (metadata) => {
    updateSubtitle(metadata.subtitle);
    updateIterations(metadata.iterationIndex, metadata.totalIterations);
    updateRandomBinaryElements(metadata.isRandomBinaryAutomaton);

    // console.log(metadata.colours);
    const coloursContainer = document.getElementById("coloursContainer");
    if (!areColoursEqual(metadata.colours)) {
        coloursContainer.innerHTML = '';
        metadata.colours.forEach((colour, index) => {
            coloursContainer.innerHTML += `<input type="color" value="${rgbToHex(colour[0], colour[1], colour[2])}" id="colour${index}" class="colourPicker" />`
        });
    }

    document.querySelectorAll(".colourPicker").forEach((e) => {
        e.onchange = (e) => {
            // console.log(hexToRgb(e.target.value));
            sendColoursUpdate();
        };
    })
};

const sendColoursUpdate = () => {
    const coloursContainer = document.getElementById("coloursContainer");
    let colours = [];
    coloursContainer.querySelectorAll('.colourPicker').forEach((e) => {
        const rgb = hexToRgb(e.value);
        colours.push(rgb)
    });
    ws.send(JSON.stringify({ type: "changeColours", data: colours }));
}

const updateRandomBinaryElements = (isRandomBinaryAutomaton) => {
    const randomBinaryControlsContainer = document.getElementById('randomBinaryControlsContainer');
    if (isRandomBinaryAutomaton) {
        randomBinaryControlsContainer.classList.replace('d-none', 'd-flex');
    } else {
        randomBinaryControlsContainer.classList.replace('d-flex', 'd-none');
    }
};

const updateSubtitle = (subtitle) => {
    const subtitleSpan = document.getElementById("subtitle");
    const currentText = subtitleSpan.textContent;
    if (currentText !== subtitle) {
        subtitleSpan.textContent = subtitle;
    }
};

const updateIterations = (iterationIndex, totalIterations) => {
    const iterationsSpan = document.getElementById("iterations");
    iterationsSpan.textContent = `${iterationIndex + 1} / ${totalIterations}`;
};

// PLAY/PAUSE
const playPauseBtn = document.getElementById("playPauseBtn");
const playPauseIcon = document.getElementById("playPauseIcon");

playPauseBtn.onclick = () => {
    // Send message to server
    ws.send(JSON.stringify({ type: "togglePause" }));
    // Assume success
    if (playPauseIcon.classList.contains("bi-play-fill")) {
        updatePlayPauseButton(false);
    } else {
        updatePlayPauseButton(true);
    }
};

const updatePlayPauseButton = (isPaused) => {
    if (isPaused) {
        playPauseIcon.classList.remove("bi-pause-fill");
        playPauseIcon.classList.add("bi-play-fill");
    } else {
        playPauseIcon.classList.remove("bi-play-fill");
        playPauseIcon.classList.add("bi-pause-fill");
    }
};

// RESET
const resetBtn = document.getElementById("resetBtn");
resetBtn.onclick = () => {
    ws.send(JSON.stringify({ type: "reset" }));
};


// INITIALISATION
const performInitialisation = (initialisationData) => {
    const automataList = document.getElementById('automataList');

    automataList.innerHTML = initialisationData.automataNames.map((name, index) => {
        if (index == 0) {
            return `<li class="list-group-item automata-option active">${name}</li>`
        } else {
            return `<li class="list-group-item automata-option">${name}</li>`
        }
    }).join('');

    addAutomataClickEvents();
};

// CHANGING AUTOMATA
const addAutomataClickEvents = () => {
    document.querySelectorAll("#automataList .list-group-item").forEach(item => {
        item.addEventListener("click", () => {
            document.querySelectorAll("#automataList .list-group-item").forEach(i => i.classList.remove("active"));
            item.classList.add("active");
            ws.send(JSON.stringify({ type: "changeAutomaton", data: item.textContent.trim() }));
        });
    });
};

// CHANGING SPEED
document.querySelectorAll("#speedControls .btn").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll("#speedControls .btn").forEach(i => i.classList.remove("btn-secondary"));
        document.querySelectorAll("#speedControls .btn").forEach(i => i.classList.add("btn-outline-secondary"));
        item.classList.replace("btn-outline-secondary", "btn-secondary");
        ws.send(JSON.stringify({ type: "changeFramerateMultiplier", data: item.value }));
    });
});

const updateFramerateMultiplier = (multiplier) => {
    document.querySelectorAll("#speedControls .btn").forEach(item => {
        item.classList.remove("btn-secondary");
        item.classList.remove("btn-outline-secondary");
        if (item.value == multiplier) {
            item.classList.add("btn-secondary");
        } else {
            item.classList.add("btn-outline-secondary");
        }
    })
};

// REWIND
const rewindBtn = document.getElementById("rewindBtn");
const rewindIcon = document.getElementById("rewindIcon");

const updateRewindButton = (isRewinding) => {
    if (isRewinding) {
        rewindIcon.classList.replace("bi-rewind", "bi-rewind-fill");
        rewindBtn.classList.replace("btn-outline-secondary", "btn-secondary");
    } else {
        rewindIcon.classList.replace("bi-rewind-fill", "bi-rewind");
        rewindBtn.classList.replace("btn-secondary", "btn-outline-secondary");
    }
};

rewindBtn.onclick = () => {
    ws.send(JSON.stringify({ type: "toggleRewind" }));
    const isRewinding = !rewindIcon.classList.contains("bi-rewind-fill");
    updateRewindButton(isRewinding);
};

// RANDOMISE NOTATION
document.getElementById("randomiseNotationBtn").onclick = () => {
    ws.send(JSON.stringify({ type: "randomiseNotation" }));
}

// USER ENTERED NOTATION
document.getElementById("bsNotationForm").onsubmit = (e) => {
    e.preventDefault();
    const notation = document.getElementById("bsNotationInput").value;
    ws.send(JSON.stringify({ type: "submitNotation", data: notation }));
};