const API_URL = '';
let currentUser = null;
let itensTemporarios = [];
let produtosCatalogo = [];
let usuariosCatalogo = [];
let modalNovoPedidoInst = null;
let modalDetalhesInst = null;
let modalRecebimentoInst = null;
let modalEditarUsuarioInst = null;

function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch(e) { return null; }
}

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
    if (response.status === 401) {
        logout();
        throw new Error('Não autorizado');
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Erro na requisição');
    return data;
}

function showView(viewId) {
    if (currentUser && !currentUser.isAdmin) {
        if (['caixa', 'financeiro', 'produtos', 'usuarios'].includes(viewId)) {
            viewId = 'painel';
        }
    }

    document.querySelectorAll('.view-section').forEach(el => el.classList.add('d-none'));
    document.getElementById(`view-${viewId}`).classList.remove('d-none');
    
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    const activeLink = document.querySelector(`.nav-link[onclick="showView('${viewId}')"]`);
    if(activeLink) activeLink.classList.add('active');

    if (viewId === 'painel') carregarPainel();
    if (viewId === 'caixa') carregarCaixa();
    if (viewId === 'financeiro') carregarFinanceiro();
    if (viewId === 'produtos') carregarProdutos();
    if (viewId === 'usuarios') carregarUsuarios();
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const senha = document.getElementById('loginSenha').value;
    const errorEl = document.getElementById('loginError');
    errorEl.classList.add('d-none');

    try {
        const data = await apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, senha }) });
        localStorage.setItem('token', data.access_token);
        checkAuth();
    } catch (error) {
        errorEl.classList.remove('d-none');
        errorEl.textContent = error.message;
    }
}

function logout() {
    localStorage.removeItem('token');
    currentUser = null;
    checkAuth();
}

async function checkAuth() {
    const token = localStorage.getItem('token');
    const navbar = document.getElementById('mainNavbar');
    if (!token) {
        navbar.classList.add('d-none');
        showView('login');
        return;
    }
    
    currentUser = parseJwt(token);
    navbar.classList.remove('d-none');
    
    const adminMode = currentUser.nivel === true;
    currentUser.isAdmin = adminMode;
    
    document.querySelectorAll('.admin-only').forEach(el => {
        adminMode ? el.classList.remove('d-none') : el.classList.add('d-none');
    });

    document.getElementById('userNameDisplay').textContent = `Usuário ${currentUser.sub}`;
    showView('painel');
}

