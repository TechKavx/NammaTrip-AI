const form = document.getElementById("tripForm");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const loadingText = document.getElementById("loadingText");
const shareTripButton = document.getElementById("shareTripBtn");
const shareStatus = document.getElementById("shareStatus");
let currentTripData = null;
let assistantContext = {
    city: null,
    currentPlace: null,
    itinerary: [],
    hiddenGems: [],
    messages: []
};

const askForm = document.getElementById("askForm");
const askInput = document.getElementById("askInput");
const askChatWindow = document.getElementById("askChatWindow");
const askSuggestions = document.getElementById("askSuggestions");
const askSendButton = document.getElementById("askSendButton");
const askStatus = document.getElementById("askStatus");
const numberOfPersonsInput = document.getElementById("numberOfPersons");
const budgetInput = document.getElementById("budget");
const totalBudgetDisplay = document.getElementById("totalBudget");

function getNumberOfPersons() {
    return Math.max(1, Number(numberOfPersonsInput?.value) || 1);
}

function getBudgetPerPerson() {
    return Math.max(0, Number(budgetInput?.value) || 0);
}

function calculateTotalBudget() {
    const totalBudget = getNumberOfPersons() * getBudgetPerPerson();
    if (totalBudgetDisplay) {
        totalBudgetDisplay.textContent = `₹${totalBudget}`;
    }
    return totalBudget;
}

if (numberOfPersonsInput) {
    numberOfPersonsInput.addEventListener("input", calculateTotalBudget);
}
if (budgetInput) {
    budgetInput.addEventListener("input", calculateTotalBudget);
}
calculateTotalBudget();

if (shareTripButton) {
    shareTripButton.addEventListener("click", shareTrip);
}

function clearCurrentTrip() {
    currentTripData = null;
    if (shareTripButton) {
        shareTripButton.disabled = true;
    }
}

form.addEventListener("input", clearCurrentTrip);
form.addEventListener("change", clearCurrentTrip);

if (askForm) {
    askForm.addEventListener("submit", event => {
        event.preventDefault();
        askNammaTrip();
    });
}

if (askSuggestions) {
    askSuggestions.addEventListener("click", event => {
        const suggestion = event.target.closest(".ask-suggestion");
        if (!suggestion) {
            return;
        }
        askInput.value = suggestion.dataset.question || suggestion.textContent.trim();
        askNammaTrip();
    });
}

document.querySelectorAll(".chip input").forEach(input => {
  input.addEventListener("change", () => {
    input.closest(".chip").classList.toggle("selected", input.checked);
  });
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const interests = [...document.querySelectorAll('input[type="checkbox"]:checked')].map(x => x.value);
  if (!interests.length) {
    alert("Please choose at least one interest.");
    return;
  }

  const transport = document.querySelector('input[name="transport"]:checked').value;
    const numberOfPersons = getNumberOfPersons();
    const budgetPerPerson = getBudgetPerPerson();
    const totalBudget = calculateTotalBudget();
  const payload = {
    city: document.getElementById("city").value || "Coimbatore",
        budget: budgetPerPerson,
        budget_per_person: budgetPerPerson,
        number_of_persons: numberOfPersons,
        total_budget: totalBudget,
    start: document.getElementById("start").value,
    end: document.getElementById("end").value,
    interests,
    transport
  };

  result.classList.add("hidden");
    clearCurrentTrip();
  loading.classList.remove("hidden");

  const steps = [
    "Understanding your interests...",
    "Finding suitable local places...",
    "Optimizing route and time...",
    "Checking live weather...",
    "Calculating your budget..."
  ];
  let i = 0;
  const interval = setInterval(() => {
    loadingText.textContent = steps[i++ % steps.length];
  }, 650);

  try {
    const response = await fetch("/api/plan", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)
    });
    const data = await response.json();

    clearInterval(interval);
    loading.classList.add("hidden");
    showResult(data);
  } catch(err) {
    clearInterval(interval);
    loading.classList.add("hidden");
    alert("Something went wrong. Make sure Flask is running.");
    console.error(err);
  }
});

