/**
 * Componente de Bloque de Proveedores y Clientes
 * Maneja la visualización de los últimos proveedores y clientes en un bloque del panel
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos los bloques de proveedores-clientes en la página
    document.querySelectorAll('.providers-clients-block').forEach(bloque => {
        const idComponente = bloque.id;
        const urlApiProveedores = bloque.dataset.providersApi;
        const urlApiClientes = bloque.dataset.clientsApi;

        // Obtener elementos del DOM
        const elementoCarga = document.getElementById(`${idComponente}-loading`);
        const elementoError = document.getElementById(`${idComponente}-error`);
        const elementoContenido = document.getElementById(`${idComponente}-content`);
        const listaProveedores = document.getElementById(`${idComponente}-providers-list`);
        const listaClientes = document.getElementById(`${idComponente}-clients-list`);
        const botonReintentar = elementoError ? elementoError.querySelector('.btn-retry') : null;

        // Mostrar estado de carga
        function mostrarCargando() {
            if (elementoCarga) elementoCarga.style.display = 'flex';
            if (elementoError) elementoError.style.display = 'none';
            if (elementoContenido) elementoContenido.style.display = 'none';
        }

        // Mostrar estado de error
        function mostrarError() {
            if (elementoCarga) elementoCarga.style.display = 'none';
            if (elementoError) elementoError.style.display = 'flex';
            if (elementoContenido) elementoContenido.style.display = 'none';
        }

        // Mostrar contenido
        function mostrarContenido() {
            if (elementoCarga) elementoCarga.style.display = 'none';
            if (elementoError) elementoError.style.display = 'none';
            if (elementoContenido) elementoContenido.style.display = 'block';
        }

        // Formatear número con separador de miles
        function formatearNumero(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        }

        // Crear HTML de un elemento de la lista
        function crearElementoLista(item, tipo) {
            const icono = tipo === 'provider' ? 'building' : 'user-tie';
            const cantidad = item.total_contracts || item.contracts_count || 0;
            const cantidadFormateada = formatearNumero(cantidad);
            
            return `
                <div class="list-item">
                    <div class="item-icon">
                        <i class="fas fa-${icono}"></i>
                    </div>
                    <div class="item-details">
                        <h4 class="item-title">${item.nombre || item.razon_social || 'Sin nombre'}</h4>
                        <p class="item-subtitle">${cantidadFormateada} contrato${cantidad !== 1 ? 's' : ''}</p>
                    </div>
                    <div class="item-actions">
                        <a href="/${tipo === 'provider' ? 'proveedores' : 'clientes'}/${item.id}" 
                           class="btn btn-sm btn-link" 
                           title="Ver detalles">
                            <i class="fas fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            `;
        }

        // Mostrar datos en la interfaz
        function mostrarDatos(proveedores, clientes) {
            try {
                // Mostrar proveedores
                if (listaProveedores) {
                    listaProveedores.innerHTML = '';
                    const topProveedores = Array.isArray(proveedores) ? proveedores.slice(0, 5) : [];
                    
                    if (topProveedores.length > 0) {
                        topProveedores.forEach(proveedor => {
                            listaProveedores.insertAdjacentHTML('beforeend', crearElementoLista(proveedor, 'provider'));
                        });
                    } else {
                        listaProveedores.innerHTML = '<div class="no-items">No hay proveedores disponibles</div>';
                    }
                }

                // Mostrar clientes
                if (listaClientes) {
                    listaClientes.innerHTML = '';
                    const topClientes = Array.isArray(clientes) ? clientes.slice(0, 5) : [];
                    
                    if (topClientes.length > 0) {
                        topClientes.forEach(cliente => {
                            listaClientes.insertAdjacentHTML('beforeend', crearElementoLista(cliente, 'client'));
                        });
                    } else {
                        listaClientes.innerHTML = '<div class="no-items">No hay clientes disponibles</div>';
                    }
                }
                
                console.log('Datos cargados correctamente:', { proveedores, clientes });
            } catch (error) {
                console.error('Error al mostrar los datos:', error);
                mostrarError();
            }
        }

        // Obtener datos de la API
        async function obtenerDatos() {
            mostrarCargando();

            try {
                // Obtener datos de proveedores y clientes en paralelo
                const [respuestaProveedores, respuestaClientes] = await Promise.all([
                    fetch(urlApiProveedores),
                    fetch(urlApiClientes)
                ]);

                if (!respuestaProveedores.ok || !respuestaClientes.ok) {
                    throw new Error('Error al cargar los datos');
                }

                const [datosProveedores, datosClientes] = await Promise.all([
                    respuestaProveedores.json(),
                    respuestaClientes.json()
                ]);

                // Función para extraer datos de la respuesta de la API
                function extraerDatos(respuesta, claveDatos) {
                    // Si la respuesta ya es un array, devolverlo directamente
                    if (Array.isArray(respuesta)) {
                        return respuesta;
                    }
                    
                    // Intentar extraer datos de la estructura anidada
                    if (respuesta && respuesta.data) {
                        // Estructura: { data: { [claveDatos]: [...] } }
                        if (respuesta.data[claveDatos]) {
                            return respuesta.data[claveDatos];
                        }
                        // Estructura: { data: [...] }
                        if (Array.isArray(respuesta.data)) {
                            return respuesta.data;
                        }
                    }
                    
                    // Estructura antigua: { [claveDatos]: [...] }
                    return respuesta[claveDatos] || [];
                }

                // Procesar y mostrar los datos
                try {
                    const proveedores = extraerDatos(datosProveedores, 'proveedores');
                    const clientes = extraerDatos(datosClientes, 'clientes');
                    mostrarDatos(proveedores, clientes);
                    mostrarContenido();
                } catch (error) {
                    console.error('Error al procesar los datos:', error);
                    mostrarError();
                }
            } catch (error) {
                console.error('Error al obtener datos:', error);
                mostrarError();
            }
        }

        // Manejadores de eventos
        if (botonReintentar) {
            botonReintentar.addEventListener('click', obtenerDatos);
        }

        // Carga inicial de datos
        if (urlApiProveedores && urlApiClientes) {
            obtenerDatos();
        } else {
            console.error('Faltan URLs de API para el bloque de proveedores-clientes');
            mostrarError();
        }
    });
});