function formatCurrency(val) {
    return Number(val).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function getBadgeClass(status) {
    const s = status.toUpperCase();
    if (s === 'PENDENTE') return 'status-pendente';
    if (s === 'FINALIZADO') return 'status-finalizado';
    if (s === 'CANCELADO') return 'status-cancelado';
    return 'bg-secondary text-white';
}

async function carregarPainel() {
    try {
        const data = await apiFetch('/orders/');
        const grid = document.getElementById('painelGrid');
        grid.innerHTML = '';
        
        data.pedidos.filter(p => p.status === 'PENDENTE').forEach(p => {
            const isPendente = p.status === 'PENDENTE';
            const html = `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card shadow-sm border-0 rounded-4 h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold m-0">Pedido #${p.id}</h5>
                                <span class="status-badge ${getBadgeClass(p.status)}">${p.status}</span>
                            </div>
                            <h3 class="fw-bold text-primary mb-3">${formatCurrency(p.preco)}</h3>
                            <div class="d-flex gap-2 mt-4">
                                ${isPendente ? `<button class="btn btn-outline-primary btn-sm rounded-pill flex-grow-1" onclick="abrirDetalhes(${p.id})">Editar Itens</button>` : `<button class="btn btn-outline-secondary btn-sm rounded-pill flex-grow-1" onclick="abrirDetalhes(${p.id})">Ver Itens</button>`}
                                ${isPendente ? `<button class="btn btn-outline-danger btn-sm rounded-pill" onclick="atualizarStatus(${p.id}, 'CANCELADO')"><i class="bi bi-x-lg"></i></button>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            grid.insertAdjacentHTML('beforeend', html);
        });
    } catch (e) { console.error(e); }
}

async function carregarCaixa() {
    try {
        const data = await apiFetch('/orders/');
        const tbody = document.getElementById('caixaTableBody');
        tbody.innerHTML = '';
        data.pedidos.filter(p => p.status === 'PENDENTE').forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold">#${p.id}</td>
                <td>ID ${p.usuario}</td>
                <td class="fw-bold text-primary">${formatCurrency(p.preco)}</td>
                <td class="text-end">
                    <button class="btn btn-primary btn-sm rounded-pill px-3" onclick="abrirRecebimento(${p.id}, ${p.preco})">
                        Receber <i class="bi bi-cash ms-1"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e) { console.error(e); }
}

async function carregarFinanceiro() {
    try {
        const data = await apiFetch('/orders/');
        const tbody = document.getElementById('financeiroTableBody');
        tbody.innerHTML = '';
        let total = 0;
        const historico = data.pedidos.filter(p => p.status !== 'PENDENTE');
        historico.forEach(p => {
            if (p.status === 'FINALIZADO') total += p.preco;
            const forma = p.forma_pagamento ? `<span class="badge bg-light text-dark border">${p.forma_pagamento}</span>` : '-';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold">#${p.id}</td>
                <td><span class="status-badge ${getBadgeClass(p.status)}">${p.status}</span></td>
                <td>${forma}</td>
                <td class="fw-bold">${formatCurrency(p.preco)}</td>
                <td class="text-end">
                    <button class="btn btn-outline-danger btn-sm rounded-pill px-3" onclick="deletarPedido(${p.id})"><i class="bi bi-trash"></i> Excluir</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        document.getElementById('faturamentoTotal').textContent = formatCurrency(total);
    } catch(e) { console.error(e); }
}

async function carregarProdutos() {
    try {
        const data = await apiFetch('/produtos/');
        produtosCatalogo = data.produtos;
        const tbody = document.getElementById('produtosTableBody');
        if(!tbody) return;
        tbody.innerHTML = '';
        produtosCatalogo.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold">#${p.id}</td>
                <td>${p.nome}</td>
                <td class="fw-bold">${formatCurrency(p.preco)}</td>
                <td class="text-end">
                    <button class="btn btn-outline-danger btn-sm rounded-pill px-3" onclick="deletarProduto(${p.id})">Excluir</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e) { console.error(e); }
}

async function handleProduto(e) {
    e.preventDefault();
    const nome = document.getElementById('prodNome').value;
    const preco = parseFloat(document.getElementById('prodPreco').value);
    try {
        await apiFetch('/produtos/', { method: 'POST', body: JSON.stringify({ nome, preco }) });
        e.target.reset();
        carregarProdutos();
    } catch(e) { alert(e.message); }
}

async function deletarProduto(id) {
    if(!confirm("Excluir este produto do catálogo?")) return;
    try {
        await apiFetch(`/produtos/${id}`, { method: 'DELETE' });
        carregarProdutos();
    } catch(e) { alert(e.message); }
}

async function abrirNovoPedido() {
    itensTemporarios = [];
    renderTempItens();
    
    try {
        const data = await apiFetch('/produtos/');
        produtosCatalogo = data.produtos;
        const select = document.getElementById('tempProduto');
        select.innerHTML = '<option value="">Selecione...</option>';
        produtosCatalogo.forEach(p => {
            select.innerHTML += `<option value="${p.id}">${p.nome}</option>`;
        });
        
        document.getElementById('addTempItemForm').reset();
        document.getElementById('tempPreco').value = '';
        
        if (!modalNovoPedidoInst) {
            modalNovoPedidoInst = new bootstrap.Modal(document.getElementById('novoPedidoModal'));
        }
        modalNovoPedidoInst.show();
    } catch(e) { alert(e.message); }
}

function onSelectProduto() {
    const id = document.getElementById('tempProduto').value;
    const p = produtosCatalogo.find(x => x.id == id);
    if(p) {
        document.getElementById('tempPreco').value = p.preco.toFixed(2);
    } else {
        document.getElementById('tempPreco').value = '';
    }
}

function handleTempItem(e) {
    e.preventDefault();
    const select = document.getElementById('tempProduto');
    const id = select.value;
    const tipo = select.options[select.selectedIndex].text;
    const precoUnitario = parseFloat(document.getElementById('tempPreco').value);
    const quantidade = parseInt(document.getElementById('tempQtd').value);
    
    if(!id) return;
    
    itensTemporarios.push({ tipo, precoUnitario, quantidade });
    renderTempItens();
    
    select.value = '';
    document.getElementById('tempPreco').value = '';
    document.getElementById('tempQtd').value = 1;
}

function renderTempItens() {
    const tbody = document.getElementById('tempItensBody');
    tbody.innerHTML = '';
    let total = 0;
    
    if(itensTemporarios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted small py-3">Nenhum item adicionado.</td></tr>';
    } else {
        itensTemporarios.forEach((item, index) => {
            const sub = item.precoUnitario * item.quantidade;
            total += sub;
            tbody.innerHTML += `
                <tr>
                    <td>${item.tipo}</td>
                    <td>${item.quantidade}x</td>
                    <td>${formatCurrency(item.precoUnitario)}</td>
                    <td class="fw-bold">${formatCurrency(sub)}</td>
                    <td class="text-end"><button class="btn btn-link text-danger p-0" onclick="removerTempItem(${index})"><i class="bi bi-trash"></i></button></td>
                </tr>
            `;
        });
    }
    document.getElementById('tempTotal').textContent = `Total: ${formatCurrency(total)}`;
}

function removerTempItem(index) {
    itensTemporarios.splice(index, 1);
    renderTempItens();
}

async function salvarNovoPedido() {
    if(itensTemporarios.length === 0) {
        alert("Adicione pelo menos um item ao pedido.");
        return;
    }
    
    try {
        await apiFetch('/orders/', { 
            method: 'POST', 
            body: JSON.stringify({ itens: itensTemporarios }) 
        });
        modalNovoPedidoInst.hide();
        carregarPainel();
    } catch(e) { alert(e.message); }
}

async function atualizarStatus(id, novoStatus) {
    if(!confirm(`Deseja alterar o pedido #${id} para ${novoStatus}?`)) return;
    try {
        await apiFetch(`/orders/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: novoStatus })
        });
        if(!document.getElementById('view-painel').classList.contains('d-none')) carregarPainel();
        if(!document.getElementById('view-caixa').classList.contains('d-none')) carregarCaixa();
        if(!document.getElementById('view-financeiro').classList.contains('d-none')) carregarFinanceiro();
    } catch(e) { alert(e.message); }
}

function abrirRecebimento(id, preco) {
    document.getElementById('receberIdPedido').value = id;
    document.getElementById('receberTotalDisplay').textContent = formatCurrency(preco);
    if (!modalRecebimentoInst) {
        modalRecebimentoInst = new bootstrap.Modal(document.getElementById('recebimentoModal'));
    }
    modalRecebimentoInst.show();
}

async function confirmarRecebimento() {
    const id = document.getElementById('receberIdPedido').value;
    const formaPagamento = document.querySelector('input[name="formaPagamento"]:checked').value;
    
    try {
        await apiFetch(`/orders/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: 'FINALIZADO', forma_pagamento: formaPagamento })
        });
        modalRecebimentoInst.hide();
        if(!document.getElementById('view-painel').classList.contains('d-none')) carregarPainel();
        if(!document.getElementById('view-caixa').classList.contains('d-none')) carregarCaixa();
        if(!document.getElementById('view-financeiro').classList.contains('d-none')) carregarFinanceiro();
    } catch(e) { alert(e.message); }
}

