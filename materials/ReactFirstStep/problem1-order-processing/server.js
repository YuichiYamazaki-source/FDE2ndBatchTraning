const express = require("express");
const orderRoutes = require("./routes/orderRoutes");

const app = express();
const PORT = 3000;

app.use(express.json());

app.use("/orders", orderRoutes);

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Order Processing Server running on http://localhost:${PORT}`);
});
