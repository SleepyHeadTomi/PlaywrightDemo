import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture()
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

BASE_URL = "https://www.saucedemo.com/"

def test_title(page):
    page.goto(BASE_URL)
    assert page.title() == "Swag Labs"

def test_login_correct_credentials(page):
    page.goto(f"{BASE_URL}")
    username_input = page.locator('[data-test="username"]')
    password_input = page.locator('[data-test="password"]')
    submit_btn = page.locator('input[type="submit"]')

    username_input.fill("standard_user")
    password_input.fill("secret_sauce")
    submit_btn.click()

    assert page.url == f"{BASE_URL}inventory.html"

@pytest.mark.parametrize("username,password", [
    ("wrong_user", "secret_sauce"),
    ("standard_user", "wrong_sauce"),
])
def test_login_wrong_credentials(page, username, password):
    page.goto(f"{BASE_URL}")
    username_input = page.locator('[data-test="username"]')
    password_input = page.locator('[data-test="password"]')
    submit_btn = page.locator('[data-test="login-button"]')

    username_input.fill(username)
    password_input.fill(password)
    submit_btn.click()

    assert page.url == f"{BASE_URL}"
    assert (page.locator('[data-test="error"]').inner_text() ==
            "Epic sadface: Username and password do not match any user in this service")

def test_inventory_not_accessed_without_login(page):
    page.goto(f"{BASE_URL}inventory.html")
    error_msg = page.locator('[data-test="error"]').inner_text()
    assert error_msg == "Epic sadface: You can only access '/inventory.html' when you are logged in."

def test_order_backpack_e2e(page):
    page.goto(f"{BASE_URL}")
    username_input = page.locator('[data-test="username"]')
    password_input = page.locator('[data-test="password"]')
    submit_btn = page.locator('input[type="submit"]')

    username_input.fill("standard_user")
    password_input.fill("secret_sauce")
    submit_btn.click()

    assert page.url == f"{BASE_URL}inventory.html"

    backpack_img = page.get_by_alt_text("Sauce Labs Backpack")
    backpack_img.click()

    assert page.locator('[data-test="inventory-item-name"]').inner_text() == "Sauce Labs Backpack"

    add_btn = page.get_by_role("button", name="Add to cart")
    add_btn.click()

    cart = page.locator('[data-test="shopping-cart-link"]')
    cart.click()

    assert page.locator('[data-test="title"]').inner_text() == "Your Cart"

    checkout_btn = page.get_by_role("button", name="Checkout")
    checkout_btn.click()

    assert page.locator('[data-test="title"]').inner_text() == "Checkout: Your Information"

    page.locator('[data-test="firstName"]').fill("John")
    page.locator('[data-test="lastName"]').fill("Doe")
    page.locator('[data-test="postalCode"]').fill("12345")
    page.get_by_role("button", name="Continue").click()

    assert page.locator('[data-test="title"]').inner_text() == "Checkout: Overview"
    assert page.locator('[data-test="inventory-item-name"]').inner_text() == "Sauce Labs Backpack"

    page.get_by_role("button", name="Finish").click()

    assert page.locator('[data-test="complete-header"]').inner_text() == "Thank you for your order!"

    page.get_by_role("button", name="Back Home").click()

    assert page.url == f"{BASE_URL}inventory.html"

    page.locator("#react-burger-menu-btn").click()
    page.locator('[data-test="logout-sidebar-link"]').click()

    assert page.url == BASE_URL