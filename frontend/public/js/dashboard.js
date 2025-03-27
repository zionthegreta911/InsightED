const apiUrl = "http://127.0.0.1:5000"; // Flask Backend URL
let pieChart, barChart;

// Function to Upload CSV
function uploadCSV() {
    let fileInput = document.getElementById('csvFile');
    let file = fileInput.files[0];

    if (!file) {
        alert("❌ Please select a file.");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch(`${apiUrl}/upload`, { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            alert("✅ File uploaded successfully!");
            fetchStudentList();
            setTimeout(generateCharts, 3000);
        })
        .catch(error => console.error("❌ Upload Error:", error));
}

// Function to Fetch Student List from Flask API
function fetchStudentList() {
  fetch(`${apiUrl}/students`)
        .then(response => response.json())
        .then(data => {
            let studentList = document.getElementById("studentList");
            studentList.innerHTML = "";

            data.forEach(student => {
                let listItem = document.createElement("li");
                listItem.innerHTML = `
                    ${student["STUDENT NAME"]} (ID: ${student["STUDENT ID"]}) 
                    <button onclick="analyzeStudent(${student['STUDENT ID']})">Analyze</button>
                `;
                studentList.appendChild(listItem);
            });
        })
        .catch(error => console.error("Error fetching student data:", error));
}

// Function to Analyze an Individual Student
// Function to analyze an individual student and fetch recommendations
function analyzeStudent(studentId) {
    fetch(`${apiUrl}/assess/individual?student_id=${studentId}`)
        .then(response => response.json())
        .then(data => {
            // Display the analysis result in the DOM
            document.getElementById("analysisResult").innerHTML = data.result;

            // Extract the dominant trait from the analysis result HTML
            const resultHTML = data.result;
            const dominantData = extractDominantTrait(resultHTML); // Extract the trait and score

            if (dominantData) {
                // Fetch AI recommendations based on the dominant trait
                fetchRecommendation(dominantData.trait);
            }
        })
        .catch(error => console.error("Error analyzing student:", error));
}




// Function to Analyze All Students
function analyzeAll() {
    fetch(`${apiUrl}/assess/all`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("analysisResult").innerHTML = data.result;
            fetchDashboardStats();
        })
        .catch(error => console.error("Error analyzing all students:", error));
}

// Function to Fetch AI Recommendations for All Students
// Function to fetch AI recommendation based on the dominant trait
function fetchRecommendation(dominantTrait) {
    fetch("http://127.0.0.1:5000/get-recommendation", {
        method: "POST",  // Ensure the method is POST
        headers: {
            "Content-Type": "application/json",  // Set the content type to JSON
        },
        body: JSON.stringify({ dominant_trait: dominantTrait.toLowerCase() })  // Send the dominant trait in the body
    })
    .then(response => response.json())
    .then(data => {
        // Display the AI recommendations
        document.getElementById("recommendations").innerHTML = `
            <h3>AI Recommendation</h3>
            <p><strong>Most Dominant Trait:</strong> ${dominantTrait}</p>
            <p><strong>Recommendation for Students:</strong> ${data.student_recommendation}</p>
            <p><strong>Teaching Strategy:</strong> ${data.teacher_strategy}</p>
        `;
    })
    .catch(error => {
        console.error("Error fetching AI recommendation:", error);
    });
}



// Function to Fetch and Update Dashboard Stats
function fetchDashboardStats() {
    fetch(`${apiUrl}/dashboard/stats`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("totalSurveys").innerText = data.totalSurveys;

            let dominantTraitsDiv = document.getElementById("dominantTraits");
            dominantTraitsDiv.innerHTML = "";

            Object.keys(data.dominantTraitCount).forEach(trait => {
                let total = data.dominantTraitCount[trait].total;
                let ids = data.dominantTraitCount[trait].ids.join(", ");
                let traitBox = document.createElement("div");

                traitBox.classList.add("trait-box");
                traitBox.innerHTML = `
                    <h4>${trait.toUpperCase()}</h4>
                    <p>${total} / ${data.totalSurveys} students</p>
                    <small>ID Nos: ${ids}</small>
                `;
                dominantTraitsDiv.appendChild(traitBox);

            });

            updateBarChart(data.traitAverages);
        })
        .catch(error => console.error("Error fetching dashboard stats:", error));
}

