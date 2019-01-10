// Renders the component for the Home screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import Header from './../Header/Header';
import ModuleCard from './../ModuleCard/ModuleCard';
import Loading from './../Loading/Loading';

import './Home.css';

const MODULES = require('./../../data/modules.json');

class Home extends Component {
    state = {
      name: '',
      loading: true,
      modules: []
    }


    navigate = (url) => {
      // Handles changing the screen when clicking on a module
      this.props.history.push(url);
    }

    componentDidMount(){
      // Pulls the users name and redirects to the Login
      // page if authentication is required
      const token = localStorage.getItem('trsToken');
      if(!token){
        this.navigate('/login');
      } else {
        const auth = 'Bearer '.concat(token);
        axios.get('/service/user/authorize', { headers: { Authorization: auth }})
          .then(res => {
            this.setState({
              name: res.data.id,
              modules: res.data.modules,
              loading: false
            });
          })
          .catch( err => {
            if(err.response.status===401){
              this.navigate('/login');
            }
          })
      }
    }

    renderModuleCards(){
      // Only renders cards that users have access to

      // Check to see if the modules returned by the service
      // appear in the modules.json file
      let goodModules = [];
      for(let module of this.state.modules){
        if(module in MODULES){
          goodModules.push(module);
        }
      }
      const rowCount = Math.ceil(goodModules.length/2);

      let i = 0;
      let rows = [];
      while(i < rowCount){
        const idx1 = i*2;
        const idx2 = idx1 + 1;
        
        // Render the first module
        const module1 = goodModules[idx1];
        const moduleCard1 = (
            <Col xs={12} sm={12} md={6} lg={6}>
              <ModuleCard 
                title={MODULES[module1].title}
                icon={MODULES[module1].icon}
                bullets={MODULES[module1].bullets}
                click={()=>this.navigate(MODULES[module1].link)}
              />
            </Col>
        )
        
        // If the number of modules is odd, render the second module
        let module2 = null;
        let moduleCard2 = null;
        if(idx2 < goodModules.length){
          module2 = goodModules[idx2];
          moduleCard2 = (
            <Col xs={12} sm={12} md={6} lg={6}>
              <ModuleCard 
                title={MODULES[module2].title}
                icon={MODULES[module2].icon}
                bullets={MODULES[module2].bullets}
                click={()=>this.navigate(MODULES[module2].link)}
              />
            </Col>
          )
        }

        const row = (
          <Row className='module-row'>
            {moduleCard1}
            {moduleCard2}
          </Row>
        )
        rows.push(row);
        i++;
      }
      return rows

    }

    render() {
      let message = null;
      if(this.state.modules.length===0){
        message = <h4>Contact your system administrator to request access to a module.</h4>
      } else {
        message = <h4>Choose a module to begin.</h4>
      }

      let rows = this.renderModuleCards();

      if(this.state.loading){
        return(
          <div>
            <Header />
            <div className="event-loading">
              <Loading />
            </div>
          </div>
        )
      } else {
        return (
          <div>
            <Header />
            <div className="Home">
              <div className="home-header">
                <h2>Welcome, {this.state.name}!</h2><hr/>
                {message}
              </div>
              {rows}
            </div>
          </div>
        );
      }
    }
}

export default withRouter(Home);
