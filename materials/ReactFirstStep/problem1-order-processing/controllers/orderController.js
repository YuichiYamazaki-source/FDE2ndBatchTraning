const Order = require("../models/Order");
const processOrderWorkflow = require("../services/orderWorkflow");

// POST /orders - Create a new order
const createOrder = async (req, res) => {
  try {
    const { customerName, items, totalAmount } = req.body;

    // Event Loop Demonstration
    console.log("Order received");
    setTimeout(() => console.log("Timer completed"), 0);
    Promise.resolve().then(() => console.log("Promise resolved"));
    console.log("Order processing started");

    const finalOrder = await processOrderWorkflow({ customerName, items, totalAmount });

    res.status(201).json({
      message: "Order processed successfully",
      order: finalOrder,
    });
  } catch (error) {
    if (error.message.includes("Payment failed")) {
      const orders = Order.findAll();
      const latestOrder = orders.find(
        (o) => o.customerName === req.body.customerName && o.status === "PLACED"
      );
      if (latestOrder) {
        Order.updateStatus(latestOrder.id, "FAILED");
      }
      return res.status(400).json({
        message: "Payment failed",
        error: error.message,
        order: latestOrder ? Order.findById(latestOrder.id) : null,
      });
    }
    res.status(500).json({ message: "Internal server error", error: error.message });
  }
};

// GET /orders/:id - Retrieve order status
const getOrderById = async (req, res) => {
  try {
    const order = Order.findById(req.params.id);
    if (!order) {
      return res.status(404).json({ message: "Order not found" });
    }
    res.status(200).json(order);
  } catch (error) {
    res.status(500).json({ message: "Database error", error: error.message });
  }
};

// GET /orders - Retrieve all orders
const getAllOrders = async (req, res) => {
  try {
    const orders = Order.findAll();
    res.status(200).json(orders);
  } catch (error) {
    res.status(500).json({ message: "Database error", error: error.message });
  }
};

module.exports = { createOrder, getOrderById, getAllOrders };
