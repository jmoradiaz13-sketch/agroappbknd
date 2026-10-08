# Tabla de rangos iniciales — validar con técnico antes de producción

Fuente: `src/*.pdf`. Regla: ningún valor sin `fuente`.

| Parámetro | Unidad | Deficiente < | Óptimo | Exceso > | Fuente |
|---|---|---|---|---|---|
| materia_organica_pct | % | 2.0 | 2.0–5.0 | 5.0 | guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12-18 |
| fosforo_mg_kg | mg/kg | 15 | 15–40 | 40 | guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos.pdf cap. fertilidad |
| potasio_cmol_kg | cmol/kg | 0.2 | 0.2–0.6 | 0.6 | guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.20-25 |
| calcio_cmol_kg | cmol/kg | 3.0 | 3.0–10.0 | 10.0 | guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos.pdf cap. acidez |
| magnesio_cmol_kg | cmol/kg | 0.8 | 0.8–3.0 | 3.0 | guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.20-25 |
| conductividad_ds_m | dS/m | — | 0–2.0 | 2.0 | guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf cap. salinidad |
| nitrogeno_pct | % | 0.1 | 0.1–0.3 | 0.3 | manual_de_agroecologia_y_agroforesteria._practicas_para_una_agricultura_ecologica.pdf cap. fertilidad |

Decisión diseño: motor puro en `aplicacion/servicios/motor_diagnostico.py`,
sin ML. El técnico acepta/rechaza/edita (ver `TarjetaDiagnostico.tsx`).
Estrategias también inmutables (`modelos/estrategia.py`).
