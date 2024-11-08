from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import yaml
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EcommerceBooking:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        service = Service('./drivers/chromedriver.exe')
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def load_config(self, path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)

    def login(self):
        credentials = self.config['credentials']
        self.driver.get("http://www.automationpractice.pl/index.php?controller=authentication")

        try:
            # Enter email
            email_input = self.driver.find_element(By.ID, "email")
            email_input.send_keys(credentials['username'])

            # Enter password
            password_input = self.driver.find_element(By.ID, "passwd")
            password_input.send_keys(credentials['password'])

            # Re-locate the sign-in button just before clicking
            sign_in_button = self.driver.find_element(By.ID,"SubmitLogin")
            self.wait.until(
                EC.element_to_be_clickable((By.ID, "SubmitLogin"))
            )
            sign_in_button.click()

            self.driver.refresh()
            logger.info("Logged in successfully.")
            
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            raise

    def filter_and_list_products(self, filters):
        """
        Apply filters and list all available products.

        :param filters: Dictionary containing filter criteria.
                        Example:
                        {
                            'category': 'Women',
                            'size': 'M',
                            'color': 'Blue'
                        }
        """
        self.filters = filters
        try:
            # Apply category filter
            if 'category' in filters:
                category = filters['category']
                category_element = self.wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, category))
                )
                category_element.click()
                logger.info(f"Applied category filter: {category}")
            
            # Apply size filter
            if 'size' in filters:
                size = filters['size']
                size_id = self.get_size_id(size)
                if size_id:
                    size_element = self.driver.find_element(By.ID, f'layered_id_attribute_group_{size_id}')
                    size_element.click()
                    logger.info(f"Applied size filter: {size}")
                else:
                    logger.warning(f"Size '{size}' not found in size mapping.")
            
            # Apply color filter
            if 'color' in filters:
                color = filters['color']
                color_id = self.get_color_id(color)
                if color_id:
                    color_element = self.driver.find_element(By.ID, f'layered_id_attribute_group_{color_id}')
                    color_element.click()
                    logger.info(f"Applied color filter: {color}")
                else:
                    logger.warning(f"Color '{color}' not found in color mapping.")
            
            # Wait for the filter results to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.product_list'))
            )
            time.sleep(2)  # Optional: wait for additional loading

            # Retrieve and display all available products
            products = self.driver.find_elements(By.CSS_SELECTOR, 'ul.product_list > li.ajax_block_product')
            print(f"Total available products after applying filters: {len(products)}")
            for idx, product in enumerate(products, start=1):
                product_name = product.find_element(By.CSS_SELECTOR, '.product-name').text
                product_price = product.find_element(By.CSS_SELECTOR, '.price').text
                print(f"{idx}. {product_name} - {product_price}")
        
        except Exception as e:
            logger.error(f"Error in filter_and_list_products: {e}", exc_info=True)
            raise

    def get_size_id(self, size):
        """
        Map size name to its corresponding ID used in the filter.

        :param size: Size name as in filter (e.g., 'S', 'M', 'L').
        :return: ID suffix for the size or None if not found.
        """
        size_mapping = {
            'S': '1',
            'M': '2',
            'L': '3'
        }
        return size_mapping.get(size.upper())

    def get_color_id(self, color):
        """
        Map color name to its corresponding ID used in the filter.

        :param color: Color name as in filter (e.g., 'Blue', 'Orange').
        :return: ID suffix for the color or None if not found.
        """
        color_mapping = {
            'Beige': '7',
            'White': '8',
            'Black': '11',
            'Orange': '13',
            'Blue': '14',
            'Green': '15',
            'Yellow': '16',
            'Pink': '24',
            'Brown': '30',
            'Gray': '35'
        }
        return color_mapping.get(color.capitalize())
    
    def pick_first_product(self):
        products = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-container .product-name"))
        )
        products[0].click()
        # apply filters and customize product
        self.customize_and_add_to_cart()



    def customize_and_add_to_cart(self):
        
        filters = self.filters
        details = self.config['booking_details']
        # Select size
        size_select = Select(self.wait.until(
            EC.presence_of_element_located((By.ID, "group_1"))
        ))
        size_select.select_by_visible_text(filters['size'])

        # Select color if available
        if filters.get('color'):
            color = filters['color'].lower()
            color_elements = self.driver.find_elements(By.CSS_SELECTOR, "#color_to_pick_list li a")
            for elem in color_elements:
                color_name = elem.get_attribute("name").lower()
                if color == color_name:
                    elem.click()
                    break
        # refresh page
        self.driver.refresh()
        # Set quantity
        quantity_wanted = self.driver.find_element(By.ID, "quantity_wanted")
        quantity_wanted.clear()
        quantity_wanted.send_keys(str(details['quantity']))

        # Add to cart
        add_to_cart_button = self.driver.find_element(By.NAME, "Submit")
        add_to_cart_button.click()

        # Wait for confirmation modal
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "layer_cart"))
        )
        logger.info("Added to cart successfully.")

    
    def proceed_to_checkout(self):
        # Click on 'Proceed to checkout' in the modal
        proceed_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@title='Proceed to checkout']"))
        )
        proceed_button.click()
        
        # Summary Page: Proceed to checkout
        summary_proceed = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//p[@class='cart_navigation clearfix']/a[@title='Proceed to checkout']"))
        )
        summary_proceed.click()
        
        # Address Page: Proceed to checkout
        address_proceed = self.wait.until(
            EC.element_to_be_clickable((By.NAME, "processAddress"))
        )
        address_proceed.click()
        
        # Shipping Page: Agree to terms and proceed
        terms_checkbox = self.wait.until(
            EC.element_to_be_clickable((By.ID, "cgv"))
        )
        terms_checkbox.click()
        
        shipping_proceed = self.driver.find_element(By.NAME, "processCarrier")
        shipping_proceed.click()
        
        # Payment Page: Choose payment method (e.g., Pay by bank wire)
        pay_by_bank = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "bankwire"))
        )
        pay_by_bank.click()
        
        # Confirm Order
        confirm_order_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']/span[contains(text(), 'I confirm my order')]"))
        )
        confirm_order_button.click()
        
        # Verify Order Completion
        confirmation = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cheque-indent strong"))
        )
        if "Your order on My Store is complete." in confirmation.text:
            print("Order completed successfully.")
        else:
            print("Order completion failed.")

    

    def close_browser(self):
        self.driver.quit() 