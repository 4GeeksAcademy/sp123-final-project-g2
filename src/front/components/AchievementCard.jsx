export const AchievementCard = ({ achievement }) => {
  return (
    <div className="col-md-4">
      <div className="card mb-3 shadow">
        <div className="card-body text-center">
          {achievement.icon && (
            <img
              src={achievement.icon}
              alt={achievement.name}
              className="img-fluid mb-2"
              style={{ maxHeight: "100px" }}
            />
          )}
          <h5>{achievement.name}</h5>
          <p>{achievement.description}</p>
          <p><strong>Puntos requeridos:</strong> {achievement.required_points}</p>
        </div>
      </div>
    </div>
  );
};
