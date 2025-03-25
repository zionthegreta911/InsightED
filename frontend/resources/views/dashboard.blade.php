<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INSIGHTED - Student Personality Dashboard</title>
    
    <!-- External Libraries -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <link rel="stylesheet" href="{{ asset('css/styles.css') }}"> <!-- Load your styles.css -->
    @vite(['resources/css/app.css']) <!-- Load Tailwind CSS -->
</head>
<body>
    

    <!-- Main Content -->
    <!-- Sidebar -->
   
    <!-- Sidebar -->
     
    <aside class="sidebar">
    <body class="bg-gray-100 flex">
    <!-- Title with Aurora Effect -->
    <h1 class="title">InsightEd
    <div class="aurora">
      <div class="aurora__item"></div>
      <div class="aurora__item"></div>
      <div class="aurora__item"></div>
      <div class="aurora__item"></div>
    </div>
  </h1>
        <div class="space-y-4">
            <!-- File Upload Section -->
            <div id="dropzone" class="dropzone">
                <input type="file" id="csvFile" class="hidden" accept=".csv">
             <!-- Download Sample CSV Button with GIF -->
<!-- Download Sample CSV Button with Custom CSS -->
<button class="sidebar-secondary-button flex items-center">
    <img src="{{ asset('css/download.gif') }}" alt="Download" class="download-gif mr-2">
    Download Sample CSV
</button>


                <p class="mt-1 text-sm text-gray-600">Drop CSV or click to browse</p>
            </div>

            <!-- Status Indicator -->
            <div class="status-indicator">
                <div></div>
                Ready to process data
            </div>

            <!-- Action Buttons -->
            <div class="space-y-2">
                <button class="sidebar-button" onclick="uploadCSV()">Upload & Process</button>
                 <!-- Analyze All Button -->
 <!-- Analyze All Button with Inline CSS -->
<button onclick="analyzeAll()" 
        style="width: 100%; background-color:rgb(138, 37, 141); color: white; padding: 0.75rem 1rem; border-radius: 0.375rem; transition: background-color 0.2s;">
    Analyze All
</button>

                <button class="sidebar-secondary-button" onclick="resetData()">
                    


                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v6h6M20 20v-6h-6M9 9l6 6"></path>
                    </svg>
                    Reset Data
                </button>
            </div>
        </div>
    </aside>

     <!-- Dashboard Content with Background -->
     <main class="dashboard-container pattern-wavy">
            <h2 class="text-xl font-semibold text-gray-800 mb-4"></h2>

            <div class="dashboard-section">
                <h3>Total Surveys: <span id="totalSurveys">0</span></h3>
            </div>

            <div class="dashboard-section">
                <h3>Students</h3>
                <ul id="studentList"></ul>
            </div>
             


            <div class="dashboard-section">
  <div class="dashboard-section">
    <h3>Analysis Result</h3>
    <div class="analysis-result">
        <!-- Left Part of the Analysis Result -->
        <div id="analysisResult" class="left-container">
            <!-- Content will be dynamically added here -->
        </div>

        <!-- Right Part of the Analysis Result (Medium-Sized Container) -->
        <div id="dominantTraitContainer" class="right-container">
            <h3>Most Dominant Trait:</h3>
            <p id="dominantTrait">Loading...</p>
        </div>
    </div>
</div>



            <div class="dashboard-section">
                <h3>AI Recommendations</h3>
                <div id="recommendations"></div>
            </div>

            <div class="dashboard-section dashboard-chart">
                <h3></h3>
                <canvas id="barChart"></canvas>
            </div>
        </main>

    </div>
</body>

    </div>
</aside>


    <script>
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
            studentList.innerHTML = "";  // Clear any previous list

            data.forEach(student => {
                let listItem = document.createElement("li");
                listItem.classList.add("student-item", "flex", "justify-between", "items-center", "p-4", "bg-gray-800", "text-white", "rounded-lg", "mb-4");
                
                // HTML for each student entry
                listItem.innerHTML = `
                    <div class="student-info">
                        <span class="student-name">${student["STUDENT NAME"]} (ID: ${student["STUDENT ID"]})</span>
                        <p class="most-dominant-trait">Most Dominant Trait: Openness</p> <!-- Update dynamically as per your data -->
                    </div>
                    <button class="btn-analyze bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600" onclick="analyzeStudent(${student['STUDENT ID']})">Analyze</button>
                `;
                
                studentList.appendChild(listItem);  // Append student list item to the list
            });
        })
        .catch(error => console.error("Error fetching student data:", error));
}

        // Function to Analyze Individual Student
        function analyzeStudent(studentId) {
            fetch(`${apiUrl}/assess/individual?student_id=${studentId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("analysisResult").innerHTML = data.result;
                fetchRecommendation(studentId); // Fetch AI recommendation for the student
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
        function fetchAllRecommendations() {
            fetch(`${apiUrl}/assess/recommendations/all`)
            .then(response => response.json())
            .then(data => {
                let recommendationsDiv = document.getElementById("recommendations");
                let output = "<ul>";
                data.forEach(student => {
                    output += `
                        <li>
                            <strong>Student ID:</strong> ${student.student_id} - 
                            <strong>Trait:</strong> ${student.dominant_trait}<br>
                            <strong>Recommendation:</strong> ${student.recommendation}
                        </li><br>
                    `;
                });
                output += "</ul>";
                recommendationsDiv.innerHTML = output;
            })
            .catch(error => console.error("Error fetching all recommendations:", error));
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

        // Function to Fetch AI Recommendation for a Student
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
    </script>

</body>
</html>