function showResult(data) {
    currentTripData = Array.isArray(data.itinerary) && data.itinerary.length
        ? data
        : null;
    assistantContext.city = data.city || null;
    assistantContext.itinerary = Array.isArray(data.itinerary) ? data.itinerary : [];
    assistantContext.hiddenGems = Array.isArray(data.hidden_gems) ? data.hidden_gems : [];
    assistantContext.currentPlace = assistantContext.itinerary[0]?.name || null;
    assistantContext.messages = [];
    resetAssistantChat();
    if (shareTripButton) {
        shareTripButton.disabled = !currentTripData;
    }
  result.classList.remove("hidden");
  document.getElementById("resultTitle").textContent = `${data.city} — AI Trip Plan`;
    document.getElementById("resultPersons").textContent = data.number_of_persons ?? 1;
    document.getElementById("resultBudgetPerPerson").textContent = `₹${data.budget_per_person ?? data.total_budget ?? 0}`;
    document.getElementById("resultTotalBudget").textContent = `₹${data.total_budget ?? 0}`;
  document.getElementById("spent").textContent = `₹${data.spent}`;
  document.getElementById("remaining").textContent = `₹${data.remaining}`;
  document.getElementById("distance").textContent = `${data.distance} km`;
  document.getElementById("weather").textContent =
    data.weather.temperature === "—" ? data.weather.label : `${data.weather.label} • ${data.weather.temperature}°C`;
// Generate dynamic explanation
const whyPlanText = document.getElementById("whyPlanText");

if (whyPlanText) {

    const selectedInterests =
        [...document.querySelectorAll(
            '#tripForm input[type="checkbox"]:checked'
        )].map(input => input.value);

    const interestText =
        selectedInterests.length > 0
            ? selectedInterests.join(" + ")
            : "your selected interests";

    let weatherReason = "";

    if (data.weather.mode === "indoor") {

        weatherReason =
            "The weather is wet, so indoor-friendly places were given more importance.";

    } else if (data.weather.mode === "outdoor") {

        weatherReason =
            "The current weather is suitable for outdoor activities.";

    } else {

        weatherReason =
            "The current weather was also considered while selecting places.";
    }

    whyPlanText.innerHTML = `
        <strong>💡 Here's why:</strong><br><br>

        Your plan prioritizes
        <strong>${interestText}</strong>
        based on your interests.

        The itinerary uses approximately
        <strong>₹${data.spent}</strong>
        of your budget, leaving
        <strong>₹${data.remaining}</strong>
        remaining.

        ${weatherReason}
    `;
}
  const timeline = document.getElementById("timeline");
  timeline.innerHTML = "";

  if (!data.itinerary.length) {
    timeline.innerHTML = `<p>No suitable places fit the selected time/budget. Try increasing the budget or trip duration.</p>`;
    return;
  }

  data.itinerary.forEach((p, index) => {
    const div = document.createElement("div");
    div.className = "stop";
    div.innerHTML = `
      <div class="dot"></div>
      <div class="time">${p.start} – ${p.end}</div>
      <h3>${index+1}. ${p.name}</h3>
      <p>${p.description}</p>
      <div class="meta">
        <span>🚗 ${p.distance} km travel</span>
        <span>⏱️ ${p.duration} min visit</span>
        <span>💰 ₹${p.cost}</span>
      </div>
    `;
    timeline.appendChild(div);
  });
  renderMap(data.itinerary);
  renderHiddenGems(data.hidden_gems);

  result.scrollIntoView({behavior:"smooth"});
}

function resetAssistantChat() {
    if (!askChatWindow) {
        return;
    }
    askChatWindow.innerHTML = `
        <div class="ask-message assistant-message">
            <div class="ask-avatar">🤖</div>
            <div class="ask-bubble">
                <strong>NammaTrip</strong>
                <p>${assistantContext.city ? `Hi! 👋 Ask me anything about your ${assistantContext.city} trip.` : "Hi! 👋 Ask me anything about your destination."}</p>
            </div>
        </div>
    `;
    renderAssistantSuggestions([
        "🕐 Opening hours",
        "🍴 Nearby food",
        "🏨 Hotels nearby",
        "📍 What's nearby?",
        "🎯 Things to do"
    ]);
}

function appendAssistantMessage(type, text) {
    const message = document.createElement("div");
    message.className = `ask-message ${type}-message`;
    const avatar = type === "user" ? "👤" : "🤖";
    const label = type === "user" ? "You" : "NammaTrip";
    message.innerHTML = `
        <div class="ask-avatar">${avatar}</div>
        <div class="ask-bubble">
            <strong>${label}</strong>
            <p></p>
        </div>
    `;
    message.querySelector("p").textContent = text;
    askChatWindow.appendChild(message);
    askChatWindow.scrollTop = askChatWindow.scrollHeight;
}

