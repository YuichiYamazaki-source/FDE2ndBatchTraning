const express = require("express");
const router = express.Router();
const { createOrder, getOrderById, getAllOrders } = require("../controllers/orderController");

router.post("/", createOrder);
router.get("/:id", getOrderById);
router.get("/", getAllOrders);

module.exports = router;
