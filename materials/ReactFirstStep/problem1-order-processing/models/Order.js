// In-memory storage for orders
const orders = {};
let idCounter = 1;

const Order = {
  create(data) {
    const id = String(idCounter++);
    const order = {
      id,
      customerName: data.customerName,
      items: data.items,
      totalAmount: data.totalAmount,
      status: "PLACED",
      createdAt: new Date().toISOString(),
    };
    orders[id] = order;
    return order;
  },

  findById(id) {
    return orders[id] || null;
  },

  findAll() {
    return Object.values(orders).sort(
      (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
    );
  },

  updateStatus(id, status) {
    if (orders[id]) {
      orders[id].status = status;
      return orders[id];
    }
    return null;
  },
};

module.exports = Order;
