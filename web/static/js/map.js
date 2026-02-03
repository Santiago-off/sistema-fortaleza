let lastState = [];
const canvas = document.getElementById('map-canvas');

function updateData() {
    axios.get('/api/nodes').then(response => {
        let nodes = response.data;
        
        // Orden alfabético estricto
        nodes.sort((a, b) => a.name.localeCompare(b.name));

        // Comparación de estado para evitar refrescos de CPU innecesarios
        if (JSON.stringify(nodes) === JSON.stringify(lastState)) return;
        lastState = nodes;

        renderInterface(nodes);
    });

}
function renderTable(nodes) {
    const tbody = document.getElementById('table-body');
    let html = '';
    
    nodes.forEach(node => {
        // Verificamos si tiene una IP remota para mostrar el escudo
        const hasRemoteIP = node.remote_ip && node.remote_ip !== "N/A" && !node.remote_ip.startsWith('0.0.0.0');

        html += `
            <tr class="proc-row">
                <td>
                    <div style="color: #00ff41; font-weight: bold;">${node.name}</div>
                    <div style="font-size: 0.75em; color: #666;">PID: ${node.pid}</div>
                </td>
                <td><code style="color: #0088ff;">${node.remote_ip}</code></td>
                <td><small style="font-family: monospace; font-size: 10px; color: #444;">${node.hash.substring(0,16)}...</small></td>
                <td>
                    <button class="btn-action" onclick="executeAction(${node.pid}, 'isolate', '${node.remote_ip}', '${node.name}')" title="Aislar Proceso">⏸️</button>
                    
                    ${hasRemoteIP ? 
                        `<button class="btn-action" onclick="executeAction(${node.pid}, 'block_ip', '${node.remote_ip}', '${node.name}')" title="Bloquear IP en Firewall" style="background: rgba(0, 136, 255, 0.2); border: 1px solid #0088ff;">🛡️</button>` 
                        : ''
                    }

                    <button class="btn-action" onclick="executeAction(${node.pid}, 'terminate', '${node.remote_ip}', '${node.name}')" title="Kill & Blacklist" style="background: rgba(255, 0, 0, 0.2); border: 1px solid #ff0000;">🚫</button>
                </td>
            </tr>`;
    });
    tbody.innerHTML = html;
}

function renderInterface(nodes) {
    const term = document.getElementById('proc-search')?.value.toLowerCase() || "";
    const tbody = document.getElementById('table-body');
    let tableHtml = '';
    let svgHtml = `<svg width="100%" height="100%" viewBox="0 0 600 600">`;

    const centerX = 300;
    const centerY = 300;
    const radius = 220;

    nodes.forEach((node, i) => {
        const isMatch = node.name.toLowerCase().includes(term) || node.pid.toString().includes(term);
        const angle = (i * (360 / nodes.length)) * (Math.PI / 180);
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);

        // Solo añadimos a la tabla si coincide con la búsqueda
        if (isMatch) {
            tableHtml += `
                <tr style="border-left: 2px solid #00ff41;">
                    <td><b style="color:#00ff41">${node.name}</b><br><small style="color:#666">PID: ${node.pid}</small></td>
                    <td><code style="color:#0088ff">${node.remote_ip}</code></td>
                    <td><small style="word-break:break-all; font-size:10px">${node.hash.substring(0,32)}...</small></td>
                    <td>
                        <button class="btn-action" onclick="executeAction(${node.pid}, 'isolate', '${node.remote_ip}', '${node.name}')">⏸️</button>
                        <button class="btn-action" onclick="executeAction(${node.pid}, 'terminate', '${node.remote_ip}', '${node.name}')" style="background:#400">🚫</button>
                    </td>
                </tr>`;
        }

        // El mapa siempre muestra TODO, pero resalta lo buscado
        const color = isMatch ? "#00ff41" : "#113311";
        const opacity = isMatch ? "1" : "0.3";
        
        svgHtml += `
            <line x1="${centerX}" y1="${centerY}" x2="${x}" y2="${y}" stroke="${color}" stroke-width="0.5" opacity="0.2" />
            <circle cx="${x}" cy="${y}" r="4" fill="${color}" opacity="${opacity}">
                <title>${node.name} (PID: ${node.pid})</title>
            </circle>
            <text x="${x+6}" y="${y+3}" fill="${color}" font-size="8" opacity="${opacity}">${node.name}</text>
        `;
    });

    svgHtml += `<circle cx="${centerX}" cy="${centerY}" r="10" fill="#fff" /></svg>`;
    
    tbody.innerHTML = tableHtml;
    canvas.innerHTML = svgHtml;
}

setInterval(updateData, 3000);
updateData();