// URLs das peças de alta qualidade do Lichess (tema cburnett) via GitHub RAW CDN
const PIECE_URLS = {
    'P': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/wP.svg',
    'R': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/wR.svg',
    'N': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/wN.svg',
    'B': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/wB.svg',
    'Q': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/wQ.svg',
    'K': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/wK.svg',
    'p': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/bP.svg',
    'r': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/bR.svg',
    'n': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/bN.svg',
    'b': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/bB.svg',
    'q': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/bQ.svg',
    'k': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/bK.svg'
};

const UNICODE_FALLBACK = {
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
};

// Estado da aplicação
let ws = null;
let currentRoomId = "";
let myColor = "white";
let myName = "";
let currentFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
let selectedSquare = null;
let targetSquare = null;
let isSubmitted = false;

// Elementos DOM
const lobbyModal = document.getElementById("lobby-modal");
const gameContainer = document.getElementById("game-container");
const chessboardEl = document.getElementById("chessboard");
const logEl = document.getElementById("battle-log");

// Seleção de cor no lobby
document.querySelectorAll(".color-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".color-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        myColor = btn.dataset.color;
    });
});

// Botão de Entrar
document.getElementById("btn-join").addEventListener("click", () => {
    myName = document.getElementById("player-name").value || "Jogador";
    currentRoomId = document.getElementById("room-id").value || "sala-1";
    
    document.getElementById("display-room-id").innerText = currentRoomId;
    const roleMap = { white: "⚪ Brancas", black: "⚫ Pretas", spectator: "👁️ Espectador" };
    document.getElementById("display-player-role").innerText = `${myName} (${roleMap[myColor]})`;
    
    if (myColor === "white") {
        document.getElementById("my-name").innerText = `${myName} (Brancas)`;
        document.getElementById("opponent-name").innerText = "Adversário (Pretas)";
    } else if (myColor === "black") {
        document.getElementById("my-name").innerText = `${myName} (Pretas)`;
        document.getElementById("opponent-name").innerText = "Adversário (Brancas)";
    }

    lobbyModal.classList.add("hidden");
    gameContainer.classList.remove("hidden");

    connectWebSocket();
});

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    ws = new WebSocket(`${protocol}//${host}/ws/game/${currentRoomId}/${myColor}`);

    ws.onopen = () => {
        addLog("Conectado ao servidor quântico de jogadas simultâneas.", "system");
        document.getElementById("connection-status").innerText = "🟢 Conectado";
        document.getElementById("connection-status").className = "badge badge-online";
    };

    ws.onclose = () => {
        addLog("Conexão perdida com o servidor. Reconectando...", "collision");
        document.getElementById("connection-status").innerText = "🔴 Desconectado";
        document.getElementById("connection-status").style.background = "rgba(255, 75, 75, 0.2)";
        setTimeout(connectWebSocket, 3000);
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleServerMessage(message);
    };
}

function handleServerMessage(msg) {
    const type = msg.type;
    const data = msg.data;

    if (type === "game_state") {
        currentFen = data.fen;
        renderBoard();
        updateReadyStatus(data.white_ready, data.black_ready);
        updateTimer(data.timer_seconds, data.turn_duration);
    } else if (type === "player_joined") {
        addLog(data.message, "system");
    } else if (type === "move_submitted") {
        updateReadyStatus(data.white_ready, data.black_ready);
        if (data.color === myColor) {
            isSubmitted = true;
            document.getElementById("btn-submit-move").disabled = true;
            document.getElementById("btn-submit-move").innerText = "JOGADA ENVIADA ✅";
            document.getElementById("my-badge").className = "status-badge ready";
            document.getElementById("my-badge").innerText = "⚡ Pronto!";
        }
    } else if (type === "timer_tick") {
        updateTimer(data.timer_seconds, 20);
        updateReadyStatus(data.white_ready, data.black_ready);
    } else if (type === "turn_resolved") {
        currentFen = data.fen;
        isSubmitted = false;
        selectedSquare = null;
        targetSquare = null;
        document.getElementById("selected-move-text").innerText = "Nenhuma peça selecionada";
        document.getElementById("btn-submit-move").disabled = true;
        document.getElementById("btn-submit-move").innerText = "CONFIRMAR JOGADA ⚡";
        
        // Exibir eventos de colisão ou captura
        if (data.events && data.events.length > 0) {
            data.events.forEach(ev => {
                const logType = ev.includes("COLISÃO") ? "collision" : ev.includes("VENCEM") ? "victory" : "system";
                addLog(ev, logType);
            });
            
            // Se houve colisão, animar o tabuleiro
            if (data.events.some(ev => ev.includes("COLISÃO"))) {
                triggerExplosionAnimation();
            }
        } else {
            addLog(`Turno resolvido: Brancas (${data.white_move_uci || 'Passou'}) vs Pretas (${data.black_move_uci || 'Passou'})`, "system");
        }

        renderBoard();
        updateReadyStatus(false, false);
    } else if (type === "game_over") {
        addLog(`🏆 FIM DE JOGO! ${data.reason}`, "victory");
        alert(`🏆 FIM DE JOGO!\n\n${data.reason}`);
    } else if (type === "error") {
        addLog(`⚠️ Erro: ${data.message}`, "collision");
        alert(`Erro: ${data.message}`);
    }
}

