async function updateStats() {
    const response = await fetch("http://10.42.0.1:8000/metrics");
    const data = await response.json();
    document.querySelector(".cpuval").textContent = data.cpu + "%";
    document.querySelector(".cpubar2").style.width = data.cpu + "%";
    document.querySelector(".ramval").textContent = data.ram + "%";
    document.querySelector(".rambar2").style.width = data.ram + "%";
    document.querySelector(".diskval").textContent = data.disk + "%";
    document.querySelector(".diskbar2").style.width = data.disk + "%";
    document.querySelector(".tempval").textContent = data.temp + "°C";
    document.querySelector(".tempbar2").style.width = data.temp + "%";

    const response2 = await fetch("http://10.42.0.1:8000/info");
    const data2 = await response2.json();
    document.querySelector(".valuehost").textContent = data2.hostname;
    document.querySelector(".valueos").textContent = data2.os;
    document.querySelector(".valuekernel").textContent = data2.kernel;
    document.querySelector(".valuetime").textContent = data2.uptime;

    const response3 = await fetch("https://api.ipify.org?format=json");
    const data3 = await response3.json();
    document.querySelector(".valueip").textContent = data3.ip;
}


setInterval(updateStats, 1000);

document.querySelector(".reboot").addEventListener("click", async () => {

    const ok = confirm("Are you sure you want to reboot your computer?");
    if (!ok) return;

    console.log("CLICKED REBOOT");

    const res = await fetch("http://10.42.0.1:8000/reboot");
    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log(data);
});

document.querySelector(".suspend").addEventListener("click", async () => {

    const ok = confirm("Are you sure you want to suspend your computer?");
    if (!ok) return;

    console.log("CLICKED SUSPEND");

    const res = await fetch("http://10.42.0.1:8000/suspend");
    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log(data);
});

document.querySelector(".poweroff").addEventListener("click", async () => {
    const ok = confirm("Are you sure you want to turn off your computer?");

    if (!ok) return;

    const res = await fetch("http://10.42.0.1:8000/poweroff");
    const data = await res.json();

    console.log(data.message);
});

function toggleTheme() {
    document.body.classList.toggle("dark");

    const icon = document.getElementById("themeIcon");
    const isDark = document.body.classList.contains("dark");

    if (isDark) {
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");
    } else {
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");
    }

    localStorage.setItem(
        "theme",
        document.body.classList.contains("dark") ? "dark" : "light"
    );
}

window.onload = () => {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark");
    }
};


const ctx = document.getElementById('myChart').getContext('2d');


const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['10:00','10:05','10:10','10:15','10:20','10:25','10:30','10:35','10:40','10:45','10:50','10:55','11:00'],
        datasets: [
            {
                label: 'CPU',
                data: [60, 65, 50, 70, 62, 55, 63, 58, 66, 60, 75, 62, 70],
                borderColor: '#6c63ff',
                tension: 0.4, // плавность линии
                fill: false
            },
            {
                label: 'RAM',
                data: [30, 35, 33, 40, 36, 32, 35, 31, 38, 34, 42, 30, 35],
                borderColor: '#2ecc71',
                tension: 0.4,
                fill: false
            },
            {
                label: 'DISK',
                data: [40, 45, 46, 42, 40, 35, 48, 42, 48, 44, 45, 49, 41],
                borderColor: '#2485EE',
                tension: 0.4,
                fill: false
            },
            {
                label: 'TEMP',
                data: [55, 59, 54, 50, 51, 57, 52, 47, 46, 42, 40, 41, 40],
                borderColor: '#EE8543',
                tension: 0.4,
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {

            }
        },
        scales: {
            y: {
                min: 0,
                max: 100,
                ticks: {
                    callback: value => value + '%'
                }
            }
        }
    }
});