const state = {
    specialities: [],
};

async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    const data = await response.json();
    if (!response.ok) {
        if (response.status === 401) {
            window.location.href = "/login/user";
        }
        throw new Error(data.message || "Request failed.");
    }
    return data;
}

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.remove("hidden");
    toast.style.background = isError ? "#8c1c13" : "#173955";
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => toast.classList.add("hidden"), 2800);
}

function renderList(containerId, items, formatter, emptyMessage) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    if (!items.length) {
        container.innerHTML = `<div class="list-item muted">${emptyMessage}</div>`;
        return;
    }

    items.forEach((item) => {
        const card = document.createElement("article");
        card.className = "list-item";
        card.innerHTML = formatter(item);
        container.appendChild(card);
    });
}

async function loadSpecialities() {
    const response = await request("/api/specialities");
    state.specialities = response.data;
    const select = document.getElementById("availabilitySpeciality");
    select.innerHTML = '<option value="">Speciality</option>';
    response.data.forEach((speciality) => {
        const option = document.createElement("option");
        option.value = speciality.name;
        option.textContent = speciality.name;
        select.appendChild(option);
    });

    renderList(
        "specialityList",
        response.data,
        (item) => `<strong>${item.name}</strong><br>${item.description || "Speciality available for scheduling."}`,
        "No specialities found."
    );
}

async function searchAvailability(event) {
    event.preventDefault();
    const params = new URLSearchParams();
    const fields = {
        doctor_name: "doctorName",
        speciality: "availabilitySpeciality",
        date: "availabilityDate",
        start_time: "startTime",
        end_time: "endTime",
    };

    Object.entries(fields).forEach(([param, elementId]) => {
        const value = document.getElementById(elementId).value;
        if (value) {
            params.set(param, value);
        }
    });

    const response = await request(`/api/availability?${params.toString()}`);
    renderList(
        "availabilityList",
        response.data,
        (item) => `
            <strong>${item.doctor_name}</strong><br>
            Doctor ID: ${item.doctor_id}<br>
            Speciality: ${item.speciality}<br>
            Clinic: ${item.clinic} (Clinic ID ${item.clinic_id})<br>
            Date: ${item.date || "Recurring"}<br>
            Day: ${item.day}<br>
            Available Time: ${
                Array.isArray(item.available_time)
                    ? item.available_time
                          .map(
                              (slot) =>
                                  `<button type="button" class="slot-button" data-doctor-id="${item.doctor_id}" data-clinic-id="${item.clinic_id}" data-date="${item.date}" data-time="${slot}">${slot}</button>`
                          )
                          .join(" ")
                    : item.available_time
            }
        `,
        "No availability matched your filters."
    );
    bindSlotButtons();
}

async function createPatient(event) {
    event.preventDefault();
    const response = await request("/api/patients", {
        method: "POST",
        body: JSON.stringify({
            name: document.getElementById("patientName").value,
            contact: document.getElementById("patientContact").value,
        }),
    });

    document.getElementById("patientId").value = response.data.id;
    document.getElementById("patientResult").classList.remove("muted");
    document.getElementById("patientResult").innerHTML = `
        <strong>Patient created</strong><br>
        ID: ${response.data.id}<br>
        Name: ${response.data.name}<br>
        Contact: ${response.data.contact}
    `;
    event.target.reset();
    showToast(`Patient profile ${response.data.id} created.`);
}

async function bookAppointment(event) {
    event.preventDefault();
    const response = await request("/api/appointments", {
        method: "POST",
        body: JSON.stringify({
            patient_id: Number(document.getElementById("patientId").value),
            doctor_id: Number(document.getElementById("doctorId").value),
            clinic_id: Number(document.getElementById("clinicId").value),
            date: document.getElementById("appointmentDate").value,
            time: document.getElementById("appointmentTime").value,
        }),
    });

    document.getElementById("bookingResult").classList.remove("muted");
    document.getElementById("bookingResult").innerHTML = `
        <strong>Appointment #${response.data.id}</strong><br>
        Patient: ${response.data.patient.name}<br>
        Doctor: ${response.data.doctor.name}<br>
        Clinic: ${response.data.clinic.name}<br>
        Date: ${response.data.date}<br>
        Time: ${response.data.time}<br>
        Confirmation: ${response.data.is_confirmed ? "Confirmed" : "Pending admin confirmation"}<br>
        Status: ${response.data.status}
    `;
    showToast(`Appointment ${response.data.id} booked.`);
}

async function logout() {
    await request("/api/auth/logout", { method: "POST" });
    window.location.href = "/";
}

function bindSlotButtons() {
    document.querySelectorAll(".slot-button").forEach((button) => {
        button.addEventListener("click", () => {
            document.getElementById("doctorId").value = button.dataset.doctorId;
            document.getElementById("clinicId").value = button.dataset.clinicId;
            if (button.dataset.date) {
                document.getElementById("appointmentDate").value = button.dataset.date;
            }
            document.getElementById("appointmentTime").value = button.dataset.time;
            showToast("Slot copied into the booking form.");
        });
    });
}

function bindEvents() {
    document.getElementById("availabilityForm").addEventListener("submit", async (event) => {
        try {
            await searchAvailability(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("patientForm").addEventListener("submit", async (event) => {
        try {
            await createPatient(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("appointmentForm").addEventListener("submit", async (event) => {
        try {
            await bookAppointment(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("refreshAvailability").addEventListener("click", async () => {
        try {
            await loadSpecialities();
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("logoutButton").addEventListener("click", async () => {
        try {
            await logout();
        } catch (error) {
            showToast(error.message, true);
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    try {
        await loadSpecialities();
    } catch (error) {
        showToast(error.message, true);
    }
});
