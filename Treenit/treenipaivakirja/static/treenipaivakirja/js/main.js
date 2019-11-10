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