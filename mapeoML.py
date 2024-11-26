import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    TimeoutException,
    StaleElementReferenceException
)   
import time
import re
import screperML

def start_chrome_debugging():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_debug"

    if not os.path.exists(chrome_path):
        raise FileNotFoundError(f"Chrome no se encontró en la ruta: {chrome_path}")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    chrome_debug_command = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}"
    ]
    subprocess.Popen(chrome_debug_command)

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?: [A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
        r'localhost|' 
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' 
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def procesar_pagina(driver, fechas_especificas, processed_urls):
    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-list.sc-list-marketplace"))
    )

    container = driver.find_element(By.CSS_SELECTOR, ".sc-list.sc-list-marketplace")
    tarjetas = container.find_elements(By.CSS_SELECTOR, ".andes-card.sc-row.sc-row-marketplace.false.andes-card--flat.andes-card--padding-0")

    if not tarjetas:
        print("No se encontraron tarjetas en la página.")
        return False

    tarjeta_numerada = {}
    tarjeta_num = 1

    for tarjeta in tarjetas:
        try:
            fecha_texto = tarjeta.find_element(By.CLASS_NAME, "left-column__order-date").text.strip().lower()
            tarjeta_numerada[tarjeta_num] = tarjeta
            tarjeta_num += 1
            print(f"Fecha de la tarjeta {tarjeta_num - 1}: {fecha_texto}")

        except NoSuchElementException as e:
            print(f"No se pudo encontrar el elemento necesario en la tarjeta: {str(e)}")

    for num in range(1, tarjeta_num):
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            try:
                if num - 1 < len(tarjetas):
                    tarjeta = tarjeta_numerada[num]
                    fecha_texto = tarjeta.find_element(By.CLASS_NAME, "left-column__order-date").text.strip().lower()

                    if any(fecha in fecha_texto for fecha in fechas_especificas):
                        boton = tarjeta.find_element(By.CSS_SELECTOR, ".primary-action a")
                        url_detalle = boton.get_attribute("href")

                        if url_detalle in processed_urls:
                            print(f"URL ya procesada: {url_detalle}")
                            break

                        processed_urls.add(url_detalle)
                        print(f"Accediendo al detalle de la tarjeta {num}: {url_detalle}")

                        driver.get(url_detalle)
                        screperML.scrape_product_details(driver)

                        driver.back()
                        WebDriverWait(driver, 50).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-list.sc-list-marketplace"))
                        )
                        print(f"Regresado a la lista de tarjetas después de procesar la tarjeta {num}.")
                    else:
                        print(f"Fecha {fecha_texto} no está en el rango. No se procesará esta tarjeta.")
                    break
                else:
                    print(f"Índice {num - 1} fuera de rango. Intento {attempts + 1}")
                    break

            except StaleElementReferenceException:
                attempts += 1
                print(f"Elemento obsoleto en la tarjeta {num}. Intentando recuperar... Intento {attempts}")

                container = driver.find_element(By.CSS_SELECTOR, ".sc-list.sc-list-marketplace")
                tarjetas = container.find_elements(By.CSS_SELECTOR, ".andes-card.sc-row.sc-row-marketplace.false.andes-card--flat.andes-card--padding-0")
                tarjeta_numerada[num] = tarjetas[num - 1] if num - 1 < len(tarjetas) else None

            except NoSuchElementException as e:
                print(f"No se pudo encontrar el elemento necesario en la tarjeta {num}: {str(e)}")
                break
            except NoSuchWindowException as e:
                print(f"La ventana del navegador ya estaba cerrada: {str(e)}")
                return
            except Exception as e:
                print(f"Ocurrió un error inesperado en la tarjeta {num}: {str(e)}")
                break

    return True

def click_siguiente_pagina(driver):
    try:
        boton_siguiente = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".andes-pagination__button.andes-pagination__button--next a"))
        )
        boton_siguiente.click()
        print("Hizo clic en el botón 'Siguiente'.")
        return True
    except NoSuchElementException:
        print("No se encontró el botón 'Siguiente'.")
        return False
    except TimeoutException:
        print("Tiempo de espera agotado para encontrar el botón 'Siguiente'.")
        return False

def main_process(url_base, fechas_especificas):
    if not is_valid_url(url_base):
        print(f"URL inválida: {url_base}")
        return

    start_chrome_debugging()

    time.sleep(5)

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    processed_urls = set()  # Mantener un registro de URLs procesadas
    previous_page_content = None  # Para comparar el contenido de las páginas

    try:
        while True:
            print(f"Accediendo a la URL: {url_base}")
            driver.get(url_base)

            if not procesar_pagina(driver, fechas_especificas, processed_urls):
                break

            # Verifica si el contenido de la página ha cambiado
            current_page_content = driver.page_source
            if previous_page_content == current_page_content:
                print("El contenido de la página no ha cambiado. Terminando el proceso.")
                break
            previous_page_content = current_page_content

            # Manejo de la paginación
            if not click_siguiente_pagina(driver):
                print("No se pudo avanzar a la siguiente página. Terminando.")
                break

        # Revisar nuevamente la página para tarjetas no procesadas
        print("Revisando nuevamente las tarjetas para asegurarse de que todas fueron procesadas.")
        driver.get(url_base)
        procesar_pagina(driver, fechas_especificas, processed_urls)

    except TimeoutException:
        print("Tiempo de espera agotado al intentar cargar la página.")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
    finally:
        driver.quit()

# Ejemplo de llamada a la función principal:
# main_process("https://www.cualquier-url.com", ["20 jul", "19 jul", "18 jul", "17 jul"])
