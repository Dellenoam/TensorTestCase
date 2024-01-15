import pytest
from fuzzywuzzy import fuzz
from sbis_tensor_pages import SbisPage
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    yield browser
    browser.quit()


@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 20)


@pytest.fixture
def sbis_page(browser, wait):
    return SbisPage(browser, wait)


def test_tensor_about_image_size(browser, sbis_page):
    # Переходим на страницу sbis
    sbis_page.go_to_sbis_page()

    # Переходим в контакты
    sbis_page.go_to_contacts_page()

    # Идем на страницу Tensor
    sbis_page.go_to_tensor_page()

    # Переключаемся на вкладку с открытой страницей Tensor
    tensor_page = sbis_page.switch_to_tensor_tab()

    # Пробуем получить блок "Сила в людях"
    try:
        block_power_in_people = tensor_page.get_block_power_in_people()
    except NoSuchElementException:
        pytest.fail("Блок 'Сила в людях' не найден")

    # Переходим на страницу about
    tensor_page.go_to_tensor_about_page(block_power_in_people)

    # Изменился ли url страницы после перехода
    assert tensor_page.get_current_url() == 'https://tensor.ru/about'

    # Получаем все изображения из страницы about из блока Работаем
    images = tensor_page.get_tensor_about_images()

    # Проверяем, что они одного размера
    for image in images:
        assert image.size == images[0].size, "Размеры изображений не совпадают"


def test_change_region(browser, sbis_page):
    # Переходим на страницу sbis
    sbis_page.go_to_sbis_page()

    # Переходим на страницу с контактами
    sbis_page.go_to_contacts_page()

    # Получаем партнеров до смены региона
    main_partners = sbis_page.get_current_partners()

    # Проверяем, что регион соответствует настоящему
    main_region = sbis_page.get_current_region()
    assert fuzz.ratio(main_region, 'Свердловская область') >= 80, "Регионы не совпадают"

    # Изменяем регион
    sbis_page.change_region('Камчатский край')

    # Получаем новый регион и сравниваем с предыдущим
    new_region = sbis_page.get_current_region()
    assert new_region != main_region, "Регион не изменился"

    # Сравниваем предыдущих партнеров региона с текущими
    new_partners = sbis_page.get_current_partners()
    assert new_partners != main_partners, "Партнеры не изменились"

    # Проверяем, есть ли в текущей ссылке выбранный регион
    assert 'kamchatskij-kraj' in sbis_page.get_current_url(), "Текущий url не содержит выбранный регион"

    # Проверяем, изменился ли заголовок страницы на выбранный регион
    assert fuzz.ratio(sbis_page.get_current_title(), 'Камчатский край') >= 80, 'На странице title не изменился на новый'


def test_sbis_download_size(browser, sbis_page):
    # Переходим на страницу sbis
    sbis_page.go_to_sbis_page()

    # Переходим на страницу загрузки СБИС
    sbis_page.go_to_download_page()

    # Открываем загрузку плагина СБИС
    sbis_page.go_to_download_plugin_page()

    # Выбираем платформу Windows для плагина
    sbis_page.choose_plugin_windows_platform()

    # Скачиваем файл в папку проекта и получаем ожидаемый размер и реальный
    expected_file_size, real_file_size = sbis_page.download_windows_plugin()

    # Сравниваем ожидаемый размер файла с реальным
    assert expected_file_size == real_file_size, 'Размер файла не равен размеру на сайте'
