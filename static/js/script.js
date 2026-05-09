document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();
});

function fetchDashboardData() {
    const segmento = document.getElementById('filter-segment').value;
    
    // Llamada a la API de Flask
    fetch(`/api/data?segmento=${segmento}`)
        .then(response => response.json())
        .then(data => {
            // 1. Actualizar KPIs
            document.getElementById('total-clientes').innerText = data.total_clientes;
            document.getElementById('clientes-activos').innerText = data.clientes_activos;
            document.getElementById('ticket-promedio').innerText = `$${data.ticket_promedio}`;
            document.getElementById('ventas-promedio').innerText = `$${data.ventas_promedio_cliente}`;

            // 2. Llenar Tabla
            const tableBody = document.getElementById('table-body');
            tableBody.innerHTML = ''; // Limpiar tabla

            data.clientes.forEach(c => {
                const row = `
                    <tr>
                        <td>${c.customer_id}</td>
                        <td>${c.customer_name}</td>
                        <td>${c.segment}</td>
                        <td>${c.region}</td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error('Error:', error));
}