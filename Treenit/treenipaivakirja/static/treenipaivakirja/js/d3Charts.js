function drawComboChart(div,dataset,opt){

    // set default values
    let options = opt || {} 
    let animation = options.animation || false
    let avgLine = options.avgLine || false
    let barlabel = options.barlabel || false
    let circle = options.circle || {radius: 4, display: false}
    let colors = options.colors || d3.schemeCategory10 
    let fontFamily = options.fontFamily || 'Helvetica'
    let grid = options.grid || false 
    let height = options.height || 300
    let legend = options.legend || false
    let line = options.line || {width: 2, labels: false}
    let margin = options.margin || {top: 50, bottom: 50, left: 50, right: 50}
    let padding = options.padding || 0.1
    let responsiveness = options.responsiveness || false
    let serietype = options.serietype || false
    let ticks = options.ticks || {count: (dataset) ? dataset.length : 0}
    let title = options.title || {label:'', size:10, fontWeight: 'normal'}
    let tooltip = options.tooltip || false
    let traceDiff = options.traceDiff || false
    let type = options.type || 'bar'
    let width = options.width || 500
    let xaxis = options.xaxis || {font: {size: 10}, orientation: 'horizontal'}
    let xlabel = options.xlabel || {label:'', size:10, fontWeight: 'normal'}
    let yaxis = options.yaxis || {font: {size: 10}}
    let ylabel = options.ylabel || {label:'', size:10, fontWeight: 'normal'}
    let y2axis = options.y2axis || false
    let y2label = options.y2label || {label:'', size:10, fontWeight: 'normal'}
    
    let bordercolor = '#a8adb5'
    let borderwidth = 3

    // append svg
    let container = d3.select('#' + div)
    container.selectAll('svg').remove()
    let svg = container.append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('font-family', fontFamily)
        
    // responsiveness
    if (responsiveness) {svg.call(responsivefy)}

    // calculate centerpoint
    let centerX = margin.left + (width - margin.right - margin.left) / 2
    let centerY = margin.top + (height - margin.top - margin.bottom) / 2

    // check if we have some data
    if (!dataset || dataset.length == 0){
        svg.append('text')
            .attr('x', centerX)
            .attr('y', margin.top)
            .attr('text-anchor','middle')
            .text('No data')
            .style('font-size',12)
            .style('font-style','italic')
            .attr('fill','#dc3545')
        return
    }

    // copy of original dataset
    let data = JSON.parse(JSON.stringify(dataset))
    
    // add artificial headers to series if not provided in data
    let seriesHeaders = data[0]['series'].constructor == Object // true if series headers are provided in data
    if (!seriesHeaders){
        for (i in data){
            var val = data[i]['series']
            series_dict = {}
            if (val.length > 1){
                for (j in val){
                    series_dict['Serie' + (parseInt(j) + 1)] = val[j]
                }
            }
            else {
                series_dict['Serie1'] = val 
            }
            data[i]['series'] = series_dict
        }
    }

    // extract categories, series and values from data
    let categories = data.map(d => d.category)
    let series = []
    let values = []
    data.forEach(element => {
        Object.keys(element.series).forEach(key => {
            if (!series.includes(key)){series.push(key)}
        })
        values = values.concat(Object.values(element.series))
    })
    let types = {}
    for (let i=0; i<series.length; i++){
        if (serietype && Object.keys(serietype).includes(String(i))){
            types[series[i]] = serietype[i]
        }
        else {
            types[series[i]] = type
        }
    }

    let series1 = series.slice(0)
    let values1 = values.slice(0)
    let series2 = []
    let values2 = []

    // if secondary Y-axis, split series and values according to corresponging axis
    if (y2axis){
        var index = y2axis.serieIndex
        if (!Array.isArray(index)){index = [index]}
        index.sort(function(a, b){return a - b})
        for (let i = index.length-1; i >= 0; i--){
            if (typeof series[index[i]] != 'undefined'){
                series1.splice(index[i],1)
                series2.push(series[index[i]])
            }
        }
        values1 = []
        series1.forEach(serie => {
            data.forEach(element => {
                let val = element.series[serie]
                if (typeof val !== 'undefined' && val !== ''){
                    values1.push(element.series[serie])
                }   
            })
        })
        series2.forEach(serie => {
            data.forEach(element => {
                let val = element.series[serie]
                if (typeof val !== 'undefined' && val !== ''){
                    values2.push(element.series[serie])
                }  
            })
        })
    }

    // enable bootstrap tooltip
    try {$(function () {$('[data-toggle="tooltip"]').tooltip()})}
    catch(err) {}

    // create scales
    let categoryScale = d3.scaleBand()
        .range([margin.left, width - margin.right])
        .domain(categories) 
        .padding(padding)

    let seriesScale = d3.scaleBand()
        .range([0, categoryScale.bandwidth()])
        .domain(series.filter(d => types[d] == 'bar')) 
        .padding(padding)

    let yaxisMin = yaxis.min
    let yaxisMax = yaxis.max
    if (typeof yaxisMin == 'undefined' || yaxisMin > d3.max(values1, d => +d)) {yaxisMin = d3.min(values1, d => +d) - ((d3.max(values1, d => +d) - d3.min(values1, d => +d)) * 0.1)}
    if (typeof yaxisMax == 'undefined' || yaxisMax < d3.max(values1, d => +d)) {yaxisMax = d3.max(values1, d => +d) + ((d3.max(values1, d => +d) - d3.min(values1, d => +d)) * 0.1)}

    let y1Scale = d3.scaleLinear()
        .range([height - margin.bottom, margin.top])
        .domain([yaxisMin,yaxisMax])

    let y2axisMin = y2axis.min
    let y2axisMax = y2axis.max
    if (typeof y2axisMin == 'undefined' || y2axisMin > d3.max(values2, d => +d)) {y2axisMin = d3.min(values2, d => +d) - ((d3.max(values2, d => +d) - d3.min(values2, d => +d)) * 0.1)}
    if (typeof y2axisMax == 'undefined' || y2axisMax < d3.max(values2, d => +d)) {y2axisMax = d3.max(values2, d => +d) + ((d3.max(values2, d => +d) - d3.min(values2, d => +d)) * 0.1)}

    let y2Scale = d3.scaleLinear()
        .range([height - margin.bottom, margin.top])
        .domain([y2axisMin,y2axisMax])

    let colorScale = d3.scaleOrdinal()
        .domain(series)
        .range(colors)

    // create Y1-axis
    if (series1.length > 0){
        var axisY1 = d3.axisLeft(y1Scale)
        svg.append('g')
            .attr('class', 'axisy1')
            .style('font-size', yaxis.font.size || 12)
            .attr('transform', `translate(${margin.left},0)`)
            .call(axisY1)
    }

    // create Y2-axis
    if (series2.length > 0){
        var axisY2 = d3.axisRight(y2Scale)
        svg.append('g')
            .attr('class', 'axisy2')
            .style('font-size', y2axis.font.size || 12)
            .attr('transform', `translate(${width - margin.right},0)`)
            .call(axisY2)
    }

    // create grid
    if (grid && typeof axisY1 !== 'undefined'){
        svg.append('g')
        .attr('class', 'grid')        
        .attr('transform', `translate(${margin.left},0)`)
        .call(axisY1
            .tickSize(-width + margin.left + margin.right, 0, 0)
            .tickFormat(''))

        svg.select('.grid').selectAll('line')
            .style('stroke', '#D6D6D6')
            .style('fill','none')

        svg.select('.grid').selectAll('path')
            .style('display','none')  //remove upper most grid line 
    }

    // create X-axis
    // get tick values based on number of ticks provided as parameter
    let categoryCount = data.length
    let gap = Math.round(categoryCount / Math.min(ticks.count,data.length))
    let tickValues = []

    for (var i = 0; i < categories.length; i++){
        if ((i+1) % gap == 0){
            tickValues.push(categories[i])
        }
    }
    
    let axisX = d3.axisBottom(categoryScale).tickValues(tickValues)

    svg.append('g')
        .attr('class', 'axisx')  
        .style('font-size', xaxis.font.size || 12)  
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(axisX)

    if (xaxis.orientation == 'vertical'){
        svg.select('.axisx').selectAll("text")	
            .style('text-anchor', 'end')
            .attr('dx', '-1em')
            .attr('dy', '-0.6em')
            .attr('transform', 'rotate(-90)')
    }
    else if (xaxis.orientation == 'skew'){
        svg.select('.axisx').selectAll("text")	
            .style('text-anchor', 'end')
            .attr('dx', '-1em')
            .attr('dy', '-0.2em')
            .attr('transform', 'rotate(-45)')
    }
    
    // add bars
    series1.filter(d => types[d] == 'bar').forEach(serie => {
        addBars(serie,y1Scale,yaxisMin)
        addBarlabels(serie,y1Scale)
        if (tooltip){
            addTooltips(serie)
        }
    })
    series2.filter(d => types[d] == 'bar').forEach(serie => {
        addBars(serie,y2Scale,y2axisMin)
        addBarlabels(serie,y2Scale)
        if (tooltip){
            addTooltips(serie)
        }
    })

    // add lines
    series1.filter(d => types[d] == 'line').forEach(serie => {
        addLine(serie,y1Scale)
        addCircle(serie,y1Scale)
        if (line.labels){addLinelabels(serie,y1Scale)}
        if (tooltip){addTooltips(serie)}
    })
    series2.filter(d => types[d] == 'line').forEach(serie => {
        addLine(serie,y2Scale)
        addCircle(serie,y2Scale)
        if (line.labels){addLinelabels(serie,y2Scale)}
        if (tooltip){addTooltips(serie)}
    })

    // add titles
    addTitles(svg,width,height,centerX,centerY,margin,title,xlabel,ylabel,y2label)

    // add legend
    if (legend){
        addLegend(svg,series,colorScale,legend)
    }

    // add average-line
    if (avgLine){ 
        addAvgLine(values1,y1Scale)
        if (y2axis){addAvgLine(values2,y2Scale)} 
    }

    // add mouseenter and mouseleave actions to bars
    svg.selectAll('rect')
        .on('mouseenter', function() { 
            d3.select(this).style('stroke', bordercolor)
            d3.select(this).style('stroke-width', borderwidth)

            if (traceDiff){
                y = d3.select(this).attr('value')

                svg.append('line')
                    .attr('class','baseline')
                    .attr('x1', margin.left)
                    .attr('y1', d3.select(this).attr('y'))
                    .attr('x2', width - margin.right)
                    .attr('y2', d3.select(this).attr('y'))
                    .attr('stroke', '#DC3545')

                series.forEach(serie => {
                    svg.select('.barlabels_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
                        .selectAll('.barlabel')
                        .text(d => {
                            if (d.series[serie] == 0){ return ''}
                            else {
                                let diff = Math.round((d.series[serie] - y) / y * 100)
                                if (diff > 0) {return '+' + diff + '%'}
                                else {return diff + '%'}
                            }
                        })
                        .style('font-size',traceDiff.size)
                        .style('fill',traceDiff.color)
                })
            }
        })
        .on('mouseleave', function() { 
            d3.select(this).style('stroke', 'none')
            svg.selectAll('.baseline').remove()
            series.forEach(serie => {
                svg.select('.barlabels_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
                    .selectAll('.barlabel')
                    .text(d => {return (!barlabel || d.series[serie] == 0) ? '' : d.series[serie]})
                    .style('font-size', barlabel.size)
                    .style('fill', barlabel.color)
            })
    })


    function addBars(serie,yScale,yaxisMin){
        let bars = svg.append('g')
            .attr('class', 'bars_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
            .selectAll('rect')
            .data(data.filter((d,i) => {return typeof d.series[serie] !== 'undefined' && d.series[serie] !== ''})) 

        bars.enter().append('rect')
            .attr('x', d => categoryScale(d.category) + seriesScale(serie))
            .attr('y', d => {return animation ? yScale(yaxisMin) : yScale(d.series[serie])})
            .attr('width', seriesScale.bandwidth()) 
            .attr('height', d => {return animation ? 0 : yScale(yaxisMin) - yScale(d.series[serie])})
            .attr('fill', colorScale(serie))
            .attr('category', d => d.category)
            .attr('serie', serie)
            .attr('value', d => d.series[serie])

        if (animation) { 
            svg.selectAll('.bars_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))	
                .selectAll('rect')
                .transition()
                    .delay(function (d, i) { return i * (animation.delay || 10) })
                    .duration((animation.duration || 500))
                    .attr('y', d => yScale(d.series[serie]))
                    .attr('height', d => yScale(yaxisMin) - yScale(d.series[serie]))
        }
    }

    function addBarlabels(serie,yScale){
        svg.append('g')
            .attr('class','barlabels_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
            .selectAll('.barlabel')  		
            .data(data.filter((d,i) => {return typeof d.series[serie] !== 'undefined' && d.series[serie] !== ''}))
            .enter()
            .append('text')
            .attr('class','barlabel')
            .attr('x', d => categoryScale(d.category) + seriesScale(serie) + seriesScale.bandwidth() / 2 )
            .attr('y', d => yScale(d.series[serie]))
            .attr('dy', '2em')
            .attr('text-anchor', 'middle')
            .text(d => {return (!barlabel || d.series[serie] == 0) ? '' : d.series[serie]})
            .style('font-size', barlabel.size || 10)
            .style('fill', barlabel.color)
            .style('opacity', animation ? '0' : '1')

        if (animation) {
            svg.selectAll('.barlabel')
                .transition()
                    .delay(function (d, i) { return i * (animation.delay * 1.5 || 20)})
                    .duration(animation.duration  * 1.5 || 1000)
                    .style('opacity', '1')
        }
    }

    function addLine(serie,yScale){
        let valueline = d3.line()
            .x(d => categoryScale(d.category) + categoryScale.bandwidth() / 2)
            .y(d => yScale(d.series[serie]))

        svg.append('g')
            .attr('class', 'line_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
            .append("path")
            .datum(data.filter((d,i) => {return typeof d.series[serie] !== 'undefined' && d.series[serie] !== ''}))
            .attr("d", valueline)
            .attr('fill', 'none')
            .style('stroke', colorScale(serie))
            .style('stroke-width', line.width || 2)
    }

    function addLinelabels(serie,yScale){
        svg.append('g')
            .attr('class','linelabels_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
            .selectAll('.linelabel')  		
            .data(data.filter((d,i) => {return typeof d.series[serie] !== 'undefined' && d.series[serie] !== ''}))
            .enter()
            .append('text')
            .attr('class','linelabel')
            .attr('x', d => categoryScale(d.category) + categoryScale.bandwidth() / 2 )
            .attr('y', d => yScale(d.series[serie]))
            .attr('dy', '-1em')
            .attr('text-anchor', 'middle')
            .text(d => d.series[serie])
            .style('font-size', line.labels.size || 10)
            .style('fill', line.labels.color)
    }

    function addCircle(serie,yScale){
        svg.append('g')
            .attr('class', 'dots_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_'))
            .selectAll('.dot')
            .data(data.filter((d,i) => {return typeof d.series[serie] !== 'undefined' && d.series[serie] !== ''}))
            .enter()
            .append('circle') 
            .attr('class', 'dot')
            .attr('cx', d => categoryScale(d.category) + categoryScale.bandwidth() / 2)
            .attr('cy', d => yScale(d.series[serie]))
            .attr('r', circle.radius)
            .style('fill', colorScale(serie))
            .style('fill-opacity', circle.display ? '1' : '0')
            .on('mouseenter', function() { 
                if (!circle.display){
                    d3.select(this).style('fill-opacity', 1)
                }
                d3.select(this).style('stroke', bordercolor)
                d3.select(this).style('stroke-width', borderwidth)
            })
            .on('mouseleave', function() { 
                if (!circle.display){
                    d3.select(this).style('fill-opacity', 0)
                }
                d3.select(this).style('stroke', 'none')
            })
    }

    function addTooltips(serie){
        if (types[serie] == 'bar'){
            var elements = svg.selectAll('.bars_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_')).selectAll('rect')	
        }
        else if (types[serie] == 'line'){
            var elements = svg.selectAll('.dots_' + serie.replace(/[^a-zA-Z0-9-_]/g,'_')).selectAll('.dot')	
        }
        elements.attr('data-toggle','tooltip')
            .attr('data-placement','top')
            .attr('title', d => (tooltip.prefix || '') + (seriesHeaders ? serie + ': ' : '') + d.series[serie] + (tooltip.suffix || ''))

        }


    function addAvgLine(values,yScale){
        values = values.filter((d) => {return typeof d !== 'undefined' && d !== ''})
        avgY = Math.round(d3.mean(values, d => d) * 10) / 10

        avg = svg.append('g')
            .attr('class','avg')

        avg.append('line')
            .attr('x1', margin.left)
            .attr('y1', yScale(avgY))
            .attr('x2', width - margin.right)
            .attr('y2', yScale(avgY))
            .attr('class','avgline')
            .style('stroke', avgLine.color || '#DC3545')
            .style('opacity', animation ? '0' : '1')
            
        avg.append('text')
            .text((avgLine.prefix || '') + avgY + (avgLine.suffix || ''))
            .attr('x', width - margin.right)
            .attr('y', yScale(avgY))
            .attr("dx", ".35em")
            .attr("dy", ".35em")
            .style('font-size', avgLine.size)
            .attr('fill', avgLine.color || '#DC3545')
            .style('opacity', animation ? '0' : '1')

        if (animation){
            avg.select('line')
                .transition()
                .duration(animation.duration * 2 || 1000)
                .style('opacity', '1')
            avg.select('text')
                .transition()
                .duration(animation.duration * 2|| 1000)
                .style('opacity', '1')
        }
    }
}



function drawPieChart(div,dataset,opt){

    // set default values
    let options = opt || {}
    let fontFamily = options.fontFamily || 'Helvetica'
    let title = options.title || {label:'', size:10, fontWeight: 'normal'}
    let width = options.width || 500
    let height = options.height || 300
    let margin = options.margin || {top: 50, bottom: 50, left: 50, right: 50}
    let colors = options.colors || d3.schemeCategory10 
    let tooltip = options.tooltip || false
    let slicelabel = options.slicelabel || {size:10, color:'#fff', threshold: 0.10}
    let radius = options.radius || {inner: 0, outer: (height - margin.top - margin.bottom) / 2}
    let legend = options.legend || false
    let maxSliceCount = options.maxSliceCount || 20
    let responsiveness = options.responsiveness || false

    let bordercolor = '#a8adb5'
    let borderwidth = 4

    // append svg
    let container = d3.select('#' + div)
    container.selectAll('svg').remove()
    let svg = container.append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('font-family', fontFamily)
    
    // responsiveness
    if (responsiveness) {svg.call(responsivefy)}

    // calculate centerpoint
    let centerX = margin.left + (width - margin.right - margin.left) / 2
    let centerY = margin.top + (height - margin.top - margin.bottom) / 2

    // check if we have some data
    if (!dataset || dataset.length == 0){
        svg.append('text')
            .attr('x', centerX)
            .attr('y', margin.top)
            .attr('text-anchor','middle')
            .text('No data')
            .style('font-size',12)
            .style('font-style','italic')
            .attr('fill','#dc3545')
        return
    }

    // copy of original dataset
    let data = JSON.parse(JSON.stringify(dataset))

    let sumSeries = d3.sum(data, d => d.series)

    // enable bootstrap tooltip
    try {$(function () {$('[data-toggle="tooltip"]').tooltip()})}
    catch(err) {}
    
    // sort data by value
    data = data.sort((a, b) => {return d3.descending(a.series, b.series)})

    // restrict number of slices
    other = Math.round(d3.sum(data.filter((d,i) => {return i >= (maxSliceCount - 1)}), d => d.series) * 10 ) / 10
    data = data.filter((d,i) => {return i < (maxSliceCount - 1)})
    data.push({'category':'Other', series: other})
    data = data.sort((a, b) => {return d3.descending(a.series, b.series)})

    // drop zero values
    data = data.filter(d => {return d.series > 0})

    // create color-scale
    let categories = data.map(d => d.category)
    let colorScale = d3.scaleOrdinal()
        .domain(categories)
        .range(colors)

    // create pie
    let pie = d3.pie()
        .value(d => d.series)
 
    let arc = d3.arc()
        .outerRadius(radius.outer)
        .innerRadius(radius.inner)

    let chart = svg.append('g')
        .attr('class','pie')
        .attr("transform", `translate(${centerX}, ${centerY})`)

    chart.selectAll('g')
        .data(pie(data))
        .enter()
        .append('g')
        .attr('class','slice')
        .attr('category', d => d.data.category)
        .attr('value', d => d.data.series)
        .append('path')
        .attr('d', arc)
        .attr('fill', d => colorScale(d.data.category))
        .style('stroke', '#fff')
        .style('stroke-width', 1)
        .on('mouseenter', function() { 
            d3.select(this).style('stroke', bordercolor)
            d3.select(this).style('stroke-width', borderwidth)
        })
        .on('mouseleave', function() { 
            d3.select(this).style('stroke', '#fff')
            d3.select(this).style('stroke-width', 1)
        })

    let slice = container.selectAll(".slice")

    // add labels to slices
    if (slicelabel){

        let threshold = slicelabel.threshold || 0.10

        slice.append("text")
            .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"})
            .text(d => { 
                if (d.data.series / sumSeries > threshold) {return d.data.category}
            })
            .attr('text-anchor', 'middle')
            .style('font-size',slicelabel.size)
            .attr('fill', slicelabel.color)
        slice.append("text")
            .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"})
            .attr("dy", "1.2em")
            .text(d => { 
                if (d.data.series / sumSeries > threshold) {return Math.round(d.data.series / sumSeries * 100) + ' %'}
            })
            .attr('text-anchor', 'middle')
            .style('font-size',slicelabel.size)
            .attr('fill', slicelabel.color)
    }


    // add tooltips
    if (tooltip){
        svg.selectAll('.slice')		
        .attr('data-toggle','tooltip')
        .attr('data-placement', d => {
            if (d.startAngle < Math.PI) {return 'right'}
            else {return 'left'}
            })
        .attr('title', d => (tooltip.prefix || '') + d.data.category + ': ' + d.data.series + (tooltip.suffix || ''))
    }

    // add title
    svg.append('text')
      .attr('x', centerX )
      .attr('y', margin.top / 2)
      .attr('text-anchor', 'middle')
      .text(title.label)
      .style('font-size',title.size)
      .style('font-weight', title.fontWeight)
      .attr('fill', title.color)

   // add legend
   if (legend){
        addLegend(svg,categories,colorScale,legend)
   }

}


// Function for creating legend
function addLegend(svg,labels,colorScale,options){

    // set default values
    let coord = options.coord || {x:0, y:0}
    let rect = options.rect || {size: 15, space: 5}
    let font = options.font || {size: 10}
 
    let legend = svg.append('g')
        .attr('class', 'legends')
        .selectAll('.legend')
        .data(labels)
        .enter()
        .append('g')
        .attr('class', 'legend')
        .attr('transform', function(d, i) {
            let height = rect.size + rect.space
            let vert = coord.y + (i * height) 
            return 'translate(' + coord.x + ',' + vert + ')'
        })
 
     legend.append('rect')
         .attr('width', rect.size)
         .attr('height', rect.size)
         .style('fill', d => colorScale(d))
 
     legend.append('text')
         .attr('x', rect.size + rect.space)
         .attr('y', rect.size)
         .attr('dy', -rect.size/4)
         .attr("font-size", font.size)
         .text(d => d)
}



function responsivefy(svg) {

    // get container + svg aspect ratio
    var container = d3.select(svg.node().parentNode),
        width = parseInt(svg.style("width")),
        height = parseInt(svg.style("height")),
        aspect = width / height

    // add viewBox and preserveAspectRatio properties,
    // and call resize so that svg resizes on inital page load
    svg.attr("viewBox", "0 0 " + width + " " + height)
        .attr("perserveAspectRatio", "xMinYMid")
        .call(resize)

    // to register multiple listeners for same event type, 
    // you need to add namespace, i.e., 'click.foo'
    // necessary if you call invoke this function for multiple svgs
    // api docs: https://github.com/mbostock/d3/wiki/Selections#on
    d3.select(window).on("resize." + container.attr("id"), resize)

    // get width of container and resize svg to fit it
    function resize() {
        var targetWidth = parseInt(container.style("width"))
        svg.attr("width", targetWidth)
        svg.attr("height", Math.round(targetWidth / aspect))
    }
}


// Adds x- and y-labels and main title for chart
function addTitles(svg,width,height,centerX,centerY,margin,title,xlabel,ylabel,y2label) {
    // add title
    svg.append('text')
        .attr('x', centerX )
        .attr('y', margin.top / 2)
        .attr('text-anchor', 'middle')
        .text(title.label)
        .style('font-size',title.size)
        .style('font-weight', title.fontWeight)
        .attr('fill', title.color)

    // add x-label
    svg.append('text')
        .attr('x', centerX )
        .attr('y', height - (margin.bottom / 2))
        .attr('text-anchor','middle')
        .text(xlabel.label)
        .style('font-size',xlabel.size)
        .style('font-weight', xlabel.fontWeight)
        .attr('fill', xlabel.color)

    // add y1-label
    svg.append('text')
        .attr('transform', `rotate(-90,${margin.left / 3},${centerY})`)
        .attr('x', margin.left / 3)
        .attr('y', centerY)
        .attr('text-anchor','start')
        .text(ylabel.label)
        .style('font-size',ylabel.size)
        .style('font-weight', ylabel.fontWeight)
        .attr('fill', ylabel.color)

    // add y2-label
    svg.append('text')
        .attr('transform', `rotate(-90,${width - margin.right / 3 * 2},${centerY})`)
        .attr('x', width - margin.right / 3 * 2)
        .attr('y', centerY)
        .attr('text-anchor','start')
        .text(y2label.label)
        .style('font-size',y2label.size)
        .style('font-weight', y2label.fontWeight)
        .attr('fill', y2label.color)
}