import React, { useContext } from "react";
import NewsCard from "./NewsCard";
import ThemeContext from "../context/ThemeContext";

const NewsList = ({ newsList })=>{
    //console.log(newsList.news)
    
    const { darkMode } = useContext(ThemeContext);
    

    
    
    
    return (
        
        <div>
            <ul 
                className={`w-full h-full flex flex-col justify-between divide-y-1 ${
                    darkMode ? "divide-gray-800" : null
                }`}
            >


                {(typeof newsList.news === 'object') ? newsList.news.map((value)=>{
                    return(
                        <NewsCard>
                            <h2 className='font-semibold text-xl break-words'> {value[0]}  </h2>
                        
                        
                            
                            <p className='text-base mt-1'>
                                <button className={`text-white px-2 py-1 rounded-full text-sm ${
                                    value[1] > 0 ? "bg-green-500"
                                        : value[1] < 0 ? "bg-red-500"
                                            : "bg-slate-500"
                                            }`}> 

                                    {value[1] > 0 ? `Bullish`
                                        : value[1] < 0 ? `Bearish`
                                            : `Neutral`}  
                                </button>
                                <br/>
                                <br/>
                                
                                Via: {value[3]}                                                             
                                
                                <br/>
                                <a className="text-blue-600" href = {`${value[2]}`}> Full Article </a>
                            </p>
                            

                        </NewsCard>
                    )
                }): console.log("UNDEFINED STUFF")}
            </ul>
        </div>
        




    );
};

export default NewsList