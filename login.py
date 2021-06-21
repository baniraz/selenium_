import pytest
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from helpers import login_admin

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


def sort_checker(li):
    li_sort = li.copy()
    li_sort = sorted(li_sort)
    assert li_sort == li, f"Список не отсортирован"


def check_countries(countries_elems):
    countries_list = []
    countries_to_check = []
    for i in countries_elems:
        countries_list.append(i.find_element_by_css_selector('td:nth-child(5)').text)
        if int(i.find_element_by_css_selector('td:nth-child(6)').text) > 0:
            countries_to_check.append(i.find_element_by_css_selector('td:nth-child(5)').text)
    sort_checker(countries_list)
    return countries_to_check


def check_zones(driver, countries_to_check, backpage, where_is_the_zone, how_to_check):
    for country in countries_to_check:
        driver.find_element_by_xpath(f"//a[contains(text(), '{country}')]").click()
        zone_rows = driver.find_elements_by_css_selector('table#table-zones > tbody > tr')
        zones = []
        for i in zone_rows[1: -1]:
            zone_name = i.find_element_by_xpath(where_is_the_zone)
            zones.append(zone_name.get_attribute(how_to_check))
        sort_checker(zones)
        driver.get(backpage)


def test_list_sorts_in_countries(driver):
    login_admin(driver)
    driver.get("http://localhost/litecart/admin/?app=countries&doc=countries/")
    countries_url = 'http://localhost/litecart/admin/?app=countries&doc=countries/'
    driver.get(countries_url)
    countries_elems = driver.find_elements_by_css_selector('table.dataTable > tbody > tr.row')
    countries_to_check = check_countries(countries_elems)
    check_zones(driver, countries_to_check, countries_url, './td[3]/input', 'value')
    driver.close()


def test_list_sorts_in_zones(driver):
    login_admin(driver)
    zones_url = 'http://localhost/litecart/admin/?app=geo_zones&doc=geo_zones/'
    driver.get(zones_url)
    countries_elems = driver.find_elements_by_css_selector('table.dataTable > tbody > tr.row')
    countries_to_check = []
    for i in countries_elems:
        countries_to_check.append(i.find_element_by_css_selector('td:nth-child(3) > a').text)
    check_zones(driver, countries_to_check, zones_url, './td[3]/select/option[@selected="selected"]', 'text')