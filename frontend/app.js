const cityRow = document.querySelector("#cities");
const card = document.querySelector("#card");

function message(text, isError) {
  card.dataset.condition = "";
  card.innerHTML = "";
  const paragraph = document.createElement("p");
  paragraph.className = isError ? "error" : "waiting";
  paragraph.textContent = text;
  card.appendChild(paragraph);
}

async function readJson(response) {
  let body = {};
  try {
    body = await response.json();
  } catch (_error) {
    body = {};
  }
  if (!response.ok) {
    const detail = typeof body.detail === "string"
      ? body.detail
      : "The weather programs did not answer.";
    throw new Error(detail);
  }
  return body;
}

function showSky(city, forecast) {
  card.dataset.condition = String(forecast.condition || "").toLowerCase();
  card.innerHTML = "";

  const place = document.createElement("p");
  place.className = "place";
  place.textContent = city.name;

  const country = document.createElement("p");
  country.className = "country";
  country.textContent = city.country;

  const temp = document.createElement("p");
  temp.className = "temp";
  temp.textContent = String(forecast.temperature_c);
  const unit = document.createElement("span");
  unit.textContent = " °C";
  temp.appendChild(unit);

  const feels = document.createElement("p");
  feels.className = "feels";
  feels.textContent = `${forecast.feels} · ${forecast.condition}`;

  const meta = document.createElement("p");
  meta.className = "meta";
  meta.textContent = `Humidity ${forecast.humidity_percent}% · Wind ${forecast.wind_kph} km/h · ${forecast.date}`;

  const map = document.createElement("p");
  map.className = "meta";
  map.textContent = `Map spot ${Number(city.latitude).toFixed(2)}, ${Number(city.longitude).toFixed(2)}`;

  const summary = document.createElement("p");
  summary.className = "summary";
  summary.textContent = forecast.summary;

  card.append(place, country, temp, feels, meta, map, summary);
}

async function loadCities() {
  message("Loading cities...");
  try {
    const response = await fetch("/api/cities", { cache: "no-store" });
    const cities = await readJson(response);
    cityRow.innerHTML = "";
    if (!Array.isArray(cities) || cities.length === 0) {
      message("The city book has no cities.");
      return;
    }
    cities.forEach((city) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = city.name;
      button.addEventListener("click", () => selectCity(city.id, button));
      cityRow.appendChild(button);
    });
    message("Pick a city to see the sky.");
  } catch (error) {
    message(error.message, true);
  }
}

async function selectCity(id, button) {
  cityRow.querySelectorAll("button").forEach((item) => {
    item.setAttribute("aria-pressed", item === button ? "true" : "false");
  });
  message("Looking up the sky...");
  try {
    const response = await fetch(`/api/weather?city=${encodeURIComponent(id)}`, {
      cache: "no-store",
    });
    const body = await readJson(response);
    showSky(body.city, body.forecast);
  } catch (error) {
    message(error.message, true);
  }
}

loadCities();
