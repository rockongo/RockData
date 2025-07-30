<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RockData - Resultado</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
        }
        .rockdata-logo {
            width: 200px;
            margin-bottom: 10px;
        }
        .titulo-principal {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
        }
        .leyenda {
            font-style: italic;
            color: #777;
            margin-bottom: 1rem;
        }
        .caja-pronostico {
            background-color: #e3fcef;
            border-left: 5px solid #28a745;
            padding: 1rem;
            margin-top: 1rem;
            font-weight: 500;
            color: #155724;
        }
        .caja-seccion {
            background-color: #fff;
            border: 1px solid #dee2e6;
            border-radius: .5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .caja-seccion h5 {
            color: #0056b3;
            font-size: 1.1rem;
        }
        .sugerencias {
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 1rem;
            font-weight: 500;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container py-4">
        <div class="text-center">
            <img src="/static/logo_rockdata.png" alt="RockData" class="rockdata-logo">
            <div class="leyenda">No adivinamos. Calculamos.</div>
            <div class="titulo-principal" id="partido">O'Higgins vs Colo Colo</div>
            <div class="text-muted" id="liga">Primera A de Chile, Jornada X</div>
        </div>

        <div class="caja-seccion">
            <h5>⏱️ Gol en el Primer Tiempo</h5>
            <div id="gol_1t_prob">Probabilidad: 33.4%</div>
            <div id="gol_1t_texto">NO se recomienda apostar a 1 gol en el primer tiempo.</div>
        </div>

        <div class="caja-seccion">
            <h5>🤝 Ambos Equipos Marcan</h5>
            <div id="ambos_marcan_prob">Probabilidad: 56.8%</div>
            <div id="ambos_marcan_texto">Recomendamos APOSTAR a que ambos anotan.</div>
            <div class="text-muted" id="ambos_marcan_justificacion">O'Higgins marca 1.2, Colo Colo 1.9 goles por partido.</div>
        </div>

        <div class="caja-seccion">
            <h5>⚽ Goles Totales</h5>
            <div>+1.5 goles: <span id="goles_15">64.2%</span></div>
            <div>+2.5 goles: <span id="goles_25">57.6%</span></div>
            <div class="mt-1 fw-bold text-success" id="goles_sugerencia">Recomendación: Apostar por +1.5 goles</div>
            <div class="text-muted">📌 Este escenario tiene la mayor probabilidad de concretarse.</div>
        </div>

        <div class="caja-seccion">
            <h5>🚩 Córners</h5>
            <div>+7.5: <span id="corners_75">89.5%</span></div>
            <div>+8.5: <span id="corners_85">78.2%</span></div>
            <div>+9.5: <span id="corners_95">66.9%</span></div>
            <div class="mt-1 fw-bold text-success" id="corners_sugerencia">Sugerencia: +7.5 córners</div>
            <div class="text-muted" id="corners_justificacion">O'Higgins genera 4.6 y Colo Colo 5.1. Total esperado: 9.7</div>
        </div>

        <div class="caja-seccion">
            <h5>🟨 Tarjetas</h5>
            <div>+3.5: <span id="tarjetas_35">82.4%</span></div>
            <div>+4.5: <span id="tarjetas_45">65.3%</span></div>
            <div class="mt-1 fw-bold text-success" id="tarjetas_sugerencia">Sugerencia: Más de 3.5 tarjetas</div>
            <div class="text-muted" id="tarjetas_justificacion">O'Higgins suma 2.0, Colo Colo 2.3 tarjetas por partido</div>
        </div>

        <div class="caja-pronostico">
            Pronóstico Final: <span id="resultado_final">Colo Colo</span><br>
            <small class="text-muted" id="resultado_justificacion">Colo Colo tiene 46.6% de probabilidad de ganar. O'Higgins solo 27.6%</small>
        </div>

        <div class="sugerencias mt-4">
            <strong>💡 Sugerencias de Apuesta:</strong>
            <ul class="mb-0">
                <li id="sugerencia1">Ambos anotan o Más de 1.5 goles</li>
                <li id="sugerencia2">Más de 4.5 tarjetas</li>
            </ul>
            <div class="text-muted mt-1"><small>Estas sugerencias se basan en estadísticas reales. Usa los datos para tomar tus propias decisiones.</small></div>
        </div>

        <div class="text-center mt-4">
            <a href="/" class="btn btn-primary">🔙 Volver a seleccionar equipos</a>
        </div>
    </div>
</body>
</html>

