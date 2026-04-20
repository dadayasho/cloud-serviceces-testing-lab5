from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import json


# Путь к chromedriver
service = Service("/usr/bin/chromedriver")
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-infobars")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

try:
    # открываем YouTube
    driver.get("https://www.youtube.com")
    print("Открылся YouTube")

    # загружаем куки
    with open("./yt_cookies.json", "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            if "name" not in cookie or "value" not in cookie:
                continue
            driver.add_cookie({
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", ".youtube.com"),
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", True),
                "httpOnly": cookie.get("httpOnly", False),
            })

    # обновляем
    driver.refresh()
    time.sleep(5)

    print("Title:", driver.title)
    print("URL:", driver.current_url)

    # ггрузим морду
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ytd-rich-grid-renderer, ytd-browse")
        )
    )
    print("Главная страница загружена")

    # закрытие popup уведомлений
    try:
        close_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 
                 "paper-dialog button[aria-label*='Close'], "
                 "button[aria-label*='Закрыть'], "
                 "#dismiss-button, .ytp-button.ytp-popup")
            )
        )
        close_button.click()
        time.sleep(1)
        print("Всплывающее окно закрыто")
    except:
        print("Всплывающее окно найден")
    print("Поиск ...")
    # ищем
    search_box = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input#search, input[name='search_query']")
        )
    )
    search_box.clear()
    search_box.send_keys("srt-10 donuts")
    search_box.submit()
    print("Поиск выполнен")

    time.sleep(3)

    # кликаем на первый видос
    first_video = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 
             "ytd-rich-item-renderer a#video-title, "
             "ytd-video-renderer a#video-title, "
             "#dismissible a#video-title")
        )
    )
    first_video.click()
    print("Открыто первое видео")

    # ждем загрузки
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#top-level-buttons-computed, #info"))
    )
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    print("Page title (video):", driver.title)
    print("URL (video):", driver.current_url)

    # лайкаем по объекту лайка ориентируемся
    selectors = [
        "#top-level-buttons-computed button[aria-label*='Нравится'], "
        "#top-level-buttons-computed button[aria-label*='Like']"
    ]

    like_button = None
    used_selector = None

    for selector in selectors:
        try:
            like_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            used_selector = selector
            print(f"Найдена кнопка лайка по селектору: {selector}")
            print(f"aria-label: '{like_button.get_attribute('aria-label')}'")
            break
        except Exception as e:
            print(f"'{selector}' → {str(e)[:40]}")

    # доп проверка
    if not like_button:
        try:
            print("🔍 Ищем в segmented контейнере...")
            segmented_hosts = driver.find_elements(By.CSS_SELECTOR, 
                "yt-segmented-like-dislike-button-view-model, "
                "ytd-segmented-like-dislike-button-renderer, "
                ".ytSegmentedLikeDislikeButtonViewModelHost")
            for host in segmented_hosts:
                try:
                    like_button = host.find_element(By.CSS_SELECTOR, 
                        "like-button-view-model button, "
                        ".yt-spec-button-shape-next--segmented-start button")
                    used_selector = "nested in segmented host"
                    print("Найден в segmented контейнере!")
                    break
                except:
                    continue
        except:
            pass

    if not like_button:
        print("Кнопка лайка не найдена, сохраняем лог")
        with open("youtube_page_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise Exception("Like button not found!")

    # проверка состояния
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
    time.sleep(1)

    ActionChains(driver).move_to_element(like_button).perform()
    time.sleep(1)

    like_state = like_button.get_attribute("aria-pressed")
    print(f"Прожат ли лайк '{like_state}'")

    # ставим -> проверяем -> если снялся -> ставим заново
    print("Ставим лайк")

    # первый клик (ставим лайк)
    driver.execute_script("arguments[0].click();", like_button)
    like_button.click()
    time.sleep(3)

    final_state = like_button.get_attribute("aria-pressed")
    print(f"После 1 клика: '{final_state}' (было: '{like_state}')")

    # обновляем и проверяем
    print("Обновляем страницу")
    driver.refresh()
    time.sleep(5)

    like_button_after = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, used_selector)))
    final_state_after = like_button_after.get_attribute("aria-pressed")

    if final_state_after == "false":
        print("Лайк снялся -> ставим снова")
        # ставим лайк один раз
        driver.execute_script("arguments[0].click();", like_button_after)
        time.sleep(2)  # немного подождём пока реакция примется

        # ф5
        driver.refresh()
        print("Страница обновлена")

        # снова ждём кнопку
        like_button_after = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, used_selector)))
        final_final_state = like_button_after.get_attribute("aria-pressed")
        print(f"Состояние после обновления: '{final_final_state}'")

        if final_final_state == "true":
            print("Лайк на месте")
        else:
            print("Проблема - лайк не держится")
    else:
        print("Лайк сохранился после обновления")

    print("Скрипт выполнен успешно")

except Exception as e:
    print(f"Ошибка: {e}")
finally:
    driver.quit()