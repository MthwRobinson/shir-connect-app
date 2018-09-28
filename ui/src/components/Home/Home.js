// Renders the component for the Home screen
import React, { Component } from 'react';
import { Col } from 'react-bootstrap';

import ModuleCard from './../ModuleCard/ModuleCard';

import './Home.css';

class Home extends Component {
    render() {
      return (
        <div className="Home">
          <Col xs={4} sm={4} md={4} lg={4}>
            <ModuleCard 
              title="Upcoming Events"
              icon="fa fa-calendar"
              bullets={[
                "View upcoming events from Eventbrite",
                "Export event information as a .csv file"
              ]}
            />
          </Col>
        </div>
      );
    }
}

export default Home;
