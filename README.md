# Simulador de Tanque con Descarga Gravitatoria

---

## ¿Qué hace este simulador?

Simula el nivel de líquido en un tanque con **descarga gravitatoria**. Permite analizar cómo responde el sistema ante cambios en:

- Apertura de la válvula de salida
- Caudal de entrada
- Característica de la válvula (lineal, isoporcentual, rápida)

> **Documentación técnica**: [modelo_conceptual.pdf](assets/docs/modelo_conceptual.pdf)

---

## Modelo de espacio de estados

Se utilizó la plantilla de resolución de la cátedra de Simulación y Optimización de la carrera de Ingeniería Química de la Universidad Nacional de Jujuy.

La estrategia de implementación fue la siguiente:

- Implementar en Octave el modelo de espacio de estados
- Pasar al lenguaje Python la aplicación
- Desplegar la aplicación en Streamlit a través de GitHub
- Usar IDEs: Geany y VSCodium, según conveniencia, con IA generativa para detectar errores de código, para identación automática y sugerencias para mejorar experiencia frontend

---

## Tecnologías Utilizadas

- **SO**: AntiX Linux
- **IDE**: Geany / Geany Copilot - VSCodium / API DeepSeek

| Tecnología | Propósito |
|------------|-----------|
| Octave | Modelado inicial y validación |
| Python 3.8+ | Lenguaje necesario para desplegar en Streamlit |
| Streamlit | Interfaz web interactiva |
| Plotly | Gráficas interactivas |
| SciPy | Resolución de ecuaciones diferenciales |
| NumPy | Operaciones numéricas |

---

## Cómo usar el simulador

### Opción 1: En línea (recomendado)

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://simulacion-tanque.streamlit.app)

### Opción 2: Localmente

Clonar el repositorio:

    git clone https://github.com/ffedezn-cloud/simulacion-tanque.git
    cd simulacion-tanque

Instalar dependencias:

    pip install -r requirements.txt

Ejecutar la aplicación:

    streamlit run app.py

---

## Bibliografía

- Tarifa, E. (2025). Apuntes Simulación y Optimización de Procesos. UNJu - FI.
- Ingham, J. (1994). Chemical Engineering Dynamics. Editorial VCH.
- Documentación de Streamlit: https://docs.streamlit.io
- Documentación de SciPy: https://docs.scipy.org

---

## Créditos

| Rol | Nombre |
|-----|--------|
| **Autor** | Federico Franco |
| **Carrera** | Ingeniería Química |
| **Año** | 2026 |

---

## Licencia

Distribuido bajo licencia **MIT**. Ver el archivo LICENSE para más información.

---

## Contacto

**Federico Franco**  
ffede.zn@gmail.com  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/fede-franco-70a301418/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/ffedezn-cloud)

---

**¿Te resultó interesante este proyecto? Dame una estrella en GitHub.**

---

