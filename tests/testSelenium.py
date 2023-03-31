import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def testing():
    pytest.driver = webdriver.Chrome('chromedriver.exe')
    # Переходим на страницу авторизации
    pytest.driver.get('https://petfriends.skillfactory.ru/login')
    yield
    pytest.driver.quit()


@pytest.fixture()
def test_show_my_pets():
    element = WebDriverWait(pytest.driver, 3).until(EC.presence_of_element_located((By.ID, "email")))
    # Вводим email
    pytest.driver.find_element(By.ID, 'email').send_keys('kozlaleksan2013@gmail.com')
    element = WebDriverWait(pytest.driver, 3).until(EC.presence_of_element_located((By.ID, "pass")))
    # Вводим пароль
    pytest.driver.find_element(By.ID, 'pass').send_keys('22091991kk')
    element = WebDriverWait(pytest.driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    element = WebDriverWait(pytest.driver, 3).until(EC.presence_of_element_located((By.LINK_TEXT, "Мои питомцы")))
    # Нажимаем на ссылку "Мои питомцы"
    pytest.driver.find_element(By.LINK_TEXT, "Мои питомцы").click()


# Проверка карточек питомцев
def test_show_pet_friends():
    # Устанавливаем неявное ожидание
    pytest.driver.implicitly_wait(10)
    # Вводим email
    pytest.driver.find_element(By.ID, 'email').send_keys('kozlaleksan2013@gmail.com')
    # Вводим пароль
    pytest.driver.find_element(By.ID, 'pass').send_keys('22091991kk')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.current_url == 'http://petfriends1.herokuapp.com/all_pets'

    images = pytest.driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-img-top')
    names = pytest.driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-title')
    descriptions = pytest.driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-text')

    for i in range(len(names)):
        assert images[i].get_attribute('src') != ''
        assert names[i].text != ''
        assert descriptions[i].text != ''
        assert ',' in descriptions[i].text
        parts = descriptions[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


# Проверяем что на странице со списком моих питомцев присутствуют все питомцы
def test_all_pets_are_present(test_show_my_pets):
    element = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".\\.col-sm-4.left")))
    stat = pytest.driver.find_elements(By.CSS_SELECTOR, ".\\.col-sm-4.left")
    element = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".table.table-hover tbody tr")))
    # Сохраняем в переменную pets элементы карточек питомцев
    pets = pytest.driver.find_elements(By.CSS_SELECTOR, '.table.table-hover tbody tr')

    # Получаем количество питомцев из данных статистики
    number = stat[0].text.split('\n')
    number = number[1].split(' ')
    number = int(number[1])
    # Получаем количество карточек питомцев
    number_of_pets = len(pets)
    # Проверяем что количество питомцев из статистики совпадает с количеством карточек питомцев
    assert number == number_of_pets


# Поверяем что на странице со списком моих питомцев хотя бы у половины питомцев есть фото
def test_photo_availability(test_show_my_pets):
    element = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".\\.col-sm-4.left")))
    stat = pytest.driver.find_elements(By.CSS_SELECTOR, ".\\.col-sm-4.left")
    # Сохраняем в переменную images элементы с атрибутом img
    images = pytest.driver.find_elements(By.CSS_SELECTOR, '.table.table-hover img')
    # Получаем количество питомцев из данных статистики
    number = stat[0].text.split('\n')
    number = number[1].split(' ')
    number = int(number[1])
    # Находим половину от количества питомцев
    half = number // 2
    # Находим количество питомцев с фотографией
    number_а_photos = 0
    for i in range(len(images)):
        if images[i].get_attribute('src') != '':
            number_а_photos += 1
    # Проверяем что количество питомцев с фотографией больше или равно половине количества питомцев
    assert number_а_photos >= half
    # print(f'количество фото: {number_а_photos}')
    # print(f'Половина от числа питомцев: {half}')


# Поверяем что на странице со списком моих питомцев, у всех питомцев есть имя, возраст и порода
def test_there_is_a_name_age_and_gender(test_show_my_pets):
    element = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".table.table-hover tbody tr")))
    # Сохраняем в переменную pet_data элементы с данными о питомцах
    pet_data = pytest.driver.find_elements(By.CSS_SELECTOR, '.table.table-hover tbody tr')
    # Перебираем данные из pet_data, оставляем имя, возраст, и породу, остальное меняем на пустую строку
    # и разделяем по пробелу. Находим количество элементов в получившемся списке и сравниваем их
    # с ожидаемым результатом
    for i in range(len(pet_data)):
        data_pet = pet_data[i].text.replace('\n', '').replace('×', '')
        split_data_pet = data_pet.split(' ')
        result = len(split_data_pet)
        assert result == 3


# Поверяем что на странице со списком моих питомцев, у всех питомцев разные имена
def test_all_pets_have_different_names(test_show_my_pets):
    element = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".table.table-hover tbody tr")))
    # Сохраняем в переменную pet_data элементы с данными о питомцах
    pet_data = pytest.driver.find_elements(By.CSS_SELECTOR, '.table.table-hover tbody tr')
    # Перебираем данные из pet_data, оставляем имя, возраст, и породу остальное меняем на пустую строку
    # и разделяем по пробелу.Выбераем имена и добавляем их в список pets_name.
    pets_name = []
    for i in range(len(pet_data)):
        data_pet = pet_data[i].text.replace('\n', '').replace('×', '')
        split_data_pet = data_pet.split(' ')
        pets_name.append(split_data_pet[0])
    # Перебираем имена и если имя повторяется то прибавляем к счетчику r единицу.
    # Проверяем, если r == 0 то повторяющихся имен нет.
    r = 0
    for i in range(len(pets_name)):
        if pets_name.count(pets_name[i]) > 1:
            r += 1
    assert r == 0
    print(r)
    print(pets_name)
