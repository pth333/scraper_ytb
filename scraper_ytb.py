import subprocess
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def start_chrome():
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe" 
    # profile_path = "C:/Users/My PC/AppData/Local/Google/Chrome/User Data/Profile 2"
    subprocess.Popen([
        chrome_path,
        "--remote-debugging-port=9222",
        # f"--user-data-dir={profile_path}" 
    ])

def setup_selenium():
    options = Options()
    options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_content(link, driver, wait, target_post_count=20):
    driver.get(link)

    elem = driver.find_element(By.TAG_NAME,"html")
    elem.send_keys(Keys.END)
    time.sleep(10)
    elem.send_keys(Keys.HOME)

    post_count = 0
    while post_count < target_post_count:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main")))

        main_contents = driver.find_elements(By.CSS_SELECTOR, "#main:not([data-processed='true'])")
        # lấy ra từng main của post
        for content_part in main_contents:
            if post_count >= target_post_count:  
                break

            driver.execute_script("arguments[0].scrollIntoView();", content_part)
            # driver.execute_script("arguments[0].setAttribute('data-processed', 'true')", content_part)

            get_content_text(content_part)
            get_img(content_part)
            get_like_dislike(content_part)

            time.sleep(5)

            comment_url = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-button-shape a.yt-spec-button-shape-next"))).get_attribute('href')
            # comment_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-button-shape a.yt-spec-button-shape-next")))
            # comment_url = comment_link.get_attribute('href')

            print("Link phần tử bình luận: ", comment_url)

            get_comment(driver,comment_url)

            post_count += 1
            # Đánh dấu bài viết là đã xử lý
            driver.execute_script("arguments[0].setAttribute('data-processed', 'true')", content_part)

            clear_cache(driver)

            print(f"Collected posts: {post_count}")

    print(f"Total posts collected: {post_count}")

def clear_cache(driver):
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.delete_all_cookies()

def get_comment(driver,comment_url):
    try:
        main_tab = driver.current_window_handle
        driver.execute_script("window.open(arguments[0], '_blank');", comment_url)
        driver.switch_to.window(driver.window_handles[-1])
        # Xóa cache sau khi chuyển tab
        clear_cache(driver)
        # Đợi trang bình luận tải xong
        time.sleep(5)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content-text")))

        current_url = driver.current_url
        print("Link hiện tại: ", current_url)

        comments = driver.find_elements(By.CSS_SELECTOR, '#content-text')

        comment_text = ''
        count = 0
        for comment in comments:
            if count >= 19:
                break
            comment_text += comment.text + "\n"
            count += 1
        
        print("Bình luận: \n", comment_text)

        driver.close()
        driver.switch_to.window(main_tab)

        time.sleep(5)

    except Exception as e:
        print("Error:", e)

def get_content_text(content_part):
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content-text")))
    main_contents = content_part.find_element(By.CSS_SELECTOR, "#content-text")
    print("Content: ",main_contents.text)

def get_img(content_part):
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "yt-img-shadow img")))
        image_content = content_part.find_element(By.CSS_SELECTOR, "yt-img-shadow img").get_attribute('src')
        print("URL image: ", image_content)
    except Exception as e:
        print("Không tìm thấy ảnh:", e)

def get_like_dislike(content_part):
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#vote-count-middle")))
    like_dislike = content_part.find_element(By.CSS_SELECTOR, "#vote-count-middle").text
    print("Like: ", like_dislike)
        
try: 
    array_ytb_url = [{"site_id":"2","site_url":"https:\/\/monkeykaka.net","youtube_url":"https:\/\/www.youtube.com\/@MonkeyKaKa"},
                 {"site_id":"4","site_url":"https:\/\/monkeypupu.com","youtube_url":"https:\/\/www.youtube.com\/@PUPUMONKEY-2"},
                 {"site_id":"5","site_url":"https:\/\/monkeypuka.com","youtube_url":"https:\/\/www.youtube.com\/@MonkeyPuka"},
                 {"site_id":"11","site_url":"https:\/\/cms.kolsup.com\/monkeycutis","youtube_url":"https:\/\/www.youtube.com\/@CUTIS9"},
                 {"site_id":"12","site_url":"https:\/\/cms.kolsup.com\/monkeyabu","youtube_url":"https:\/\/www.youtube.com\/@MONKEYABU16"},
                 {"site_id":"14","site_url":"https:\/\/monkeyyoyo.com","youtube_url":"https:\/\/www.youtube.com\/@monkeybabyyoyo514"},
                 {"site_id":"17","site_url":"https:\/\/monkeybibi.com","youtube_url":"https:\/\/www.youtube.com\/@MonkeyBiBi16"},
                 {"site_id":"21","site_url":"https:\/\/monkeypika.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@MonkeyPika2610"},
                 {"site_id":"35","site_url":"https:\/\/monkeyzim.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@zimmonkey"},
                 {"site_id":"113","site_url":"https:\/\/caseoh.club","youtube_url":"https:\/\/www.youtube.com\/@caseoh_"},
                 {"site_id":"127","site_url":"https:\/\/ohnonina.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@ohnonina"},
                 {"site_id":"128","site_url":"https:\/\/gardenanswer.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@gardenanswer"},
                 {"site_id":"129","site_url":"https:\/\/thebodycoachtv.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@TheBodyCoachTV"},
                 {"site_id":"130","site_url":"https:\/\/funforlouis.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@Louis"},
                 {"site_id":"131","site_url":"https:\/\/veritasium.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@veritasium"},
                 {"site_id":"133","site_url":"https:\/\/mikechen.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@MikeyChenX"},
                 {"site_id":"134","site_url":"https:\/\/haileyinbookland.kolsup.com","youtube_url":"https:\/\/www.youtube.com\/@HaileyinBookland"}]
    start_chrome()
    driver = setup_selenium()
    # webdriver.Chrome()
    wait = WebDriverWait(driver, 15)
    
    for link in array_ytb_url:
        link_community = link['youtube_url'] + '/community'
        content_home = get_content(link_community, driver, wait)
        exit()
finally:
    time.sleep(30)
    driver.quit()