async function abrirDetalhes(id) {
    document.getElementById('addIdPedido').value = id;
    await renderItensModal(id);
    if (!modalDetalhesInst) {
        modalDetalhesInst = new bootstrap.Modal(document.getElementById('pedidoModal'));
    }
    modalDetalhesInst.show();
}

async function renderItensModal(id) {
    try {
        const data = await apiFetch(`/orders/${id}`);
        const p = data.pedido;
        const list = document.getElementById('itensList');
        list.innerHTML = '';
        
        if (p.itens.length === 0) {
            list.innerHTML = '<p class="text-muted small text-center my-3">Nenhum item adicionado.</p>';
        } else {
            p.itens.forEach(i => {
                const isPendente = p.status === 'PENDENTE';
                list.insertAdjacentHTML('beforeend', `
                    <div class="item-row">
                        <div>
                            <span class="fw-bold d-block">${i.tipo}</span>
                            <span class="small text-muted">${i.quantidade}x ${formatCurrency(i.precoUnitario)}</span>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <span class="fw-bold">${formatCurrency(i.quantidade * i.precoUnitario)}</span>
                            ${isPendente ? `<button class="btn btn-link text-danger p-0 border-0" onclick="removerItem(${id}, ${i.id})"><i class="bi bi-trash"></i></button>` : ''}
                        </div>
                    </div>
                `);
            });
        }
        
        const form = document.getElementById('addItemForm');
        p.status === 'PENDENTE' ? form.classList.remove('d-none') : form.classList.add('d-none');
    } catch(e) { console.error(e); }
}

