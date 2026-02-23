const express = require("express");
const router = express.Router();
const { createMovie, getMovieById, getMovieByName, getAllMovies} = require("../controllers/orderController");

router.post("/", createMovie);
router.get("/:id", getMovieById);
router.get("/", getMovieByName);
router.get("/"), getAllMovies;

module.exports = movieRouter;