function updateReadyStatus(whiteReady, blackReady) {
    const myReady = myColor === "white" ? whiteReady : blackReady;
    const oppReady = myColor === "white" ? blackReady : whiteReady;

    const myBadge = document.getElementById("my-badge");
    const oppBadge = document.getElementById("opponent-badge");

    if (myReady) {
        myBadge.className = "status-badge ready";
        myBadge.innerText = "⚡ Pronto!";
    } else {
        myBadge.className = "status-badge thinking";
        myBadge.innerText = "🤔 Escolhendo Jogada...";
    }

    if (oppReady) {
        oppBadge.className = "status-badge ready";
        oppBadge.innerText = "⚡ Jogada Submetida!";
    } else {
        oppBadge.className = "status-badge thinking";
        oppBadge.innerText = "🤔 Pensando...";
    }
}

function updateTimer(seconds, total) {
    document.getElementById("timer-display").innerText = seconds;
    const bar = document.getElementById("timer-bar");
    const percent = Math.max(0, (seconds / total) * 100);
    bar.style.width = `${percent}%`;

    if (seconds <= 5) {
        bar.classList.add("urgent");
        document.querySelector(".timer-circle").style.borderColor = "#ff4b4b";
        document.querySelector(".timer-circle span").style.color = "#ff4b4b";
    } else {
        bar.classList.remove("urgent");
        document.querySelector(".timer-circle").style.borderColor = "#00f2fe";
        document.querySelector(".timer-circle span").style.color = "#00f2fe";
    }
}

function addLog(text, className = "system") {
    const entry = document.createElement("div");
    entry.className = `log-entry ${className}`;
    entry.innerText = text;
    logEl.prepend(entry);
}

function triggerExplosionAnimation() {
    const overlay = document.getElementById("explosion-overlay");
    overlay.classList.remove("hidden");
    chessboardEl.classList.add("square", "collision");
    setTimeout(() => {
        overlay.classList.add("hidden");
        chessboardEl.classList.remove("square", "collision");
    }, 1200);
}

// Renderizador do Tabuleiro 8x8 a partir de FEN
function renderBoard() {
    chessboardEl.innerHTML = "";
    const boardPart = currentFen.split(" ")[0];
    const ranks = boardPart.split("/");

    // Se jogar de Pretas, podemos inverter o tabuleiro se quisermos
    const isBlackView = myColor === "black";
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    const rankNumbers = [8, 7, 6, 5, 4, 3, 2, 1];

    for (let r = 0; r < 8; r++) {
        const rankIndex = isBlackView ? (7 - r) : r;
        const rankStr = ranks[rankIndex];
        let fileIndex = 0;

        for (let i = 0; i < rankStr.length; i++) {
            const char = rankStr[i];
            if (!isNaN(char)) {
                const emptyCount = parseInt(char, 10);
                for (let e = 0; e < emptyCount; e++) {
                    const actualFile = isBlackView ? (7 - fileIndex) : fileIndex;
                    createSquare(actualFile, rankNumbers[rankIndex], null);
                    fileIndex++;
                }
            } else {
                const actualFile = isBlackView ? (7 - fileIndex) : fileIndex;
                createSquare(actualFile, rankNumbers[rankIndex], char);
                fileIndex++;
            }
        }
    }
}

function createSquare(fileIdx, rankNum, pieceChar) {
    const fileChar = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][fileIdx];
    const sqName = `${fileChar}${rankNum}`;
    
    const sqEl = document.createElement("div");
    const isDark = (fileIdx + rankNum) % 2 === 0;
    sqEl.className = `square ${isDark ? 'dark' : 'light'}`;
    sqEl.dataset.square = sqName;

    if (selectedSquare === sqName) sqEl.classList.add("selected");
    if (targetSquare === sqName) sqEl.classList.add("target");

    if (pieceChar) {
        const pieceEl = document.createElement("div");
        pieceEl.className = "piece";
        pieceEl.style.backgroundImage = `url('${PIECE_URLS[pieceChar]}')`;
        pieceEl.innerText = UNICODE_FALLBACK[pieceChar] || "";
        pieceEl.style.color = "transparent"; // Esconde o fallback se a imagem carregar
        sqEl.appendChild(pieceEl);
    }

    sqEl.addEventListener("click", () => onSquareClick(sqName, pieceChar));
    chessboardEl.appendChild(sqEl);
}

function onSquareClick(sqName, pieceChar) {
    if (isSubmitted || myColor === "spectator") return;

    // Se clicou na mesma casa selecionada, desmarca
    if (selectedSquare === sqName) {
        selectedSquare = null;
        targetSquare = null;
        updateMoveControls();
        renderBoard();
        return;
    }

    // Se selecionou uma peça própria
    const isMyPiece = pieceChar && (
        (myColor === "white" && pieceChar === pieceChar.toUpperCase()) ||
        (myColor === "black" && pieceChar === pieceChar.toLowerCase())
    );

    if (isMyPiece) {
        selectedSquare = sqName;
        targetSquare = null;
    } else if (selectedSquare) {
        targetSquare = sqName;
    }

    updateMoveControls();
    renderBoard();
}

function updateMoveControls() {
    const textEl = document.getElementById("selected-move-text");
    const btnEl = document.getElementById("btn-submit-move");

    if (selectedSquare && targetSquare) {
        textEl.innerText = `Movimento selecionado: ${selectedSquare.toUpperCase()} ➔ ${targetSquare.toUpperCase()}`;
        btnEl.disabled = false;
    } else if (selectedSquare) {
        textEl.innerText = `Peça em ${selectedSquare.toUpperCase()} selecionada. Escolha o destino...`;
        btnEl.disabled = true;
    } else {
        textEl.innerText = "Nenhuma peça selecionada";
        btnEl.disabled = true;
    }
}

document.getElementById("btn-submit-move").addEventListener("click", () => {
    if (!selectedSquare || !targetSquare || isSubmitted) return;
    const uciMove = `${selectedSquare}${targetSquare}`;
    
    ws.send(JSON.stringify({
        type: "submit_move",
        data: { uci: uciMove }
    }));
});
