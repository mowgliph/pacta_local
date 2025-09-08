/**
 * Reusable Table Component JavaScript Functions
 * Provides sorting, filtering, pagination, and search functionality
 */

// Global object to store table instances
window.reusableTables = window.reusableTables || {};

/**
 * Initialize a reusable table with all functionality
 * @param {string} tableId - The unique ID of the table
 * @param {Object} options - Configuration options
 */
function initializeReusableTable(tableId, options = {}) {
    const defaultOptions = {
        itemsPerPage: 10,
        sortable: true,
        searchable: true,
        filterable: true,
        currentPage: 1,
        sortColumn: null,
        sortDirection: 'asc'
    };
    
    const config = { ...defaultOptions, ...options };
    
    // Store table configuration
    window.reusableTables[tableId] = {
        config: config,
        originalData: [],
        filteredData: [],
        currentData: []
    };
    
    // Get table elements
    const table = document.getElementById(tableId);
    const searchInput = document.getElementById(`search-${tableId}`);
    const filtersPanel = document.getElementById(`filters-${tableId}`);
    
    if (!table) {
        console.error(`Table with ID '${tableId}' not found`);
        return;
    }
    
    // Store original data
    storeOriginalData(tableId);
    
    // Initialize functionality
    if (config.sortable) {
        initializeSorting(tableId);
    }
    
    if (config.searchable && searchInput) {
        initializeSearch(tableId);
    }
    
    if (config.filterable && filtersPanel) {
        initializeFilters(tableId);
    }
    
    // Initialize pagination
    initializePagination(tableId);
    
    // Initial render
    renderTable(tableId);
}

/**
 * Store original table data for filtering and searching
 */
function storeOriginalData(tableId) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
    
    const data = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        const rowData = {
            element: row,
            id: row.dataset.id || '',
            searchText: '',
            data: {}
        };
        
        cells.forEach((cell, index) => {
            const column = cell.dataset.column || `col_${index}`;
            const text = cell.textContent.trim();
            rowData.data[column] = text;
            rowData.searchText += ` ${text}`;
        });
        
        rowData.searchText = rowData.searchText.toLowerCase();
        return rowData;
    });
    
    window.reusableTables[tableId].originalData = data;
    window.reusableTables[tableId].filteredData = [...data];
    window.reusableTables[tableId].currentData = [...data];
}

/**
 * Initialize sorting functionality
 */
function initializeSorting(tableId) {
    const table = document.getElementById(tableId);
    const sortableHeaders = table.querySelectorAll('th.sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;
            const type = header.dataset.type || 'text';
            sortTable(tableId, column, type);
        });
    });
}

/**
 * Sort table by column
 */
function sortTable(tableId, column, type = 'text') {
    const tableInstance = window.reusableTables[tableId];
    const config = tableInstance.config;
    
    // Determine sort direction
    if (config.sortColumn === column) {
        config.sortDirection = config.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        config.sortColumn = column;
        config.sortDirection = 'asc';
    }
    
    // Sort the filtered data
    tableInstance.filteredData.sort((a, b) => {
        let valueA = a.data[column] || '';
        let valueB = b.data[column] || '';
        
        // Handle different data types
        switch (type) {
            case 'currency':
                valueA = parseFloat(valueA.replace(/[^0-9.-]/g, '')) || 0;
                valueB = parseFloat(valueB.replace(/[^0-9.-]/g, '')) || 0;
                break;
            case 'date':
                valueA = new Date(valueA);
                valueB = new Date(valueB);
                break;
            case 'number':
                valueA = parseFloat(valueA) || 0;
                valueB = parseFloat(valueB) || 0;
                break;
            default:
                valueA = valueA.toLowerCase();
                valueB = valueB.toLowerCase();
        }
        
        let comparison = 0;
        if (valueA > valueB) comparison = 1;
        if (valueA < valueB) comparison = -1;
        
        return config.sortDirection === 'desc' ? -comparison : comparison;
    });
    
    // Update sort indicators
    updateSortIndicators(tableId, column, config.sortDirection);
    
    // Reset to first page and render
    config.currentPage = 1;
    renderTable(tableId);
}

/**
 * Update sort indicators in table headers
 */
function updateSortIndicators(tableId, activeColumn, direction) {
    const table = document.getElementById(tableId);
    const headers = table.querySelectorAll('th.sortable');
    
    headers.forEach(header => {
        const column = header.dataset.column;
        header.classList.remove('sorted-asc', 'sorted-desc');
        
        if (column === activeColumn) {
            header.classList.add(`sorted-${direction}`);
        }
    });
}