function appendAssistantLoading() {
    const loadingMessage = document.createElement("div");
    loadingMessage.className = "ask-message assistant-message ask-thinking";
    loadingMessage.innerHTML = `
        <div class="ask-avatar">🤖</div>
        <div class="ask-bubble"><strong>NammaTrip</strong><p><span class="ask-dots"><i></i><i></i><i></i></span> NammaTrip is thinking...</p></div>
    `;
    askChatWindow.appendChild(loadingMessage);
    askChatWindow.scrollTop = askChatWindow.scrollHeight;
    return loadingMessage;
}

function renderAssistantSuggestions(suggestions) {
    if (!askSuggestions) {
        return;
    }
    askSuggestions.innerHTML = "";
    suggestions.slice(0, 5).forEach(question => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "ask-suggestion";
        button.dataset.question = question;
        button.textContent = question;
        askSuggestions.appendChild(button);
    });
}

function assistantResultIcon(result) {
    const icons = {
        hotel: "🏨",
        restaurant: "🍴",
        cafe: "☕",
        shopping: "🛍️",
        attraction: "📍"
    };
    return icons[result.type] || "📌";
}

function renderAssistantResults(results) {
    if (!results || !results.length) {
        return;
    }
    const resultsContainer = document.createElement("div");
    resultsContainer.className = "ask-results";
    results.forEach(resultItem => {
        const card = document.createElement("article");
        card.className = "ask-result-card";
        card.innerHTML = `
            <div class="ask-result-title"><span>${assistantResultIcon(resultItem)}</span><strong></strong></div>
            <div class="ask-result-meta"></div>
            <p></p>
        `;
        card.querySelector("strong").textContent = resultItem.name || "Local option";
        const meta = [];
        if (typeof resultItem.distance === "number") {
            meta.push(`📍 ${resultItem.distance} km away`);
        }
        if (resultItem.price_level) {
            meta.push(`💰 ${resultItem.price_level}`);
        }
        card.querySelector(".ask-result-meta").textContent = meta.join("  •  ");
        card.querySelector("p").textContent = resultItem.description || "Demo dataset information.";
        resultsContainer.appendChild(card);
    });
    askChatWindow.appendChild(resultsContainer);
    askChatWindow.scrollTop = askChatWindow.scrollHeight;
}

async function askNammaTrip() {
    const message = askInput?.value.trim();
    if (!message || !askSendButton) {
        return;
    }

    const city = currentTripData?.city || document.getElementById("city")?.value || "Coimbatore";
    appendAssistantMessage("user", message);
    assistantContext.messages.push({role: "user", content: message});
    askInput.value = "";
    askSendButton.disabled = true;
    askStatus.textContent = "NammaTrip is checking your local travel data...";
    const loadingMessage = appendAssistantLoading();

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                message,
                city,
                current_place: assistantContext.currentPlace || "",
                itinerary: assistantContext.itinerary
            })
        });
        if (!response.ok) {
            throw new Error("Ask NammaTrip request failed");
        }
        const data = await response.json();
        loadingMessage.remove();
        appendAssistantMessage("assistant", data.answer || "I could not find an answer for that yet.");
        renderAssistantResults(Array.isArray(data.results) ? data.results : []);
        renderAssistantSuggestions(Array.isArray(data.suggestions) && data.suggestions.length
            ? data.suggestions
            : ["Tell me about this place", "What is nearby?", "What can I do there?"]);
        if (data.place) {
            assistantContext.currentPlace = data.place;
        }
        assistantContext.messages.push({role: "assistant", content: data.answer || ""});
        askStatus.textContent = assistantContext.city
            ? `Using your ${assistantContext.city} trip context.`
            : "Ask another local travel question.";
    } catch (error) {
        loadingMessage.remove();
        appendAssistantMessage("assistant", "I could not reach the travel assistant. Please try again.");
        askStatus.textContent = "The assistant is temporarily unavailable.";
        console.error("Ask NammaTrip failed:", error);
    } finally {
        askSendButton.disabled = false;
        askInput.focus();
    }
}

