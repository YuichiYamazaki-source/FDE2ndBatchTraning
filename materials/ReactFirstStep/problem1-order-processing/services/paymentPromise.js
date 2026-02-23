// ============================================
// Payment Processing using PROMISE pattern
// ============================================

const processPaymentPromise = (totalAmount) => {
  console.log("Processing payment (promise-based)...");

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (totalAmount > 1000) {
        reject(new Error("Payment failed: Amount exceeds 1000"));
      } else {
        resolve({ success: true, message: "Payment successful", amount: totalAmount });
      }
    }, 3000);
  });
};

module.exports = processPaymentPromise;
