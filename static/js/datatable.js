document.addEventListener('DOMContentLoaded', function() {
    const tableSelector = document.getElementById('table-selector');
    const limitSelector = document.getElementById('limit-selector');
    const btnSearch = document.getElementById('btn-search-table');
    const tableElement = document.getElementById('dynamic-datatable');
    
    let dynamicDataTableInstance = null;

    // Cargar la lista de tablas al inicio
    fetch('/api/database_tables')
        .then(response => response.json())
        .then(data => {
            tableSelector.innerHTML = ''; // Limpiar
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Seleccione una tabla...';
            tableSelector.appendChild(defaultOption);

            data.tables.forEach(tableName => {
                const option = document.createElement('option');
                option.value = tableName;
                option.textContent = tableName;
                tableSelector.appendChild(option);
            });
        })
        .catch(error => console.error('Error al cargar tablas:', error));

    // Acción al hacer click en el botón de consultar
    btnSearch.addEventListener('click', function() {
        const selectedTable = tableSelector.value;
        const limit = limitSelector.value;

        if (!selectedTable) {
            alert('Por favor, seleccione una tabla primero.');
            return;
        }

        // Mostrar estado de carga (opcional pero buena UX)
        btnSearch.disabled = true;
        btnSearch.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> Cargando...';

        fetch(`/api/database_data?table=${selectedTable}&limit=${limit}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta de la red');
                }
                return response.json();
            })
            .then(data => {
                buildDynamicTable(data.columns, data.data);
            })
            .catch(error => {
                console.error('Error fetching table data:', error);
                alert('Ocurrió un error al cargar los datos.');
            })
            .finally(() => {
                // Restaurar botón
                btnSearch.disabled = false;
                btnSearch.innerHTML = '<i class="fa-solid fa-search me-2"></i> Consultar';
            });
    });

    // Función para construir la tabla dinámica HTML y aplicar simple-datatables
    function buildDynamicTable(columns, data) {
        // Si existe una instancia de data table, la destruimos
        if (dynamicDataTableInstance) {
            dynamicDataTableInstance.destroy();
        }

        // Construir Thead
        const thead = tableElement.querySelector('thead');
        thead.innerHTML = '';
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);

        // Construir Tbody
        const tbody = tableElement.querySelector('tbody');
        tbody.innerHTML = '';
        data.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                // Formateo simple para que no se desborde, se puede mejorar
                td.textContent = row[col] !== null ? row[col] : 'NULL';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        // Inicializar Simple-DataTables
        dynamicDataTableInstance = new simpleDatatables.DataTable(tableElement, {
            searchable: true,
            fixedHeight: false,
            perPage: 15,
            labels: {
                placeholder: "Buscar en tabla...",
                perPage: "registros por página",
                noRows: "No hay registros encontrados",
                info: "Mostrando {start} a {end} de {rows} registros"
            }
        });
    }
});
