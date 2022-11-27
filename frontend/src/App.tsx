import 'bootstrap/dist/css/bootstrap.css';
import "bootstrap-icons/font/bootstrap-icons.css";
import Sidebar from './components/Sidebar/Sidebar';
import MainContent from './components/MainContent/MainContent';


function App() {

  return (
    <div className="App">
      <Sidebar>
        <MainContent/>
        
      </Sidebar>

    </div>
  );
}

export default App;
