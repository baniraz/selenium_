import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from helpers import login_admin
import re
from selenium.webdriver.common.keys import Keys
import random
import string
import time


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
    item = 0
    while item < len(driver.find_elements_by_css_selector("li.product")):
        ducks = driver.find_elements_by_css_selector("li.product")[item]
        label_count = len(ducks.find_elements_by_css_selector("div.sticker"))
        assert label_count == 1
        item += 1


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


def test_ducks(driver):
    driver.get("http://localhost/litecart/")
    driver.find_element_by_css_selector('li.category-1').click()
    ducks_mp = {}
    ducks_elem_mp = driver.find_elements_by_css_selector('li.product > a.link')
    for duck in ducks_elem_mp:
        duck_name = duck.find_element_by_css_selector('.name').text
        if duck.find_element_by_css_selector('.image-wrapper > div.sticker').text == 'SALE':
            duck_price = duck.find_element_by_css_selector('.price-wrapper > .regular-price').text
            duck_sale_price = duck.find_element_by_css_selector('.price-wrapper > .campaign-price').text
        else:
            duck_price = duck.find_element_by_css_selector('.price').text
            duck_sale_price = ''
        duck_link = duck.get_attribute('href')
        ducks_mp[duck_name] = [duck_price, duck_sale_price, duck_link]
    for duck in ducks_mp:
        driver.get(ducks_mp[duck][2])
        assert duck == driver.find_element_by_css_selector('h1.title').text
        if ducks_mp[duck][1]:
            price = driver.find_element_by_css_selector('#box-product .regular-price')
            assert price.text == ducks_mp[duck][0]
            price_color = price.value_of_css_property('color').split()
            price_color = [int(re.findall(r'\d+', x)[0]) for x in price_color]
            assert price_color[0] == price_color[1] == price_color[2]
            price_size = int(re.findall(r'\d+', price.value_of_css_property('font-size'))[0])
            campaign_price = driver.find_element_by_css_selector('#box-product .campaign-price')
            assert campaign_price.text == ducks_mp[duck][1]
            campaign_price_color = campaign_price.value_of_css_property('color').split()
            campaign_price_color = [int(re.findall(r'\d+', x)[0]) for x in campaign_price_color]
            assert 0 == campaign_price_color[1] == campaign_price_color[2]
            campaign_price_size = int(re.findall(r'\d+', campaign_price.value_of_css_property('font-size'))[0])
            assert campaign_price_size > price_size
        else:
            price = driver.find_element_by_css_selector('#box-product .price')
            assert price.text == ducks_mp[duck][0]
            price_color = price.value_of_css_property('color').split()
            price_color = [int(re.findall(r'\d+', x)[0]) for x in price_color]
            assert price_color[0] == price_color[1] == price_color[2]


def generate_logpass():
    login = ''
    password = ''
    adress = random.choice(string.ascii_letters).upper()
    postcode = ''
    city = random.choice(string.ascii_letters).upper()
    phone = '+1'
    for _ in range(random.randint(5, 12)):
        login += random.choice(string.ascii_letters).lower()
    for _ in range(random.randint(5, 12)):
        password += random.choice(string.ascii_letters + string.digits)
    for _ in range(random.randint(4, 8)):
        adress += random.choice(string.ascii_letters).lower()
    for _ in range(5):
        postcode += random.choice(string.digits)
    for _ in range(random.randint(4, 8)):
        city += random.choice(string.ascii_letters).lower()
    for _ in range(10):
        phone += random.choice(string.digits)
    adress_ads = [' St.', ' Ave.', ' Blvd.', ' Ln.']
    adress += random.choice(adress_ads)
    name_separator = random.randint(2, len(login) - 2)
    f_name = login[:name_separator].capitalize()
    l_name = login[name_separator:].capitalize()
    emails = ['@gmail.com', '@mail.ru', '@yandex.ru']
    login += random.choice(emails)
    return login, password, f_name, l_name, adress, postcode, city, phone


def test_user_registration(driver):
    driver.get("http://localhost/litecart/en/create_account")
    login, password, f_name, l_name, adress, postcode, city, phone = generate_logpass()
    driver.find_element_by_name('firstname').send_keys(f_name)
    driver.find_element_by_name('lastname').send_keys(l_name)
    driver.find_element_by_name('address1').send_keys(adress)
    driver.find_element_by_name('postcode').send_keys(postcode)
    driver.find_element_by_name('city').send_keys(city)
    driver.find_element_by_css_selector('span.select2-container').click()
    driver.find_element_by_css_selector('input.select2-search__field').send_keys('United States')
    driver.find_element_by_css_selector('input.select2-search__field').send_keys(Keys.ENTER)
    driver.find_element_by_name('email').send_keys(login)
    driver.find_element_by_name('phone').send_keys(phone)
    driver.find_element_by_name('newsletter').click()
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_name('confirmed_password').send_keys(password)
    driver.find_element_by_name('create_account').click()
    driver.find_element_by_name('zone_code').click()
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_name('confirmed_password').send_keys(password)
    driver.find_element_by_name('create_account').click()
    time.sleep(1)
    driver.implicitly_wait(10)
    driver.find_element_by_link_text("Logout").click()
    driver.implicitly_wait(10)
    driver.find_element_by_name('email').send_keys(login)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_name('login').click()
    driver.find_element_by_link_text('Logout').click()
    time.sleep(1)
    driver.implicitly_wait(10)
    driver.find_element_by_link_text("Logout").click()
