from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import json

service = Service("/usr/bin/chromedriver")
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-infobars")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
options.page_load_strategy = 'eager'

try:
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    driver.get("https://www.youtube.com")
    print("Открылся YouTube")

    # куки грузим
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

    driver.refresh()
    print("Страница обновлена")

    print("Ищем строку поиска...")
    search_box = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input#search, input[name='search_query']"))
    )
    search_box.clear()
    search_box.send_keys("srt-10 donuts")
    search_box.submit()
    print("Поиск успешен")

    # результаты поиска
    wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "ytd-rich-item-renderer a#video-title, "
            "ytd-video-renderer a#video-title, "
            "#dismissible a#video-title"
        ))
    )

    first_video = wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "ytd-rich-item-renderer a#video-title, "
            "ytd-video-renderer a#video-title, "
            "#dismissible a#video-title"
        ))
    )
    first_video.click()
    print("Открыто первое видео")

    # минимальное ожидание
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#top-level-buttons-computed")))
    driver.execute_script("window.scrollTo(0, 0);")
    print("Видео загружено:", driver.title)

    
    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Close'], button[aria-label*='Закрыть']")
        close_btn.click()
    except:
        pass


    LIKE_SELECTOR = "#top-level-buttons-computed button[aria-label*='Нравится']"
    
    def get_like_button():
        try:
            return driver.find_element(By.CSS_SELECTOR, LIKE_SELECTOR)
        except:
            return driver.find_element(By.CSS_SELECTOR, 
                ".yt-segmented-like-dislike-button-renderer button")

    def click_like():
        btn = get_like_button()
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        driver.execute_script("arguments[0].click();", btn)
        return btn.get_attribute('aria-pressed')

    print("Проверка")
    
    # если не стоит -> поставить -> обновить
    first_like = get_like_button()
    if first_like.get_attribute('aria-pressed') == 'false':
        print("Нету -> ставим")
        click_like()
        print("Поставили -> Refresh...")
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#top-level-buttons-computed")))
        print("Refresh 1 OK")
    else:
        #если стоит -> убрать -> обновить -> поставить -> обновить  
        print("Уже liked -> убираем")
        click_like()  # Снимаем
        print("Сняли -> Refresh...")
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#top-level-buttons-computed")))
        
        print("Ставим обратно")
        click_like()
        print("Поставили -> Refresh...")
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#top-level-buttons-computed")))
        print("✅ Финальный Refresh OK")

    final_like = get_like_button()
    print(f"'{final_like.get_attribute('aria-pressed')}'")

except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        driver.quit()
    except:
        pass