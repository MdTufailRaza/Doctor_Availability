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
    showToast.timeoutId = window.setTimeout(() => {
        toast.classList.add("hidden");
    }, 2800);
}

function renderList(containerId, items, formatter) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    if (!items.length) {
        container.innerHTML = '<div class="list-item muted">No records found.</div>';
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

    const selects = [document.getElementById("specialityFilter"), document.getElementById("availabilitySpeciality")];
    selects.forEach((select) => {
        const current = select.value;
        const firstOption = select.options[0].outerHTML;
        select.innerHTML = firstOption;
        state.specialities.forEach((speciality) => {
            const option = document.createElement("option");
            option.value = speciality.name;
            option.textContent = speciality.name;
            select.appendChild(option);
        });
        select.value = current;
    });
}

async function loadClinics() {
    const response = await request("/api/clinics");
    document.getElementById("clinicCount").textContent = `${response.data.length} clinics`;
    renderList("clinicList", response.data, (clinic) => `
        <strong>${clinic.name}</strong><br>
        Location: ${clinic.location}<br>
        Clinic ID: ${clinic.id}<br>
        Doctors: ${clinic.doctors.map((doctor) => `${doctor.name} (${doctor.speciality})`).join(", ") || "None"}
    `);
}

async function loadDoctors(speciality = "") {
    const query = speciality ? `?speciality=${encodeURIComponent(speciality)}` : "";
    const response = await request(`/api/doctors${query}`);
    renderList("doctorList", response.data, (doctor) => `
        <strong>${doctor.name}</strong><br>
        ID: ${doctor.id}<br>
        Speciality: ${doctor.speciality}<br>
        Email: ${doctor.email}<br>
        Admin: ${doctor.is_admin ? "Yes" : "No"}
    `);
}

async function searchAvailability(event) {
    event.preventDefault();
    const params = new URLSearchParams();

    ["doctor_name", "speciality", "date", "start_time", "end_time"].forEach((field) => {
        const element = document.getElementById(
            {
                doctor_name: "doctorName",
                speciality: "availabilitySpeciality",
                date: "availabilityDate",
                start_time: "startTime",
                end_time: "endTime",
            }[field]
        );
        if (element.value) {
            params.set(field, element.value);
        }
    });

    const response = await request(`/api/availability?${params.toString()}`);
    renderList("availabilityList", response.data, (item) => `
        <strong>${item.doctor_name}</strong><br>
        Speciality: ${item.speciality}<br>
        Clinic: ${item.clinic} (ID ${item.clinic_id})<br>
        ${item.date ? `Date: ${item.date}<br>` : ""}
        Day: ${item.day}<br>
        Available: ${Array.isArray(item.available_time) ? item.available_time.join(", ") : item.available_time}
    `);
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
    showToast(`Patient created with ID ${response.data.id}.`);
    event.target.reset();
}

async function bookAppointment(event) {
    event.preventDefault();
    const response = await request("/api/appointments", {
        method: "POST",
        body: JSON.stringify({
            patient_id: Number(document.getElementById("patientId").value),
            doctor_id: Number(document.getElementById("appointmentDoctorId").value),
            clinic_id: Number(document.getElementById("appointmentClinicId").value),
            date: document.getElementById("appointmentDate").value,
            time: document.getElementById("appointmentTime").value,
        }),
    });

    renderAppointmentStatus(response.data);
    showToast(`Appointment ${response.data.id} booked successfully.`);
}

function renderAppointmentStatus(appointment) {
    const card = document.getElementById("appointmentStatusCard");
    card.classList.remove("muted");
    card.innerHTML = `
        <strong>Appointment #${appointment.id}</strong><br>
        Patient: ${appointment.patient.name}<br>
        Doctor: ${appointment.doctor.name}<br>
        Clinic: ${appointment.clinic.name}<br>
        Date: ${appointment.date}<br>
        Time: ${appointment.time}<br>
        Status: ${appointment.status}
    `;
}

async function lookupAppointmentStatus(event) {
    event.preventDefault();
    const appointmentId = document.getElementById("lookupAppointmentId").value;
    const response = await request(`/api/appointments/${appointmentId}`);
    renderAppointmentStatus(response.data);
}

async function updateAppointmentStatus(event) {
    event.preventDefault();
    const appointmentId = document.getElementById("updateAppointmentId").value;
    const response = await request(`/api/appointments/${appointmentId}/status`, {
        method: "PATCH",
        body: JSON.stringify({
            status: document.getElementById("appointmentStatus").value,
        }),
    });
    renderAppointmentStatus(response.data);
    showToast(`Appointment ${appointmentId} updated.`);
}

async function calculateUtilization(event) {
    event.preventDefault();
    const params = new URLSearchParams({
        doctor_id: document.getElementById("utilDoctorId").value,
        clinic_id: document.getElementById("utilClinicId").value,
        start_date: document.getElementById("utilStartDate").value,
        end_date: document.getElementById("utilEndDate").value,
    });
    const response = await request(`/api/utilization?${params.toString()}`);
    const card = document.getElementById("utilizationCard");
    card.classList.remove("muted");
    card.innerHTML = `
        <strong>Doctor ${response.data.doctor_id} / Clinic ${response.data.clinic_id}</strong><br>
        Range: ${response.data.start_date} to ${response.data.end_date}<br>
        Booked Slots: ${response.data.booked_slots}<br>
        Total Slots: ${response.data.total_slots}<br>
        Utilization: ${(response.data.utilization * 100).toFixed(2)}%
    `;
}

async function refreshDashboard() {
    await Promise.all([loadSpecialities(), loadClinics(), loadDoctors()]);
}

function bindEvents() {
    document.getElementById("refreshDashboard").addEventListener("click", () => {
        refreshDashboard().catch((error) => showToast(error.message, true));
    });
    document.getElementById("doctorFilterForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            await loadDoctors(document.getElementById("specialityFilter").value);
        } catch (error) {
            showToast(error.message, true);
        }
    });
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
    document.getElementById("statusLookupForm").addEventListener("submit", async (event) => {
        try {
            await lookupAppointmentStatus(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("statusUpdateForm").addEventListener("submit", async (event) => {
        try {
            await updateAppointmentStatus(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("utilizationForm").addEventListener("submit", async (event) => {
        try {
            await calculateUtilization(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    try {
        await refreshDashboard();
    } catch (error) {
        showToast(error.message, true);
    }
});
