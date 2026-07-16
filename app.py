# app.py (Vercel için yeni kod)
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Müşterilerden gelecek verileri burada geçici olarak tutacağız
gelen_raporlar = {}

HTML_SABLON = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Gastro Analiz Paneli</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
        .container { max-width: 1200px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 16px; border: 1px solid #334155; }
        h1 { color: #38bdf8; margin-bottom: 20px; }
        .table-responsive { margin-top: 20px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 12px 15px; border-bottom: 1px solid #334155; }
        th { background: #0f172a; color: #94a3b8; font-size: 12px; text-transform: uppercase; }
        .no-data { text-align: center; padding: 40px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Gastro Canlı Satış Analiz Paneli</h1>
        <p>Müşteri bilgisayarlarından anlık gelen rapor verileri.</p>
        
        <div class="table-responsive">
            {% if veriler %}
                <table>
                    <thead>
                        <tr>
                            {% for col in kolonlar %}
                                <th>{{ col }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in veriler %}
                            <tr>
                                {% for cell in row %}
                                    <td>{{ cell }}</td>
                                {% endfor %}
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="no-data">🔌 Şu an bağlı bir istemci veya gelen veri yok.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>"""

@app.route('/')
def index():
    # Burası gelen verileri ekrana basacak
    kolonlar = gelen_raporlar.get('columns', [])
    satirlar = gelen_raporlar.get('rows', [])
    return render_template_string(HTML_SABLON, kolonlar=kolonlar, veriler=satirlar)

@app.route('/veri-gonder', methods=['POST'])
def veri_gonder():
    global gelen_raporlar
    veri = request.json
    
    # Gelen veriyi hafızaya kaydet
    gelen_raporlar = {
        "columns": veri.get('columns', []),
        "rows": veri.get('rows', [])
    }
    return jsonify({"status": "success", "message": "Veri başarıyla alındı!"})
