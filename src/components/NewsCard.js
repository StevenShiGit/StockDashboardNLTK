import React, { useContext } from "react";
import ThemeContext from "../context/ThemeContext";

//render stuff between components (children)
const NewsCard = ({ children }) => {
  const { darkMode } = useContext(ThemeContext);
  return (
    <div 
      className={`max-w-xl rounded-md p-8 border-2 ${
        darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-neutral-200"
      }`}
    >
        <div className='p-4'>
            {children}
        </div>
    </div>
  );
};

export default NewsCard;
