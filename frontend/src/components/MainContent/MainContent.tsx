import React, { FC, useEffect, useState } from 'react';
import './MainContent.css';
import logo from '../../logo.svg';
import parse, { Element } from 'html-react-parser';

interface MainContentProps {}

const MainContent: FC<MainContentProps> = () => {  
    const [data, setData] = useState({
      name: '',
      about: '',
    })
    const [graph, setGraph] = useState('')
  
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
    async function getData2() {
      const url=`http://localhost:5000/graph`
      fetch(url, {
        method: "GET",
      })
      .then((response: any) => {
        if (!response.ok) {
          throw new Error('Network response not OK 2');
        }
        return response.json()
        
      })
      .then((data) => {
        console.log(data)
        setGraph(data)
  
      }).catch((error) => {
        console.error('There has been a problem with your fetch operation',
        error);
      })
    }
    
    const parser = (input: string) =>
    parse(input, {
      replace: domNode => {
        if (domNode instanceof Element && domNode.attribs.class === 'remove') {
          return <></>;
        }
      }
    });

    useEffect(() => {
        getData()
        getData2()
    }, [])
    
  
    return (
      <div>
          <img src={logo} className="App-logo" alt="logo" />
          <h1>Your name: {data.name}</h1>
          <h2>The title: {data.about}</h2>
          <React.Fragment>{parser(graph)}</React.Fragment>
  
      </div>
    );
  };

export default MainContent;
