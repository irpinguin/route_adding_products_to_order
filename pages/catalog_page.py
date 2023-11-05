import random
import re
import time

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from base.links import Links
from base.base_page import BasePage


# from pages.product_page import ProductPage


class CatalogPage(BasePage):
    PAGE_URL = Links.CATALOG_PAGE
    BRANDS_SAMPLE_QTY = 100

    # Locators
    CATALOG_MENU_LOC = '//a[@id="catalog-btn"]'
    CATALOG_SIGN_LOC = '//section[@class="catalog container"]/div[2]/div[1]/nav/ol/li[2]/span'
    CATALOG_SIGN_VAL = "Каталог"
    FILTER_BTN_LOC = '//section[@class="catalog container"]/div[2]/div[2]/button'
    FILTER_SIGN_LOC = FILTER_BTN_LOC
    FILTER_SIGN_VAL = 'Закрыть фильтр'
    FILTER_APPLY_BTN_LOC = '//button[@class="btn-block btn-success btn do-filter"]'

    FILTER_BRAND_BTN_LOC = '//button[@id="dropdown-filter_manufacturer_and_brands_select"]'
    FILTER_BRAND_SEARCH_FLD_LOC = f'{FILTER_BRAND_BTN_LOC}/following-sibling::div/div/input'
    FILTER_BRAND_SIGN_LOC = FILTER_BRAND_SEARCH_FLD_LOC
    FILTER_BRAND_SIGN_VAL = 'Поиск'
    FILTER_BRAND_UL = '/following-sibling::div/ul[@class="dropdown-menu inner"]'
    FILTER_BRAND_LI = f'{FILTER_BRAND_BTN_LOC}{FILTER_BRAND_UL}/li[@class="lvl-2"]'

    PAGE_PER_PAGE_360_LOC = '//div[@id="catalog-content"]/div/div[3]/form/select/option[6]'

    CATALOG_ITEM_LOC = '//div[@id="catalog-content"]/div[3]/div'
    CATALOG_ITEM_PRODUCT_ID_2_LOC = '/div/div[3]/div/a'
    CATALOG_ITEM_PRODUCT_NAME_2_LOC = '/div/div[2]/a'
    CATALOG_ITEM_PRODUCT_PRICE_SPEC_LOC = '//span[@class="price"]'
    CATALOG_ITEM_PRODUCT_SPECIAL_PRICE_SIGN_LOC = '//i[@class="prop-special-price fa fa-fw"]'

    PRODUCT_PAGE_MANUFACTURER_NAME_LOC = '//table[@class="table table-condensed"]/tbody/tr[1]/td/a'
    PRODUCT_PAGE_COUNTRY_NAME_LOC = '//table[@class="table table-condensed"]/tbody/tr[3]/td/a'

    #
    # Getters
    #
    def get_catalog_page(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.CATALOG_MENU_LOC)))

    def get_catalog_page_sign(self):
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, self.CATALOG_SIGN_LOC)))

    def get_filter_btn(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.FILTER_BTN_LOC)))

    def get_filter_sign(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.FILTER_SIGN_LOC)))

    def get_filter_apply_btn(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.FILTER_APPLY_BTN_LOC)))

    def get_filter_brand_btn(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.FILTER_BRAND_BTN_LOC)))

    def get_filter_brand_search_fld(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.FILTER_BRAND_SEARCH_FLD_LOC)))

    def get_filter_brand_product_qty(self, brand_name):
        btn = self.get_filter_apply_btn()
        match = re.search(r'\((\d+)\)', btn.text)
        if match:
            product_qty = int(match.group(1))
            if product_qty > 0:
                print(f"\t- Number of products selected for the brand '{brand_name}': {product_qty}")
            elif product_qty == 0:
                print(f"\t- Products of the brand {brand_name} are not available for sale.")
        else:
            product_qty = None
            print(f"\t- For the brand {brand_name}, the 'Применить' button does not show the number "
                  f"of selected products.")
        return product_qty

    def get_products_per_page(self):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, self.PAGE_PER_PAGE_360_LOC)))

    def get_filter_state(self):
        btn = self.get_filter_btn()
        btn_state = btn.get_attribute('aria-pressed')
        if btn_state == "false":
            return False
        return True

    def get_catalog_item_special_price_flag(self, catalog_item_element, catalog_item_locator):
        # получаем признак наличия специальной цены
        try:
            catalog_item_element.find_element(By.XPATH, catalog_item_locator)
            product_special_price_flag = True
        except NoSuchElementException:
            product_special_price_flag = False
        return product_special_price_flag

    def get_catalog_content_items(self):

        products = []

        catalog_items = self.driver.find_elements(By.XPATH, self.CATALOG_ITEM_LOC)

        # для каждого элемента каталога
        for i in range(len(catalog_items)):
            product = {}

            # получаем product_id
            locator = f'{self.CATALOG_ITEM_LOC}[{i + 1}]{self.CATALOG_ITEM_PRODUCT_ID_2_LOC}'
            product_id = catalog_items[i].find_element(By.XPATH, locator).get_attribute("data-element-id")
            product['product_id'] = product_id

            # получаем Наименование товара
            locator = f'{self.CATALOG_ITEM_LOC}[{i + 1}]{self.CATALOG_ITEM_PRODUCT_NAME_2_LOC}'
            product_name = catalog_items[i].find_element(By.XPATH, locator)
            product['name'] = product_name.text

            # получаем признак наличия специальной цены
            locator = f'{self.CATALOG_ITEM_LOC}[{i + 1}]{self.CATALOG_ITEM_PRODUCT_SPECIAL_PRICE_SIGN_LOC}'
            product_special_price_flag = self.get_catalog_item_special_price_flag(catalog_items[i], locator)
            product['is_special_price'] = product_special_price_flag

            # получаем цену, если есть специальная цена, то данные по цене находятся по другому XPath
            if product_special_price_flag:
                locator = f'{self.CATALOG_ITEM_LOC}[{i + 1}]{self.CATALOG_ITEM_PRODUCT_PRICE_SPEC_LOC}'
            else:
                locator = f'{self.CATALOG_ITEM_LOC}[{i + 1}]{self.CATALOG_ITEM_PRODUCT_ID_2_LOC}'
            product_price = catalog_items[i].find_element(By.XPATH, locator)
            product['price'] = product_price.text

            products.append(product)

        return products

    #
    # Actions
    #
    def open_catalog_page(self):
        self.get_catalog_page().click()
        print("\tOn Catalog page the link to the Catalog page is clicked")

    def set_qty_products_per_page(self):
        # Для упрощения, пока устанавливаем 360 товаров на страницу и смотрим-обрабатываем только первую страницу
        self.get_products_per_page().click()

    def filter_open(self):
        filter_status = self.get_filter_state()
        if filter_status:
            print("\tThe filter is already open.")
        else:
            self.get_filter_btn().click()
            print("\tOn Catalog page the open filter button is clicked.")
        # TODO: разобраться с ожиданием
        time.sleep(self.TIMEOUT)
        sign = self.get_filter_sign()
        self.assert_sign("Verifying that the filter is open", sign, self.FILTER_SIGN_VAL)

    def filter_brand_open(self):
        self.get_filter_brand_btn().click()
        print("\tFilter Brand button is clicked.")

        # assert
        print("\t- Verifying that the filter Brand is open: ", end='')
        assert self.get_filter_brand_search_fld().get_attribute('placeholder') == self.FILTER_BRAND_SIGN_VAL
        print("OK.")

    def select_random_brand(self):
        locator = f'{self.FILTER_BRAND_LI}[{random.randint(1, self.BRANDS_SAMPLE_QTY + 1)}]/a'
        brand = self.driver.find_element(By.XPATH, locator)
        # brand_id = brand.get_attribute('data-id')
        brand_name = brand.text
        print(f"\tFrom the first {self.BRANDS_SAMPLE_QTY} brands, random brand was chosen: {brand_name}.")
        return brand_name

    def filter_brand_select(self, brand_name):
        locator = f'{self.FILTER_BRAND_LI}/a[text()="{brand_name}"]'
        self.get_filter_brand_search_fld().send_keys(brand_name)
        # time.sleep(self.TIMEOUT)
        element = self.driver.find_element(By.XPATH, locator)
        # time.sleep(self.TIMEOUT)
        element.click()
        print(f"\tBrand filter applied: {brand_name}.")

    def filter_brand_apply(self):
        self.get_filter_apply_btn().click()
        print("\tThe 'Применить' button is clicked.")

    # TODO: как можно получать сюда данные, которые собираются в другом классе
    #   для каждого вебэлемента надо выдернуть ид продукта и передать его в класс страницы продукта,
    #   и получить обратно словарь значений свойств товара
    #   неплохо также где-то список этих словарей хранить для последующего использования
    def get_data_from_product_page(self, product_id):

        PRODUCT_NAME_LOC = '//h1'
        TABLE_LOC = '//table[@class="table table-condensed"]'
        MANUFACTURER_NAME_LOC = f'{TABLE_LOC}/tbody/tr[1]/td/a'
        BRAND_NAME_LOC = f'{TABLE_LOC}/tbody/tr[2]/td/a'
        COUNTRY_NAME_LOC = f'{TABLE_LOC}/tbody/tr[3]/td/a'
        COLOR_NAME_LOC = f'{TABLE_LOC}/tbody/tr[4]//input[@class="package-color"]'
        ACTION_SIGN_LOC = '//div[@class="element-actions alert alert-warning mb-0 mt-20"]/div'
        ACTION_TEXT = "Этот товар участвует в акци"
        PRICE_LOC = '//div[@class="panel-body text-center"]/div/span'

        product = {}

        # проверяем, что находимся на странице нужного товара
        get_url = self.driver.current_url
        expected_url = f"{Links.CATALOG_PAGE}i{product_id}/"
        assert get_url == expected_url

        # получаем данные о свойствах товара
        product['product_id'] = product_id
        product['name'] = self.wait.until(EC.element_to_be_clickable((By.XPATH, PRODUCT_NAME_LOC))).text
        product['manufacturer'] = self.wait.until(EC.element_to_be_clickable((By.XPATH, MANUFACTURER_NAME_LOC))).text
        product['brand'] = self.wait.until(EC.element_to_be_clickable((By.XPATH, BRAND_NAME_LOC))).text
        # элемент присутствует на странице товара только если товар участвует в акции и у него есть спеццена
        try:
            action_sign = self.wait.until(EC.visibility_of_element_located((By.XPATH, ACTION_SIGN_LOC))).text
            if ACTION_TEXT in action_sign:
                product['is_special_price'] = True
        except TimeoutException:
            product['is_special_price'] = False

        product['country'] = self.wait.until(EC.element_to_be_clickable((By.XPATH, COUNTRY_NAME_LOC))).text
        product['color'] = self.wait.until(EC.visibility_of_element_located((By.XPATH, COLOR_NAME_LOC))).accessible_name
        product['price'] = self.wait.until(EC.element_to_be_clickable((By.XPATH, PRICE_LOC))).text

        return product

    def get_catalog_content_items_data_from_product(self, products):
        i = 0
        products_from_product_pages = []
        # time.sleep(self.TIMEOUT)

        for i in range(len(products)):
            # переходим на страницу товара
            self.driver.get(f"{self.PAGE_URL}i{products[i]['product_id']}")
            # time.sleep(self.TIMEOUT)
            product = self.get_data_from_product_page(products[i]['product_id'])
            # print(f'{i+1}. product data: {product}')
            products_from_product_pages.append(product)
            self.driver.back()
            # time.sleep(self.TIMEOUT/2)
        return products_from_product_pages

    def clear_filter(self):
        # TODO: проверить, что фильтр установлен, если да, то найти Сброс фильтра и его нажать
        #    проверить, что фильтр сброшен
        pass

    def set_sorting_novelty(self):
        pass

    def set_sorting_popularity(self):
        pass

    #
    # Methods
    #
    def health_check(self):
        print("Verifying that the Catalog page is opened correctly.")
        self.assert_page_url()
        self.assert_sign("Verifying that the Catalog page is open",
                         self.get_catalog_page_sign(), self.CATALOG_SIGN_VAL)

    def filter_brand_route(self):
        print("Verify that the brand filter in the catalog is working correctly.")
        self.filter_brand_open()
        # TODO убрать фиксированный бренд
        # brand_name = self.select_random_brand()
        brand_name = "Old Spice"
        self.filter_brand_select(brand_name)
        # после выбора бренда и до применения фильтра на кнопке "Применить" отображается количество товаров в фильтре
        # после того, как фильтр применили, количество товаров на кнопке "Применить" уже не отображается
        filter_brand_product_qty = self.get_filter_brand_product_qty(brand_name)
        self.filter_brand_apply()
        self.set_qty_products_per_page()

        # self.get_catalog_content_items()
        assert self.get_filter_brand_btn().text == brand_name
        print(f"\t- The button displays the name of the expected brand: {brand_name}.")

        catalog_content_items = self.get_catalog_content_items()
        # print(f'\ncatalog_content_items:\n{catalog_content_items}\n')

        # в содержании каталога есть не вся информация о товаре, поэтому
        # для каждого представленного товара ходим на страницу товара и там получаем полные данные
        catalog_content_items_data_from_product = self.get_catalog_content_items_data_from_product(catalog_content_items)
        # print(f'\ncatalog_content_items_data_from_product:\n{catalog_content_items_data_from_product}\n')

        # проверяем, что количество отобранных товаров совпадает со значением, которое было на кнопке "Применить"
        catalog_content_items_qty = len(catalog_content_items)
        assert filter_brand_product_qty == catalog_content_items_qty
        print(f"\t- The number of products selected in the brand filter: {filter_brand_product_qty} "
              f"is the same as the number of products in the catalog content: {catalog_content_items_qty}.")

        # проверяем, что в содержимом отфильтрованного каталога нет товаров других брендов
        for product in catalog_content_items_data_from_product:
            assert product['brand'] == brand_name
        print(f'\t- In the content of the filtered catalog, there are only products of the selected brand: {brand_name}')

        # проверяем, что количество товаров со спецценой одинаковое на странице товаров и по данным со страниц товаров
        catalog_content_items_with_special_price = 0
        catalog_content_items_data_from_product_with_special_price = 0

        for product in catalog_content_items:
            if product['is_special_price']:
                catalog_content_items_with_special_price += 1
        for product in catalog_content_items_data_from_product:
            if product['is_special_price']:
                catalog_content_items_data_from_product_with_special_price += 1
        assert catalog_content_items_with_special_price == catalog_content_items_data_from_product_with_special_price
        print(f"\t- The number of products with a special price is the same on the product page: "
              f"{catalog_content_items_with_special_price} and according to the data from the product pages: "
              f"{catalog_content_items_data_from_product_with_special_price}")

        # проверяем, что цены для товаров одинаковы на странице каталога и на странице продукта
        diff = []
        for catalog_content_product, product_from_page in zip(
                catalog_content_items, catalog_content_items_data_from_product):
            if catalog_content_product['price'] != product_from_page['price']:
                diff.append(f"Difference in price for the product {catalog_content_product['name']}: "
                            f"{catalog_content_product['price']} != {product_from_page['price']}")
        assert not diff, f"The following price differences were found:\n{', '.join(diff)}"
        print("\t- For all items in the filtered catalog, the price is the same as the price on the product page.")
