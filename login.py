import pytest
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


@pytest.fixture
def driver(request):
    wd = webdriver.Chrome()
    request.addfinalizer(wd.quit)
    return wd


def test_login(driver):
    driver.get("http://localhost/litecart/admin")
    driver.find_element_by_name("username").send_keys("admin")
    driver.find_element_by_name("password").send_keys("admin")
    driver.find_element_by_name("remember_me").click()
    driver.find_element_by_name("login").click()
    # driver.find_element_by_link_text('Appearence').click()
    # time.sleep(2)
    for section in range(1, len(driver.find_elements_by_css_selector("#app-")) + 1):
        driver.find_element_by_css_selector(f"#app-:nth-child({section})").click()
        if driver.find_elements_by_css_selector(f"#app-:nth-child({section}) li") is not None:
            for sub_section in range(1, len(driver.find_elements_by_css_selector(f"#app-:nth-child({section}) li")) + 1):
                driver.find_element_by_css_selector(f"#app-:nth-child({section}) li:nth-child({sub_section})").click()
                assert driver.find_element_by_css_selector("#content > h1"), "Заголовок H1 не найден"
    driver.find_element_by_css_selector('[title="Logout"]').click()
    driver.find_element_by_css_selector('div [class="content"]')


def test_check_stickers(driver):
    driver.get("http://localhost/litecart/")
    ducks = driver.find_elements_by_css_selector('div.image-wrapper')
    for duck in ducks:
        try:
            duck.find_element_by_css_selector('div.sticker')
        except NoSuchElementException:
            print('U ' + duck.find_element_by_xpath('../div[@class="name"]').text + ' Нет стикера!')
    for duck in ducks:
        duck.find_element_by_css_selector('div.sticker')