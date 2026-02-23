const bookings = {};
let idCounter = 1;

const Booking = {
  create(data) {
    const bookingId = String(idCounter++);
    const booking = {
      bookingId, 
      movieId: data.movieId,
      userName: data.userName,
      seatsBooked: data.seatBooked,
      status: data.status,
      createAt: new Date().toISOString()
    };
    bookings[bookingId] = booking;
    return booking;
  },

    findByBookingId(bookingId) {
    return bookings[bookingId] || null;
  },

  findAll() {
    return Object.values(bookings).sort(
      (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
    );
  },

  updateStatus(bookingId, status) {
    if (bookings[bookingId]) {
        bookings[bookingId].status = status;
        return orders[id];
    }
    return null;
  },
};

module.exports = Booking