// Renders the component for the Home screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';

import ModuleCard from './../ModuleCard/ModuleCard';

import './Home.css';

const MODULES = require('./../../data/modules.json');

class Home extends Component {
    render() {
      return (
        <div className="Home">
          <div className="home-header">
            <h2>Welcome!</h2><hr/>
            <h4>Choose a module to begin.</h4>
          </div>
          <Row className="module-row">
            <Col xs={12} sm={12} md={6} lg={6}>
              <ModuleCard 
                title={MODULES[0].title}
                icon={MODULES[0].icon}
                bullets={MODULES[0].bullets}
                link={MODULES[0].link}
              />
            </Col>
            <Col xs={12} sm={12} md={6} lg={6}>
              <ModuleCard 
                title={MODULES[1].title}
                icon={MODULES[1].icon}
                bullets={MODULES[1].bullets}
                link={MODULES[1].link}
              />
            </Col>
          </Row>
          <Row className="module-row">
            <Col xs={12} sm={12} md={6} lg={6}>
              <ModuleCard 
                title={MODULES[2].title}
                icon={MODULES[2].icon}
                bullets={MODULES[2].bullets}
                link={MODULES[2].link}
              />
            </Col>
            <Col xs={12} sm={12} md={6} lg={6}>
              <ModuleCard 
                title={MODULES[3].title}
                icon={MODULES[3].icon}
                bullets={MODULES[3].bullets}
                link={MODULES[3].link}
              />
            </Col>
          </Row>
        </div>
      );
    }
}

export default Home;
