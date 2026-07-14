from flask import Flask, request, jsonify, render_template_string
import pymssql

app = Flask(__name__)

# Dinamik bağlantı kuran yardımcı fonksiyon
def get_dynamic_connection(config):
    try:
        conn = pymssql.connect(
            server=config.get('server'),
            port=int(config.get('port', 1433)),
            database=config.get('database'),
            user=config.get('user'),
            password=config.get('password'),
            tds_version="7.3",
            timeout=10 # Bağlantı zaman aşımı süresi
        )
        return conn
    except Exception as e:
        print("❌ Dinamik Bağlantı Hatası:", str(e))
        return None

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal SQL Analytics Suite</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root[data-theme="dark"] {
            --bg-base: #090d16;
            --bg-surface: #111827;
            --bg-surface-hover: #1f2937;
            --border: #1f2937;
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.15);
            --success: #10b981;
            --danger: #f43f5e;
            --card-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }

        :root[data-theme="light"] {
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-hover: #f1f5f9;
            --border: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --primary: #4f46e5;
            --primary-glow: rgba(79, 70, 229, 0.1);
            --success: #10b981;
            --danger: #ef4444;
            --card-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.05);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.2s, border-color 0.2s, color 0.2s; }
        body { 
            background: var(--bg-base); 
            color: var(--text-primary); 
            font-family: 'Inter', system-ui, sans-serif; 
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }

        .dashboard-container {
            width: 100%;
            max-width: 1400px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: var(--card-shadow);
            overflow: hidden;
        }

        header {
            padding: 30px 40px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, transparent 100%);
        }

        .brand-zone h1 {
            font-size: 24px;
            font-weight: 800;
            background: linear-gradient(to right, #818cf8, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-zone p { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }

        .workspace { padding: 40px; }

        /* Veritabanı Ayar Paneli */
        .config-panel {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 30px;
        }
        .config-panel-title {
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 15px;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }

        /* Form Elemanları */
        .field-group { display: flex; flex-direction: column; gap: 6px; }
        .field-group label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); }
        input[type="text"], input[type="password"], select {
            width: 100%;
            padding: 12px 16px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg-base);
            color: var(--text-primary);
            font-size: 13.5px;
            outline: none;
        }
        input:focus, select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-glow); }

        /* Workspace Grid */
        .workspace-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 30px;
        }
        @media (max-width: 768px) {
            .workspace-grid { grid-template-columns: 1fr; }
        }

        .btn-action {
            padding: 12px 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--bg-surface);
            color: var(--text-primary);
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-action:hover { background: var(--bg-surface-hover); }

        .btn-generate {
            width: 100%;
            background: var(--primary);
            color: white;
            padding: 16px;
            border-radius: 14px;
            border: none;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .btn-generate:hover { transform: translateY(-2px); box-shadow: 0 15px 25px rgba(99, 102, 241, 0.35); }

        /* Rapor & Tablo Alanları */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
            display: none;
        }
        .stat-card {
            background: var(--bg-base);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        .stat-card .value { font-size: 24px; font-weight: 800; color: var(--primary); }
        .stat-card .label { font-size: 11px; text-transform: uppercase; color: var(--text-secondary); margin-top: 4px; font-weight: 600; }

        .report-wrapper {
            border-top: 1px solid var(--border);
            padding-top: 40px;
            display: none;
        }
        .report-header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }
        .search-box { min-width: 250px; }

        .table-responsive {
            width: 100%;
            overflow-x: auto;
            border-radius: 16px;
            border: 1px solid var(--border);
            background: var(--bg-surface);
        }
        table { width: 100%; border-collapse: collapse; font-size: 13.5px; text-align: left; white-space: nowrap; }
        th, td { padding: 16px 24px; border-bottom: 1px solid var(--border); }
        th { background: var(--bg-base); color: var(--text-secondary); font-weight: 700; text-transform: uppercase; font-size: 11px; }
        tr:hover td { background-color: var(--bg-surface-hover); }

        .btn-excel { background: var(--success); color: white; border: none; }
        .btn-pdf { background: var(--danger); color: white; border: none; }

        .error { color: var(--danger); background: rgba(244, 63, 94, 0.1); border: 1px solid var(--danger); padding: 16px; border-radius: 12px; margin-top: 20px; }
    </style>
