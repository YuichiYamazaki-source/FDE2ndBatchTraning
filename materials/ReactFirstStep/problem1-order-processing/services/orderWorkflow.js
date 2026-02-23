// ============================================
// End-to-End Order Workflow using ASYNC/AWAIT
// ============================================

const Order = require("../models/Order");
const processPaymentPromise = require("./paymentPromise");

// Step 1: Save order
const saveOrder = async (orderData) => {
  console.log("Step 1: Saving order...");
  const order = Order.create(orderData);
  console.log("Order saved with ID:", order.id);
  return order;
};

// Step 2: Process payment
const processPayment = async (order) => {
  console.log("Step 2: Processing payment...");
  const result = await processPaymentPromise(order.totalAmount);
  Order.updateStatus(order.id, "PAID");
  console.log("Payment completed. Status updated to PAID");
  return result;
};

// Step 3: Start cooking
const startCooking = async (orderId) => {
  console.log("Step 3: Starting cooking...");
  return new Promise((resolve) => {
    setTimeout(() => {
      Order.updateStatus(orderId, "COOKING");
      console.log("Cooking started. Status updated to COOKING");
      resolve();
    }, 2000);
  });
};

// Step 4: Assign delivery
const assignDelivery = async (orderId) => {
  console.log("Step 4: Assigning delivery...");
  return new Promise((resolve) => {
    setTimeout(() => {
      Order.updateStatus(orderId, "OUT_FOR_DELIVERY");
      console.log("Delivery assigned. Status updated to OUT_FOR_DELIVERY");
      resolve();
    }, 2000);
  });
};

// Step 5: Complete delivery
const completeDelivery = async (orderId) => {
  console.log("Step 5: Completing delivery...");
  return new Promise((resolve) => {
    setTimeout(() => {
      Order.updateStatus(orderId, "DELIVERED");
      console.log("Order delivered. Status updated to DELIVERED");
      resolve();
    }, 2000);
  });
};

// Full workflow using async/await
const processOrderWorkflow = async (orderData) => {
  const order = await saveOrder(orderData);
  await processPayment(order);
  await startCooking(order.id);
  await assignDelivery(order.id);
  await completeDelivery(order.id);
  return Order.findById(order.id);
};

module.exports = processOrderWorkflow;
