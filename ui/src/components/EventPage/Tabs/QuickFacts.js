// Renders the information in the Quick Facts
// section of the events view
import moment from 'moment';
import React, { Component } from 'react';
import { Col } from 'react-bootstrap';
import Plot from 'react-plotly.js';
import { withRouter } from 'react-router-dom';

const PLOT_COLORS = [
  'rgb(0,73,131)',
  'rgb(0,87,156)',
  'rgb(0,101,182)',
  'rgb(0,115,207)',
  'rgb(3,143,255)',
  'rgb(29,154,255)'
]

class QuickFacts extends Component {
  //--------------------
  // DEMOGRAPHICS INFO
  //--------------------
  renderAgeGroupList = () => {
    // Shows the number of people in each age group
    // who are attending the event
    const event = this.props.event;
    let ageGroups = [];
    for(let group in event.age_groups){
      const count = event.age_groups[group];
      if(group==='Young Professional'){
        ageGroups.push(<li><b>YP:</b> {count}</li>);
      } else {
        ageGroups.push(<li><b>{group}:</b> {count}</li>);
      }
    }
    return(
      <div>
        <ul className="quick-facts-list">
          {ageGroups}
        </ul>
      </div>
    )
  }

  renderAgeGroups = () => {
    // Creates a donut chart showing the 
    // proportions of each age group
    
    // Generate the data for the plot
    const event = this.props.event;
    let values = [];
    let labels = [];
    for(let group in event.age_groups){
      if(group==='Young Professional'){
        labels.push('YP');
      } else {
        labels.push(group);
      }
      values.push(event.age_groups[group]);
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: PLOT_COLORS, color: 'white'}
    }]


    // Determine the layout and render
    const layout = {
      height: 200,
      width: 200,
      showlegend: false,
      margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
    }

    const ageGroupList = this.renderAgeGroupList();
    return(
      <Col xs={6} sm={6} md={6} lg={6}>
      <div className='quick-facts-plot-container'>
        <h4>Age Groups</h4>
        <div className='quick-facts-list'>
          {ageGroupList}
        </div>
        <div className='quick-facts-plot-area' id="plot-container">
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

  render(){
    const event = this.props.event;
    let ageGroups = null;
    if(event){
      ageGroups = this.renderAgeGroups();
    }
    return(
      <div className='QuickFacts'>
        <h4>Demographics</h4><hr/>
        {ageGroups}

      </div> 
    )
  }
};
export default withRouter(QuickFacts);
