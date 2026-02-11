import { useState } from "react";

export const LessonForm = ({ moduleId, onSubmit }) => {
  const [title, setTitle] = useState("");
  const [videoUrl, setVideoUrl] = useState("");

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit({
      title,
      video_url: videoUrl,
      module_id: moduleId
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4 shadow">
      <h4>Nueva lección</h4>

      <div className="mb-3">
        <label className="form-label">Título</label>
        <input
          className="form-control"
          value={title}
          onChange={e => setTitle(e.target.value)}
          required
        />
      </div>

      <div className="mb-3">
        <label className="form-label">URL del video</label>
        <input
          type="url"
          className="form-control"
          value={videoUrl}
          onChange={e => setVideoUrl(e.target.value)}
        />
      </div>

      <button className="btn btn-primary w-100">
        Guardar lección
      </button>
    </form>
  );
};