/**
 * Initialize search functionality
 */
function initializeSearch(tableId) {
    const searchInput = document.getElementById(`search-${tableId}`);
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            searchTable(tableId, searchInput.value);
        }, 300));
    }
}

/**
 * Search table data
 */
function searchTable(tableId, searchTerm) {
    const tableInstance = window.reusableTables[tableId];
    const term = searchTerm.toLowerCase().trim();
    
    if (term === '') {
        tableInstance.filteredData = [...tableInstance.originalData];
    } else {
        tableInstance.filteredData = tableInstance.originalData.filter(row => 
            row.searchText.includes(term)
        );
    }
    
    // Apply existing filters
    applyFilters(tableId);
    
    // Reset to first page and render
    tableInstance.config.currentPage = 1;
    renderTable(tableId);
}

/**
 * Initialize filter functionality
 */
function initializeFilters(tableId) {
    const filtersPanel = document.getElementById(`filters-${tableId}`);
    
    if (filtersPanel) {
        const filterSelects = filtersPanel.querySelectorAll('.filter-select, .filter-date');
        
        filterSelects.forEach(filter => {
            filter.addEventListener('change', () => {
                applyFilters(tableId);
            });
        });
    }
}

/**
 * Apply all active filters
 */
function applyFilters(tableId) {
    const tableInstance = window.reusableTables[tableId];
    const filtersPanel = document.getElementById(`filters-${tableId}`);
    
    if (!filtersPanel) {
        renderTable(tableId);
        return;
    }
    
    const filters = filtersPanel.querySelectorAll('.filter-select, .filter-date');
    let filteredData = [...tableInstance.filteredData];
    
    filters.forEach(filter => {
        const column = filter.dataset.column;
        const value = filter.value.trim();
        
        if (value !== '') {
            filteredData = filteredData.filter(row => {
                const cellValue = row.data[column] || '';
                return cellValue.toLowerCase().includes(value.toLowerCase());
            });
        }
    });
    
    tableInstance.currentData = filteredData;
    tableInstance.config.currentPage = 1;
    renderTable(tableId);
}

/**
 * Toggle filters panel visibility
 */
function toggleFilters(tableId) {
    const filtersPanel = document.getElementById(`filters-${tableId}`);
    
    if (filtersPanel) {
        const isVisible = filtersPanel.style.display !== 'none';
        filtersPanel.style.display = isVisible ? 'none' : 'block';
    }
}

/**
 * Clear all filters
 */
function clearFilters(tableId) {
    const filtersPanel = document.getElementById(`filters-${tableId}`);
    
    if (filtersPanel) {
        const filters = filtersPanel.querySelectorAll('.filter-select, .filter-date');
        filters.forEach(filter => {
            filter.value = '';
        });
        
        applyFilters(tableId);
    }
}

/**
 * Initialize pagination
 */
function initializePagination(tableId) {
    const tableInstance = window.reusableTables[tableId];
    const itemsPerPageSelect = document.getElementById(`items-per-page-${tableId}`);
    
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', (e) => {
            changeItemsPerPage(tableId, parseInt(e.target.value));
        });
    }
}

/**
 * Change items per page
 */
function changeItemsPerPage(tableId, itemsPerPage) {
    const tableInstance = window.reusableTables[tableId];
    tableInstance.config.itemsPerPage = itemsPerPage;
    tableInstance.config.currentPage = 1;
    renderTable(tableId);
}

/**
 * Change page
 */
function changePage(tableId, direction) {
    const tableInstance = window.reusableTables[tableId];
    const config = tableInstance.config;
    const totalPages = Math.ceil(tableInstance.currentData.length / config.itemsPerPage);
    
    if (direction === 'prev' && config.currentPage > 1) {
        config.currentPage--;
    } else if (direction === 'next' && config.currentPage < totalPages) {
        config.currentPage++;
    } else if (typeof direction === 'number') {
        config.currentPage = direction;
    }
    
    renderTable(tableId);
}

/**
 * Render table with current data and pagination
 */
