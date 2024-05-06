//add sentiment by adding stockSentiment state, updating the fetch from stock-api, and printing it

import React, { useContext, useEffect, useState } from "react";
import ThemeContext from "../context/ThemeContext";
import Overview from "./Overview";
import Details from "./Details";
import Chart from "./Chart";
import Header from "./Header";
import StockContext from "../context/StockContext";
import NewsList from "./NewsList"
import { fetchStockDetails, fetchQuote, fetchSentiment } from "../utils/api/stock-api";

const Dashboard = () => {
  const { darkMode } = useContext(ThemeContext);

  const { stockSymbol } = useContext(StockContext);

  const [stockDetails, setStockDetails] = useState({});

  const [quote, setQuote] = useState({});

  const [sentiment, setSentiment] = useState({});

  //use effect allows side effects in code (api request)
  //fetch details of stock and update the stock details
  //do something at start of code run, do again if stock symbol changes
  useEffect(() => {
    const updateStockDetails = async () => {
      try {
        const result = await fetchStockDetails(stockSymbol);
        setStockDetails(result);
      } catch (error) {
        setStockDetails({});
        console.log(error);
      }
    };

    const updateStockOverview = async () => {
      try {
        const result = await fetchQuote(stockSymbol);
        setQuote(result);
      } catch (error) {
        setQuote({});
        console.log(error);
      }
    };
    //by calling update stock details, setting state of stock details also
    //also setting quote state

    const updateStockSentiment = async () => {
      try{
        //put what stock ticker in here to analyze the sentiment
        const result = await fetchSentiment(stockSymbol);
        setSentiment(result);
      }catch (error){

        setSentiment({});
        console.log(error);
      }
    }
    
    updateStockSentiment();
    updateStockDetails();
    updateStockOverview();

  }, [stockSymbol]);

  return ( //header prints name of stock (top left)
    <div className={`${darkMode ? "bg-gray-900 text-gray-300" : "bg-neutral-100"}`}>
      <div
        className={`h-screen grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 grid-rows-8 md:grid-rows-7 xl:grid-rows-5 auto-rows-fr gap-6 p-10 font-quicksand`}
      >
      
        <div className="col-span-1 md:col-span-2 xl:col-span-3 row-span-1 flex justify-start items-center">
          
          <Header name={stockDetails.name} />
        
        </div>
        
        <div className="md:col-span-2 row-span-4">
          <Chart />
        </div>
        <div>
          <Overview
          //curly braces for object
          //also used for running html in js
          //printing overview (price and symbol and stuff)
            symbol={stockSymbol}
            price={quote.pc}
            change={quote.d}
            changePercent={quote.dp}
            currency={stockDetails.currency}
            
          />
        </div>
        <div className="row-span-2 xl:row-span-3">
          <Details details={stockDetails} sentiment={sentiment} />
         
        </div>

        
        
      </div>
      
      <div className="flex items-center justify-center">
        <NewsList newsList={sentiment} />
      </div>
      
    </div>
  );
};

export default Dashboard;
