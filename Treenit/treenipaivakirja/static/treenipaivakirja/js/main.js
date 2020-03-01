// Convert "hh:mm" to decimal
function timeStringToDecimal(time){
    if (typeof time === 'string' ) {
        sepIndex = time.indexOf(':')
        if (sepIndex != -1){
            var h = parseInt(time.slice(0,2))
            var min = parseInt(time.slice(3,5))
            return h + min/60.0
        }
        else {
            return 0
        }
    }
    else if (typeof time === 'number' ) {
        return time
    }
    else {
        return 0
    }
}


// Convert duration given in hours and minutes to string "hh:mm". 
function durationToString(h,mins){
    let hours = h || 0
    let minutes = mins || 0
    hours = ('0' + hours.toString()).slice(-2)
    minutes = ('0' + minutes.toString()).slice(-2)
    return hours + ':' + minutes
}


// Convert speed given in minutes and seconds to string "mm:ss". 
function speedToString(mins,s){
    if (mins == null && s == null){
        return ''
    }
    let minutes = mins || 0
    let seconds = s || 0
    minutes = ('0' + minutes.toString()).slice(-2)
    seconds = ('0' + seconds.toString()).slice(-2)
    return minutes + ':' + seconds
}


// Round number
function round(value, decimals) {
    return Number(Math.round(value+'e'+decimals)+'e-'+decimals)
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
function showForms(prefix, requiredFields){
    // total number of forms
    let total = $(`#id_${prefix}-TOTAL_FORMS`).val()
    // initial number of forms
    let initial = $(`#id_${prefix}-INITIAL_FORMS`).val()
    let id = 0
    while (id < total) {
        if (id != initial){ // do not show empty extra-form
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
        }
        id++ 
    }
}


// add new form to formset
function addForm(prefix, requiredFields){
    // current total number of forms
    let totalElement = $(`#id_${prefix}-TOTAL_FORMS`)
    let total = totalElement.val()
    // clone new form
    let initial = $(`#id_${prefix}-INITIAL_FORMS`).val()
    let newForm = $(`#id_${prefix}-${initial}`).clone(true)
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


// Create a list of all integers between start and end
function range(start, end) {
    let ans = []
    for (let i = start; i <= end; i++) {
        ans.push(i)
    }
    return ans
}