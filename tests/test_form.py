"""
tests/test_form.py
Лабораторная работа — CI/CD с GitHub Actions
Selenium-тесты формы регистрации
"""

import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


# ─── Фикстура браузера ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    drv = webdriver.Chrome(options=options)

    # Путь к index.html относительно корня проекта
    html_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "index.html")
    )
    drv.get(f"file:///{html_path}")

    yield drv
    drv.quit()


def refresh(driver):
    """Перезагружает страницу перед каждым тестом для чистого состояния."""
    driver.refresh()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "reg-form"))
    )


# ─── Тест 1: Отображение всех элементов формы ─────────────────────────────────

def test_форма_содержит_все_поля(driver):
    """Проверяет, что все поля и кнопка присутствуют на странице."""
    refresh(driver)

    assert driver.find_element(By.ID, "username").is_displayed(), \
        "Поле 'Имя пользователя' не отображается"
    assert driver.find_element(By.ID, "email").is_displayed(), \
        "Поле 'Email' не отображается"
    assert driver.find_element(By.ID, "role").is_displayed(), \
        "Поле 'Роль' не отображается"
    assert driver.find_element(By.ID, "password").is_displayed(), \
        "Поле 'Пароль' не отображается"
    assert driver.find_element(By.ID, "agree").is_displayed(), \
        "Чекбокс согласия не отображается"

    btn = driver.find_element(By.ID, "submit-btn")
    assert btn.is_displayed(), "Кнопка отправки не отображается"
    assert "Создать аккаунт" in btn.text, \
        f"Неожиданный текст кнопки: {btn.text}"


# ─── Тест 2: Успешная регистрация при корректных данных ───────────────────────

def test_успешная_регистрация(driver):
    """Заполняет форму корректными данными и проверяет сообщение об успехе."""
    refresh(driver)

    driver.find_element(By.ID, "username").send_keys("ivan_petrov")
    driver.find_element(By.ID, "email").send_keys("ivan@example.com")

    Select(driver.find_element(By.ID, "role")).select_by_value("developer")

    driver.find_element(By.ID, "password").send_keys("secret123")
    driver.find_element(By.ID, "agree").click()
    driver.find_element(By.ID, "submit-btn").click()

    success = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "success-msg"))
    )
    assert success.is_displayed(), "Сообщение об успехе не появилось"
    assert "успешно" in success.text.lower(), \
        f"Неожиданный текст сообщения: {success.text}"


# ─── Тест 3: Ошибки валидации при пустой форме ────────────────────────────────

def test_валидация_пустой_формы(driver):
    """Отправляет пустую форму и проверяет появление ошибок валидации."""
    refresh(driver)

    driver.find_element(By.ID, "submit-btn").click()

    # Сообщение об успехе не должно появиться
    success = driver.find_element(By.ID, "success-msg")
    assert not success.is_displayed(), \
        "Сообщение об успехе не должно появляться при пустой форме"

    # Поля должны получить класс ошибки
    username_cls = driver.find_element(By.ID, "username").get_attribute("class")
    email_cls    = driver.find_element(By.ID, "email").get_attribute("class")
    password_cls = driver.find_element(By.ID, "password").get_attribute("class")

    assert "error" in username_cls, "Поле username должно иметь класс error"
    assert "error" in email_cls,    "Поле email должно иметь класс error"
    assert "error" in password_cls, "Поле password должно иметь класс error"

    # Подсказки об ошибках должны быть видны
    assert driver.find_element(By.ID, "username-error").is_displayed(), \
        "Текст ошибки для username не виден"
    assert driver.find_element(By.ID, "email-error").is_displayed(), \
        "Текст ошибки для email не виден"
    assert driver.find_element(By.ID, "password-error").is_displayed(), \
        "Текст ошибки для password не виден"


# ─── Тест 4: Ошибка при коротком пароле и невалидном email ────────────────────

def test_невалидные_данные(driver):
    """Проверяет, что слабый пароль и неверный email блокируют отправку."""
    refresh(driver)

    driver.find_element(By.ID, "username").send_keys("anna")
    driver.find_element(By.ID, "email").send_keys("не-email")     # неверный формат
    Select(driver.find_element(By.ID, "role")).select_by_value("tester")
    driver.find_element(By.ID, "password").send_keys("123")       # короче 6 символов
    driver.find_element(By.ID, "agree").click()
    driver.find_element(By.ID, "submit-btn").click()

    # Успех не должен наступить
    success = driver.find_element(By.ID, "success-msg")
    assert not success.is_displayed(), \
        "Форма не должна принимать невалидные данные"

    # Email помечен как ошибочный
    email_cls = driver.find_element(By.ID, "email").get_attribute("class")
    assert "error" in email_cls, "Поле email должно быть помечено как ошибочное"

    # Пароль помечен как ошибочный
    pwd_cls = driver.find_element(By.ID, "password").get_attribute("class")
    assert "error" in pwd_cls, "Поле password должно быть помечено как ошибочное"