function renderTable(tableId) {
    const tableInstance = window.reusableTables[tableId];
    const config = tableInstance.config;
    const data = tableInstance.currentData || tableInstance.filteredData;
    
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const loadingSpinner = document.getElementById(`loading-${tableId}`);
    const emptyState = document.getElementById(`empty-${tableId}`);
    const tableContainer = document.getElementById(`table-container-${tableId}`);
    
    // Show loading state briefly
    if (loadingSpinner) {
        loadingSpinner.style.display = 'flex';
    }
    if (tableContainer) {
        tableContainer.style.display = 'none';
    }
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    setTimeout(() => {
        // Hide loading
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        // Check if we have data
        if (data.length === 0) {
            if (emptyState) {
                emptyState.style.display = 'flex';
            }
            if (tableContainer) {
                tableContainer.style.display = 'none';
            }
            return;
        }
        
        // Show table
        if (tableContainer) {
            tableContainer.style.display = 'block';
        }
        
        // Calculate pagination
        const startIndex = (config.currentPage - 1) * config.itemsPerPage;
        const endIndex = startIndex + config.itemsPerPage;
        const pageData = data.slice(startIndex, endIndex);
        
        // Clear tbody
        tbody.innerHTML = '';
        
        // Add rows
        pageData.forEach(rowData => {
            tbody.appendChild(rowData.element);
        });
        
        // Update pagination
        updatePagination(tableId, data.length);
        
    }, 100); // Brief loading delay for better UX
}

/**
 * Update pagination controls
 */
function updatePagination(tableId, totalItems) {
    const tableInstance = window.reusableTables[tableId];
    const config = tableInstance.config;
    const totalPages = Math.ceil(totalItems / config.itemsPerPage);
    
    // Update pagination info
    const paginationInfo = document.getElementById(`pagination-info-${tableId}`);
    if (paginationInfo) {
        const startItem = (config.currentPage - 1) * config.itemsPerPage + 1;
        const endItem = Math.min(config.currentPage * config.itemsPerPage, totalItems);
        paginationInfo.textContent = `Mostrando ${startItem}-${endItem} de ${totalItems} elementos`;
    }
    
    // Update page numbers
    const pageNumbers = document.getElementById(`page-numbers-${tableId}`);
    if (pageNumbers) {
        pageNumbers.innerHTML = '';
        
        // Calculate page range to show
        const maxVisiblePages = 5;
        let startPage = Math.max(1, config.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-number ${i === config.currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => changePage(tableId, i);
            pageNumbers.appendChild(pageBtn);
        }
    }
    
    // Update prev/next buttons
    const prevBtn = document.getElementById(`prev-${tableId}`);
    const nextBtn = document.getElementById(`next-${tableId}`);
    
    if (prevBtn) {
        prevBtn.disabled = config.currentPage === 1;
    }
    if (nextBtn) {
        nextBtn.disabled = config.currentPage === totalPages;
    }
}

/**
 * Export table data to CSV
 */
function exportTable(tableId) {
    const tableInstance = window.reusableTables[tableId];
    const table = document.getElementById(tableId);
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    
    // Remove actions column from export
    const actionColumnIndex = headers.findIndex(header => header.toLowerCase().includes('accion'));
    if (actionColumnIndex !== -1) {
        headers.splice(actionColumnIndex, 1);
    }
    
    let csvContent = headers.join(',') + '\n';
    
    tableInstance.currentData.forEach(rowData => {
        const values = Object.values(rowData.data);
        if (actionColumnIndex !== -1) {
            values.splice(actionColumnIndex, 1);
        }
        
        const escapedValues = values.map(value => {
            // Escape quotes and wrap in quotes if contains comma
            const stringValue = String(value || '').replace(/"/g, '""');
            return stringValue.includes(',') ? `"${stringValue}"` : stringValue;
        });
        
        csvContent += escapedValues.join(',') + '\n';
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${tableId}_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Utility function for debouncing
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Refresh table data (useful for dynamic content)
 */
function refreshTable(tableId) {
    storeOriginalData(tableId);
    const tableInstance = window.reusableTables[tableId];
    tableInstance.filteredData = [...tableInstance.originalData];
    tableInstance.currentData = [...tableInstance.originalData];
    tableInstance.config.currentPage = 1;
    renderTable(tableId);
}

/**
 * Get current table state (useful for debugging or state management)
 */
function getTableState(tableId) {
    return window.reusableTables[tableId];
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeReusableTable,
        sortTable,
        searchTable,
        toggleFilters,
        clearFilters,
        changePage,
        changeItemsPerPage,
        exportTable,
        refreshTable,
        getTableState
    };
}