/**
 * OpenAI代理服务前端应用
 */

// 全局变量
let currentPage = 'dashboard';
let charts = {};
let chatHistory = [];

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否已登录
    checkLoginStatus();
    
    // 初始化导航
    initNavigation();
    
    // 初始化页面
    loadDashboard();
    
    // 初始化事件监听
    initEventListeners();
    
    // 检查服务状态
    checkServiceStatus();
});

/**
 * 检查登录状态
 */
function checkLoginStatus() {
    // 尝试加载仪表盘数据来检查登录状态
    fetch('/api/stats/overview')
        .then(response => {
            if (response.status === 401) {
                // 未登录，重定向到登录页面
                window.location.href = '/login';
            }
            return response.json();
        })
        .catch(error => {
            console.error('检查登录状态失败:', error);
        });
}

/**
 * 通用 fetch 请求包装器，处理 401 错误
 */
function authenticatedFetch(url, options = {}) {
    return fetch(url, options)
        .then(response => {
            if (response.status === 401) {
                // 未登录，重定向到登录页面
                window.location.href = '/login';
                return Promise.reject('未授权访问');
            }
            return response;
        });
}

/**
 * 初始化导航
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-page]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const page = this.getAttribute('data-page');
            if (page && page !== currentPage) {
                // 隐藏当前页面
                document.getElementById(`${currentPage}-page`).classList.add('d-none');
                
                // 显示新页面
                document.getElementById(`${page}-page`).classList.remove('d-none');
                
                // 更新导航状态
                document.querySelectorAll('.nav-link').forEach(navLink => {
                    navLink.classList.remove('active');
                });
                this.classList.add('active');
                
                // 更新当前页面
                currentPage = page;
                
                // 加载页面数据
                loadPageData(page);
            }
        });
    });
    
    // 设置默认激活的导航
    document.querySelector('.nav-link[data-page="dashboard"]').classList.add('active');
}

/**
 * 初始化事件监听
 */
function initEventListeners() {
    // 刷新按钮
    document.getElementById('refresh-btn').addEventListener('click', function() {
        loadPageData(currentPage);
        showToast('数据已刷新', 'success');
    });
    
    // Key管理相关事件
    document.getElementById('add-key-btn').addEventListener('click', function() {
        document.getElementById('add-key-form').reset();
        const modal = new bootstrap.Modal(document.getElementById('add-key-modal'));
        modal.show();
    });
    
    document.getElementById('save-key-btn').addEventListener('click', function() {
        saveKey();
    });
    
    // 模型管理相关事件
    document.getElementById('refresh-models-btn').addEventListener('click', function() {
        refreshModels();
    });
    
    document.getElementById('add-model-btn').addEventListener('click', function() {
        document.getElementById('add-model-form').reset();
        const modal = new bootstrap.Modal(document.getElementById('add-model-modal'));
        modal.show();
    });
    
    // 聊天页面模型刷新相关事件
    document.getElementById('refresh-chat-models-btn')?.addEventListener('click', function() {
        refreshChatModels();
    });
    
    document.getElementById('save-model-btn').addEventListener('click', function() {
        saveModel();
    });
    
    // 统计分析相关事件
    document.querySelectorAll('input[name="period"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                loadStatsData(this.value);
            }
        });
    });
    
    // 聊天相关事件
    document.getElementById('send-btn').addEventListener('click', function() {
        sendMessage();
    });
    
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

/**
 * 加载页面数据
 */
function loadPageData(page) {
    switch (page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'keys':
            loadKeys();
            break;
        case 'models':
            loadModels();
            break;
        case 'stats':
            loadStatsData();
            break;
        case 'chat':
            loadChat();
            break;
    }
}

/**
 * 加载仪表盘数据
 */
function loadDashboard() {
    // 加载概览数据
    authenticatedFetch('/api/stats/overview')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const dbInfo = data.data.database_info;
                document.getElementById('total-keys').textContent = dbInfo.keys_count;
                document.getElementById('active-keys').textContent = dbInfo.active_keys_count;
                document.getElementById('total-models').textContent = dbInfo.models_count;
                document.getElementById('total-requests').textContent = dbInfo.total_usage;
                
                // 加载模型使用分布图表
                loadModelUsageChart(data.data.model_usage);
                
                // 加载Key使用分布图表
                loadKeyUsageChart(data.data.key_usage);
                
                // 加载最近请求
                loadRecentRequests(data.data.recent_chats);
            } else {
                showToast('加载仪表盘数据失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('加载仪表盘数据失败: ' + error.message, 'danger');
        });
}

