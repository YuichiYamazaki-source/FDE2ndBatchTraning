// ============================================
// Payment Processing using CALLBACK pattern
// ============================================

const processPaymentCallback = (totalAmount, callback) => {
  console.log("Processing payment (callback-based)...");

  setTimeout(() => {
    if (totalAmount > 1000) {
      callback(new Error("Payment failed: Amount exceeds 1000"), null);
    } else {
      callback(null, { success: true, message: "Payment successful", amount: totalAmount });
    }
  }, 3000);
};

module.exports = processPaymentCallback;
