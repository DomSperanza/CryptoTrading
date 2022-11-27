import React, { FC, useEffect, useState } from 'react';
import './MainContent.css';
import logo from '../../logo.svg';

interface MainContentProps {}

const MainContent: FC<MainContentProps> = () => {  
    const [data, setData] = useState({
      name: '',
      about: '',
    })
  
    async function getData() {
      const url='http://localhost:5000/'
      fetch(url, {
        method: "GET",
  
      })
      .then((response: any) => {
        if (!response.ok) {
          throw new Error('Network response not OK');
        }
        return response.json()
        
      })
      .then((data) => {
        setData(data)
  
      }).catch((error) => {
        console.error('There has been a problem with your fetch operation',
        error);
      })
    }
  
    useEffect(() => {
        getData()
    }, [])
    
  
    return (
      <div>
          <img src={logo} className="App-logo" alt="logo" />
          <h1>Your name: {data.name}</h1>
          <h2>The title: {data.about}</h2>
          
  
      </div>
    );
  };

export default MainContent;
