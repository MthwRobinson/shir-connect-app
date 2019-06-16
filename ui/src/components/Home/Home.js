// Renders the component for the Home screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import { refreshAccessToken } from './../../utilities/authentication';
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
      axios.get('/service/user/authorize')
        .then(res => {
          this.setState({
            name: res.data.id,
            modules: res.data.modules,
            loading: false
          });

          // Refresh the token to keep the session active
          refreshAccessToken();
        })
        .catch(err => {
          if(err.response.status===401){
            this.navigate('/login');
          } else {
            this.navigate('/server-error');
          }
        })
    }

    renderModuleCards(){
      // Only renders cards that users have access to

      // Check to see if the modules returned by the service
      // appear in the modules.json file
      let availableModules = [];
      for(let module of this.state.modules){
        if(module in MODULES){
          availableModules.push(module);
        }
      }
      
      let rows = [];
      for(let i=0; i < availableModules.length; i++){
        const module = availableModules[i];
        const moduleCard = (
          <Col xs={12} sm={12} md={12} lg={6}>
              <ModuleCard 
                title={MODULES[module].title}
                icon={MODULES[module].icon}
                bullets={MODULES[module].bullets}
                click={()=>this.navigate(MODULES[module].link)}
              />
          </Col>
        )
        rows.push(moduleCard);
      }
      return rows

    }

    render() {
      let message = null;
      if(this.state.modules.length===0){
        message = (
          <h4>
            You do not currently have access to any modules.
            Contact your system administrator to request access.
          </h4>
        )
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
              <div>
                <Row>
                  {rows}
                </Row>
              </div>
            </div>
          </div>
        );
      }
    }
}

export default withRouter(Home);
