from playwright.sync_api import sync_playwright, Playwright
import sys

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

def first_scenario(playwright: Playwright, platform, enviroment):
    browser = platform.launch()
    page = browser.new_page()
    page.goto(enviroment)

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

    #Премахва първия елемент и добява предпоследния към количката, след което проверява
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



def second_scenario(playwright: Playwright, platform, enviroment):
    browser = platform.launch()
    page = browser.new_page()
    page.goto(enviroment)

    login_with_standard(page)

    page.locator("select.product_sort_container").select_option(value="hilo")

    # създава лист от цените и ги превръща в числа
    divs = page.locator("div.inventory_item_price")
    prices = [divs.nth(i).inner_text() for i in range(divs.count())]
    prices = [float(p.replace('$', '')) for p in prices]

    if prices != sorted(prices, reverse=True):
        raise ValueError("Prices not in the correct order")
    logout(page)

def get_browser():
    if len(sys.argv) > 1:
        platform = sys.argv[1]
        if platform == "chromium":
            platform = playwright.chromium
        elif platform == "firefox":
            platform = playwright.firefox
    else:
        print("No platform inputted. Using default")
        platform = playwright.chromium

    return platform

def get_enviroment():
    # за различните възможности добавяме един сайт само като пример
    enviroment = {
    "prod": "https://www.saucedemo.com/",
    "dev": "https://www.saucedemo.com/",
    "staging": "https://www.saucedemo.com/",
}
    if len(sys.argv) > 2:
        return enviroment[sys.argv[2]]
    else:
        print("No enviroment inputted. Using default")
        return enviroment["prod"]


tests = {
    "first_scenario": first_scenario,
    "second_scenario": second_scenario
}

# Тестването на кода се случва чрез python VersionTwo {platform} {Желани тестове}
if __name__ == "__main__":
    test_results = []
    with sync_playwright() as playwright:
        # Намира избран браузър, използван за извикване на тестовете
        platform = get_browser()
        # Намира избран enviroment за извикване на функциите
        enviroment = get_enviroment()

        # Намира избрани тестове при започване на кода и извиква функциите
        selected_tests = sys.argv[3:]
        if not selected_tests:
            print("Running all tests.")
            for name, test in tests.items():
                try:
                    test(playwright, platform, enviroment)
                    test_results.append((name, "Passed"))
                except Exception as e:
                    print(f"Test {name} failed: {e}")
                    test_results.append((name, f"Failed: {e}"))
        else:
            print(f"Running selected tests: {selected_tests}")
            for name in selected_tests:
                if name in tests:
                    try:
                        tests[name](playwright, platform, enviroment)
                        test_results.append((name, "Passed"))
                    except Exception as e:
                        print(f"Test {name} failed: {e}")
                        test_results.append((name, f"Failed: {e}"))
                else:
                    print(f"Unknown test: {name}")
                    test_results.append((name, "Unknown Test"))

    html_content = "<html><body><h1>Test Report</h1>"

    for name, result in test_results:
        html_content += f"<li>{name}: {result}</li>"

    html_content += "</body></html>"

    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Test report generated: test_report.html")