</head>
<body>

    <div class="dashboard-container">
        <header>
            <div class="brand-zone">
                <h1>Universal SQL Analytics</h1>
                <p>Kendi SQL Server'ınızı bağlayarak anında rapor üretin</p>
            </div>
            <button class="btn-action" id="theme-toggle" onclick="toggleTheme()">☀️ Temayı Değiştir</button>
        </header>

        <div class="workspace">
            <div class="config-panel">
                <div class="config-panel-title">🔑 SQL Server Bağlantı Ayarları</div>
                <div class="config-grid">
                    <div class="field-group">
                        <label>Sunucu Adı (Server / IP)</label>
                        <input type="text" id="db_server" placeholder="örn: localhost veya IP" value="WIN-51TT52DNHRR">
                    </div>
                    <div class="field-group">
                        <label>Port</label>
                        <input type="text" id="db_port" placeholder="1433" value="1433">
                    </div>
                    <div class="field-group">
                        <label>Veritabanı (Database)</label>
                        <input type="text" id="db_name" placeholder="gastropos" value="gastropos">
                    </div>
                    <div class="field-group">
                        <label>Kullanıcı (User)</label>
                        <input type="text" id="db_user" placeholder="sa" value="sa">
                    </div>
                    <div class="field-group">
                        <label>Şifre (Password)</label>
                        <input type="password" id="db_password" placeholder="••••••" value="12345s">
                    </div>
                </div>
                <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
                    <button class="btn-action" style="background: var(--primary); color: white; border: none;" onclick="loadAllViews()">🔌 Sunucuya Bağlan ve Viewleri Getir</button>
                </div>
            </div>

            <div class="workspace-grid">
                <div class="field-group">
                    <label>Veri Kaynağı (Seçili View)</label>
                    <select id="view" onchange="loadColumns()">
                        <option value="">-- Önce Yukarıdan Sunucuya Bağlanın --</option>
                    </select>
                </div>
                <div class="field-group">
                    <label>Gösterilecek Kolonlar</label>
                    <select id="kolonlar" multiple></select>
                </div>
            </div>

            <button class="btn-generate" onclick="getReport()">⚡ Seçili Raporu Analiz Et ve Oluştur</button>

            <div id="error-box"></div>

            <div class="stats-grid" id="stats-grid">
                <div class="stat-card">
                    <div class="value" id="stat-rows">0</div>
                    <div class="label">Toplam Kayıt Satırı</div>
                </div>
                <div class="stat-card">
                    <div class="value" id="stat-cols">0</div>
                    <div class="label">Görüntülenen Kolon</div>
                </div>
                <div class="stat-card">
                    <div class="value" style="color: var(--success);" id="stat-time">Şimdi</div>
                    <div class="label">Analiz Zamanı</div>
                </div>
            </div>

            <div class="report-wrapper" id="report-wrapper">
                <div class="report-header-bar">
                    <h2 id="report-title">Seçili Rapor</h2>
                    <input type="text" class="search-box" id="table-search" placeholder="Tabloda anlık ara..." onkeyup="filterTable()">
                    <div class="export-group" style="display: flex; gap: 8px;">
                        <button class="btn-action btn-excel" onclick="exportToExcel()">📊 Excel (XLSX)</button>
                        <button class="btn-action btn-pdf" onclick="exportToPDF()">📕 PDF Rapor</button>
                    </div>
                </div>

                <div class="table-responsive">
                    <table id="report-table">
                        </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Tarayıcıdan SQL bağlantı bilgilerini toplar
        function getDbCredentials() {
            return {
                server: document.getElementById("db_server").value,
                port: document.getElementById("db_port").value,
                database: document.getElementById("db_name").value,
                user: document.getElementById("db_user").value,
                password: document.getElementById("db_password").value
            };
        }

        function toggleTheme() {
            const root = document.documentElement;
            const currentTheme = root.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', newTheme);
            document.getElementById('theme-toggle').innerText = newTheme === 'dark' ? '☀️ Açık Tema' : '🌙 Koyu Tema';
        }

        async function loadAllViews() {
            const credentials = getDbCredentials();
            try {
                const res = await fetch('/get_all_views', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(credentials)
                });
                const data = await res.json();
                
                if (data.error || !Array.isArray(data)) {
                    showError(data.error || "Beklenmeyen veri formatı.");
                    return;
                }

                const sel = document.getElementById("view");
                sel.innerHTML = "<option value=''>-- Lütfen Bir View Seçin --</option>";
                data.forEach(v => {
                    let opt = document.createElement("option");
                    opt.value = v;
                    opt.textContent = v;
                    sel.appendChild(opt);
                });
                clearError();
                alert("Veritabanı bağlantısı başarılı! View'ler listelendi.");
            } catch (err) {
                showError("Veritabanı API bağlantı hatası.");
            }
        }

        async function loadColumns() {
            const view = document.getElementById("view").value;
            if (!view) return;
            const credentials = getDbCredentials();
            try {
                const res = await fetch(`/get_columns?view=${encodeURIComponent(view)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(credentials)
                });
                const cols = await res.json();
                
                if (cols.error || !Array.isArray(cols)) {
                    showError(cols.error || "Sütunlar listelenirken hata oluştu.");
                    return;
                }

                const sel = document.getElementById("kolonlar");
                sel.innerHTML = "";
                cols.forEach(c => {
                    let opt = document.createElement("option");
                    opt.value = c;
                    opt.textContent = c;
                    sel.appendChild(opt);
                });
                clearError();
            } catch (err) {
                showError("Sütunlar yüklenemedi.");
            }
        }

        async function getReport() {
            const view = document.getElementById("view").value;
            const cols = Array.from(document.getElementById("kolonlar").selectedOptions).map(o => o.value);
            if (!view || cols.length === 0) return alert("Lütfen önce veri kaynağı (view) ve sütün seçimi gerçekleştirin.");
            
            const credentials = getDbCredentials();
            const payload = { ...credentials, view: view, columns: cols };

            try {
                const res = await fetch('/get_report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                if (data.error) {
                    showError(data.error);
                    document.getElementById("report-wrapper").style.display = "none";
                    document.getElementById("stats-grid").style.display = "none";
                    return;
                }

                document.getElementById("report-title").innerText = view;
                let tableHtml = "<thead><tr>";
                data.columns.forEach(c => tableHtml += `<th>${c}</th>`);
                tableHtml += "</tr></thead><tbody>";
                
                data.rows.forEach(row => {
                    tableHtml += "<tr>";
                    row.forEach(cell => tableHtml += `<td>${cell !== null ? cell : ''}</td>`);
                    tableHtml += "</tr>";
                });
                tableHtml += "</tbody>";
                
                document.getElementById("report-table").innerHTML = tableHtml;
                
                document.getElementById("stat-rows").innerText = data.rows.length;
                document.getElementById("stat-cols").innerText = data.columns.length;
                document.getElementById("stat-time").innerText = new Date().toLocaleTimeString();
                
                document.getElementById("report-wrapper").style.display = "block";
                document.getElementById("stats-grid").style.display = "grid";
                clearError();
            } catch (err) {
                showError("Rapor verisi getirilirken teknik hata oluştu.");
            }
        }

        function filterTable() {
            const input = document.getElementById("table-search");
            const filter = input.value.toUpperCase();
            const table = document.getElementById("report-table");
            const tr = table.getElementsByTagName("tr");

            for (let i = 1; i < tr.length; i++) {
                let rowText = tr[i].innerText.toUpperCase();
                if (rowText.indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }

        function exportToExcel() {
            const table = document.getElementById("report-table");
            let csv = [];
            csv.push("\\uFEFF");

            for (let i = 0; i < table.rows.length; i++) {
                if (table.rows[i].style.display === "none") continue;
                let row = [], cols = table.rows[i].querySelectorAll("td, th");
                for (let j = 0; j < cols.length; j++) {
                    let data = cols[j].innerText.replace(/"/g, '""');
                    row.push('"' + data + '"');
                }
                csv.push(row.join(";"));
            }
            
            const csvContent = csv.join("\\r\\n");
            const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            const viewName = document.getElementById("view").value || "rapor";
            
            link.href = URL.createObjectURL(blob);
            link.setAttribute("download", `${viewName}_${new Date().toLocaleDateString()}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function exportToPDF() {
            window.print();
        }

        function showError(message) {
            document.getElementById("error-box").innerHTML = `<div class="error"><strong>Bağlantı/Sistem Uyarısı:</strong> ${message}</div>`;
        }
        function clearError() {
            document.getElementById("error-box").innerHTML = "";
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_all_views', methods=['POST'])
def get_all_views():
    config = request.json
    conn = get_dynamic_connection(config)
    if not conn:
        return jsonify({"error": "Girilen bilgilere göre veritabanına bağlanılamadı. SQL Server servislerinizi, IP adresinizi, Kullanıcı adı/Şifrenizi ve SQL Server port izinlerinizi (1433) kontrol edin."})
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sys.views ORDER BY name")
        views = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(views)
    except Exception as e:
        return jsonify({"error": f"View listeleme hatası: {str(e)}"})

@app.route('/get_columns', methods=['POST'])
def get_columns():
    config = request.json
    view_name = request.args.get('view')
    conn = get_dynamic_connection(config)
    if not conn: 
        return jsonify({"error": "Veritabanı bağlantısı kurulamadı."})
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT TOP 0 * FROM [{view_name}]")
        columns = [col[0] for col in cur.description]
        cur.close()
        conn.close()
        return jsonify(columns)
    except Exception as e:
        return jsonify({"error": f"Sütun bilgileri okunamadı: {str(e)}"})

@app.route('/get_report', methods=['POST'])
def get_report():
    config = request.json
    view_name = config.get('view')
    columns = config.get('columns', [])
    conn = get_dynamic_connection(config)
    if not conn:
        return jsonify({"error": "Sorgu için veritabanına bağlanılamadı."})
    try:
        cur = conn.cursor()
        safe_cols = ", ".join([f"[{c}]" for c in columns])
        cur.execute(f"SELECT TOP 500 {safe_cols} FROM [{view_name}]")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"columns": columns, "rows": rows})
    except Exception as e:
        return jsonify({"error": f"Veri çekilirken SQL hatası oluştu: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)