// Calculate duration in hours (decimal) when given hours and minutes
function calculateDuration(h, min){
    let hours = h || 0
    let minutes = min || 0
    let duration = parseInt(hours) + parseInt(minutes)/60.0
    duration = Math.round(duration * 100) / 100
    return duration
}


// Calculate speed (min/km) when given minutes and seconds
function calculateSpeedMinPerKm(min, s){
    let minutes = min || 0
    let seconds = s || 0
    let speedMinPerKm = parseInt(minutes) + parseInt(seconds)/60.0
    speedMinPerKm = Math.round(speedMinPerKm * 100) / 100
    return speedMinPerKm
}


// Convert min/km to km/h
function convertMinPerKmToKmPerH(speedMinPerKm){
    let speed = speedMinPerKm || 0
    if (speed === 0) {
        return 0
    } else {
        let speedKmPerH = Math.round(60.0/speed * 100) / 100
        return speedKmPerH
    }
}


// Calculate minutes and seconds when given speed in form min/km
function extractMinAndSecFromSpeed(speedMinPerKm){
    let speed = speedMinPerKm || 0
    let minutes = Math.floor(speed)
    let seconds = Math.round((speed - minutes) * 60.0)
    return {minutes,seconds}
}


// show selected element and activate corresbonding nav-button
function showDiv(id) {
    buttons = document.getElementsByName("nav_btn")
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove("active")
    }
    document.getElementById("btn_" + id).classList.add("active")
    let pages = document.getElementsByName("page")
    for (let i = 0; i < pages.length; i++) {
        if (pages[i].id == id) {
        pages[i].style.display = 'block'
        }
        else {
        pages[i].style.display = 'none'
        }
    }
}


// show all initialized forms in formset
function showForms(prefix, initialCount, requiredFields){
    let id = 0
    while (id < initialCount) {
        let form = $(`#id_${prefix}-${id}`)
        form.find('input,select').each (function() {
            let fieldName = $(this).attr('name').split('-')[2]
            if (requiredFields.includes(fieldName)){
                $(this).prop('required', true)
            }
            if (fieldName == 'DELETE'){
                $(this).prop('checked', false)
            }
        })
        form.collapse('show')
        id++ 
    }
}


// add new form to formset
function addForm(prefix, initialCount, requiredFields){
    // current total number of forms
    let totalElement = $(`#id_${prefix}-TOTAL_FORMS`)
    let total = totalElement.val()
    // clone new form
    let initialForm = $(`#id_${prefix}-${initialCount}`)
    let newForm = initialForm.clone(true)
    // destroy datepickers
    newForm.find('.date-picker').each (function() {
        $(this).datepicker().destroy()
    })
    // update id, name and value of the new form. Tag required fields.
    newForm.attr('id', `id_${prefix}-${total}`)
    newForm.find('input,select,button').each (function() {
        let fieldName = $(this).attr('name').split('-')[2]
        $(this).attr({
            'name': `${prefix}-${total}-${fieldName}`, 
            'id': `id_${prefix}-${total}-${fieldName}`
        })
        if (requiredFields.includes(fieldName)){
            $(this).prop('required', true)
        }
        if (fieldName == 'loppupvm'){
            $(this).addClass('date-picker picker-end')
        }
        if (fieldName == 'alkupvm'){
            $(this).addClass('date-picker picker-start')
        }
    })
    // add new form to DOM
    newForm.collapse('show')
    let lastForm = $(`#id_${prefix}-${total-1}`)
    lastForm.after(newForm)
    // update total amount of forms
    total++
    totalElement.val(total)
}


// delete form from formset
function deleteForm(prefix, id, requiredFields){
    let form = $(`#id_${prefix}-${id}`)
    form.collapse('hide')
    form.find('input,select').each (function() {
        let fieldName = $(this).attr('name').split('-')[2]
        if (requiredFields.includes(fieldName)){
            $(this).prop('required', false)
        }
        if (fieldName == 'DELETE'){
            $(this).prop('checked', true)
        }
    })
}