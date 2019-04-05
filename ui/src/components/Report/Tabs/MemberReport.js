// Renders the information in the Members
// section of the report view
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import Plot from 'react-plotly.js';
import { withRouter } from 'react-router-dom';

import Loading from './../../Loading/Loading';
import { DONUT_PLOT_COLORS } from './../../../utilities/plots';

class MemberReport extends Component {
  state = {
    'mounted': false
  }

  componentDidMount(){
    this.setState({mounted: true});
  }

  renderAgeGroupList = () => {
    // Shows the count for each demographic
    const demographics = this.props.demographics;
    let ageGroups = [];
    for(let group in demographics){
      const count = demographics[group];
      if(group==='Young Professional'){
        ageGroups.push(<li><b>YP:</b> {count}</li>);
      } else {
        ageGroups.push(<li><b>{group}:</b> {count}</li>);
      }
    }
    return(
      <div>
        <ul className='quick-facts-bullets'>
          {ageGroups}
        </ul>
      </div>
    )

  }

  renderAgeGroups = () => {
    // Creates a donut chart showing the 
    // proportions of each age group
    
    // Generate the data for the plot
    const demographics = this.props.demographics;
    let values = [];
    let labels = [];
    for(let group in demographics){
      if(group !== 'All'){
        if(group==='Young Professional'){
          labels.push('YP');
        } else {
          labels.push(group);
        }
        values.push(demographics[group]);
      }
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: DONUT_PLOT_COLORS, color: 'white'}
    }]

    const ageGroupList = this.renderAgeGroupList();
    if(!this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Demographics</h4>
          <div className='quick-facts-plot-area'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const size = .5*width
      const layout = {
        height: size,
        width: size, 
        showlegend: false,
        margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Age Groups</h4>
          <div className='quick-facts-list'>
            {ageGroupList}
          </div>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }
  
  render(){
    const ageGroups = this.renderAgeGroups();
   return(
      <div className='QuickFacts'>
        <h2>Demographics</h2>
        <Row>
          {ageGroups}
        </Row><hr/>
      </div> 
    )
  }
};
export default withRouter(MemberReport);
