import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import ThemeContext from '../context/ThemeContext';
import Header from './Header';
import Card from './Card'






function CompanyList() {
    const { darkMode } = useContext(ThemeContext);
    const history = useNavigate();
    const companies = [
        { id: 1, name: '3M' },
        { id: 2, name: 'American Express' },
        { id: 3, name: 'Amgen' },
        { id: 4, name: 'Apple' },
        { id: 5, name: 'Boeing' },
        { id: 6, name: 'Caterpillar' },
        { id: 7, name: 'Chevron' },
        { id: 8, name: 'Cisco Systems' },
        { id: 9, name: 'Coca-Cola' },
        { id: 10, name: 'Dow' },
        { id: 11, name: 'Goldman Sachs' },
        { id: 12, name: 'The Home Depot' },
        { id: 13, name: 'Honeywell' },
        { id: 14, name: 'IBM' },
        { id: 15, name: 'Intel' },
        { id: 16, name: 'Johnson & Johnson' },
        { id: 17, name: 'JPMorgan Chase' },
        { id: 18, name: 'McDonald\'s' },
        { id: 19, name: 'Merck & Co.' },
        { id: 20, name: 'Microsoft' },
        { id: 21, name: 'Nike' },
        { id: 22, name: 'Procter & Gamble' },
        { id: 23, name: 'Salesforce' },
        { id: 24, name: 'The Travelers Companies' },
        { id: 25, name: 'UnitedHealth Group' },
        { id: 26, name: 'Verizon' },
        { id: 27, name: 'Visa' },
        { id: 28, name: 'Walmart' },
        { id: 29, name: 'Walgreens Boots Alliance' },
        { id: 30, name: 'The Walt Disney Company' },
      ];
    
      function redirect(){
        const path = "/ticker";
        history.push(path);
      }
  return (
    <div className={`${darkMode ? "bg-gray-900 text-gray-300" : "bg-neutral-100"}`}>

        
        <div className={`p-10 font-quicksand`}>
    
            <div className="grid-2 col-span-1 md:col-span-2 xl:col-span-3 row-span-1 flex justify-start items-center">
                    
                    <Header name="Top Companies"/>
                    
            </div>

            <div className="flex justify-center items-center">
                <ul>
                    {companies.map(item => {   
                        return(
                            <Card>
                                <div className="w-96">
                                    {item.name}
                                    
                                </div>
                            </Card>
                            
                        )
                    })}
                </ul>
            </div>
            
            
        </div>
    </div>
        
      
    
  );
}

export default CompanyList;
