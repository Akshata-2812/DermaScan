document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("signupForm")?.addEventListener("submit", async function (e) {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const age = document.getElementById("age").value;
        const sex = document.getElementById("sex").value;

        const response = await fetch("/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, age, sex }),
        });

        const data = await response.json();
        alert(data.message);
    });

    document.getElementById("uploadForm")?.addEventListener("submit", async function (e) {
        e.preventDefault();
        const fileInput = document.getElementById("file");
        const username = document.getElementById("username").value;

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("username", username);

        const response = await fetch("/upload", { method: "POST", body: formData });
        const data = await response.json();
        alert(data.message);
    });

    document.getElementById("generateReport")?.addEventListener("click", async function () {
        const username = document.getElementById("username").value;
        const reportType = document.querySelector('input[name="reportType"]:checked').value;

        const response = await fetch(`/generate_report?username=${username}&type=${reportType}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${username}_report.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            alert("Failed to generate report.");
        }
    });
});
//console.log("Username is:", username);

function savePrediction() {
    //const username = "{ username }";  // Pass from Flask to HTML template
    const resultDiv = document.getElementById("result");
    

    if (!resultDiv || !resultDiv.innerHTML.trim()) {
        alert("No prediction result found!");
        return;
    }

    const result = resultDiv.innerHTML.trim();

    if (!username || !result) {
        alert("Missing username or prediction!");
        return;
    }

    fetch("/manual_save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            result: JSON.stringify(window.latestResult)
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Saved successfully!");
    })
    .catch(err => {
        console.error(err);
        alert("Error saving result.");
    });
}