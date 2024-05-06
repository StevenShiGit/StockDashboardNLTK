import React, { useContext, useaState } from "react";
import Card from "./Card";
import ThemeContext from "../context/ThemeContext";

const NewsDetails = ({ details, quote, name }) => {
  const { darkMode } = useContext(ThemeContext);

  
  

  return (
    <Card>
      <ul
        className={`w-full h-full flex flex-col justify-between divide-y-1 ${
          darkMode ? "divide-gray-800" : null
        }`}
      > 
       
        <div className="flex justify-center items-center">
             <ul>
                 
                     
                         <Card>
                             <div className="w-96">
                                {name}
                                {logo}

                                {quote.d}
                                 
                             </div>
                         </Card>
                         
                     
                
             </ul>
         </div>

    


        
          
      
      </ul>
    </Card>
  );
};

export default NewsDetails;
