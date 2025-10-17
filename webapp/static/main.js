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

// Updates to perform as a result of an automaton metadata message
const updateMetadata = (metadata) => {
    updateSubtitle(metadata.subtitle);
    updateIterations(metadata.iterationIndex, metadata.totalIterations);
};

const updateSubtitle = (subtitle) => {
    const subtitleSpan = document.getElementById("subtitle");
    subtitleSpan.textContent = subtitle;
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