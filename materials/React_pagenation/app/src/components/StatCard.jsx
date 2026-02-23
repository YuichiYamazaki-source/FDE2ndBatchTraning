const StatCard = ({ title, value, color}) => {
    return (
    <div className="col-md-4 mb-3">
      <div className={`card text-white bg-${color}`}>
        <div className="card-body text-center">
          <h5 className="card-title">{title}</h5>
          <p className="card-text display-4">{value}</p>
        </div>
      </div>
    </div>
  );
};

export default StatCard;