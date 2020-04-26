function createTable(div,data,opt){

    let options = opt || {}
    let width = options.width || '100%'
    let height = options.height || '100%'
    let sort = options.sort || false
    let border = options.border || false
    let padding = options.padding || '5px'
    let hover = options.hover || false
    let font = options.font || {size: '14px', fontFamily: 'Helvetica'}
    let textAlign = options.textAlign || 'center'
    let header = options.header || {color:'#000', backgroudColor: '#e9ecef'}
    let footer = options.footer || false

    // add table
    let container = d3.select('#' + div)
    container.selectAll('table').remove()
    let table = container.append('table')
        .attr('width', width)
        .attr('height', height)
        .style('font-family', font.fontFamily)
        .style('font-size', font.size)
        .style('border-collapse','collapse')
    let tbody = table.append('tbody')
    let thead = table.append('thead')
        .style('color',header.color)
        .style('background-color',header.backgroudColor)

    // check if we have some data
    if (!data || data.length == 0){
        tbody.append('tr')   
            .append('td')
            .text('No data')
            .style('font-size','12px')
            .style('font-style','italic')
            .style('background-color','#f5c6cb')
            .style('text-align','center') 
        return
    }

    // column names to list
    let columns = []
    data.forEach(row => {
        Object.keys(row).forEach(col => {
            if(!columns.includes(col)){columns.push(col)}
        })
    })

    // add headers
    thead.append('tr')
    let headers = thead.select('tr')
        .selectAll('th')
        .data(columns)
        .enter()
        .append('th')
        .text(d => d)
        .style('padding', padding)
        .style('text-align', textAlign)

    if (sort){
        headers.append('i')
            .attr('id','sort_up')
            .text(' \u2191')
            .style('opacity','0.3')  
        headers.append('i')
            .attr('id','sort_down')
            .text('\u2193')
            .style('opacity','0.3')  

        headers.on('click', function (d) {
            if (this.className != 'ascending'){
                rows.sort(function(a, b) {return d3.ascending(a[d],b[d])})
                this.className = 'ascending'
                headers.selectAll('#sort_up').style('opacity','0.3')
                headers.selectAll('#sort_down').style('opacity','0.3')
                d3.select(this).select('#sort_up').style('opacity','1')
            } else {
                rows.sort(function(a, b) {return d3.descending(a[d],b[d])})
                this.className = 'descending'
                headers.selectAll('#sort_up').style('opacity','0.3')
                headers.selectAll('#sort_down').style('opacity','0.3')
                d3.select(this).select('#sort_down').style('opacity','1')
            }
        })

        headers.on('mouseover',function(d) {
              d3.select(this).style('cursor', 'pointer')
            })

        headers.on('mouseout', function(d) {
              d3.select(this).style('cursor', 'default') 
            })
    }
     
    // add rows
    let rows = tbody.selectAll('tr')
        .data(data, d => d)
        .enter()
        .append('tr')

    if (hover){
        rows.on('mouseover', function(d){
            d3.select(this).style('background-color', '#f5f5f5')
        })
        rows.on('mouseout', function(d){
            d3.select(this).style('background-color', '#fff')
        })
    }

    // add cells
    rows.selectAll('td')
        .data(function (d) {
            return columns.map(function (h) {
                return {name: h, value: d[h]}
            })
        })
        .enter()
        .append('td')
        .text(function (d) { return d.value})
        .style('padding', padding)
        .style('text-align', textAlign)

    // add footer
    if (footer){
        // aggregate columns
        columns_total = []
        footer_columns = Object.keys(footer.columns)|| []
        for (i in columns){
            if (footer_columns.includes(i)){
                columns_total[i] = [0]
                let count = 0
                data.forEach(row => {
                    if (!(isNaN(parseFloat(row[columns[i]])))){
                        columns_total[i][0] += row[columns[i]]
                        count += 1
                    }
                })
                if (footer.columns[i] == 'mean' && count != 0){
                    columns_total[i][0] = columns_total[i][0] / count
                }
                columns_total[i][0] = Math.round(columns_total[i][0] * 10) / 10
            }
            else {         
                columns_total[i] = ['']
            }
        }

        let tfoot = table.append('tfoot')
        tfoot.append('tr')
        tfoot.select('tr')
            .selectAll('th')
            .data(columns_total)
            .enter()
            .append('th')
            .text(d => d)
            .style('padding', padding)
            .style('text-align', textAlign)
            .style('color', footer.color)
            .style('background-color', footer.backgroudColor)
    }

    if (border){
        table.style('border','solid 1px #dee2e6')
        table.selectAll('th').style('border','solid 1px #dee2e6').style('border-collapse','collapse')
        table.selectAll('td').style('border','solid 1px #dee2e6').style('border-collapse','collapse')
    }
}
