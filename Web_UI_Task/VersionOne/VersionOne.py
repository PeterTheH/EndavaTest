from playwright.sync_api import sync_playwright, Playwright

# Проверява дали поисканите продукти са в количката
def check_items_in_cart(names, page):
    product_names = names.copy()
    divs = page.locator("div.inventory_item_name")
    for i in range(divs.count()):
        name = divs.nth(i).inner_text()

        if name not in product_names:
            raise AssertionError(f"Item {name} not ordered")

        product_names.remove(name)
    if product_names: # Ако не всички елементи поръчани елементи са намерени
        raise AssertionError(f"Not all items in cart: {product_names}")

def login_with_standard(page):
    usernames = page.inner_text("div#login_credentials").split('\n')[1:-1]  # Намира username, слага ги в лист и премахва стойността на хедъра и празния последен елемент
    passwords = page.inner_text("div.login_password").split('\n')[1]  # В дадения случай паролата е една за всички, ако не е в сила използваме горния метод
    if len(usernames) == 0 or len(passwords) == 0:
        raise AssertionError("username or password are empty")  # Допускаме, че трябва да има валидни данни за влизане в сайта
    page.fill("input#user-name", usernames[0])  # Допускаме, че всички usernames са валидни и избираме първия възможен
    page.fill("input#password", passwords)
    page.click("input#login-button")
    page.wait_for_url("**/inventory.html")

def logout(page):
    page.locator("button#react-burger-menu-btn").click()
    page.locator("a#logout_sidebar_link").click()

def first_scenario(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.goto("https://www.saucedemo.com/")

    login_with_standard(page)

    # Намираме всички възможни продукти, за да извлечем първия и последния
    inventory_div = page.locator("div.inventory_list").locator("> div")

    if (inventory_div.count() == 0):
        raise ValueError("Inventory is empty")

    #Добавяме и двата към количката
    inventory_div.first.locator('button').click()
    inventory_div.last.locator('button').click()

    #Намира имената на поръчаните продукти и ги слага в лист и ги проверява в количката
    names_to_check = [inventory_div.first.locator('div.inventory_item_name').inner_text(), inventory_div.last.locator('div.inventory_item_name').inner_text()]

    page.locator('a.shopping_cart_link').click()
    page.wait_for_url("**/cart.html")
    check_items_in_cart(names_to_check, page)
    page.locator("button#continue-shopping").click()
    page.wait_for_url("**/inventory.html")


    names_to_check.pop(0)
    inventory_div.first.locator("button").click()
    inventory_div.nth(-2).locator("button").click()
    names_to_check.append(inventory_div.nth(-2).locator('div.inventory_item_name').inner_text())

    page.locator('a.shopping_cart_link').click()
    page.wait_for_url("**/cart.html")
    check_items_in_cart(names_to_check, page)
    page.locator("button#continue-shopping").click()
    page.wait_for_url("**/inventory.html")


    page.locator('a.shopping_cart_link').click()
    page.wait_for_url("**/cart.html")
    page.locator('button#checkout').click()
    page.wait_for_url("**/checkout-step-one.html")

    page.fill("input#first-name", "test")
    page.fill("input#last-name", "test")
    page.fill("input#postal-code", "test")
    page.locator('input#continue').click()
    page.wait_for_url("**/checkout-step-two.html")
    check_items_in_cart(names_to_check, page)
    page.locator("button#finish").click()
    page.wait_for_url("**/checkout-complete.html")
    page.locator('button#back-to-products').click()
    page.wait_for_url("**/inventory.html")

    page.locator('a.shopping_cart_link').click()
    page.wait_for_url("**/cart.html")
    check_items_in_cart([], page)
    logout(page)



def second_scenario(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.goto("https://www.saucedemo.com/")

    login_with_standard(page)

    page.locator("select.product_sort_container").select_option(value="hilo")

    divs = page.locator("div.inventory_item_price")
    # създава лист от цените и ги превръща в числа
    prices = [divs.nth(i).inner_text() for i in range(divs.count())]
    prices = [float(p.replace('$', '')) for p in prices]

    if prices != sorted(prices, reverse=True):
        raise ValueError("Prices not in the correct order")
    logout(page)

with sync_playwright() as playwright:
    first_scenario(playwright)
    second_scenario(playwright)