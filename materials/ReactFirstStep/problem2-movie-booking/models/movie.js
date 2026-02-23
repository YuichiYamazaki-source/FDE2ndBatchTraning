const movies = {};
let idCounter = 1;

const Movie = {
  create(data) {
    const movieId = String(idCounter++);
    const movie = {
      movieId,
      movieName: data.movieName,
      totalSeats: data.totalSeats,
      availableSeats: data.availableSeats
    };
    movies[movieId] = movie;
    return movie
  },

  findById(movieId) {
    return movies[movieId] || null;
  },

  findByName(movieName) {
    return movies[movieName] || null;
  },

  findAll() {
    return Object.valaues(movies).sort(
        (a, b) => Number(b.movie[movieId]) - Number(a.movie[movieId])
    );
  },
};

module.exports = Movie