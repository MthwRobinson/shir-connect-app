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
      loading: true
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
        axios.get('/service/test', { headers: { Authorization: auth }})
          .then(res => {
            this.setState({
              name: res.data.name,
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

    render() {
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
                <h4>Choose a module to begin.</h4>
              </div>
              <Row className="module-row">
                <Col xs={12} sm={12} md={6} lg={6}>
                  <ModuleCard 
                    title={MODULES[0].title}
                    icon={MODULES[0].icon}
                    bullets={MODULES[0].bullets}
                    click={()=>this.navigate(MODULES[0].link)}
                  />
                </Col>
                <Col xs={12} sm={12} md={6} lg={6}>
                  <ModuleCard 
                    title={MODULES[1].title}
                    icon={MODULES[1].icon}
                    bullets={MODULES[1].bullets}
                    click={()=>this.navigate(MODULES[1].link)}
                  />
                </Col>
              </Row>
              <Row className="module-row">
                <Col xs={12} sm={12} md={6} lg={6}>
                  <ModuleCard 
                    title={MODULES[2].title}
                    icon={MODULES[2].icon}
                    bullets={MODULES[2].bullets}
                    click={()=>this.navigate(MODULES[2].link)}
                  />
                </Col>
                <Col xs={12} sm={12} md={6} lg={6}>
                  <ModuleCard 
                    title={MODULES[3].title}
                    icon={MODULES[3].icon}
                    bullets={MODULES[3].bullets}
                    click={()=>this.navigate(MODULES[3].link)}
                  />
                </Col>
              </Row>
            </div>
          </div>
        );
      }
    }
}

export default withRouter(Home);
