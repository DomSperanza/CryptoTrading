import React, { FC, useEffect, useState } from 'react';
import './MainContent.css';
import logo from '../../logo.svg';

interface MainContentProps {}

const MainContent: FC<MainContentProps> = () => {  
    const [data, setData] = useState({
      name: '',
      about: '',
    })
    const [graph, setGraph] = useState<string|undefined>('')
  
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
      })
      .catch((error) => {
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
        return response.text()
      })
      .then((html:any) => {
        // ! As a note, this is an unsecure way of displaying HTML
        // ! this app is only designed for local host usage, so 
        // ! raw HTML injection theoretically can be trusted from the flask server
        const parser = new DOMParser();
        const doc = parser.parseFromString(html,"text/html")
        const docBody = doc.querySelector('body')?.innerHTML
        // console.log(docBody)
        setGraph(docBody)
      })
      .catch((error) => {
        console.error('There has been a problem with your fetch operation',
        error);
      })
    }

    useEffect(() => {
        getData()
        getData2()
        setGraph('')
    }, [])
    
    return (
      <div>
          <h1>Your name: {data.name}</h1>
          <h2>The title: {data.about}</h2>
          <div dangerouslySetInnerHTML={{__html:graph!}} className='border'></div>
  
      </div>
    );
  };

export default MainContent;
