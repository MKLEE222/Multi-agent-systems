"""Fixed public tau2 source excerpts; no benchmark database or task labels.

Function/method bodies are copied verbatim. Only @is_tool decorators and the
ToolKitBase base/initialization (registration machinery) are omitted. Data model
classes are copied from the same commit. This is a source-body native verifier,
not the full tau2 environment, agent, policy, or official evaluator.
"""
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class Variant(BaseModel):
    """Represents a specific variant of a product with its options, availability and price"""

    item_id: str = Field(description="Unique identifier for the variant")
    options: Dict[str, str] = Field(
        description="Dictionary of option names to values (e.g. {'color': 'blue', 'size': 'large'})"
    )
    available: bool = Field(description="Whether this variant is currently in stock")
    price: float = Field(description="Price of this variant")

class Product(BaseModel):
    """Represents a product with its variants"""

    name: str = Field(description="Name of the product")
    product_id: str = Field(description="Unique identifier for the product")
    variants: Dict[str, Variant] = Field(
        description="Dictionary of variants indexed by variant ID"
    )

class UserName(BaseModel):
    """Represents a user's full name"""

    first_name: str = Field(description="User's first name")
    last_name: str = Field(description="User's last name")

class UserAddress(BaseModel):
    """Represents a physical address"""

    address1: str = Field(description="Primary address line")
    address2: str = Field(description="Secondary address line")
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    state: str = Field(description="State or province name")
    zip: str = Field(description="Postal code")

class PaymentMethodBase(BaseModel):
    source: str = Field(description="Type of payment method")
    id: str = Field(description="Unique identifier for the payment method")

class CreditCard(PaymentMethodBase):
    source: Literal["credit_card"] = Field(
        description="Indicates this is a credit card payment method"
    )
    brand: str = Field(description="Credit card brand (e.g., visa, mastercard)")
    last_four: str = Field(description="Last four digits of the credit card")

class Paypal(PaymentMethodBase):
    source: Literal["paypal"] = Field(
        description="Indicates this is a paypal payment method"
    )

class GiftCard(PaymentMethodBase):
    source: Literal["gift_card"] = Field(
        description="Indicates this is a gift card payment method"
    )
    balance: float = Field(description="Gift card value amount")
    id: str = Field(description="Unique identifier for the gift card")

PaymentMethod = Union[CreditCard, GiftCard, Paypal]

class User(BaseModel):
    """Represents a user with their personal information, payment methods and order history"""

    user_id: str = Field(description="Unique identifier for the user")
    name: UserName = Field(description="User's full name")
    address: UserAddress = Field(description="User's primary address")
    email: str = Field(description="User's email address")
    payment_methods: Dict[str, PaymentMethod] = Field(
        description="Dictionary of payment methods indexed by payment method ID"
    )
    orders: List[str] = Field(description="List of order IDs associated with this user")

class OrderFullfilment(BaseModel):
    """Represents the fulfillment details for items in an order"""

    tracking_id: list[str] = Field(description="List of tracking IDs for shipments")
    item_ids: list[str] = Field(
        description="List of item IDs included in this fulfillment"
    )

class OrderItem(BaseModel):
    """Represents an item in an order"""

    name: str = Field(description="Name of the product")
    product_id: str = Field(description="ID of the product")
    item_id: str = Field(description="ID of the specific variant")
    price: float = Field(description="Price of the item at time of purchase")
    options: Dict[str, str] = Field(description="Options selected for this item")

OrderPaymentType = Literal["payment", "refund"]

class OrderPayment(BaseModel):
    """Represents a payment or refund transaction for an order"""

    transaction_type: OrderPaymentType = Field(
        description="Type of transaction (payment or refund)"
    )
    amount: float = Field(description="Amount of the transaction")
    payment_method_id: str = Field(description="ID of the payment method used")

OrderStatus = Literal[
    "processed",
    "pending",
    "pending (item modified)",
    "delivered",
    "cancelled",
    "exchange requested",
    "return requested",
]

CancelReason = Literal["no longer needed", "ordered by mistake"]

class Order(BaseModel):
    """Represents an order with its items, status, fulfillment and payment details"""

    order_id: str = Field(description="Unique identifier for the order")
    user_id: str = Field(description="Unique identifier for the user")
    address: UserAddress = Field(description="Address of the user")
    items: List[OrderItem] = Field(description="Items in the order")
    status: OrderStatus = Field(description="Status of the order")
    fulfillments: List[OrderFullfilment] = Field(
        description="Fulfillments of the order"
    )
    payment_history: List[OrderPayment] = Field(description="Payments of the order")
    cancel_reason: Optional[CancelReason] = Field(
        description="Reason for cancelling the order. Should be 'no longer needed' or 'ordered by mistake'",
        default=None,
    )
    exchange_items: Optional[List[str]] = Field(
        description="Items to be exchanged", default=None
    )
    exchange_new_items: Optional[List[str]] = Field(
        description="Items exchanged for", default=None
    )
    exchange_payment_method_id: Optional[str] = Field(
        description="Payment method ID for the exchange", default=None
    )
    exchange_price_difference: Optional[float] = Field(
        description="Price difference for the exchange", default=None
    )
    return_items: Optional[List[str]] = Field(
        description="Items to be returned", default=None
    )
    return_payment_method_id: Optional[str] = Field(
        description="Payment method ID for the return", default=None
    )

