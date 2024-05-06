import React, { useContext } from "react";
import Card from "./Card";
import ThemeContext from "../context/ThemeContext";

const Details = ({ details, sentiment}) => {
  const { darkMode } = useContext(ThemeContext);

  //print these details
  const detailsList = {
    name: "Name",
    country: "Country",
    currency: "Currency",
    exchange: "Exchange",
    ipo: "IPO Date",
    marketCapitalization: "Market Capitalization",
    finnhubIndustry: "Industry",
    sentiment: "Sentiment",
  };

  
  console.log(sentiment.sentiment)

  return (
    <Card>
      <ul
        className={`w-full h-full flex flex-col justify-between divide-y-1 ${
          darkMode ? "divide-gray-800" : null
        }`}
      >
        {Object.keys(detailsList).map((item) => { //mapping keys in details list, using html to print and show data
          //also prints the descriptpion detailsList
          //detailList and details must have same item description/key
          return (
            //keys identify item, so if they are re-rendered, only key is re-rendered
            <li key={item} className="flex-1 flex justify-between items-center">
              
              <span>{detailsList[item]}</span> 
              <span className="font-bold">
                {item === "marketCapitalization"? 
                  `${(details[item] / 1000).toFixed(2)}B`
                
                  : item === "sentiment"?
                      
                      sentiment.sentiment
                    :details[item]}
                
              </span>
            </li>
          );
        })}
        
          
      
      </ul>
    </Card>
  );
};

export default Details;
