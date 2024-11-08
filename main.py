#%%
from modules.ecommerce_booking import EcommerceBooking

def main():
    booking = EcommerceBooking(config_path='config/config.yaml')
    try:
        filters=dict(category="Women", size="M", color="Pink")
        booking.login()
        booking.filter_and_list_products(filters)
        booking.search_and_select_product()
        booking.customize_and_add_to_cart()
        booking.proceed_to_checkout()
        print("Purchase automation completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    # finally:
    #     booking.close_browser()
#%%
if __name__ == "__main__":
    main()