function generateShareText(data) {
    const weather = data.weather.temperature === "—"
        ? data.weather.label
        : `${data.weather.label} • ${data.weather.temperature}°C`;
    const itinerary = data.itinerary.length
        ? data.itinerary.map((place, index) => `
${index + 1}. ${place.name}
⏰ ${place.start} – ${place.end}
⏱️ ${place.duration} min
💰 ₹${place.cost}`).join("\n")
        : "\nNo suitable places were found for the selected time and budget.";
    const hiddenGems = data.hidden_gems && data.hidden_gems.length
        ? `\n\n✨ Hidden Gems\n\n${data.hidden_gems.map(gem => `- ${gem.name}`).join("\n")}`
        : "";

    return `🌍 NammaTrip AI — My Trip Plan

📍 Destination: ${data.city}

👥 Number of Persons: ${data.number_of_persons ?? 1}
💰 Budget Per Person: ₹${data.budget_per_person ?? 0}
🧾 Total Budget: ₹${data.total_budget ?? 0}
💳 Estimated Trip Cost: ₹${data.total_spent ?? data.spent}
💵 Budget Remaining: ₹${data.remaining}
🛣️ Total Travel: ${data.distance} km
🌦️ Weather: ${weather}

🗓️ Itinerary
${itinerary}${hiddenGems}

Plan created with NammaTrip AI ✨`;
}

function showShareStatus(message, isError = false) {
    if (!shareStatus) {
        return;
    }

    shareStatus.textContent = message;
    shareStatus.classList.toggle("share-status-error", isError);
    window.clearTimeout(showShareStatus.timeout);
    showShareStatus.timeout = window.setTimeout(() => {
        shareStatus.textContent = "";
        shareStatus.classList.remove("share-status-error");
    }, 3000);
}

async function shareTrip() {
    if (!currentTripData) {
        showShareStatus("Generate a trip before sharing.", true);
        return;
    }

    const shareText = generateShareText(currentTripData);

    try {
        if (navigator.share) {
            await navigator.share({
                title: "NammaTrip AI — My Trip Plan",
                text: shareText
            });
            showShareStatus("Trip shared successfully!");
            return;
        }

        await navigator.clipboard.writeText(shareText);
        showShareStatus("Trip copied to clipboard!");
    } catch (error) {
        if (error.name === "AbortError") {
            return;
        }
        showShareStatus("Unable to share this trip. Please try again.", true);
        console.error("Trip sharing failed:", error);
    }
}

function renderMap(itinerary) {

    if (!itinerary || itinerary.length === 0) {
        return;
    }

    // Create the map
    const mapElement = document.getElementById("map");

    if (!mapElement) {
        return;
    }

    // Remove old map if user generates another trip
    if (window.tripMap) {
        window.tripMap.remove();
    }

    window.tripMap = L.map("map");

    // OpenStreetMap tiles
    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: '&copy; OpenStreetMap contributors'
        }
    ).addTo(window.tripMap);

    // Store route coordinates
    const routeCoordinates = [];

    // Add markers
    itinerary.forEach((place, index) => {

        const lat = place.lat;
        const lon = place.lon;

        routeCoordinates.push([lat, lon]);

        const marker = L.marker([lat, lon]).addTo(window.tripMap);

        marker.bindPopup(`
            <div class="map-place">
                ${index + 1}. ${place.name}
            </div>
            <p>${place.start} – ${place.end}</p>
            <p>💰 ₹${place.cost}</p>
        `);

        // Open first place automatically
        if (index === 0) {
            marker.openPopup();
        }
    });

    // Draw route line
    if (routeCoordinates.length > 1) {

        L.polyline(
            routeCoordinates,
            {
                weight: 5,
                opacity: 0.8
            }
        ).addTo(window.tripMap);
    }

    // Fit map to all locations
    if (routeCoordinates.length === 1) {

        window.tripMap.setView(
            routeCoordinates[0],
            14
        );

    } else {

        window.tripMap.fitBounds(
            routeCoordinates,
            {
                padding: [40, 40]
            }
        );
    }
}// ================================
// NATURAL LANGUAGE AI ASSISTANT
// ================================

const aiGenerateBtn = document.getElementById("aiGenerateBtn");
const aiPrompt = document.getElementById("aiPrompt");
const aiStatus = document.getElementById("aiStatus");

