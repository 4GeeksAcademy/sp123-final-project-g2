export const MultimediaResource = ({ resource }) => {
  if (resource.type === "video") {
    return (
      <video controls className="w-100 mb-3">
        <source src={resource.url} />
      </video>
    );
  }

  if (resource.type === "image") {
    return <img src={resource.url} className="img-fluid mb-3" />;
  }

  return <a href={resource.url} target="_blank">Ver recurso</a>;
};
