from selenium import webdriver
from selenium.webdriver.common.by import By


def test_eight_components():
    driver = webdriver.Chrome('./chromedriver')

    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    title = driver.title
    # print("Title: ", title)
    assert title == "Web form"

    driver.implicitly_wait(0.5)

    text_box = driver.find_element(by=By.NAME, value="my-text")
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

    text_box.send_keys("Selenium")
    submit_button.click()

    message = driver.find_element(by=By.ID, value="message")
    value = message.text
    assert value == "Received!"

    print('Title: ', title, "\nValue:\n", value)

    #driver.quit()

if __name__ == '__main__':
    test_eight_components()