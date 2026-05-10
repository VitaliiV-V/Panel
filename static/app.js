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
    document.querySelector(".trackname").textContent = data2.track;
    document.querySelector(".position").textContent = data2.position;
    document.querySelector(".length").textContent = data2.length;
    document.querySelector(".vol").textContent = data2.volume + '%';


    if(data2.status == "Playing\n") {
        document.querySelector(".btn-play").innerHTML =
          '<i class="fas fa-pause" style="font-size: 40px; padding-right: 5px;"></i>';   } else {
        document.querySelector(".btn-play").innerHTML =
          '<i class="fas fa-play" style="font-size: 40px;"></i>';
    }
    const slider = document.querySelector(".slider");

    slider.value = data2.progress;

    const volume = document.querySelector(".volume");

    volume.value = data2.volume;

    const response3 = await fetch("https://api.ipify.org?format=json");
    const data3 = await response3.json();
    document.querySelector(".valueip").textContent = data3.ip;


}


setInterval(updateStats, 500);

document.querySelector(".reboot").addEventListener("click", async () => {

    const ok = confirm("Are you sure you want to reboot your computer?");
    if (!ok) return;

    console.log("CLICKED REBOOT");

    const res = await fetch("http://10.42.0.1:8000/reboot");
    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log(data);
});

document.querySelector(".volume").addEventListener("change", function () {
  console.log("Финальное значение:", slider.value);
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

    if(res.status == "Playing\n") {
        document.querySelector(".btn-play").innerHTML =
          '<i class="fas fa-pause" style="font-size: 40px; padding-right: 5px;"></i>';   } else {
        document.querySelector(".btn-play").innerHTML =
          '<i class="fas fa-play" style="font-size: 40px;"></i>';
    }

    console.log(data.message);
});

document.querySelector(".btn-play").addEventListener("click", async () => {

    const res = await fetch("http://10.42.0.1:8000/playpause");
    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log(data);
});

document.querySelector(".btn-next").addEventListener("click", async () => {

    const res = await fetch("http://10.42.0.1:8000/next");
    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log(data);
});

document.querySelector(".btn-prev").addEventListener("click", async () => {

    const res = await fetch("http://10.42.0.1:8000/previous");
    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log(data);
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
