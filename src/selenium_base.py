from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By

import undetected_chromedriver as uc
from time import sleep

from src.classes import Item


def parse():
    driver = uc.Chrome(use_subprocess=True)
    driver.delete_all_cookies()

    driver.get("https://smartytitans.com/live/research")
    sleep(2)

    driver.find_element(By.XPATH, '//button[@class="p-button-success w-full button-find p-ripple p-button p-component"]').click()
    sleep(3)
    with open("selenium_site.txt", "a") as f:
        scrollable_element = driver.find_element(By.XPATH, '//div[@class="p-datatable-wrapper"]')
        number_of_elements = driver.find_element(By.XPATH,
                                                 '//div[@class="p-d-flex p-ai-center p-jc-between ng-star-inserted"]').text
        number_of_elements = int([int(i) for i in number_of_elements.split() if i.isdigit()][0])

        size_of_element = scrollable_element.size['height']
        list_of_elements = []
        for _ in range(int(number_of_elements/7)):
            item_classes_list = []
            matched_elements = driver.find_elements(By.XPATH, "//tbody/tr/td")
            matched_elements_classes = driver.find_elements(By.XPATH, "//tbody/tr")
            for element in matched_elements_classes:
                if element.get_attribute("class").find('superior') != -1:
                    item_class = 'Uncommon'
                elif element.get_attribute("class").find('legendary') != -1:
                    item_class = 'Legendary'
                elif element.get_attribute("class").find('epic') != -1:
                    item_class = 'Epic'
                elif element.get_attribute("class").find('flawless') != -1:
                    item_class = 'Rare'
                else:
                    item_class = 'Common'
                item_classes_list.append(item_class)

            elmnts = matched_elements
            visible_item_counter = 0
            for i in range(0, len(elmnts), 11):
                item = Item(elmnts[i].text, elmnts[i + 1].text, elmnts[i + 2].text, elmnts[i + 3].text,
                            elmnts[i + 4].text, elmnts[i + 5].text, elmnts[i + 6].text,
                            elmnts[i + 7].text, elmnts[i + 8].text, elmnts[i + 9].text,
                            item_classes_list[visible_item_counter])

                list_of_elements.append(item)
                f.write(f'{item.__str__()}\n')
                visible_item_counter += 1

            scroll_origin = ScrollOrigin.from_element(scrollable_element)
            ActionChains(driver)\
                .scroll_from_origin(scroll_origin, 0, size_of_element)\
                .perform()

            sleep(0.1)

    driver.close()
