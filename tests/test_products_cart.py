"""Products and Cart module - FR-06 to FR-09."""
import pytest

from pages.cart_page import CartPage
from utils.logger import log_step


@pytest.mark.smoke
@pytest.mark.fr("FR-06")
def test_products_visible_with_name_price_and_button(inventory):
    """FR-06: at least 6 products are listed, each with name, price and Add to cart."""
    products = inventory.get_products()
    log_step(f"{len(products)} products found: {[p['name'] for p in products]}")

    assert len(products) >= 6, f"Expected at least 6 products, found {len(products)}"
    for product in products:
        assert product["name"], "A product has no name"
        assert product["price"] > 0, f"'{product['name']}' has no valid price"
        assert product["button_text"] == "Add to cart", (
            f"'{product['name']}' button reads '{product['button_text']}'"
        )


@pytest.mark.smoke
@pytest.mark.fr("FR-07")
def test_add_to_cart_updates_badge_and_button(inventory):
    """FR-07: adding an item makes the badge show 1 and the button change to Remove."""
    name = inventory.add_to_cart_by_index(0)
    log_step(f"Added '{name}' to the cart")

    assert inventory.wait_for_cart_count(1), f"Cart badge shows {inventory.cart_count()}, expected 1"
    assert inventory.wait_for_button_text(name, "Remove"), "Button did not change to 'Remove'"


@pytest.mark.regression
@pytest.mark.fr("FR-07")
def test_add_multiple_items_increments_badge(inventory):
    """FR-07: the badge increments by 1 for every item added."""
    names = [inventory.add_to_cart_by_index(i) for i in range(3)]
    log_step(f"Added three items: {names}")

    assert inventory.wait_for_cart_count(3), f"Cart badge shows {inventory.cart_count()}, expected 3"
    for name in names:
        assert inventory.wait_for_button_text(name, "Remove"), f"'{name}' button is not 'Remove'"


@pytest.mark.regression
@pytest.mark.fr("FR-08")
def test_remove_item_clears_badge_and_restores_button(inventory):
    """FR-08: removing the only added item empties the badge and restores Add to cart."""
    name = inventory.add_to_cart_by_index(0)
    assert inventory.wait_for_cart_count(1), "Precondition failed: badge did not reach 1"

    inventory.remove_from_cart(name)
    log_step(f"Removed '{name}'")

    assert inventory.wait_for_cart_count(0), f"Cart badge shows {inventory.cart_count()}, expected none"
    assert inventory.wait_for_button_text(name, "Add to cart"), "Button did not revert to 'Add to cart'"


@pytest.mark.regression
@pytest.mark.fr("FR-08")
def test_remove_one_of_two_items_decrements_badge(inventory):
    """FR-08: with two items in the cart, removing one leaves the badge at 1."""
    first = inventory.add_to_cart_by_index(0)
    second = inventory.add_to_cart_by_index(1)
    assert inventory.wait_for_cart_count(2), "Precondition failed: badge did not reach 2"

    inventory.remove_from_cart(first)
    log_step(f"Removed '{first}', kept '{second}'")

    assert inventory.wait_for_cart_count(1), f"Cart badge shows {inventory.cart_count()}, expected 1"
    assert inventory.wait_for_button_text(first, "Add to cart")
    assert inventory.wait_for_button_text(second, "Remove")


@pytest.mark.regression
@pytest.mark.fr("FR-09")
def test_cart_lists_selected_items_with_matching_name_and_price(inventory, driver):
    """FR-09: the Cart shows the chosen items with the same names and prices as Products."""
    catalogue = {p["name"]: p["price"] for p in inventory.get_products()}
    chosen = [inventory.add_to_cart_by_index(0), inventory.add_to_cart_by_index(2)]
    expected = sorted((name, catalogue[name]) for name in chosen)
    log_step(f"Selected on Products page: {expected}")

    inventory.open_cart()
    cart = CartPage(driver)
    assert cart.is_loaded(), "Cart page did not open"
    actual = sorted((item["name"], item["price"]) for item in cart.get_items())
    log_step(f"Listed on Cart page: {actual}")

    assert actual == expected, f"Cart contents {actual} differ from selection {expected}"