// Function to Generate and Update Bar Chart
function generateCharts() {
    fetch(`${apiUrl}/assess/ocean-averages`)
        .then(response => response.json())
        .then(data => {
            if (!data || Object.keys(data).length === 0) {
                console.error("❌ No data received for charts!");
                return;
            }

            const traitLabels = Object.keys(data);
            const traitScores = Object.values(data);
            const traitColors = ["red", "blue", "yellow", "green", "purple"];

            if (barChart) {
                barChart.destroy();
            }

            const barCtx = document.getElementById("barChart").getContext("2d");
            barChart = new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: traitLabels,
                    datasets: [{
                        label: "Average Scores",
                        data: traitScores,
                        backgroundColor: traitColors
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, max: 5 }
                    }
                }
            });

            console.log("✅ Graphs successfully updated with:", data);
        })
        .catch(error => console.error("❌ ERROR: Graphs not updating! Check backend.", error));
}

// Function to Fetch AI Recommendation for an Individual Student
function fetchRecommendation(studentId) {
    fetch(`${apiUrl}/assess/recommendations?student_id=${studentId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("recommendations").innerHTML = `
                <strong>Most Dominant Trait:</strong> ${data.dominant_trait}<br>
                <strong>Recommendation:</strong> ${data.recommendation}
            `;
        })
        .catch(error => console.error("Error fetching AI recommendation:", error));
}

// Initialize the page by fetching students and generating charts
document.addEventListener("DOMContentLoaded", function () {
    fetchStudentList();
    setTimeout(generateCharts, 2000);
});
// Function to extract dominant trait from the analysis result HTML
// Function to extract the dominant trait from the analysis result
// Function to extract the dominant trait from the analysis result
// Function to extract the most dominant trait from the analysis result HTML
function extractDominantTrait(analysisHTML) {
    // Example to match: "Most Dominant Trait: Extraversion (3.9)"
    const match = analysisHTML.match(/Most Dominant Trait: (\w+) \((\d+\.\d+)\)/);
    
    if (match) {
        return match[1];  // Return the dominant trait, e.g., "Extraversion"
    }
    return null;
}

function analyzeStudent(studentId) {
    fetch(`${apiUrl}/assess/individual?student_id=${studentId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("analysisResult").innerHTML = data.result;
            
            // Extract the dominant trait from the analysis result
            const dominantTrait = extractDominantTrait(data.result);
            
            console.log("Dominant Trait:", dominantTrait);  // Log the dominant trait
            
            if (dominantTrait) {
                // Call fetchRecommendation with the dominant trait
                fetchRecommendation(dominantTrait);
            } else {
                console.error("❌ No dominant trait found!");
            }
        })
        .catch(error => console.error("Error analyzing student:", error));
}


// Function to fetch AI recommendation based on dominant trait
function fetchRecommendation(dominantTrait) {
    fetch("http://127.0.0.1:5000/get-recommendation", {
        method: "POST",  // Ensure the method is POST
        headers: {
            "Content-Type": "application/json",  // Set the content type to JSON
        },
        body: JSON.stringify({ dominant_trait: dominantTrait.toLowerCase() })  // Send the dominant trait in the body
    })
    .then(response => response.json())
    .then(data => {
        // Display the AI recommendations
        document.getElementById("recommendations").innerHTML = `
            <h3>AI Recommendation</h3>
            <p><strong>Most Dominant Trait:</strong> ${dominantTrait}</p>
            <p><strong>Recommendation for Students:</strong> ${data.student_recommendation}</p>
            <p><strong>Teaching Strategy:</strong> ${data.teacher_strategy}</p>
        `;
    })
    .catch(error => {
        console.error("Error fetching AI recommendation:", error);
    });
}





document.getElementById("recommendations").innerHTML = `
    <h3>AI Recommendation</h3>
    ${dominantTrait ? `<p><strong>Most Dominant Trait:</strong> ${dominantTrait}</p>` : ""}
    <p><strong>Recommendation for Students:</strong> ${data.student_recommendation || "No data available."}</p>
    <p><strong>Teaching Strategy:</strong> ${data.teacher_strategy || "No data available."}</p>
`;
