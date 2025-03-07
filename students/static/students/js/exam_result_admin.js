document.addEventListener("DOMContentLoaded", function () {
    const studentField = document.querySelector("#id_student");
    const field1Definition = document.querySelector("#id_field1_definition");
    const field2Definition = document.querySelector("#id_field2_definition");
    const field3Definition = document.querySelector("#id_field3_definition");
    const field4Definition = document.querySelector("#id_field4_definition");
    const field5Definition = document.querySelector("#id_field5_definition");

    function updateFieldDefinitions(studentId) {
        if (!studentId) return;

        fetch(`/api/get_field_definitions/?student_id=${studentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error:", data.error);
                    return;
                }

                [field1Definition, field2Definition, field3Definition, field4Definition, field5Definition].forEach(selectField => {
                    if (selectField) {
                        selectField.innerHTML = '<option value="">---------</option>';
                        data.fields.forEach(field => {
                            let option = document.createElement("option");
                            option.value = field.id;
                            option.textContent = field.name;
                            selectField.appendChild(option);
                        });
                    }
                });
            })
            .catch(error => console.error("Fetch error:", error));
    }

    if (studentField) {
        studentField.addEventListener("change", function () {
            updateFieldDefinitions(this.value);
        });
    }
});
