

# Código de replicación para "Large Language Models Reflect Human Citation Patterns with a Heightened Citation Bias"
https://arxiv.org/abs/2405.15739

## Ejecución de los scripts y creación de las figuras
Para ejecutar los scripts, primero ejecute:

```text
poetry install
```

luego:

```text
poetry run python src/00_download_data.py
```

o abra el entorno virtual con:

```text
poetry shell
```

Las figuras y los resultados pueden replicarse en los notebooks correspondientes que se encuentran en src/figures. 

Los datos necesarios para ejecutar los notebooks se pueden encontrar en la carpeta results.  

Los datos sin procesar creados en los scripts de Python de la carpeta src están disponibles en: https://zenodo.org/records/11299894. Estos datos contienen una nueva carpeta de datos y archivos complementarios a la carpeta results.

## Datos
Describimos los pasos de nuestra canalización automatizada para obtener toda la información necesaria para nuestro análisis. Nuestra recolección de datos resultó en $166$ artículos publicados en AAAI ($25$), NeurIPS ($72$), ICML ($38$) e ICLR ($31$), para un total de 3.066 referencias (vea la Tabla del Apéndice \ref{tab:paper_details} para una lista completa de los artículos incluidos). La canalización de recolección de datos utiliza GPT-4 para postprocesar partes de los datos, lo cual cuesta aproximadamente 14 dólares para nuestro experimento. Tenga en cuenta que estos pasos solo deben realizarse una vez para la recolección de datos. Sin embargo, los pasos 4 y 5 también se utilizan para postprocesar y enriquecer la información de las referencias generadas y deberán realizarse en cada ejecución. El experimento se ejecutó el 4 de noviembre de 2023 y cada paso fue verificado y probado manualmente.

### Paso 1. ArXiv (src/00_download_data.py y src/utils/arxiv.py)
Buscamos todos los artículos en arXiv publicados originalmente entre el 1 de marzo de 2022 y el 31 de octubre de 2023 en la categoría de aprendizaje automático (cs.LG) que hacen referencia a AAAI, NeurIPS, ICLR o ICML en su referencia de revista. Tenga en cuenta que también verificamos si podemos utilizar todos estos artículos de arXiv dados sus licencias de datos y atribuimos su participación en la Tabla del Apéndice \ref{tab:paper_details}. Utilizamos palabras clave (es decir, workshop, tiny paper, 2020, 2021, track on datasets and benchmarks, y bridge) para eliminar artículos que no aparecen en los procedimientios de la conferencia o anteriores a 2022. Descargamos y descomprimimos el archivo *tar.gz* proporcionado por los autores a arXiv y verificamos si el artículo existe en Semantic Scholar mediante coincidencia de títulos. Almacenamos el título, ID y fecha de arXiv y Semantic Scholar. Además, almacenamos todos los títulos de las referencias con su ID correspondiente de Semantic Scholar.

### Paso 2. Tex (src/00_download_data.py y src/utils/tex.py)
Verificamos si existe un archivo *tex* principal en la carpeta descomprimida del artículo buscando un único archivo que contenga `\begin{document}` y `\end{document}`. Si encontramos un archivo *tex* principal, iniciamos el proceso de limpieza; de lo contrario, excluimos el artículo de nuestro análisis. El proceso de limpieza consta de tres pasos. Primero, eliminamos todo excepto la información de los autores, la información de la conferencia, el resumen, la introducción y las referencias. Segundo, eliminamos figuras, tablas, referencias a secciones y apéndices, etc. Finalmente, transformamos todas las citas en números entre corchetes. Después de la limpieza, verificamos si hay disponible un archivo *bib* o *bbl* y compilamos el *tex* a *PDF*. Si ninguno de los archivos está disponible o el artículo tiene errores de compilación, lo excluimos de nuestro análisis (Tabla del Apéndice \ref{tab:sup_1}). Tenga en cuenta que un archivo *bib* permite tanto la compilación de *PDFLatex* como de *bibtex*, mientras que solo un archivo *bbl* no permite la compilación de *bibtex*. Como consecuencia, los artículos con solo un archivo *bbl* pueden contener potencialmente artículos en su lista de referencias que no están citados en la introducción del artículo. Resolvemos este problema en el siguiente paso.

### Paso 3. PDF (src/00_download_data.py y src/utils/pdf.py)
Transformamos el *PDF* a *txt* y separamos el contenido principal del artículo (información de los autores, información de la conferencia, resumen e introducción) de las referencias. Luego, buscamos todas las citas en el texto utilizando un patrón regex para capturar números entre corchetes y emparejarlos con la lista de referencias. Este enfoque garantiza que solo mantengamos las referencias que se citan en la introducción. Almacenamos el contenido principal del artículo y las referencias citadas en la introducción en archivos *txt* separados.

### Paso 4. Postprocesamiento Postprocesamiento (src/01_postprocess_data.py)
Una gran cantidad de variaciones e inconsistencias en las listas de referencias dificulta extraer y analizar estructuradamente toda la información de los autores, el título, el lugar de publicación y el año. Notamos que este comportamiento era aún más pronunciado en las referencias generadas por LLM. Por lo tanto, examinamos las capacidades de GPT-4 para imponer una estructura a la lista de referencias mediante el postprocesamiento de los datos. Alimentamos a GPT-4 con la lista de referencias en *txt*, acompañada por el mensaje de sistema predeterminado: "*You are a helpful assistant*" y la siguiente instrucción de postprocesamiento:

