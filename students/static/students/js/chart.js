document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/exam_chart/")
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error:", data.error);
                return;
            }

            const ctx = document.getElementById("examChart").getContext("2d");

            new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.exam_names,
                    datasets: [
                        {
                            label: "학생 점수",
                            data: data.student_scores,
                            borderColor: "blue",
                            backgroundColor: "rgba(0, 0, 255, 0.2)",
                            borderWidth: 2,
                            fill: true
                        },
                        {
                            label: "반 평균",
                            data: data.class_averages,
                            borderColor: "red",
                            backgroundColor: "rgba(255, 0, 0, 0.2)",
                            borderWidth: 2,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error("Fetch error:", error));
});