if (aiGenerateBtn) {

    aiGenerateBtn.addEventListener("click", async () => {

        const text = aiPrompt.value.trim();

        if (!text) {
            aiStatus.textContent = "Please describe your trip first.";
            return;
        }

        aiStatus.textContent = "✨ Understanding your trip...";

        const trip = understandTrip(text);

        // Show what the assistant understood
        aiStatus.textContent =
            `Got it! ${trip.city}, ${trip.persons} person${trip.persons === 1 ? "" : "s"}, ₹${trip.budget} per person, ${trip.hours} hours — ${trip.interests.join(", ")}.`;

        // Fill the normal planner form
        document.getElementById("city").value = trip.city;
        document.getElementById("budget").value = trip.budget;
        document.getElementById("numberOfPersons").value = trip.persons;
        calculateTotalBudget();

        // Set start and end time
        document.getElementById("start").value = trip.start;
        document.getElementById("end").value = trip.end;

        // Clear existing interests
        document.querySelectorAll(
            '#tripForm input[type="checkbox"]'
        ).forEach(input => {
            input.checked = false;
            input.closest(".chip")?.classList.remove("selected");
        });

        // Select detected interests
        trip.interests.forEach(interest => {

            const checkbox = document.querySelector(
                `#tripForm input[type="checkbox"][value="${interest}"]`
            );

            if (checkbox) {
                checkbox.checked = true;
                checkbox.closest(".chip")?.classList.add("selected");
            }
        });

        // Automatically submit the existing planner
        form.dispatchEvent(new Event("submit"));
    });
}


// =================================
// UNDERSTAND USER'S TRIP REQUEST
// =================================

