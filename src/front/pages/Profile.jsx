import useGlobalReducer from "../hooks/useGlobalReducer";
import { UserProfileForm } from "../components/UserProfileForm";

export const Profile = () => {
  const { store, dispatch } = useGlobalReducer();

  return (
    <div className="container mt-4">
      <UserProfileForm
        user={store.current_user}
        onUpdate={(data) => console.log("UPDATE", data)}
        onDelete={() => console.log("DELETE USER")}
      />
    </div>
  );
};
