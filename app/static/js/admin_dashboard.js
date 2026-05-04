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
        if (response.status === 401 || response.status === 403) {
            window.location.href = "/login/admin";
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
        const node = document.createElement("article");
        node.className = "list-item";
        node.innerHTML = formatter(item);
        container.appendChild(node);
    });
}

async function loadStats() {
    const response = await request("/api/admin/stats");
    const entries = [
        ["Patients", response.data.total_patients],
        ["Doctors", response.data.total_doctors],
        ["Clinics", response.data.total_clinics],
        ["Appointments", response.data.total_appointments],
        ["Pending Confirmation", response.data.pending_confirmation],
        ["Confirmed Booked", response.data.confirmed_booked],
        ["Today's Appointments", response.data.todays_appointments],
    ];

    const grid = document.getElementById("statsGrid");
    grid.innerHTML = "";
    entries.forEach(([label, value]) => {
        const card = document.createElement("article");
        card.className = "stat-card";
        card.innerHTML = `<strong>${value}</strong><br>${label}`;
        grid.appendChild(card);
    });

    Object.entries(response.data.appointments_by_status).forEach(([status, count]) => {
        const card = document.createElement("article");
        card.className = "stat-card";
        card.innerHTML = `<strong>${count}</strong><br>${status}`;
        grid.appendChild(card);
    });
}

async function loadPatients() {
    const response = await request("/api/admin/patients");
    renderList(
        "patientList",
        response.data,
        (patient) => `
            <strong>${patient.name}</strong><br>
            Patient ID: ${patient.id}<br>
            Contact: ${patient.contact}<br>
            Appointments: ${patient.appointment_count}
        `,
        "No patients found."
    );
}

async function loadAppointments(status = "") {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    const response = await request(`/api/admin/appointments${query}`);
    renderList(
        "appointmentList",
        response.data,
        (appointment) => `
            <strong>Appointment #${appointment.id}</strong><br>
            Patient: ${appointment.patient.name} (${appointment.patient.contact})<br>
            Doctor: ${appointment.doctor.name}<br>
            Clinic: ${appointment.clinic.name}<br>
            Date: ${appointment.date}<br>
            Time: ${appointment.time}<br>
            Status: ${appointment.status}<br>
            Confirmation: ${appointment.is_confirmed ? `Confirmed at ${appointment.confirmed_at}` : "Pending"}
        `,
        "No appointments found."
    );
}

async function confirmAppointment(event) {
    event.preventDefault();
    const appointmentId = document.getElementById("confirmAppointmentId").value;
    const response = await request(`/api/admin/appointments/${appointmentId}/confirm`, {
        method: "POST",
    });
    document.getElementById("confirmResult").classList.remove("muted");
    document.getElementById("confirmResult").innerHTML = `
        <strong>Appointment confirmed</strong><br>
        Appointment ID: ${response.data.id}<br>
        Patient: ${response.data.patient.name}<br>
        Status: ${response.data.status}<br>
        Confirmed: Yes
    `;
    showToast(`Appointment ${appointmentId} confirmed.`);
    await refreshDashboard();
}

async function updateStatus(event) {
    event.preventDefault();
    const appointmentId = document.getElementById("updateAppointmentId").value;
    const response = await request(`/api/admin/appointments/${appointmentId}/status`, {
        method: "PATCH",
        body: JSON.stringify({
            status: document.getElementById("appointmentStatus").value,
        }),
    });
    document.getElementById("statusResult").classList.remove("muted");
    document.getElementById("statusResult").innerHTML = `
        <strong>Status updated</strong><br>
        Appointment ID: ${response.data.id}<br>
        Patient: ${response.data.patient.name}<br>
        New Status: ${response.data.status}
    `;
    showToast(`Appointment ${appointmentId} updated.`);
    await refreshDashboard();
}

async function refreshDashboard() {
    await Promise.all([
        loadStats(),
        loadPatients(),
        loadAppointments(document.getElementById("appointmentStatusFilter").value),
    ]);
}

async function logout() {
    await request("/api/auth/logout", { method: "POST" });
    window.location.href = "/";
}

function bindEvents() {
    document.getElementById("refreshAdminDashboard").addEventListener("click", () => {
        refreshDashboard().catch((error) => showToast(error.message, true));
    });
    document.getElementById("appointmentFilterForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            await loadAppointments(document.getElementById("appointmentStatusFilter").value);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("confirmForm").addEventListener("submit", async (event) => {
        try {
            await confirmAppointment(event);
        } catch (error) {
            showToast(error.message, true);
        }
    });
    document.getElementById("statusUpdateForm").addEventListener("submit", async (event) => {
        try {
            await updateStatus(event);
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
        await refreshDashboard();
    } catch (error) {
        showToast(error.message, true);
    }
});
