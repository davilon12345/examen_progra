document.addEventListener('DOMContentLoaded', function() {
    const filterSegment = document.getElementById('filter-segment');
    const filterRegion = document.getElementById('filter-region');
    const filterYear = document.getElementById('filter-year');
    const filterCategory = document.getElementById('filter-category');

    // Instancias globales de Chart.js
    let chartVentasSegmento = null;
    let chartTopClientes = null;
    let chartClientesRegion = null;
    let chartTicketSegmento = null;
    let dataTableInstance = null;

    const alertBox = document.getElementById('global-alert');

    function handleFetchError(error) {
        console.error('Fetch Error:', error);
        if (window.showError) {
            window.showError(`Error al conectar con la base de datos. Verifica tu archivo config.py y asegúrate de que PostgreSQL esté corriendo y la base de datos "superstore" exista. Detalles: ${error.message}`);
        }
    }

    // Función para obtener filtros iniciales
    function loadFilters() {
        fetch('/api/filters')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if(data.error) throw new Error(data.error);
                
                populateSelect(filterSegment, data.segments || []);
                populateSelect(filterRegion, data.regions || []);
                populateSelect(filterYear, data.years || []);
                populateSelect(filterCategory, data.categories || []);

                updateDashboard();
            })
            .catch(handleFetchError);
    }

    function populateSelect(selectElement, items) {
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            selectElement.appendChild(option);
        });
    }

    const filters = [filterSegment, filterRegion, filterYear, filterCategory];
    filters.forEach(filter => {
        if(filter) filter.addEventListener('change', updateDashboard);
    });

    function updateDashboard() {
        const params = new URLSearchParams();
        if (filterSegment.value) params.append('segment', filterSegment.value);
        if (filterRegion.value) params.append('region', filterRegion.value);
        if (filterYear.value) params.append('year', filterYear.value);
        if (filterCategory.value) params.append('category', filterCategory.value);

        const queryString = `?${params.toString()}`;

        // Limpiar errores si había
        if(alertBox) alertBox.classList.add('d-none');
        const status = document.getElementById('connection-status');
        if(status) status.classList.add('d-none');

        Promise.all([
            fetch(`/api/kpis${queryString}`).then(res => res.json()),
            fetch(`/api/charts${queryString}`).then(res => res.json()),
            fetch(`/api/table_data${queryString}`).then(res => res.json())
        ]).then(([kpis, chartsData, tableData]) => {
            if(kpis.error) throw new Error(kpis.error);
            updateKPIs(kpis);
            updateCharts(chartsData);
            updateTable(tableData);
        }).catch(handleFetchError);
    }

    function updateKPIs(data) {
        document.getElementById('kpi-total-clientes').textContent = (data.total_clientes || 0).toLocaleString();
        document.getElementById('kpi-clientes-activos').textContent = (data.clientes_activos || 0).toLocaleString();
        document.getElementById('kpi-ticket-promedio').textContent = `$${(data.ticket_promedio || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById('kpi-ventas-promedio').textContent = `$${(data.ventas_promedio_cliente || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    }

    function updateCharts(data) {
        Chart.defaults.color = '#ccc';
        Chart.defaults.borderColor = '#333';
        Chart.defaults.font.family = "'Rajdhani', sans-serif";

        const ctxVentasSegmento = document.getElementById('chart-ventas-segmento');
        if (ctxVentasSegmento && data.ventas_segmento) {
            if (chartVentasSegmento) chartVentasSegmento.destroy();
            chartVentasSegmento = new Chart(ctxVentasSegmento.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.ventas_segmento.map(d => d.label),
                    datasets: [{
                        data: data.ventas_segmento.map(d => d.value),
                        backgroundColor: ['#00f3ff', '#39ff14', '#ff00ff', '#ff003c', '#0dcaf0'],
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
            });
        }

        const ctxTopClientes = document.getElementById('chart-top-clientes');
        if (ctxTopClientes && data.top_clientes) {
            if (chartTopClientes) chartTopClientes.destroy();
            chartTopClientes = new Chart(ctxTopClientes.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.top_clientes.map(d => d.label),
                    datasets: [{
                        label: 'Ventas ($)',
                        data: data.top_clientes.map(d => d.value),
                        backgroundColor: 'rgba(255, 0, 255, 0.6)', // Magenta
                        borderColor: '#ff00ff',
                        borderWidth: 1
                    }]
                },
                options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false }
            });
        }

        const ctxClientesRegion = document.getElementById('chart-clientes-region');
        if (ctxClientesRegion && data.clientes_region) {
            if (chartClientesRegion) chartClientesRegion.destroy();
            chartClientesRegion = new Chart(ctxClientesRegion.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.clientes_region.map(d => d.label),
                    datasets: [{
                        label: 'Clientes',
                        data: data.clientes_region.map(d => d.value),
                        backgroundColor: 'rgba(57, 255, 20, 0.6)', // Neon green
                        borderColor: '#39ff14',
                        borderWidth: 1
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        const ctxTicketSegmento = document.getElementById('chart-ticket-segmento');
        if (ctxTicketSegmento && data.ticket_segmento) {
            if (chartTicketSegmento) chartTicketSegmento.destroy();
            chartTicketSegmento = new Chart(ctxTicketSegmento.getContext('2d'), {
                type: 'line',
                data: {
                    labels: data.ticket_segmento.map(d => d.label),
                    datasets: [{
                        label: 'Ticket Promedio ($)',
                        data: data.ticket_segmento.map(d => d.value),
                        backgroundColor: 'rgba(0, 243, 255, 0.2)', // Cyan
                        borderColor: '#00f3ff',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointBackgroundColor: '#00f3ff',
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    }

    function updateTable(data) {
        if(!data || !Array.isArray(data)) return;
        
        const tableBody = document.querySelector('#customers-table tbody');
        if(!tableBody) return;
        
        tableBody.innerHTML = '';

        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold">${row.cliente}</td>
                <td><span class="badge" style="background-color: var(--card-bg); border: 1px solid var(--primary-color); color: var(--primary-color);">${row.segmento}</span></td>
                <td>${row.region}</td>
                <td>${row.total_pedidos}</td>
                <td>$${row.total_ventas.toLocaleString()}</td>
                <td class="${row.total_ganancia >= 0 ? 'text-success' : 'text-danger'}">$${row.total_ganancia.toLocaleString()}</td>
                <td>$${row.ticket_promedio.toLocaleString()}</td>
            `;
            tableBody.appendChild(tr);
        });

        if (dataTableInstance) {
            dataTableInstance.destroy();
        }
        
        const tableElement = document.getElementById('customers-table');
        dataTableInstance = new simpleDatatables.DataTable(tableElement, {
            searchable: true,
            fixedHeight: false,
            perPage: 10,
            labels: {
                placeholder: "Buscar jugador...",
                perPage: "jugadores por página",
                noRows: "No hay datos para mostrar (Revisa tu BD)",
                info: "Mostrando {start} a {end} de {rows} jugadores"
            }
        });
    }

    // Inicializar
    loadFilters();
});