class NativeRetailTools:
    def __init__(self, db):
        self.db = db

    def _get_order(self, order_id: str) -> Order:
        """Get the order from the database.

        Args:
            order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.

        Returns:
            The order.

        Raises:
            ValueError: If the order is not found.
        """
        if order_id not in self.db.orders:
            raise ValueError("Order not found")
        return self.db.orders[order_id]

    def _get_user(self, user_id: str) -> User:
        """Get the user from the database.

        Args:
            user_id: The user id, such as 'sara_doe_496'.

        Returns:
            The user.

        Raises:
            ValueError: If the user is not found.
        """
        if user_id not in self.db.users:
            raise ValueError("User not found")
        return self.db.users[user_id]

    def _get_product(self, product_id: str) -> Product:
        """Get the product from the database.

        Args:
            product_id: The product id, such as '6086499569'. Be careful the product id is different from the item id.

        Returns:
            The product.

        Raises:
            ValueError: If the product is not found.
        """
        if product_id not in self.db.products:
            raise ValueError("Product not found")
        return self.db.products[product_id]

    def _get_variant(self, product_id: str, variant_id: str) -> Variant:
        """Get the variant from the database.

        Args:
            product_id: The product id, such as '6086499569'. Be careful the product id is different from the item id.
            variant_id: The variant id, such as '1008292230'.

        Returns:
            The variant.

        Raises:
            ValueError: If the variant is not found.
        """
        product = self._get_product(product_id)
        if variant_id not in product.variants:
            raise ValueError("Variant not found")
        return product.variants[variant_id]

    def _get_payment_method(
        self, user_id: str, payment_method_id: str
    ) -> PaymentMethod:
        """Get the payment method from the database.

        Args:
            payment_method_id: The payment method id, such as 'gift_card_0000000' or 'credit_card_0000000'.

        Returns:
            The payment method.

        Raises:
            ValueError: If the payment method is not found.
        """
        user = self._get_user(user_id)
        if payment_method_id not in user.payment_methods:
            raise ValueError("Payment method not found")
        return user.payment_methods[payment_method_id]

    def get_order_details(self, order_id: str) -> Order:
        """Get the status and details of an order.

        Args:
            order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.

        Returns:
            Order: The order details.

        Raises:
            ValueError: If the order is not found.
        """
        order = self._get_order(order_id)
        return order

    def get_product_details(self, product_id: str) -> Product:
        """Get the inventory details of a product.

        Args:
            product_id: The product id, such as '6086499569'. Be careful the product id is different from the item id.

        Returns:
            Product: The product details.

        Raises:
            ValueError: If the product is not found.
        """
        product = self._get_product(product_id)
        return product

    def get_user_details(self, user_id: str) -> User:
        """Get the details of a user, including their orders.

        Args:
            user_id: The user id, such as 'sara_doe_496'.

        Returns:
            User: The user details.

        Raises:
            ValueError: If the user is not found.
        """
        user = self._get_user(user_id)
        return user

    def modify_pending_order_items(
        self,
        order_id: str,
        item_ids: List[str],
        new_item_ids: List[str],
        payment_method_id: str,
    ) -> Order:
        """Modify items in a pending order to new items of the same product type. For a pending order, this function can only be called once. The agent needs to explain the exchange detail and ask for explicit user confirmation (yes/no) to proceed.

        Args:
            order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.
            item_ids: The item ids to be modified, each such as '1008292230'. There could be duplicate items in the list.
            new_item_ids: The item ids to be modified for, each such as '1008292230'. There could be duplicate items in the list. Each new item id should match the item id in the same position and be of the same product.
            payment_method_id: The payment method id to pay or receive refund for the item price difference, such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details.

        Returns:
            Order: The order details after the modification.

        Raises:
            ValueError: If the order is not pending.
            ValueError: If the items to be modified do not exist.
            ValueError: If the new items do not exist or do not match the old items.
            ValueError: If the number of items to be modified does not match.
        """

        # Check if the order exists and is pending
        order = self._get_order(order_id)
        if order.status != "pending":
            raise ValueError("Non-pending order cannot be modified")

        # Check if the items to be modified exist. There can be duplicate items in the list.
        all_item_ids = [item.item_id for item in order.items]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                raise ValueError(f"{item_id} not found")

        # Check new items exist, match old items, and are available
        if len(item_ids) != len(new_item_ids):
            raise ValueError("The number of items to be exchanged should match")

        diff_price = 0
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            if item_id == new_item_id:
                raise ValueError(
                    "The new item id should be different from the old item id"
                )
            item = next((item for item in order.items if item.item_id == item_id), None)
            if item is None:
                raise ValueError(f"Item {item_id} not found")
            product_id = item.product_id
            variant = self._get_variant(product_id, new_item_id)
            if not variant.available:
                raise ValueError(f"New item {new_item_id} not found or available")

            old_price = item.price
            new_price = variant.price
            diff_price += new_price - old_price

        # Check if the payment method exists
        payment_method = self._get_payment_method(order.user_id, payment_method_id)

        # If the new item is more expensive, check if the gift card has enough balance
        if isinstance(payment_method, GiftCard) and payment_method.balance < diff_price:
            raise ValueError("Insufficient gift card balance to pay for the new item")

        # Handle the payment or refund
        order.payment_history.append(
            OrderPayment(
                transaction_type="payment" if diff_price > 0 else "refund",
                amount=abs(diff_price),
                payment_method_id=payment_method_id,
            )
        )
        if isinstance(payment_method, GiftCard):
            payment_method.balance -= diff_price
            payment_method.balance = round(payment_method.balance, 2)

        # Modify the order
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            item = next((item for item in order.items if item.item_id == item_id), None)
            if item is None:
                raise ValueError(f"Item {item_id} not found")
            item.item_id = new_item_id
            item.price = variant.price
            item.options = variant.options
        order.status = "pending (item modified)"

        return order