function understandTrip(text) {

    const lower = text.toLowerCase();
    // =================================
// TAMIL LANGUAGE SUPPORT
// =================================

const tamilText = lower;

const tamilInterestKeywords = {

    food: [
        "சாப்பாடு",
        "சாப்பிட",
        "உணவு",
        "ஹோட்டல்",
        "ஹோட்டல்கள்"
    ],

    nature: [
        "இயற்கை",
        "மலை",
        "ஏரி",
        "நீர்வீழ்ச்சி",
        "பசுமை",
        "இயற்கையான"
    ],

    photography: [
        "புகைப்படம்",
        "போட்டோ",
        "போட்டோகிராபி",
        "புகைப்படங்கள்"
    ],

    spiritual: [
        "கோவில்",
        "கோயில்",
        "ஆன்மீகம்",
        "சாமி"
    ],

    history: [
        "வரலாறு",
        "வரலாற்று",
        "அருங்காட்சியகம்"
    ],

    shopping: [
        "ஷாப்பிங்",
        "கடைகள்",
        "கடை"
    ],

    adventure: [
        "சாகசம்",
        "அட்வென்ச்சர்",
        "வாட்டர் பார்க்"
    ],

    family: [
        "குடும்பம்",
        "குழந்தைகள்"
    ]
};

    // -------------------------------
    // CITY DETECTION
    // -------------------------------

    let city = "Coimbatore";
    // Tamil city names

if (
    tamilText.includes("கோயம்புத்தூர்") ||
    tamilText.includes("கோவை")
) {
    city = "Coimbatore";
}

if (tamilText.includes("சென்னை")) {
    city = "Chennai";
}

if (tamilText.includes("மதுரை")) {
    city = "Madurai";
}

if (tamilText.includes("ஊட்டி")) {
    city = "Ooty";
}

    const cities = [
        "coimbatore",
        "chennai",
        "madurai",
        "ooty",
        "bangalore"
    ];

    for (const c of cities) {

        if (lower.includes(c)) {
            city = c.charAt(0).toUpperCase() + c.slice(1);
            break;
        }
    }


    // -------------------------------
    // BUDGET DETECTION
    // -------------------------------

    let budget = 1500;
    // Tamil / Indian rupee phrases

const tamilBudgetMatch = lower.match(
    /(?:₹|ரூபாய்|ரூ)\s*(\d{2,5})/
);

if (tamilBudgetMatch) {
    budget = Number(tamilBudgetMatch[1]);
}

    const budgetMatch = lower.match(
        /(?:₹|rs\.?|rupees?)\s?(\d{2,5})/
    );

    if (budgetMatch) {
        budget = Number(budgetMatch[1]);
    }

    // Also detect phrases like:
    // budget 1000
    // under 1500

    const budgetWordMatch = lower.match(
        /(?:budget|under|within)\s*(?:₹|rs\.?|rupees?)?\s*(\d{2,5})/
    );

    if (budgetWordMatch) {
        budget = Number(budgetWordMatch[1]);
    }

    let persons = 1;
    const personsMatch = lower.match(
        /(?:for|with|party of|persons?|people|members?)\s*(\d{1,2})|\b(\d{1,2})\s*(?:persons?|people|members?)\b/
    );
    if (personsMatch) {
        persons = Number(personsMatch[1] || personsMatch[2]);
    }


    // -------------------------------
    // TIME / HOURS DETECTION
    // -------------------------------

    // -------------------------------
// TIME / HOURS DETECTION
// -------------------------------

let hours = 6;

// English
const hourMatch = lower.match(
    /(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)/
);

if (hourMatch) {
    hours = Number(hourMatch[1]);
}

// Tamil
const tamilHourMatch = lower.match(
    /(\d+(?:\.\d+)?)\s*(?:மணி\s*நேரம்|மணி)/
);

if (tamilHourMatch) {
    hours = Number(tamilHourMatch[1]);
}


    // -------------------------------
    // START TIME
    // -------------------------------

    // -------------------------------
// START TIME
// -------------------------------

let start = "10:00";

// English time
const timeMatch = lower.match(
    /(?:at|from|starting)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/
);

if (timeMatch) {

    let hour = Number(timeMatch[1]);

    const minute = timeMatch[2]
        ? Number(timeMatch[2])
        : 0;

    const period = timeMatch[3];

    if (period === "pm" && hour < 12) {
        hour += 12;
    }

    if (period === "am" && hour === 12) {
        hour = 0;
    }

    start =
        `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}


// Tamil morning / evening time
const tamilTimeMatch = lower.match(
    /(?:காலை|மதியம்|மாலை|இரவு)\s*(\d{1,2})(?::(\d{2}))?/
);

if (tamilTimeMatch) {

    let hour = Number(tamilTimeMatch[1]);

    const minute = tamilTimeMatch[2]
        ? Number(tamilTimeMatch[2])
        : 0;

    if (
        lower.includes("மாலை") ||
        lower.includes("இரவு")
    ) {
        if (hour < 12) {
            hour += 12;
        }
    }

    if (
        lower.includes("காலை") &&
        hour === 12
    ) {
        hour = 0;
    }

    start =
        `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

    // -------------------------------
    // CALCULATE END TIME
    // -------------------------------

    const [startHour, startMinute] = start
        .split(":")
        .map(Number);

    const startTotal =
        startHour * 60 + startMinute;

    let endTotal =
        startTotal + Math.round(hours * 60);

    // Keep inside same day
    endTotal = Math.min(endTotal, 23 * 60 + 30);

    const endHour =
        Math.floor(endTotal / 60);

    const endMinute =
        endTotal % 60;

    const end =
        `${String(endHour).padStart(2, "0")}:${String(endMinute).padStart(2, "0")}`;


    // -------------------------------
    // INTEREST DETECTION
    // -------------------------------

    const interests = [];

    const interestKeywords = {

        food: [
            "food",
            "foods",
            "eat",
            "eating",
            "restaurant",
            "restaurants",
            "foodie",
            "cafe",
            "cafes"
        ],

        photography: [
            "photography",
            "photo",
            "photos",
            "photogenic",
            "instagram",
            "instagrammable"
        ],

        nature: [
            "nature",
            "greenery",
            "mountain",
            "mountains",
            "lake",
            "waterfall",
            "scenery",
            "scenic"
        ],

        spiritual: [
            "temple",
            "temples",
            "spiritual",
            "religious",
            "prayer"
        ],

        history: [
            "history",
            "historical",
            "museum",
            "heritage"
        ],

        shopping: [
            "shopping",
            "mall",
            "malls",
            "shop"
        ],

        adventure: [
            "adventure",
            "adventurous",
            "water park",
            "activities"
        ],

        family: [
            "family",
            "kids",
            "children"
        ],

        indoor: [
            "indoor",
            "indoors",
            "rain",
            "rainy",
            "hot"
        ]
    };


    for (const [interest, keywords] of Object.entries(interestKeywords)) {
      // Detect Tamil interests

for (
    const [interest, keywords]
    of Object.entries(tamilInterestKeywords)
) {

    for (const keyword of keywords) {

        if (tamilText.includes(keyword)) {

            if (!interests.includes(interest)) {
                interests.push(interest);
            }

            break;
        }
    }
}

        for (const keyword of keywords) {

            if (lower.includes(keyword)) {

                if (!interests.includes(interest)) {
                    interests.push(interest);
                }

                break;
            }
        }
    }


    // Default interests
    if (interests.length === 0) {
        interests.push("nature", "photography");
    }


    // -------------------------------
    // RETURN STRUCTURED TRIP
    // -------------------------------

    return {
        city,
        budget,
        persons,
        hours,
        start,
        end,
        interests
    };
}
// =====================================
// CHANGE MY PLAN
// =====================================

const changePlanBtn = document.getElementById("changePlanBtn");
const changePlanPanel = document.getElementById("changePlanPanel");
const regenerateBtn = document.getElementById("regenerateBtn");
const cancelChangeBtn = document.getElementById("cancelChangeBtn");
const changeStatus = document.getElementById("changeStatus");


// Open Change My Plan panel
if (changePlanBtn) {

    changePlanBtn.addEventListener("click", () => {

        changePlanPanel.classList.remove("hidden");

        // Get current values from main planner
        document.getElementById("changeBudget").value =
            document.getElementById("budget").value;

        document.getElementById("changePersons").value =
            document.getElementById("numberOfPersons").value;

        document.getElementById("changeStart").value =
            document.getElementById("start").value;

        document.getElementById("changeEnd").value =
            document.getElementById("end").value;

        // Copy current interests
        const currentInterests =
            [...document.querySelectorAll(
                '#tripForm input[type="checkbox"]:checked'
            )].map(input => input.value);

        document.querySelectorAll(
            '.change-chip input[type="checkbox"]'
        ).forEach(input => {

            input.checked =
                currentInterests.includes(input.value);

        });

        // Copy current transport
        const currentTransport =
            document.querySelector(
                '#tripForm input[name="transport"]:checked'
            );

        if (currentTransport) {

            const transportRadio =
                document.querySelector(
                    `input[name="changeTransport"][value="${currentTransport.value}"]`
                );

            if (transportRadio) {
                transportRadio.checked = true;
            }
        }

        changeStatus.textContent = "";

        changePlanPanel.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    });
}


// Cancel
if (cancelChangeBtn) {

    cancelChangeBtn.addEventListener("click", () => {

        changePlanPanel.classList.add("hidden");
        changeStatus.textContent = "";

    });
}


// Regenerate itinerary
if (regenerateBtn) {

    regenerateBtn.addEventListener("click", async () => {

        const budget =
            Number(document.getElementById("changeBudget").value);

        const numberOfPersons =
            Math.max(1, Number(document.getElementById("changePersons").value) || 1);

        const totalBudget =
            numberOfPersons * budget;

        const start =
            document.getElementById("changeStart").value;

        const end =
            document.getElementById("changeEnd").value;

        const interests =
            [...document.querySelectorAll(
                '.change-chip input[type="checkbox"]:checked'
            )].map(input => input.value);

        const transportInput =
            document.querySelector(
                'input[name="changeTransport"]:checked'
            );

        const transport =
            transportInput ? transportInput.value : "car";

        const city =
            document.getElementById("city").value ||
            "Coimbatore";


        // Validation
        if (!budget || budget <= 0) {

            changeStatus.textContent =
                "Please enter a valid budget.";

            return;
        }

        if (!start || !end) {

            changeStatus.textContent =
                "Please select your start and end time.";

            return;
        }

        if (interests.length === 0) {

            changeStatus.textContent =
                "Please select at least one interest.";

            return;
        }


        // Check time
        if (start >= end) {

            changeStatus.textContent =
                "End time must be after start time.";

            return;
        }


        changeStatus.textContent =
            "✨ Regenerating your personalized trip...";

        regenerateBtn.disabled = true;


        try {

            const response = await fetch("/api/plan", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    city: city,

                    budget: budget,

                    budget_per_person: budget,

                    number_of_persons: numberOfPersons,

                    total_budget: totalBudget,

                    start: start,

                    end: end,

                    interests: interests,

                    transport: transport

                })

            });


            if (!response.ok) {
                throw new Error("Failed to generate plan");
            }


            const data = await response.json();


            // Update main planner values
            document.getElementById("budget").value =
                budget;

            document.getElementById("numberOfPersons").value =
                numberOfPersons;

            calculateTotalBudget();

            document.getElementById("start").value =
                start;

            document.getElementById("end").value =
                end;


            // Update main interests
            document.querySelectorAll(
                '#tripForm input[type="checkbox"]'
            ).forEach(input => {

                input.checked =
                    interests.includes(input.value);

                input.closest(".chip")
                    ?.classList
                    .toggle("selected", input.checked);

            });


            // Update main transport
            const mainTransport =
                document.querySelector(
                    `#tripForm input[name="transport"][value="${transport}"]`
                );

            if (mainTransport) {
                mainTransport.checked = true;
            }


            // Display new itinerary
            showResult(data);


            changeStatus.textContent =
                "✅ Your trip has been updated!";


            // Close panel after short delay
            setTimeout(() => {

                changePlanPanel.classList.add("hidden");

            }, 800);


        } catch (error) {

            console.error(error);

            changeStatus.textContent =
                "❌ Could not regenerate the plan. Please try again.";

        } finally {

            regenerateBtn.disabled = false;

        }

    });
}
// =====================================
// HIDDEN GEMS
// =====================================

