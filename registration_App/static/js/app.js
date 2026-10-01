const API_URL = "/api/registrations";

const form = document.getElementById("registration-form");
const nameInput = document.getElementById("name");
const placeInput = document.getElementById("place");
const phoneInput = document.getElementById("phone");
const emailInput = document.getElementById("email");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const messageBox = document.getElementById("message");
const tableBody = document.getElementById("registrations-body");

// null = creating a new record, a number = editing that record
let editingId = null;

// ---------- Helpers ----------

function showMessage(text, isError = false) {
    messageBox.textContent = text;
    messageBox.className = isError ? "message error" : "message";
}

function hideMessage() {
    messageBox.className = "message hidden";
}

// Wrapper around fetch(): returns parsed JSON or throws an Error with the API message.
async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    let data = null;
    try {
        data = await response.json();
    } catch (e) {
        // Response had no JSON body
    }

    if (!response.ok) {
        throw new Error((data && data.error) || "Something went wrong");
    }
    return data;
}

function resetForm() {
    form.reset();
    editingId = null;
    emailInput.required = true;
    submitBtn.textContent = "REGISTER";
    cancelBtn.classList.add("hidden");
}

// ---------- Read ----------

async function loadRegistrations() {
    try {
        const registrations = await request(API_URL);
        renderTable(registrations);
    } catch (error) {
        showMessage(error.message, true);
    }
}

function renderTable(registrations) {
    tableBody.innerHTML = "";

    if (registrations.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 5;
        cell.className = "empty";
        cell.textContent = "No registrations yet.";
        row.appendChild(cell);
        tableBody.appendChild(row);
        return;
    }

    registrations.forEach((item) => {
        const row = document.createElement("tr");

        // textContent (not innerHTML) keeps user input from being run as HTML.
        [item.id, item.name, item.place, item.phone].forEach((value) => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        const actions = document.createElement("td");
        actions.className = "actions";

        const editBtn = document.createElement("button");
        editBtn.textContent = "Edit";
        editBtn.className = "small";
        editBtn.addEventListener("click", () => startEdit(item.id));

        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";
        deleteBtn.className = "small danger";
        deleteBtn.addEventListener("click", () => deleteRegistration(item.id));

        actions.appendChild(editBtn);
        actions.appendChild(deleteBtn);
        row.appendChild(actions);

        tableBody.appendChild(row);
    });
}

// ---------- Create / Update ----------

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        name: nameInput.value.trim(),
        place: placeInput.value.trim(),
        phone: phoneInput.value.trim(),
    };
    if (editingId === null) {
        payload.email = emailInput.value.trim();
    }

    try {
        if (editingId === null) {
            await request(API_URL, { method: "POST", body: JSON.stringify(payload) });
            showMessage("Registration added.");
        } else {
            await request(`${API_URL}/${editingId}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            });
            showMessage("Registration updated.");
        }
        resetForm();
        loadRegistrations();
    } catch (error) {
        showMessage(error.message, true);
    }
});

// ---------- Edit ----------

async function startEdit(id) {
    try {
        const item = await request(`${API_URL}/${id}`);
        nameInput.value = item.name;
        placeInput.value = item.place;
        phoneInput.value = item.phone;

        editingId = item.id;
        emailInput.required = false;
        submitBtn.textContent = "UPDATE";
        cancelBtn.classList.remove("hidden");
        hideMessage();
        nameInput.focus();
    } catch (error) {
        showMessage(error.message, true);
    }
}

cancelBtn.addEventListener("click", () => {
    resetForm();
    hideMessage();
});

// ---------- Delete ----------

async function deleteRegistration(id) {
    if (!confirm("Are you sure you want to delete this registration?")) {
        return;
    }

    try {
        await request(`${API_URL}/${id}`, { method: "DELETE" });
        showMessage("Registration deleted.");
        if (editingId === id) {
            resetForm();
        }
        loadRegistrations();
    } catch (error) {
        showMessage(error.message, true);
    }
}

// ---------- Start ----------

loadRegistrations();
