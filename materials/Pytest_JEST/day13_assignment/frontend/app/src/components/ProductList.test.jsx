import {render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import axios from "axios";
import ProductList from "./ProductList";

jest.mock("axios");

const mockProducts = [
    { name: "Wireless Mouse", price: 29.99, category: "Electronics" },
    { name: "Mechanical Keyboard", price: 79.99, category: "Electronics" },
];

test("API call is triggered on component load", () => {
    axios.get.mockResolvedValue({ data: mockProducts });
    render(<ProductList />);
    expect(axios.get).toHaveBeenCalledWith("http://localhost:8000/products");
});

test("Loading message is shown while data is fetched", () => {
    axios.get.mockReturnValue(new Promise(() => {}));
    render(<ProductList />);
    expect(screen.getByText("Loading...")).toBeInTheDocument()
});

test("Product list is rendered after successful API response", async () => {
    axios.get.mockResolvedValue({ data: mockProducts });
    render(<ProductList />);
    await waitFor(() => {
        expect(screen.getByText(/Wireless Mouse/)).toBeInTheDocument();
        expect(screen.getByText(/Mechanical Keyboard/)).toBeInTheDocument();
    });
});

test("Error message is displayed when API fails", async () => {
    axios.get.mockRejectedValue(new Error("Network Error"));
    render(<ProductList />);
    await waitFor(() => {
        expect(screen.getByText("Failed to fetch products")).toBeInTheDocument();
    });
});

test("Empty product list message is shown when no data exists", async () => {
    axios.get.mockResolvedValue({ data: [] });
    render(<ProductList />);
    await waitFor(() => {
        expect(screen.getByText("product found")).toBeInTheDocument();
    });
});