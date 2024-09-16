import subprocess
import requests
import re
import json
import random
import base64
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
    subprocess.Popen([
        chrome_path,
        "--remote-debugging-port=9222",
    ])

def setup_selenium():
    options = Options()
    options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def rotate_user_agent(user_agents):
    random_user_agent = random.choice(user_agents)
    options = Options()
    options.add_argument(f"user-agent={random_user_agent}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print(f"Đang sử dụng User-Agent: {random_user_agent}")
    return driver

def clear_cache(driver):
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.delete_all_cookies()

def get_content(link, driver):
    try:
        driver.get(link)
     
        elem = driver.find_element(By.TAG_NAME,"html")
        elem.send_keys(Keys.END)
        time.sleep(15)
        elem.send_keys(Keys.HOME)

        post_count = 0
        max_post = 20

        while True:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            posts = soup.find_all(id='main')
            list_post = []
            for post in posts:
                if post_count < max_post:
                    list_post.append(post)
                    post_count += 1
                else:
                    break
            if post_count >= max_post:
                break
        return list_post
    
    finally:
        driver.quit()
    
def get_comment(driver, content_part):
    link_comment = content_part.find('a', class_='yt-spec-button-shape-next').get('href')
    relative_comment_url =  'https://www.youtube.com' + link_comment
    
    # print("Link comment: ", relative_comment_url)
    driver.get(relative_comment_url)
    time.sleep(5)

    clear_cache(driver)

    comment_count = 0
    max_comment = 20
    skip_first = True 
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        comments = soup.find_all(id='content-text')
        list_comment = ''
        for comment_content in comments:
            if skip_first:
                skip_first = False  # Bỏ qua comment đầu tiên
                continue
            if comment_count < max_comment:
                list_comment += comment_content.text + "\n"
                comment_count += 1
            else:
                break
        if comment_count >= max_comment:
            break
    return list_comment
    
def get_content_text(content_part):
    try:
        # Tìm phần tử chứa nội dung
        content_element = content_part.find(id='content-text')
        contents = []
        for element in content_element.descendants:
            # Kiểm tra nếu element là thẻ <a>
            if element.name == 'a':
                link = element['href']  
                text = element.text.strip() 
                contents.append(f'<a href="{link}" {get_attributes(element)}></a>')
            elif element.string and element.string.strip():
                # Lấy văn bản thuần (không phải thẻ <a>) và loại bỏ khoảng trắng
                contents.append(element.string.strip())

        return ' '.join(contents)
    
    except Exception as e:
        print("Lỗi khi lấy nội dung:", e)
        return ""

def get_attributes(element):
    attrs = ['{}="{}"'.format(attr, value) for attr, value in element.attrs.items() if attr != 'href']
    return ' '.join(attrs) if attrs else ''

def get_img(content_part):
    try:
        time.sleep(5)
        image_element = content_part.select_one('yt-img-shadow img')
        image_content = image_element.get('src')
        return image_content
    except Exception as e:
        print("Không tìm thấy ảnh:", e)

def get_like(content_part):
    likes = content_part.find(id='vote-count-middle').text
    return likes

# Hàm chuẩn hóa URL YouTube
def normalize_youtube_url(url):
    # Tìm tất cả các phần sau '@' và loại bỏ bất kỳ phần bổ sung nào như '/featured'
    match = re.search(r'https://www\.youtube\.com/@[^/]+', url)
    if match:
        return match.group(0)
    return url

def create_wordpress_post(content, image_post, like_number, comments):
    api_url = 'http://new-website.com/wp-content/themes/new-theme/inc/insert-data.php'
    response = requests.post(api_url, headers=wordpress_header, data={'content' : content,
                                                                      'image_post' : image_post,
                                                                      'like_number' : like_number,
                                                                      'comments' : comments})
    print(response.status_code) 
    print(response.text) 
    
try: 
    wordpress_user = 'hieuphan'
    wordpress_password = 'hieuphan202'
    credentials = f"{wordpress_user}:{wordpress_password}"
    wp_token = base64.b64encode(credentials.encode())
    wordpress_header = {'Authorization': 'Basic ' + wp_token.decode('utf-8')}

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    ]

    list_url = "https://studio.kolsup.com/tool/test.php?dsad189fmas92=query_youtube_url"

    response = requests.get(list_url)
    array_ytb_url = json.loads(response.text)
    start_chrome()
    driver = setup_selenium()
    # driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)

    for link in array_ytb_url:
        if isinstance(link, dict) and 'youtube_url' in link:
        # Chuẩn hóa URL
            link_community = normalize_youtube_url(link['youtube_url']) + '/community'
            # print("Link cộng đồng:", link_community)

        content_home = get_content(link_community, driver)
        count = 0

        for main_content in content_home:
            content = get_content_text(main_content)
            image_post = get_img(main_content)
            like_number = get_like(main_content)
            print("Content: ", content)
            print("URL image: ", image_post)
            print(f"Like Number:{like_number}")
            # Đóng trình điều khiển hiện tại và tạo lại với User-Agent mới
            # driver.quit()
            print("Đang lấy dữ liệu bình luận...")
            time.sleep(5)
            driver = rotate_user_agent(user_agent_list)
            comments = get_comment(driver, main_content)
            print("Comments:\n ", comments)
            print("Đang thêm dữ liệu...")
            create_wordpress_post(content, image_post, like_number, comments)
            print("-------------------------------------------")
            print("Bài: ", count+1)

            # count += 1
            # if(count == 3):
            #     break

        print("Số bài post: ", count)
        print("Kết thúc...")
        exit()
finally:
    driver.quit()