/**
 * 加载Key数据
 */
function loadKeys() {
    const tableBody = document.getElementById('keys-table');
    tableBody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="loading"></div> 加载中...</td></tr>';
    
    authenticatedFetch('/api/keys')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                tableBody.innerHTML = '';
                
                if (data.data.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="7" class="text-center">暂无Key数据</td></tr>';
                    return;
                }
                
                data.data.forEach(key => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${key.id}</td>
                        <td>${key.name || '-'}</td>
                        <td>${maskKey(key.key_value)}</td>
                        <td><span class="badge bg-${getStatusColor(key.status)}">${key.status}</span></td>
                        <td>${key.usage_count}</td>
                        <td>${key.last_used ? formatDate(key.last_used) : '-'}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editKey(${key.id})">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteKey(${key.id})">
                                <i class="bi bi-trash"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="testKey(${key.id})">
                                <i class="bi bi-check-circle"></i>
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="7" class="text-center">加载失败: ' + data.message + '</td></tr>';
            }
        })
        .catch(error => {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">加载失败: ' + error.message + '</td></tr>';
        });
}

/**
 * 加载模型数据
 */
function loadModels() {
    const tableBody = document.getElementById('models-table');
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="loading"></div> 加载中...</td></tr>';
    
    authenticatedFetch('/api/models')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                tableBody.innerHTML = '';
                
                if (data.data.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="6" class="text-center">暂无模型数据</td></tr>';
                    return;
                }
                
                data.data.forEach(model => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${model.id}</td>
                        <td>${model.model_name}</td>
                        <td>${model.description || '-'}</td>
                        <td>${formatDate(model.created_at)}</td>
                        <td>${formatDate(model.updated_at)}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editModel('${model.model_name}')">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteModel('${model.model_name}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center">加载失败: ' + data.message + '</td></tr>';
            }
        })
        .catch(error => {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center">加载失败: ' + error.message + '</td></tr>';
        });
}

/**
 * 加载统计数据
 */
