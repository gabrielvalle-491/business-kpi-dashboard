# Business KPI Dashboard

English: [README.md](README.md)

![CI](https://github.com/gabrielvalle-491/business-kpi-dashboard/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Tablero de KPIs de ventas, clientes y operaciones.

**▶ Demo en vivo:** https://gabrielvalle-491.github.io/business-kpi-dashboard/

![Captura del tablero](docs/screenshot.jpg)

## El problema de negocio

El dueño de una empresa de distribución en crecimiento recibe los números desde tres
fuentes —las exportaciones de pedidos, la lista de clientes y la bandeja de soporte— y
dedica todos los lunes a armar a mano la misma planilla. Nadie advierte a tiempo que las
entregas se están atrasando ni qué región está impulsando el crecimiento.

## Qué muestra

| Área | KPIs |
|------|------|
| **Ventas** | Ingresos, pedidos, ticket promedio, margen bruto %, crecimiento mensual, ingresos por categoría / región / canal, productos principales |
| **Clientes** | Clientes activos, tasa de clientes recurrentes |
| **Operaciones** | % de entregas a tiempo frente a un objetivo del 90%, tasa de devoluciones |
| **Soporte** | Tickets por tema, tiempo promedio de resolución, CSAT (% de calificaciones de 4-5 estrellas) |

Dos formas de usarlo:

1. **Aplicación interactiva** (Streamlit) con filtros por rango de fechas, región y canal.
2. **Informe HTML estático** (`docs/index.html`) que se genera con un solo comando y se publica
   con GitHub Pages; es fácil de enviar por correo o compartir con alguien que no usa Python.

Las reglas de negocio son explícitas y están cubiertas por pruebas: los ingresos solo cuentan
pedidos *entregados* (se excluyen devoluciones y cancelaciones), y "a tiempo" significa entregado
dentro de los días prometidos.

## Inicio rápido

```bash
pip install -r requirements.txt

python -m dashboard.generate_data data          # 12 months of demo data
streamlit run app.py                            # interactive dashboard
python -m dashboard.build_static data docs/index.html   # shareable HTML report
```

Reemplace los archivos CSV de `data/` por exportaciones reales (con las mismas columnas) y el
tablero funciona con datos reales.

Las mismas tareas también están disponibles desde un único punto de entrada por línea de comandos:

```bash
python -m dashboard --help
python -m dashboard generate data                  # same as dashboard.generate_data
python -m dashboard build data docs/index.html     # same as dashboard.build_static
python -m dashboard summary data                   # print the headline KPIs
```

El comando termina con código `0` si todo sale bien y con `1` (y un mensaje `error:`) cuando
falta un archivo CSV o una columna obligatoria.

## Conjunto de datos de demostración (sintético)

`generate_data.py` simula una pequeña empresa realista: ~5,500 pedidos en 12 meses
con crecimiento, estacionalidad y caídas los fines de semana, una base de clientes de cola larga
(unos pocos compradores fieles y muchos que compran una sola vez), 5 regiones, 3 canales,
devoluciones/cancelaciones, demoras en las entregas y 1,500 tickets de soporte.

| KPI (año completo) | Valor |
|---|---:|
| Ingresos | $1,982,710 |
| Pedidos | 5,502 |
| Ticket promedio | $360.36 |
| Margen bruto | 37.5% |
| Clientes recurrentes | 41.2% |
| Entregas a tiempo | 86.2% |
| CSAT | 73.7% |

## Estructura del proyecto

```
app.py                    # Streamlit app
dashboard/
├── kpis.py               # all KPI logic (pure pandas, unit tested)
├── charts.py             # Plotly figures shared by app + static report
├── build_static.py       # HTML report for GitHub Pages
└── generate_data.py      # realistic demo data
data/                     # orders.csv, customers.csv, tickets.csv
docs/                     # published static dashboard
tests/
```

## Pruebas

```bash
pytest -q
```

## Cómo se lo entregaría a un cliente

Si me contrata para este trabajo, yo:

- **Le pediría tres exportaciones** (CSV, u hojas de Excel que convierto a CSV), con estas columnas:
  - `orders.csv`: `order_id`, `order_date`, `customer_id`, `region`, `channel`, `category`, `product`,
    `revenue`, `cost`, `status` (`Delivered` / `Returned` / `Cancelled`), `promised_days`, `delivery_days`
  - `tickets.csv`: `ticket_id`, `opened_at`, `topic`, `resolution_hours`, `csat` (1-5)
  - `customers.csv`: `customer_id`, `signup_date` (más cualquier otro campo que ya tenga)
- **Mapearía una sola vez sus nombres de columnas y valores de estado** a los indicados arriba, para
  que su equipo siga exportando exactamente como lo hace hoy.
- **Acordaría con usted por escrito las reglas de negocio** antes del primer informe (qué cuenta como
  ingreso, qué significa "a tiempo", el objetivo de entregas) y las mantendría cubiertas por las pruebas
  unitarias de `tests/`.
- **Lo actualizaría semanalmente**: se colocan las nuevas exportaciones en `data/`, se ejecuta
  `python -m dashboard build data docs/index.html` y se comparte el informe HTML actualizado (o el enlace
  a la aplicación Streamlit), con una lista de pasos breve para que cualquier persona de su equipo pueda hacerlo.
- **Informaría los problemas con claridad en lugar de mostrar números incorrectos**: `python -m dashboard`
  se detiene con código de salida `1` y un mensaje `error:` cuando falta un archivo o una columna
  obligatoria, y el flujo de CI ejecuta las pruebas con cada cambio.
- **Le entregaría todo**: el código fuente, una guía breve en español o en inglés y una llamada de
  presentación.

## Notas

- Todos los datos son sintéticos. No se usan datos reales de ninguna empresa.
- Desarrollado con Python (pandas, Plotly, Streamlit) y [Claude Code](https://claude.com/claude-code) como programador asistente de IA.

## Autor

**Gabriel Valle** — Automatización de datos e IA (Excel, PDF, flujos de trabajo) · Villa Mercedes, Argentina · Remoto