function renderHiddenGems(gems) {

    const container =
        document.getElementById("hiddenGems");

    if (!container) {
        return;
    }

    container.innerHTML = "";
    const hiddenGemStatus = document.getElementById("hiddenGemStatus");
    if (hiddenGemStatus) {
        hiddenGemStatus.textContent = "";
    }

    if (!gems || gems.length === 0) {

        container.innerHTML = `
            <p>
                No hidden gems matched your current preferences.
                Try changing your interests or budget.
            </p>
        `;

        return;
    }


    gems.forEach((gem, index) => {

        const card =
            document.createElement("div");

        card.className =
            "hidden-gem-card";


        const tags =
            gem.category
                .map(category => `
                    <span class="hidden-gem-tag">
                        ${category}
                    </span>
                `)
                .join("");

        const alreadyAdded = Boolean(
            currentTripData?.itinerary?.some(place => place.name === gem.name)
        );


        card.innerHTML = `

            <div class="hidden-gem-number">
                LOCAL GEM #${index + 1}
            </div>

            <h3>
                ${gem.name}
            </h3>

            <p>
                ${gem.description}
            </p>

            <span class="hidden-gem-cost">
                💰 ₹${gem.cost}
            </span>

            <div class="hidden-gem-tags">
                ${tags}
            </div>

            <button type="button" class="add-gem-btn" ${alreadyAdded ? "disabled" : ""}>
                ${alreadyAdded ? "Already added to your trip" : "➕ Add to My Trip"}
            </button>

        `;

        const addButton = card.querySelector(".add-gem-btn");
        if (!alreadyAdded) {
            addButton.addEventListener("click", () => addHiddenGemToTrip(gem.name, addButton));
        }


        container.appendChild(card);

    });
}