\vspace{0.1cm}
\begin{tcolorbox}[mypromptbox]
\begin{center}
    A continuación, compartimos con usted una lista de referencias con su número de cita correspondiente entre corchetes. ¿Podría extraer para cada referencia los autores, el número de autores, el título, el año de publicación y el lugar de publicación? Por favor, devuelva únicamente la información extraída en una tabla markdown con el número de cita (sin corchetes), autores, número de autores, título, año de publicación y lugar de publicación como columnas. \\
    === \\
     **[lista de referencias generada por GPT-4]**
\end{center}
\end{tcolorbox}
\vspace{0.1cm}

Luego, almacenamos la tabla markdown en un archivo *csv*. GPT-4 estructura la información con éxito y la hace más consistente, por ejemplo, eliminando los guiones silábicos. A veces se introduce un pequeño error (por ejemplo, añadiendo una fila final con "…"), pero estos se resuelven manualmente durante el proceso de verificación. Tenga en cuenta que también solicitamos el número de autores. Aunque podemos calcular fácilmente el número de autores a través de los metadatos de Semantic Scholar, esto nos permite verificar la precisión de GPT-4 en esta tarea, ya que lo utilizaremos más adelante para postprocesar las referencias generadas donde el valor de referencia (ground truth) podría no estar disponible.

### Paso 5. Semantic Scholar src/02_semantic_data.py)
Enriquecemos la información de las referencias de la introducción haciendo coincidir el título extraído del archivo *csv* en el paso anterior con los títulos de referencia que extraímos de Semantic Scholar en el paso 1. Este enfoque proporciona una verificación adicional de que GPT-4 no cambia la información del título en el paso 4. Tras la coincidencia, podemos utilizar el ID de Semantic Scholar para recuperar el lugar de publicación, el año, los autores, el recuento de citas, el recuento de citas influyentes y el recuento de referencias. Además, almacenamos los IDs de los artículos a los que se refieren las propias referencias de la introducción.

### Paso 6. Prompts "Vanilla" (src/03_call_LLM.py y src/04_postprocess_LLM.py)
Enviamos a GPT-4 el contenido principal, que incluye la información de los autores, la información de la conferencia, el resumen y la introducción, acompañados por el mensaje de sistema predeterminado: "*You are a helpful assistant*" y el siguiente prompt:
\vspace{0.1cm}
\begin{tcolorbox}[mypromptbox]
\begin{center}
    A continuación, compartimos con usted una introducción escrita de un artículo y hemos omitido las referencias. Los números entre corchetes indican citas. ¿Podría sugerirnos una referencia explícita asociada a cada número? No devuelva nada excepto el número de cita entre corchetes y la referencia correspondiente. \\
    === \\
     **[contenido principal]**
\end{center}
\end{tcolorbox}
\vspace{0.1cm}
Luego, postprocesamos la respuesta de GPT-4 para extraer el título, el lugar de publicación, el año de publicación, los nombres de los autores y el número de autores de cada referencia generada, utilizando el mismo enfoque que se describe en el paso 4. Repetimos este enfoque "vanilla" cinco veces para los $166$ artículos.

### Paso 7. Verificación de existencia (src/05_semantic_LLM.py)
Determinamos si las referencias generadas existen mediante la coincidencia de títulos y nombres de autores con las entradas de Semantic Scholar. Para los títulos, medimos la similitud entre la coincidencia de Semantic Scholar y la referencia generada comparando la mejor subcadena coincidente. Para los autores, los comparamos dividiéndolos en tokens (palabras), eliminando duplicados y luego calculando la similitud basándonos en la mejor coincidencia parcial de los conjuntos de tokens. En caso de "et al.", solo consideramos al primer autor. La similitud se calcula mediante comparación a nivel de carácter. Determinamos los umbrales para las puntuaciones de títulos y autores etiquetando manualmente $100$ coincidencias como verdaderas o falsas y maximizando la puntuación $F_1$.

### Paso 8. Prompts "Iterativos" (src/06_iterate_LLM.py, src/07_postprocess_LLM.py) y src/08_semantic_LLM.py)
También nos basamos en nuestro enfoque "vanilla", introduciendo un enfoque "iterativo" donde enviamos a GPT-4 el contenido principal acompañado por el mensaje de sistema predeterminado: "*You are a helpful assistant*" y el siguiente prompt:
\vspace{0.1cm}
\begin{tcolorbox}[mypromptbox]
\begin{center}
    **[prompt vanilla + respuesta de GPT-4]** \\
    Las siguientes referencias asociadas a estos números de cita: \\ **[números de referencias generadas que no existen]** \\ no existen. ¿Podría reemplazar todas estas referencias inexistentes con existentes? Mantenga las demás referencias como están. No devuelva nada excepto el número de cita entre corchetes y la referencia correspondiente. \\
    === \\
     **[contenido principal]**
\end{center}
\end{tcolorbox}
\vspace{0.1cm}
Nuevamente, postprocesamos la respuesta de GPT-4 utilizando el mismo enfoque que se describe en los pasos 4, 5 y 7. Luego, se fusionan las referencias generadas existentes previamente con las referencias generadas recientemente.