function loadStatsData(period = 'all') {
    // 加载使用统计
    authenticatedFetch(`/api/stats/usage?period=${period}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalUsage = data.data.total_usage;
                document.getElementById('stats-total-usage').textContent = totalUsage.total_usage;
                document.getElementById('stats-total-tokens').textContent = totalUsage.total_tokens;
                document.getElementById('stats-total-requests').textContent = totalUsage.total_requests;
                
                // 加载模型统计图表
                loadModelStatsChart(data.data.model_stats);
                
                // 加载Key统计图表
                loadKeyStatsChart(data.data.key_stats);
            } else {
                showToast('加载统计数据失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('加载统计数据失败: ' + error.message, 'danger');
        });
    
    // 加载每小时使用趋势
    authenticatedFetch('/api/stats/hourly')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadHourlyUsageChart(data.data);
            } else {
                showToast('加载每小时使用趋势失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('加载每小时使用趋势失败: ' + error.message, 'danger');
        });
}

/**
 * 加载聊天数据
 */
function loadChat() {
    // 加载模型列表
    loadChatModels();
    
    // 加载聊天历史
    loadChatHistory();
}

/**
 * 加载聊天历史
 */
function loadChatHistory() {
    const historyContainer = document.getElementById('chat-history');
    historyContainer.innerHTML = '<div class="text-center text-muted"><div class="loading"></div> 加载中...</div>';
    
    authenticatedFetch('/api/chat/history?limit=10')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                historyContainer.innerHTML = '';
                chatHistory = data.data;
                
                if (data.data.length === 0) {
                    historyContainer.innerHTML = '<div class="text-center text-muted">暂无聊天历史</div>';
                    return;
                }
                
                data.data.forEach((chat, index) => {
                    const item = document.createElement('div');
                    item.className = 'chat-history-item';
                    item.innerHTML = `
                        <div class="d-flex justify-content-between">
                            <div>
                                <strong>${chat.model}</strong>
                                <div class="text-muted small">${formatDate(chat.timestamp)}</div>
                            </div>
                            <div>
                                <span class="badge bg-info">${chat.tokens_used} tokens</span>
                            </div>
                        </div>
                    `;
                    item.addEventListener('click', function() {
                        showChatHistory(chat);
                    });
                    historyContainer.appendChild(item);
                });
            } else {
                historyContainer.innerHTML = '<div class="text-center text-muted">加载失败: ' + data.message + '</div>';
            }
        })
        .catch(error => {
            historyContainer.innerHTML = '<div class="text-center text-muted">加载失败: ' + error.message + '</div>';
        });
}

/**
 * 显示聊天历史详情
 */
function showChatHistory(chat) {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = '';
    
    try {
        const request = JSON.parse(chat.request);
        const response = chat.response ? JSON.parse(chat.response) : null;
        
        // 显示请求
        if (request.messages && request.messages.length > 0) {
            request.messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `chat-message ${msg.role}`;
                messageDiv.innerHTML = `
                    <div>${msg.content}</div>
                    <div class="timestamp">${formatDate(chat.timestamp)}</div>
                `;
                chatContainer.appendChild(messageDiv);
            });
        }
        
        // 显示响应
        if (response && response.choices && response.choices.length > 0) {
            const choice = response.choices[0];
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message assistant';
            messageDiv.innerHTML = `
                <div>${choice.message.content}</div>
                <div class="timestamp">${formatDate(chat.timestamp)}</div>
            `;
            chatContainer.appendChild(messageDiv);
        }
        
        // 滚动到底部
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        chatContainer.innerHTML = '<div class="text-center text-muted">解析聊天历史失败</div>';
    }
}

/**
 * 发送消息
 */
function sendMessage() {
    const modelSelect = document.getElementById('model-select');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    
    const model = modelSelect.value;
    const message = chatInput.value.trim();
    
    if (!model) {
        showToast('请选择模型', 'warning');
        return;
    }
    
    if (!message) {
        showToast('请输入消息', 'warning');
        return;
    }
    
    // 清空输入框
    chatInput.value = '';
    
    // 显示用户消息
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'chat-message user';
    userMessageDiv.innerHTML = `
        <div>${message}</div>
        <div class="timestamp">${formatDate(new Date())}</div>
    `;
    chatContainer.appendChild(userMessageDiv);
    
    // 显示加载中消息
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = `
        <div><div class="loading"></div> 思考中...</div>
    `;
    chatContainer.appendChild(loadingDiv);
    
    // 滚动到底部
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // 发送请求
    authenticatedFetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            messages: [
                { role: 'user', content: message }
            ]
        })
    })
    .then(response => response.json())
    .then(data => {
        // 移除加载中消息
        chatContainer.removeChild(loadingDiv);
        
        if (data.success) {
            const response = data.data;
            if (response.choices && response.choices.length > 0) {
                const choice = response.choices[0];
                const assistantMessageDiv = document.createElement('div');
                assistantMessageDiv.className = 'chat-message assistant';
                assistantMessageDiv.innerHTML = `
                    <div>${choice.message.content}</div>
                    <div class="timestamp">${formatDate(new Date())}</div>
                `;
                chatContainer.appendChild(assistantMessageDiv);
            }
        } else {
            const errorMessageDiv = document.createElement('div');
            errorMessageDiv.className = 'chat-message assistant';
            errorMessageDiv.innerHTML = `
                <div>错误: ${data.message}</div>
                <div class="timestamp">${formatDate(new Date())}</div>
            `;
            chatContainer.appendChild(errorMessageDiv);
        }
        
        // 滚动到底部
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // 刷新聊天历史
        loadChatHistory();
    })
    .catch(error => {
        // 移除加载中消息
        chatContainer.removeChild(loadingDiv);
        
        const errorMessageDiv = document.createElement('div');
        errorMessageDiv.className = 'chat-message assistant';
        errorMessageDiv.innerHTML = `
            <div>请求失败: ${error.message}</div>
            <div class="timestamp">${formatDate(new Date())}</div>
        `;
        chatContainer.appendChild(errorMessageDiv);
        
        // 滚动到底部
        chatContainer.scrollTop = chatContainer.scrollHeight;
    });
}

/**
 * 保存Key
 */
function saveKey() {
    const name = document.getElementById('key-name').value.trim();
    const keyValue = document.getElementById('key-value').value.trim();
    const status = document.getElementById('key-status').value;
    
    if (!name || !keyValue) {
        showToast('请填写所有必填字段', 'warning');
        return;
    }
    
    authenticatedFetch('/api/keys', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            key_value: keyValue,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('add-key-modal'));
            modal.hide();
            showToast('Key添加成功', 'success');
            loadKeys();
            
            // 重置模态框
            resetKeyModal();
        } else {
            showToast('Key添加失败: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        showToast('Key添加失败: ' + error.message, 'danger');
    });
}

/**
 * 保存模型
 */
function saveModel() {
    const modelName = document.getElementById('model-name').value.trim();
    const description = document.getElementById('model-description').value.trim();
    const capabilities = document.getElementById('model-capabilities').value.trim();
    
    if (!modelName) {
        showToast('请填写模型名称', 'warning');
        return;
    }
    
    authenticatedFetch('/api/models', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model_name: modelName,
            description: description,
            capabilities: capabilities
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('add-model-modal'));
            modal.hide();
            showToast('模型添加成功', 'success');
            loadModels();
            
            // 重置模态框
            resetModelModal();
        } else {
            showToast('模型添加失败: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        showToast('模型添加失败: ' + error.message, 'danger');
    });
}

/**
 * 刷新模型列表
 */
function refreshModels() {
    showToast('正在刷新模型列表...', 'info');
    
    authenticatedFetch('/api/models?refresh=true')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('模型列表刷新成功', 'success');
                loadModels();
            } else {
                showToast('模型列表刷新失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('模型列表刷新失败: ' + error.message, 'danger');
        });
}

/**
 * 刷新聊天页面模型列表
 * 此函数会从OpenAI API获取最新模型列表并保存到数据库
 */
function refreshChatModels() {
    showToast('正在刷新聊天模型列表...', 'info');
    
    // 获取当前选中的模型
    const modelSelect = document.getElementById('model-select');
    const currentModel = modelSelect.value;
    
    // 调用刷新接口，从OpenAI API获取最新模型列表并保存到数据库
    authenticatedFetch('/api/models/chat?refresh=true')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 重新加载聊天模型列表（从数据库获取）
                loadChatModels(currentModel);
                showToast('聊天模型列表刷新成功', 'success');
            } else {
                showToast('聊天模型列表刷新失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('聊天模型列表刷新失败: ' + error.message, 'danger');
        });
}

/**
 * 加载聊天模型列表（直接从数据库获取）
 * 此函数直接从数据库获取模型列表，不调用OpenAI API
 */
function loadChatModels(selectedModel = null) {
    const modelSelect = document.getElementById('model-select');
    modelSelect.innerHTML = '<option value="">加载中...</option>';
    
    // 直接从数据库获取模型列表，不调用OpenAI API
    authenticatedFetch('/api/models/chat')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modelSelect.innerHTML = '';
                
                if (data.data.length === 0) {
                    modelSelect.innerHTML = '<option value="">暂无可用模型</option>';
                    return;
                }
                
                data.data.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.model_name;
                    option.textContent = model.model_name;
                    modelSelect.appendChild(option);
                });
                
                // 恢复之前选中的模型，如果没有则选择第一个
                if (selectedModel && data.data.some(model => model.model_name === selectedModel)) {
                    modelSelect.value = selectedModel;
                } else if (data.data.length > 0) {
                    modelSelect.value = data.data[0].model_name;
                }
            } else {
                modelSelect.innerHTML = '<option value="">加载失败</option>';
                showToast('加载模型列表失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            modelSelect.innerHTML = '<option value="">加载失败</option>';
            showToast('加载模型列表失败: ' + error.message, 'danger');
        });
}

/**
 * 检查服务状态
 */
function checkServiceStatus() {
    authenticatedFetch('/health')
        .then(response => response.json())
        .then(data => {
            const indicator = document.getElementById('status-indicator');
            if (data.status === 'healthy') {
                indicator.className = 'badge bg-success';
                indicator.innerHTML = '<i class="bi bi-circle-fill"></i> 运行中';
            } else {
                indicator.className = 'badge bg-danger';
                indicator.innerHTML = '<i class="bi bi-circle-fill"></i> 异常';
            }
        })
        .catch(error => {
            const indicator = document.getElementById('status-indicator');
            indicator.className = 'badge bg-danger';
            indicator.innerHTML = '<i class="bi bi-circle-fill"></i> 连接失败';
        });
}

/**
 * 加载模型使用分布图表
 */
function loadModelUsageChart(modelUsage) {
    const ctx = document.getElementById('model-usage-chart').getContext('2d');
    
    // 销毁旧图表
    if (charts.modelUsage) {
        charts.modelUsage.destroy();
    }
    
    const labels = modelUsage.map(item => item.model_name);
    const data = modelUsage.map(item => item.total_usage);
    
    charts.modelUsage = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#dc3545',
                    '#ffc107',
                    '#6f42c1',
                    '#20c997',
                    '#fd7e14',
                    '#6610f2'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

/**
 * 加载Key使用分布图表
 */
function loadKeyUsageChart(keyUsage) {
    const ctx = document.getElementById('key-usage-chart').getContext('2d');
    
    // 销毁旧图表
    if (charts.keyUsage) {
        charts.keyUsage.destroy();
    }
    
    const labels = keyUsage.map(item => item.name || `Key ${item.id}`);
    const data = keyUsage.map(item => item.usage_count);
    
    charts.keyUsage = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '使用次数',
                data: data,
                backgroundColor: '#0d6efd'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * 加载最近请求
 */
function loadRecentRequests(recentChats) {
    const tbody = document.getElementById('recent-requests');
    tbody.innerHTML = '';
    
    if (recentChats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">暂无请求数据</td></tr>';
        return;
    }
    
    recentChats.forEach(chat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(chat.timestamp)}</td>
            <td>${chat.model}</td>
            <td>Key ${chat.key_id}</td>
            <td>${chat.tokens_used}</td>
            <td><span class="badge bg-success">成功</span></td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * 加载模型统计图表
 */
function loadModelStatsChart(modelStats) {
    const ctx = document.getElementById('model-stats-chart').getContext('2d');
    
    // 销毁旧图表
    if (charts.modelStats) {
        charts.modelStats.destroy();
    }
    
    const labels = modelStats.map(item => item.model_name);
    const usageData = modelStats.map(item => item.usage_count);
    const tokensData = modelStats.map(item => item.tokens_used);
    
    charts.modelStats = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '使用次数',
                    data: usageData,
                    backgroundColor: '#0d6efd'
                },
                {
                    label: 'Token使用',
                    data: tokensData,
                    backgroundColor: '#198754'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * 加载Key统计图表
 */
function loadKeyStatsChart(keyStats) {
    const ctx = document.getElementById('key-stats-chart').getContext('2d');
    
    // 销毁旧图表
    if (charts.keyStats) {
        charts.keyStats.destroy();
    }
    
    const labels = keyStats.map(item => item.key_name || `Key ${item.key_id}`);
    const usageData = keyStats.map(item => item.usage_count);
    const tokensData = keyStats.map(item => item.tokens_used);
    
    charts.keyStats = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '使用次数',
                    data: usageData,
                    backgroundColor: '#0d6efd'
                },
                {
                    label: 'Token使用',
                    data: tokensData,
                    backgroundColor: '#198754'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * 加载每小时使用趋势图表
 */
function loadHourlyUsageChart(hourlyData) {
    const ctx = document.getElementById('hourly-usage-chart').getContext('2d');
    
    // 销毁旧图表
    if (charts.hourlyUsage) {
        charts.hourlyUsage.destroy();
    }
    
    const labels = hourlyData.map(item => {
        const date = new Date(item.hour);
        return date.getHours() + ':00';
    });
    const data = hourlyData.map(item => item.request_count);
    
    charts.hourlyUsage = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '请求数',
                data: data,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * 编辑Key
 */
function editKey(keyId) {
    // 获取Key信息
    authenticatedFetch(`/api/keys/${keyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const key = data.data;
                
                // 填充表单
                document.getElementById('key-name').value = key.name || '';
                document.getElementById('key-value').value = key.key_value || '';
                document.getElementById('key-status').value = key.status || 'active';
                
                // 更改模态框标题
                document.querySelector('#add-key-modal .modal-title').textContent = '编辑Key';
                
                // 更改保存按钮文本和功能
                const saveBtn = document.getElementById('save-key-btn');
                saveBtn.textContent = '更新';
                saveBtn.onclick = function() {
                    updateKey(keyId);
                };
                
                // 显示模态框
                const modal = new bootstrap.Modal(document.getElementById('add-key-modal'));
                modal.show();
            } else {
                showToast('获取Key信息失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('获取Key信息失败: ' + error.message, 'danger');
        });
}

/**
 * 更新Key
 */
function updateKey(keyId) {
    const name = document.getElementById('key-name').value.trim();
    const keyValue = document.getElementById('key-value').value.trim();
    const status = document.getElementById('key-status').value;
    
    if (!name || !keyValue) {
        showToast('请填写所有必填字段', 'warning');
        return;
    }
    
    authenticatedFetch(`/api/keys/${keyId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            key_value: keyValue,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('add-key-modal'));
            modal.hide();
            showToast('Key更新成功', 'success');
            loadKeys();
            
            // 重置模态框
            resetKeyModal();
        } else {
            showToast('Key更新失败: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        showToast('Key更新失败: ' + error.message, 'danger');
    });
}

/**
 * 重置Key模态框
 */
function resetKeyModal() {
    document.getElementById('add-key-form').reset();
    document.querySelector('#add-key-modal .modal-title').textContent = '添加Key';
    
    const saveBtn = document.getElementById('save-key-btn');
    saveBtn.textContent = '保存';
    saveBtn.onclick = function() {
        saveKey();
    };
}

/**
 * 删除Key
 */
function deleteKey(keyId) {
    if (confirm('确定要删除这个Key吗？')) {
        authenticatedFetch(`/api/keys/${keyId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Key删除成功', 'success');
                loadKeys();
            } else {
                showToast('Key删除失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('Key删除失败: ' + error.message, 'danger');
        });
    }
}

/**
 * 测试Key
 */
function testKey(keyId) {
    showToast('正在测试Key...', 'info');
    
    authenticatedFetch(`/api/keys/${keyId}/test`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const result = data.data;
            if (result.valid) {
                showToast('Key测试成功', 'success');
            } else {
                showToast('Key测试失败: ' + result.message, 'danger');
            }
        } else {
            showToast('Key测试失败: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        showToast('Key测试失败: ' + error.message, 'danger');
    });
}

/**
 * 编辑模型
 */
function editModel(modelName) {
    // 获取模型信息
    authenticatedFetch(`/api/models/${modelName}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const model = data.data;
                
                // 填充表单
                document.getElementById('model-name').value = model.model_name || '';
                document.getElementById('model-description').value = model.description || '';
                document.getElementById('model-capabilities').value = model.capabilities || '';
                
                // 更改模态框标题
                document.querySelector('#add-model-modal .modal-title').textContent = '编辑模型';
                
                // 更改保存按钮文本和功能
                const saveBtn = document.getElementById('save-model-btn');
                saveBtn.textContent = '更新';
                saveBtn.onclick = function() {
                    updateModel(modelName);
                };
                
                // 显示模态框
                const modal = new bootstrap.Modal(document.getElementById('add-model-modal'));
                modal.show();
            } else {
                showToast('获取模型信息失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('获取模型信息失败: ' + error.message, 'danger');
        });
}

/**
 * 更新模型
 */
function updateModel(modelName) {
    const name = document.getElementById('model-name').value.trim();
    const description = document.getElementById('model-description').value.trim();
    const capabilities = document.getElementById('model-capabilities').value.trim();
    
    if (!name) {
        showToast('请填写模型名称', 'warning');
        return;
    }
    
    authenticatedFetch(`/api/models/${name}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            description: description,
            capabilities: capabilities
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('add-model-modal'));
            modal.hide();
            showToast('模型更新成功', 'success');
            loadModels();
            
            // 重置模态框
            resetModelModal();
        } else {
            showToast('模型更新失败: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        showToast('模型更新失败: ' + error.message, 'danger');
    });
}

/**
 * 重置模型模态框
 */
function resetModelModal() {
    document.getElementById('add-model-form').reset();
    document.querySelector('#add-model-modal .modal-title').textContent = '添加模型';
    
    const saveBtn = document.getElementById('save-model-btn');
    saveBtn.textContent = '保存';
    saveBtn.onclick = function() {
        saveModel();
    };
}

/**
 * 删除模型
 */
function deleteModel(modelName) {
    if (confirm('确定要删除这个模型吗？')) {
        authenticatedFetch(`/api/models/${modelName}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('模型删除成功', 'success');
                loadModels();
            } else {
                showToast('模型删除失败: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('模型删除失败: ' + error.message, 'danger');
        });
    }
}

/**
 * 显示提示消息
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    
    bsToast.show();
    
    // 自动移除
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * 获取状态颜色
 */
function getStatusColor(status) {
    switch (status) {
        case 'active':
            return 'success';
        case 'inactive':
            return 'secondary';
        case 'error':
            return 'danger';
        default:
            return 'secondary';
    }
}

/**
 * 掩码Key值
 */
function maskKey(key) {
    if (key.length <= 8) {
        return key;
    }
    return key.substring(0, 8) + '...';
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}