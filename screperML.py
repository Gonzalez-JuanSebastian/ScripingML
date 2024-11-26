import pandas as pd
import os
import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

def scrape_product_details(driver):
    # Añadir un tiempo de espera antes de empezar a extraer los datos
    print("Esperando 2 segundos antes de comenzar la extracción de datos...")
    time.sleep(2)

    # Extraer el Código SKU y mantener solo los números
    try:
        codigo = driver.find_element(By.CSS_SELECTOR, ".sc-title-subtitle-action__sublabel").text
        codigo = re.sub(r'\D', '', codigo)  # Eliminar caracteres no numéricos
        print(codigo)
    except Exception as e:
        print(f"No se pudo extraer el SKU: {str(e)}")
        codigo = ""

    # Unidades 
    try:
        unidades = driver.find_element(By.CLASS_NAME, "sc-quantity").text
        print(unidades)
    except Exception as e:
        print(f"No se pudo extraer las unidades: {str(e)}")
        unidades = ""

    # Extraer el nombre
    try:
        nombre = driver.find_element(By.CLASS_NAME, "sc-detail-title__text").text
        print(nombre)
    except Exception as e:
        print(f"No se pudo extraer el nombre: {str(e)}")
        nombre = ""

    # Extraer los datos
    try:
        datos_element = driver.find_element(By.CLASS_NAME, "sc-text")
        datos_text = datos_element.text
        datos = datos_text
        print(f"Datos extraídos: {datos}")
    except Exception as e:
        print(f"No se pudo extraer los datos: {str(e)}")
        datos = ""

    # Cobro 
    try:
        cobro_element = driver.find_element(By.CSS_SELECTOR, ".sc-account-title__subtext span")
        cobro = cobro_element.text
        print(cobro)
    except Exception as e:
        cobro = "0"
        
    # FEM 
    try:
        fem_element = driver.find_element(By.CSS_SELECTOR, ".sc-notes__content-text")
        fem = fem_element.text
        print(fem)
    except Exception as e:
        fem = ""

    # Total 
    try:
        total = driver.find_element(By.CLASS_NAME, "sc-account-rows__row__price").text
        total = re.sub(r'[^\d,.]', '', total)  # Eliminar caracteres no numéricos excepto ',' y '.'
        total = total.replace(',', '')  # Eliminar las comas para dejar solo el número
        print(total)
    except Exception as e:
        print(f"No se pudo extraer el total: {str(e)}")
        total = "0"

    # Buscar el texto "Precio del producto" y extraer el siguiente <span>
    precio_del_producto = ""
    try:
        elements = driver.find_elements(By.CLASS_NAME, "sc-account-module")
        precio_del_producto = None  # Inicializar la variable antes del bucle

        for element in elements:
            if "Precio del producto" in element.text or "Precio de los productos" in element.text:
                # Buscar todos los elementos <span> dentro del elemento actual
                span_elements = element.find_elements(By.TAG_NAME, "span")
                for span in span_elements:
                    # Verificar si el texto dentro del span contiene un precio
                    if "$" in span.text:
                        precio_del_producto = span.text.strip()
                        precio_del_producto = re.sub(r'[^\d,.]', '', precio_del_producto)  # Eliminar caracteres no numéricos excepto ',' y '.'
                        precio_del_producto = precio_del_producto.replace(',', '')  # Eliminar las comas para dejar solo el número
                        break
            if precio_del_producto:
                break

        if precio_del_producto:
            print(f"Precio encontrado: {precio_del_producto}")
        else:
            print("No se encontró el precio del producto.")

    except Exception as e:
        print(f"No se pudo encontrar el precio del producto: {str(e)}")

    # Buscar el texto "Cargos por venta" y extraer el siguiente <span>
    cargos_por_ventas = ""
    try:
        elements = driver.find_elements(By.CLASS_NAME, "sc-account-module")
        for element in elements:
            if "Cargos por venta" in element.text:
                # Buscar todos los elementos <span> dentro del elemento actual
                span_elements = element.find_elements(By.TAG_NAME, "span")
                for span in span_elements:
                    # Verificar si el texto dentro del span contiene un precio
                    if "-$" in span.text:
                        cargos_por_ventas = span.text.strip()
                        cargos_por_ventas = re.sub(r'[^\d,.]', '', cargos_por_ventas)  # Eliminar caracteres no numéricos excepto ',' y '.'
                        cargos_por_ventas = cargos_por_ventas.replace(',', '')  # Eliminar las comas para dejar solo el número
                        break
                if cargos_por_ventas:
                    break
    except Exception as e:
        print(f"No se pudo encontrar los cargos por venta: {str(e)}")

    # Buscar el texto "Envíos" y extraer el siguiente <span>
    envios = ""
    try:
        elements = driver.find_elements(By.CLASS_NAME, "sc-account-rows__row")
        for element in elements:
            title_element = element.find_element(By.CLASS_NAME, "sc-account-rows__row__title")
            if "Envíos" in title_element.text:
                subtotal_element = element.find_element(By.CLASS_NAME, "sc-account-rows__row__subTotal")
                envios = subtotal_element.text.strip()
                envios = re.sub(r'[^\d,.]', '', envios)  # Eliminar caracteres no numéricos excepto ',' y '.'
                envios = envios.replace(',', '')  # Eliminar las comas para dejar solo el número
                break
    except Exception as e:
        print(f"No se pudo encontrar los envíos: {str(e)}")

    print(f"Envíos encontrados: {envios}")

    # Buscar el texto "Impuestos" y extraer el siguiente <span>
    impuestos = ""
    try:
        elements = driver.find_elements(By.CLASS_NAME, "sc-account-rows__row")
        for element in elements:
            title_element = element.find_element(By.CLASS_NAME, "sc-account-rows__row__title")
            if "Impuestos" in title_element.text:
                subtotal_element = element.find_element(By.CLASS_NAME, "sc-account-rows__row__subTotal")
                impuestos = subtotal_element.text.strip()
                impuestos = re.sub(r'[^\d,.]', '', impuestos)  # Eliminar caracteres no numéricos excepto ',' y '.'
                impuestos = impuestos.replace(',', '')  # Eliminar las comas para dejar solo el número
                break
    except Exception as e:
        print(f"No se pudo encontrar los impuestos: {str(e)}")

    print(f"Impuestos encontrados: {impuestos}")

    # Crear un DataFrame donde cada lista es una columna
    data = pd.DataFrame({
        'FEM': [fem],
        'Codigo': [codigo],
        'Nombre': [nombre],
        'Unidades': [unidades],
        'Datos': [datos],
        'NumCobro': [cobro],
        'Precio del Producto': [precio_del_producto],
        'Total': [total],
        'Cargos por Venta': [cargos_por_ventas],
        'Envios': [envios],
        'Impuestos': [impuestos],
    })

    # Especificar el directorio y la ruta del archivo
    directory = "...data"
    file_path = os.path.join(directory, "producto_data.csv")

    # Crear el directorio si no existe
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Comprobar si el archivo ya existe
    if os.path.exists(file_path):
        # Añadir al archivo existente
        data.to_csv(file_path, mode='a', index=False, encoding='utf-8-sig', header=False, sep=';')
    else:
        # Crear un nuevo archivo
        data.to_csv(file_path, index=False, encoding='utf-8-sig', sep=';')

    print(f"Datos guardados en {file_path}")

    # Mostrar las primeras filas
    print(data.head())
