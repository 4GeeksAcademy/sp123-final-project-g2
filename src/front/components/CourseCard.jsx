export const CourseCard = ({ course, onDetails }) => {
  return (
    <div className="col-md-4">
      <div className="card mb-3 shadow">
        <div className="card-body">
          <h5>{course.title}</h5>
          <p>{course.description}</p>

          <button
            className="btn btn-secondary"
            onClick={() => onDetails(course)}
          >
            Details
          </button>
        </div>
      </div>
    </div>
  );
};
