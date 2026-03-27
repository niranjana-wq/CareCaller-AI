let isCallActive = false;
let isProcessing = false; // Prevents recording while AI is speaking/thinking
let mediaRecorder;
let audioChunks = [];
let audioContext;
let analyser;
let micStream;

// Call State
let callState = {
    responses: {}, current_step: "greeting", question_index: 0, escalate: false, call_ended: false
};
let chatHistory = [];

const startBtn = document.getElementById("startCallBtn");
const endBtn = document.getElementById("endCallBtn");
const statusInd = document.getElementById("statusIndicator");
const volBar = document.getElementById("volBar");
const transcriptOut = document.getElementById("transcriptOutput");
const jsonOut = document.getElementById("jsonOutput");

startBtn.onclick = async () => {
    isCallActive = true;
    startBtn.style.display = "none";
    endBtn.style.display = "inline-block";
    statusInd.textContent = "Connecting...";
    
    callState = {responses: {}, current_step: "greeting", question_index: 0, escalate: false, call_ended: false};
    chatHistory = [];
    
    // Initial fetch to jumpstart
    await triggerAgentText("hello");
    // Connect microphone
    startListening();
};

endBtn.onclick = endCall;

async function triggerAgentText(text) {
    isProcessing = true;
    updateStatus("processing", "Agent Thinking...");
    
    chatHistory.push({role: "user", message: text});
    
    try {
        const res = await fetch("https://carecaller-backend.onrender.com/chat_text", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ user_text: text, state: callState, chat_history: chatHistory })
        });
        const data = await res.json();
        handleBackendResponse(data);
    } catch (e) {
        console.error("Backend error:", e);
        endCall();
    }
}

function handleBackendResponse(data) {
    callState = data.state;
    chatHistory.push({role: "agent", message: data.agent_text});
    
    transcriptOut.innerHTML = `<strong>AI Health Assistant:</strong> ${data.agent_text}`;
    jsonOut.textContent = JSON.stringify(callState.responses, null, 2);
    
    if (data.audio_b64) {
        updateStatus("speaking", "Agent Speaking...");
        const audio = new Audio("data:audio/mp3;base64," + data.audio_b64);
        audio.play().catch(e => console.error("Autoplay blocked:", e));
        
        audio.onended = () => {
            if (callState.call_ended) endCall();
            else resumeListening();
        };
    } else {
        if (callState.call_ended) endCall();
        else resumeListening();
    }
}

function resumeListening() {
    isProcessing = false;
    updateStatus("listening", "Listening... (Speak now)");
}

async function startListening() {
    try {
        micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
        alert("Microphone access required!");
        endCall();
        return;
    }
    
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(micStream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    let isSpeaking = false;
    let silenceTimer = null;
    
    mediaRecorder = new MediaRecorder(micStream);
    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
    
    mediaRecorder.onstop = async () => {
        if (!isCallActive) return;
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        audioChunks = [];
        
        if (audioBlob.size > 200) { 
            await submitAudio(audioBlob);
        } else {
            resumeListening();
        }
    };

    function runVAD() {
        if (!isCallActive) return;
        requestAnimationFrame(runVAD);
        
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
        let average = sum / dataArray.length;
        
        volBar.style.width = Math.min(100, average * 2) + "%";
        
        if (isProcessing) return; // Ignores audio if AI is talking
        
        const threshold = 25; // Adjusted sensitivity for laptop background noise
        
        if (average > threshold) {
            if (!isSpeaking) {
                isSpeaking = true;
                audioChunks = [];
                mediaRecorder.start();
                updateStatus("capturing", "🎙️ Capturing Speech...");
                
                // Safety: Force stop after 12 seconds even if noise continues
                setTimeout(() => {
                    if (isSpeaking) {
                        isSpeaking = false;
                        isProcessing = true;
                        mediaRecorder.stop();
                    }
                }, 12000);
            }
            clearTimeout(silenceTimer);
            silenceTimer = setTimeout(() => {
                if (isSpeaking) {
                    isSpeaking = false;
                    isProcessing = true; // Lock the mic!
                    mediaRecorder.stop();
                }
            }, 1500); // 1.5s of silence triggers sending to API
        }
    }
    runVAD();
}

async function submitAudio(blob) {
    updateStatus("processing", "Transcribing & Thinking...");
    transcriptOut.innerHTML = `<em>Processing your voice...</em>`;
    
    let formData = new FormData();
    formData.append("audio", blob, "audio.webm");
    formData.append("state", JSON.stringify(callState));
    formData.append("chat_history", JSON.stringify(chatHistory));
    
    try {
        const res = await fetch("/chat_audio", { method: "POST", body: formData });
        const data = await res.json();
        
        if (data.user_text && data.user_text.trim() !== "") {
            chatHistory.push({role: "user", message: data.user_text});
        }
        handleBackendResponse(data);
    } catch (e) {
        console.error(e);
        resumeListening();
    }
}

function updateStatus(className, text) {
    statusInd.className = "status " + className;
    statusInd.textContent = text;
}

function endCall() {
    isCallActive = false;
    isProcessing = true;
    if (micStream) micStream.getTracks().forEach(t => t.stop());
    if (audioContext) audioContext.close();
    
    startBtn.style.display = "inline-block";
    endBtn.style.display = "none";
    updateStatus("idle", "Call Ended");
    volBar.style.width = "0%";
}