async function handleAddItem(e) {
    e.preventDefault();
    const id = document.getElementById('addIdPedido').value;
    const tipo = document.getElementById('addTipo').value;
    const precoUnitario = parseFloat(document.getElementById('addPreco').value);
    const quantidade = parseInt(document.getElementById('addQtd').value);
    
    try {
        await apiFetch(`/orders/${id}/items`, {
            method: 'POST',
            body: JSON.stringify({ quantidade, tipo, precoUnitario })
        });
        e.target.reset();
        await renderItensModal(id);
        carregarPainel();
    } catch(e) { alert(e.message); }
}

async function removerItem(idPedido, idItem) {
    try {
        await apiFetch(`/orders/${idPedido}/items/${idItem}`, { method: 'DELETE' });
        await renderItensModal(idPedido);
        carregarPainel();
    } catch(e) { alert(e.message); }
}

async function handleRegister(e) {
    e.preventDefault();
    const nome = document.getElementById('regNome').value;
    const email = document.getElementById('regEmail').value;
    const senha = document.getElementById('regSenha').value;
    const admin = document.getElementById('regAdmin').checked;
    const msg = document.getElementById('regMessage');
    
    try {
        await apiFetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ nome, email, senha, status: true, nivel: admin })
        });
        msg.className = 'small text-center mt-3 text-success';
        msg.textContent = 'Usuário cadastrado com sucesso!';
        e.target.reset();
    } catch(e) {
        msg.className = 'small text-center mt-3 text-danger';
        msg.textContent = e.message;
    }
}

async function deletarPedido(id) {
    if(!confirm(`Tem certeza que deseja excluir permanentemente o pedido #${id} do financeiro?`)) return;
    try {
        await apiFetch(`/orders/${id}`, { method: 'DELETE' });
        carregarFinanceiro();
    } catch(e) { alert(e.message); }
}

async function carregarUsuarios() {
    try {
        const data = await apiFetch('/auth/users');
        usuariosCatalogo = data.usuarios;
        const tbody = document.getElementById('usuariosTableBody');
        if(!tbody) return;
        tbody.innerHTML = '';
        usuariosCatalogo.forEach(u => {
            const nivelBadge = u.nivel ? '<span class="badge bg-primary">Admin</span>' : '<span class="badge bg-secondary">Normal</span>';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold">#${u.id}</td>
                <td>${u.nome}</td>
                <td>${u.email}</td>
                <td>${nivelBadge}</td>
                <td class="text-end">
                    <button class="btn btn-outline-primary btn-sm rounded-pill px-3 me-1" onclick="abrirEditarUsuario(${u.id})">Editar</button>
                    <button class="btn btn-outline-danger btn-sm rounded-pill px-3" onclick="deletarUsuario(${u.id})">Excluir</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e) { console.error(e); }
}

async function deletarUsuario(id) {
    if(!confirm("Tem certeza que deseja excluir este usuário?")) return;
    try {
        await apiFetch(`/auth/users/${id}`, { method: 'DELETE' });
        carregarUsuarios();
    } catch(e) { alert(e.message); }
}

function abrirEditarUsuario(id) {
    const u = usuariosCatalogo.find(user => user.id === id);
    if(!u) return;
    
    document.getElementById('editUserId').value = u.id;
    document.getElementById('editUserNome').value = u.nome;
    document.getElementById('editUserEmail').value = u.email;
    document.getElementById('editUserSenha').value = '';
    document.getElementById('editUserAdmin').checked = u.nivel;
    
    if (!modalEditarUsuarioInst) {
        modalEditarUsuarioInst = new bootstrap.Modal(document.getElementById('editarUsuarioModal'));
    }
    modalEditarUsuarioInst.show();
}

async function salvarEdicaoUsuario(e) {
    e.preventDefault();
    const id = document.getElementById('editUserId').value;
    const nome = document.getElementById('editUserNome').value;
    const email = document.getElementById('editUserEmail').value;
    const senha = document.getElementById('editUserSenha').value;
    const nivel = document.getElementById('editUserAdmin').checked;
    
    const payload = { nome, email, nivel };
    if (senha) payload.senha = senha;
    
    try {
        await apiFetch(`/auth/users/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        });
        modalEditarUsuarioInst.hide();
        carregarUsuarios();
    } catch(e) { alert(e.message); }
}

document.addEventListener('DOMContentLoaded', checkAuth);