async function addHiddenGemToTrip(gemName, button) {
    if (!currentTripData) {
        showHiddenGemStatus("Please generate a trip plan first.", true);
        return;
    }

    if (currentTripData.itinerary.some(place => place.name === gemName)) {
        showHiddenGemStatus("Already added to your trip.", true);
        button.disabled = true;
        return;
    }

    const budgetPerPerson = Number(currentTripData.budget_per_person ?? getBudgetPerPerson());
    const numberOfPersons = Math.max(
        1,
        Number(currentTripData.number_of_persons ?? getNumberOfPersons()) || 1
    );
    const transport = currentTripData.transport
        || document.querySelector('input[name="transport"]:checked')?.value
        || "car";
    const interests = Array.isArray(currentTripData.interests)
        ? currentTripData.interests
        : [...document.querySelectorAll('#tripForm input[type="checkbox"]:checked')]
            .map(input => input.value);
    const payload = {
        city: currentTripData.city || document.getElementById("city").value,
        hidden_gem: gemName,
        number_of_persons: numberOfPersons,
        budget_per_person: budgetPerPerson,
        total_budget: numberOfPersons * budgetPerPerson,
        start: currentTripData.start || document.getElementById("start").value,
        end: currentTripData.end || document.getElementById("end").value,
        interests,
        transport,
        required_places: [gemName]
    };

    button.disabled = true;
    button.textContent = "Adding...";
    showHiddenGemStatus("Regenerating your itinerary with this Hidden Gem...");

    try {
        const response = await fetch("/api/add-hidden-gem", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok || data.success === false) {
            throw new Error(data.message || "This Hidden Gem could not be added.");
        }
        showResult(data);
        showHiddenGemStatus(`${gemName} was added to your trip.`);
    } catch (error) {
        button.disabled = false;
        button.textContent = "➕ Add to My Trip";
        showHiddenGemStatus(error.message, true);
    }
}

function showHiddenGemStatus(message, isError = false) {
    const status = document.getElementById("hiddenGemStatus");
    if (!status) {
        return;
    }
    status.textContent = message;
    status.classList.toggle("hidden-gem-status-error", isError);
}