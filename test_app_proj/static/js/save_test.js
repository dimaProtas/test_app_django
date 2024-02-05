const saveQuestion = (survey_id, question_id, question_index) => {
    let selectedValue = null;
    try {
        const choises = document.querySelectorAll('#choise_id')
        

        choises.forEach(checkbox => {
            if (checkbox.checked) {
                selectedValue = JSON.parse(checkbox.value.replace(/'/g, '"'))
            }
        });
    } catch (error) {
        console.error('Произошла ошибка:', error);
    }

    const text_value = document.getElementById('text_value')
    const text_value_result = text_value ? text_value.value : null;
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

    fetch('http://127.0.0.1:8000/save_questions/', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'survey_id': survey_id,
            'question_id': question_id,
            'choice_id': selectedValue ? selectedValue.id : null,
            'text_response': text_value_result,
        })
    })
    .then(responce => {
        if (!responce.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return responce.json()
    })
    .then(data => {
        if (data.success == 'OK') {
            console.log('Ответ сохранён!')
            if (selectedValue !== null && selectedValue.dependent_question_id) {
                window.location.href = `/child_question/${survey_id}/${selectedValue.dependent_question_id}/${question_index}/`;
            } else {
                window.location.href = `/test/${survey_id}/${question_index}/`;
            }

        } else {
            console.log('Ошибка сохранения!')
        }
    })
}