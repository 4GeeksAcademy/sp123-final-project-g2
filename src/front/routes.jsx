// Import necessary components and functions from react-router-dom.

import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
} from "react-router-dom";
import { Layout } from "./pages/Layout";
import { Home } from "./pages/Home";
import { Single } from "./pages/Single";
import { Demo } from "./pages/Demo";
import { Login } from "./pages/Login.jsx";
import { Register } from "./pages/Register.jsx";
import { Courses } from "./pages/Courses.jsx";
import { Modules } from "./pages/Modules.jsx";
import { Lessons } from "./pages/Lessons.jsx";
import { LessonDetails } from "./pages/LessonDetails.jsx";
import { Dashboard } from "./pages/Dashboard.jsx";
import { MyProgress } from "./pages/MyProgress.jsx";
import { Achievements } from "./pages/Achievements.jsx";
import { CourseDetail } from "./pages/CourseDetail.jsx";
import { Profile } from "./pages/Profile.jsx";
import { QuienesSomos } from "./pages/QuienesSomos.jsx";
import { PublicCourses } from "./pages/PublicCourses.jsx";
import { Planes } from "./pages/Planes.jsx";



export const router = createBrowserRouter(
    createRoutesFromElements(
    // CreateRoutesFromElements function allows you to build route elements declaratively.
    // Create your routes here, if you want to keep the Navbar and Footer in all views, add your new routes inside the containing Route.
    // Root, on the contrary, create a sister Route, if you have doubts, try it!
    // Note: keep in mind that errorElement will be the default page when you don't get a route, customize that page to make your project more attractive.
    // Note: The child paths of the Layout element replace the Outlet component with the elements contained in the "element" attribute of these child paths.

      // Root Route: All navigation will start from here.
      <Route path="/" element={<Layout />} errorElement={<h1>Not found!</h1>} >

        {/* Nested Routes: Defines sub-routes within the BaseHome component. */}
        <Route path= "/" element={<Home />} />
        <Route path="/single/:theId" element={ <Single />} />  {/* Dynamic route for single items */}
        <Route path="/demo" element={<Demo />} />
        <Route path="/login" element={<Login/>} />
        <Route path="/register" element={<Register />} />
        <Route path="/courses-public" element={<PublicCourses />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/modules" element={<Modules />} />
        <Route path="/lessons" element={<Lessons />} />
        <Route path="/lesson-details" element={<LessonDetails />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/my-progress" element={<MyProgress />} />
        <Route path="/achievements" element={<Achievements />} />
        <Route path="/courses/:courseId" element={<CourseDetail />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/quienes-somos" element={<QuienesSomos />} />
        <Route path="/planes" element={<Planes />} />
      </Route>
    )
);